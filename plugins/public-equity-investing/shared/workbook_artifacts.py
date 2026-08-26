"""Shared workbook cover helpers for Public Equity Investing deterministic artifacts."""

from __future__ import annotations

import math
from typing import Any, Iterable, Mapping, Sequence


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, float) and not math.isfinite(value):
        return default
    return str(value)


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _fmt(value: Any, default: str = "n/a") -> str:
    num = _number(value)
    if num is None:
        return _text(value, default)
    if abs(num) >= 100:
        return f"{num:,.1f}"
    if abs(num) >= 10:
        return f"{num:,.2f}"
    return f"{num:,.3f}"


def _fmt_pct(value: Any, default: str = "n/a") -> str:
    num = _number(value)
    if num is None:
        return _text(value, default)
    if abs(num) <= 2:
        return f"{num * 100:,.1f}%"
    return f"{num:,.1f}%"


def _join_messages(items: Sequence[Any] | None, limit: int = 3) -> str:
    if not items:
        return "None flagged"
    out: list[str] = []
    for item in items[:limit]:
        if isinstance(item, Mapping):
            out.append(_text(item.get("message") or item.get("code") or item))
        else:
            out.append(_text(item))
    suffix = "" if len(items) <= limit else f" (+{len(items) - limit} more)"
    return "; ".join(out) + suffix


def cover_dict_rows(rows: Iterable[Sequence[Any]]) -> list[dict[str, Any]]:
    return [
        {
            "section": row[0] if len(row) > 0 else "",
            "metric": row[1] if len(row) > 1 else "",
            "value": row[2] if len(row) > 2 else "",
            "notes": row[3] if len(row) > 3 else "",
        }
        for row in rows
    ]


