"""Core deterministic 3-statement operating model engine.

Design goals:
- No network calls, no hidden randomness, standard library only.
- Preserve source/assumption labels in outputs.
- Produce a long-format model table suitable for deterministic export.
- Keep workbook rendering separate from source ingestion and model judgment.
"""

from __future__ import annotations

import copy
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

ALLOWED_PERIODICITIES = {"annual", "quarterly"}
ALLOWED_SCENARIOS = ("base", "downside", "upside")
MODEL_TOLERANCE = 0.05


@dataclass
class Period:
    index: int
    label: str
    year: int
    periodicity: str
    time_factor: float


def deep_merge(base: Any, override: Any) -> Any:
    """Recursively merge override into base without mutating either argument."""
    if override is None:
        return copy.deepcopy(base)
    if isinstance(base, dict) and isinstance(override, dict):
        out = copy.deepcopy(base)
        for key, value in override.items():
            out[key] = deep_merge(out.get(key), value)
        return out
    return copy.deepcopy(override)


def coalesce(*values: Any, default: Any = None) -> Any:
    for value in values:
        if value is not None:
            return value
    return default


def is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def period_sort_key(label: str) -> tuple[int, int]:
    text = str(label)
    year_match = re.search(r"(19|20|21)\d{2}", text)
    year = int(year_match.group(0)) if year_match else 0
    q_match = re.search(r"q([1-4])", text.lower())
    quarter = int(q_match.group(1)) if q_match else 4
    return (year, quarter)


def latest_period_key(mapping: dict[str, Any]) -> str | None:
    if not isinstance(mapping, dict) or not mapping:
        return None
    return max(mapping.keys(), key=period_sort_key)


def normalize_plan(plan: dict[str, Any], skill_root: Path) -> dict[str, Any]:
    """Apply non-conclusion-changing defaults and canonical metadata."""
    normalized = copy.deepcopy(plan)
    normalized.setdefault("meta", {})
    normalized["meta"].setdefault("currency", "USD")
    normalized["meta"].setdefault("units", "USD_mm")
    normalized["meta"].setdefault("accounting_basis", "unspecified")
    normalized.setdefault("source_basis", [])
    normalized.setdefault(
        "scenarios",
        {
            "base": {"overrides": {}},
            "downside": {"overrides": {}},
            "upside": {"overrides": {}},
        },
    )
    normalized.setdefault("sensitivities", {})
    normalized.setdefault("other_balance_sheet", {})
    normalized["other_balance_sheet"].setdefault(
        "other_assets", last_bs_value(normalized, "other_assets", 0.0)
    )
    normalized["other_balance_sheet"].setdefault(
        "other_liabilities", last_bs_value(normalized, "other_liabilities", 0.0)
    )
    normalized["workbook_mode"] = "deterministic_export"
    normalized["artifact_level"] = "deterministic_export"
    return normalized


