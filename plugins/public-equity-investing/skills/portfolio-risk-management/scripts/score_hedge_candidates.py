#!/usr/bin/env python3
"""Materialize a deterministic hedge candidate scorecard and basis-risk ledger."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED = ["hedge", "hedge_type", "risk_hedged"]

SCORE_WEIGHTS = {
    "exposure_fit_score": 1.30,
    "thesis_preservation_score": 1.25,
    "relationship_stability_score": 0.95,
    "downside_behavior_score": 1.15,
    "tenor_alignment_score": 0.80,
    "cost_carry_score": 0.90,
    "liquidity_score": 0.85,
    "implementation_complexity_score": 0.60,
    "basis_risk_score": 1.20,
}

SCORECARD_FIELDS = [
    "rank",
    "hedge",
    "hedge_type",
    "risk_hedged",
    "target_position",
    "composite_score",
    "bucket",
    "valid_score_count",
    "implementation_status",
    "as_of",
    "source",
    "readiness_status",
    "live_pricing_status",
    "borrow_status",
    "option_chain_status",
    "risk_model_status",
    "basis_risk",
    "basis_risk_mitigation",
    "monitoring_trigger",
    "warnings",
]

BASIS_FIELDS = [
    "hedge",
    "hedge_type",
    "risk_hedged",
    "basis_risk",
    "severity",
    "why_it_matters",
    "mitigation",
    "monitoring_trigger",
    "implementation_status",
    "as_of",
    "source",
    "readiness_status",
    "live_pricing_status",
    "borrow_status",
    "option_chain_status",
    "risk_model_status",
]

READINESS_FIELDS = [
    "live_pricing_status",
    "borrow_status",
    "option_chain_status",
    "risk_model_status",
]

READY_STATUSES = {"current", "available", "confirmed", "validated", "not_applicable", "n/a", "na"}

CREDIT_HEDGE_WARNING = (
    "Credit hedge construction belongs in Credit Markets; use here only as "
    "public-equity risk context."
)

CREDIT_HEDGE_TYPE_PATTERNS = {
    "cds",
    "credit default swap",
    "bond",
    "bonds",
    "loan",
    "loans",
    "bank loan",
    "leveraged loan",
    "high yield",
    "investment grade",
    "spread dv01",
    "spread_dv01",
    "spread hedge",
    "credit spread",
    "cs01",
    "dv01",
    "capital structure",
    "capital-structure",
    "distressed",
    "recovery",
    "covenant",
    "credit hedge",
    "credit instrument",
    "credit security",
}


def _normalized_text(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", " ").replace("/", " ").replace("-", " ")


def is_credit_hedge_type(value: Any) -> bool:
    text = _normalized_text(value)
    if not text:
        return False
    return any(
        pattern.replace("_", " ").replace("-", " ") in text
        for pattern in CREDIT_HEDGE_TYPE_PATTERNS
    )


def row_has_credit_hedge(row: dict[str, str]) -> bool:
    return any(
        is_credit_hedge_type(row.get(field))
        for field in ["hedge_type", "instrument_type", "security_type", "asset_class"]
    )


def parse_score(value: Any, field: str, warnings: list[str]) -> float | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        score = float(text)
    except ValueError:
        warnings.append(f"{field} invalid numeric value {value!r}")
        return None
    if not math.isfinite(score):
        warnings.append(f"{field} is not finite")
        return None
    if score < 0:
        warnings.append(f"{field} negative score excluded")
        return None
    if score <= 5:
        return score / 5.0 * 100.0
    if score <= 100:
        return score
    warnings.append(f"{field} above 100 capped at 100")
    return 100.0


def bucket(score: float | None) -> str:
    if score is None:
        return "needs_scoring_inputs"
    if score >= 80:
        return "primary hedge candidate"
    if score >= 65:
        return "usable with checks"
    if score >= 50:
        return "watchlist / situational"
    return "reject or resize instead"


def severity_from_basis(score: float | None, text: str) -> str:
    lowered = text.lower()
    if any(
        term in lowered
        for term in ["high", "severe", "correlation break", "over-hedge", "wrong tenor"]
    ):
        return "high"
    if score is None:
        return "needs_review"
    if score >= 75:
        return "low"
    if score >= 50:
        return "medium"
    return "high"


def valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def readiness_status(row: dict[str, str], warnings: list[str]) -> str:
    as_of = str(row.get("as_of") or row.get("source_as_of") or "").strip()
    source = str(row.get("source") or "").strip()
    if not as_of:
        warnings.append("missing as_of")
    elif not valid_date(as_of):
        warnings.append("as_of invalid date; expected YYYY-MM-DD")
    if not source:
        warnings.append("missing source")

    missing_statuses: list[str] = []
    weak_statuses: list[str] = []
    for field in READINESS_FIELDS:
        status = str(row.get(field) or "").strip().lower()
        if not status:
            missing_statuses.append(field)
        elif status not in READY_STATUSES:
            weak_statuses.append(f"{field}={status}")

    if missing_statuses:
        warnings.append("missing readiness fields: " + ", ".join(missing_statuses))
    if weak_statuses:
        warnings.append("non-ready readiness fields: " + ", ".join(weak_statuses))

    if not as_of or not source or missing_statuses:
        return "screen-grade"
    if weak_statuses:
        return "needs-targeted-checks"
    return "implementation-data-ready"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = [str(f or "").strip() for f in (reader.fieldnames or [])]
        missing = [field for field in REQUIRED if field not in fields]
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError("input CSV must include at least one hedge candidate")
    return rows


def score_row(row: dict[str, str], index: int) -> dict[str, Any]:
    warnings: list[str] = []
    for field in REQUIRED:
        if not str(row.get(field) or "").strip():
            raise ValueError(f"row {index}: {field} is required")
    weighted = 0.0
    weight_total = 0.0
    valid_count = 0
    score_values: dict[str, float | None] = {}
    for field, weight in SCORE_WEIGHTS.items():
        value = parse_score(row.get(field), field, warnings)
        score_values[field] = value
        if value is None:
            continue
        weighted += value * weight
        weight_total += weight
        valid_count += 1
    composite = round(weighted / weight_total, 2) if weight_total else None
    if valid_count == 0:
        warnings.append("no valid score fields provided")
    if not str(row.get("basis_risk") or "").strip():
        warnings.append("missing basis_risk")
    if not str(row.get("implementation_status") or "").strip():
        warnings.append("missing implementation_status")
    readiness = readiness_status(row, warnings)
    credit_handoff = row_has_credit_hedge(row)
    if credit_handoff:
        warnings.append(CREDIT_HEDGE_WARNING)
        readiness = "route_to_credit_markets"

    basis_score = score_values.get("basis_risk_score")
    implementation_status = str(row.get("implementation_status") or "").strip()
    if credit_handoff:
        implementation_status = "route_to_credit_markets"
    candidate_bucket = bucket(composite)
    if credit_handoff:
        candidate_bucket = "route to Credit Markets"
    return {
        "rank": 0,
        "hedge": str(row.get("hedge") or "").strip(),
        "hedge_type": str(row.get("hedge_type") or "").strip(),
        "risk_hedged": str(row.get("risk_hedged") or "").strip(),
        "target_position": str(row.get("target_position") or "").strip(),
        "retained_exposure": str(row.get("retained_exposure") or "").strip(),
        "composite_score": composite,
        "bucket": candidate_bucket,
        "valid_score_count": valid_count,
        "implementation_status": implementation_status,
        "as_of": str(row.get("as_of") or row.get("source_as_of") or "").strip(),
        "source": str(row.get("source") or "").strip(),
        "readiness_status": readiness,
        "live_pricing_status": str(row.get("live_pricing_status") or "").strip(),
        "borrow_status": str(row.get("borrow_status") or "").strip(),
        "option_chain_status": str(row.get("option_chain_status") or "").strip(),
        "risk_model_status": str(row.get("risk_model_status") or "").strip(),
        "basis_risk": str(row.get("basis_risk") or "").strip(),
        "basis_risk_mitigation": str(
            row.get("basis_risk_mitigation") or row.get("mitigation") or ""
        ).strip(),
        "monitoring_trigger": str(row.get("monitoring_trigger") or "").strip(),
        "basis_risk_severity": severity_from_basis(basis_score, str(row.get("basis_risk") or "")),
        "warnings": "; ".join(warnings),
    }


def materialize(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    scored = [score_row(row, idx) for idx, row in enumerate(rows, start=2)]
    scored.sort(
        key=lambda row: (
            row["readiness_status"] == "route_to_credit_markets",
            -1 if row["composite_score"] is None else -row["composite_score"],
            row["hedge"],
        )
    )
    for rank, row in enumerate(scored, start=1):
        row["rank"] = rank
    return scored


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {field: "" if row.get(field) is None else row.get(field, "") for field in fields}
            )


def basis_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "hedge": row["hedge"],
                "hedge_type": row["hedge_type"],
                "risk_hedged": row["risk_hedged"],
                "basis_risk": row["basis_risk"],
                "severity": row["basis_risk_severity"],
                "why_it_matters": "Hedge can fail if this mismatch dominates the target exposure.",
                "mitigation": row["basis_risk_mitigation"],
                "monitoring_trigger": row["monitoring_trigger"],
                "implementation_status": row["implementation_status"],
                "as_of": row["as_of"],
                "source": row["source"],
                "readiness_status": row["readiness_status"],
                "live_pricing_status": row["live_pricing_status"],
                "borrow_status": row["borrow_status"],
                "option_chain_status": row["option_chain_status"],
                "risk_model_status": row["risk_model_status"],
            }
        )
    return out


def markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Hedge Candidate Scorecard",
        "",
        "> Deterministic materializer from supplied inputs only. Confirm live pricing, borrow, options, liquidity, and risk-model data before implementation.",
        "",
        "| Rank | Hedge | Type | Risk Hedged | Score | Bucket | Readiness | Implementation | Basis Risk | Warnings |",
        "|---:|---|---|---|---:|---|---|---|---|---|",
    ]
    for row in rows:
        score = "" if row["composite_score"] is None else f"{row['composite_score']:.2f}"
        lines.append(
            f"| {row['rank']} | {row['hedge']} | {row['hedge_type']} | {row['risk_hedged']} | {score} | {row['bucket']} | {row['readiness_status']} | {row['implementation_status']} | {row['basis_risk']} | {row['warnings']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score supplied public-equity-investing hedge candidates."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        rows = materialize(load_rows(args.input_csv))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "hedge_scorecard.csv", SCORECARD_FIELDS, rows)
    write_csv(args.output_dir / "basis_risk_ledger.csv", BASIS_FIELDS, basis_rows(rows))
    (args.output_dir / "hedge_scorecard.json").write_text(
        json.dumps({"rows": rows, "basis_risk_ledger": basis_rows(rows)}, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "hedge_scorecard_support_note.md").write_text(
        markdown(rows), encoding="utf-8"
    )
    print(f"Wrote hedge scorecard outputs to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
