"""Risk-position-sizing calculation helpers.

This module owns the sizing math only. The CLI wrapper owns input/output and
run-log behavior.
"""

from __future__ import annotations

from typing import Any


def fnum(x: Any, default: float | None = None) -> float | None:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except (TypeError, ValueError):
        return default


def safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return a / b


def pct_to_notional(pct: float | None, nav: float) -> float | None:
    return None if pct is None else nav * pct / 100.0


def notional_to_pct(notional: float | None, nav: float) -> float | None:
    return None if notional is None else notional / nav * 100.0


def signed_return(direction: str, entry: float, price: float) -> float:
    raw = price / entry - 1.0
    return -raw if direction.lower() == "short" else raw


def confidence_multiplier(label: str) -> float:
    label = (label or "medium").lower()
    return {"high": 1.0, "medium": 0.75, "low": 0.50}.get(label, 0.75)


CREDIT_ROUTE_MESSAGE = (
    "Use Credit Markets for CDS, bonds, loans, spread DV01/CS01, "
    "capital-structure, distressed, recovery, covenant, or debt-security sizing. "
    "Public Equity Investing may use CDS/spreads only as common-equity risk context."
)

CREDIT_INSTRUMENT_PATTERNS = {
    "cds",
    "credit default swap",
    "bond",
    "bonds",
    "note",
    "notes",
    "debenture",
    "loan",
    "loans",
    "bank loan",
    "leveraged loan",
    "term loan",
    "high yield",
    "investment grade",
    "spread dv01",
    "spread_dv01",
    "cs01",
    "dv01",
    "capital structure",
    "capital-structure",
    "distressed debt",
    "distressed claim",
    "recovery waterfall",
    "covenant",
    "credit security",
    "credit instrument",
}


