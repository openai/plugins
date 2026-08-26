#!/usr/bin/env python3
"""Materialize deterministic trade scenario expected-value tables.

Input CSV columns:
- scenario
- probability
- current_value
- target_value
- key_drivers
- timing

Optional columns:
- trigger
- source
- source_as_of / source_date / retrieval_date
- borrow_fee / carry_cost / holding_period_days for shorts
- break_price for event pitches
- recovery_value / bond_price / yield_or_spread for credit pitches

Probabilities may be decimals (0.25) or percentages (25 / 25%).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

REQUIRED = ["scenario", "probability", "current_value", "target_value", "key_drivers", "timing"]


def parse_number(value: Any, field: str) -> float:
    text = str(value or "").strip().replace(",", "").replace("$", "")
    if text.endswith("%"):
        text = text[:-1]
        scale = 0.01
    else:
        scale = 1.0
    try:
        number = float(text) * scale
    except ValueError as exc:
        raise ValueError(f"{field} must be numeric, got {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def parse_optional_number(value: Any, field: str, default: float | None = None) -> float | None:
    if str(value or "").strip() == "":
        return default
    return parse_number(value, field)


def parse_probability(value: Any) -> float:
    p = parse_number(value, "probability")
    if p > 1.0:
        p = p / 100.0
    if p < 0:
        raise ValueError("probability cannot be negative")
    return p


def parse_source_date(value: Any, field: str, run_date: date, warnings: list[str]) -> str:
    text = str(value or "").strip()
    if not text:
        warnings.append(f"missing {field}")
        return ""
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        warnings.append(f"{field} invalid date {text!r}; expected YYYY-MM-DD")
        return text
    if parsed > run_date:
        warnings.append(f"{field} is after run_date")
    elif (run_date - parsed).days > 180:
        warnings.append(f"{field} is stale")
    return text


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = [str(f or "").strip() for f in (reader.fieldnames or [])]
        missing = [field for field in REQUIRED if field not in fields]
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError("input CSV must include at least one scenario row")
    return rows


def scenario_return(side: str, current_value: float, target_value: float) -> float:
    if current_value == 0:
        raise ValueError("current_value cannot be zero")
    if side == "short":
        return (current_value - target_value) / current_value
    return (target_value - current_value) / current_value


def materialize(
    rows: list[dict[str, str]], side: str, run_date: date | None = None
) -> dict[str, Any]:
    run_date = run_date or date.today()
    output_rows: list[dict[str, Any]] = []
    total_probability = 0.0
    expected_return = 0.0

    for idx, row in enumerate(rows, start=2):
        scenario = str(row.get("scenario", "")).strip()
        if not scenario:
            raise ValueError(f"row {idx}: scenario is required")
        probability = parse_probability(row.get("probability"))
        current_value = parse_number(row.get("current_value"), "current_value")
        target_value = parse_number(row.get("target_value"), "target_value")
        gross_return = scenario_return(
            "short" if side == "short" else "long", current_value, target_value
        )
        warnings: list[str] = []

        holding_period_days = parse_optional_number(
            row.get("holding_period_days"), "holding_period_days", 365.0
        )
        if holding_period_days is not None and holding_period_days <= 0:
            raise ValueError(f"row {idx}: holding_period_days must be positive")
        borrow_fee = parse_optional_number(row.get("borrow_fee"), "borrow_fee", 0.0) or 0.0
        carry_cost = parse_optional_number(row.get("carry_cost"), "carry_cost", 0.0) or 0.0
        financing_cost = 0.0
        if side == "short":
            financing_cost = (borrow_fee + carry_cost) * ((holding_period_days or 365.0) / 365.0)

        net_return = gross_return - financing_cost
        weighted_return = probability * net_return
        total_probability += probability
        expected_return += weighted_return

        source_as_of = parse_source_date(
            row.get("source_as_of") or row.get("source_date"), "source_as_of", run_date, warnings
        )
        retrieval_date = str(row.get("retrieval_date") or "").strip()
        if retrieval_date:
            parse_source_date(retrieval_date, "retrieval_date", run_date, warnings)

        output_rows.append(
            {
                "scenario": scenario,
                "probability": probability,
                "current_value": current_value,
                "target_value": target_value,
                "gross_return": gross_return,
                "financing_cost": financing_cost,
                "net_return": net_return,
                "weighted_return": weighted_return,
                "event_spread": (target_value - current_value) / current_value
                if side == "event"
                else None,
                "break_price": parse_optional_number(row.get("break_price"), "break_price"),
                "recovery_value": parse_optional_number(
                    row.get("recovery_value"),
                    "recovery_value",
                    target_value if side == "credit" else None,
                ),
                "bond_price": parse_optional_number(
                    row.get("bond_price"), "bond_price", current_value if side == "credit" else None
                ),
                "yield_or_spread": str(row.get("yield_or_spread") or "").strip(),
                "borrow_fee": borrow_fee if side == "short" else None,
                "carry_cost": carry_cost if side == "short" else None,
                "holding_period_days": holding_period_days,
                "key_drivers": str(row.get("key_drivers", "")).strip(),
                "timing": str(row.get("timing", "")).strip(),
                "trigger": str(row.get("trigger", "")).strip(),
                "source": str(row.get("source", "")).strip(),
                "source_as_of": source_as_of,
                "retrieval_date": retrieval_date,
                "warnings": "; ".join(warnings),
            }
        )

    probability_error = abs(total_probability - 1.0)
    return {
        "side": side,
        "total_probability": total_probability,
        "probability_ok": probability_error <= 0.0001,
        "probability_error": probability_error,
        "expected_return": expected_return,
        "rows": output_rows,
    }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def markdown_table(result: dict[str, Any]) -> str:
    lines = [
        "| Scenario | Probability | Current | Target | Gross return | Financing cost | Net return | Weighted return | Key drivers | Timing | Trigger | Source | Source as-of | Warnings |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|",
    ]
    for row in result["rows"]:
        lines.append(
            "| {scenario} | {probability} | {current:.2f} | {target:.2f} | {gross} | {cost} | {net} | {weighted} | {drivers} | {timing} | {trigger} | {source} | {source_as_of} | {warnings} |".format(
                scenario=row["scenario"],
                probability=pct(row["probability"]),
                current=row["current_value"],
                target=row["target_value"],
                gross=pct(row["gross_return"]),
                cost=pct(row["financing_cost"]),
                net=pct(row["net_return"]),
                weighted=pct(row["weighted_return"]),
                drivers=row["key_drivers"],
                timing=row["timing"],
                trigger=row["trigger"],
                source=row["source"],
                source_as_of=row["source_as_of"],
                warnings=row["warnings"],
            )
        )
    lines.append("")
    lines.append(f"Expected return: **{pct(result['expected_return'])}**")
    lines.append(f"Probability sum: **{pct(result['total_probability'])}**")
    if not result["probability_ok"]:
        lines.append("")
        lines.append(
            "> QA warning: probabilities do not sum to 100%. Fix before using in a PM pitch."
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize long/short scenario and expected-value tables."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--side", choices=["long", "short", "event", "credit"], default="long")
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=Path(
            "/tmp/public_equity_investing_long_short_pitch/trade_scenarios_support_note.md"
        ),
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("/tmp/public_equity_investing_long_short_pitch/trade_scenarios.json"),
    )
    parser.add_argument(
        "--run-date",
        default=date.today().isoformat(),
        help="Freshness date for source_as_of checks, YYYY-MM-DD.",
    )
    args = parser.parse_args()

    try:
        run_date = datetime.strptime(args.run_date, "%Y-%m-%d").date()
        result = materialize(load_rows(args.input_csv), args.side, run_date)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(markdown_table(result) + "\n", encoding="utf-8")
    args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {args.markdown_out} and {args.json_out}")
    return 0 if result["probability_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
