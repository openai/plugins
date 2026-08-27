"""Supported dashboard module registry.

The registry intentionally describes presentation modules only. Public Equity Investing
skills still own the investment logic that populates each module.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleSpec:
    name: str
    description: str
    required_keys: tuple[str, ...] = ()


MODULES: dict[str, ModuleSpec] = {
    "decision_box": ModuleSpec(
        "decision_box",
        "Top-line investor view with thesis change, action posture, and key points.",
        ("stance",),
    ),
    "metric_tiles": ModuleSpec(
        "metric_tiles",
        "Grid of high-signal metrics such as event date, price, guide, valuation, or risk.",
        ("items",),
    ),
    "highlight_tiles": ModuleSpec(
        "highlight_tiles",
        "Alias for high-signal hero metrics when the producer wants to distinguish PM highlights from routine KPI tiles.",
        ("items",),
    ),
    "executive_summary": ModuleSpec(
        "executive_summary",
        "Dense PM-style summary paragraph with optional watch items and net read.",
    ),
    "key_metrics": ModuleSpec(
        "key_metrics",
        "Dense quarterly KPI board with company-specific operating metrics, growth rates, trajectory, and PM read.",
        ("rows",),
    ),
    "growth_trajectory": ModuleSpec(
        "growth_trajectory",
        "Acceleration/deceleration map across the metrics that matter for the issuer.",
        ("rows",),
    ),
    "cards": ModuleSpec(
        "cards",
        "Reusable card grid for debates, drivers, risks, read-throughs, or thesis pillars.",
        ("items",),
    ),
    "table": ModuleSpec(
        "table",
        "Responsive table for KPIs, consensus, guidance, beat/miss, or source posture.",
        ("columns", "rows"),
    ),
    "scenario_map": ModuleSpec(
        "scenario_map",
        "Bull/base/bear or probability-case cards with drivers and falsifiers.",
        ("cases",),
    ),
    "question_list": ModuleSpec(
        "question_list",
        "Call, diligence, management-meeting, or monitoring questions with listen-fors.",
        ("questions",),
    ),
    "transcript_qa": ModuleSpec(
        "transcript_qa",
        "Dense earnings-call Q&A map with analyst, firm, topic, management response, short direct quote, and answer quality.",
        ("rows",),
    ),
    "read_throughs": ModuleSpec(
        "read_throughs",
        "Cross-company and industry read-through table covering names, relationships, what was said, implications, and confidence.",
        ("rows",),
    ),
    "market_events": ModuleSpec(
        "market_events",
        "Source-backed major news, market events, regulatory items, macro shifts, and upcoming catalysts with investor impact.",
        ("events",),
    ),
    "bar_chart": ModuleSpec(
        "bar_chart",
        "Compact native bar chart for segment growth, revenue mix, guidance deltas, exposure, or other small comparable metric sets.",
        ("items",),
    ),
    "financial_trend_chart": ModuleSpec(
        "financial_trend_chart",
        "Quarterly grouped bars for revenue, gross profit, and net income with a selected profitability-margin line overlay.",
        ("periods",),
    ),
    "eps_actual_vs_estimate_chart": ModuleSpec(
        "eps_actual_vs_estimate_chart",
        "Grouped EPS chart comparing estimated EPS and actual EPS across recent quarters.",
        ("periods",),
    ),
    "equity_price_event_chart": ModuleSpec(
        "equity_price_event_chart",
        "Equity price line chart with sourced market-event annotations, gated to robust daily/hourly/minute price tapes.",
        ("prices", "events"),
    ),
    "timeline": ModuleSpec(
        "timeline",
        "Catalyst, event, filing, regulatory, or monitoring timeline.",
        ("events",),
    ),
    "text_block": ModuleSpec(
        "text_block",
        "Narrative block with optional bullets for compact explanation.",
    ),
    "source_list": ModuleSpec(
        "source_list",
        "Source ledger with URL, timestamp, confidence, and notes.",
        ("sources",),
    ),
    "missing_evidence": ModuleSpec(
        "missing_evidence",
        "Visible refresh gaps, unavailable data, stale inputs, and terminal-only fields.",
        ("items",),
    ),
}


def supported_module_names() -> list[str]:
    return sorted(MODULES)