def _normalized_text(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", " ").replace("/", " ").replace("-", " ")


def is_credit_like_instrument(value: Any) -> bool:
    text = _normalized_text(value)
    if not text:
        return False
    return any(
        pattern.replace("_", " ").replace("-", " ") in text
        for pattern in CREDIT_INSTRUMENT_PATTERNS
    )


def _route_credit_instruments(position: dict[str, Any]) -> None:
    for field in ["instrument_type", "security_type", "asset_class", "hedge_type", "instrument"]:
        if is_credit_like_instrument(position.get(field)):
            raise ValueError(CREDIT_ROUTE_MESSAGE)


def _required_portfolio_inputs(
    portfolio: dict[str, Any], position: dict[str, Any]
) -> tuple[float, float, str]:
    nav = fnum(portfolio.get("nav"))
    entry = fnum(position.get("entry_price"))
    if not nav or nav <= 0:
        raise ValueError("portfolio.nav must be a positive number")
    if not entry or entry <= 0:
        raise ValueError("position.entry_price must be a positive number")
    return nav, entry, str(position.get("direction", "long")).lower()


def _loss_budget_rows(
    portfolio: dict[str, Any],
    position: dict[str, Any],
    nav: float,
    entry: float,
    direction: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    loss_bps = fnum(portfolio.get("max_loss_bps_nav"))
    loss_budget = nav * loss_bps / 10000.0 if loss_bps is not None else None
    loss_cases = [
        ("loss_budget_downside", "downside_price"),
        ("loss_budget_stress", "stress_price"),
    ]
    for case_name, field in loss_cases:
        price = fnum(position.get(field))
        if loss_budget is None or price is None:
            continue
        move = abs(signed_return(direction, entry, price))
        notional = safe_div(loss_budget, move)
        rows.append(
            {
                "sizing_lens": case_name,
                "input_value": f"{loss_bps} bps NAV loss budget; {field}={price}",
                "formula": "loss budget dollars / absolute adverse return",
                "implied_size_pct_nav": notional_to_pct(notional, nav),
                "implied_notional": notional,
                "binding_flag": "",
                "notes": "Use stress case for binary, crowded, or illiquid trades.",
            }
        )
    return rows


def _volatility_budget_rows(
    portfolio: dict[str, Any], position: dict[str, Any], nav: float
) -> list[dict[str, Any]]:
    vol_pct = fnum(position.get("annualized_volatility_pct"))
    vol_budget_bps = fnum(portfolio.get("target_position_vol_contribution_bps"))
    if not vol_pct or not vol_budget_bps:
        return []
    vol_budget = nav * vol_budget_bps / 10000.0
    notional = vol_budget / (vol_pct / 100.0)
    return [
        {
            "sizing_lens": "volatility_budget",
            "input_value": f"{vol_budget_bps} bps NAV vol budget; {vol_pct}% annualized vol",
            "formula": "vol budget dollars / annualized volatility",
            "implied_size_pct_nav": notional_to_pct(notional, nav),
            "implied_notional": notional,
            "binding_flag": "",
            "notes": "Standalone approximation; factor model preferred when available.",
        }
    ]


def _liquidity_capacity_rows(
    liquidity: dict[str, Any], nav: float, entry: float
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    adv = fnum(liquidity.get("adv_shares"))
    liq_price = fnum(liquidity.get("price"), entry)
    exit_days = fnum(liquidity.get("required_exit_days"), 5.0) or 5.0
    if not adv or not liq_price:
        return []
    liquidity_cases = [
        ("liquidity_normal_exit", "normal_participation_rate", 0.10),
        ("liquidity_stress_exit", "stress_participation_rate", 0.05),
    ]
    for lens, part_field, default in liquidity_cases:
        part = fnum(liquidity.get(part_field), default) or default
        notional = adv * liq_price * part * exit_days
        rows.append(
            {
                "sizing_lens": lens,
                "input_value": f"ADV={adv}; participation={part}; days={exit_days}",
                "formula": "ADV x price x participation x exit days",
                "implied_size_pct_nav": notional_to_pct(notional, nav),
                "implied_notional": notional,
                "binding_flag": "",
                "notes": "Adjust downward for blocks, crowding, gap risk, or poor borrow/options liquidity.",
            }
        )
    return rows


def _limit_capacity_rows(
    portfolio: dict[str, Any], position: dict[str, Any], nav: float
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    max_single = fnum(portfolio.get("max_single_name_pct_nav"))
    current_pct = fnum(position.get("current_size_pct_nav"), 0.0) or 0.0
    if max_single is not None:
        cap = max(0.0, max_single - current_pct)
        rows.append(
            {
                "sizing_lens": "single_name_limit_capacity",
                "input_value": f"limit={max_single}% NAV; current={current_pct}% NAV",
                "formula": "single-name limit minus current issuer exposure",
                "implied_size_pct_nav": cap,
                "implied_notional": pct_to_notional(cap, nav),
                "binding_flag": "",
                "notes": "Limit capacity is a cap, not a sizing target.",
            }
        )

    sector_limit = fnum(
        position.get("sector_limit_pct_nav"),
        fnum(portfolio.get("max_sector_exposure_pct_nav")),
    )
    sector_current = fnum(position.get("current_sector_exposure_pct_nav"))
    if sector_limit is not None and sector_current is not None:
        cap = max(0.0, sector_limit - sector_current)
        rows.append(
            {
                "sizing_lens": "sector_limit_capacity",
                "input_value": f"limit={sector_limit}% NAV; current={sector_current}% NAV",
                "formula": "sector limit minus current sector exposure",
                "implied_size_pct_nav": cap,
                "implied_notional": pct_to_notional(cap, nav),
                "binding_flag": "",
                "notes": "Check correlated names before relying on this capacity.",
            }
        )
    return rows


def _pm_constraint_rows(
    portfolio: dict[str, Any],
    position: dict[str, Any],
    liquidity: dict[str, Any],
    nav: float,
    direction: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_pct = fnum(position.get("current_size_pct_nav"), 0.0) or 0.0

    active_limit = fnum(
        position.get("benchmark_active_weight_limit_pct"),
        fnum(
            portfolio.get("benchmark_active_weight_limit_pct"),
            fnum(portfolio.get("max_active_weight_pct")),
        ),
    )
    current_active = (
        fnum(
            position.get("current_active_weight_pct"),
            fnum(portfolio.get("current_active_weight_pct"), 0.0),
        )
        or 0.0
    )
    if active_limit is not None:
        cap = max(0.0, active_limit - abs(current_active))
        rows.append(
            {
                "sizing_lens": "benchmark_active_weight_capacity",
                "input_value": f"active_weight_limit={active_limit}% NAV; current_active_weight={current_active}% NAV",
                "formula": "active-weight limit minus absolute current active weight",
                "implied_size_pct_nav": cap,
                "implied_notional": pct_to_notional(cap, nav),
                "binding_flag": "",
                "notes": "Long-only and benchmark-aware PMs should size against active risk, not only absolute loss.",
            }
        )

    factor_limit = fnum(
        position.get("factor_limit_pct_nav"), fnum(portfolio.get("factor_limit_pct_nav"))
    )
    current_factor = fnum(position.get("current_factor_exposure_pct_nav"), 0.0) or 0.0
    factor_per_pct = (
        fnum(position.get("factor_exposure_per_1pct_position"), fnum(position.get("beta"), 1.0))
        or 1.0
    )
    if factor_limit is not None and factor_per_pct:
        cap = max(0.0, (factor_limit - abs(current_factor)) / abs(factor_per_pct))
        rows.append(
            {
                "sizing_lens": "factor_limit_capacity",
                "input_value": f"factor_limit={factor_limit}% NAV-equivalent; current={current_factor}; exposure_per_1pct={factor_per_pct}",
                "formula": "(factor limit minus current factor exposure) / factor exposure per 1% position",
                "implied_size_pct_nav": cap,
                "implied_notional": pct_to_notional(cap, nav),
                "binding_flag": "",
                "notes": "Use a real factor model where available; this is a PM guardrail for unwanted factor exposure.",
            }
        )

    correlation_limit = fnum(
        position.get("correlated_exposure_limit_pct_nav"),
        fnum(portfolio.get("correlated_exposure_limit_pct_nav")),
    )
    current_correlated = fnum(position.get("current_correlated_exposure_pct_nav"), 0.0) or 0.0
    correlation = abs(fnum(position.get("correlation_to_existing_book"), 1.0) or 1.0)
    if correlation_limit is not None:
        cap = max(0.0, (correlation_limit - current_correlated) / max(correlation, 0.01))
        rows.append(
            {
                "sizing_lens": "portfolio_fit_correlation_capacity",
                "input_value": f"correlated_exposure_limit={correlation_limit}% NAV; current={current_correlated}% NAV; correlation={correlation}",
                "formula": "(correlated exposure limit minus current correlated exposure) / correlation",
                "implied_size_pct_nav": cap,
                "implied_notional": pct_to_notional(cap, nav),
                "binding_flag": "",
                "notes": "Prevents a new name from becoming an accidental crowded factor/cluster bet.",
            }
        )

    if direction == "short":
        borrow_capacity = fnum(
            position.get("borrow_squeeze_capacity_pct_nav"),
            fnum(
                portfolio.get("borrow_squeeze_capacity_pct_nav"),
                fnum(portfolio.get("max_short_position_pct_nav")),
            ),
        )
        if borrow_capacity is not None:
            short_interest = fnum(
                position.get("short_interest_pct_float"),
                fnum(liquidity.get("short_interest_pct_float")),
            )
            days_to_cover = fnum(
                position.get("days_to_cover"), fnum(liquidity.get("days_to_cover"))
            )
            borrow_cost = fnum(
                position.get("borrow_cost_pct"), fnum(liquidity.get("borrow_cost_pct"))
            )
            cap = max(0.0, borrow_capacity - current_pct)
            rows.append(
                {
                    "sizing_lens": "borrow_squeeze_capacity",
                    "input_value": f"short_capacity={borrow_capacity}% NAV; current={current_pct}% NAV; short_interest={short_interest}; days_to_cover={days_to_cover}; borrow_cost={borrow_cost}",
                    "formula": "borrow/squeeze capacity minus current short exposure",
                    "implied_size_pct_nav": cap,
                    "implied_notional": pct_to_notional(cap, nav),
                    "binding_flag": "",
                    "notes": "Short sizing must account for borrow availability, borrow cost, crowding, buyback/low-float risk, and squeeze path.",
                }
            )
    return rows


def _binding_constraint(rows: list[dict[str, Any]]) -> tuple[float | None, str]:
    candidates = [
        (fnum(r.get("implied_size_pct_nav")), r["sizing_lens"])
        for r in rows
        if fnum(r.get("implied_size_pct_nav")) and fnum(r.get("implied_size_pct_nav")) > 0
    ]
    return min(candidates, key=lambda x: x[0]) if candidates else (None, "insufficient data")


def _summary(
    position: dict[str, Any],
    data: dict[str, Any],
    nav: float,
    entry: float,
    direction: str,
    raw_pct: float | None,
    binding: str,
) -> dict[str, Any]:
    current_pct = fnum(position.get("current_size_pct_nav"), 0.0) or 0.0
    confidence = str(position.get("confidence", "medium"))
    mult = confidence_multiplier(confidence)
    recommended_pct = raw_pct * mult if raw_pct is not None else None
    recommended_notional = pct_to_notional(recommended_pct, nav)
    return {
        "analysis_date": data.get("analysis_date", ""),
        "security": position.get("security", ""),
        "ticker": position.get("ticker", ""),
        "direction": direction,
        "entry_price": entry,
        "recommended_size_pct_nav": recommended_pct,
        "recommended_notional": recommended_notional,
        "recommended_shares_or_units": safe_div(recommended_notional, entry),
        "raw_binding_constraint": binding,
        "raw_binding_size_pct_nav": raw_pct,
        "confidence": confidence,
        "proposed_size_pct_nav": fnum(position.get("proposed_size_pct_nav")),
        "current_size_pct_nav": current_pct,
        "nav": nav,
    }


def _confidence_adjustment_row(summary: dict[str, Any]) -> dict[str, Any]:
    confidence = str(summary.get("confidence", "medium"))
    mult = confidence_multiplier(confidence)
    return {
        "sizing_lens": "confidence_adjustment",
        "input_value": confidence,
        "formula": "raw binding size x confidence multiplier",
        "implied_size_pct_nav": summary.get("recommended_size_pct_nav"),
        "implied_notional": summary.get("recommended_notional"),
        "binding_flag": "final_adjustment"
        if summary.get("recommended_size_pct_nav") is not None
        else "",
        "notes": f"Multiplier={mult}; PM may override based on evidence quality and mandate.",
    }


def sizing_rows(data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    portfolio = data.get("portfolio", {})
    position = data.get("position", {})
    _route_credit_instruments(position)
    liquidity = data.get("liquidity", {})
    nav, entry, direction = _required_portfolio_inputs(portfolio, position)

    rows: list[dict[str, Any]] = []
    rows.extend(_loss_budget_rows(portfolio, position, nav, entry, direction))
    rows.extend(_volatility_budget_rows(portfolio, position, nav))
    rows.extend(_liquidity_capacity_rows(liquidity, nav, entry))
    rows.extend(_limit_capacity_rows(portfolio, position, nav))
    rows.extend(_pm_constraint_rows(portfolio, position, liquidity, nav, direction))

    raw_pct, binding = _binding_constraint(rows)
    for row in rows:
        if row["sizing_lens"] == binding:
            row["binding_flag"] = "raw_binding_constraint"

    summary = _summary(position, data, nav, entry, direction, raw_pct, binding)
    rows.append(_confidence_adjustment_row(summary))
    return rows, summary


def scenario_rows(data: dict[str, Any], summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    notional = summary.get("recommended_notional")
    nav = summary["nav"]
    for scenario in data.get("scenarios", []):
        price = fnum(scenario.get("price"))
        ret = fnum(scenario.get("return_pct"))
        if price is not None:
            result_return = signed_return(summary["direction"], summary["entry_price"], price)
        elif ret is not None:
            result_return = ret / 100.0
            price = summary["entry_price"] * (1.0 + result_return)
        else:
            continue
        pnl = notional * result_return if notional is not None else None
        rows.append(
            {
                "scenario": scenario.get("name", "scenario"),
                "probability": scenario.get("probability", ""),
                "price_or_return": price,
                "pnl_dollars": pnl,
                "pnl_pct_nav": notional_to_pct(pnl, nav),
                "time_horizon": scenario.get("time_horizon", ""),
                "liquidity_assumption": scenario.get("liquidity_assumption", ""),
                "action_rule": scenario.get("action_rule", ""),
                "notes": scenario.get("notes", ""),
            }
        )
    return rows


def exposure_rows(data: dict[str, Any], summary: dict[str, Any]) -> list[dict[str, Any]]:
    portfolio = data.get("portfolio", {})
    position = data.get("position", {})
    recommended_pct = summary.get("recommended_size_pct_nav") or 0.0
    sign = -1 if summary["direction"] == "short" else 1
    beta = fnum(position.get("beta"), 1.0) or 1.0
    rows = []
    exposure_cases = [
        ("gross_exposure_pct_nav", fnum(portfolio.get("current_gross_exposure_pct"))),
        ("net_exposure_pct_nav", fnum(portfolio.get("current_net_exposure_pct"))),
        (
            "active_weight_pct_nav",
            fnum(
                position.get("current_active_weight_pct"),
                fnum(portfolio.get("current_active_weight_pct")),
            ),
        ),
        ("factor_exposure_pct_nav", fnum(position.get("current_factor_exposure_pct_nav"))),
        ("correlated_exposure_pct_nav", fnum(position.get("current_correlated_exposure_pct_nav"))),
    ]
    for name, before in exposure_cases:
        if before is None:
            continue
        incremental = abs(recommended_pct) if name.startswith("gross") else sign * recommended_pct
        rows.append(
            {
                "exposure_type": name,
                "before": before,
                "incremental": incremental,
                "after": before + incremental,
                "limit": "",
                "status": "informational",
                "source": "input",
            }
        )
    rows.append(
        {
            "exposure_type": "beta_adjusted_incremental_pct_nav",
            "before": "",
            "incremental": sign * recommended_pct * beta,
            "after": "",
            "limit": "",
            "status": "check risk model if available",
            "source": "input beta or default",
        }
    )
    return rows


def liquidity_rows(data: dict[str, Any], summary: dict[str, Any]) -> list[dict[str, Any]]:
    liquidity = data.get("liquidity", {})
    price = fnum(liquidity.get("price"), summary["entry_price"])
    adv = fnum(liquidity.get("adv_shares"))
    notional = summary.get("recommended_notional")
    if not price or not adv or notional is None:
        return []
    shares = notional / price
    normal_participation = fnum(liquidity.get("normal_participation_rate"), 0.10) or 0.10
    stress_participation = fnum(liquidity.get("stress_participation_rate"), 0.05) or 0.05
    return [
        {
            "security": summary.get("security", ""),
            "price": price,
            "adv_shares": adv,
            "adv_dollars": adv * price,
            "position_shares": shares,
            "position_dollars": notional,
            "position_pct_nav": summary.get("recommended_size_pct_nav"),
            "participation_rate": normal_participation,
            "days_to_exit": safe_div(shares, adv * normal_participation),
            "stressed_participation_rate": stress_participation,
            "stressed_days_to_exit": safe_div(shares, adv * stress_participation),
            "notes": "Simple ADV participation math; validate block liquidity and market impact.",
        }
    ]


def monitoring_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    fields = [
        "trigger_type",
        "metric",
        "threshold",
        "action",
        "owner",
        "cadence",
        "source",
    ]
    return [
        {field: trigger.get(field, "") for field in fields}
        for trigger in data.get("monitoring_triggers", [])
    ]
