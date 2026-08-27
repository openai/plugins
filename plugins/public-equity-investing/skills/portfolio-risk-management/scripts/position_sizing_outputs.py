"""Output helpers for the portfolio-risk-management sizing mode."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

from position_sizing_core import fnum


def write_csv(path: Path, headers: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def fmt(x: Any, digits: int = 2) -> str:
    if isinstance(x, float):
        return f"{x:.{digits}f}"
    if x is None:
        return ""
    return str(x)


def output_paths(out: Path) -> dict[str, str]:
    return {
        "position_summary": str(out / "position_summary.csv"),
        "sizing_cases": str(out / "sizing_cases.csv"),
        "scenario_pnl": str(out / "scenario_pnl.csv"),
        "exposure_impact": str(out / "exposure_impact.csv"),
        "liquidity_exit": str(out / "liquidity_exit.csv"),
        "monitoring_rules": str(out / "monitoring_rules.csv"),
        "support_note": str(out / "support_note.md"),
        "run_log": str(out / "run_log.json"),
        "manifest": str(out / "manifest.json"),
    }


def source_basis(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("sources", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def write_report(
    path: Path,
    summary: dict[str, Any],
    sizing: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    liquidity: list[dict[str, Any]],
) -> None:
    lines = [
        f"# Risk Position Sizing - {summary.get('security') or summary.get('ticker') or 'Position'}",
        "",
    ]
    lines += [
        "## Decision summary",
        f"- Direction: {summary.get('direction')}",
        f"- Recommended size: {fmt(summary.get('recommended_size_pct_nav'))}% NAV",
        f"- Recommended notional: {fmt(summary.get('recommended_notional'), 0)}",
        f"- Recommended shares/units: {fmt(summary.get('recommended_shares_or_units'), 0)}",
        f"- Raw binding constraint: {summary.get('raw_binding_constraint')}",
        f"- Confidence: {summary.get('confidence')}",
        "",
    ]
    lines.append("## Sizing constraints")
    for row in sizing:
        if row.get("implied_size_pct_nav") != "":
            lines.append(
                f"- {row.get('sizing_lens')}: {fmt(row.get('implied_size_pct_nav'))}% NAV {row.get('binding_flag', '')}"
            )
    if scenarios:
        lines += ["", "## Scenario P&L"]
        for scenario in scenarios:
            lines.append(
                f"- {scenario.get('scenario')}: {fmt(scenario.get('pnl_pct_nav'))}% NAV P&L; {scenario.get('notes', '')}"
            )
    if liquidity:
        lines += [
            "",
            "## Liquidity",
            f"- Normal exit days: {fmt(liquidity[0].get('days_to_exit'))}",
            f"- Stressed exit days: {fmt(liquidity[0].get('stressed_days_to_exit'))}",
        ]
    lines += [
        "",
        "## PM caveat",
        "Validate live prices, beta, volatility, liquidity, borrow, Greeks, risk limits, and portfolio correlations before using this for a trading decision.",
    ]
    path.write_text("\n".join(lines))


def write_output_bundle(
    out: Path,
    summary: dict[str, Any],
    sizing: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    exposures: list[dict[str, Any]],
    liquidity: list[dict[str, Any]],
    monitoring: list[dict[str, Any]],
) -> None:
    write_csv(
        out / "position_summary.csv",
        [
            "analysis_date",
            "security",
            "ticker",
            "direction",
            "entry_price",
            "recommended_size_pct_nav",
            "recommended_notional",
            "recommended_shares_or_units",
            "raw_binding_constraint",
            "raw_binding_size_pct_nav",
            "confidence",
            "proposed_size_pct_nav",
            "current_size_pct_nav",
        ],
        [summary],
    )
    write_csv(
        out / "sizing_cases.csv",
        [
            "sizing_lens",
            "input_value",
            "formula",
            "implied_size_pct_nav",
            "implied_notional",
            "binding_flag",
            "notes",
        ],
        sizing,
    )
    write_csv(
        out / "scenario_pnl.csv",
        [
            "scenario",
            "probability",
            "price_or_return",
            "pnl_dollars",
            "pnl_pct_nav",
            "time_horizon",
            "liquidity_assumption",
            "action_rule",
            "notes",
        ],
        scenarios,
    )
    write_csv(
        out / "exposure_impact.csv",
        [
            "exposure_type",
            "before",
            "incremental",
            "after",
            "limit",
            "status",
            "source",
        ],
        exposures,
    )
    write_csv(
        out / "liquidity_exit.csv",
        [
            "security",
            "price",
            "adv_shares",
            "adv_dollars",
            "position_shares",
            "position_dollars",
            "position_pct_nav",
            "participation_rate",
            "days_to_exit",
            "stressed_participation_rate",
            "stressed_days_to_exit",
            "notes",
        ],
        liquidity,
    )
    write_csv(
        out / "monitoring_rules.csv",
        ["trigger_type", "metric", "threshold", "action", "owner", "cadence", "source"],
        monitoring,
    )
    write_report(out / "support_note.md", summary, sizing, scenarios, liquidity)


def summarize_console(summary: dict[str, Any]) -> tuple[str, str]:
    return (
        f"Recommended size: {fmt(summary.get('recommended_size_pct_nav'))}% NAV",
        f"Binding constraint: {summary.get('raw_binding_constraint')}",
    )


def has_source_basis(data: dict[str, Any]) -> bool:
    return bool(source_basis(data))


def row_count(rows: Iterable[dict[str, Any]]) -> int:
    return sum(1 for _ in rows)


def positive_size(summary: dict[str, Any]) -> bool:
    value = fnum(summary.get("recommended_size_pct_nav"))
    return value is not None and value > 0
