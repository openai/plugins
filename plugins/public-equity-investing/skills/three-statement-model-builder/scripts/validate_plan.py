#!/usr/bin/env python3
"""Validate plan.json for Three Statement Model Builder.

Usage:
  python3 scripts/validate_plan.py path/to/plan.json

Exit codes:
  0 = valid
  1 = invalid with actionable errors
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from typing import Any

ALLOWED_PERIODICITIES = {"annual", "quarterly"}
ALLOWED_EVIDENCE_LABELS = {
    "source_reported",
    "company_provided",
    "connector_sourced",
    "public_filing",
    "web_verified",
    "management_guidance",
    "analyst_estimate",
    "benchmark",
    "assumption",
    "placeholder",
}
ALLOWED_MODEL_EVIDENCE_LABELS = ALLOWED_EVIDENCE_LABELS | {"model_calculated"}
ALLOWED_ACCOUNTING_BASIS = {"us_gaap", "ifrs", "management", "cash_basis", "unspecified"}


def is_num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value


def err(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def require_obj(parent: dict[str, Any], key: str, errors: list[str], ctx: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        err(errors, f"Missing or invalid object: {ctx}.{key}")
        return {}
    return value


def require_list(parent: dict[str, Any], key: str, errors: list[str], ctx: str) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        err(errors, f"Missing or invalid list: {ctx}.{key}")
        return []
    return value


def validate_number_map(
    value: Any,
    errors: list[str],
    ctx: str,
    low: float = -1e12,
    high: float = 1e12,
    allow_empty: bool = False,
) -> None:
    if value is None:
        if not allow_empty:
            err(errors, f"{ctx} is required")
        return
    if is_num(value):
        if not low <= float(value) <= high:
            err(errors, f"{ctx} must be between {low} and {high}")
        return
    if not isinstance(value, dict):
        err(errors, f"{ctx} must be a number or period map")
        return
    if not value and not allow_empty:
        err(errors, f"{ctx} cannot be empty")
        return
    for key, item in value.items():
        if not is_num(item) or not low <= float(item) <= high:
            err(errors, f"{ctx}.{key} must be numeric between {low} and {high}")


def validate_sources(
    plan: dict[str, Any], errors: list[str], meta_as_of_date: date | None = None
) -> None:
    sources = require_list(plan, "source_basis", errors, "plan")
    ids = set()
    covered = set()
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            err(errors, f"source_basis[{i}] must be an object")
            continue
        sid = src.get("id")
        if not sid:
            err(errors, f"source_basis[{i}].id is required")
        elif sid in ids:
            err(errors, f"duplicate source_basis id: {sid}")
        ids.add(sid)
        if not src.get("label"):
            err(errors, f"source_basis[{i}].label is required")
        if not src.get("source_type"):
            err(errors, f"source_basis[{i}].source_type is required")
        source_date_raw = src.get("as_of_date")
        source_as_of_date = parse_iso_date(source_date_raw)
        if not source_date_raw:
            err(errors, f"source_basis[{i}].as_of_date is required")
        elif source_as_of_date is None:
            err(errors, f"source_basis[{i}].as_of_date must be YYYY-MM-DD")
        elif meta_as_of_date and source_as_of_date > meta_as_of_date:
            err(errors, f"source_basis[{i}].as_of_date cannot be after meta.as_of_date")
        ev = src.get("evidence_label")
        if ev not in ALLOWED_EVIDENCE_LABELS:
            err(
                errors,
                f"source_basis[{i}].evidence_label must be one of {sorted(ALLOWED_EVIDENCE_LABELS)}",
            )
        covers = src.get("covers")
        if not isinstance(covers, list) or not covers:
            err(errors, f"source_basis[{i}].covers must be a non-empty list")
        else:
            covered.update(covers)
    if sources:
        if "historicals" not in covered:
            err(errors, "source_basis must include at least one entry covering 'historicals'")
        if not ({"forecast", "revenue", "costs", "working_capital", "ppe", "debt"} & covered):
            err(
                errors,
                "source_basis must include at least one entry covering material forecast drivers",
            )


def validate_historicals(plan: dict[str, Any], errors: list[str]) -> None:
    hist = require_obj(plan, "historicals", errors, "plan")
    is_hist = require_obj(hist, "income_statement", errors, "historicals")
    bs_hist = require_obj(hist, "balance_sheet", errors, "historicals")
    require_obj(hist, "cash_flow", errors, "historicals")
    require_obj(hist, "debt_schedule", errors, "historicals")
    require_obj(hist, "ppe", errors, "historicals")
    require_obj(hist, "working_capital", errors, "historicals")

    if not is_hist:
        err(errors, "historicals.income_statement must include at least one historical period")
    for period, row in is_hist.items():
        if not isinstance(row, dict):
            err(errors, f"historicals.income_statement.{period} must be an object")
            continue
        for key in ["revenue", "cogs", "opex", "da", "interest", "taxes", "net_income"]:
            if not is_num(row.get(key)):
                err(errors, f"historicals.income_statement.{period}.{key} must be numeric")
        if is_num(row.get("revenue")) and row["revenue"] <= 0:
            err(errors, f"historicals.income_statement.{period}.revenue must be positive")

    if not bs_hist:
        err(errors, "historicals.balance_sheet must include at least one historical period")
    for period, row in bs_hist.items():
        if not isinstance(row, dict):
            err(errors, f"historicals.balance_sheet.{period} must be an object")
            continue
        for key in [
            "cash",
            "ar",
            "inventory",
            "other_current_assets",
            "ppe_net",
            "other_assets",
            "ap",
            "accrued_expenses",
            "deferred_revenue",
            "debt",
            "other_liabilities",
            "common_equity",
            "retained_earnings",
        ]:
            if not is_num(row.get(key)):
                err(errors, f"historicals.balance_sheet.{period}.{key} must be numeric")
        if all(
            is_num(row.get(k))
            for k in [
                "cash",
                "ar",
                "inventory",
                "other_current_assets",
                "ppe_net",
                "other_assets",
                "ap",
                "accrued_expenses",
                "deferred_revenue",
                "debt",
                "other_liabilities",
                "common_equity",
                "retained_earnings",
            ]
        ):
            assets = (
                row["cash"]
                + row["ar"]
                + row["inventory"]
                + row["other_current_assets"]
                + row["ppe_net"]
                + row["other_assets"]
            )
            liab_eq = (
                row["ap"]
                + row["accrued_expenses"]
                + row["deferred_revenue"]
                + row["debt"]
                + row["other_liabilities"]
                + row["common_equity"]
                + row["retained_earnings"]
            )
            if abs(assets - liab_eq) > 0.1:
                err(
                    errors,
                    f"historicals.balance_sheet.{period} does not balance; assets minus liabilities/equity = {assets - liab_eq:.2f}",
                )


def validate_revenue(plan: dict[str, Any], errors: list[str]) -> None:
    rev = require_obj(plan, "revenue", errors, "plan")
    model = rev.get("model")
    if model not in {"segments", "total_growth", "volume_price"}:
        err(errors, "revenue.model must be one of: segments, total_growth, volume_price")
    if rev.get("evidence_label") and rev.get("evidence_label") not in ALLOWED_MODEL_EVIDENCE_LABELS:
        err(errors, "revenue.evidence_label is invalid")
    if model == "segments":
        segments = rev.get("segments")
        if not isinstance(segments, dict) or not segments:
            err(errors, "revenue.segments must be a non-empty object when model='segments'")
        else:
            for name, cfg in segments.items():
                if not isinstance(cfg, dict):
                    err(errors, f"revenue.segments.{name} must be an object")
                    continue
                if not is_num(cfg.get("base_revenue")) or cfg.get("base_revenue", 0) <= 0:
                    err(errors, f"revenue.segments.{name}.base_revenue must be positive")
                validate_number_map(
                    cfg.get("growth_rates"),
                    errors,
                    f"revenue.segments.{name}.growth_rates",
                    -0.9,
                    2.0,
                )
                if (
                    cfg.get("evidence_label")
                    and cfg.get("evidence_label") not in ALLOWED_MODEL_EVIDENCE_LABELS
                ):
                    err(errors, f"revenue.segments.{name}.evidence_label is invalid")
    if model == "total_growth":
        if not is_num(rev.get("base_revenue")) or rev.get("base_revenue", 0) <= 0:
            err(errors, "revenue.base_revenue must be positive for total_growth")
        validate_number_map(rev.get("growth_rates"), errors, "revenue.growth_rates", -0.9, 2.0)
    if model == "volume_price":
        for key in ["base_units", "base_price"]:
            if not is_num(rev.get(key)) or rev.get(key, 0) <= 0:
                err(errors, f"revenue.{key} must be positive for volume_price")
        validate_number_map(
            rev.get("unit_growth_rates"), errors, "revenue.unit_growth_rates", -0.9, 2.0
        )
        validate_number_map(
            rev.get("price_growth_rates"), errors, "revenue.price_growth_rates", -0.9, 2.0
        )


def validate_costs(plan: dict[str, Any], errors: list[str]) -> None:
    costs = require_obj(plan, "costs", errors, "plan")
    cogs = require_obj(costs, "cogs", errors, "costs")
    method = cogs.get("method", "gross_margin")
    if method not in {"gross_margin", "pct_revenue"}:
        err(errors, "costs.cogs.method must be gross_margin or pct_revenue")
    if method == "gross_margin":
        validate_number_map(cogs.get("gross_margin"), errors, "costs.cogs.gross_margin", -0.5, 0.95)
    else:
        validate_number_map(cogs.get("pct_revenue"), errors, "costs.cogs.pct_revenue", 0.0, 1.5)
    opex = require_obj(costs, "opex", errors, "costs")
    omethod = opex.get("method", "pct_revenue")
    if omethod not in {"pct_revenue", "amount"}:
        err(errors, "costs.opex.method must be pct_revenue or amount")
    if omethod == "pct_revenue":
        validate_number_map(opex.get("pct_revenue"), errors, "costs.opex.pct_revenue", 0.0, 1.5)
    else:
        validate_number_map(opex.get("amount"), errors, "costs.opex.amount", 0.0, 1e9)


def validate_working_capital(plan: dict[str, Any], errors: list[str]) -> None:
    wc = require_obj(plan, "working_capital", errors, "plan")
    if wc.get("method", "days") != "days":
        err(errors, "working_capital.method currently must be 'days'")
    validate_number_map(wc.get("ar_days"), errors, "working_capital.ar_days", 0.0, 365.0)
    validate_number_map(
        wc.get("inventory_days"), errors, "working_capital.inventory_days", 0.0, 365.0
    )
    validate_number_map(wc.get("ap_days"), errors, "working_capital.ap_days", 0.0, 365.0)
    validate_number_map(
        wc.get("other_current_assets_pct_revenue"),
        errors,
        "working_capital.other_current_assets_pct_revenue",
        0.0,
        1.0,
    )
    validate_number_map(
        wc.get("accrued_expenses_pct_revenue"),
        errors,
        "working_capital.accrued_expenses_pct_revenue",
        0.0,
        1.0,
    )
    validate_number_map(
        wc.get("deferred_revenue_pct_revenue"),
        errors,
        "working_capital.deferred_revenue_pct_revenue",
        0.0,
        1.0,
    )


def validate_ppe_debt_tax_equity(plan: dict[str, Any], errors: list[str]) -> None:
    ppe = require_obj(plan, "ppe", errors, "plan")
    if ppe.get("capex_method", "pct_revenue") not in {"pct_revenue", "amount"}:
        err(errors, "ppe.capex_method must be pct_revenue or amount")
    if ppe.get("capex_method", "pct_revenue") == "pct_revenue":
        validate_number_map(ppe.get("capex_pct_revenue"), errors, "ppe.capex_pct_revenue", 0.0, 1.0)
    else:
        validate_number_map(ppe.get("capex_amount"), errors, "ppe.capex_amount", 0.0, 1e9)
    if ppe.get("depreciation_method", "pct_beginning_ppe") not in {
        "pct_beginning_ppe",
        "pct_revenue",
        "amount",
    }:
        err(errors, "ppe.depreciation_method must be pct_beginning_ppe, pct_revenue, or amount")
    if ppe.get("depreciation_method", "pct_beginning_ppe") == "pct_beginning_ppe":
        validate_number_map(
            ppe.get("depreciation_pct_beginning_ppe"),
            errors,
            "ppe.depreciation_pct_beginning_ppe",
            0.0,
            1.0,
        )

    debt = require_obj(plan, "debt", errors, "plan")
    if not is_num(debt.get("beginning_debt")) or debt.get("beginning_debt", 0) < 0:
        err(errors, "debt.beginning_debt must be non-negative")
    if (
        not is_num(debt.get("beginning_revolver_drawn", 0.0))
        or debt.get("beginning_revolver_drawn", 0.0) < 0
    ):
        err(errors, "debt.beginning_revolver_drawn must be non-negative")
    if not is_num(debt.get("revolver_commitment", 0.0)) or debt.get("revolver_commitment", 0.0) < 0:
        err(errors, "debt.revolver_commitment must be non-negative")
    validate_number_map(
        debt.get("mandatory_amortization"),
        errors,
        "debt.mandatory_amortization",
        0.0,
        1e9,
        allow_empty=True,
    )
    validate_number_map(
        debt.get("optional_draws", {}), errors, "debt.optional_draws", 0.0, 1e9, allow_empty=True
    )
    validate_number_map(debt.get("interest_rate"), errors, "debt.interest_rate", 0.0, 1.0)
    sweep = require_obj(debt, "cash_sweep", errors, "debt")
    if not is_num(sweep.get("min_cash")) or sweep.get("min_cash", 0) < 0:
        err(errors, "debt.cash_sweep.min_cash must be non-negative")
    if not is_num(sweep.get("sweep_pct")) or not 0 <= sweep.get("sweep_pct", 0) <= 1:
        err(errors, "debt.cash_sweep.sweep_pct must be between 0 and 1")
    cov = debt.get("covenants", {})
    if cov and not isinstance(cov, dict):
        err(errors, "debt.covenants must be an object")

    tax = require_obj(plan, "tax", errors, "plan")
    if not is_num(tax.get("book_tax_rate")) or not 0 <= tax.get("book_tax_rate", 0) <= 0.6:
        err(errors, "tax.book_tax_rate must be between 0 and 0.6")
    if not is_num(tax.get("cash_tax_rate")) or not 0 <= tax.get("cash_tax_rate", 0) <= 0.6:
        err(errors, "tax.cash_tax_rate must be between 0 and 0.6")
    if not is_num(tax.get("nol_balance", 0.0)) or tax.get("nol_balance", 0.0) < 0:
        err(errors, "tax.nol_balance must be non-negative")

    eq = require_obj(plan, "equity", errors, "plan")
    if not is_num(eq.get("common_equity")):
        err(errors, "equity.common_equity must be numeric")
    validate_number_map(
        eq.get("dividends", {}), errors, "equity.dividends", 0.0, 1e9, allow_empty=True
    )
    validate_number_map(
        eq.get("buybacks", {}), errors, "equity.buybacks", 0.0, 1e9, allow_empty=True
    )
    validate_number_map(
        eq.get("issuance", {}), errors, "equity.issuance", 0.0, 1e9, allow_empty=True
    )


def validate_scenarios(plan: dict[str, Any], errors: list[str]) -> None:
    scenarios = require_obj(plan, "scenarios", errors, "plan")
    for name in ["base", "downside", "upside"]:
        if name not in scenarios or not isinstance(scenarios.get(name), dict):
            err(errors, f"scenarios.{name} is required")
            continue
        scenario = scenarios[name]
        if "overrides" not in scenario or not isinstance(scenario.get("overrides"), dict):
            err(errors, f"scenarios.{name}.overrides must be an object")
        ev = scenario.get("evidence_label")
        if ev and ev not in ALLOWED_EVIDENCE_LABELS:
            err(errors, f"scenarios.{name}.evidence_label is invalid")


def validate_sensitivities(plan: dict[str, Any], errors: list[str]) -> None:
    sens = require_obj(plan, "sensitivities", errors, "plan")
    allowed = {
        "revenue_growth_shocks",
        "gross_margin_shocks",
        "dso_day_shocks",
        "capex_pct_revenue_shocks",
        "interest_rate_shocks",
    }
    for key, value in sens.items():
        if key not in allowed:
            err(errors, f"sensitivities.{key} is not supported")
        if not isinstance(value, list):
            err(errors, f"sensitivities.{key} must be a list")
            continue
        for item in value:
            if not is_num(item):
                err(errors, f"sensitivities.{key} entries must be numeric")


def validate(path: str) -> list[str]:
    errors: list[str] = []
    try:
        plan = json.loads(open(path, "r", encoding="utf-8").read())
    except Exception as exc:
        return [f"Could not read/parse JSON: {exc}"]

    meta = require_obj(plan, "meta", errors, "plan")
    meta_as_of_date: date | None = None
    if meta:
        if not meta.get("company_name"):
            err(errors, "meta.company_name is required")
        if not meta.get("industry"):
            err(errors, "meta.industry is required")
        if not meta.get("currency"):
            err(errors, "meta.currency is required")
        if not meta.get("units"):
            err(errors, "meta.units is required")
        if not meta.get("as_of_date"):
            err(errors, "meta.as_of_date is required")
        else:
            meta_as_of_date = parse_iso_date(meta.get("as_of_date"))
            if meta_as_of_date is None:
                err(errors, "meta.as_of_date must be YYYY-MM-DD")
        if meta.get("accounting_basis") not in ALLOWED_ACCOUNTING_BASIS:
            err(errors, f"meta.accounting_basis must be one of {sorted(ALLOWED_ACCOUNTING_BASIS)}")

    timeline = require_obj(plan, "timeline", errors, "plan")
    if timeline:
        if (
            not isinstance(timeline.get("start_year"), int)
            or not 1900 <= timeline.get("start_year", 0) <= 2200
        ):
            err(errors, "timeline.start_year must be an integer year")
        if (
            not isinstance(timeline.get("horizon_periods"), int)
            or not 1 <= timeline.get("horizon_periods", 0) <= 80
        ):
            err(errors, "timeline.horizon_periods must be an integer between 1 and 80")
        if timeline.get("periodicity") not in ALLOWED_PERIODICITIES:
            err(errors, "timeline.periodicity must be annual or quarterly")
        if timeline.get("periodicity") == "annual" and timeline.get("horizon_periods", 0) > 20:
            err(errors, "annual horizon_periods should not exceed 20")
        if timeline.get("periodicity") == "quarterly" and timeline.get("horizon_periods", 0) > 80:
            err(errors, "quarterly horizon_periods should not exceed 80")

    validate_sources(plan, errors, meta_as_of_date)
    validate_historicals(plan, errors)
    validate_revenue(plan, errors)
    validate_costs(plan, errors)
    validate_working_capital(plan, errors)
    validate_ppe_debt_tax_equity(plan, errors)
    validate_scenarios(plan, errors)
    validate_sensitivities(plan, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate three-statement-model-builder plan.json")
    parser.add_argument("plan_path", help="Path to plan.json")
    args = parser.parse_args()

    errors = validate(args.plan_path)
    if errors:
        print("Plan validation FAILED:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("Plan validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