def dcf_cover_rows(
    plan: Mapping[str, Any],
    scenario_results: Mapping[str, Mapping[str, Any]],
    sensitivity_result: Mapping[str, Any],
    checks: Mapping[str, Any],
    run_log: Mapping[str, Any],
) -> list[list[Any]]:
    meta = plan.get("meta", {}) if isinstance(plan.get("meta"), Mapping) else {}
    source_basis = (
        plan.get("source_basis", []) if isinstance(plan.get("source_basis"), list) else []
    )
    scenarios = [name for name in ("downside", "base", "upside") if name in scenario_results]
    values = [
        _number(scenario_results[name].get("value_per_share"))
        for name in scenarios
        if _number(scenario_results[name].get("value_per_share")) is not None
    ]
    base = scenario_results.get("base", {})
    terminal = base.get("terminal", {}) if isinstance(base.get("terminal"), Mapping) else {}
    pv = base.get("pv", {}) if isinstance(base.get("pv"), Mapping) else {}
    wacc = base.get("wacc", {}) if isinstance(base.get("wacc"), Mapping) else {}
    sensitivity_rows = (
        sensitivity_result.get("rows", [])
        if isinstance(sensitivity_result.get("rows"), list)
        else []
    )
    drivers: list[tuple[str, float]] = []
    for sensitivity in sorted(
        {_text(row.get("sensitivity")) for row in sensitivity_rows if isinstance(row, Mapping)}
    ):
        vals = [
            _number(row.get("value"))
            for row in sensitivity_rows
            if isinstance(row, Mapping) and _text(row.get("sensitivity")) == sensitivity
        ]
        nums = [v for v in vals if v is not None]
        if nums:
            drivers.append((sensitivity, max(nums) - min(nums)))
    drivers.sort(key=lambda item: item[1], reverse=True)
    value_range = f"{_fmt(min(values))} - {_fmt(max(values))} per share" if values else "n/a"
    exit_multiple = _fmt(terminal.get("exit_ebitda_multiple"))
    exit_multiple_label = f"{exit_multiple}x" if exit_multiple != "n/a" else "n/a"

    rows: list[list[Any]] = [
        ["Section", "Metric", "Value", "Notes"],
        ["Header", "Company", meta.get("company", ""), "DCF workbook landing page"],
        [
            "Header",
            "Decision question",
            "What valuation range is supportable?",
            "Cover must answer the investment question, not just navigate the workbook",
        ],
        ["Header", "Model type", meta.get("model_type", ""), "FCFF/FCFE basis should be explicit"],
        [
            "Header",
            "Valuation date",
            meta.get("valuation_date", ""),
            "Use source freeze before PM/IC use",
        ],
        [
            "Header",
            "Currency / units",
            f"{meta.get('currency', '')} / {meta.get('units', '')}",
            "Do not mix share and enterprise metrics",
        ],
        ["Status", "Model status", run_log.get("model_status", ""), "Decision-readiness label"],
        [
            "Status",
            "Workbook mode",
            run_log.get("workbook_mode", ""),
            "Deterministic value export, not a fully linked banker formula workbook",
        ],
        [
            "Status",
            "Hard failures",
            len(run_log.get("hard_failures", []) or []),
            _join_messages(run_log.get("hard_failures", [])),
        ],
        [
            "Status",
            "Warnings",
            len(run_log.get("warnings", []) or []),
            _join_messages(run_log.get("warnings", [])),
        ],
        [
            "Executive read-through",
            "Net read",
            value_range,
            "Headline output; downside/base/upside scenario range",
        ],
        [
            "KPI tiles",
            "Base value per share",
            _fmt(base.get("value_per_share")),
            "Headline valuation metric",
        ],
        ["KPI tiles", "Base enterprise value", _fmt(base.get("enterprise_value")), "Base case"],
    ]
    for name in scenarios:
        result = scenario_results[name]
        rows.append(
            [
                "Scenario summary",
                name,
                _fmt(result.get("value_per_share")),
                f"EV {_fmt(result.get('enterprise_value'))}; equity {_fmt(result.get('equity_value'))}; discount rate {_fmt_pct(result.get('discount_rate'))}",
            ]
        )
    rows.extend(
        [
            ["DCF bridge", "PV of FCF", _fmt(pv.get("pv_fcf")), "Base case"],
            [
                "DCF bridge",
                "PV of terminal value",
                _fmt(pv.get("pv_terminal_value")),
                f"TV share of EV {_fmt_pct(base.get('tv_percent_ev'))}",
            ],
            [
                "Assumptions",
                "WACC",
                _fmt_pct(wacc.get("wacc") or base.get("discount_rate")),
                "Base case discount rate",
            ],
            [
                "Assumptions",
                "Terminal method",
                terminal.get("method", ""),
                "Exit multiple or perpetuity growth",
            ],
            [
                "Assumptions",
                "Terminal growth / exit multiple",
                f"{_fmt_pct(terminal.get('terminal_growth_rate'))} / {exit_multiple_label}",
                "Show n/a when not applicable",
            ],
        ]
    )
    for idx, (driver, spread) in enumerate(drivers[:5], start=1):
        rows.append(
            ["Sensitivity read", f"Driver {idx}", driver, f"Value/share spread {_fmt(spread)}"]
        )
    rows.extend(
        [
            [
                "Chart-ready data",
                "Scenario values",
                "Downside / base / upside",
                "Use Summary for chart-ready valuation range",
            ],
            [
                "Chart-ready data",
                "DCF bridge",
                "PV FCF / PV terminal value",
                "Use Cover rows and Summary for bridge chart",
            ],
            [
                "Chart-ready data",
                "Sensitivity drivers",
                ", ".join(driver for driver, _spread in drivers[:3]) or "n/a",
                "Use Sensitivities for full grid",
            ],
            [
                "Source posture",
                "Source count",
                len(source_basis),
                "Review Assumptions tab for source labels and dates",
            ],
            [
                "Source posture",
                "Source caveat",
                "Visible in Assumptions",
                "Unsupported or stale assumptions should not be buried",
            ],
            [
                "Workbook map",
                "Summary",
                "Scenario-level valuation table",
                "Use with Cover for headline range",
            ],
            [
                "Workbook map",
                "Model",
                "Long-format DCF outputs",
                "Source ids and evidence labels retained",
            ],
            [
                "Workbook map",
                "Sensitivities",
                "Chart-ready sensitivity rows",
                "Native charts not produced by the stdlib writer",
            ],
            [
                "Workbook map",
                "Checks / Run Log",
                "QA, warnings, and run status",
                "Resolve hard failures before decision use",
            ],
        ]
    )
    return rows


