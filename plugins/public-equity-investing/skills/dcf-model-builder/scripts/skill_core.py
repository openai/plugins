#!/usr/bin/env python3
"""Deterministic DCF model engine for dcf-model-builder.

Standard library only. No network calls. No hidden randomness.
"""

from __future__ import annotations

import copy
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from plan_validation import validate_plan_structure_without_computed_checks

ALLOWED_LABELS = {
    "reported",
    "company_guidance",
    "consensus",
    "management_case",
    "user_provided",
    "connected_app",
    "web_research",
    "analyst_estimate",
    "placeholder",
    "derived",
}

REQUIRED_SOURCE_TOPICS = {
    "historicals",
    "forecast",
    "wacc",
    "terminal_value",
    "share_count",
    "net_debt",
}

MODEL_STATUS_VALUES = {
    "decision-grade",
    "senior-review-ready",
    "screen-grade",
    "not-decision-ready",
    "blocked",
}

REQUIRED_TOP_LEVEL = [
    "meta",
    "source_basis",
    "timeline",
    "historicals",
    "forecast",
    "wacc",
    "terminal_value",
    "ev_to_equity_bridge",
    "scenarios",
    "sensitivities",
]

SCENARIOS = ["base", "downside", "upside"]


def load_json(path: str | os.PathLike[str]) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | os.PathLike[str], obj: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _date_ok(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except Exception:
        return None


def _num(value: Any, default: float = 0.0) -> float:
    if _is_number(value):
        return float(value)
    return float(default)


def _get(plan: dict[str, Any], dotted: str, default: Any = None) -> Any:
    node: Any = plan
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def _source_map(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(s.get("id")): s for s in plan.get("source_basis", []) if isinstance(s, dict)}


def _source_label(plan: dict[str, Any], source_id: str | None) -> str:
    if not source_id:
        return ""
    src = _source_map(plan).get(source_id)
    if not src:
        return ""
    return str(src.get("label", ""))


def _source_for_topic(plan: dict[str, Any], topic: str) -> dict[str, Any] | None:
    for src in plan.get("source_basis", []):
        if isinstance(src, dict) and src.get("topic") == topic:
            return src
    return None


def _vector(value: Any, horizon: int, field_name: str) -> list[float]:
    if isinstance(value, list):
        return [float(v) for v in value]
    if _is_number(value):
        return [float(value)] * horizon
    raise ValueError(f"{field_name} must be a number or list of numbers")


def _validate_vector(
    errors: list[str],
    value: Any,
    path: str,
    horizon: int,
    min_value: float | None = None,
    max_value: float | None = None,
    allow_scalar: bool = True,
) -> None:
    if isinstance(value, list):
        if len(value) != horizon:
            errors.append(f"{path} must contain exactly {horizon} values; found {len(value)}")
            return
        values = value
    elif allow_scalar and _is_number(value):
        values = [value]
    else:
        errors.append(f"{path} must be a number or list of numbers")
        return
    for idx, item in enumerate(values):
        loc = f"{path}[{idx}]" if isinstance(value, list) else path
        if not _is_number(item):
            errors.append(f"{loc} must be numeric")
            continue
        f = float(item)
        if min_value is not None and f < min_value:
            errors.append(f"{loc} must be >= {min_value}")
        if max_value is not None and f > max_value:
            errors.append(f"{loc} must be <= {max_value}")


def validate_plan_structure(plan: dict[str, Any]) -> list[str]:
    """Return actionable validation errors. Does not compute model outputs."""
    errors = validate_plan_structure_without_computed_checks(plan)
    if errors:
        return errors

    try:
        wacc_info = compute_wacc(plan, "base")
        discount_rate = (
            wacc_info["wacc"]
            if plan["forecast"].get("cash_flow_basis") == "fcff"
            else wacc_info["cost_of_equity"]
        )
        if discount_rate <= 0:
            errors.append("computed discount rate must be greater than zero")
        terminal_growth = _num(
            plan["scenarios"]["base"].get(
                "terminal_growth_rate",
                plan["terminal_value"].get("perpetual_growth_rate"),
            ),
            0.0,
        )
        if (
            plan["terminal_value"].get("method") == "perpetual_growth"
            and discount_rate <= terminal_growth
        ):
            errors.append("computed discount rate must exceed terminal growth rate")
    except Exception as exc:
        errors.append(f"could not compute WACC/terminal validation: {exc}")
    return errors


def normalize_plan(
    plan: dict[str, Any], skill_root: str | os.PathLike[str] | None = None
) -> dict[str, Any]:
    """Return a normalized copy without changing conclusion-driving assumptions."""
    normalized = copy.deepcopy(plan)
    notes: list[str] = []
    wacc = normalized.setdefault("wacc", {})
    for field in [
        "company_specific_premium",
        "country_risk_premium",
        "preferred_pct",
        "pre_tax_cost_of_preferred",
    ]:
        if field not in wacc:
            wacc[field] = 0.0
            notes.append(f"wacc.{field} was absent and was set to 0.0 for calculation transparency")
    bridge = normalized.setdefault("ev_to_equity_bridge", {})
    for field in [
        "cash",
        "debt",
        "leases",
        "minorities",
        "associates",
        "pensions",
        "preferred_stock",
        "non_operating_assets",
        "options",
        "other_debt_like_items",
    ]:
        if field not in bridge:
            bridge[field] = 0.0
            notes.append(f"ev_to_equity_bridge.{field} was absent and was set to 0.0")
    normalized["_normalization_notes"] = notes
    if skill_root is not None:
        normalized["_skill_root"] = str(skill_root)
    return normalized


def build_timeline(plan: dict[str, Any]) -> list[str]:
    start = int(plan["timeline"]["start_year"])
    horizon = int(plan["timeline"]["horizon_years"])
    periodicity = plan["timeline"].get("periodicity", "annual")
    if periodicity == "annual":
        return [str(start + i) for i in range(1, horizon + 1)]
    # Quarterly support uses Q1... labels from start year.
    labels: list[str] = []
    year = start
    quarter = 1
    for _ in range(horizon):
        labels.append(f"{year}Q{quarter}")
        quarter += 1
        if quarter > 4:
            year += 1
            quarter = 1
    return labels


def compute_wacc(
    plan: dict[str, Any], scenario_name: str | dict[str, Any] = "base"
) -> dict[str, float]:
    wacc = plan["wacc"]
    if isinstance(scenario_name, dict):
        scenario = scenario_name
    else:
        scenario = plan.get("scenarios", {}).get(str(scenario_name), {})
    risk_free_rate = float(wacc["risk_free_rate"])
    beta = float(wacc["beta"])
    erp = float(wacc["equity_risk_premium"])
    size = float(wacc.get("size_premium", 0.0))
    country = float(wacc.get("country_risk_premium", 0.0))
    company_specific = float(wacc.get("company_specific_premium", 0.0))
    cost_of_equity = risk_free_rate + beta * erp + size + country + company_specific

    marginal_tax_rate = float(wacc["marginal_tax_rate"])
    pre_tax_cost_of_debt = float(wacc["pre_tax_cost_of_debt"])
    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1.0 - marginal_tax_rate)
    pre_tax_cost_of_preferred = float(wacc.get("pre_tax_cost_of_preferred", 0.0))
    preferred_pct = float(wacc.get("preferred_pct", 0.0))
    debt_pct = float(wacc["target_debt_pct"])
    equity_pct = float(wacc["target_equity_pct"])
    base_wacc = (
        equity_pct * cost_of_equity
        + debt_pct * after_tax_cost_of_debt
        + preferred_pct * pre_tax_cost_of_preferred
    )
    scenario_adjustment = float(scenario.get("wacc_adjustment", 0.0))
    final_wacc = base_wacc + scenario_adjustment

    return {
        "risk_free_rate": risk_free_rate,
        "beta": beta,
        "equity_risk_premium": erp,
        "size_premium": size,
        "country_risk_premium": country,
        "company_specific_premium": company_specific,
        "cost_of_equity": cost_of_equity,
        "pre_tax_cost_of_debt": pre_tax_cost_of_debt,
        "after_tax_cost_of_debt": after_tax_cost_of_debt,
        "marginal_tax_rate": marginal_tax_rate,
        "target_debt_pct": debt_pct,
        "target_equity_pct": equity_pct,
        "preferred_pct": preferred_pct,
        "base_wacc": base_wacc,
        "scenario_wacc_adjustment": scenario_adjustment,
        "wacc": final_wacc,
    }


