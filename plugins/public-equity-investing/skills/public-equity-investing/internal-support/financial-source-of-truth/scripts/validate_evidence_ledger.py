#!/usr/bin/env python3
"""
Validate a Public Equity Investing evidence ledger in CSV or JSON format.

The script checks for required fields, accepted evidence labels, freshness labels,
missing source IDs, missing as-of dates for market-sensitive claims, and unsupported
high-impact assumptions.

Usage:
  python scripts/validate_evidence_ledger.py evidence_ledger.csv
  python scripts/validate_evidence_ledger.py evidence_ledger.json

JSON may be either a list of row objects or an object with a top-level "rows" list.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

CANONICAL_LABELS = {
    "fact_source_reported",
    "fact_provider_standardized",
    "derived_calculation",
    "issuer_management_claim",
    "management_adjusted",
    "analyst_adjusted",
    "analyst_interpretation",
    "assumption_user_provided",
    "assumption_inferred",
    "estimate_consensus",
    "stale_source",
    "contradicted_source",
    "missing_required_source",
    "unknown",
}

LABEL_ALIASES = {
    "verified fact": "fact_source_reported",
    "reported fact": "fact_source_reported",
    "issuer claim": "issuer_management_claim",
    "issuer / management claim": "issuer_management_claim",
    "issuer/management claim": "issuer_management_claim",
    "management statement": "issuer_management_claim",
    "management claim": "issuer_management_claim",
    "assumption": "assumption_inferred",
    "user assumption": "assumption_user_provided",
    "inference": "analyst_interpretation",
    "estimate": "assumption_inferred",
    "consensus estimate": "estimate_consensus",
    "pro forma adjustment": "analyst_adjusted",
    "stale item": "stale_source",
    "contradicted item": "contradicted_source",
    "unsupported": "missing_required_source",
}

ACCEPTED_FRESHNESS = {
    "current",
    "current but volatile",
    "stale but usable for history",
    "potentially superseded",
    "stale for decision",
    "unknown freshness",
    "unknown",
    "n/a",
    "na",
    "",
}

REQUIRED_CANONICAL = ["claim", "label", "support"]

FIELD_ALIASES = {
    "claim": [
        "claim",
        "claim / metric",
        "metric",
        "issuer / management claim",
        "management claim",
        "issue",
    ],
    "label": ["label", "evidence label", "type", "status"],
    "source": ["source", "source id", "source ids", "source id(s)", "sources"],
    "support": ["support", "exact support", "evidence support", "basis"],
    "freshness": ["freshness", "staleness", "freshness label"],
    "as_of": ["as of", "as-of", "as-of date", "date / as-of", "date"],
    "impact": ["impact", "decision impact", "materiality"],
    "caveat": ["caveat", "caveat / conflict", "conflict", "notes"],
}

MARKET_SENSITIVE_TERMS = re.compile(
    r"\b(price|yield|spread|fx|foreign exchange|rate|rates|curve|vol|volatility|"
    r"market cap|enterprise value|ev/|multiple|consensus|rating|cap rate|rent roll|"
    r"liquidity|covenant|headroom|debt balance|borrowing base)\b",
    re.IGNORECASE,
)

VAGUE_SUPPORT_VALUES = {
    "source",
    "filing",
    "company filing",
    "company report",
    "provider",
    "vendor",
    "transcript",
    "presentation",
    "website",
    "model",
    "deck",
    "memo",
    "n/a",
    "na",
}


def normalize_key(key: str) -> str:
    return re.sub(r"\s+", " ", key.strip().lower())


def normalize_label(label: str) -> str:
    key = normalize_key(label).replace("_", " ")
    if label in CANONICAL_LABELS:
        return label
    return LABEL_ALIASES.get(key, label)


def canonicalize_row(row: dict[str, Any]) -> dict[str, str]:
    normalized = {
        normalize_key(str(k)): "" if v is None else str(v).strip() for k, v in row.items()
    }
    out: dict[str, str] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                out[canonical] = normalized[alias]
                break
        else:
            out[canonical] = ""
    return out


def load_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV has no header row")
            raw_rows = list(reader)
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            raw_rows = data["rows"]
        elif isinstance(data, list):
            raw_rows = data
        else:
            raise ValueError(
                "JSON must be a list of objects or an object with a top-level 'rows' list"
            )
        if not all(isinstance(r, dict) for r in raw_rows):
            raise ValueError("Each JSON row must be an object")
    else:
        raise ValueError("Only .csv and .json ledgers are supported")

    rows = [canonicalize_row(r) for r in raw_rows]
    if not rows:
        warnings.append("Ledger contains no rows")
    return rows, warnings


def validate_rows(rows: Iterable[dict[str, str]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for idx, row in enumerate(rows, start=1):
        prefix = f"row {idx}"
        for field in REQUIRED_CANONICAL:
            if not row.get(field):
                errors.append(f"{prefix}: missing required field '{field}'")

        raw_label = row.get("label", "")
        label = normalize_label(raw_label.lower())
        if label and label not in CANONICAL_LABELS:
            warnings.append(f"{prefix}: unrecognized evidence label '{row.get('label')}'")

        freshness = row.get("freshness", "").lower()
        if freshness not in ACCEPTED_FRESHNESS:
            warnings.append(f"{prefix}: unrecognized freshness label '{row.get('freshness')}'")

        claim = row.get("claim", "")
        source = row.get("source", "")
        as_of = row.get("as_of", "")
        impact = row.get("impact", "").lower()
        support = row.get("support", "")

        source_required = {
            "fact_source_reported",
            "fact_provider_standardized",
            "derived_calculation",
            "issuer_management_claim",
            "management_adjusted",
            "analyst_adjusted",
            "estimate_consensus",
        }
        if label in source_required and not source:
            errors.append(f"{prefix}: '{label}' requires a source ID")

        support_terms = [term for term in re.split(r"\s+", support.strip()) if term]
        if label in source_required and support.lower() in VAGUE_SUPPORT_VALUES:
            warnings.append(
                f"{prefix}: source-backed claim needs exact support, not generic support '{support}'"
            )
        elif label in source_required and 0 < len(support_terms) < 3:
            warnings.append(
                f"{prefix}: source-backed claim support may be too vague; add page, table, quote, provider timestamp, or calculation bridge"
            )

        if label in {"assumption_user_provided", "assumption_inferred"} and source and not support:
            warnings.append(
                f"{prefix}: assumption has a source ID but no basis/support explanation"
            )

        if label == "issuer_management_claim" and not row.get("caveat"):
            warnings.append(
                f"{prefix}: issuer claim should include caveat, test, or evidence request"
            )

        if label == "analyst_interpretation" and not source:
            warnings.append(
                f"{prefix}: analyst interpretation should cite underlying facts or state that no supporting source is available"
            )

        if MARKET_SENSITIVE_TERMS.search(claim) and not as_of:
            warnings.append(f"{prefix}: market-sensitive claim may need an as-of date")

        judgment_labels = {
            "assumption_user_provided",
            "assumption_inferred",
            "analyst_interpretation",
        }
        impact_terms = ["high", "critical", "decision", "valuation", "credit"]
        if label in judgment_labels and any(term in impact for term in impact_terms):
            warnings.append(f"{prefix}: high-impact {label} should be sensitized or escalated")

    return errors, warnings


def main(argv: list[str]) -> int:
    if any(arg in {"-h", "--help"} for arg in argv[1:]):
        print(
            "Usage: python validate_evidence_ledger.py <evidence_ledger.csv|evidence_ledger.json>"
        )
        return 0
    if len(argv) != 2:
        print(
            "Usage: python validate_evidence_ledger.py <evidence_ledger.csv|evidence_ledger.json>"
        )
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}")
        return 2

    try:
        rows, load_warnings = load_rows(path)
        errors, warnings = validate_rows(rows)
        warnings = load_warnings + warnings
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        return 2

    print(f"Validated {len(rows)} ledger row(s).")
    if errors:
        print("\nErrors:")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("\nWarnings:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("\nResult: FAIL")
        return 1
    if warnings:
        print("\nResult: PASS WITH WARNINGS")
        return 0
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
