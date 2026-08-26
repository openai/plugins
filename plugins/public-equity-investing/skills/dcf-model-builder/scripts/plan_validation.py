"""Structural validation for dcf-model-builder plans.

This module intentionally does not compute valuation outputs. The model engine
adds final computed WACC/terminal-value validation after this structural pass.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

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


def _validate_meta(errors: list[str], plan: dict[str, Any]) -> datetime | None:
    meta = plan.get("meta", {})
    for field in [
        "company",
        "industry",
        "currency",
        "units",
        "valuation_date",
        "as_of_date",
        "accounting_basis",
        "valuation_purpose",
        "model_type",
    ]:
        if not meta.get(field):
            errors.append(f"meta.{field} is required")
    if meta.get("model_type") not in {"fcff", "fcfe"}:
        errors.append("meta.model_type must be 'fcff' or 'fcfe'")
    for field in ["valuation_date", "as_of_date"]:
        if meta.get(field) and not _date_ok(meta[field]):
            errors.append(f"meta.{field} must be YYYY-MM-DD")
    return _date(str(meta.get("valuation_date", ""))) or _date(str(meta.get("as_of_date", "")))


def _validate_sources(
    errors: list[str], plan: dict[str, Any], model_cutoff_date: datetime | None
) -> set[str]:
    source_basis = plan.get("source_basis")
    source_ids: set[str] = set()
    if not isinstance(source_basis, list) or not source_basis:
        errors.append("source_basis must be a non-empty list")
        return source_ids

    topics = set()
    for idx, src in enumerate(source_basis):
        if not isinstance(src, dict):
            errors.append(f"source_basis[{idx}] must be an object")
            continue
        for field in [
            "id",
            "topic",
            "label",
            "source_name",
            "source_type",
            "as_of_date",
            "confidence",
            "notes",
        ]:
            if field not in src or src.get(field) in (None, ""):
                errors.append(f"source_basis[{idx}].{field} is required")
        sid = str(src.get("id", ""))
        if sid:
            if sid in source_ids:
                errors.append(f"source_basis id '{sid}' is duplicated")
            source_ids.add(sid)
        if src.get("topic"):
            topics.add(str(src.get("topic")))
        if src.get("label") and src.get("label") not in ALLOWED_LABELS:
            errors.append(f"source_basis[{idx}].label '{src.get('label')}' is not allowed")
        if src.get("confidence") and src.get("confidence") not in {
            "high",
            "medium",
            "low",
        }:
            errors.append(f"source_basis[{idx}].confidence must be high, medium, or low")
        if src.get("as_of_date") and not _date_ok(src["as_of_date"]):
            errors.append(f"source_basis[{idx}].as_of_date must be YYYY-MM-DD")
        source_as_of_date = _date(str(src.get("as_of_date", "")))
        if model_cutoff_date and source_as_of_date and source_as_of_date > model_cutoff_date:
            errors.append(f"source_basis[{idx}].as_of_date cannot be after meta.valuation_date")

    missing_topics = sorted(REQUIRED_SOURCE_TOPICS - topics)
    if missing_topics:
        errors.append("source_basis missing required material topics: " + ", ".join(missing_topics))
    return source_ids


def _validate_timeline(errors: list[str], plan: dict[str, Any]) -> int:
    timeline = plan.get("timeline", {})
    horizon = timeline.get("horizon_years")
    if not isinstance(timeline.get("start_year"), int):
        errors.append("timeline.start_year must be an integer")
    if not isinstance(horizon, int) or horizon < 1 or horizon > 15:
        errors.append("timeline.horizon_years must be an integer from 1 to 15")
        horizon = 0
    if timeline.get("periodicity") not in {"annual", "quarterly"}:
        errors.append("timeline.periodicity must be 'annual' or 'quarterly'")
    return int(horizon or 0)


def _validate_historicals(errors: list[str], plan: dict[str, Any]) -> None:
    historicals = plan.get("historicals", {})
    hist_required = [
        "latest_year",
        "revenue",
        "ebitda",
        "ebit",
        "cash_taxes",
        "da",
        "capex",
        "change_nwc",
        "net_working_capital",
        "unlevered_fcf",
        "source_id",
    ]
    for field in hist_required:
        if field not in historicals:
            errors.append(f"historicals.{field} is required")
    numeric_fields = [
        "revenue",
        "ebitda",
        "ebit",
        "cash_taxes",
        "da",
        "capex",
        "change_nwc",
        "net_working_capital",
        "unlevered_fcf",
    ]
    for field in numeric_fields:
        if field in historicals and not _is_number(historicals[field]):
            errors.append(f"historicals.{field} must be numeric")
    if (
        "revenue" in historicals
        and _is_number(historicals.get("revenue"))
        and historicals["revenue"] <= 0
    ):
        errors.append("historicals.revenue must be greater than zero")
    if plan.get("meta", {}).get("model_type") == "fcfe" and "net_income" not in historicals:
        errors.append("historicals.net_income is required for FCFE models")


def _validate_source_references(
    errors: list[str], plan: dict[str, Any], source_ids: set[str]
) -> None:
    paths = [
        "historicals.source_id",
        "forecast.source_id",
        "wacc.source_id",
        "terminal_value.source_id",
        "ev_to_equity_bridge.net_debt_source_id",
        "ev_to_equity_bridge.share_count_source_id",
    ]
    for path in paths:
        sid = _get(plan, path)
        if sid and str(sid) not in source_ids:
            errors.append(f"{path} references unknown source id '{sid}'")


def _validate_forecast(errors: list[str], plan: dict[str, Any]) -> None:
    forecast = plan.get("forecast", {})
    meta = plan.get("meta", {})
    if forecast.get("cash_flow_basis") not in {"fcff", "fcfe"}:
        errors.append("forecast.cash_flow_basis must be 'fcff' or 'fcfe'")
    if (
        forecast.get("cash_flow_basis")
        and meta.get("model_type")
        and forecast.get("cash_flow_basis") != meta.get("model_type")
    ):
        errors.append("forecast.cash_flow_basis must match meta.model_type")
    if not isinstance(forecast.get("mid_year_convention"), bool):
        errors.append("forecast.mid_year_convention must be true or false")


def _validate_wacc(errors: list[str], plan: dict[str, Any]) -> None:
    wacc = plan.get("wacc", {})
    required = [
        "risk_free_rate",
        "beta",
        "equity_risk_premium",
        "size_premium",
        "pre_tax_cost_of_debt",
        "marginal_tax_rate",
        "target_debt_pct",
        "target_equity_pct",
        "source_id",
    ]
    for field in required:
        if field not in wacc:
            errors.append(f"wacc.{field} is required")
    range_checks = {
        "risk_free_rate": (-0.02, 0.20),
        "beta": (0.0, 5.0),
        "equity_risk_premium": (0.0, 0.20),
        "size_premium": (0.0, 0.15),
        "company_specific_premium": (-0.05, 0.25),
        "country_risk_premium": (0.0, 0.30),
        "pre_tax_cost_of_debt": (0.0, 0.40),
        "marginal_tax_rate": (0.0, 0.60),
        "target_debt_pct": (0.0, 1.0),
        "target_equity_pct": (0.0, 1.0),
    }
    for field, (low, high) in range_checks.items():
        if field not in wacc:
            continue
        if not _is_number(wacc[field]):
            errors.append(f"wacc.{field} must be numeric")
            continue
        value = float(wacc[field])
        if value < low or value > high:
            errors.append(f"wacc.{field} must be between {low} and {high}")
    if _is_number(wacc.get("target_debt_pct")) and _is_number(wacc.get("target_equity_pct")):
        preferred = _num(wacc.get("preferred_pct"), 0.0)
        total_weight = float(wacc["target_debt_pct"]) + float(wacc["target_equity_pct"]) + preferred
        if abs(total_weight - 1.0) > 0.02:
            errors.append(
                f"wacc capital structure weights must sum to approximately 1.0; found {total_weight:.3f}"
            )


def _validate_terminal_value(errors: list[str], plan: dict[str, Any]) -> str | None:
    terminal = plan.get("terminal_value", {})
    method = terminal.get("method")
    if method not in {"perpetual_growth", "exit_multiple"}:
        errors.append("terminal_value.method must be 'perpetual_growth' or 'exit_multiple'")
    if method == "perpetual_growth":
        if not _is_number(terminal.get("perpetual_growth_rate")):
            errors.append(
                "terminal_value.perpetual_growth_rate is required and numeric for perpetual growth"
            )
        else:
            growth = float(terminal["perpetual_growth_rate"])
            if growth < -0.05 or growth > 0.08:
                errors.append("terminal_value.perpetual_growth_rate must be between -5% and 8%")
    if method == "exit_multiple" and not _is_number(terminal.get("exit_ebitda_multiple")):
        errors.append(
            "terminal_value.exit_ebitda_multiple is required and numeric for exit multiple"
        )
    if (
        method == "exit_multiple"
        and _is_number(terminal.get("exit_ebitda_multiple"))
        and float(terminal["exit_ebitda_multiple"]) <= 0
    ):
        errors.append("terminal_value.exit_ebitda_multiple must be positive")
    if "exit_ebitda_multiple" in terminal and _is_number(terminal.get("exit_ebitda_multiple")):
        multiple = float(terminal["exit_ebitda_multiple"])
        if multiple <= 0 or multiple > 100:
            errors.append(
                "terminal_value.exit_ebitda_multiple must be positive and less than or equal to 100x"
            )
    return method if isinstance(method, str) else None


def _validate_bridge(errors: list[str], plan: dict[str, Any]) -> None:
    bridge = plan.get("ev_to_equity_bridge", {})
    required = [
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
        "diluted_shares",
        "net_debt_source_id",
        "share_count_source_id",
    ]
    for field in required:
        if field not in bridge:
            errors.append(f"ev_to_equity_bridge.{field} is required")
    for field in required:
        if field.endswith("source_id"):
            continue
        if field in bridge and not _is_number(bridge[field]):
            errors.append(f"ev_to_equity_bridge.{field} must be numeric")
    if _is_number(bridge.get("diluted_shares")) and float(bridge["diluted_shares"]) <= 0:
        errors.append("ev_to_equity_bridge.diluted_shares must be greater than zero")


def _validate_scenarios(
    errors: list[str], plan: dict[str, Any], horizon: int, method: str | None
) -> None:
    scenarios = plan.get("scenarios", {})
    forecast = plan.get("forecast", {})
    if not isinstance(scenarios, dict):
        errors.append("scenarios must be an object")
        return
    for name in SCENARIOS:
        if name not in scenarios:
            errors.append(f"scenarios.{name} is required")
            continue
        scenario = scenarios[name]
        if not isinstance(scenario, dict):
            errors.append(f"scenarios.{name} must be an object")
            continue
        if not scenario.get("description"):
            errors.append(f"scenarios.{name}.description is required")
        if horizon:
            _validate_vector(
                errors,
                scenario.get("revenue_growth"),
                f"scenarios.{name}.revenue_growth",
                horizon,
                -0.80,
                2.00,
            )
            _validate_vector(
                errors,
                scenario.get("ebit_margin"),
                f"scenarios.{name}.ebit_margin",
                horizon,
                -0.50,
                0.80,
            )
            _validate_vector(
                errors,
                scenario.get("tax_rate"),
                f"scenarios.{name}.tax_rate",
                horizon,
                0.0,
                0.60,
            )
            _validate_vector(
                errors,
                scenario.get("da_percent_revenue"),
                f"scenarios.{name}.da_percent_revenue",
                horizon,
                0.0,
                1.00,
            )
            _validate_vector(
                errors,
                scenario.get("capex_percent_revenue"),
                f"scenarios.{name}.capex_percent_revenue",
                horizon,
                0.0,
                1.50,
            )
            _validate_vector(
                errors,
                scenario.get("nwc_percent_revenue"),
                f"scenarios.{name}.nwc_percent_revenue",
                horizon,
                -1.0,
                1.0,
            )
            if forecast.get("cash_flow_basis") == "fcfe":
                _validate_vector(
                    errors,
                    scenario.get("net_income_margin"),
                    f"scenarios.{name}.net_income_margin",
                    horizon,
                    -0.50,
                    0.80,
                )
                _validate_vector(
                    errors,
                    scenario.get("net_borrowing", 0.0),
                    f"scenarios.{name}.net_borrowing",
                    horizon,
                    -1e9,
                    1e9,
                )
        if not _is_number(scenario.get("wacc_adjustment")):
            errors.append(f"scenarios.{name}.wacc_adjustment must be numeric")
        if method == "perpetual_growth":
            if not _is_number(scenario.get("terminal_growth_rate")):
                errors.append(f"scenarios.{name}.terminal_growth_rate is required and numeric")
            else:
                terminal_growth = float(scenario["terminal_growth_rate"])
                if terminal_growth < -0.05 or terminal_growth > 0.08:
                    errors.append(
                        f"scenarios.{name}.terminal_growth_rate must be between -5% and 8%"
                    )
        if scenario.get("exit_ebitda_multiple") is not None and not _is_number(
            scenario.get("exit_ebitda_multiple")
        ):
            errors.append(f"scenarios.{name}.exit_ebitda_multiple must be numeric when supplied")


def _validate_sensitivities(errors: list[str], plan: dict[str, Any]) -> None:
    sensitivities = plan.get("sensitivities", {})
    fields = [
        "wacc_delta",
        "terminal_growth_delta",
        "exit_multiple_delta",
        "revenue_growth_delta",
        "ebit_margin_delta",
    ]
    for field in fields:
        value = sensitivities.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"sensitivities.{field} must be a non-empty list")
            continue
        if 0.0 not in [float(v) for v in value if _is_number(v)]:
            errors.append(f"sensitivities.{field} should include 0.0")
        for idx, item in enumerate(value):
            if not _is_number(item):
                errors.append(f"sensitivities.{field}[{idx}] must be numeric")


def validate_plan_structure_without_computed_checks(plan: dict[str, Any]) -> list[str]:
    """Return actionable structural validation errors. Does not compute valuation outputs."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in plan:
            errors.append(f"missing top-level field: {key}")
    if errors:
        return errors

    model_cutoff_date = _validate_meta(errors, plan)
    source_ids = _validate_sources(errors, plan, model_cutoff_date)
    horizon = _validate_timeline(errors, plan)
    _validate_historicals(errors, plan)
    _validate_source_references(errors, plan, source_ids)
    _validate_forecast(errors, plan)
    _validate_wacc(errors, plan)
    method = _validate_terminal_value(errors, plan)
    _validate_bridge(errors, plan)
    _validate_scenarios(errors, plan, horizon, method)
    _validate_sensitivities(errors, plan)
    return errors