def compute_unlevered_fcf(
    plan: dict[str, Any], scenario_name: str = "base"
) -> list[dict[str, float | str]]:
    scenario = plan["scenarios"][scenario_name]
    horizon = int(plan["timeline"]["horizon_years"])
    periods = build_timeline(plan)
    revenue_growth = _vector(scenario["revenue_growth"], horizon, "revenue_growth")
    ebit_margin = _vector(scenario["ebit_margin"], horizon, "ebit_margin")
    tax_rate = _vector(scenario["tax_rate"], horizon, "tax_rate")
    da_pct = _vector(scenario["da_percent_revenue"], horizon, "da_percent_revenue")
    capex_pct = _vector(scenario["capex_percent_revenue"], horizon, "capex_percent_revenue")
    nwc_pct = _vector(scenario["nwc_percent_revenue"], horizon, "nwc_percent_revenue")

    previous_revenue = float(plan["historicals"]["revenue"])
    previous_nwc = float(
        plan["historicals"].get("net_working_capital", previous_revenue * nwc_pct[0])
    )
    rows: list[dict[str, float | str]] = []
    for i, period in enumerate(periods):
        revenue = previous_revenue * (1.0 + revenue_growth[i])
        ebit = revenue * ebit_margin[i]
        taxes = max(ebit * tax_rate[i], 0.0)
        nopat = ebit - taxes
        da = revenue * da_pct[i]
        capex = revenue * capex_pct[i]
        nwc = revenue * nwc_pct[i]
        change_nwc = nwc - previous_nwc
        unlevered_fcf = nopat + da - capex - change_nwc
        ebitda = ebit + da
        rows.append(
            {
                "period": period,
                "revenue": revenue,
                "revenue_growth": revenue_growth[i],
                "ebitda": ebitda,
                "ebit": ebit,
                "ebit_margin": ebit_margin[i],
                "tax_rate": tax_rate[i],
                "cash_taxes": taxes,
                "nopat": nopat,
                "da": da,
                "capex": capex,
                "nwc": nwc,
                "change_nwc": change_nwc,
                "unlevered_fcf": unlevered_fcf,
                "cash_flow": unlevered_fcf,
            }
        )
        previous_revenue = revenue
        previous_nwc = nwc
    return rows


def compute_equity_cash_flows(
    plan: dict[str, Any], scenario_name: str = "base"
) -> list[dict[str, float | str]]:
    scenario = plan["scenarios"][scenario_name]
    horizon = int(plan["timeline"]["horizon_years"])
    periods = build_timeline(plan)
    revenue_growth = _vector(scenario["revenue_growth"], horizon, "revenue_growth")
    ebit_margin = _vector(scenario["ebit_margin"], horizon, "ebit_margin")
    net_income_margin = _vector(scenario["net_income_margin"], horizon, "net_income_margin")
    tax_rate = _vector(scenario["tax_rate"], horizon, "tax_rate")
    da_pct = _vector(scenario["da_percent_revenue"], horizon, "da_percent_revenue")
    capex_pct = _vector(scenario["capex_percent_revenue"], horizon, "capex_percent_revenue")
    nwc_pct = _vector(scenario["nwc_percent_revenue"], horizon, "nwc_percent_revenue")
    net_borrowing = _vector(scenario.get("net_borrowing", 0.0), horizon, "net_borrowing")

    previous_revenue = float(plan["historicals"]["revenue"])
    previous_nwc = float(
        plan["historicals"].get("net_working_capital", previous_revenue * nwc_pct[0])
    )
    rows: list[dict[str, float | str]] = []
    for i, period in enumerate(periods):
        revenue = previous_revenue * (1.0 + revenue_growth[i])
        ebit = revenue * ebit_margin[i]
        net_income = revenue * net_income_margin[i]
        da = revenue * da_pct[i]
        capex = revenue * capex_pct[i]
        nwc = revenue * nwc_pct[i]
        change_nwc = nwc - previous_nwc
        fcfe = net_income + da - capex - change_nwc + net_borrowing[i]
        ebitda = ebit + da
        rows.append(
            {
                "period": period,
                "revenue": revenue,
                "revenue_growth": revenue_growth[i],
                "ebitda": ebitda,
                "ebit": ebit,
                "ebit_margin": ebit_margin[i],
                "net_income": net_income,
                "net_income_margin": net_income_margin[i],
                "tax_rate": tax_rate[i],
                "da": da,
                "capex": capex,
                "nwc": nwc,
                "change_nwc": change_nwc,
                "net_borrowing": net_borrowing[i],
                "fcfe": fcfe,
                "cash_flow": fcfe,
            }
        )
        previous_revenue = revenue
        previous_nwc = nwc
    return rows