def three_statement_cover_rows(
    plan: Mapping[str, Any],
    scenario_outputs: Mapping[str, Mapping[str, Any]],
    run_log: Mapping[str, Any],
) -> list[dict[str, Any]]:
    p0 = run_log.get("p0_handoff", {}) if isinstance(run_log.get("p0_handoff"), Mapping) else {}
    summaries = (
        p0.get("scenario_outputs", {}) if isinstance(p0.get("scenario_outputs"), Mapping) else {}
    )
    meta = plan.get("meta", {}) if isinstance(plan.get("meta"), Mapping) else {}
    source_basis = (
        plan.get("source_basis", []) if isinstance(plan.get("source_basis"), list) else []
    )
    base = summaries.get("base", {}) if isinstance(summaries.get("base"), Mapping) else {}
    rows: list[list[Any]] = [
        [
            "Header",
            "Company",
            meta.get("company_name") or meta.get("company", ""),
            "Three-statement model landing page",
        ],
        [
            "Header",
            "Decision question",
            "What operating path, liquidity, and leverage profile is supportable?",
            "Cover must answer the PM question, not just navigate the workbook",
        ],
        [
            "Header",
            "Industry",
            meta.get("industry", ""),
            "Use sector context for KPIs and operating drivers",
        ],
        ["Header", "As-of date", meta.get("as_of_date", ""), "Refresh before PM/IC use"],
        [
            "Header",
            "Currency / units",
            f"{meta.get('currency', '')} / {meta.get('units', '')}",
            "Keep all model outputs on one unit basis",
        ],
        ["Status", "Model status", run_log.get("model_status", ""), "Decision-readiness label"],
        [
            "Status",
            "Workbook mode",
            run_log.get("workbook_mode", ""),
            "Deterministic value export, not a fully linked banker formula workbook",
        ],
        [
            "Status",
            "Hard failures",
            len(run_log.get("hard_failures", []) or []),
            _join_messages(run_log.get("hard_failures", [])),
        ],
        [
            "Status",
            "Warnings",
            len(run_log.get("warnings", []) or []),
            _join_messages(run_log.get("warnings", [])),
        ],
        [
            "Executive read-through",
            "Net read",
            base.get("final_period", ""),
            "Base case final period used for headline outputs",
        ],
        [
            "Executive read-through",
            "Base revenue / EBITDA / FCF",
            f"{_fmt(base.get('final_revenue'))} / {_fmt(base.get('final_ebitda'))} / {_fmt(base.get('final_fcf'))}",
            "Final-period operating read-through",
        ],
        [
            "Executive read-through",
            "Liquidity trough",
            _fmt(p0.get("liquidity_trough")),
            "Minimum liquidity across scenarios",
        ],
        [
            "KPI tiles",
            "Base ending cash",
            _fmt(base.get("ending_cash")),
            "Base case liquidity ending point",
        ],
        [
            "KPI tiles",
            "Base peak net leverage",
            f"{_fmt(base.get('peak_net_leverage'))}x",
            "Base case balance sheet stress",
        ],
    ]
    for name in ("downside", "base", "upside"):
        summary = summaries.get(name)
        if not isinstance(summary, Mapping):
            continue
        rows.append(
            [
                "Scenario summary",
                name,
                f"Revenue {_fmt(summary.get('final_revenue'))}; EBITDA {_fmt(summary.get('final_ebitda'))}; FCF {_fmt(summary.get('final_fcf'))}",
                f"Ending cash {_fmt(summary.get('ending_cash'))}; peak net leverage {_fmt(summary.get('peak_net_leverage'))}x",
            ]
        )
    rows.extend(
        [
            [
                "Chart-ready data",
                "Scenario outputs",
                "Revenue / EBITDA / FCF / cash",
                "Use Summary for chart-ready scenario comparison",
            ],
            [
                "Chart-ready data",
                "Sensitivity outputs",
                "Stress cases",
                "Use Sensitivities for full grid",
            ],
            [
                "Driver dashboard",
                "Key operating drivers",
                ", ".join(p0.get("key_operating_drivers", [])[:6])
                if isinstance(p0.get("key_operating_drivers"), list)
                else "revenue growth, margin, working capital, capex, interest",
                "Use Model tab for period-level detail",
            ],
            [
                "Source posture",
                "Source count",
                len(source_basis),
                "Review Sources and Assumptions tabs for dates and confidence",
            ],
            [
                "QA posture",
                "Checks passed/failed",
                _text(p0.get("checks_passed_failed", "")),
                "Resolve hard failures before decision use",
            ],
            [
                "Workbook map",
                "Summary",
                "Scenario-level final-period outputs",
                "Headline model outputs by scenario",
            ],
            [
                "Workbook map",
                "Model",
                "Long-format three-statement rows",
                "All scenarios and periods",
            ],
            ["Workbook map", "Sensitivities", "Chart-ready stress cases", "Use for driver deltas"],
            [
                "Workbook map",
                "Checks / Run_Log",
                "QA and run status",
                "Review before relying on output",
            ],
        ]
    )
    return cover_dict_rows(rows)