def build_timeline(start_year: int, horizon_periods: int, periodicity: str) -> list[Period]:
    if periodicity not in ALLOWED_PERIODICITIES:
        raise ValueError(f"Unsupported periodicity: {periodicity}")
    if horizon_periods <= 0:
        raise ValueError("horizon_periods must be positive")

    periods: list[Period] = []
    if periodicity == "annual":
        for i in range(horizon_periods):
            year = start_year + i
            periods.append(Period(i, f"FY{year}", year, periodicity, 1.0))
    else:
        total_quarters = horizon_periods
        for i in range(total_quarters):
            year = start_year + (i // 4)
            quarter = (i % 4) + 1
            periods.append(Period(i, f"Q{quarter}-FY{year}", year, periodicity, 0.25))
    return periods


def get_assumption(value: Any, period: Period, default: float = 0.0) -> float:
    """Fetch scalar or period map value with prior-period fallback."""
    if value is None:
        return float(default)
    if is_number(value):
        return float(value)
    if not isinstance(value, dict) or not value:
        return float(default)

    exact_keys = [period.label, f"FY{period.year}", str(period.year)]
    for key in exact_keys:
        if key in value and value[key] is not None:
            return float(value[key])

    keyed: list[tuple[tuple[int, int], str]] = []
    for key in value.keys():
        keyed.append((period_sort_key(str(key)), str(key)))
    keyed.sort()
    target = period_sort_key(period.label)
    prior = [key for key_sort, key in keyed if key_sort <= target]
    if prior:
        return float(value[prior[-1]])
    return float(value[keyed[0][1]])


def periodicize_annual_rate(annual_rate: float, time_factor: float) -> float:
    if time_factor >= 1.0:
        return annual_rate
    if annual_rate <= -0.99:
        return -0.99
    return (1.0 + annual_rate) ** time_factor - 1.0


def last_bs(plan: dict[str, Any]) -> dict[str, Any]:
    bs = plan.get("historicals", {}).get("balance_sheet", {})
    key = latest_period_key(bs)
    return copy.deepcopy(bs.get(key, {})) if key else {}


def last_bs_value(plan: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = last_bs(plan).get(key, default)
    return float(value or 0.0)


def last_nwc(plan: dict[str, Any]) -> float:
    wc_hist = plan.get("historicals", {}).get("working_capital", {})
    key = latest_period_key(wc_hist)
    if key and is_number(wc_hist[key].get("nwc")):
        return float(wc_hist[key]["nwc"])
    bs = last_bs(plan)
    return (
        float(bs.get("ar", 0.0) or 0.0)
        + float(bs.get("inventory", 0.0) or 0.0)
        + float(bs.get("other_current_assets", 0.0) or 0.0)
        - float(bs.get("ap", 0.0) or 0.0)
        - float(bs.get("accrued_expenses", 0.0) or 0.0)
        - float(bs.get("deferred_revenue", 0.0) or 0.0)
    )


def last_hist_is(plan: dict[str, Any]) -> dict[str, Any]:
    hist = plan.get("historicals", {}).get("income_statement", {})
    key = latest_period_key(hist)
    return copy.deepcopy(hist.get(key, {})) if key else {}


def compute_revenue(plan: dict[str, Any], periods: list[Period]) -> dict[str, Any]:
    revenue_plan = plan.get("revenue", {})
    model = revenue_plan.get("model", "total_growth")
    total: list[float] = []
    segment_rows: dict[str, list[float]] = {}

    if model == "segments":
        segments = revenue_plan.get("segments", {})
        annualized: dict[str, float] = {}
        for name, cfg in segments.items():
            annualized[name] = float(cfg.get("base_revenue", 0.0) or 0.0)
            segment_rows[name] = []
        for period in periods:
            period_total = 0.0
            for name, cfg in segments.items():
                growth = get_assumption(cfg.get("growth_rates"), period, 0.0)
                growth = periodicize_annual_rate(growth, period.time_factor)
                annualized[name] *= 1.0 + growth
                value = annualized[name] * period.time_factor
                segment_rows[name].append(value)
                period_total += value
            total.append(period_total)
        return {
            "revenue": total,
            "segments": segment_rows,
            "source_id": revenue_plan.get("source_id"),
            "evidence_label": revenue_plan.get("evidence_label", "model_calculated"),
        }

    if model == "volume_price":
        units = float(revenue_plan.get("base_units", 0.0) or 0.0)
        price = float(revenue_plan.get("base_price", 0.0) or 0.0)
        segment_rows["volume_price_revenue"] = []
        for period in periods:
            ug = periodicize_annual_rate(
                get_assumption(revenue_plan.get("unit_growth_rates"), period, 0.0),
                period.time_factor,
            )
            pg = periodicize_annual_rate(
                get_assumption(revenue_plan.get("price_growth_rates"), period, 0.0),
                period.time_factor,
            )
            units *= 1.0 + ug
            price *= 1.0 + pg
            value = units * price * period.time_factor
            total.append(value)
            segment_rows["volume_price_revenue"].append(value)
        return {
            "revenue": total,
            "segments": segment_rows,
            "source_id": revenue_plan.get("source_id"),
            "evidence_label": revenue_plan.get("evidence_label", "model_calculated"),
        }

    base_revenue = float(
        coalesce(
            revenue_plan.get("base_revenue"),
            last_hist_is(plan).get("revenue"),
            default=0.0,
        )
        or 0.0
    )
    annualized_revenue = base_revenue
    segment_rows["total_revenue"] = []
    for period in periods:
        growth = periodicize_annual_rate(
            get_assumption(revenue_plan.get("growth_rates"), period, 0.0),
            period.time_factor,
        )
        annualized_revenue *= 1.0 + growth
        value = annualized_revenue * period.time_factor
        total.append(value)
        segment_rows["total_revenue"].append(value)
    return {
        "revenue": total,
        "segments": segment_rows,
        "source_id": revenue_plan.get("source_id"),
        "evidence_label": revenue_plan.get("evidence_label", "model_calculated"),
    }


def compute_income_statement(
    plan: dict[str, Any],
    periods: list[Period],
    revenue_result: dict[str, Any],
    ppe_result: dict[str, list[float]] | None = None,
    interest: list[float] | None = None,
) -> dict[str, list[float]]:
    costs = plan.get("costs", {})
    cogs_plan = costs.get("cogs", {})
    opex_plan = costs.get("opex", {})
    revenue = revenue_result["revenue"]
    da = (
        ppe_result.get("depreciation", [0.0] * len(periods)) if ppe_result else [0.0] * len(periods)
    )
    interest_values = interest if interest is not None else [0.0] * len(periods)

    out: dict[str, list[float]] = {
        k: []
        for k in [
            "revenue",
            "cogs",
            "gross_profit",
            "opex",
            "ebitda",
            "da",
            "ebit",
            "interest",
            "ebt",
            "book_taxes",
            "cash_taxes",
            "net_income",
            "deferred_tax",
            "nol_used",
            "ending_nol",
        ]
    }
    nol = float(plan.get("tax", {}).get("nol_balance", 0.0) or 0.0)
    book_tax_rate = float(plan.get("tax", {}).get("book_tax_rate", 0.0) or 0.0)
    cash_tax_rate = float(plan.get("tax", {}).get("cash_tax_rate", book_tax_rate) or 0.0)

    for i, period in enumerate(periods):
        rev = revenue[i]
        if cogs_plan.get("method", "gross_margin") == "pct_revenue":
            cogs = rev * get_assumption(cogs_plan.get("pct_revenue"), period, 0.0)
        else:
            gm = get_assumption(cogs_plan.get("gross_margin"), period, 0.0)
            cogs = rev * (1.0 - gm)
        if opex_plan.get("method", "pct_revenue") == "amount":
            opex = get_assumption(opex_plan.get("amount"), period, 0.0)
        else:
            opex = rev * get_assumption(opex_plan.get("pct_revenue"), period, 0.0)
        gp = rev - cogs
        ebitda = gp - opex
        ebit = ebitda - da[i]
        ebt = ebit - interest_values[i]
        if ebt > 0:
            nol_used = min(nol, ebt)
            taxable_income = max(0.0, ebt - nol_used)
            book_tax = ebt * book_tax_rate
            cash_tax = taxable_income * cash_tax_rate
            nol = max(0.0, nol - nol_used)
        else:
            nol_used = 0.0
            book_tax = 0.0
            cash_tax = 0.0
            nol += abs(ebt)
        net_income = ebt - book_tax
        deferred_tax = book_tax - cash_tax

        values = {
            "revenue": rev,
            "cogs": cogs,
            "gross_profit": gp,
            "opex": opex,
            "ebitda": ebitda,
            "da": da[i],
            "ebit": ebit,
            "interest": interest_values[i],
            "ebt": ebt,
            "book_taxes": book_tax,
            "cash_taxes": cash_tax,
            "net_income": net_income,
            "deferred_tax": deferred_tax,
            "nol_used": nol_used,
            "ending_nol": nol,
        }
        for key, value in values.items():
            out[key].append(value)
    return out


def compute_ppe_and_da(
    plan: dict[str, Any], periods: list[Period], revenue: list[float]
) -> dict[str, list[float]]:
    ppe_plan = plan.get("ppe", {})
    begin_ppe = float(coalesce(last_bs_value(plan, "ppe_net", 0.0), default=0.0) or 0.0)
    out = {
        "beginning_ppe": [],
        "capex": [],
        "depreciation": [],
        "disposals": [],
        "ending_ppe": [],
    }
    for i, period in enumerate(periods):
        capex_method = ppe_plan.get("capex_method", "pct_revenue")
        if capex_method == "amount":
            capex = get_assumption(ppe_plan.get("capex_amount"), period, 0.0)
        else:
            capex = revenue[i] * get_assumption(ppe_plan.get("capex_pct_revenue"), period, 0.0)

        dep_method = ppe_plan.get("depreciation_method", "pct_beginning_ppe")
        if dep_method == "pct_revenue":
            depreciation = revenue[i] * get_assumption(
                ppe_plan.get("depreciation_pct_revenue"), period, 0.0
            )
        elif dep_method == "amount":
            depreciation = get_assumption(ppe_plan.get("depreciation_amount"), period, 0.0)
        else:
            annual_rate = get_assumption(
                ppe_plan.get("depreciation_pct_beginning_ppe"), period, 0.0
            )
            depreciation = (begin_ppe + 0.5 * capex) * annual_rate * period.time_factor
        disposals = get_assumption(ppe_plan.get("disposals"), period, 0.0)
        ending_ppe = max(0.0, begin_ppe + capex - depreciation - disposals)

        out["beginning_ppe"].append(begin_ppe)
        out["capex"].append(capex)
        out["depreciation"].append(depreciation)
        out["disposals"].append(disposals)
        out["ending_ppe"].append(ending_ppe)
        begin_ppe = ending_ppe
    return out


def compute_working_capital(
    plan: dict[str, Any], periods: list[Period], revenue: list[float], cogs: list[float]
) -> dict[str, list[float]]:
    wc_plan = plan.get("working_capital", {})
    prev_nwc = last_nwc(plan)
    out = {
        "ar_days": [],
        "inventory_days": [],
        "ap_days": [],
        "ar": [],
        "inventory": [],
        "other_current_assets": [],
        "ap": [],
        "accrued_expenses": [],
        "deferred_revenue": [],
        "nwc": [],
        "change_nwc": [],
    }
    for i, period in enumerate(periods):
        annual_revenue = revenue[i] / period.time_factor if period.time_factor else revenue[i]
        annual_cogs = cogs[i] / period.time_factor if period.time_factor else cogs[i]
        ar_days = get_assumption(wc_plan.get("ar_days"), period, 0.0)
        inv_days = get_assumption(wc_plan.get("inventory_days"), period, 0.0)
        ap_days = get_assumption(wc_plan.get("ap_days"), period, 0.0)
        ar = annual_revenue * ar_days / 365.0
        inventory = annual_cogs * inv_days / 365.0
        oca = annual_revenue * get_assumption(
            wc_plan.get("other_current_assets_pct_revenue"), period, 0.0
        )
        ap = annual_cogs * ap_days / 365.0
        accrued = annual_revenue * get_assumption(
            wc_plan.get("accrued_expenses_pct_revenue"), period, 0.0
        )
        deferred = annual_revenue * get_assumption(
            wc_plan.get("deferred_revenue_pct_revenue"), period, 0.0
        )
        nwc = ar + inventory + oca - ap - accrued - deferred
        change_nwc = nwc - prev_nwc

        values = {
            "ar_days": ar_days,
            "inventory_days": inv_days,
            "ap_days": ap_days,
            "ar": ar,
            "inventory": inventory,
            "other_current_assets": oca,
            "ap": ap,
            "accrued_expenses": accrued,
            "deferred_revenue": deferred,
            "nwc": nwc,
            "change_nwc": change_nwc,
        }
        for key, value in values.items():
            out[key].append(value)
        prev_nwc = nwc
    return out


def compute_debt_and_interest(
    plan: dict[str, Any], periods: list[Period], integrated: dict[str, list[float]]
) -> dict[str, list[float]]:
    """Return debt schedule and cash sweep using already computed operating cash flow inputs."""
    debt_plan = plan.get("debt", {})
    sweep_plan = debt_plan.get("cash_sweep", {})
    beginning_debt = float(debt_plan.get("beginning_debt", last_bs_value(plan, "debt", 0.0)) or 0.0)
    beginning_cash = last_bs_value(plan, "cash", 0.0)
    beginning_revolver = float(debt_plan.get("beginning_revolver_drawn", 0.0) or 0.0)
    revolver_commitment = float(debt_plan.get("revolver_commitment", 0.0) or 0.0)
    min_cash = float(sweep_plan.get("min_cash", 0.0) or 0.0)
    sweep_pct = float(sweep_plan.get("sweep_pct", 0.0) if sweep_plan.get("enabled", True) else 0.0)

    out = {
        "beginning_cash": [],
        "beginning_debt": [],
        "beginning_revolver_drawn": [],
        "scheduled_draws": [],
        "required_draws": [],
        "total_draws": [],
        "mandatory_repayment": [],
        "optional_repayment": [],
        "total_repayments": [],
        "interest_rate": [],
        "interest": [],
        "ending_debt": [],
        "ending_revolver_drawn": [],
        "revolver_availability": [],
        "cash_before_sweep": [],
        "cash_change": [],
        "ending_cash": [],
        "minimum_cash": [],
    }

    beg_debt = beginning_debt
    beg_cash = beginning_cash
    beg_revolver = beginning_revolver
    for i, period in enumerate(periods):
        rate = get_assumption(debt_plan.get("interest_rate"), period, 0.0)
        scheduled_draw = get_assumption(debt_plan.get("optional_draws"), period, 0.0)
        available_before_draw = max(0.0, revolver_commitment - beg_revolver)
        scheduled_draw = (
            min(max(0.0, scheduled_draw), available_before_draw)
            if revolver_commitment > 0
            else max(0.0, scheduled_draw)
        )
        mandatory_repay = min(
            max(
                0.0,
                get_assumption(debt_plan.get("mandatory_amortization"), period, 0.0),
            ),
            beg_debt + scheduled_draw,
        )
        interest_base = max(0.0, beg_debt + 0.5 * scheduled_draw - 0.5 * mandatory_repay)
        interest = interest_base * rate * period.time_factor

        cfo = integrated["cash_flow_from_operations"][i]
        capex = integrated["capex"][i]
        dividends = integrated["dividends"][i]
        buybacks = integrated["buybacks"][i]
        issuance = integrated["issuance"][i]

        cash_before_sweep = (
            beg_cash
            + cfo
            - capex
            - dividends
            - buybacks
            + issuance
            + scheduled_draw
            - mandatory_repay
        )
        required_draw = 0.0
        revolver_after_scheduled = beg_revolver + scheduled_draw
        debt_after_scheduled = beg_debt + scheduled_draw - mandatory_repay
        if cash_before_sweep < min_cash:
            need = min_cash - cash_before_sweep
            availability = max(0.0, revolver_commitment - revolver_after_scheduled)
            required_draw = min(need, availability) if revolver_commitment > 0 else need
            cash_before_sweep += required_draw
            revolver_after_scheduled += required_draw
            debt_after_scheduled += required_draw

        optional_repay = 0.0
        if sweep_pct > 0.0 and cash_before_sweep > min_cash and debt_after_scheduled > 0.0:
            optional_repay = min((cash_before_sweep - min_cash) * sweep_pct, debt_after_scheduled)
        ending_cash = cash_before_sweep - optional_repay
        ending_debt = max(0.0, debt_after_scheduled - optional_repay)

        revolver_repay = min(optional_repay, revolver_after_scheduled)
        ending_revolver = max(0.0, revolver_after_scheduled - revolver_repay)
        availability = (
            max(0.0, revolver_commitment - ending_revolver) if revolver_commitment > 0 else 0.0
        )
        total_draws = scheduled_draw + required_draw
        total_repayments = mandatory_repay + optional_repay
        cash_change = ending_cash - beg_cash

        values = {
            "beginning_cash": beg_cash,
            "beginning_debt": beg_debt,
            "beginning_revolver_drawn": beg_revolver,
            "scheduled_draws": scheduled_draw,
            "required_draws": required_draw,
            "total_draws": total_draws,
            "mandatory_repayment": mandatory_repay,
            "optional_repayment": optional_repay,
            "total_repayments": total_repayments,
            "interest_rate": rate,
            "interest": interest,
            "ending_debt": ending_debt,
            "ending_revolver_drawn": ending_revolver,
            "revolver_availability": availability,
            "cash_before_sweep": cash_before_sweep,
            "cash_change": cash_change,
            "ending_cash": ending_cash,
            "minimum_cash": min_cash,
        }
        for key, value in values.items():
            out[key].append(value)
        beg_cash = ending_cash
        beg_debt = ending_debt
        beg_revolver = ending_revolver
    return out


def compute_cash_flow_statement(
    income_statement: dict[str, list[float]],
    wc: dict[str, list[float]],
    ppe: dict[str, list[float]],
    debt: dict[str, list[float]],
    equity_flows: dict[str, list[float]],
) -> dict[str, list[float]]:
    out = {
        "net_income": [],
        "da": [],
        "deferred_tax": [],
        "change_nwc": [],
        "cash_flow_from_operations": [],
        "capex": [],
        "cash_flow_from_investing": [],
        "debt_draws": [],
        "debt_repayments": [],
        "dividends": [],
        "buybacks": [],
        "issuance": [],
        "cash_flow_from_financing": [],
        "cash_change": [],
        "ending_cash": [],
    }
    n = len(income_statement["net_income"])
    for i in range(n):
        cfo = (
            income_statement["net_income"][i]
            + income_statement["da"][i]
            + income_statement["deferred_tax"][i]
            - wc["change_nwc"][i]
        )
        cfi = -ppe["capex"][i]
        cff = (
            debt["total_draws"][i]
            - debt["total_repayments"][i]
            - equity_flows["dividends"][i]
            - equity_flows["buybacks"][i]
            + equity_flows["issuance"][i]
        )
        values = {
            "net_income": income_statement["net_income"][i],
            "da": income_statement["da"][i],
            "deferred_tax": income_statement["deferred_tax"][i],
            "change_nwc": wc["change_nwc"][i],
            "cash_flow_from_operations": cfo,
            "capex": ppe["capex"][i],
            "cash_flow_from_investing": cfi,
            "debt_draws": debt["total_draws"][i],
            "debt_repayments": debt["total_repayments"][i],
            "dividends": equity_flows["dividends"][i],
            "buybacks": equity_flows["buybacks"][i],
            "issuance": equity_flows["issuance"][i],
            "cash_flow_from_financing": cff,
            "cash_change": debt["cash_change"][i],
            "ending_cash": debt["ending_cash"][i],
        }
        for key, value in values.items():
            out[key].append(value)
    return out


def compute_balance_sheet(
    plan: dict[str, Any],
    periods: list[Period],
    income_statement: dict[str, list[float]],
    wc: dict[str, list[float]],
    ppe: dict[str, list[float]],
    debt: dict[str, list[float]],
    equity_flows: dict[str, list[float]],
) -> dict[str, list[float]]:
    out = {
        "cash": [],
        "ar": [],
        "inventory": [],
        "other_current_assets": [],
        "ppe_net": [],
        "other_assets": [],
        "total_assets": [],
        "ap": [],
        "accrued_expenses": [],
        "deferred_revenue": [],
        "debt": [],
        "other_liabilities": [],
        "common_equity": [],
        "retained_earnings": [],
        "total_liabilities_equity": [],
        "balance_check": [],
    }
    other_assets = float(
        plan.get("other_balance_sheet", {}).get(
            "other_assets", last_bs_value(plan, "other_assets", 0.0)
        )
        or 0.0
    )
    other_liabilities = float(
        plan.get("other_balance_sheet", {}).get(
            "other_liabilities", last_bs_value(plan, "other_liabilities", 0.0)
        )
        or 0.0
    )
    common_equity = float(
        plan.get("equity", {}).get("common_equity", last_bs_value(plan, "common_equity", 0.0))
        or 0.0
    )
    retained_earnings = last_bs_value(plan, "retained_earnings", 0.0)
    cumulative_deferred_tax_liability = 0.0

    for i in range(len(periods)):
        common_equity += equity_flows["issuance"][i] - equity_flows["buybacks"][i]
        retained_earnings += income_statement["net_income"][i] - equity_flows["dividends"][i]
        cumulative_deferred_tax_liability += income_statement.get(
            "deferred_tax", [0.0] * len(periods)
        )[i]
        current_other_liabilities = other_liabilities + cumulative_deferred_tax_liability
        total_assets = (
            debt["ending_cash"][i]
            + wc["ar"][i]
            + wc["inventory"][i]
            + wc["other_current_assets"][i]
            + ppe["ending_ppe"][i]
            + other_assets
        )
        total_liab_eq = (
            wc["ap"][i]
            + wc["accrued_expenses"][i]
            + wc["deferred_revenue"][i]
            + debt["ending_debt"][i]
            + current_other_liabilities
            + common_equity
            + retained_earnings
        )
        values = {
            "cash": debt["ending_cash"][i],
            "ar": wc["ar"][i],
            "inventory": wc["inventory"][i],
            "other_current_assets": wc["other_current_assets"][i],
            "ppe_net": ppe["ending_ppe"][i],
            "other_assets": other_assets,
            "total_assets": total_assets,
            "ap": wc["ap"][i],
            "accrued_expenses": wc["accrued_expenses"][i],
            "deferred_revenue": wc["deferred_revenue"][i],
            "debt": debt["ending_debt"][i],
            "other_liabilities": current_other_liabilities,
            "common_equity": common_equity,
            "retained_earnings": retained_earnings,
            "total_liabilities_equity": total_liab_eq,
            "balance_check": total_assets - total_liab_eq,
        }
        for key, value in values.items():
            out[key].append(value)
    return out


def compute_covenants_or_liquidity(
    plan: dict[str, Any],
    periods: list[Period],
    income_statement: dict[str, list[float]],
    debt: dict[str, list[float]],
) -> dict[str, list[float]]:
    cov = plan.get("debt", {}).get("covenants", {})
    out = {
        "net_debt": [],
        "liquidity": [],
        "net_leverage": [],
        "interest_coverage": [],
        "min_liquidity": [],
        "max_net_leverage": [],
        "min_interest_coverage": [],
        "liquidity_headroom": [],
        "net_leverage_headroom": [],
        "interest_coverage_headroom": [],
        "covenant_breach_flag": [],
    }
    for i in range(len(periods)):
        cash = debt["ending_cash"][i]
        ending_debt = debt["ending_debt"][i]
        liquidity = cash + debt["revolver_availability"][i]
        ebitda = income_statement["ebitda"][i]
        interest = income_statement["interest"][i]
        net_debt = ending_debt - cash
        net_lev = net_debt / ebitda if ebitda > 0 else float("inf")
        icr = ebitda / interest if interest > 0 else float("inf")
        min_liq = float(cov.get("min_liquidity", 0.0) or 0.0)
        max_lev = float(cov.get("max_net_leverage", 1e9) or 1e9)
        min_icr = float(cov.get("min_interest_coverage", 0.0) or 0.0)
        liquidity_headroom = liquidity - min_liq
        net_lev_headroom = max_lev - net_lev if math.isfinite(net_lev) else -1e9
        icr_headroom = icr - min_icr if math.isfinite(icr) else 1e9
        breach = (
            1.0
            if liquidity_headroom < -MODEL_TOLERANCE
            or net_lev_headroom < -0.01
            or icr_headroom < -0.01
            else 0.0
        )
        values = {
            "net_debt": net_debt,
            "liquidity": liquidity,
            "net_leverage": net_lev,
            "interest_coverage": icr,
            "min_liquidity": min_liq,
            "max_net_leverage": max_lev,
            "min_interest_coverage": min_icr,
            "liquidity_headroom": liquidity_headroom,
            "net_leverage_headroom": net_lev_headroom,
            "interest_coverage_headroom": icr_headroom,
            "covenant_breach_flag": breach,
        }
        for key, value in values.items():
            out[key].append(value)
    return out


def equity_flows(plan: dict[str, Any], periods: list[Period]) -> dict[str, list[float]]:
    eq = plan.get("equity", {})
    out = {"dividends": [], "buybacks": [], "issuance": []}
    for period in periods:
        out["dividends"].append(get_assumption(eq.get("dividends"), period, 0.0))
        out["buybacks"].append(get_assumption(eq.get("buybacks"), period, 0.0))
        out["issuance"].append(get_assumption(eq.get("issuance"), period, 0.0))
    return out


def build_operating_scaffold(
    plan: dict[str, Any], periods: list[Period]
) -> tuple[
    dict[str, Any],
    dict[str, list[float]],
    dict[str, list[float]],
    dict[str, list[float]],
]:
    revenue_result = compute_revenue(plan, periods)
    # First pass IS without D&A/interest gives COGS for WC and revenue for PP&E.
    temp_is = compute_income_statement(
        plan,
        periods,
        revenue_result,
        ppe_result={"depreciation": [0.0] * len(periods)},
        interest=[0.0] * len(periods),
    )
    ppe = compute_ppe_and_da(plan, periods, revenue_result["revenue"])
    wc = compute_working_capital(plan, periods, revenue_result["revenue"], temp_is["cogs"])
    return revenue_result, temp_is, ppe, wc


def run_integrated_model(plan: dict[str, Any], scenario_name: str = "base") -> dict[str, Any]:
    timeline = plan.get("timeline", {})
    periods = build_timeline(
        int(timeline["start_year"]),
        int(timeline["horizon_periods"]),
        timeline.get("periodicity", "annual"),
    )
    revenue_result, temp_is, ppe, wc = build_operating_scaffold(plan, periods)
    eq = equity_flows(plan, periods)

    # Resolve the mild interest/cash-sweep circularity by fixed-point iteration.
    interest = [0.0] * len(periods)
    integrated_for_debt = {
        "cash_flow_from_operations": [0.0] * len(periods),
        "capex": ppe["capex"],
        "dividends": eq["dividends"],
        "buybacks": eq["buybacks"],
        "issuance": eq["issuance"],
    }
    debt = None
    final_is = None
    for _ in range(20):
        final_is = compute_income_statement(plan, periods, revenue_result, ppe, interest=interest)
        final_cfo = [
            final_is["net_income"][i]
            + final_is["da"][i]
            + final_is["deferred_tax"][i]
            - wc["change_nwc"][i]
            for i in range(len(periods))
        ]
        integrated_for_debt["cash_flow_from_operations"] = final_cfo
        debt = compute_debt_and_interest(plan, periods, integrated_for_debt)
        new_interest = debt["interest"]
        if max(abs(new_interest[i] - interest[i]) for i in range(len(periods))) < 1e-8:
            interest = new_interest
            break
        interest = new_interest
    final_is = compute_income_statement(plan, periods, revenue_result, ppe, interest=interest)
    final_cfo = [
        final_is["net_income"][i]
        + final_is["da"][i]
        + final_is["deferred_tax"][i]
        - wc["change_nwc"][i]
        for i in range(len(periods))
    ]
    integrated_for_debt["cash_flow_from_operations"] = final_cfo
    debt = compute_debt_and_interest(plan, periods, integrated_for_debt)
    final_is = compute_income_statement(
        plan, periods, revenue_result, ppe, interest=debt["interest"]
    )
    cf = compute_cash_flow_statement(final_is, wc, ppe, debt, eq)
    bs = compute_balance_sheet(plan, periods, final_is, wc, ppe, debt, eq)
    cov = compute_covenants_or_liquidity(plan, periods, final_is, debt)

    result = {
        "scenario": scenario_name,
        "periods": periods,
        "revenue_detail": revenue_result,
        "income_statement": final_is,
        "working_capital": wc,
        "ppe": ppe,
        "debt": debt,
        "cash_flow_statement": cf,
        "balance_sheet": bs,
        "covenants_liquidity": cov,
        "equity_flows": eq,
    }
    result["checks"] = compute_checks(plan, result)
    return result


def apply_scenario(plan: dict[str, Any], scenario_name: str) -> dict[str, Any]:
    scenario = plan.get("scenarios", {}).get(scenario_name, {})
    return deep_merge(plan, scenario.get("overrides", {}))


def run_scenarios(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}
    for scenario in ALLOWED_SCENARIOS:
        scenario_plan = apply_scenario(plan, scenario)
        outputs[scenario] = run_integrated_model(scenario_plan, scenario)
    return outputs


def shock_growth_rates(plan: dict[str, Any], delta: float) -> dict[str, Any]:
    out = copy.deepcopy(plan)
    rev = out.get("revenue", {})
    if rev.get("model") == "segments":
        for cfg in rev.get("segments", {}).values():
            rates = cfg.get("growth_rates", {})
            for key in list(rates.keys()):
                rates[key] = float(rates[key]) + delta
    else:
        rates = rev.setdefault("growth_rates", {})
        for key in list(rates.keys()):
            rates[key] = float(rates[key]) + delta
    return out


def shock_map(plan: dict[str, Any], path: list[str], delta: float) -> dict[str, Any]:
    out = copy.deepcopy(plan)
    node = out
    for key in path[:-1]:
        node = node.setdefault(key, {})
    leaf = node.get(path[-1], {})
    if isinstance(leaf, dict):
        for key in list(leaf.keys()):
            if is_number(leaf[key]):
                leaf[key] = float(leaf[key]) + delta
    elif is_number(leaf):
        node[path[-1]] = float(leaf) + delta
    return out


def run_sensitivities(plan: dict[str, Any]) -> list[dict[str, Any]]:
    sens = plan.get("sensitivities", {})
    rows: list[dict[str, Any]] = []

    cases: list[tuple[str, float, dict[str, Any]]] = []
    for delta in sens.get("revenue_growth_shocks", []):
        cases.append(("revenue_growth", float(delta), shock_growth_rates(plan, float(delta))))
    for delta in sens.get("gross_margin_shocks", []):
        cases.append(
            (
                "gross_margin",
                float(delta),
                shock_map(plan, ["costs", "cogs", "gross_margin"], float(delta)),
            )
        )
    for delta in sens.get("dso_day_shocks", []):
        cases.append(
            (
                "dso_days",
                float(delta),
                shock_map(plan, ["working_capital", "ar_days"], float(delta)),
            )
        )
    for delta in sens.get("capex_pct_revenue_shocks", []):
        cases.append(
            (
                "capex_pct_revenue",
                float(delta),
                shock_map(plan, ["ppe", "capex_pct_revenue"], float(delta)),
            )
        )
    for delta in sens.get("interest_rate_shocks", []):
        cases.append(
            (
                "interest_rate",
                float(delta),
                shock_map(plan, ["debt", "interest_rate"], float(delta)),
            )
        )

    for driver, delta, case_plan in cases:
        result = run_integrated_model(case_plan, f"sensitivity_{driver}_{delta:+.4f}")
        summary = summarize_result(result)
        rows.append(
            {
                "case": f"{driver}_{delta:+.4f}",
                "driver": driver,
                "shock": delta,
                "final_revenue": summary["final_revenue"],
                "final_ebitda": summary["final_ebitda"],
                "final_fcf": summary["final_fcf"],
                "ending_cash": summary["ending_cash"],
                "liquidity_trough": summary["liquidity_trough"],
                "peak_net_leverage": summary["peak_net_leverage"],
            }
        )
    return rows


def compute_checks(plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    periods = result["periods"]
    bs = result["balance_sheet"]
    cf = result["cash_flow_statement"]
    debt = result["debt"]
    ppe = result["ppe"]
    wc = result["working_capital"]
    is_ = result["income_statement"]
    eq = result["equity_flows"]

    checks: dict[str, Any] = {
        "period_checks": [],
        "max_balance_sheet_abs_error": 0.0,
        "max_cash_tie_abs_error": 0.0,
        "max_retained_earnings_abs_error": 0.0,
        "max_debt_rollforward_abs_error": 0.0,
        "max_ppe_rollforward_abs_error": 0.0,
        "max_nwc_rollforward_abs_error": 0.0,
    }
    prior_re = last_bs_value(plan, "retained_earnings", 0.0)
    prior_nwc = last_nwc(plan)
    for i, period in enumerate(periods):
        balance_error = bs["balance_check"][i]
        cash_tie = cf["ending_cash"][i] - bs["cash"][i]
        expected_re = prior_re + is_["net_income"][i] - eq["dividends"][i]
        re_error = expected_re - bs["retained_earnings"][i]
        debt_error = (
            debt["beginning_debt"][i]
            + debt["total_draws"][i]
            - debt["total_repayments"][i]
            - debt["ending_debt"][i]
        )
        ppe_error = (
            ppe["beginning_ppe"][i]
            + ppe["capex"][i]
            - ppe["depreciation"][i]
            - ppe["disposals"][i]
            - ppe["ending_ppe"][i]
        )
        nwc_error = prior_nwc + wc["change_nwc"][i] - wc["nwc"][i]
        checks["period_checks"].append(
            {
                "period": period.label,
                "balance_sheet_error": balance_error,
                "cash_tie_error": cash_tie,
                "retained_earnings_error": re_error,
                "debt_rollforward_error": debt_error,
                "ppe_rollforward_error": ppe_error,
                "nwc_rollforward_error": nwc_error,
            }
        )
        checks["max_balance_sheet_abs_error"] = max(
            checks["max_balance_sheet_abs_error"], abs(balance_error)
        )
        checks["max_cash_tie_abs_error"] = max(checks["max_cash_tie_abs_error"], abs(cash_tie))
        checks["max_retained_earnings_abs_error"] = max(
            checks["max_retained_earnings_abs_error"], abs(re_error)
        )
        checks["max_debt_rollforward_abs_error"] = max(
            checks["max_debt_rollforward_abs_error"], abs(debt_error)
        )
        checks["max_ppe_rollforward_abs_error"] = max(
            checks["max_ppe_rollforward_abs_error"], abs(ppe_error)
        )
        checks["max_nwc_rollforward_abs_error"] = max(
            checks["max_nwc_rollforward_abs_error"], abs(nwc_error)
        )
        prior_re = bs["retained_earnings"][i]
        prior_nwc = wc["nwc"][i]
    return checks


def summarize_result(result: dict[str, Any]) -> dict[str, float]:
    is_ = result["income_statement"]
    cf = result["cash_flow_statement"]
    cov = result["covenants_liquidity"]
    debt = result["debt"]
    periods = result["periods"]
    fcf = [cf["cash_flow_from_operations"][i] - cf["capex"][i] for i in range(len(periods))]
    final_idx = len(periods) - 1
    peak_net_leverage = max([x for x in cov["net_leverage"] if math.isfinite(x)] or [0.0])
    return {
        "final_revenue": is_["revenue"][final_idx],
        "final_ebitda": is_["ebitda"][final_idx],
        "final_ebitda_margin": is_["ebitda"][final_idx] / is_["revenue"][final_idx]
        if is_["revenue"][final_idx]
        else 0.0,
        "final_fcf": fcf[final_idx],
        "ending_cash": debt["ending_cash"][final_idx],
        "ending_debt": debt["ending_debt"][final_idx],
        "liquidity_trough": min(cov["liquidity"]),
        "peak_net_leverage": peak_net_leverage,
        "min_interest_coverage": min(
            [x for x in cov["interest_coverage"] if math.isfinite(x)] or [999.0]
        ),
        "final_period": periods[final_idx].label,
    }


def _parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def source_freshness_warnings(plan: dict[str, Any]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    meta_as_of = _parse_iso_date(plan.get("meta", {}).get("as_of_date"))
    dated_sources: list[date] = []
    for src in plan.get("source_basis", []):
        if not isinstance(src, dict):
            continue
        src_date = _parse_iso_date(src.get("as_of_date"))
        if not src_date:
            continue
        dated_sources.append(src_date)
        if not meta_as_of:
            continue
        age_days = (meta_as_of - src_date).days
        covers = set(src.get("covers", [])) if isinstance(src.get("covers"), list) else set()
        if age_days < 0:
            warnings.append(
                {
                    "code": "SOURCE_DATE_AFTER_MODEL_AS_OF",
                    "message": f"{src.get('id', 'source')} is dated after meta.as_of_date; confirm the model as-of date.",
                }
            )
        elif (
            covers & {"forecast", "revenue", "costs", "working_capital", "ppe", "debt"}
            and age_days > 120
        ):
            warnings.append(
                {
                    "code": "STALE_FORECAST_SOURCE",
                    "message": f"{src.get('id', 'source')} is {age_days} days older than meta.as_of_date for forecast-driver support.",
                }
            )
        elif covers & {"historicals"} and age_days > 270:
            warnings.append(
                {
                    "code": "STALE_HISTORICAL_SOURCE",
                    "message": f"{src.get('id', 'source')} historical support is {age_days} days older than meta.as_of_date; refresh for decision-grade use.",
                }
            )
    if dated_sources and (max(dated_sources) - min(dated_sources)).days > 365:
        warnings.append(
            {
                "code": "SOURCE_DATE_SPREAD",
                "message": "Source dates span more than one year; verify historicals, forecasts, guidance, and market context are contemporaneous.",
            }
        )
    return warnings


def evaluate_hard_failures_and_warnings(
    plan: dict[str, Any], scenario_outputs: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    hard_failures: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    checks_summary: dict[str, Any] = {}

    for scenario, result in scenario_outputs.items():
        checks = result["checks"]
        checks_summary[scenario] = {k: v for k, v in checks.items() if k != "period_checks"}
        if checks["max_balance_sheet_abs_error"] > MODEL_TOLERANCE:
            hard_failures.append(
                {
                    "code": "BALANCE_SHEET_DOES_NOT_BALANCE",
                    "message": f"{scenario}: balance sheet error exceeds tolerance.",
                }
            )
        if checks["max_cash_tie_abs_error"] > MODEL_TOLERANCE:
            hard_failures.append(
                {
                    "code": "CASH_DOES_NOT_TIE",
                    "message": f"{scenario}: ending cash does not tie to cash flow statement.",
                }
            )
        if checks["max_retained_earnings_abs_error"] > MODEL_TOLERANCE:
            hard_failures.append(
                {
                    "code": "RETAINED_EARNINGS_ROLLFORWARD_FAIL",
                    "message": f"{scenario}: retained earnings roll-forward fails.",
                }
            )
        if checks["max_debt_rollforward_abs_error"] > MODEL_TOLERANCE:
            hard_failures.append(
                {
                    "code": "DEBT_ROLLFORWARD_FAIL",
                    "message": f"{scenario}: debt roll-forward fails.",
                }
            )
        if checks["max_ppe_rollforward_abs_error"] > MODEL_TOLERANCE:
            hard_failures.append(
                {
                    "code": "PPE_ROLLFORWARD_FAIL",
                    "message": f"{scenario}: PP&E roll-forward fails.",
                }
            )
        if checks["max_nwc_rollforward_abs_error"] > MODEL_TOLERANCE:
            hard_failures.append(
                {
                    "code": "NWC_ROLLFORWARD_FAIL",
                    "message": f"{scenario}: working capital roll-forward fails.",
                }
            )

        cov = result["covenants_liquidity"]
        if max(cov["covenant_breach_flag"] or [0.0]) > 0:
            warnings.append(
                {
                    "code": "LIQUIDITY_OR_COVENANT_ISSUE",
                    "message": f"{scenario}: liquidity or covenant headroom issue appears in forecast.",
                }
            )
        if min(result["debt"]["ending_cash"] or [0.0]) < -MODEL_TOLERANCE:
            warnings.append(
                {
                    "code": "NEGATIVE_CASH",
                    "message": f"{scenario}: ending cash falls below zero.",
                }
            )

    base = scenario_outputs.get("base")
    downside = scenario_outputs.get("downside")
    upside = scenario_outputs.get("upside")
    if base and downside and upside:
        b = summarize_result(base)
        d = summarize_result(downside)
        u = summarize_result(upside)
        if (
            abs(b["final_revenue"] - d["final_revenue"]) < MODEL_TOLERANCE
            and abs(b["final_revenue"] - u["final_revenue"]) < MODEL_TOLERANCE
        ):
            hard_failures.append(
                {
                    "code": "SCENARIO_SWITCH_NO_OUTPUT_CHANGE",
                    "message": "scenario switch changes labels but not material model outputs.",
                }
            )

    source_basis = plan.get("source_basis", [])
    if not source_basis:
        hard_failures.append(
            {
                "code": "SOURCE_BASIS_MISSING",
                "message": "source_basis is missing for material historicals or forecast drivers.",
            }
        )
    else:
        covers = {cover for src in source_basis for cover in src.get("covers", [])}
        if "historicals" not in covers:
            hard_failures.append(
                {
                    "code": "HISTORICAL_SOURCE_MISSING",
                    "message": "source_basis does not cover historical financials.",
                }
            )
        if not ({"revenue", "forecast", "costs"} & covers):
            hard_failures.append(
                {
                    "code": "FORECAST_SOURCE_MISSING",
                    "message": "source_basis does not cover material forecast drivers.",
                }
            )
        if any(src.get("evidence_label") == "placeholder" for src in source_basis):
            warnings.append(
                {
                    "code": "PLACEHOLDER_ASSUMPTIONS_ACTIVE",
                    "message": "placeholder source basis remains active; model should be treated as screen-grade only.",
                }
            )
        warnings.extend(source_freshness_warnings(plan))

    # Senior judgment warnings.
    hist_is = last_hist_is(plan)
    hist_revenue = float(hist_is.get("revenue", 0.0) or 0.0)
    if base and hist_revenue > 0:
        first_revenue = base["income_statement"]["revenue"][0]
        final_revenue = base["income_statement"]["revenue"][-1]
        periods_count = max(1, len(base["periods"]))
        annualized_cagr = (
            (final_revenue / hist_revenue) ** (1.0 / periods_count) - 1.0
            if final_revenue > 0
            else -1.0
        )
        if annualized_cagr > 0.20:
            warnings.append(
                {
                    "code": "AGGRESSIVE_REVENUE_RAMP",
                    "message": "base case revenue CAGR exceeds 20%; verify capacity, market share, sales productivity, and demand evidence.",
                }
            )
        if first_revenue > hist_revenue * 1.25:
            warnings.append(
                {
                    "code": "STEP_UP_REVENUE",
                    "message": "first forecast period revenue steps up more than 25% from latest historical period.",
                }
            )

    if base:
        gm_first = (
            base["income_statement"]["gross_profit"][0] / base["income_statement"]["revenue"][0]
        )
        gm_last = (
            base["income_statement"]["gross_profit"][-1] / base["income_statement"]["revenue"][-1]
        )
        if gm_last - gm_first > 0.05:
            warnings.append(
                {
                    "code": "UNSUPPORTED_MARGIN_EXPANSION",
                    "message": "gross margin expands by more than 500 bps; verify mix, pricing, utilization, input costs, and sourcing evidence.",
                }
            )
        capex = base["ppe"]["capex"][-1]
        da = base["ppe"]["depreciation"][-1]
        rev_growth = (
            (base["income_statement"]["revenue"][-1] / base["income_statement"]["revenue"][0] - 1.0)
            if base["income_statement"]["revenue"][0]
            else 0.0
        )
        if rev_growth > 0.10 and capex < da * 0.75:
            warnings.append(
                {
                    "code": "CAPEX_TOO_LOW_FOR_GROWTH",
                    "message": "capex is below 75% of D&A despite forecast revenue growth; verify maintenance and growth capex.",
                }
            )
        hist_nwc_ratio = last_nwc(plan) / hist_revenue if hist_revenue else 0.0
        forecast_nwc_ratio = (
            base["working_capital"]["nwc"][-1] / base["income_statement"]["revenue"][-1]
            if base["income_statement"]["revenue"][-1]
            else 0.0
        )
        if hist_nwc_ratio - forecast_nwc_ratio > 0.05:
            warnings.append(
                {
                    "code": "WORKING_CAPITAL_RELEASE_INCONSISTENT_WITH_HISTORY",
                    "message": "forecast working capital intensity improves by more than 500 bps vs. history; verify DSO/DIO/DPO assumptions.",
                }
            )

    return hard_failures, warnings, checks_summary


def model_status(
    hard_failures: list[dict[str, str]],
    warnings: list[dict[str, str]],
    plan: dict[str, Any],
) -> str:
    if hard_failures:
        return "not-decision-ready"
    if any(w.get("code") == "PLACEHOLDER_ASSUMPTIONS_ACTIVE" for w in warnings):
        return "screen-grade"
    if warnings:
        return "senior-review-ready"
    labels = {src.get("evidence_label") for src in plan.get("source_basis", [])}
    if labels and labels <= {
        "source_reported",
        "connector_sourced",
        "public_filing",
        "web_verified",
        "management_guidance",
        "company_provided",
    }:
        return "decision-grade"
    return "senior-review-ready"


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isinf(value):
            return "n/m"
        return f"{value:,.1f}"
    return str(value)


def to_model_rows(plan: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scenario = result["scenario"]
    periods = result["periods"]
    unit = plan.get("meta", {}).get("units", "")

    def add(
        statement: str,
        section: str,
        line_item: str,
        series: list[float],
        formula_basis: str,
        evidence_label: str = "model_calculated",
        source_id: str = "",
        notes: str = "",
    ) -> None:
        for period, value in zip(periods, series):
            rows.append(
                {
                    "scenario": scenario,
                    "statement": statement,
                    "section": section,
                    "line_item": line_item,
                    "period": period.label,
                    "value": value,
                    "unit": unit,
                    "evidence_label": evidence_label,
                    "source_id": source_id,
                    "formula_basis": formula_basis,
                    "notes": notes,
                }
            )

    is_ = result["income_statement"]
    bs = result["balance_sheet"]
    cf = result["cash_flow_statement"]
    debt = result["debt"]
    wc = result["working_capital"]
    ppe = result["ppe"]
    cov = result["covenants_liquidity"]

    add(
        "IS",
        "Revenue",
        "Revenue",
        is_["revenue"],
        "driver-based revenue forecast",
        result["revenue_detail"].get("evidence_label", "model_calculated"),
        result["revenue_detail"].get("source_id", ""),
    )
    add("IS", "COGS", "COGS", is_["cogs"], "revenue x (1 - gross margin)")
    add("IS", "Gross Profit", "Gross Profit", is_["gross_profit"], "revenue - COGS")
    add(
        "IS",
        "Opex",
        "Operating Expense",
        is_["opex"],
        "revenue x opex percent or amount",
    )
    add("IS", "Profitability", "EBITDA", is_["ebitda"], "gross profit - opex")
    add("IS", "Profitability", "D&A", is_["da"], "from PP&E schedule")
    add("IS", "Profitability", "EBIT", is_["ebit"], "EBITDA - D&A")
    add(
        "IS",
        "Financing",
        "Interest Expense",
        is_["interest"],
        "average debt x interest rate",
    )
    add("IS", "Taxes", "EBT", is_["ebt"], "EBIT - interest")
    add("IS", "Taxes", "Book Taxes", is_["book_taxes"], "positive EBT x book tax rate")
    add(
        "IS",
        "Taxes",
        "Cash Taxes",
        is_["cash_taxes"],
        "taxable income after NOL x cash tax rate",
    )
    add("IS", "Net Income", "Net Income", is_["net_income"], "EBT - book taxes")

    for line in [
        "cash",
        "ar",
        "inventory",
        "other_current_assets",
        "ppe_net",
        "other_assets",
        "total_assets",
        "ap",
        "accrued_expenses",
        "deferred_revenue",
        "debt",
        "other_liabilities",
        "common_equity",
        "retained_earnings",
        "total_liabilities_equity",
        "balance_check",
    ]:
        add(
            "BS",
            "Balance Sheet",
            line.replace("_", " ").title(),
            bs[line],
            "linked balance sheet schedule",
        )

    for line in [
        "net_income",
        "da",
        "deferred_tax",
        "change_nwc",
        "cash_flow_from_operations",
        "capex",
        "cash_flow_from_investing",
        "debt_draws",
        "debt_repayments",
        "dividends",
        "buybacks",
        "issuance",
        "cash_flow_from_financing",
        "cash_change",
        "ending_cash",
    ]:
        add(
            "CF",
            "Cash Flow",
            line.replace("_", " ").title(),
            cf[line],
            "cash flow statement roll-forward",
        )

    for line in [
        "beginning_debt",
        "scheduled_draws",
        "required_draws",
        "total_draws",
        "mandatory_repayment",
        "optional_repayment",
        "total_repayments",
        "interest_rate",
        "interest",
        "ending_debt",
        "ending_revolver_drawn",
        "revolver_availability",
        "minimum_cash",
    ]:
        add(
            "DEBT",
            "Debt",
            line.replace("_", " ").title(),
            debt[line],
            "debt roll-forward and cash sweep",
        )

    for line in [
        "ar_days",
        "inventory_days",
        "ap_days",
        "ar",
        "inventory",
        "other_current_assets",
        "ap",
        "accrued_expenses",
        "deferred_revenue",
        "nwc",
        "change_nwc",
    ]:
        add(
            "WORKING_CAPITAL",
            "Working Capital",
            line.replace("_", " ").title(),
            wc[line],
            "days/percent-driven working capital",
        )

    for line in ["beginning_ppe", "capex", "depreciation", "disposals", "ending_ppe"]:
        add(
            "PPE",
            "PP&E",
            line.replace("_", " ").title(),
            ppe[line],
            "PP&E roll-forward",
        )

    for line in [
        "net_debt",
        "liquidity",
        "net_leverage",
        "interest_coverage",
        "liquidity_headroom",
        "net_leverage_headroom",
        "interest_coverage_headroom",
        "covenant_breach_flag",
    ]:
        add(
            "COVENANTS_LIQUIDITY",
            "Liquidity",
            line.replace("_", " ").title(),
            cov[line],
            "liquidity and covenant metrics",
        )

    for pc in result["checks"]["period_checks"]:
        for key, value in pc.items():
            if key == "period":
                continue
            rows.append(
                {
                    "scenario": scenario,
                    "statement": "CHECKS",
                    "section": "QA",
                    "line_item": key.replace("_", " ").title(),
                    "period": pc["period"],
                    "value": value,
                    "unit": unit,
                    "evidence_label": "model_calculated",
                    "source_id": "",
                    "formula_basis": "machine-computed tie-out check",
                    "notes": "hard failure if above tolerance",
                }
            )
    return rows


def assumption_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def walk(prefix: str, node: Any, source_id: str = "", evidence_label: str = "") -> None:
        if isinstance(node, dict):
            sid = node.get("source_id", source_id)
            ev = node.get("evidence_label", evidence_label)
            for key, value in node.items():
                if key in {"source_id", "evidence_label", "description", "notes"}:
                    continue
                walk(f"{prefix}.{key}" if prefix else key, value, sid, ev)
        elif isinstance(node, list):
            rows.append(
                {
                    "assumption_path": prefix,
                    "period_or_key": "list",
                    "value": json.dumps(node),
                    "evidence_label": evidence_label,
                    "source_id": source_id,
                    "notes": "list assumption",
                }
            )
        else:
            bits = prefix.split(".")
            period_or_key = bits[-1] if bits else ""
            category = ".".join(bits[:-1]) if len(bits) > 1 else prefix
            rows.append(
                {
                    "assumption_path": category,
                    "period_or_key": period_or_key,
                    "value": node,
                    "evidence_label": evidence_label,
                    "source_id": source_id,
                    "notes": "",
                }
            )

    for top in [
        "revenue",
        "costs",
        "working_capital",
        "ppe",
        "debt",
        "tax",
        "equity",
        "scenarios",
        "sensitivities",
    ]:
        if top in plan:
            walk(top, plan[top])
    return rows


def summary_rows(
    plan: dict[str, Any], scenario_outputs: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario, result in scenario_outputs.items():
        s = summarize_result(result)
        for key, value in s.items():
            rows.append(
                {
                    "scenario": scenario,
                    "metric": key,
                    "value": value,
                    "unit": plan.get("meta", {}).get("units", ""),
                    "notes": "scenario summary",
                }
            )
    return rows


def check_rows(scenario_outputs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario, result in scenario_outputs.items():
        for key, value in result["checks"].items():
            if key == "period_checks":
                continue
            rows.append(
                {
                    "scenario": scenario,
                    "check": key,
                    "value": value,
                    "pass": abs(float(value)) <= MODEL_TOLERANCE,
                    "tolerance": MODEL_TOLERANCE,
                }
            )
    return rows


def source_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(src) for src in plan.get("source_basis", [])]


def p0_handoff(
    plan: dict[str, Any],
    scenario_outputs: dict[str, dict[str, Any]],
    hard_failures: list[dict[str, str]],
    warnings: list[dict[str, str]],
    status: str,
) -> dict[str, Any]:
    scenarios = {name: summarize_result(result) for name, result in scenario_outputs.items()}
    base = scenarios.get("base", {})
    all_liquidity = [summary.get("liquidity_trough", 0.0) for summary in scenarios.values()]
    return {
        "operating_forecast_summary": {
            "company_name": plan.get("meta", {}).get("company_name"),
            "industry": plan.get("meta", {}).get("industry"),
            "currency": plan.get("meta", {}).get("currency"),
            "units": plan.get("meta", {}).get("units"),
            "final_period": base.get("final_period"),
        },
        "scenario_outputs": scenarios,
        "base_downside_upside_revenue_ebitda_fcf_cash": {
            name: {
                "final_revenue": s.get("final_revenue"),
                "final_ebitda": s.get("final_ebitda"),
                "final_fcf": s.get("final_fcf"),
                "ending_cash": s.get("ending_cash"),
            }
            for name, s in scenarios.items()
        },
        "liquidity_trough": min(all_liquidity) if all_liquidity else None,
        "key_operating_drivers": [
            "revenue growth",
            "gross margin",
            "opex leverage",
            "DSO/DIO/DPO",
            "capex intensity",
            "interest rate",
            "cash sweep",
        ],
        "checks_passed_failed": {
            "hard_failure_count": len(hard_failures),
            "warning_count": len(warnings),
        },
        "model_status": status,
        "paths": {
            "workbook": "output/model.xlsx",
            "plan": "output/plan.json",
            "run_log": "output/run_log.json",
            "support_note": "output/support_note.md",
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Library module for three-statement-model-builder. "
            "Use scripts/run_pipeline.py for deterministic CLI execution."
        )
    )
    parser.parse_args()
    print(
        "This is a library module. Use scripts/run_pipeline.py to build a three-statement model export."
    )