def compute_terminal_value(
    plan: dict[str, Any],
    forecast_rows: list[dict[str, Any]],
    discount_rate: float,
    scenario_name: str = "base",
    method_override: str | None = None,
) -> dict[str, float | str]:
    if not forecast_rows:
        raise ValueError("forecast_rows cannot be empty")
    scenario = plan["scenarios"][scenario_name]
    terminal = plan["terminal_value"]
    method = method_override or terminal.get("method", "perpetual_growth")
    final = forecast_rows[-1]
    final_fcf = float(final["cash_flow"])
    final_ebitda = float(final.get("ebitda", 0.0))
    if method == "perpetual_growth":
        g = float(scenario.get("terminal_growth_rate", terminal.get("perpetual_growth_rate", 0.0)))
        if discount_rate <= g:
            raise ValueError(
                f"discount rate {discount_rate:.4f} must exceed terminal growth {g:.4f}"
            )
        terminal_fcf = final_fcf * (1.0 + g)
        terminal_value = terminal_fcf / (discount_rate - g)
        implied_exit_multiple = terminal_value / final_ebitda if final_ebitda else None
        implied_fcf_yield = terminal_fcf / terminal_value if terminal_value else None
        return {
            "method": method,
            "terminal_growth_rate": g,
            "terminal_fcf": terminal_fcf,
            "terminal_value": terminal_value,
            "exit_ebitda_multiple": float(terminal.get("exit_ebitda_multiple", 0.0)),
            "implied_exit_ebitda_multiple": implied_exit_multiple
            if implied_exit_multiple is not None
            else 0.0,
            "implied_fcf_yield": implied_fcf_yield if implied_fcf_yield is not None else 0.0,
        }
    if method == "exit_multiple":
        multiple = float(scenario.get("exit_ebitda_multiple", terminal.get("exit_ebitda_multiple")))
        if multiple <= 0:
            raise ValueError("exit EBITDA multiple must be positive")
        terminal_value = final_ebitda * multiple
        implied_fcf_yield = final_fcf / terminal_value if terminal_value else None
        implied_growth_rate = None
        # Rearranged Gordon growth is approximate because final FCF is used rather than next-year FCF.
        if terminal_value and final_fcf:
            implied_growth_rate = (discount_rate * terminal_value - final_fcf) / (
                terminal_value + final_fcf
            )
        return {
            "method": method,
            "terminal_growth_rate": float(
                scenario.get("terminal_growth_rate", terminal.get("perpetual_growth_rate", 0.0))
            ),
            "terminal_fcf": final_fcf,
            "terminal_value": terminal_value,
            "exit_ebitda_multiple": multiple,
            "implied_exit_ebitda_multiple": multiple,
            "implied_fcf_yield": implied_fcf_yield if implied_fcf_yield is not None else 0.0,
            "implied_growth_rate": implied_growth_rate if implied_growth_rate is not None else 0.0,
        }
    raise ValueError(f"unsupported terminal value method: {method}")


def discount_cash_flows(
    forecast_rows: list[dict[str, Any]],
    terminal_value: float,
    discount_rate: float,
    mid_year_convention: bool = True,
) -> dict[str, Any]:
    if discount_rate <= -1.0:
        raise ValueError("discount rate must be greater than -100%")
    pv_rows: list[dict[str, Any]] = []
    for i, row in enumerate(forecast_rows, start=1):
        period_power = i - 0.5 if mid_year_convention else i
        pv = float(row["cash_flow"]) / ((1.0 + discount_rate) ** period_power)
        pv_rows.append(
            {
                "period": row["period"],
                "cash_flow": row["cash_flow"],
                "discount_period": period_power,
                "pv_cash_flow": pv,
            }
        )
    n = len(forecast_rows)
    pv_terminal = terminal_value / ((1.0 + discount_rate) ** n)
    pv_fcf = sum(float(r["pv_cash_flow"]) for r in pv_rows)
    return {
        "pv_rows": pv_rows,
        "pv_fcf": pv_fcf,
        "pv_terminal_value": pv_terminal,
        "total_pv": pv_fcf + pv_terminal,
    }


def compute_enterprise_value(pv_fcf: float, pv_terminal_value: float) -> float:
    return float(pv_fcf) + float(pv_terminal_value)


def compute_equity_value(plan: dict[str, Any], enterprise_value: float) -> dict[str, float]:
    bridge = plan["ev_to_equity_bridge"]
    add_backs = (
        float(bridge.get("cash", 0.0))
        + float(bridge.get("non_operating_assets", 0.0))
        + float(bridge.get("associates", 0.0))
    )
    deductions = (
        float(bridge.get("debt", 0.0))
        + float(bridge.get("leases", 0.0))
        + float(bridge.get("minorities", 0.0))
        + float(bridge.get("pensions", 0.0))
        + float(bridge.get("preferred_stock", 0.0))
        + float(bridge.get("options", 0.0))
        + float(bridge.get("other_debt_like_items", 0.0))
    )
    equity_value = enterprise_value + add_backs - deductions
    return {
        "add_backs": add_backs,
        "deductions": deductions,
        "equity_value": equity_value,
    }


def compute_enterprise_value_from_equity(plan: dict[str, Any], equity_value: float) -> float:
    bridge = plan["ev_to_equity_bridge"]
    add_backs = (
        float(bridge.get("cash", 0.0))
        + float(bridge.get("non_operating_assets", 0.0))
        + float(bridge.get("associates", 0.0))
    )
    deductions = (
        float(bridge.get("debt", 0.0))
        + float(bridge.get("leases", 0.0))
        + float(bridge.get("minorities", 0.0))
        + float(bridge.get("pensions", 0.0))
        + float(bridge.get("preferred_stock", 0.0))
        + float(bridge.get("options", 0.0))
        + float(bridge.get("other_debt_like_items", 0.0))
    )
    return equity_value - add_backs + deductions


def compute_value_per_share(plan: dict[str, Any], equity_value: float) -> float:
    shares = float(plan["ev_to_equity_bridge"]["diluted_shares"])
    if shares <= 0:
        raise ValueError("diluted shares must be greater than zero")
    return equity_value / shares


def run_scenario(
    plan: dict[str, Any],
    scenario_name: str = "base",
    terminal_method_override: str | None = None,
) -> dict[str, Any]:
    cash_flow_basis = plan["forecast"].get(
        "cash_flow_basis", plan["meta"].get("model_type", "fcff")
    )
    wacc_info = compute_wacc(plan, scenario_name)
    discount_rate = (
        wacc_info["wacc"]
        if cash_flow_basis == "fcff"
        else wacc_info["cost_of_equity"]
        + float(plan["scenarios"][scenario_name].get("wacc_adjustment", 0.0))
    )
    forecast_rows = (
        compute_unlevered_fcf(plan, scenario_name)
        if cash_flow_basis == "fcff"
        else compute_equity_cash_flows(plan, scenario_name)
    )
    terminal_info = compute_terminal_value(
        plan,
        forecast_rows,
        discount_rate,
        scenario_name,
        method_override=terminal_method_override,
    )
    pv_info = discount_cash_flows(
        forecast_rows,
        float(terminal_info["terminal_value"]),
        discount_rate,
        bool(plan["forecast"].get("mid_year_convention", True)),
    )

    if cash_flow_basis == "fcff":
        enterprise_value = compute_enterprise_value(
            float(pv_info["pv_fcf"]), float(pv_info["pv_terminal_value"])
        )
        equity_bridge = compute_equity_value(plan, enterprise_value)
        equity_value = equity_bridge["equity_value"]
    else:
        equity_value = compute_enterprise_value(
            float(pv_info["pv_fcf"]), float(pv_info["pv_terminal_value"])
        )
        enterprise_value = compute_enterprise_value_from_equity(plan, equity_value)
        equity_bridge = {
            "add_backs": 0.0,
            "deductions": 0.0,
            "equity_value": equity_value,
        }

    value_per_share = compute_value_per_share(plan, equity_value)
    tv_percent_ev = (
        float(pv_info["pv_terminal_value"]) / enterprise_value if enterprise_value else 0.0
    )
    return {
        "scenario": scenario_name,
        "cash_flow_basis": cash_flow_basis,
        "forecast_rows": forecast_rows,
        "wacc": wacc_info,
        "discount_rate": discount_rate,
        "terminal": terminal_info,
        "pv": pv_info,
        "enterprise_value": enterprise_value,
        "equity_bridge": equity_bridge,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "tv_percent_ev": tv_percent_ev,
    }


