#!/usr/bin/env python3
"""Materialize standard Public Equity Investing sensitivity tables.

The script is dependency-free and intentionally conservative. If required
inputs are missing, it emits "input required" rows instead of inventing values.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AXES = {
    "valuation_multiples": [8.0, 10.0, 12.0],
    "eps_revisions": [-0.10, 0.0, 0.10],
    "multiple_changes": [-0.10, 0.0, 0.10],
    "revenue_growth_shocks": [-0.05, 0.0, 0.05],
    "margin_shock_bps": [-200, 0, 200],
    "event_probabilities": [0.25, 0.50, 0.75],
    "rate_changes_bps": [-100, 0, 100],
    "spread_changes_bps": [-100, 0, 100],
}

TABLE_ORDER = [
    "price_target_scenario",
    "valuation_sensitivity",
    "eps_revision_sensitivity",
    "kpi_driver_sensitivity",
    "equity_liquidity_downside",
    "event_probability_tree",
    "macro_factor_sensitivity",
    "thesis_trigger_table",
]

SOURCE_COLUMNS = ["source_id", "source_posture", "as_of_date"]
PROBABILITY_TOLERANCE = 0.0001


def load_payload(path: str | None) -> dict[str, Any]:
    if not path:
        return {"base": {}, "axes": {}, "triggers": [], "cases": [], "_input_was_provided": False}
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    payload.setdefault("base", {})
    payload.setdefault("axes", {})
    payload.setdefault("triggers", [])
    payload.setdefault("cases", [])
    payload["_input_was_provided"] = True
    return payload


def axis(payload: dict[str, Any], name: str) -> list[Any]:
    values = payload.get("axes", {}).get(name, DEFAULT_AXES[name])
    if not isinstance(values, list) or not values:
        return DEFAULT_AXES[name]
    return values


def number(base: dict[str, Any], key: str, default: float | None = None) -> float | None:
    value = base.get(key, default)
    if value is None or value == "":
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def numeric_value(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def probability_value(value: Any) -> float | None:
    numeric = numeric_value(value)
    if numeric is None:
        return None
    if numeric < 0 or numeric > 1:
        return None
    return numeric


def source_context(payload: dict[str, Any], item: dict[str, Any] | None = None) -> dict[str, str]:
    base = payload.get("base", {})
    source = payload.get("source", {})
    metadata = payload.get("metadata", {})
    if not isinstance(source, dict):
        source = {}
    if not isinstance(metadata, dict):
        metadata = {}
    item = item or {}

    def pick(*values: Any, default: str) -> str:
        for value in values:
            if value not in (None, ""):
                return str(value)
        return default

    return {
        "source_id": pick(
            item.get("source_id"),
            item.get("source"),
            base.get("source_id"),
            source.get("source_id"),
            metadata.get("source_id"),
            payload.get("source_id"),
            default="missing",
        ),
        "source_posture": pick(
            item.get("source_posture"),
            base.get("source_posture"),
            source.get("source_posture"),
            metadata.get("source_posture"),
            payload.get("source_posture"),
            default="user_supplied"
            if metadata.get("source_name") and metadata.get("as_of")
            else "unsourced_or_illustrative",
        ),
        "as_of_date": pick(
            item.get("as_of_date"),
            base.get("as_of_date"),
            source.get("as_of_date"),
            metadata.get("as_of"),
            payload.get("as_of_date"),
            default="missing",
        ),
    }


def with_source(
    row: dict[str, Any], payload: dict[str, Any], item: dict[str, Any] | None = None
) -> dict[str, Any]:
    row.update(source_context(payload, item))
    return row


def validate_probability_distribution(cases: list[dict[str, Any]]) -> dict[str, Any]:
    values: list[float] = []
    missing: list[str] = []
    invalid: list[str] = []

    for index, case in enumerate(cases):
        label = str(case.get("scenario", f"case_{index + 1}"))
        raw = case.get("probability")
        if raw in (None, ""):
            missing.append(label)
            continue
        parsed = probability_value(raw)
        if parsed is None:
            invalid.append(label)
            continue
        values.append(parsed)

    total = sum(values)
    if missing:
        return {
            "ok": False,
            "status": "missing probabilities: " + ", ".join(missing),
            "sum": total if values else None,
        }
    if invalid:
        return {
            "ok": False,
            "status": "invalid probabilities outside 0.0-1.0: " + ", ".join(invalid),
            "sum": total if values else None,
        }
    if not values:
        return {"ok": False, "status": "missing probabilities", "sum": None}
    if abs(total - 1.0) > PROBABILITY_TOLERANCE:
        return {
            "ok": False,
            "status": f"probabilities must sum to 100%; supplied sum is {total * 100:.1f}%",
            "sum": total,
        }
    return {"ok": True, "status": "ok", "sum": total}


def fmt(value: Any, digits: int = 1) -> str:
    if value is None:
        return "input required"
    if isinstance(value, str):
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(numeric) or math.isinf(numeric):
        return "n/a"
    return f"{numeric:.{digits}f}"


def fmt_pct(value: Any, digits: int = 1) -> str:
    if value is None:
        return "input required"
    try:
        return f"{float(value) * 100:.{digits}f}%"
    except (TypeError, ValueError):
        return str(value)


def fmt_bps(value: Any) -> str:
    if value is None:
        return "input required"
    try:
        return f"{float(value):.0f} bps"
    except (TypeError, ValueError):
        return str(value)


def fmt_multiple(value: Any, digits: int = 1) -> str:
    if value is None:
        return "input required"
    try:
        return f"{float(value):.{digits}f}x"
    except (TypeError, ValueError):
        return str(value)


def return_pct(value: float | None, base_price: float | None) -> float | None:
    if value is None or base_price is None or base_price == 0:
        return None
    return value / base_price - 1


def fmt_ratio(value: float | None) -> str:
    if value is None:
        return "input required"
    return f"{value:.2f}x"


def break_even_probability(
    upside_price: float | None, downside_price: float | None, share_price: float | None
) -> float | None:
    if upside_price is None or downside_price is None or share_price is None:
        return None
    spread = upside_price - downside_price
    if spread == 0:
        return None
    probability = (share_price - downside_price) / spread
    if probability < 0 or probability > 1:
        return None
    return probability


def skew_label(
    expected_return: float | None,
    required_return: float | None,
    downside_upside_ratio: float | None,
) -> str:
    if expected_return is None:
        return "input required"
    hurdle = required_return if required_return is not None else 0.10
    if expected_return >= hurdle and (
        downside_upside_ratio is None or downside_upside_ratio <= 0.75
    ):
        return "underwriteable upside"
    if expected_return > 0:
        return "optical upside / needs proof"
    if expected_return < 0:
        return "negative skew"
    return "balanced / watchlist"


def action_rule(
    return_value: float | None, required_return: float | None, downside_upside_ratio: float | None
) -> str:
    if return_value is None:
        return "input required"
    hurdle = required_return if required_return is not None else 0.10
    if return_value >= hurdle and (downside_upside_ratio is None or downside_upside_ratio <= 0.75):
        return "add / press if evidence confirms"
    if return_value >= 0:
        return "hold / wait for proof"
    if return_value <= -0.15:
        return "trim / exit unless thesis is re-underwritten"
    return "watchlist / re-underwrite"


def table(
    name: str,
    description: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "columns": columns,
        "rows": rows,
        "notes": notes or [],
    }


def build_price_target_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    share_price = number(base, "share_price")
    required_return = number(base, "required_return", number(base, "hurdle_return", 0.10))
    cases = payload.get("cases") or [
        {
            "scenario": "upside",
            "price_target": base.get("upside_price_target"),
            "probability": base.get("upside_probability"),
            "rationale": "upside case",
        },
        {
            "scenario": "base",
            "price_target": base.get("base_price_target"),
            "probability": base.get("base_probability"),
            "rationale": "base case",
        },
        {
            "scenario": "downside",
            "price_target": base.get("downside_price_target"),
            "probability": base.get("downside_probability"),
            "rationale": "downside case",
        },
    ]
    probability_check = validate_probability_distribution(cases)
    prepared_cases = []
    probability_weighted = 0.0
    targets_complete = True
    returns = []
    for case in cases:
        target = number(case, "price_target")
        probability = probability_value(case.get("probability"))
        return_value = return_pct(target, share_price)
        if target is None:
            targets_complete = False
        if return_value is not None:
            returns.append(return_value)
        if target is not None and probability is not None and probability_check["ok"]:
            probability_weighted += target * probability
        prepared_cases.append((case, target, probability, return_value))
    positive_upside = max([ret for ret in returns if ret > 0], default=None)
    downside_abs = abs(min([ret for ret in returns if ret < 0], default=0.0)) if returns else None
    downside_upside_ratio = (
        downside_abs / positive_upside
        if positive_upside not in (None, 0) and downside_abs is not None
        else None
    )
    target_values = [target for _, target, _, _ in prepared_cases if target is not None]
    break_even = break_even_probability(
        max(target_values) if target_values else None,
        min(target_values) if target_values else None,
        share_price,
    )
    rows = []
    for case, target, probability, return_value in prepared_cases:
        rows.append(
            with_source(
                {
                    "scenario": case.get("scenario", "case"),
                    "price_target": fmt(target),
                    "return_vs_share_price": fmt_pct(return_value),
                    "required_return": fmt_pct(required_return),
                    "expected_return_vs_hurdle": fmt_pct(
                        return_value - required_return
                        if return_value is not None and required_return is not None
                        else None
                    ),
                    "downside_upside_ratio": fmt_ratio(downside_upside_ratio),
                    "break_even_probability": fmt_pct(break_even),
                    "skew_label": skew_label(return_value, required_return, downside_upside_ratio),
                    "action_rule": action_rule(
                        return_value, required_return, downside_upside_ratio
                    ),
                    "probability": fmt_pct(probability),
                    "probability_check": probability_check["status"],
                    "probability_sum": fmt_pct(probability_check["sum"]),
                    "rationale": case.get("rationale", ""),
                    "implication": case.get("implication", ""),
                },
                payload,
                case,
            )
        )
    can_weight = probability_check["ok"] and targets_complete
    weighted_return = return_pct(probability_weighted if can_weight else None, share_price)
    rows.append(
        with_source(
            {
                "scenario": "probability_weighted",
                "price_target": fmt(probability_weighted if can_weight else None),
                "return_vs_share_price": fmt_pct(weighted_return),
                "required_return": fmt_pct(required_return),
                "expected_return_vs_hurdle": fmt_pct(
                    weighted_return - required_return
                    if weighted_return is not None and required_return is not None
                    else None
                ),
                "downside_upside_ratio": fmt_ratio(downside_upside_ratio),
                "break_even_probability": fmt_pct(break_even),
                "skew_label": skew_label(weighted_return, required_return, downside_upside_ratio),
                "action_rule": action_rule(weighted_return, required_return, downside_upside_ratio),
                "probability": "n/a",
                "probability_check": probability_check["status"],
                "probability_sum": fmt_pct(probability_check["sum"]),
                "rationale": "weighted by supplied case probabilities",
                "implication": "compare expected return to hurdle and downside/upside skew"
                if can_weight
                else "input required: complete case targets and probabilities summing to 100%",
            },
            payload,
        )
    )
    return table(
        "price_target_scenario",
        "Bull/base/bear price-target, expected return, break-even probability, and skew table.",
        [
            "scenario",
            "price_target",
            "return_vs_share_price",
            "required_return",
            "expected_return_vs_hurdle",
            "downside_upside_ratio",
            "break_even_probability",
            "skew_label",
            "action_rule",
            "probability",
            "probability_check",
            "probability_sum",
            "rationale",
            "implication",
        ]
        + SOURCE_COLUMNS,
        rows,
        [
            "Requires share_price and complete case price targets for calculated return output.",
            "Probability-weighted output requires every case probability to be present and sum to 100%.",
            "Skew labels distinguish underwriteable upside from merely optical upside.",
        ],
    )


def build_valuation_sensitivity(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    ebitda = number(base, "ebitda")
    eps = number(base, "eps", number(base, "ntm_eps"))
    net_debt = number(base, "net_debt", 0.0)
    shares = number(base, "shares_outstanding")
    rows = []
    for multiple in axis(payload, "valuation_multiples"):
        ev_method_price = None
        if ebitda is not None and net_debt is not None and shares not in (None, 0):
            ev_method_price = (ebitda * float(multiple) - net_debt) / shares
        pe_method_price = eps * float(multiple) if eps is not None else None
        rows.append(
            with_source(
                {
                    "multiple": fmt_multiple(multiple),
                    "ev_ebitda_implied_price": fmt(ev_method_price),
                    "pe_implied_price": fmt(pe_method_price),
                    "method_note": "EV/EBITDA requires ebitda, net_debt, shares; P/E requires eps",
                },
                payload,
            )
        )
    return table(
        "valuation_sensitivity",
        "Implied price by valuation multiple.",
        ["multiple", "ev_ebitda_implied_price", "pe_implied_price", "method_note"] + SOURCE_COLUMNS,
        rows,
    )


def build_eps_revision_sensitivity(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    eps = number(base, "eps", number(base, "ntm_eps"))
    base_multiple = number(base, "pe_multiple", number(base, "multiple"))
    rows = []
    for eps_revision in axis(payload, "eps_revisions"):
        for multiple_change in axis(payload, "multiple_changes"):
            revised_eps = eps * (1 + float(eps_revision)) if eps is not None else None
            revised_multiple = (
                base_multiple * (1 + float(multiple_change)) if base_multiple is not None else None
            )
            implied_price = (
                revised_eps * revised_multiple
                if revised_eps is not None and revised_multiple is not None
                else None
            )
            rows.append(
                with_source(
                    {
                        "eps_revision": fmt_pct(eps_revision),
                        "multiple_change": fmt_pct(multiple_change),
                        "revised_eps": fmt(revised_eps, 2),
                        "revised_multiple": fmt_multiple(revised_multiple),
                        "implied_price": fmt(implied_price),
                    },
                    payload,
                )
            )
    return table(
        "eps_revision_sensitivity",
        "Price sensitivity to EPS revisions and multiple change.",
        ["eps_revision", "multiple_change", "revised_eps", "revised_multiple", "implied_price"]
        + SOURCE_COLUMNS,
        rows,
        ["Requires eps and pe_multiple or multiple."],
    )


def build_kpi_driver_sensitivity(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    revenue = number(base, "revenue")
    margin = number(base, "ebit_margin", number(base, "ebitda_margin"))
    flowthrough = number(base, "incremental_margin", margin)
    rows = []
    for revenue_shock in axis(payload, "revenue_growth_shocks"):
        for margin_bps in axis(payload, "margin_shock_bps"):
            revenue_delta = revenue * float(revenue_shock) if revenue is not None else None
            margin_delta = float(margin_bps) / 10000.0
            profit_impact = None
            if revenue is not None and margin is not None:
                base_profit = revenue * margin
                scenario_revenue = revenue * (1 + float(revenue_shock))
                scenario_margin = margin + margin_delta
                profit_impact = scenario_revenue * scenario_margin - base_profit
            rows.append(
                with_source(
                    {
                        "revenue_shock": fmt_pct(revenue_shock),
                        "margin_shock": fmt_bps(margin_bps),
                        "revenue_delta": fmt(revenue_delta),
                        "profit_impact": fmt(profit_impact),
                        "flowthrough_note": "uses margin shock on scenario revenue; incremental margin available separately"
                        if flowthrough is not None
                        else "input required",
                    },
                    payload,
                )
            )
    return table(
        "kpi_driver_sensitivity",
        "Operating KPI sensitivity to revenue and margin shocks.",
        ["revenue_shock", "margin_shock", "revenue_delta", "profit_impact", "flowthrough_note"]
        + SOURCE_COLUMNS,
        rows,
        [
            "Adapt driver names to the relevant sector KPI: NIM, ARR, NRR, NOI, production, loss ratio, take rate, or other key KPI."
        ],
    )


def build_equity_liquidity_downside(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    cash = number(base, "cash")
    revolver = number(base, "revolver_availability")
    minimum_liquidity = number(base, "minimum_liquidity")
    fcf = number(base, "fcf", number(base, "free_cash_flow"))
    maturities = number(base, "maturities_12m")
    debt = number(base, "debt")
    ebitda = number(base, "ebitda")
    rows = []
    for revenue_shock in axis(payload, "revenue_growth_shocks"):
        stressed_fcf = fcf * (1 + float(revenue_shock)) if fcf is not None else None
        liquidity = None
        if any(value is not None for value in [cash, revolver, stressed_fcf, maturities]):
            liquidity = (
                (cash or 0.0) + (revolver or 0.0) + (stressed_fcf or 0.0) - (maturities or 0.0)
            )
        liquidity_headroom = (
            liquidity - minimum_liquidity
            if liquidity is not None and minimum_liquidity is not None
            else None
        )
        leverage = debt / ebitda if debt is not None and ebitda not in (None, 0) else None
        rows.append(
            with_source(
                {
                    "stress_case": f"fcf shock {fmt_pct(revenue_shock)}",
                    "stressed_fcf": fmt(stressed_fcf),
                    "liquidity_after_12m_maturities": fmt(liquidity),
                    "minimum_liquidity": fmt(minimum_liquidity),
                    "liquidity_headroom": fmt(liquidity_headroom),
                    "debt_to_ebitda": fmt_multiple(leverage),
                    "implication": "liquidity breach"
                    if liquidity_headroom is not None and liquidity_headroom < 0
                    else ("liquidity ok" if liquidity_headroom is not None else "input required"),
                },
                payload,
            )
        )
    return table(
        "equity_liquidity_downside",
        "Common-equity liquidity downside stress; route credit-security valuation to Credit Markets.",
        [
            "stress_case",
            "stressed_fcf",
            "liquidity_after_12m_maturities",
            "minimum_liquidity",
            "liquidity_headroom",
            "debt_to_ebitda",
            "implication",
        ]
        + SOURCE_COLUMNS,
        rows,
    )


def build_event_probability_tree(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    share_price = number(base, "share_price", number(base, "unaffected_price"))
    success_price = number(base, "success_price", number(base, "deal_price"))
    fail_price = number(base, "fail_price", number(base, "downside_price_target"))
    rows = []
    for probability in axis(payload, "event_probabilities"):
        parsed_probability = probability_value(probability)
        probability_check = (
            "ok"
            if parsed_probability is not None
            else "invalid probability: use decimal values between 0% and 100%"
        )
        expected_price = None
        if success_price is not None and fail_price is not None and parsed_probability is not None:
            expected_price = (
                parsed_probability * success_price + (1 - parsed_probability) * fail_price
            )
        rows.append(
            with_source(
                {
                    "success_probability": fmt_pct(parsed_probability),
                    "probability_check": probability_check,
                    "success_price": fmt(success_price),
                    "fail_price": fmt(fail_price),
                    "expected_price": fmt(expected_price),
                    "expected_return": fmt_pct(return_pct(expected_price, share_price)),
                    "break_even_probability": fmt_pct(
                        break_even_probability(success_price, fail_price, share_price)
                    ),
                    "skew_label": skew_label(
                        return_pct(expected_price, share_price),
                        number(base, "required_return", number(base, "hurdle_return", 0.10)),
                        None,
                    ),
                    "action_rule": action_rule(
                        return_pct(expected_price, share_price),
                        number(base, "required_return", number(base, "hurdle_return", 0.10)),
                        None,
                    ),
                    "interpretation": "compare expected return to hurdle, timing, borrow, liquidity, downside gap, and exit plan",
                },
                payload,
            )
        )
    return table(
        "event_probability_tree",
        "Probability-weighted event outcome table.",
        [
            "success_probability",
            "probability_check",
            "success_price",
            "fail_price",
            "expected_price",
            "expected_return",
            "break_even_probability",
            "skew_label",
            "action_rule",
            "interpretation",
        ]
        + SOURCE_COLUMNS,
        rows,
        [
            "Requires success_price and fail_price for calculated expected value.",
            "Each event probability is a standalone success-probability case and must be a decimal between 0.0 and 1.0.",
        ],
    )


def build_macro_factor_sensitivity(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload["base"]
    share_price = number(base, "share_price")
    rate_sensitivity = number(base, "rate_sensitivity_pct_per_100bps")
    spread_sensitivity = number(base, "spread_sensitivity_pct_per_100bps")
    rows = []
    for rate_bps in axis(payload, "rate_changes_bps"):
        pct_impact = (
            rate_sensitivity * (float(rate_bps) / 100.0) if rate_sensitivity is not None else None
        )
        price_impact = (
            share_price * pct_impact if share_price is not None and pct_impact is not None else None
        )
        rows.append(
            with_source(
                {
                    "factor": "rates",
                    "factor_move": fmt_bps(rate_bps),
                    "price_impact_pct": fmt_pct(pct_impact),
                    "price_impact": fmt(price_impact),
                    "caveat": "requires rate_sensitivity_pct_per_100bps",
                },
                payload,
            )
        )
    for spread_bps in axis(payload, "spread_changes_bps"):
        pct_impact = (
            spread_sensitivity * (float(spread_bps) / 100.0)
            if spread_sensitivity is not None
            else None
        )
        price_impact = (
            share_price * pct_impact if share_price is not None and pct_impact is not None else None
        )
        rows.append(
            with_source(
                {
                    "factor": "credit_spread",
                    "factor_move": fmt_bps(spread_bps),
                    "price_impact_pct": fmt_pct(pct_impact),
                    "price_impact": fmt(price_impact),
                    "caveat": "requires spread_sensitivity_pct_per_100bps",
                },
                payload,
            )
        )
    return table(
        "macro_factor_sensitivity",
        "Macro/rate/spread sensitivity table.",
        ["factor", "factor_move", "price_impact_pct", "price_impact", "caveat"] + SOURCE_COLUMNS,
        rows,
    )


def build_thesis_trigger_table(payload: dict[str, Any]) -> dict[str, Any]:
    triggers = payload.get("triggers") or []
    rows = []
    if not triggers:
        triggers = [
            {
                "trigger": "estimate revision",
                "threshold": "input required",
                "implication": "confirm or disconfirm thesis",
                "next_step": "equity-model-update",
            },
            {
                "trigger": "valuation support",
                "threshold": "input required",
                "implication": "reassess risk/reward",
                "next_step": "memo-builder",
            },
            {
                "trigger": "downside / stop case",
                "threshold": "input required",
                "implication": "review sizing or hedge",
                "next_step": "portfolio-risk-management",
            },
        ]
    for item in triggers:
        rows.append(
            with_source(
                {
                    "trigger": item.get("trigger", ""),
                    "threshold": item.get("threshold", "input required"),
                    "monitoring_cadence": item.get("monitoring_cadence", item.get("cadence", "")),
                    "implication": item.get("implication", ""),
                    "next_step": item.get("next_step", ""),
                    "source_or_owner": item.get("source_or_owner", item.get("owner", "")),
                },
                payload,
                item,
            )
        )
    return table(
        "thesis_trigger_table",
        "Confirm/disconfirm triggers and next actions.",
        [
            "trigger",
            "threshold",
            "monitoring_cadence",
            "implication",
            "next_step",
            "source_or_owner",
        ]
        + SOURCE_COLUMNS,
        rows,
    )


BUILDERS = {
    "price_target_scenario": build_price_target_scenario,
    "valuation_sensitivity": build_valuation_sensitivity,
    "eps_revision_sensitivity": build_eps_revision_sensitivity,
    "kpi_driver_sensitivity": build_kpi_driver_sensitivity,
    "equity_liquidity_downside": build_equity_liquidity_downside,
    "event_probability_tree": build_event_probability_tree,
    "macro_factor_sensitivity": build_macro_factor_sensitivity,
    "thesis_trigger_table": build_thesis_trigger_table,
}


def select_tables(raw: str) -> list[str]:
    if raw == "all":
        return TABLE_ORDER
    names = [part.strip() for part in raw.split(",") if part.strip()]
    unknown = [name for name in names if name not in BUILDERS]
    if unknown:
        raise ValueError(f"Unknown table(s): {', '.join(unknown)}")
    return names


def render_markdown(tables: list[dict[str, Any]]) -> str:
    chunks = []
    for tbl in tables:
        chunks.append(f"## {tbl['name']}\n")
        chunks.append(f"{tbl['description']}\n")
        columns = tbl["columns"]
        chunks.append("| " + " | ".join(columns) + " |")
        chunks.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in tbl["rows"]:
            chunks.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
        if tbl["notes"]:
            chunks.append("")
            for note in tbl["notes"]:
                chunks.append(f"- {note}")
        chunks.append("")
    return "\n".join(chunks).strip() + "\n"


def primary_source_id(payload: dict[str, Any]) -> str:
    source = payload.get("source", {})
    base = payload.get("base", {})
    metadata = payload.get("metadata", {})
    if not isinstance(source, dict):
        source = {}
    if not isinstance(metadata, dict):
        metadata = {}
    for value in [
        source.get("source_id"),
        base.get("source_id"),
        metadata.get("source_id"),
        payload.get("source_id"),
    ]:
        if value not in (None, "", "missing"):
            return str(value)
    return "S1"


def source_ledger(payload: dict[str, Any]) -> list[dict[str, str]]:
    source = payload.get("source", {})
    base = payload.get("base", {})
    metadata = payload.get("metadata", {})
    if not isinstance(source, dict):
        source = {}
    if not isinstance(metadata, dict):
        metadata = {}
    sid = primary_source_id(payload)
    source_title = (
        source.get("title")
        or source.get("source_name")
        or base.get("source_name")
        or metadata.get("source_name")
    )
    source_as_of = (
        source.get("as_of_date")
        or base.get("as_of_date")
        or metadata.get("as_of")
        or payload.get("as_of_date")
    )
    source_status = (
        source.get("source_posture")
        or base.get("source_posture")
        or metadata.get("source_posture")
        or payload.get("source_posture")
        or ("user_supplied" if source_title and source_as_of else "unsourced_or_illustrative")
    )
    return [
        {
            "id": sid,
            "title": str(source_title or "Scenario sensitivity input package"),
            "as_of": str(source_as_of or "Not provided"),
            "type": str(source.get("source_type") or "user/model input"),
            "status": str(source_status),
            "excerpt": "Scenario, price, probability, hurdle, and source-posture inputs used by the sensitivity materializer.",
        }
    ]


def first_table(tables: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for tbl in tables:
        if tbl.get("name") == name:
            return tbl
    return tables[0] if tables else None


def row_by_scenario(table_obj: dict[str, Any] | None, scenario: str) -> dict[str, Any]:
    if not table_obj:
        return {}
    for row in table_obj.get("rows", []):
        if str(row.get("scenario", "")).lower() == scenario:
            return row
    return {}


def visible_missing_evidence(tables: list[dict[str, Any]], payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    text_blob = json.dumps(tables).lower()
    if "input required" in text_blob:
        issues.append(
            "Some scenario values are input required; do not treat the probability-weighted value as decision-ready until completed."
        )
    if "probabilities must sum" in text_blob or "missing probabilities" in text_blob:
        issues.append("Scenario probabilities are missing, invalid, or do not sum to 100%.")
    source = source_ledger(payload)[0]
    if source["as_of"].lower() in {"not provided", "missing", ""}:
        issues.append(
            "Source as-of date is missing; refresh current price, consensus/model inputs, and probability support."
        )
    if not issues:
        issues.append(
            "Validate current price, probability source, model tie-out, and source freshness before sizing or portfolio action."
        )
    return issues


def classify_readiness(tables: list[dict[str, Any]], payload: dict[str, Any]) -> dict[str, Any]:
    base = payload.get("base", {})
    if not isinstance(base, dict):
        base = {}
    missing_required: list[str] = []
    warnings: list[str] = []

    if not payload.get("_input_was_provided"):
        missing_required.append("input_json")
    if not base:
        missing_required.append("base_case")
    if number(base, "share_price") is None:
        missing_required.append("base.share_price")

    price_table = first_table(tables, "price_target_scenario")
    probability_statuses = {
        str(row.get("probability_check", ""))
        for row in (price_table or {}).get("rows", [])
        if str(row.get("scenario", "")).lower() != "probability_weighted"
    }
    invalid_probability_statuses = [
        status for status in probability_statuses if status and status != "ok"
    ]
    if invalid_probability_statuses:
        missing_required.append("scenario.probabilities")
        warnings.append(
            "Scenario probabilities are missing, invalid, or do not sum to 100%; probability-weighted value is not decision-ready."
        )

    text_blob = json.dumps(tables).lower()
    if "input required" in text_blob:
        warnings.append("One or more scenario outputs contain input required placeholders.")

    source = source_ledger(payload)[0]
    source_missing = source["as_of"].lower() in {"not provided", "missing", ""} or source[
        "status"
    ].lower() in {
        "unsourced_or_illustrative",
        "missing",
        "not provided",
    }
    if source_missing:
        warnings.append(
            "Source/as-of posture is missing or illustrative; cap the output below senior-review-ready."
        )

    if missing_required:
        model_status = "not-decision-ready"
        readiness_effect = "blocked"
        decision_impact = "Do not use for target, rating, sizing, circulation, or PM action until required base-case and probability inputs are supplied."
    elif source_missing:
        model_status = "screen-grade"
        readiness_effect = "screen_grade"
        decision_impact = (
            "Useful for triage, but missing source/as-of support keeps it below decision-grade."
        )
    else:
        model_status = "senior-review-ready"
        readiness_effect = "senior_review_ready"
        decision_impact = "Scenario math, source/as-of posture, current price, and probability checks are complete enough for senior review."

    return {
        "model_status": model_status,
        "readiness_effect": readiness_effect,
        "decision_impact": decision_impact,
        "missing_required_inputs": sorted(set(missing_required)),
        "warnings": sorted(set(warnings)),
        "source_posture": source["status"],
        "probability_validation": "ok"
        if not invalid_probability_statuses
        else "; ".join(sorted(invalid_probability_statuses)),
    }


def build_dashboard_payload(
    tables: list[dict[str, Any]], payload: dict[str, Any], readiness: dict[str, Any] | None = None
) -> dict[str, Any]:
    base = payload.get("base", {})
    if not isinstance(base, dict):
        base = {}
    readiness = readiness or classify_readiness(tables, payload)
    production_ready = readiness["model_status"] == "senior-review-ready"
    sid = primary_source_id(payload)
    price_table = first_table(tables, "price_target_scenario")
    weighted = row_by_scenario(price_table, "probability_weighted")
    rows = price_table.get("rows", []) if price_table else []
    table_columns = price_table.get("columns", []) if price_table else []
    cited_rows = [dict(row, source_id=sid, citations=[sid]) for row in rows]
    scenario_cases = [
        {
            "label": str(row.get("scenario", "case")),
            "status": "base"
            if str(row.get("scenario", "")).lower() == "base"
            else ("bear" if "down" in str(row.get("scenario", "")).lower() else "bull"),
            "summary": f"Value {row.get('price_target', '')}; return {row.get('return_vs_share_price', '')}; action {row.get('action_rule', '')}.",
            "citations": [sid],
        }
        for row in rows
        if str(row.get("scenario", "")).lower() != "probability_weighted"
    ]
    snapshot = [
        {
            "label": "Current price",
            "value": str(base.get("share_price", "input required")),
            "detail": "Spot anchor for return and break-even math.",
            "status": "neutral",
            "citations": [sid],
        },
        {
            "label": "Probability-weighted value",
            "value": str(weighted.get("price_target", "input required")),
            "detail": "Valid only when probabilities are complete and sum to 100%.",
            "status": "watch",
            "citations": [sid],
        },
        {
            "label": "Expected return vs hurdle",
            "value": str(weighted.get("expected_return_vs_hurdle", "input required")),
            "detail": "Compares expected return to the PM hurdle.",
            "status": "watch",
            "citations": [sid],
        },
        {
            "label": "Downside/upside ratio",
            "value": str(weighted.get("downside_upside_ratio", "input required")),
            "detail": "Measures whether downside overwhelms upside.",
            "status": "risk",
            "citations": [sid],
        },
        {
            "label": "Break-even probability",
            "value": str(weighted.get("break_even_probability", "input required")),
            "detail": "Probability needed to justify current price.",
            "status": "neutral",
            "citations": [sid],
        },
        {
            "label": "Skew label",
            "value": str(weighted.get("skew_label", "input required")),
            "detail": "PM interpretation of underwriteable versus optical upside.",
            "status": "watch",
            "citations": [sid],
        },
        {
            "label": "PM action",
            "value": str(weighted.get("action_rule", "input required")),
            "detail": "Add, hold, trim, exit, wait for proof, or re-underwrite rule.",
            "status": "neutral",
            "citations": [sid],
        },
    ]
    return {
        "kind": "public_equity_investing_dashboard.v1",
        "mode": "scenario_sensitivity",
        "layout": "single_page",
        "title": f"{base.get('ticker') or base.get('issuer') or 'Issuer'} Scenario Sensitivity Dashboard",
        "subtitle": "Decision infrastructure for public-equity scenario skew, thresholds, and source posture.",
        "issuer": {
            "ticker": str(base.get("ticker") or "TBD"),
            "name": str(base.get("issuer") or base.get("company") or "Scenario issuer"),
        },
        "metadata": {
            "freeze_time": str(
                base.get("freeze_time")
                or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            ),
            "source_posture": str(source_ledger(payload)[0]["status"]),
            "citation_policy": "strict" if production_ready else "warn",
            "decision_context": "Does probability-weighted upside clear the hurdle after downside, evidence quality, and missing inputs?",
            "payload_stage": "production" if production_ready else "draft",
            "readiness_label": "Scenario sensitivity production payload"
            if production_ready
            else "Scenario sensitivity draft payload; missing evidence visible",
            "readiness_posture": "senior_review_ready"
            if production_ready
            else readiness["readiness_effect"],
            "model_status": readiness["model_status"],
            "decision_impact": readiness["decision_impact"],
            "missing_required_inputs": readiness["missing_required_inputs"],
            "probability_validation": readiness["probability_validation"],
        },
        "hero": {
            "eyebrow": "Scenario sensitivity",
            "headline": "Scenario table anchors current price, expected return, skew, and action thresholds",
            "dek": "Raw JSON/CSV/Markdown tables remain support artifacts; the dashboard surfaces PM decision logic.",
            "callout_label": "PM action",
            "callout": str(weighted.get("action_rule", "wait for proof until inputs are complete")),
            "citations": [sid],
        },
        "snapshot": snapshot,
        "tabs": [
            {
                "id": "pm-decision",
                "label": "PM Decision",
                "modules": [
                    {
                        "type": "decision_box",
                        "data": {
                            "label": "Scenario read",
                            "stance": str(weighted.get("action_rule", "Wait for proof")),
                            "summary": f"Probability-weighted value is {weighted.get('price_target', 'input required')} with expected return versus hurdle of {weighted.get('expected_return_vs_hurdle', 'input required')}.",
                            "stock_skew": str(weighted.get("skew_label", "input required")),
                            "citations": [sid],
                        },
                    },
                    {"type": "metric_tiles", "data": {"items": snapshot}},
                ],
            },
            {
                "id": "scenario-map",
                "label": "Scenario Map",
                "modules": [
                    {
                        "type": "scenario_map",
                        "data": {
                            "cases": scenario_cases
                            or [
                                {
                                    "label": "Input required",
                                    "status": "watch",
                                    "summary": "Add scenario rows before relying on the dashboard.",
                                    "citations": [sid],
                                }
                            ]
                        },
                    },
                    {"type": "table", "data": {"columns": table_columns, "rows": cited_rows}},
                ],
            },
            {
                "id": "evidence-and-qa",
                "label": "Evidence & QA",
                "modules": [
                    {"type": "source_list", "data": {"sources": source_ledger(payload)}},
                    {
                        "type": "missing_evidence",
                        "data": {"items": visible_missing_evidence(tables, payload)},
                    },
                ],
            },
        ],
        "sources": source_ledger(payload),
    }


def write_csv(table_obj: dict[str, Any], output: str | None) -> None:
    handle = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout
    close = output is not None
    try:
        writer = csv.DictWriter(handle, fieldnames=table_obj["columns"])
        writer.writeheader()
        writer.writerows(table_obj["rows"])
    finally:
        if close:
            handle.close()


def run_log_path(output: str | None, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    if output:
        return Path(output).resolve().parent / "run_log.json"
    return None


def write_run_log(
    path: Path | None,
    *,
    status: str,
    output: str | None,
    output_format: str,
    table_names: list[str],
    source_basis: dict[str, Any],
    warnings: list[str],
    hard_failures: list[str],
    readiness: dict[str, Any] | None = None,
) -> None:
    if path is None:
        return
    readiness = readiness or {
        "model_status": "not-decision-ready" if hard_failures else "screen-grade",
        "readiness_effect": "blocked" if hard_failures else "screen_grade",
        "decision_impact": "Readiness could not be classified; treat as support only.",
        "missing_required_inputs": [],
        "warnings": [],
        "source_posture": source_basis.get("source_posture")
        if isinstance(source_basis, dict)
        else "",
        "probability_validation": "not_checked",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    outputs = {
        "primary": str(Path(output).resolve()) if output else "stdout",
        "run_log": str(path),
        "manifest": str(path.parent / "manifest.json"),
    }
    output_manifest = [
        {
            "key": key,
            "path": artifact_path,
            "required": key != "primary" or bool(output),
            "written": key in {"run_log", "manifest"}
            or (bool(output) and Path(artifact_path).exists()),
            "description": "Scenario-sensitivity deterministic artifact.",
            "artifact_role": "narrative_support"
            if key == "primary" and output_format == "markdown"
            else "support_artifact",
            "hidden_unless_requested": key == "primary" or key in {"run_log", "manifest"},
        }
        for key, artifact_path in outputs.items()
    ]
    payload = {
        "status": status,
        "model_status": "not-decision-ready" if hard_failures else readiness["model_status"],
        "readiness_effect": readiness["readiness_effect"],
        "decision_impact": readiness["decision_impact"],
        "missing_required_inputs": readiness["missing_required_inputs"],
        "source_posture": readiness["source_posture"],
        "probability_validation": readiness["probability_validation"],
        "artifact_level": "deterministic_export",
        "workbook_mode": f"{output_format}_export",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tables": table_names,
        "source_basis": [source_basis] if source_basis else [],
        "warnings": sorted(set(warnings + list(readiness.get("warnings", [])))),
        "hard_failures": hard_failures,
        "outputs": outputs,
        "primary_human_deliverable": None,
        "support_artifacts": [artifact_path for artifact_path in outputs.values() if artifact_path],
        "support_artifacts_user_visible_default": False,
        "final_response_guidance": {
            "lead_with": "html_dashboard_or_workbook_when_available",
            "mention_support_artifacts": "only_briefly_unless_requested",
        },
        "output_manifest": output_manifest,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (path.parent / "manifest.json").write_text(
        json.dumps(
            {
                "outputs": output_manifest,
                "primary_human_deliverable": None,
                "support_artifacts_user_visible_default": False,
                "final_response_guidance": payload["final_response_guidance"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize Public Equity Investing sensitivity tables."
    )
    parser.add_argument("--input", help="Optional JSON input file.")
    parser.add_argument("--tables", default="all", help="Comma-separated table names or 'all'.")
    parser.add_argument("--format", choices=["markdown", "json", "csv"], default="json")
    parser.add_argument("--output", help="Optional output path. CSV supports one table at a time.")
    parser.add_argument(
        "--dashboard-output",
        help="Optional production dashboard payload JSON path for scenario_sensitivity.",
    )
    parser.add_argument(
        "--run-log",
        help="Optional run log path. Defaults to output directory when --output is used.",
    )
    args = parser.parse_args()

    log_path = run_log_path(args.output, args.run_log)
    try:
        payload = load_payload(args.input)
        names = select_tables(args.tables)
        tables = [BUILDERS[name](payload) for name in names]
        readiness = classify_readiness(tables, payload)
    except Exception as exc:
        write_run_log(
            log_path,
            status="failed",
            output=args.output,
            output_format=args.format,
            table_names=[],
            source_basis={},
            warnings=[],
            hard_failures=[str(exc)],
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        if args.format == "json":
            text = json.dumps({"tables": tables}, indent=2)
            if args.output:
                Path(args.output).write_text(text + "\n", encoding="utf-8")
            else:
                print(text)
        elif args.format == "markdown":
            text = render_markdown(tables)
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
            else:
                print(text, end="")
        else:
            if len(tables) != 1:
                failure = "CSV output supports exactly one table. Pass --tables <single_table>."
                write_run_log(
                    log_path,
                    status="failed",
                    output=args.output,
                    output_format=args.format,
                    table_names=names,
                    source_basis=payload.get("source", {}),
                    warnings=[],
                    hard_failures=[failure],
                )
                print(f"ERROR: {failure}", file=sys.stderr)
                return 1
            write_csv(tables[0], args.output)
        if args.dashboard_output:
            dashboard_payload = build_dashboard_payload(tables, payload, readiness)
            Path(args.dashboard_output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.dashboard_output).write_text(
                json.dumps(dashboard_payload, indent=2) + "\n", encoding="utf-8"
            )
    except Exception as exc:
        failure = f"could not write output: {exc}"
        write_run_log(
            log_path,
            status="failed",
            output=args.output,
            output_format=args.format,
            table_names=names,
            source_basis=payload.get("source", {}),
            warnings=[],
            hard_failures=[failure],
            readiness=readiness,
        )
        print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    write_run_log(
        log_path,
        status="completed",
        output=args.output,
        output_format=args.format,
        table_names=names,
        source_basis=payload.get("source", {}),
        warnings=[],
        hard_failures=[],
        readiness=readiness,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
