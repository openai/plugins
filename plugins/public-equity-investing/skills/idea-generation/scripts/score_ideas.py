#!/usr/bin/env python3
"""Materialize a deterministic public-equity-investing idea scorecard from supplied CSV inputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

SCORE_WEIGHTS = {
    "variant_perception_score": 1.25,
    "catalyst_score": 1.15,
    "valuation_score": 1.10,
    "revisions_score": 1.00,
    "quality_score": 0.90,
    "growth_score": 0.85,
    "risk_reward_score": 1.15,
    "liquidity_score": 0.55,
    "crowding_score": 0.55,
    "momentum_score": 0.50,
    "portfolio_fit_score": 0.70,
}


OUTPUT_FIELDS = [
    "rank",
    "ticker",
    "security",
    "company",
    "idea_type",
    "direction",
    "sector",
    "composite_score",
    "bucket",
    "valid_score_count",
    "variant_view",
    "catalyst",
    "first_rejection_risk",
    "next_step",
    "source",
    "source_as_of",
    "freshness_status",
    "warnings",
]


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


def bucket_for(score: float | None) -> str:
    if score is None:
        return "needs_scoring_inputs"
    if score >= 75:
        return "A - immediate research candidate"
    if score >= 60:
        return "B - watchlist / needs trigger"
    if score >= 45:
        return "C - screen flag only"
    return "Reject / low-priority false positive"


def parse_iso_date(value: Any, field: str, warnings: list[str]) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        warnings.append(f"{field} invalid date {value!r}; expected YYYY-MM-DD")
        return None


def source_freshness(row: dict[str, str], run_date: date, warnings: list[str]) -> tuple[str, str]:
    source_as_of = str(
        row.get("source_as_of") or row.get("source_date") or row.get("as_of_date") or ""
    ).strip()
    if not source_as_of:
        warnings.append("missing source_as_of")
        return "", "missing"
    parsed = parse_iso_date(source_as_of, "source_as_of", warnings)
    if parsed is None:
        return source_as_of, "invalid"
    if parsed > run_date:
        warnings.append("source_as_of is after run_date")
        return source_as_of, "future"
    if (run_date - parsed).days > 180:
        warnings.append("source_as_of is stale")
        return source_as_of, "stale"
    return source_as_of, "current"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("input CSV must include a header row")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError("input CSV must include at least one candidate row")
    return rows


def score_row(row: dict[str, str], index: int, run_date: date) -> dict[str, Any]:
    warnings: list[str] = []
    ticker = str(row.get("ticker") or "").strip()
    security = str(row.get("security") or "").strip()
    if not ticker and not security:
        raise ValueError(f"row {index}: ticker or security is required")

    weighted_score = 0.0
    weight_total = 0.0
    valid_count = 0
    for field, weight in SCORE_WEIGHTS.items():
        score = parse_score(row.get(field), field, warnings)
        if score is None:
            continue
        weighted_score += score * weight
        weight_total += weight
        valid_count += 1

    composite = round(weighted_score / weight_total, 2) if weight_total else None
    if valid_count == 0:
        warnings.append("no valid numeric score fields provided")
    if not str(row.get("variant_view") or "").strip():
        warnings.append("missing variant_view")
    if not str(row.get("first_rejection_risk") or "").strip():
        warnings.append("missing first_rejection_risk")
    source_as_of, freshness_status = source_freshness(row, run_date, warnings)

    return {
        "rank": 0,
        "ticker": ticker,
        "security": security,
        "company": str(row.get("company") or "").strip(),
        "idea_type": str(row.get("idea_type") or "").strip(),
        "direction": str(row.get("direction") or "").strip(),
        "sector": str(row.get("sector") or "").strip(),
        "composite_score": composite,
        "bucket": bucket_for(composite),
        "valid_score_count": valid_count,
        "variant_view": str(row.get("variant_view") or "").strip(),
        "catalyst": str(row.get("catalyst") or "").strip(),
        "first_rejection_risk": str(row.get("first_rejection_risk") or "").strip(),
        "next_step": str(row.get("next_step") or "").strip(),
        "source": str(row.get("source") or "").strip(),
        "source_as_of": source_as_of,
        "freshness_status": freshness_status,
        "warnings": "; ".join(warnings),
    }


def materialize(rows: list[dict[str, str]], run_date: date | None = None) -> list[dict[str, Any]]:
    run_date = run_date or date.today()
    scored = [score_row(row, idx, run_date) for idx, row in enumerate(rows, start=2)]
    scored.sort(
        key=lambda row: (
            -1 if row["composite_score"] is None else -row["composite_score"],
            row["ticker"] or row["security"],
        )
    )
    for rank, row in enumerate(scored, start=1):
        row["rank"] = rank
    return scored


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: "" if row.get(field) is None else row.get(field, "")
                    for field in OUTPUT_FIELDS
                }
            )


def markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Public Equity Investing Idea Scorecard",
        "",
        "> Deterministic materializer from supplied inputs only. Scores rank research candidates, not final recommendations.",
        "",
        "| Rank | Ticker/Security | Type | Score | Bucket | Variant View | Catalyst | First Rejection Risk | Warnings |",
        "|---:|---|---|---:|---|---|---|---|---|",
    ]
    for row in rows:
        label = row["ticker"] or row["security"]
        score = "" if row["composite_score"] is None else f"{row['composite_score']:.2f}"
        lines.append(
            f"| {row['rank']} | {label} | {row['idea_type']} | {score} | {row['bucket']} | {row['variant_view']} | {row['catalyst']} | {row['first_rejection_risk']} | {row['warnings']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score supplied public-equity idea candidates into a deterministic PM triage log."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/public_equity_investing_idea_generation_output"),
    )
    parser.add_argument(
        "--run-date",
        default=date.today().isoformat(),
        help="Freshness date for source_as_of checks, YYYY-MM-DD.",
    )
    args = parser.parse_args()

    try:
        run_date = datetime.strptime(args.run_date, "%Y-%m-%d").date()
        rows = materialize(load_rows(args.input_csv), run_date)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "ranked_ideas.csv", rows)
    (args.output_dir / "idea_scorecard.json").write_text(
        json.dumps({"rows": rows}, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "idea_scorecard_support_note.md").write_text(
        markdown(rows), encoding="utf-8"
    )
    print(f"Wrote idea scorecard outputs to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