def _adjust_vector(
    value: Any,
    horizon: int,
    delta: float,
    floor: float | None = None,
    cap: float | None = None,
) -> list[float]:
    vals = _vector(value, horizon, "adjust_vector")
    out = []
    for v in vals:
        new_v = v + delta
        if floor is not None:
            new_v = max(floor, new_v)
        if cap is not None:
            new_v = min(cap, new_v)
        out.append(new_v)
    return out


def _safe_run_value_per_share(
    plan: dict[str, Any], method: str | None = None
) -> tuple[float | None, str | None]:
    try:
        result = run_scenario(plan, "base", terminal_method_override=method)
        value = float(result["value_per_share"])
        if not math.isfinite(value):
            return None, "non-finite value per share"
        return value, None
    except Exception as exc:
        return None, str(exc)


def run_sensitivities(plan: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    horizon = int(plan["timeline"]["horizon_years"])
    base_scenario = plan["scenarios"]["base"]
    base_tg = float(
        base_scenario.get(
            "terminal_growth_rate",
            plan["terminal_value"].get("perpetual_growth_rate", 0.0),
        )
    )
    base_exit = float(
        base_scenario.get(
            "exit_ebitda_multiple",
            plan["terminal_value"].get("exit_ebitda_multiple", 0.0),
        )
    )
    sens = plan.get("sensitivities", {})

    for w_delta in sens.get("wacc_delta", [0.0]):
        for tg_delta in sens.get("terminal_growth_delta", [0.0]):
            p = copy.deepcopy(plan)
            p["terminal_value"]["method"] = "perpetual_growth"
            p["scenarios"]["base"]["wacc_adjustment"] = float(
                base_scenario.get("wacc_adjustment", 0.0)
            ) + float(w_delta)
            p["scenarios"]["base"]["terminal_growth_rate"] = base_tg + float(tg_delta)
            value, error = _safe_run_value_per_share(p, method="perpetual_growth")
            rows.append(
                {
                    "sensitivity": "WACC / Terminal Growth",
                    "x_axis": "wacc_delta",
                    "x_value": float(w_delta),
                    "y_axis": "terminal_growth_delta",
                    "y_value": float(tg_delta),
                    "metric": "value_per_share",
                    "value": value,
                    "units": plan["meta"].get("currency", "") + "/share",
                    "notes": error or "",
                }
            )

    if base_exit > 0:
        for w_delta in sens.get("wacc_delta", [0.0]):
            for mult_delta in sens.get("exit_multiple_delta", [0.0]):
                p = copy.deepcopy(plan)
                p["terminal_value"]["method"] = "exit_multiple"
                p["terminal_value"]["exit_ebitda_multiple"] = max(
                    0.1, base_exit + float(mult_delta)
                )
                p["scenarios"]["base"]["exit_ebitda_multiple"] = max(
                    0.1, base_exit + float(mult_delta)
                )
                p["scenarios"]["base"]["wacc_adjustment"] = float(
                    base_scenario.get("wacc_adjustment", 0.0)
                ) + float(w_delta)
                value, error = _safe_run_value_per_share(p, method="exit_multiple")
                rows.append(
                    {
                        "sensitivity": "WACC / Exit Multiple",
                        "x_axis": "wacc_delta",
                        "x_value": float(w_delta),
                        "y_axis": "exit_multiple_delta",
                        "y_value": float(mult_delta),
                        "metric": "value_per_share",
                        "value": value,
                        "units": plan["meta"].get("currency", "") + "/share",
                        "notes": error or "",
                    }
                )

    for rev_delta in sens.get("revenue_growth_delta", [0.0]):
        for margin_delta in sens.get("ebit_margin_delta", [0.0]):
            p = copy.deepcopy(plan)
            p["scenarios"]["base"]["revenue_growth"] = _adjust_vector(
                base_scenario["revenue_growth"], horizon, float(rev_delta), floor=-0.9
            )
            p["scenarios"]["base"]["ebit_margin"] = _adjust_vector(
                base_scenario["ebit_margin"],
                horizon,
                float(margin_delta),
                floor=-0.8,
                cap=0.95,
            )
            value, error = _safe_run_value_per_share(p, method=plan["terminal_value"].get("method"))
            rows.append(
                {
                    "sensitivity": "Revenue Growth / EBIT Margin",
                    "x_axis": "revenue_growth_delta",
                    "x_value": float(rev_delta),
                    "y_axis": "ebit_margin_delta",
                    "y_value": float(margin_delta),
                    "metric": "value_per_share",
                    "value": value,
                    "units": plan["meta"].get("currency", "") + "/share",
                    "notes": error or "",
                }
            )

    directionality = compute_sensitivity_directionality(rows)
    return {"rows": rows, "directionality": directionality}


def _value_at(
    rows: list[dict[str, Any]], sensitivity: str, x_value: float, y_value: float
) -> float | None:
    candidates = [
        r
        for r in rows
        if r.get("sensitivity") == sensitivity
        and abs(float(r.get("x_value", 999.0)) - x_value) < 1e-9
        and abs(float(r.get("y_value", 999.0)) - y_value) < 1e-9
        and r.get("value") is not None
    ]
    if not candidates:
        return None
    return float(candidates[0]["value"])


def compute_sensitivity_directionality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    checks: dict[str, Any] = {"passed": True, "details": []}

    def add_check(name: str, passed: bool, detail: str) -> None:
        checks["details"].append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            checks["passed"] = False

    def check_axis(
        sensitivity: str,
        axis: str,
        fixed_axis_zero: str,
        should_increase_with_axis: bool,
    ) -> None:
        subset = [
            r for r in rows if r.get("sensitivity") == sensitivity and r.get("value") is not None
        ]
        if not subset:
            add_check(f"{sensitivity} {axis}", False, "no successful rows")
            return
        if axis == "x":
            fixed_rows = [r for r in subset if abs(float(r.get("y_value", 0.0))) < 1e-9]
            key = "x_value"
        else:
            fixed_rows = [r for r in subset if abs(float(r.get("x_value", 0.0))) < 1e-9]
            key = "y_value"
        if len(fixed_rows) < 2:
            add_check(f"{sensitivity} {axis}", False, "not enough zero-axis rows")
            return
        low = min(fixed_rows, key=lambda r: float(r[key]))
        high = max(fixed_rows, key=lambda r: float(r[key]))
        low_v = float(low["value"])
        high_v = float(high["value"])
        if should_increase_with_axis:
            passed = high_v >= low_v
            detail = f"value at high axis {high_v:.2f} vs low axis {low_v:.2f}"
        else:
            passed = high_v <= low_v
            detail = f"value at high axis {high_v:.2f} vs low axis {low_v:.2f}"
        add_check(f"{sensitivity} {axis} direction", passed, detail)

    check_axis(
        "WACC / Terminal Growth",
        "x",
        "terminal_growth_delta",
        should_increase_with_axis=False,
    )
    check_axis("WACC / Terminal Growth", "y", "wacc_delta", should_increase_with_axis=True)
    check_axis(
        "WACC / Exit Multiple",
        "x",
        "exit_multiple_delta",
        should_increase_with_axis=False,
    )
    check_axis("WACC / Exit Multiple", "y", "wacc_delta", should_increase_with_axis=True)
    check_axis(
        "Revenue Growth / EBIT Margin",
        "x",
        "ebit_margin_delta",
        should_increase_with_axis=True,
    )
    check_axis(
        "Revenue Growth / EBIT Margin",
        "y",
        "revenue_growth_delta",
        should_increase_with_axis=True,
    )
    return checks


def _source_warnings(plan: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    labels = [
        str(src.get("label")) for src in plan.get("source_basis", []) if isinstance(src, dict)
    ]
    if "placeholder" in labels:
        warnings.append(
            "One or more material source entries use placeholder evidence labels; output is screen-grade at best."
        )
    weak_topics = [
        str(src.get("topic"))
        for src in plan.get("source_basis", [])
        if isinstance(src, dict)
        and src.get("label") in {"analyst_estimate", "placeholder"}
        and src.get("topic") in {"forecast", "wacc", "terminal_value"}
    ]
    if weak_topics:
        warnings.append(
            "Material valuation inputs rely on analyst estimates/placeholders: "
            + ", ".join(sorted(set(weak_topics)))
        )
    valuation_date = _date(str(plan.get("meta", {}).get("valuation_date", "")))
    if valuation_date:
        dated = []
        for src in plan.get("source_basis", []):
            if not isinstance(src, dict):
                continue
            d = _date(str(src.get("as_of_date", "")))
            if d:
                dated.append((src.get("topic"), d))
                age = abs((valuation_date - d).days)
                if (
                    src.get("topic") in {"wacc", "share_count", "net_debt", "market_data"}
                    and age > 120
                ):
                    warnings.append(
                        f"Source for {src.get('topic')} is {age} days from valuation date; refresh market/bridge data for decision-grade use."
                    )
        if dated:
            min_date = min(d for _, d in dated)
            max_date = max(d for _, d in dated)
            spread = (max_date - min_date).days
            if spread > 365:
                warnings.append(
                    f"Source dates span {spread} days; confirm market data, historicals, and share count are contemporaneous."
                )
    return warnings


def compute_checks(
    plan: dict[str, Any],
    scenario_results: dict[str, dict[str, Any]],
    sensitivity_result: dict[str, Any],
) -> dict[str, Any]:
    hard_failures: list[str] = []
    warnings: list[str] = []
    informational: list[str] = []

    validation_errors = validate_plan_structure(plan)
    if validation_errors:
        hard_failures.extend(validation_errors)

    required_topics = REQUIRED_SOURCE_TOPICS
    topics = {
        str(src.get("topic")) for src in plan.get("source_basis", []) if isinstance(src, dict)
    }
    missing_topics = sorted(required_topics - topics)
    if missing_topics:
        hard_failures.append(
            "source basis missing for material valuation inputs: " + ", ".join(missing_topics)
        )

    base = scenario_results.get("base")
    if not base:
        hard_failures.append("base scenario did not run")
    else:
        forecast_rows = base.get("forecast_rows", [])
        fcfs = [row.get("cash_flow") for row in forecast_rows]
        if not fcfs or all(not _is_number(v) for v in fcfs):
            hard_failures.append("no forecast FCF/FCFE was produced")
        wacc_value = float(base.get("discount_rate", 0.0))
        if wacc_value <= 0 or not math.isfinite(wacc_value):
            hard_failures.append("WACC/cost of equity is non-positive or invalid")
        terminal = base.get("terminal", {})
        if not terminal or not _is_number(terminal.get("terminal_value")):
            hard_failures.append("terminal value missing or invalid")
        elif terminal.get("method") == "perpetual_growth" and wacc_value <= float(
            terminal.get("terminal_growth_rate", 0.0)
        ):
            hard_failures.append("discount rate must exceed terminal growth")
        for metric in ["enterprise_value", "equity_value", "value_per_share"]:
            value = base.get(metric)
            if not _is_number(value):
                hard_failures.append(f"discounting math failed for {metric}")
        bridge = plan.get("ev_to_equity_bridge", {})
        if (
            not _is_number(bridge.get("diluted_shares"))
            or float(bridge.get("diluted_shares", 0.0)) <= 0
        ):
            hard_failures.append("EV-to-equity bridge missing valid diluted shares")
        tv_pct = float(base.get("tv_percent_ev", 0.0))
        if tv_pct > 0.85:
            warnings.append(
                f"Terminal value is {tv_pct:.1%} of enterprise value, which is very high."
            )
        elif tv_pct > 0.75:
            warnings.append(
                f"Terminal value is {tv_pct:.1%} of enterprise value; senior review should pressure-test terminal assumptions."
            )
        terminal_growth = float(terminal.get("terminal_growth_rate", 0.0))
        if terminal.get("method") == "perpetual_growth" and terminal_growth > 0.04:
            warnings.append(
                f"Terminal growth of {terminal_growth:.1%} exceeds a typical mature-company long-run threshold."
            )
        hist_margin = float(plan["historicals"].get("ebit", 0.0)) / float(
            plan["historicals"].get("revenue", 1.0)
        )
        final_margin = float(forecast_rows[-1].get("ebit_margin", 0.0)) if forecast_rows else 0.0
        if final_margin - hist_margin > 0.05:
            forecast_src = _source_for_topic(plan, "forecast") or {}
            if forecast_src.get("label") not in {
                "company_guidance",
                "management_case",
                "consensus",
                "reported",
                "user_provided",
            }:
                warnings.append(
                    f"Forecast EBIT margin expands by {(final_margin - hist_margin):.1%} versus latest historical margin without strong source support."
                )

    if not sensitivity_result.get("directionality", {}).get("passed", False):
        hard_failures.append("sensitivity outputs failed directionality checks")

    warnings.extend(_source_warnings(plan))
    warnings.extend(plan.get("_normalization_notes", []))

    # Deduplicate preserving order.
    hard_failures = list(dict.fromkeys(hard_failures))
    warnings = list(dict.fromkeys(warnings))

    checks = {
        "hard_failures": hard_failures,
        "warnings": warnings,
        "informational": informational,
        "sensitivity_directionality": sensitivity_result.get("directionality", {}),
    }
    if base:
        checks.update(
            {
                "base_tv_percent_ev": base.get("tv_percent_ev"),
                "base_discount_rate": base.get("discount_rate"),
                "base_enterprise_value": base.get("enterprise_value"),
                "base_equity_value": base.get("equity_value"),
                "base_value_per_share": base.get("value_per_share"),
            }
        )
    return checks


def determine_model_status(
    plan: dict[str, Any], hard_failures: list[str], warnings: list[str]
) -> str:
    if hard_failures:
        return "not-decision-ready"
    labels = [src.get("label") for src in plan.get("source_basis", []) if isinstance(src, dict)]
    if "placeholder" in labels:
        return "screen-grade"
    if any(label == "analyst_estimate" for label in labels):
        return "screen-grade"
    if warnings:
        return "senior-review-ready"
    return "decision-grade"


def _fmt_pct(x: float | None) -> str:
    if x is None or not math.isfinite(float(x)):
        return "n/a"
    return f"{float(x) * 100:.1f}%"


def _fmt_num(x: float | None) -> str:
    if x is None or not math.isfinite(float(x)):
        return "n/a"
    return f"{float(x):,.1f}"


def _fmt_price(x: float | None) -> str:
    if x is None or not math.isfinite(float(x)):
        return "n/a"
    return f"{float(x):,.2f}"


def build_p0_handoff(
    plan: dict[str, Any],
    scenario_results: dict[str, dict[str, Any]],
    sensitivity_result: dict[str, Any],
    model_status: str,
    warnings: list[str],
    output_dir: str | os.PathLike[str],
) -> dict[str, Any]:
    scenario_summary: dict[str, Any] = {}
    values = []
    for name in SCENARIOS:
        r = scenario_results.get(name)
        if not r:
            continue
        scenario_summary[name] = {
            "enterprise_value": r.get("enterprise_value"),
            "equity_value": r.get("equity_value"),
            "value_per_share": r.get("value_per_share"),
            "discount_rate": r.get("discount_rate"),
            "terminal_value": r.get("terminal", {}).get("terminal_value"),
            "terminal_method": r.get("terminal", {}).get("method"),
            "tv_percent_ev": r.get("tv_percent_ev"),
        }
        if _is_number(r.get("value_per_share")):
            values.append(float(r["value_per_share"]))
    selected_range = {
        "low_value_per_share": min(values) if values else None,
        "high_value_per_share": max(values) if values else None,
        "basis": "downside/base/upside scenario range",
    }

    key_drivers = identify_key_value_drivers(sensitivity_result.get("rows", []))
    base = scenario_results.get("base", {})
    output = Path(output_dir)
    return {
        "selected_valuation_range": selected_range,
        "scenarios": scenario_summary,
        "wacc_and_terminal_assumptions": {
            "base_discount_rate": base.get("discount_rate"),
            "base_wacc": base.get("wacc", {}).get("wacc"),
            "base_cost_of_equity": base.get("wacc", {}).get("cost_of_equity"),
            "terminal_method": base.get("terminal", {}).get("method"),
            "terminal_growth_rate": base.get("terminal", {}).get("terminal_growth_rate"),
            "exit_ebitda_multiple": base.get("terminal", {}).get("exit_ebitda_multiple"),
        },
        "key_value_drivers": key_drivers,
        "major_caveats": warnings[:10],
        "model_status": model_status,
        "paths": {
            "workbook": str(output / "model.xlsx"),
            "plan": str(output / "plan.json"),
            "run_log": str(output / "run_log.json"),
            "support_note": str(output / "support_note.md"),
        },
    }


def identify_key_value_drivers(
    sensitivity_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    drivers: list[dict[str, Any]] = []
    for sensitivity in sorted({str(r.get("sensitivity")) for r in sensitivity_rows}):
        vals = [
            float(r["value"])
            for r in sensitivity_rows
            if r.get("sensitivity") == sensitivity and _is_number(r.get("value"))
        ]
        if vals:
            drivers.append(
                {
                    "driver": sensitivity,
                    "value_per_share_range": max(vals) - min(vals),
                    "low": min(vals),
                    "high": max(vals),
                }
            )
    drivers.sort(key=lambda d: d["value_per_share_range"], reverse=True)
    return drivers[:5]


def to_model_rows(
    plan: dict[str, Any],
    scenario_results: dict[str, dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]] | None = None,
    checks: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    forecast_source = str(plan.get("forecast", {}).get("source_id", ""))
    forecast_label = _source_label(plan, forecast_source)
    wacc_source = str(plan.get("wacc", {}).get("source_id", ""))
    wacc_label = _source_label(plan, wacc_source)
    terminal_source = str(plan.get("terminal_value", {}).get("source_id", ""))
    terminal_label = _source_label(plan, terminal_source)
    bridge = plan.get("ev_to_equity_bridge", {})
    bridge_source = str(bridge.get("net_debt_source_id", ""))
    bridge_label = _source_label(plan, bridge_source)
    share_source = str(bridge.get("share_count_source_id", ""))
    share_label = _source_label(plan, share_source)
    units = plan.get("meta", {}).get("units", "")

    for scenario_name, result in scenario_results.items():
        for f in result.get("forecast_rows", []):
            period = f["period"]
            for section, line_item, key in [
                ("IS", "Revenue", "revenue"),
                ("IS", "EBITDA", "ebitda"),
                ("IS", "EBIT", "ebit"),
                ("IS", "Cash Taxes", "cash_taxes"),
                ("FCF", "NOPAT", "nopat"),
                ("FCF", "D&A", "da"),
                ("FCF", "Capex", "capex"),
                ("FCF", "Change in NWC", "change_nwc"),
                ("FCF", "Unlevered FCF", "unlevered_fcf"),
                ("FCF", "FCFE", "fcfe"),
            ]:
                if key not in f:
                    continue
                rows.append(
                    {
                        "section": section,
                        "line_item": line_item,
                        "scenario": scenario_name,
                        "period": period,
                        "value": f[key],
                        "units": units,
                        "evidence_label": forecast_label,
                        "source_id": forecast_source,
                        "notes": "forecast output",
                    }
                )
        w = result.get("wacc", {})
        for line_item, key in [
            ("Cost of Equity", "cost_of_equity"),
            ("Pre-tax Cost of Debt", "pre_tax_cost_of_debt"),
            ("After-tax Cost of Debt", "after_tax_cost_of_debt"),
            ("Marginal Tax Rate", "marginal_tax_rate"),
            ("Target Debt %", "target_debt_pct"),
            ("Target Equity %", "target_equity_pct"),
            ("WACC", "wacc"),
        ]:
            rows.append(
                {
                    "section": "WACC",
                    "line_item": line_item,
                    "scenario": scenario_name,
                    "period": "valuation_date",
                    "value": w.get(key),
                    "units": "%"
                    if "Rate" in line_item
                    or "%" in line_item
                    or line_item
                    in {
                        "WACC",
                        "Cost of Equity",
                        "Pre-tax Cost of Debt",
                        "After-tax Cost of Debt",
                    }
                    else "x",
                    "evidence_label": wacc_label,
                    "source_id": wacc_source,
                    "notes": "cost of capital output",
                }
            )
        terminal = result.get("terminal", {})
        for line_item, value in [
            ("Terminal Value", terminal.get("terminal_value")),
            ("PV of Terminal Value", result.get("pv", {}).get("pv_terminal_value")),
            ("TV Percent of EV", result.get("tv_percent_ev")),
            (
                "Implied Exit EBITDA Multiple",
                terminal.get("implied_exit_ebitda_multiple"),
            ),
            ("Implied FCF Yield", terminal.get("implied_fcf_yield")),
        ]:
            rows.append(
                {
                    "section": "TV",
                    "line_item": line_item,
                    "scenario": scenario_name,
                    "period": "terminal",
                    "value": value,
                    "units": "%" if "Percent" in line_item or "Yield" in line_item else units,
                    "evidence_label": terminal_label,
                    "source_id": terminal_source,
                    "notes": str(terminal.get("method", "")),
                }
            )
        for line_item, value, label, source_id in [
            (
                "PV of FCF",
                result.get("pv", {}).get("pv_fcf"),
                forecast_label,
                forecast_source,
            ),
            (
                "Enterprise Value",
                result.get("enterprise_value"),
                bridge_label,
                bridge_source,
            ),
            ("Equity Value", result.get("equity_value"), bridge_label, bridge_source),
            ("Diluted Shares", bridge.get("diluted_shares"), share_label, share_source),
            (
                "Value per Share",
                result.get("value_per_share"),
                share_label,
                share_source,
            ),
        ]:
            rows.append(
                {
                    "section": "VALUATION",
                    "line_item": line_item,
                    "scenario": scenario_name,
                    "period": "valuation_date",
                    "value": value,
                    "units": plan.get("meta", {}).get("currency", "")
                    + ("/share" if "Share" in line_item else "mm"),
                    "evidence_label": label,
                    "source_id": source_id,
                    "notes": "valuation output",
                }
            )

    if checks:
        for item in checks.get("hard_failures", []):
            rows.append(
                {
                    "section": "CHECKS",
                    "line_item": "Hard Failure",
                    "scenario": "all",
                    "period": "run",
                    "value": "",
                    "units": "",
                    "evidence_label": "derived",
                    "source_id": "",
                    "notes": item,
                }
            )
        for item in checks.get("warnings", []):
            rows.append(
                {
                    "section": "CHECKS",
                    "line_item": "Warning",
                    "scenario": "all",
                    "period": "run",
                    "value": "",
                    "units": "",
                    "evidence_label": "derived",
                    "source_id": "",
                    "notes": item,
                }
            )

    for src in plan.get("source_basis", []):
        rows.append(
            {
                "section": "ASSUMPTIONS",
                "line_item": f"Source Basis - {src.get('topic')}",
                "scenario": "all",
                "period": str(src.get("as_of_date", "")),
                "value": "",
                "units": "",
                "evidence_label": src.get("label", ""),
                "source_id": src.get("id", ""),
                "notes": f"{src.get('source_name', '')}: {src.get('notes', '')}",
            }
        )
    return rows


def _rows_to_table(rows: list[dict[str, Any]], columns: list[str] | None = None) -> list[list[Any]]:
    if not rows:
        return [columns or []]
    if columns is None:
        columns = []
        for row in rows:
            for key in row.keys():
                if key not in columns:
                    columns.append(key)
    return [columns] + [[row.get(col, "") for col in columns] for row in rows]


def build_workbook_sheets(
    plan: dict[str, Any],
    scenario_results: dict[str, dict[str, Any]],
    sensitivity_result: dict[str, Any],
    checks: dict[str, Any],
    run_log: dict[str, Any],
) -> dict[str, list[list[Any]]]:
    summary_rows: list[dict[str, Any]] = []
    for name in SCENARIOS:
        result = scenario_results.get(name)
        if not result:
            continue
        summary_rows.append(
            {
                "scenario": name,
                "enterprise_value": result.get("enterprise_value"),
                "equity_value": result.get("equity_value"),
                "value_per_share": result.get("value_per_share"),
                "discount_rate": result.get("discount_rate"),
                "pv_fcf": result.get("pv", {}).get("pv_fcf"),
                "pv_terminal_value": result.get("pv", {}).get("pv_terminal_value"),
                "terminal_value": result.get("terminal", {}).get("terminal_value"),
                "tv_percent_ev": result.get("tv_percent_ev"),
                "terminal_method": result.get("terminal", {}).get("method"),
            }
        )

    model_rows = to_model_rows(plan, scenario_results, sensitivity_result.get("rows", []), checks)
    sensitivity_rows = sensitivity_result.get("rows", [])
    check_rows = []
    for item in checks.get("hard_failures", []):
        check_rows.append({"severity": "hard_failure", "check": item, "status": "fail"})
    for item in checks.get("warnings", []):
        check_rows.append({"severity": "warning", "check": item, "status": "review"})
    for detail in checks.get("sensitivity_directionality", {}).get("details", []):
        check_rows.append(
            {
                "severity": "check",
                "check": detail.get("check"),
                "status": "pass" if detail.get("passed") else "fail",
                "detail": detail.get("detail"),
            }
        )

    assumptions_rows = []
    for src in plan.get("source_basis", []):
        assumptions_rows.append(
            {
                "id": src.get("id"),
                "topic": src.get("topic"),
                "label": src.get("label"),
                "source_name": src.get("source_name"),
                "source_type": src.get("source_type"),
                "as_of_date": src.get("as_of_date"),
                "confidence": src.get("confidence"),
                "notes": src.get("notes"),
            }
        )
    assumptions_rows.extend(
        [
            {
                "id": "meta.company",
                "topic": "meta",
                "label": "derived",
                "source_name": plan.get("meta", {}).get("company"),
                "source_type": "plan",
                "as_of_date": plan.get("meta", {}).get("as_of_date"),
                "confidence": "",
                "notes": "company modeled",
            },
            {
                "id": "meta.model_type",
                "topic": "meta",
                "label": "derived",
                "source_name": plan.get("meta", {}).get("model_type"),
                "source_type": "plan",
                "as_of_date": plan.get("meta", {}).get("valuation_date"),
                "confidence": "",
                "notes": "cash flow basis",
            },
        ]
    )

    run_rows = [
        ["field", "value"],
        ["model_status", run_log.get("model_status")],
        ["workbook_mode", run_log.get("workbook_mode")],
        ["hard_failure_count", len(run_log.get("hard_failures", []))],
        ["warning_count", len(run_log.get("warnings", []))],
        ["company", plan.get("meta", {}).get("company")],
        ["valuation_date", plan.get("meta", {}).get("valuation_date")],
    ]
    for idx, warning in enumerate(run_log.get("warnings", [])[:20], start=1):
        run_rows.append([f"warning_{idx}", warning])
    for idx, failure in enumerate(run_log.get("hard_failures", [])[:20], start=1):
        run_rows.append([f"hard_failure_{idx}", failure])

    return {
        "Summary": _rows_to_table(summary_rows),
        "Model": _rows_to_table(
            model_rows,
            [
                "section",
                "line_item",
                "scenario",
                "period",
                "value",
                "units",
                "evidence_label",
                "source_id",
                "notes",
            ],
        ),
        "Sensitivities": _rows_to_table(
            sensitivity_rows,
            [
                "sensitivity",
                "x_axis",
                "x_value",
                "y_axis",
                "y_value",
                "metric",
                "value",
                "units",
                "notes",
            ],
        ),
        "Checks": _rows_to_table(check_rows),
        "Assumptions": _rows_to_table(assumptions_rows),
        "Run Log": run_rows,
    }


def render_report(
    plan: dict[str, Any],
    scenario_results: dict[str, dict[str, Any]],
    checks: dict[str, Any],
    run_log: dict[str, Any],
) -> str:
    meta = plan.get("meta", {})
    lines: list[str] = []
    lines.append(f"# DCF Valuation Report: {meta.get('company', 'Company')}")
    lines.append("")
    lines.append(f"**Model status:** `{run_log.get('model_status')}`  ")
    lines.append(f"**Workbook mode:** `{run_log.get('workbook_mode')}`  ")
    lines.append(f"**Valuation date:** {meta.get('valuation_date')}  ")
    lines.append(f"**Currency / units:** {meta.get('currency')} / {meta.get('units')}  ")
    lines.append("")
    lines.append("## Valuation range")
    handoff = run_log.get("p0_handoff", {})
    value_range = handoff.get("selected_valuation_range", {})
    lines.append(
        f"- Scenario value per share range: **{_fmt_price(value_range.get('low_value_per_share'))} to {_fmt_price(value_range.get('high_value_per_share'))}**"
    )
    lines.append(f"- Basis: {value_range.get('basis', 'scenario range')}")
    lines.append("")
    lines.append("| Scenario | EV | Equity value | Value / share | Discount rate | TV % EV |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for name in SCENARIOS:
        r = scenario_results.get(name)
        if not r:
            continue
        lines.append(
            f"| {name.title()} | {_fmt_num(r.get('enterprise_value'))} | {_fmt_num(r.get('equity_value'))} | {_fmt_price(r.get('value_per_share'))} | {_fmt_pct(r.get('discount_rate'))} | {_fmt_pct(r.get('tv_percent_ev'))} |"
        )
    lines.append("")
    base = scenario_results.get("base", {})
    if base:
        terminal = base.get("terminal", {})
        wacc = base.get("wacc", {})
        lines.append("## Base-case DCF bridge")
        lines.append(
            f"- PV of explicit cash flows: **{_fmt_num(base.get('pv', {}).get('pv_fcf'))}**"
        )
        lines.append(
            f"- PV of terminal value: **{_fmt_num(base.get('pv', {}).get('pv_terminal_value'))}**"
        )
        lines.append(f"- Enterprise value: **{_fmt_num(base.get('enterprise_value'))}**")
        lines.append(f"- Equity value: **{_fmt_num(base.get('equity_value'))}**")
        lines.append(f"- Value per share: **{_fmt_price(base.get('value_per_share'))}**")
        lines.append("")
        lines.append("## WACC and terminal value")
        lines.append(f"- Cost of equity: **{_fmt_pct(wacc.get('cost_of_equity'))}**")
        lines.append(f"- WACC: **{_fmt_pct(wacc.get('wacc'))}**")
        lines.append(f"- Terminal method: **{terminal.get('method')}**")
        lines.append(f"- Terminal growth: **{_fmt_pct(terminal.get('terminal_growth_rate'))}**")
        lines.append(
            f"- Implied exit EBITDA multiple: **{_fmt_num(terminal.get('implied_exit_ebitda_multiple'))}x**"
        )
        lines.append("")
    lines.append("## Key value drivers")
    drivers = handoff.get("key_value_drivers", [])
    if drivers:
        lines.append("| Driver | Value/share range | Low | High |")
        lines.append("|---|---:|---:|---:|")
        for d in drivers:
            lines.append(
                f"| {d.get('driver')} | {_fmt_price(d.get('value_per_share_range'))} | {_fmt_price(d.get('low'))} | {_fmt_price(d.get('high'))} |"
            )
    else:
        lines.append("No sensitivity drivers were available.")
    lines.append("")
    lines.append("## QA checks")
    hard = checks.get("hard_failures", [])
    warns = checks.get("warnings", [])
    if hard:
        lines.append("**Hard failures:**")
        for item in hard:
            lines.append(f"- {item}")
    else:
        lines.append("No hard failures detected.")
    if warns:
        lines.append("")
        lines.append("**Warnings / senior-review items:**")
        for item in warns:
            lines.append(f"- {item}")
    else:
        lines.append("")
        lines.append("No warnings detected.")
    lines.append("")
    lines.append("## Source basis")
    lines.append("| Topic | Label | Source | As of | Confidence |")
    lines.append("|---|---|---|---|---|")
    for src in plan.get("source_basis", []):
        lines.append(
            f"| {src.get('topic')} | {src.get('label')} | {src.get('source_name')} | {src.get('as_of_date')} | {src.get('confidence')} |"
        )
    lines.append("")
    lines.append("## Generated artifacts")
    for label, path in handoff.get("paths", {}).items():
        lines.append(f"- {label}: `{path}`")
    lines.append("")
    lines.append(
        "This deterministic export is value-based. It is not a fully linked banker formula workbook."
    )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Library module for dcf-model-builder. "
            "Use scripts/run_pipeline.py for deterministic CLI execution."
        )
    )
    parser.parse_args()
    print("This is a library module. Use scripts/run_pipeline.py to build a DCF model export.")
