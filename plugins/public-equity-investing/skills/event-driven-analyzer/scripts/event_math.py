#!/usr/bin/env python3
"""Event-driven math helpers.

Usage:
  python scripts/event_math.py --mode cash_merger --input input.json
  python scripts/event_math.py --mode stock_deal --input input.json
  python scripts/event_math.py --mode scenario_ev --input input.json
  python scripts/event_math.py --mode scenario_ev --input input.json --allow-probability-sum-mismatch
  python scripts/event_math.py --mode cvr --input input.json

All numeric probabilities should be decimals, e.g. 0.75 for 75%.
This script performs deterministic math only; it does not fetch market data.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

PROBABILITY_SUM_TOLERANCE = 1e-6


def _as_float(
    data: dict[str, Any], key: str, required: bool = True, default: float | None = None
) -> float:
    value = data.get(key, default)
    if value is None:
        if required:
            raise ValueError(f"missing required numeric field: {key}")
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"field {key} must be numeric, got {value!r}") from exc


def _safe_div(num: float, den: float) -> float | None:
    if den == 0:
        return None
    return num / den


def _as_probability(value: Any, context: str) -> float:
    try:
        probability = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{context} probability must be numeric, got {value!r}") from exc
    if probability < 0.0 or probability > 1.0:
        raise ValueError(f"{context} probability must be between 0 and 1, got {probability}")
    return probability


def annualized_return(gross_return: float, days: float) -> float | None:
    if days <= 0:
        return None
    if gross_return <= -1:
        return -1.0
    return (1.0 + gross_return) ** (365.0 / days) - 1.0


def cash_merger(data: dict[str, Any]) -> dict[str, Any]:
    current_price = _as_float(data, "current_price")
    deal_price = _as_float(data, "deal_price")
    days_to_close = _as_float(data, "days_to_close", required=False, default=float("nan"))
    break_price = _as_float(data, "break_price", required=False, default=float("nan"))
    expected_dividends = _as_float(data, "expected_dividends", required=False, default=0.0)
    financing_cost = _as_float(data, "financing_cost", required=False, default=0.0)
    other_carry = _as_float(data, "other_carry", required=False, default=0.0)

    adjusted_deal_value = deal_price + expected_dividends - financing_cost - other_carry
    gross_spread = _safe_div(adjusted_deal_value, current_price)
    gross_return = None if gross_spread is None else gross_spread - 1.0

    implied_probability = None
    if not math.isnan(break_price):
        implied_probability = _safe_div(
            current_price - break_price, adjusted_deal_value - break_price
        )

    annualized = None
    if gross_return is not None and not math.isnan(days_to_close):
        annualized = annualized_return(gross_return, days_to_close)

    return {
        "mode": "cash_merger",
        "current_price": current_price,
        "adjusted_deal_value": adjusted_deal_value,
        "gross_return": gross_return,
        "annualized_return": annualized,
        "market_implied_probability": implied_probability,
        "notes": [
            "Market-implied probability depends heavily on break_price.",
            "Annualized return should be paired with downside and scenario EV.",
        ],
    }


def stock_deal(data: dict[str, Any]) -> dict[str, Any]:
    target_price = _as_float(data, "target_price")
    acquirer_price = _as_float(data, "acquirer_price")
    exchange_ratio = _as_float(data, "exchange_ratio")
    target_shares = _as_float(data, "target_shares", required=False, default=1.0)
    days_to_close = _as_float(data, "days_to_close", required=False, default=float("nan"))
    expected_target_dividends = _as_float(
        data, "expected_target_dividends", required=False, default=0.0
    )
    expected_acquirer_dividends = _as_float(
        data, "expected_acquirer_dividends", required=False, default=0.0
    )
    borrow_cost = _as_float(data, "borrow_cost", required=False, default=0.0)

    deal_value = acquirer_price * exchange_ratio
    adjusted_deal_value = (
        deal_value
        + expected_target_dividends
        - (exchange_ratio * expected_acquirer_dividends)
        - borrow_cost
    )
    gross_return = _safe_div(adjusted_deal_value, target_price)
    if gross_return is not None:
        gross_return -= 1.0
    hedge_shares = target_shares * exchange_ratio
    annualized = None
    if gross_return is not None and not math.isnan(days_to_close):
        annualized = annualized_return(gross_return, days_to_close)

    return {
        "mode": "stock_deal",
        "target_price": target_price,
        "acquirer_price": acquirer_price,
        "exchange_ratio": exchange_ratio,
        "deal_value": deal_value,
        "adjusted_deal_value": adjusted_deal_value,
        "gross_return": gross_return,
        "annualized_return": annualized,
        "hedge_shares_per_target_shares": hedge_shares,
        "notes": [
            "Review collar, election, dividend, borrow, and acquirer vote risk separately.",
        ],
    }


def scenario_ev(
    data: dict[str, Any], allow_probability_sum_mismatch: bool = False
) -> dict[str, Any]:
    current_price = _as_float(data, "current_price")
    scenarios: list[dict[str, Any]] = data.get("scenarios", [])
    if not scenarios:
        raise ValueError("scenario_ev requires a non-empty scenarios list")

    probability_sum = 0.0
    expected_terminal_value = 0.0
    weighted_annualized = 0.0
    rows = []

    for scenario in scenarios:
        name = scenario.get("name", "unnamed")
        if "probability" not in scenario:
            raise ValueError(f"scenario {name!r} missing required probability")
        probability = _as_probability(scenario["probability"], f"scenario {name!r}")
        terminal_value = float(scenario["terminal_value"])
        days = float(
            scenario.get("days_to_resolution", data.get("days_to_resolution", float("nan")))
        )
        ret = terminal_value / current_price - 1.0
        ann = None if math.isnan(days) else annualized_return(ret, days)
        probability_sum += probability
        expected_terminal_value += probability * terminal_value
        if ann is not None:
            weighted_annualized += probability * ann
        rows.append(
            {
                "name": name,
                "probability": probability,
                "terminal_value": terminal_value,
                "return": ret,
                "days_to_resolution": None if math.isnan(days) else days,
                "annualized_return": ann,
            }
        )

    probabilities_sum_to_100pct = abs(probability_sum - 1.0) < PROBABILITY_SUM_TOLERANCE
    if not probabilities_sum_to_100pct and not allow_probability_sum_mismatch:
        raise ValueError(
            "scenario probabilities must sum to 1.0; "
            f"got {probability_sum:.6f}. "
            "Pass --allow-probability-sum-mismatch to emit diagnostic, non-memo-ready output."
        )

    notes = [
        "Scenario-weighted annualized return can be misleading when timing varies materially.",
    ]
    if not probabilities_sum_to_100pct:
        notes.insert(
            0,
            "Probability sum mismatch was explicitly allowed; revise before using probability-weighted conclusions.",
        )

    expected_return = expected_terminal_value / current_price - 1.0
    return {
        "mode": "scenario_ev",
        "current_price": current_price,
        "probability_sum": probability_sum,
        "probabilities_sum_to_100pct": probabilities_sum_to_100pct,
        "expected_terminal_value": expected_terminal_value,
        "expected_return": expected_return,
        "probability_weighted_annualized_return": weighted_annualized,
        "scenarios": rows,
        "notes": notes,
    }


def cvr(data: dict[str, Any]) -> dict[str, Any]:
    milestones: list[dict[str, Any]] = data.get("milestones", [])
    if not milestones:
        raise ValueError("cvr requires a non-empty milestones list")
    default_discount_rate = _as_float(data, "discount_rate", required=False, default=0.12)
    liquidity_discount = _as_float(data, "liquidity_discount", required=False, default=0.0)

    pv = 0.0
    rows = []
    for milestone in milestones:
        name = milestone.get("name", "unnamed")
        payment = float(milestone["payment"])
        probability = _as_probability(milestone["probability"], f"milestone {name!r}")
        years = float(milestone["years"])
        discount_rate = float(milestone.get("discount_rate", default_discount_rate))
        value = payment * probability / ((1.0 + discount_rate) ** years)
        pv += value
        rows.append(
            {
                "name": name,
                "payment": payment,
                "probability": probability,
                "years": years,
                "discount_rate": discount_rate,
                "present_value": value,
            }
        )
    pv_after_discount = pv - liquidity_discount
    return {
        "mode": "cvr",
        "gross_present_value": pv,
        "liquidity_discount": liquidity_discount,
        "net_present_value": pv_after_discount,
        "milestones": rows,
        "notes": [
            "Review milestone dependency, sponsor incentives, reporting rights, transferability, and enforcement risk.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Event-driven math helpers")
    parser.add_argument(
        "--mode", required=True, choices=["cash_merger", "stock_deal", "scenario_ev", "cvr"]
    )
    parser.add_argument("--input", help="Path to JSON input. If omitted, reads stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument(
        "--allow-probability-sum-mismatch",
        action="store_true",
        help="Allow scenario_ev probabilities that do not sum to 1.0; output is diagnostic and not memo-ready.",
    )
    args = parser.parse_args()

    try:
        if args.input:
            data = json.loads(Path(args.input).read_text())
        else:
            data = json.load(sys.stdin)

        if args.mode == "cash_merger":
            result = cash_merger(data)
        elif args.mode == "stock_deal":
            result = stock_deal(data)
        elif args.mode == "scenario_ev":
            result = scenario_ev(
                data,
                allow_probability_sum_mismatch=args.allow_probability_sum_mismatch,
            )
        elif args.mode == "cvr":
            result = cvr(data)
        else:
            raise AssertionError(args.mode)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
