#!/usr/bin/env python3
"""Lightweight schema validator for financials-normalizer CSV outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

REQUIRED = {
    "entity",
    "source_id",
    "statement",
    "line_item_original",
    "line_item_standard",
    "line_item_id",
    "period_end",
    "period_label",
    "period_type",
    "currency",
    "units",
    "source_value",
    "normalized_value",
    "normalization_method",
    "source_location",
    "evidence_label",
    "confidence",
}
EVIDENCE = {
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
STATEMENTS = {
    "income_statement",
    "balance_sheet",
    "cash_flow",
    "kpi_schedule",
    "segment",
    "equity_risk_debt_liquidity_context",
    "share_count",
    "working_capital",
    "capital_allocation",
    "consensus_estimate",
    "etf_index_context",
    "adjustment",
}
PERIOD_TYPES = {
    "annual",
    "quarterly",
    "monthly",
    "ytd",
    "ltm",
    "forecast",
    "budget",
    "pro_forma",
    "scenario",
}
LOCATION_OPTIONAL = {
    "assumption_user_provided",
    "assumption_inferred",
    "missing_required_source",
    "unknown",
}
CONFIDENCE = {"high", "medium", "low"}


def is_number(value: str) -> bool:
    try:
        number = float(str(value).replace(",", ""))
    except Exception:
        return False
    return math.isfinite(number)


def validate(path: Path) -> dict:
    errors, warnings = [], []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = sorted(REQUIRED - fields)
        if missing:
            return {
                "ok": False,
                "rows": 0,
                "errors": ["missing columns: " + ", ".join(missing)],
                "warnings": [],
            }
        rows = list(reader)
    for i, row in enumerate(rows, start=2):
        label = f"row {i}"
        source_id = row.get("source_id", "")
        if not source_id or source_id == "SRC-UNSPECIFIED":
            errors.append(
                f"{label}: missing source_id; SRC-UNSPECIFIED is not decision-grade provenance"
            )
        elif not source_id.startswith("SRC-"):
            warnings.append(f"{label}: source_id should start with SRC-")
        if row.get("evidence_label") not in EVIDENCE:
            errors.append(f"{label}: invalid evidence_label {row.get('evidence_label')!r}")
        if row.get("statement") not in STATEMENTS:
            errors.append(f"{label}: invalid statement {row.get('statement')!r}")
        if (
            row.get("statement") == "consensus_estimate"
            and row.get("evidence_label") != "estimate_consensus"
        ):
            errors.append(
                f"{label}: consensus_estimate is reserved for external consensus "
                "labeled estimate_consensus"
            )
        if row.get("period_type") not in PERIOD_TYPES:
            errors.append(f"{label}: invalid period_type {row.get('period_type')!r}")
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{label}: invalid confidence {row.get('confidence')!r}")
        if row.get("evidence_label") != "missing_required_source" and not is_number(
            row.get("normalized_value", "")
        ):
            errors.append(f"{label}: normalized_value is not numeric")
        if row.get("evidence_label") not in LOCATION_OPTIONAL and not row.get("source_location"):
            warnings.append(f"{label}: missing source_location")
    return {"ok": not errors, "rows": len(rows), "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.csv_path.exists():
        print(f"file not found: {args.csv_path}", file=sys.stderr)
        return 2
    result = validate(args.csv_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("ok" if result["ok"] else "failed")
        print(f"rows: {result['rows']}")
        for error in result["errors"]:
            print(f"error: {error}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
