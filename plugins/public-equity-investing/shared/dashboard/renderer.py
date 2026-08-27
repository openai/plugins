"""Render standalone Public Equity Investing HTML dashboards from typed payloads."""

from __future__ import annotations

import html
import json
import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .qa import equity_price_event_readiness, validate_payload

PACKAGE_DIR = Path(__file__).resolve().parent
ASSET_DIR = PACKAGE_DIR / "assets"
TEMPLATE_PATH = PACKAGE_DIR / "templates" / "base.html"


def render_dashboard(
    payload: Mapping[str, Any],
    *,
    validate: bool = True,
    validation_profile: str = "production",
) -> str:
    if validate:
        report = validate_payload(payload, profile=validation_profile)
        if report["hard_failures"]:
            raise ValueError(
                "Dashboard payload failed validation: " + "; ".join(report["hard_failures"])
            )

    css = (ASSET_DIR / "dashboard.css").read_text(encoding="utf-8")
    source_records = _source_records(payload)
    source_index = {str(source["id"]): source for source in source_records}
    js = (
        (ASSET_DIR / "dashboard.js")
        .read_text(encoding="utf-8")
        .replace(
            "__SOURCE_DATA__",
            _safe_json(_source_tooltip_payload(source_index)),
        )
    )
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    title = str(payload.get("title", "Public Equity Investing Dashboard"))
    body = _render_body(payload, source_index)
    return (
        template.replace("{{title}}", _escape(title))
        .replace("{{styles}}", css)
        .replace("{{body}}", body)
        .replace("{{script}}", js)
    )


def _render_body(payload: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]) -> str:
    issuer = payload.get("issuer") if isinstance(payload.get("issuer"), Mapping) else {}
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), Mapping) else {}
    hero = payload.get("hero") if isinstance(payload.get("hero"), Mapping) else {}
    ticker = str(issuer.get("ticker") or issuer.get("name") or "PM")
    issuer_name = str(issuer.get("name") or ticker)
    mode = str(payload.get("mode") or "public-equity-investing")
    freeze_time = str(
        metadata.get("freeze_time") or metadata.get("as_of") or "source freeze not provided"
    )
    accent = _safe_color(
        str(issuer.get("accent_color") or payload.get("accent_color") or "#245f5a")
    )
    ticker_badge = _ticker_badge_color(issuer, payload, accent)
    layout = str(payload.get("layout") or "tabs").lower()

    tabs = list(payload.get("tabs", []))
    if source_index and not any(
        tab.get("id") == "sources" for tab in tabs if isinstance(tab, Mapping)
    ):
        tabs.append(
            {
                "id": "sources",
                "label": "Sources",
                "modules": [
                    {
                        "type": "source_list",
                        "title": "Sources and Refresh Gaps",
                        "eyebrow": "Evidence log",
                        "data": {"sources": list(source_index.values())},
                    }
                ],
            }
        )

    if layout == "single_page":
        section_shell = f"""
      <section class="section-shell">
        {_render_toc(tabs)}
        {_render_single_page_sections(tabs, source_index)}
      </section>
        """
    else:
        section_shell = f"""
      <section class="tab-shell">
        {_render_tab_list(tabs)}
        {_render_tab_panels(tabs, source_index)}
      </section>
        """

    utility_bar = _render_utility_bar()
    callout = hero.get("callout") or metadata.get("decision_context")
    callout_html = ""
    hero_class = "hero"
    if callout:
        callout_html = f"""
        <div class="hero-callout">
          <span class="label">{_escape(str(hero.get("callout_label") or "Core Debate"))}</span>
          <strong>{_render_inline_text(callout, source_index, hero.get("citations"), append_non_numeric_citations=True, link_numeric_citations=True)}</strong>
        </div>"""
    else:
        hero_class += " no-callout"

    return f"""
    <header class="top-band" style="--issuer-accent: {accent}; --ticker-badge-bg: {ticker_badge}">
      <nav class="utility">
        <div class="utility-meta">
          <span>{_escape(mode.replace("_", " ").title())}</span>
          <span>{_escape(issuer_name)}</span>
          <span>{_escape(freeze_time)}</span>
        </div>
      </nav>
      <section class="{hero_class}">
        <div class="identity-lockup" aria-label="Issuer identity tile">
          <span>{_escape(_identity_text(ticker))}</span>
        </div>
        <div class="hero-copy">
          <p class="eyebrow">{_escape(str(hero.get("eyebrow") or "Public Equity Investing Dashboard"))}</p>
          <h1>{_escape(str(hero.get("headline") or payload.get("title") or issuer_name))}</h1>
          <p>{_render_inline_text(hero.get("dek") or payload.get("subtitle") or "Decision-grade public-equity-investing dashboard.", source_index, hero.get("citations"), append_non_numeric_citations=True, link_numeric_citations=True)}</p>
        </div>
        {callout_html}
      </section>
    </header>
    {utility_bar}
    <main data-report-copy-root>
      {_render_metric_tiles(payload.get("snapshot", []), source_index, class_name="snapshot-grid")}
      {section_shell}
    </main>
    """


def _render_utility_bar() -> str:
    return (
        '<div class="dashboard-utility-bar" aria-label="Dashboard actions">'
        '<div><span class="utility-kicker">Reader actions</span></div>'
        '<div class="utility-actions">'
        '<button class="utility-action" type="button" data-copy-full-report>Copy Full Report</button>'
        '<button class="utility-action" type="button" data-print-dashboard>Print / Save PDF</button>'
        "</div>"
        "</div>"
    )


def _render_tab_list(tabs: Sequence[Any]) -> str:
    buttons: list[str] = []
    for index, tab in enumerate(tabs):
        if not isinstance(tab, Mapping):
            continue
        tab_id = str(tab.get("id") or f"tab-{index + 1}")
        active = " is-active" if index == 0 else ""
        selected = "true" if index == 0 else "false"
        buttons.append(
            f'<button class="tab-button{active}" data-tab="{_escape_attr(tab_id)}" '
            f'role="tab" aria-selected="{selected}">{_escape(str(tab.get("label") or tab_id.title()))}</button>'
        )
    return f'<div class="tab-list" role="tablist" aria-label="Dashboard sections">{"".join(buttons)}</div>'


def _render_tab_panels(tabs: Sequence[Any], source_index: Mapping[str, Mapping[str, Any]]) -> str:
    panels: list[str] = []
    for index, tab in enumerate(tabs):
        if not isinstance(tab, Mapping):
            continue
        tab_id = str(tab.get("id") or f"tab-{index + 1}")
        label = str(tab.get("label") or tab_id.title())
        active = " is-active" if index == 0 else ""
        modules = tab.get("modules", [])
        panels.append(
            f'<section id="{_escape_attr(tab_id)}" class="tab-panel{active}" role="tabpanel">'
            f'<div class="print-tab-heading"><span>{index + 1:02d}</span><h2>{_escape(label)}</h2></div>'
            + "".join(
                _render_module(module, source_index)
                for module in modules
                if isinstance(module, Mapping)
            )
            + "</section>"
        )
    return "".join(panels)


def _render_toc(tabs: Sequence[Any]) -> str:
    links: list[str] = []
    for index, tab in enumerate(tabs):
        if not isinstance(tab, Mapping):
            continue
        tab_id = str(tab.get("id") or f"section-{index + 1}")
        active = " is-active" if index == 0 else ""
        links.append(
            f'<a class="toc-link{active}" href="#{_escape_attr(tab_id)}">'
            f"<span>{index + 1:02d}</span>{_escape(str(tab.get('label') or tab_id.title()))}</a>"
        )
    return f'<nav class="toc-list" aria-label="Dashboard contents">{"".join(links)}</nav>'


def _render_single_page_sections(
    tabs: Sequence[Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    sections: list[str] = []
    for index, tab in enumerate(tabs):
        if not isinstance(tab, Mapping):
            continue
        tab_id = str(tab.get("id") or f"section-{index + 1}")
        label = str(tab.get("label") or tab_id.title())
        modules = tab.get("modules", [])
        sections.append(
            f'<section id="{_escape_attr(tab_id)}" class="dashboard-section" tabindex="-1">'
            f'<div class="section-anchor-heading"><span>{index + 1:02d}</span><h2>{_escape(label)}</h2></div>'
            + "".join(
                _render_module(module, source_index, parent_heading=label)
                for module in modules
                if isinstance(module, Mapping)
            )
            + "</section>"
        )
    return '<div class="section-stack">' + "".join(sections) + "</div>"


def _render_module(
    module: Mapping[str, Any],
    source_index: Mapping[str, Mapping[str, Any]],
    *,
    parent_heading: str | None = None,
) -> str:
    module_type = str(module.get("type") or "")
    data = module.get("data") if isinstance(module.get("data"), Mapping) else {}
    heading = _render_heading(module, parent_heading=parent_heading)

    if module_type == "decision_box":
        return heading + _render_decision_box(data, source_index)
    if module_type in {"metric_tiles", "highlight_tiles"}:
        return heading + _render_metric_tiles(data.get("items", []), source_index)
    if module_type == "executive_summary":
        return heading + _render_executive_summary(data, source_index)
    if module_type == "key_metrics":
        return heading + _render_key_metrics(data, source_index)
    if module_type == "growth_trajectory":
        return heading + _render_growth_trajectory(data, source_index)
    if module_type == "transcript_qa":
        return heading + _render_transcript_qa(data, source_index)
    if module_type == "read_throughs":
        return heading + _render_read_throughs(data, source_index)
    if module_type == "market_events":
        return heading + _render_market_events(data, source_index)
    if module_type == "bar_chart":
        return heading + _render_bar_chart(data, source_index)
    if module_type == "financial_trend_chart":
        return heading + _render_financial_trend_chart(data, source_index)
    if module_type == "eps_actual_vs_estimate_chart":
        return heading + _render_eps_actual_vs_estimate_chart(data, source_index)
    if module_type == "equity_price_event_chart":
        body = _render_equity_price_event_chart(data, source_index)
        return heading + body if body else ""
    if module_type == "cards":
        return heading + _render_cards(data.get("items", []), source_index)
    if module_type == "table":
        return heading + _render_table(data, source_index)
    if module_type == "scenario_map":
        return heading + _render_scenarios(data.get("cases", []), source_index)
    if module_type == "question_list":
        return heading + _render_questions(data.get("questions", []), source_index)
    if module_type == "timeline":
        return heading + _render_timeline(data.get("events", []), source_index)
    if module_type == "text_block":
        return heading + _render_text_block(data, source_index)
    if module_type == "source_list":
        return heading + _render_sources(data.get("sources", []), source_index)
    if module_type == "missing_evidence":
        return heading + _render_missing(data.get("items", []), source_index)

    return f'<div class="notice">Unsupported module: {_escape(module_type)}</div>'


def _render_heading(module: Mapping[str, Any], *, parent_heading: str | None = None) -> str:
    title = module.get("title")
    eyebrow = module.get("eyebrow")
    if not title and not eyebrow:
        return ""
    if title and parent_heading and not eyebrow:
        normalized_title = re.sub(r"[\s_-]+", " ", str(title).strip().lower())
        normalized_parent = re.sub(r"[\s_-]+", " ", parent_heading.strip().lower())
        if normalized_title == normalized_parent:
            return ""
    eyebrow_html = f'<p class="eyebrow">{_escape(str(eyebrow))}</p>' if eyebrow else ""
    title_html = f"<h2>{_escape(str(title))}</h2>" if title else ""
    return f'<div class="section-heading">{eyebrow_html}{title_html}</div>'


def _render_decision_box(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    bullets = data.get("key_points") or data.get("bullets") or []
    fallback_citations = _citations_for(data)
    bullets_html = "".join(
        f"<li>{_format_cell(item, source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</li>"
        for item in bullets
    )
    meta = []
    for label in ("thesis_change", "estimate_revision", "stock_skew", "next_catalyst"):
        if data.get(label):
            meta.append(
                f"<span><strong>{_escape(label.replace('_', ' ').title())}</strong>"
                f"{_format_cell(data[label], source_index, data.get(f'{label}_citations') or fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</span>"
            )
    citation_note = _citation_note(fallback_citations, source_index)
    return f"""
    <article class="decision-box">
      <span class="label">{_escape(str(data.get("label") or "PM Bottom Line"))}</span>
      <h3>{_render_inline_text(data.get("stance") or "Decision view not provided", source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</h3>
      <p>{_format_cell(data.get("summary") or "", source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>
      <div class="decision-meta">{"".join(meta)}</div>
      <ul class="check-list">{bullets_html}</ul>
      {citation_note}
    </article>
    """


def _render_metric_tiles(
    items: Any,
    source_index: Mapping[str, Mapping[str, Any]],
    class_name: str = "metric-grid",
) -> str:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)) or not items:
        return ""
    tiles = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        status = _status_class(str(item.get("status") or ""))
        item_citations = _citations_for(item)
        tiles.append(
            f'<article class="metric-tile {status}">'
            f'<span class="tile-label">{_escape(str(item.get("label") or ""))}</span>'
            f"<strong>{_format_cell(item.get('value') or '', source_index, item_citations, append_non_numeric_citations=False)}</strong>"
            f"<small>{_format_cell(item.get('detail') or '', source_index, item_citations, append_non_numeric_citations=False)}</small>"
            "</article>"
        )
    return f'<section class="{class_name}">{"".join(tiles)}</section>'


def _render_executive_summary(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    headline = data.get("headline")
    body = data.get("body") or data.get("summary") or data.get("text") or ""
    bullets = data.get("bullets") or data.get("watch_items") or []
    net_read = data.get("net_read")
    fallback_citations = _citations_for(data)
    body_html = (
        _format_rich_text(
            str(body),
            source_index,
            fallback_citations,
            append_non_numeric_citations=False,
            link_numeric_citations=False,
        )
        if body
        else ""
    )
    bullets_html = "".join(
        f"<li>{_format_cell(item, source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</li>"
        for item in bullets
    )
    citation_note = _citation_note(fallback_citations, source_index)
    return (
        '<article class="executive-summary">'
        + (
            f"<h3>{_render_inline_text(headline, source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</h3>"
            if headline
            else ""
        )
        + body_html
        + (f'<ul class="check-list">{bullets_html}</ul>' if bullets_html else "")
        + (
            f'<p class="net-read"><strong>Net read:</strong> {_format_cell(net_read, source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>'
            if net_read
            else ""
        )
        + citation_note
        + "</article>"
    )


def _render_key_metrics(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    table_data = dict(data)
    if "columns" not in table_data:
        table_data["columns"] = [
            {"key": "metric", "label": "Metric"},
            {"key": "current", "label": "Current"},
            {"key": "growth", "label": "Growth"},
            {"key": "compare", "label": "Consensus / Guide"},
            {"key": "trajectory", "label": "Trajectory"},
            {"key": "read", "label": "PM Read"},
        ]
    table_data.setdefault("rows", data.get("items", []))
    table_data.setdefault("density", "dense")
    return _render_table(table_data, source_index)


def _render_growth_trajectory(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    table_data = dict(data)
    if "columns" not in table_data:
        table_data["columns"] = [
            {"key": "metric", "label": "Metric"},
            {"key": "prior", "label": "Prior"},
            {"key": "current", "label": "Current"},
            {"key": "trajectory", "label": "Trajectory"},
            {"key": "read", "label": "PM Read"},
        ]
    table_data.setdefault("rows", data.get("items", []))
    table_data.setdefault("density", "dense")
    return _render_table(table_data, source_index)


def _render_transcript_qa(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    table_data = dict(data)
    if "columns" not in table_data:
        table_data["columns"] = [
            {"key": "number", "label": "#"},
            {"key": "analyst", "label": "Analyst (Firm)"},
            {"key": "topic", "label": "Topic"},
            {"key": "response", "label": "Mgmt Response"},
            {"key": "quote", "label": "Direct Quote"},
            {"key": "quality", "label": "Quality"},
        ]
    table_data.setdefault("rows", data.get("questions", []))
    table_data.setdefault("density", "dense")
    return _render_table(table_data, source_index)


def _render_read_throughs(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    table_data = dict(data)
    if "columns" not in table_data:
        table_data["columns"] = [
            {"key": "name", "label": "Name"},
            {"key": "relationship", "label": "Relationship"},
            {"key": "parent_said", "label": "Parent Said"},
            {"key": "read_through", "label": "Read-Through"},
            {"key": "implication", "label": "Implication"},
            {"key": "confidence", "label": "Confidence"},
        ]
    table_data.setdefault("rows", data.get("items", []))
    table_data.setdefault("density", "dense")
    return _render_table(table_data, source_index)


def _render_market_events(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    events = data.get("events") or data.get("rows") or []
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        return ""

    rows: list[str] = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        event_citations = _citations_for(event) or _source_ref_from_fields(event)
        cited_source = _first_cited_source(event_citations, source_index)
        source_title = str(
            event.get("source_title") or event.get("source") or cited_source.get("title") or ""
        )
        source_url = str(
            event.get("source_url") or event.get("url") or cited_source.get("url") or ""
        )
        source_as_of = str(
            event.get("as_of")
            or event.get("source_as_of")
            or event.get("published")
            or cited_source.get("as_of")
            or cited_source.get("date")
            or cited_source.get("published")
            or ""
        )
        source_html = (
            f'<a href="{_escape_attr(source_url)}" target="_blank" rel="noreferrer">{_escape(source_title or "Source")}</a>'
            if source_url
            else _escape(source_title or "Not sourced")
        )
        if source_as_of:
            source_html += f"<small>{_escape(source_as_of)}</small>"
        rows.append(
            "<tr>"
            f'<td data-label="Date / Window">{_format_cell(event.get("date") or event.get("window") or "", source_index, event_citations, append_non_numeric_citations=False)}</td>'
            f'<td data-label="Event">{_format_cell(event.get("event") or event.get("title") or "", source_index, event_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</td>'
            f'<td data-label="Type">{_escape(str(event.get("type") or event.get("category") or event.get("timing") or ""))}</td>'
            f'<td data-label="Potential Impact">{_format_cell(event.get("impact") or event.get("potential_impact") or "", source_index, event_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</td>'
            f'<td data-label="Investor Read">{_format_cell(event.get("investor_read") or event.get("pm_read") or event.get("read") or "", source_index, event_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</td>'
            f'<td data-label="Source">{source_html}</td>'
            "</tr>"
        )

    return f"""
    <div class="table-wrap dense-table market-events-table" data-table-label="{_escape_attr(str(data.get("mobile_label") or "Market events and news coverage"))}">
      <table>
        <thead><tr><th>Date / Window</th><th>Event</th><th>Type</th><th>Potential Impact</th><th>Investor Read</th><th>Source</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>
    """


def _render_bar_chart(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    items = data.get("items") or data.get("rows") or []
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return ""

    rows = [item for item in items if isinstance(item, Mapping)]
    values = [_to_float(row.get("bar_value", row.get("value"))) for row in rows]
    max_value = max([abs(value) for value in values if value is not None] or [1.0])

    rendered: list[str] = []
    for row, value in zip(rows, values, strict=False):
        row_citations = _citations_for(row)
        width = 0.0 if value is None else min(abs(value) / max_value * 100, 100)
        label = str(row.get("label") or row.get("metric") or "")
        detail = row.get("detail") or row.get("subtitle") or ""
        display_value = row.get("display") or row.get("value") or ""
        rendered.append(
            '<div class="bar-row">'
            f'<div class="bar-label"><strong>{_escape(label)}</strong>'
            + (
                f"<span>{_format_cell(detail, source_index, row_citations)}</span>"
                if detail
                else ""
            )
            + "</div>"
            f'<div class="bar-track" aria-label="{_escape_attr(label)}">'
            f'<span class="bar-fill" style="--bar-width: {width:.1f}%"></span>'
            "</div>"
            f'<div class="bar-value">{_format_cell(display_value, source_index, row_citations)}</div>'
            "</div>"
        )
    return f'<div class="bar-chart">{"".join(rendered)}</div>'


def _render_financial_trend_chart(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    periods = data.get("periods") or data.get("rows") or []
    rows = [row for row in periods if isinstance(row, Mapping)]
    margin_key = _selected_margin_metric(data, rows)
    margin_label = str(
        data.get("margin_label") or data.get("line_label") or _metric_label(margin_key)
    )
    complete_rows = [
        row
        for row in rows
        if row.get("period")
        and _to_float(row.get("revenue")) is not None
        and _to_float(row.get("gross_profit")) is not None
        and _to_float(row.get("net_income")) is not None
        and _to_ratio(row.get(margin_key)) is not None
    ]
    if len(complete_rows) < 2:
        return ""

    series = [
        ("revenue", "Revenue", "#2563eb"),
        ("gross_profit", "Gross Profit", "#14b8a6"),
        ("net_income", "Net Income", "#7c3aed"),
    ]
    bar_values = [_to_float(row.get(key)) for row in complete_rows for key, _, _ in series]
    margins = [_to_ratio(row.get(margin_key)) for row in complete_rows]
    svg = _render_grouped_bar_line_svg(
        complete_rows,
        series,
        line_key=margin_key,
        line_label=margin_label,
        line_color="#111827",
        value_min_max=_min_max_with_zero([value for value in bar_values if value is not None]),
        line_min_max=_margin_min_max_with_zero([value for value in margins if value is not None]),
        value_formatter=_format_number,
        line_formatter=lambda value: f"{value * 100:.1f}%",
    )
    table_rows = [
        {
            "period": row.get("period"),
            "revenue": _format_number(_to_float(row.get("revenue"))),
            "gross_profit": _format_number(_to_float(row.get("gross_profit"))),
            "net_income": _format_number(_to_float(row.get("net_income"))),
            margin_key: _format_ratio(_to_ratio(row.get(margin_key))),
            "source": row.get("source") or row.get("source_title") or row.get("as_of") or "",
            "citations": _citations_for(row) or _source_ref_from_fields(row),
        }
        for row in complete_rows
    ]
    margin_note = data.get("margin_rationale") or data.get("margin_note") or data.get("line_note")
    return (
        '<div class="combo-chart">'
        + svg
        + _render_chart_legend(
            [(label, color) for _, label, color in series] + [(margin_label, "#111827")]
        )
        + _render_chart_note(margin_note, source_index, _citations_for(data))
        + _render_table(
            {
                "columns": [
                    {"key": "period", "label": "Period"},
                    {"key": "revenue", "label": "Revenue"},
                    {"key": "gross_profit", "label": "Gross Profit"},
                    {"key": "net_income", "label": "Net Income"},
                    {"key": margin_key, "label": margin_label},
                    {"key": "source", "label": "Source"},
                ],
                "rows": table_rows,
                "density": "dense",
                "mobile_label": str(
                    data.get("mobile_label") or "Quarterly financial trend source table"
                ),
            },
            source_index,
        )
        + "</div>"
    )


def _render_eps_actual_vs_estimate_chart(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    periods = data.get("periods") or data.get("rows") or []
    rows = [row for row in periods if isinstance(row, Mapping)]
    complete_rows = [
        row
        for row in rows
        if row.get("period")
        and _to_float(row.get("estimated_eps")) is not None
        and _to_float(row.get("actual_eps")) is not None
    ]
    if len(complete_rows) < 2:
        return ""

    series = [
        ("estimated_eps", "Estimated EPS", "#94a3b8"),
        ("actual_eps", "Actual EPS", "#245f5a"),
    ]
    values = [_to_float(row.get(key)) for row in complete_rows for key, _, _ in series]
    svg = _render_grouped_bar_svg(
        complete_rows,
        series,
        value_min_max=_min_max_with_zero([value for value in values if value is not None]),
        value_formatter=lambda value: f"${value:.2f}",
    )
    table_rows = []
    for row in complete_rows:
        estimate = _to_float(row.get("estimated_eps"))
        actual = _to_float(row.get("actual_eps"))
        surprise = row.get("surprise")
        if surprise is None and estimate is not None and actual is not None:
            surprise = actual - estimate
        table_rows.append(
            {
                "period": row.get("period"),
                "estimated_eps": _format_eps(estimate),
                "actual_eps": _format_eps(actual),
                "surprise": _format_eps(_to_float(surprise)),
                "basis": row.get("basis") or "",
                "source": row.get("source") or row.get("source_title") or row.get("as_of") or "",
                "citations": _citations_for(row) or _source_ref_from_fields(row),
            }
        )
    return (
        '<div class="combo-chart">'
        + svg
        + _render_chart_legend([(label, color) for _, label, color in series])
        + _render_table(
            {
                "columns": ["period", "estimated_eps", "actual_eps", "surprise", "basis", "source"],
                "rows": table_rows,
                "density": "dense",
                "mobile_label": str(
                    data.get("mobile_label") or "EPS estimate versus actual source table"
                ),
            },
            source_index,
        )
        + "</div>"
    )


def _render_equity_price_event_chart(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    prices = data.get("prices") or []
    events = data.get("events") or []
    _ = prices, events
    readiness = equity_price_event_readiness(data)
    if not readiness["ready"]:
        return ""
    price_rows = readiness["price_rows"]
    event_rows = readiness["event_rows"]

    svg = _render_price_event_svg(price_rows, event_rows)
    event_table = _render_market_events(
        {
            "events": event_rows,
            "mobile_label": data.get("mobile_label") or "Annotated equity events",
        },
        source_index,
    )
    return '<div class="combo-chart price-event-chart">' + svg + event_table + "</div>"


def _render_grouped_bar_line_svg(
    rows: Sequence[Mapping[str, Any]],
    series: Sequence[tuple[str, str, str]],
    *,
    line_key: str,
    line_label: str,
    line_color: str,
    value_min_max: tuple[float, float],
    line_min_max: tuple[float, float],
    value_formatter: Any,
    line_formatter: Any,
) -> str:
    bars_svg, geometry = _grouped_bar_parts(rows, series, value_min_max)
    line_points = []
    for index, row in enumerate(rows):
        value = _to_ratio(row.get(line_key))
        if value is None:
            continue
        x = geometry["left"] + geometry["group_width"] * index + geometry["group_width"] / 2
        y = _scale_y(
            value, line_min_max[0], line_min_max[1], geometry["top"], geometry["plot_height"]
        )
        line_points.append((x, y, value))
    path = ""
    if line_points:
        path = " ".join(
            ("M" if idx == 0 else "L") + f"{x:.1f},{y:.1f}"
            for idx, (x, y, _) in enumerate(line_points)
        )
    markers = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5"><title>{_escape(line_label)}: {_escape(line_formatter(value))}</title></circle>'
        for x, y, value in line_points
    )
    right_axis = _render_right_axis_ticks(
        geometry, line_min_max[0], line_min_max[1], line_formatter
    )
    return (
        _svg_open(geometry)
        + bars_svg
        + f'<path class="combo-line" style="--line-color: {line_color}" d="{path}"></path>'
        + f'<g class="combo-markers" style="--line-color: {line_color}">{markers}</g>'
        + right_axis
        + _svg_close()
    )


def _render_grouped_bar_svg(
    rows: Sequence[Mapping[str, Any]],
    series: Sequence[tuple[str, str, str]],
    *,
    value_min_max: tuple[float, float],
    value_formatter: Any,
) -> str:
    bars_svg, geometry = _grouped_bar_parts(
        rows, series, value_min_max, value_formatter=value_formatter
    )
    return _svg_open(geometry) + bars_svg + _svg_close()


def _grouped_bar_parts(
    rows: Sequence[Mapping[str, Any]],
    series: Sequence[tuple[str, str, str]],
    value_min_max: tuple[float, float],
    *,
    value_formatter: Any = None,
) -> tuple[str, dict[str, float]]:
    if value_formatter is None:
        value_formatter = _format_number
    width = 760.0
    height = 320.0
    left = 54.0
    right = 54.0
    top = 22.0
    bottom = 58.0
    plot_width = width - left - right
    plot_height = height - top - bottom
    group_width = plot_width / max(len(rows), 1)
    bar_width = min(16.0, group_width / (len(series) + 1.5))
    min_value, max_value = value_min_max
    zero_y = _scale_y(0.0, min_value, max_value, top, plot_height)
    parts = [
        _render_left_axis_ticks(
            width, right, top, plot_height, left, min_value, max_value, value_formatter
        )
    ]
    for row_index, row in enumerate(rows):
        center = left + group_width * row_index + group_width / 2
        label = str(row.get("period") or row.get("label") or "")
        parts.append(
            f'<text class="chart-x-label" x="{center:.1f}" y="{height - 20}" text-anchor="middle">{_escape(label)}</text>'
        )
        start_x = center - (len(series) * bar_width + (len(series) - 1) * 4) / 2
        for series_index, (key, series_label, color) in enumerate(series):
            value = _to_float(row.get(key))
            if value is None:
                continue
            y = _scale_y(value, min_value, max_value, top, plot_height)
            rect_y = min(y, zero_y)
            rect_height = max(abs(zero_y - y), 1.0)
            x = start_x + series_index * (bar_width + 4)
            parts.append(
                f'<rect class="combo-bar" x="{x:.1f}" y="{rect_y:.1f}" width="{bar_width:.1f}" height="{rect_height:.1f}" fill="{color}">'
                f"<title>{_escape(series_label)} {label}: {_escape(value_formatter(value))}</title>"
                "</rect>"
            )
    return "".join(parts), {
        "width": width,
        "height": height,
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom,
        "plot_width": plot_width,
        "plot_height": plot_height,
        "group_width": group_width,
    }


def _render_price_event_svg(
    price_rows: Sequence[Mapping[str, Any]], event_rows: Sequence[Mapping[str, Any]]
) -> str:
    width = 760.0
    height = 320.0
    left = 54.0
    right = 34.0
    top = 24.0
    bottom = 58.0
    plot_width = width - left - right
    plot_height = height - top - bottom
    values = [_to_float(row.get("price")) for row in price_rows]
    min_value, max_value = _min_max_with_padding([value for value in values if value is not None])
    x_step = plot_width / max(len(price_rows) - 1, 1)
    points = []
    date_to_index = {str(row.get("date")): index for index, row in enumerate(price_rows)}
    for index, row in enumerate(price_rows):
        value = _to_float(row.get("price"))
        if value is None:
            continue
        x = left + x_step * index
        y = _scale_y(value, min_value, max_value, top, plot_height)
        points.append((x, y, value, str(row.get("date"))))
    path = " ".join(
        ("M" if idx == 0 else "L") + f"{x:.1f},{y:.1f}" for idx, (x, y, _, _) in enumerate(points)
    )
    marker_parts = []
    for event_index, event in enumerate(event_rows, start=1):
        raw_date = str(event.get("date") or event.get("window") or "")
        index = date_to_index.get(raw_date)
        if index is None:
            index = min(
                round((event_index - 1) / max(len(event_rows) - 1, 1) * (len(price_rows) - 1)),
                len(price_rows) - 1,
            )
        x, y, _, _ = points[index]
        marker_parts.append(
            f'<g class="event-marker" transform="translate({x:.1f} {y:.1f})">'
            '<circle r="7"></circle>'
            f'<text y="-11" text-anchor="middle">{event_index}</text>'
            f"<title>{_escape(str(event.get('event') or event.get('title') or raw_date))}</title>"
            "</g>"
        )
    x_labels = ""
    if points:
        x_labels = (
            f'<text class="chart-x-label" x="{points[0][0]:.1f}" y="{height - 20}" text-anchor="middle">{_escape(points[0][3])}</text>'
            f'<text class="chart-x-label" x="{points[-1][0]:.1f}" y="{height - 20}" text-anchor="middle">{_escape(points[-1][3])}</text>'
        )
    geometry = {
        "width": width,
        "height": height,
        "left": left,
        "top": top,
        "plot_height": plot_height,
    }
    return (
        _svg_open(geometry)
        + f'<line class="chart-grid" x1="{left}" x2="{width - right}" y1="{top + plot_height:.1f}" y2="{top + plot_height:.1f}"></line>'
        + f'<text class="chart-axis-label" x="{left}" y="{top + 4}">{_escape(_format_price(max_value))}</text>'
        + f'<text class="chart-axis-label" x="{left}" y="{top + plot_height}">{_escape(_format_price(min_value))}</text>'
        + f'<path class="price-line" d="{path}"></path>'
        + "".join(marker_parts)
        + x_labels
        + _svg_close()
    )


def _render_left_axis_ticks(
    width: float,
    right: float,
    top: float,
    plot_height: float,
    left: float,
    min_value: float,
    max_value: float,
    formatter: Any,
) -> str:
    parts: list[str] = []
    for tick in _axis_ticks(min_value, max_value):
        y = _scale_y(tick, min_value, max_value, top, plot_height)
        grid_class = "chart-grid chart-zero-line" if abs(tick) < 1e-9 else "chart-grid"
        parts.append(
            f'<line class="{grid_class}" x1="{left}" x2="{width - right}" y1="{y:.1f}" y2="{y:.1f}"></line>'
        )
        parts.append(
            f'<text class="chart-axis-label" x="{left - 6}" y="{y + 4:.1f}" text-anchor="end">{_escape(formatter(tick))}</text>'
        )
    return "".join(parts)


def _render_right_axis_ticks(
    geometry: Mapping[str, float],
    min_value: float,
    max_value: float,
    formatter: Any,
) -> str:
    parts: list[str] = []
    width = geometry["width"]
    top = geometry["top"]
    plot_height = geometry["plot_height"]
    for tick in _axis_ticks(min_value, max_value):
        y = _scale_y(tick, min_value, max_value, top, plot_height)
        parts.append(
            f'<text class="chart-axis-label right-axis-label" x="{width - 4}" y="{y + 4:.1f}" text-anchor="end">{_escape(formatter(tick))}</text>'
        )
    return "".join(parts)


def _axis_ticks(min_value: float, max_value: float, target_count: int = 7) -> list[float]:
    if max_value == min_value:
        return [min_value]
    step = _nice_step((max_value - min_value) / max(target_count - 1, 1))
    start = math.ceil((min_value - 1e-9) / step) * step
    end = math.floor((max_value + 1e-9) / step) * step
    ticks: list[float] = []
    current = start
    guard = 0
    while current <= end + step * 0.001 and guard < 20:
        ticks.append(0.0 if abs(current) < step * 0.001 else current)
        current += step
        guard += 1
    if not ticks:
        ticks = [min_value, max_value]
    return ticks


def _svg_open(geometry: Mapping[str, float]) -> str:
    return (
        f'<svg class="native-chart" viewBox="0 0 {geometry["width"]:.0f} {geometry["height"]:.0f}" role="img" '
        'aria-label="Dashboard chart" preserveAspectRatio="xMidYMid meet">'
    )


def _svg_close() -> str:
    return "</svg>"


def _render_chart_legend(items: Sequence[tuple[str, str]]) -> str:
    return (
        '<div class="chart-legend">'
        + "".join(
            f'<span><i style="--legend-color: {color}"></i>{_escape(label)}</span>'
            for label, color in items
        )
        + "</div>"
    )


def _render_chart_note(
    note: Any, source_index: Mapping[str, Mapping[str, Any]], citations: Any = None
) -> str:
    if not note:
        return ""
    return (
        '<p class="chart-note">'
        + _format_cell(
            note,
            source_index,
            citations,
            append_non_numeric_citations=False,
            link_numeric_citations=False,
        )
        + "</p>"
    )


def _render_cards(items: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    cards = []
    for item in (
        items if isinstance(items, Sequence) and not isinstance(items, (str, bytes)) else []
    ):
        if not isinstance(item, Mapping):
            continue
        bullets = item.get("bullets") or []
        item_citations = _citations_for(item)
        bullets_html = "".join(
            f"<li>{_format_cell(bullet, source_index, item_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</li>"
            for bullet in bullets
        )
        label = item.get("eyebrow") or item.get("label")
        citation_note = _citation_note(item_citations, source_index, label="Card sources")
        cards.append(
            f'<article class="card {_status_class(str(item.get("status") or ""))}">'
            + (f'<span class="label">{_escape(str(label))}</span>' if label else "")
            + f"<strong>{_render_inline_text(item.get('title') or '', source_index, item_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</strong>"
            + f"<p>{_format_cell(item.get('body') or item.get('text') or '', source_index, item_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>"
            + (f"<ul>{bullets_html}</ul>" if bullets_html else "")
            + citation_note
            + "</article>"
        )
    return f'<div class="card-grid">{"".join(cards)}</div>'


def _render_table(data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]) -> str:
    columns = data.get("columns") if isinstance(data.get("columns"), Sequence) else []
    rows = data.get("rows") if isinstance(data.get("rows"), Sequence) else []
    normalized_columns = [
        (*_normalize_column(column), _column_alignment_class(column)) for column in columns
    ]
    header = "".join(
        f'<th class="{class_name}">{_escape(label)}</th>'
        if class_name
        else f"<th>{_escape(label)}</th>"
        for _, label, class_name in normalized_columns
    )
    body_rows = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        cells = []
        row_citations = _citations_for(row) or _source_ref_from_fields(row)
        for key, label, class_name in normalized_columns:
            value = row.get(key, "")
            cell_citations = row_citations
            if key in _NO_FALLBACK_CITATION_COLUMNS and not (
                isinstance(value, Mapping) and _citations_for(value)
            ):
                cell_citations = []
            class_attr = f' class="{class_name}"' if class_name else ""
            cells.append(
                f'<td{class_attr} data-label="{_escape_attr(label)}">'
                f"{_format_cell(value, source_index, cell_citations, append_non_numeric_citations=False)}</td>"
            )
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    density = " dense-table" if str(data.get("density") or "").lower() == "dense" else ""
    return f"""
    <div class="table-wrap{density}" data-table-label="{_escape_attr(str(data.get("mobile_label") or "Dashboard table"))}">
      <table>
        <thead><tr>{header}</tr></thead>
        <tbody>{"".join(body_rows)}</tbody>
      </table>
    </div>
    """


def _render_scenarios(cases: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    cards = []
    for case in (
        cases if isinstance(cases, Sequence) and not isinstance(cases, (str, bytes)) else []
    ):
        if not isinstance(case, Mapping):
            continue
        kind = _slug(str(case.get("status") or case.get("type") or case.get("label") or "case"))
        case_citations = _citations_for(case)
        bullets = "".join(
            f"<li>{_format_cell(item, source_index, case_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</li>"
            for item in case.get("bullets", [])
        )
        citation_note = _citation_note(case_citations, source_index, label="Case sources")
        cards.append(
            f'<article class="scenario-card {kind}">'
            f'<span class="label">{_escape(str(case.get("type") or case.get("label") or "Case"))}</span>'
            f"<strong>{_render_inline_text(case.get('title') or '', source_index, case_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</strong>"
            f"<p>{_format_cell(case.get('headline') or case.get('body') or case.get('summary') or '', source_index, case_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>"
            f"<ul>{bullets}</ul>"
            f"{citation_note}"
            "</article>"
        )
    return f'<div class="scenario-grid">{"".join(cards)}</div>'


def _render_questions(questions: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    items = []
    for index, question in enumerate(
        questions
        if isinstance(questions, Sequence) and not isinstance(questions, (str, bytes))
        else []
    ):
        if not isinstance(question, Mapping):
            continue
        question_citations = _citations_for(question)
        citation_note = _citation_note(question_citations, source_index, label="Question sources")
        items.append(
            '<article class="question-item">'
            "<div>"
            f'<span class="label">Question {index + 1}</span>'
            f"<h3>{_render_inline_text(question.get('question') or question.get('q') or '', source_index, question_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</h3>"
            f'<p class="question-meta">{_format_cell(question.get("why") or question.get("why_it_matters") or "", source_index, question_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>'
            "</div><div>"
            "<strong>Listen-fors</strong>"
            f"<p>{_format_cell(question.get('listen_for') or question.get('listen_fors') or '', source_index, question_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>"
            f"{citation_note}</div></article>"
        )
    return f'<div class="question-list">{"".join(items)}</div>'


def _render_timeline(events: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    items = []
    for event in (
        events if isinstance(events, Sequence) and not isinstance(events, (str, bytes)) else []
    ):
        if not isinstance(event, Mapping):
            continue
        event_citations = _citations_for(event) or _source_ref_from_fields(event)
        items.append(
            '<article class="timeline-item">'
            f"<time>{_format_cell(event.get('date') or event.get('window') or '', source_index, event_citations)}</time>"
            f"<strong>{_render_inline_text(event.get('title') or event.get('event') or '', source_index, event_citations)}</strong>"
            f"<p>{_format_cell(event.get('detail') or event.get('read_through') or '', source_index, event_citations)}</p>"
            "</article>"
        )
    return f'<div class="timeline">{"".join(items)}</div>'


def _render_text_block(
    data: Mapping[str, Any], source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    fallback_citations = _citations_for(data)
    bullets = "".join(
        f"<li>{_format_cell(item, source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</li>"
        for item in data.get("bullets", [])
    )
    citation_note = _citation_note(fallback_citations, source_index)
    return (
        '<article class="text-block">'
        f"<p>{_format_cell(data.get('body') or data.get('text') or '', source_index, fallback_citations, append_non_numeric_citations=False, link_numeric_citations=False)}</p>"
        + (f'<ul class="check-list">{bullets}</ul>' if bullets else "")
        + citation_note
        + "</article>"
    )


def _render_sources(sources: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    items = []
    source_rows = _normalized_sources(sources)
    if not source_rows and source_index:
        source_rows = list(source_index.values())
    for source in source_rows:
        if not isinstance(source, Mapping):
            continue
        source_id = str(source.get("id") or source.get("source_id") or "")
        workbook_ref = _workbook_ref(source)
        title = _escape(
            str(
                source.get("title")
                or source.get("name")
                or source.get("url")
                or workbook_ref
                or "Source"
            )
        )
        url = str(source.get("url") or _workbook_href(source) or "")
        source_type = (
            source.get("type")
            or source.get("source_type")
            or ("model_cell" if _is_workbook_source(source) else "")
        )
        status = (
            source.get("status")
            or source.get("source_status")
            or source.get("reliance_status")
            or ""
        )
        timestamp = (
            source.get("as_of")
            or source.get("timestamp")
            or source.get("date")
            or source.get("accessed")
        )
        note = (
            _workbook_detail(source)
            or source.get("note")
            or source.get("description")
            or source.get("excerpt")
            or source.get("detail")
            or ""
        )
        link = (
            f'<a href="{_escape_attr(url)}" target="_blank" rel="noreferrer">{title}</a>'
            if url
            else f"<strong>{title}</strong>"
        )
        items.append(
            f'<li id="source-{_slug(source_id)}">'
            f'<span class="source-id">{_escape(source_id)}</span>{link}'
            + (f"<small>{_escape(str(source_type))}</small>" if source_type else "")
            + (f"<small>{_escape(str(status))}</small>" if status else "")
            + f"<span>{_escape(str(note))}</span>"
            + (f"<small>{_escape(str(timestamp))}</small>" if timestamp else "")
            + "</li>"
        )
    return f'<ol class="source-list">{"".join(items)}</ol>'


def _render_missing(items: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    rows = []
    for item in (
        items if isinstance(items, Sequence) and not isinstance(items, (str, bytes)) else []
    ):
        if isinstance(item, Mapping):
            item_citations = _citations_for(item)
            rows.append(
                f"<li><strong>{_escape(str(item.get('item') or item.get('field') or 'Missing evidence'))}</strong>"
                f": {_format_cell(item.get('needed') or item.get('detail') or '', source_index, item_citations)}</li>"
            )
        else:
            rows.append(f"<li>{_format_cell(item, source_index)}</li>")
    return '<div class="notice"><ul class="check-list">' + "".join(rows) + "</ul></div>"


def _normalize_column(column: Any) -> tuple[str, str]:
    if isinstance(column, Mapping):
        key = str(column.get("key") or column.get("field") or column.get("label") or "")
        label = str(column.get("label") or key.replace("_", " ").title())
        return key, label
    key = str(column)
    return key, key.replace("_", " ").title()


def _column_alignment_class(column: Any) -> str:
    key, label = _normalize_column(column)
    if isinstance(column, Mapping):
        explicit = str(column.get("align") or column.get("type") or "").strip().lower()
        if explicit in {"number", "numeric", "currency", "percent", "percentage", "right"}:
            return "is-numeric"
        if explicit in {"left", "text", "string"}:
            return ""
    numeric_hint = re.compile(
        r"(?:%|\b(?:amount|arr|bps|capex|cash|debt|ebitda|eps|growth|income|irr|"
        r"leverage|margin|moic|multiple|opex|price|profit|rate|return|revenue|"
        r"sales|shares?|value|valuation|variance)\b)",
        re.IGNORECASE,
    )
    return "is-numeric" if numeric_hint.search(f"{key} {label}") else ""


def _format_cell(
    value: Any,
    source_index: Mapping[str, Mapping[str, Any]],
    fallback_citations: Any = None,
    *,
    append_non_numeric_citations: bool = True,
    link_numeric_citations: bool = True,
) -> str:
    if isinstance(value, Mapping):
        citations = _citations_for(value) or fallback_citations
        status = value.get("status")
        text = _render_inline_text(
            value.get("text") or value.get("value") or "",
            source_index,
            citations,
            append_non_numeric_citations=bool(_citations_for(value))
            or append_non_numeric_citations,
            link_numeric_citations=link_numeric_citations,
        )
        if status:
            return f'{text} <span class="status {_status_class(str(status))}">{_escape(str(status))}</span>'
        return text
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return (
            "<ul>"
            + "".join(
                f"<li>{_format_cell(item, source_index, fallback_citations, append_non_numeric_citations=append_non_numeric_citations, link_numeric_citations=link_numeric_citations)}</li>"
                for item in value
            )
            + "</ul>"
        )
    return _render_inline_text(
        value,
        source_index,
        fallback_citations,
        append_non_numeric_citations=append_non_numeric_citations,
        link_numeric_citations=link_numeric_citations,
    )


def _render_inline_text(
    value: Any,
    source_index: Mapping[str, Mapping[str, Any]],
    citations: Any = None,
    *,
    append_non_numeric_citations: bool = True,
    link_numeric_citations: bool = True,
) -> str:
    if isinstance(value, Mapping):
        return _format_cell(value, source_index, citations)
    text = "" if value is None else str(value)
    if not text:
        return ""
    pattern = re.compile(r"\[([A-Za-z][A-Za-z0-9_.:-]{0,40})\]")
    pieces: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        source_id = match.group(1)
        if source_id not in source_index:
            continue
        pieces.append(_escape(text[last : match.start()]))
        pieces.append(_citation_ref(source_id, source_index))
        last = match.end()
    rendered = _escape(text) if last == 0 else "".join(pieces + [_escape(text[last:])])
    if last == 0 and link_numeric_citations:
        linked = _link_numeric_text(text, citations, source_index)
        if linked:
            return linked
    if append_non_numeric_citations:
        return rendered + _citation_refs(citations, source_index)
    return rendered


_NUMERIC_CITATION_RE = re.compile(
    r"(?<![A-Za-z])(?:[+-]?[$€£]?\d[\d,]*(?:\.\d+)?(?:\s?(?:B|M|K|bn|mm|billion|million))?%?|\d{4})(?![A-Za-z])",
    re.IGNORECASE,
)
_MONTH_RE = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b",
    re.IGNORECASE,
)
_NO_FALLBACK_CITATION_COLUMNS = {
    "metric",
    "name",
    "relationship",
    "workstream",
    "event",
    "title",
    "topic",
    "analyst",
    "type",
    "category",
}


def _link_numeric_text(
    text: str,
    citations: Any,
    source_index: Mapping[str, Mapping[str, Any]],
) -> str:
    citation = _first_linkable_citation(citations, source_index)
    if citation is None:
        return ""
    if _should_link_entire_value(text):
        return _citation_link(text, citation, source_index)
    pieces: list[str] = []
    last = 0
    matched = False
    for match in _NUMERIC_CITATION_RE.finditer(text):
        matched = True
        pieces.append(_escape(text[last : match.start()]))
        pieces.append(_citation_link(match.group(0), citation, source_index))
        last = match.end()
    if not matched:
        return ""
    pieces.append(_escape(text[last:]))
    return "".join(pieces)


def _should_link_entire_value(text: str) -> bool:
    compact = re.sub(r"\s+", " ", text.strip())
    if not compact or not _NUMERIC_CITATION_RE.search(compact):
        return False
    if len(compact) <= 28:
        words = re.findall(r"[A-Za-z]+", compact)
        return len(words) <= 4
    if len(compact) <= 64 and _MONTH_RE.search(compact):
        return True
    return False


def _first_linkable_citation(citations: Any, source_index: Mapping[str, Mapping[str, Any]]) -> Any:
    for citation in _dedupe_citations(_listify(citations)):
        if isinstance(citation, Mapping):
            source_id = str(citation.get("id") or citation.get("source_id") or "").strip()
            if source_id and source_id in source_index:
                return source_id
            if citation.get("url") or citation.get("source_url"):
                return citation
            continue
        source_id = str(citation).strip()
        if source_id and source_id in source_index:
            return source_id
    return None


def _citation_link(
    content: str, citation: Any, source_index: Mapping[str, Mapping[str, Any]]
) -> str:
    if isinstance(citation, Mapping):
        source_id = str(citation.get("id") or citation.get("source_id") or "").strip()
        if source_id and source_id in source_index:
            return _citation_link_for_source_id(content, source_id)
        url = str(citation.get("url") or citation.get("source_url") or "").strip()
        if url:
            title = str(
                citation.get("title")
                or citation.get("source_title")
                or citation.get("name")
                or "Source"
            )
            detail = str(
                citation.get("excerpt")
                or citation.get("pinpoint")
                or citation.get("note")
                or citation.get("detail")
                or ""
            )
            date = str(
                citation.get("as_of") or citation.get("date") or citation.get("published") or ""
            )
            return (
                f'<a class="citation-link" href="{_escape_attr(url)}" target="_blank" rel="noreferrer" '
                f'data-citation-title="{_escape_attr(title)}" data-citation-detail="{_escape_attr(detail)}" '
                f'data-citation-date="{_escape_attr(date)}" aria-label="Source for {_escape_attr(content)}">'
                f"{_escape(content)}</a>"
            )
    source_id = str(citation).strip()
    if source_id and source_id in source_index:
        return _citation_link_for_source_id(content, source_id)
    return _escape(content)


def _citation_link_for_source_id(content: str, source_id: str) -> str:
    source_attr = _escape_attr(source_id)
    return (
        f'<a class="citation-link" href="#source-{_slug(source_id)}" '
        f'data-citation-id="{source_attr}" aria-label="Source {source_attr} for {_escape_attr(content)}">'
        f"{_escape(content)}</a>"
    )


def _citation_note(
    citations: Any, source_index: Mapping[str, Mapping[str, Any]], label: str = "Section sources"
) -> str:
    refs = _citation_refs(citations, source_index)
    if not refs:
        return ""
    return f'<p class="section-citation-note"><span>{_escape(label)}:</span>{refs}</p>'


def _citations_for(value: Any) -> list[Any]:
    if not isinstance(value, Mapping):
        return []
    citations: list[Any] = []
    for key in ("citations", "citation_ids", "source_ids"):
        citations.extend(_listify(value.get(key)))
    for key in ("citation", "source_id"):
        item = value.get(key)
        if item:
            citations.append(item)
    if value.get("source_ref") or value.get("source_url"):
        source_ref = (
            value.get("source_ref") if isinstance(value.get("source_ref"), Mapping) else value
        )
        citations.append(source_ref)
    return _dedupe_citations(citations)


def _source_ref_from_fields(value: Mapping[str, Any]) -> list[Any]:
    if value.get("source_id") or value.get("source_url") or value.get("url"):
        return [value]
    return []


def _first_cited_source(
    citations: Sequence[Any], source_index: Mapping[str, Mapping[str, Any]]
) -> Mapping[str, Any]:
    for citation in citations:
        source_id = _citation_key(citation)
        if source_id in source_index:
            return source_index[source_id]
    return {}


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        if "," in value or ";" in value:
            return [item.strip() for item in re.split(r"[,;]", value) if item.strip()]
        return [value]
    return [value]


def _dedupe_citations(citations: Sequence[Any]) -> list[Any]:
    seen: set[str] = set()
    result: list[Any] = []
    for citation in citations:
        key = _citation_key(citation)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(citation)
    return result


def _citation_key(citation: Any) -> str:
    if isinstance(citation, Mapping):
        return str(
            citation.get("id")
            or citation.get("source_id")
            or citation.get("url")
            or citation.get("source_url")
            or ""
        ).strip()
    return str(citation or "").strip()


def _citation_refs(citations: Any, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    refs = []
    for citation in _dedupe_citations(_listify(citations)):
        if isinstance(citation, Mapping):
            source_id = str(citation.get("id") or citation.get("source_id") or "").strip()
            if source_id:
                refs.append(_citation_ref(source_id, source_index))
                continue
            url = str(citation.get("url") or citation.get("source_url") or "").strip()
            if url:
                refs.append(_external_citation_ref(citation))
            continue
        source_id = str(citation).strip()
        if source_id:
            refs.append(_citation_ref(source_id, source_index))
    if not refs:
        return ""
    return '<span class="citation-run" aria-label="Citations">' + "".join(refs) + "</span>"


def _citation_ref(source_id: str, source_index: Mapping[str, Mapping[str, Any]]) -> str:
    label = f"[{source_id}]"
    if source_id in source_index:
        source_attr = _escape_attr(source_id)
        return (
            f'<a class="citation-chip" href="#source-{_slug(source_id)}" '
            f'data-citation-id="{source_attr}" aria-label="Citation {source_attr}">{_escape(label)}</a>'
        )
    return f'<span class="citation-chip citation-unresolved">{_escape(label)}</span>'


def _external_citation_ref(citation: Mapping[str, Any]) -> str:
    url = str(citation.get("url") or citation.get("source_url") or "")
    title = str(
        citation.get("title") or citation.get("source_title") or citation.get("name") or "Source"
    )
    detail = str(
        citation.get("excerpt")
        or citation.get("pinpoint")
        or citation.get("note")
        or citation.get("detail")
        or ""
    )
    date = str(citation.get("as_of") or citation.get("date") or citation.get("published") or "")
    return (
        f'<a class="citation-chip" href="{_escape_attr(url)}" target="_blank" rel="noreferrer" '
        f'data-citation-title="{_escape_attr(title)}" data-citation-detail="{_escape_attr(detail)}" '
        f'data-citation-date="{_escape_attr(date)}" aria-label="Citation source">[source]</a>'
    )


def _source_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in ("sources", "model_citations", "workbook_citations"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            records.extend(
                dict(item, id=record_id)
                for record_id, item in value.items()
                if isinstance(item, Mapping)
            )
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            records.extend(item for item in value if isinstance(item, Mapping))
    for key in ("model_citations_path", "workbook_citations_path"):
        records.extend(_load_source_records_from_path(payload, payload.get(key)))
    return _normalized_sources(records)


def _resolve_payload_path(payload: Mapping[str, Any], path_value: Any) -> Path | None:
    raw = str(path_value or "").strip()
    if not raw or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
        return None
    path = Path(raw)
    if not path.is_absolute() and payload.get("_payload_dir"):
        path = Path(str(payload.get("_payload_dir"))) / path
    return path


def _load_source_records_from_path(
    payload: Mapping[str, Any], path_value: Any
) -> list[dict[str, Any]]:
    path = _resolve_payload_path(payload, path_value)
    if not path or not path.exists():
        return []
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(loaded, Mapping):
        for key in ("model_citations", "workbook_citations", "sources"):
            if isinstance(loaded.get(key), Sequence) and not isinstance(
                loaded.get(key), (str, bytes)
            ):
                return [item for item in loaded[key] if isinstance(item, Mapping)]
        return [
            dict(item, id=record_id)
            for record_id, item in loaded.items()
            if isinstance(item, Mapping)
        ]
    if isinstance(loaded, Sequence) and not isinstance(loaded, (str, bytes)):
        return [item for item in loaded if isinstance(item, Mapping)]
    return []


def _normalized_sources(sources: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)):
        return rows
    seen: set[str] = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, Mapping):
            continue
        row = dict(source)
        source_id = str(row.get("id") or row.get("source_id") or f"S{index}").strip()
        if not source_id:
            continue
        if source_id in seen:
            source_id = f"{source_id}-{index}"
        row["id"] = source_id
        seen.add(source_id)
        rows.append(row)
    return rows


def _source_tooltip_payload(
    source_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, str]]:
    payload: dict[str, dict[str, str]] = {}
    for source_id, source in source_index.items():
        date_bits = [
            str(source.get(key))
            for key in ("date", "as_of", "timestamp", "accessed", "retrieved_at", "last_checked")
            if source.get(key)
        ]
        workbook_ref = _workbook_ref(source)
        workbook_detail = _workbook_detail(source)
        payload[source_id] = {
            "id": source_id,
            "title": str(
                source.get("title")
                or source.get("name")
                or source.get("url")
                or workbook_ref
                or source_id
            ),
            "type": str(source.get("type") or source.get("source_type") or ""),
            "status": str(
                source.get("status")
                or source.get("source_status")
                or source.get("reliance_status")
                or ""
            ),
            "date": "; ".join(date_bits),
            "detail": workbook_detail
            or str(
                source.get("pinpoint")
                or source.get("excerpt")
                or source.get("note")
                or source.get("detail")
                or source.get("description")
                or ""
            ),
            "url": str(source.get("url") or _workbook_href(source) or ""),
        }
    return payload


def _workbook_ref(source: Mapping[str, Any]) -> str:
    sheet = str(source.get("sheet") or source.get("worksheet") or source.get("tab") or "").strip()
    cell_range = str(source.get("range") or source.get("cell") or source.get("cells") or "").strip()
    if sheet and cell_range:
        return f"{sheet}!{cell_range}"
    return sheet or cell_range


def _is_workbook_source(source: Mapping[str, Any]) -> bool:
    source_type = str(source.get("type") or source.get("category") or "").lower()
    return bool(
        source.get("workbook_path")
        or source.get("workbook")
        or source.get("sheet")
        or source.get("range")
        or source.get("cell")
        or source_type in {"model_cell", "workbook_cell", "workbook_range"}
    )


def _file_href(path_value: Any) -> str:
    raw = str(path_value or "").strip()
    if not raw:
        return ""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
        return raw
    if raw.startswith("/"):
        return "file://" + raw
    return raw


def _workbook_href(source: Mapping[str, Any]) -> str:
    path = (
        source.get("workbook_path")
        or source.get("workbook")
        or source.get("path")
        or source.get("href")
    )
    if not path:
        return ""
    href = _file_href(path)
    if _workbook_ref(source):
        separator = "&" if "#" in href else "#"
        href = (
            f"{href}{separator}sheet={quote(str(source.get('sheet') or source.get('worksheet') or source.get('tab') or ''), safe='')}"
            f"&range={quote(str(source.get('range') or source.get('cell') or source.get('cells') or ''), safe='')}"
        )
    return href


def _workbook_detail(source: Mapping[str, Any]) -> str:
    if not _is_workbook_source(source):
        return ""
    parts = []
    ref = _workbook_ref(source)
    if ref:
        parts.append(ref)
    if source.get("value") not in (None, ""):
        parts.append(f"value: {source.get('value')}")
    if source.get("formula"):
        parts.append(f"formula: {source.get('formula')}")
    if source.get("source_label"):
        parts.append(f"source: {source.get('source_label')}")
    return "; ".join(str(part) for part in parts if part)


def _safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace(",", "").replace("$", "").replace("+", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _to_ratio(value: Any) -> float | None:
    if isinstance(value, str) and "%" in value:
        parsed = _to_float(value)
        return None if parsed is None else parsed / 100.0
    parsed = _to_float(value)
    if parsed is None:
        return None
    return parsed / 100.0 if abs(parsed) > 2 else parsed


def _selected_margin_metric(data: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> str:
    explicit = (
        data.get("margin_metric")
        or data.get("line_metric")
        or data.get("profitability_metric")
        or data.get("margin_key")
    )
    if explicit:
        return str(explicit)
    for candidate in (
        "net_margin",
        "operating_margin",
        "adjusted_operating_margin",
        "ebitda_margin",
        "fcf_margin",
    ):
        if any(_to_ratio(row.get(candidate)) is not None for row in rows):
            return candidate
    return "net_margin"


def _metric_label(metric: str) -> str:
    labels = {
        "net_margin": "Net Margin",
        "operating_margin": "Operating Margin",
        "adjusted_operating_margin": "Adjusted Operating Margin",
        "ebitda_margin": "EBITDA Margin",
        "fcf_margin": "FCF Margin",
        "gross_margin": "Gross Margin",
    }
    if metric in labels:
        return labels[metric]
    return metric.replace("_", " ").title()


def _min_max_with_zero(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    finite_values = [value for value in values if math.isfinite(value)]
    if not finite_values:
        return 0.0, 1.0
    raw_min = min(finite_values)
    raw_max = max(finite_values)
    if raw_min >= 0:
        return _nice_bounds(0.0, raw_max, keep_zero_floor=True)
    if raw_max <= 0:
        return _nice_bounds(raw_min, 0.0, keep_zero_ceiling=True)
    return _nice_bounds(raw_min, raw_max)


def _margin_min_max_with_zero(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    finite_values = [value for value in values if math.isfinite(value)]
    if not finite_values:
        return 0.0, 1.0
    raw_min = min(finite_values)
    raw_max = max(finite_values)
    if raw_min >= 0:
        upper = max(raw_max * 1.08, 0.05)
        return 0.0, math.ceil(upper / 0.05) * 0.05
    if raw_max <= 0:
        lower = min(raw_min * 1.08, -0.05)
        return math.floor(lower / 0.05) * 0.05, 0.0
    return _nice_bounds(raw_min, raw_max)


def _nice_bounds(
    min_value: float,
    max_value: float,
    *,
    keep_zero_floor: bool = False,
    keep_zero_ceiling: bool = False,
) -> tuple[float, float]:
    if min_value == max_value:
        if min_value == 0:
            return 0.0, 1.0
        padding = abs(min_value) * 0.1 or 1.0
        min_value -= padding
        max_value += padding
    span = max_value - min_value
    padding = span * 0.08
    padded_min = min_value if keep_zero_floor else min_value - padding
    padded_max = max_value if keep_zero_ceiling else max_value + padding
    step = _nice_step((padded_max - padded_min) / 5.0)
    nice_min = 0.0 if keep_zero_floor else math.floor(padded_min / step) * step
    nice_max = 0.0 if keep_zero_ceiling else math.ceil(padded_max / step) * step
    if nice_min == nice_max:
        nice_max = nice_min + step
    return nice_min, nice_max


def _nice_step(raw_step: float) -> float:
    if raw_step <= 0 or not math.isfinite(raw_step):
        return 1.0
    exponent = math.floor(math.log10(raw_step))
    base = 10**exponent
    fraction = raw_step / base
    for nice in (1.0, 1.5, 2.0, 2.5, 5.0, 10.0):
        if fraction <= nice:
            return nice * base
    return 10.0 * base


def _min_max_with_padding(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    min_value = min(values)
    max_value = max(values)
    if min_value == max_value:
        padding = abs(max_value) * 0.08 or 1.0
        return min_value - padding, max_value + padding
    padding = (max_value - min_value) * 0.08
    return min_value - padding, max_value + padding


def _scale_y(
    value: float, min_value: float, max_value: float, top: float, plot_height: float
) -> float:
    if max_value == min_value:
        return top + plot_height / 2
    return top + (max_value - value) / (max_value - min_value) * plot_height


def _format_number(value: float | None) -> str:
    if value is None:
        return ""
    if abs(value) < 1e-9:
        return "0"
    abs_value = abs(value)
    if abs_value >= 1000:
        return f"{value / 1000:.1f}B"
    return f"{value:.1f}M"


def _format_ratio(value: float | None) -> str:
    return "" if value is None else f"{value * 100:.1f}%"


def _format_eps(value: float | None) -> str:
    return "" if value is None else f"${value:.2f}"


def _format_price(value: float | None) -> str:
    return "" if value is None else f"${value:.2f}"


def _format_rich_text(
    value: str,
    source_index: Mapping[str, Mapping[str, Any]],
    citations: Any = None,
    *,
    append_non_numeric_citations: bool = True,
    link_numeric_citations: bool = True,
) -> str:
    paragraphs = [part.strip() for part in value.split("\n\n") if part.strip()]
    return "".join(
        f"<p>{_render_inline_text(part, source_index, citations, append_non_numeric_citations=append_non_numeric_citations, link_numeric_citations=link_numeric_citations).replace(chr(10), '<br>')}</p>"
        for part in paragraphs
    )


def _identity_text(ticker: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]", "", ticker.upper())
    return (clean or "PM")[:4]


def _safe_color(color: str) -> str:
    return color if re.match(r"^#[0-9A-Fa-f]{6}$", color) else "#245f5a"


def _ticker_badge_color(issuer: Mapping[str, Any], payload: Mapping[str, Any], accent: str) -> str:
    for field in (
        "identity_color",
        "ticker_badge_color",
        "brand_dark_color",
        "dark_brand_color",
        "brand_color",
        "accent_color",
    ):
        value = issuer.get(field) or payload.get(field)
        if isinstance(value, str) and re.match(r"^#[0-9A-Fa-f]{6}$", value):
            return _ensure_white_text_readable(value)

    candidates: list[str] = []
    for field in ("brand_colors", "palette", "colors"):
        value = issuer.get(field) or payload.get(field)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            candidates.extend(str(item) for item in value)

    safe_candidates = [
        str(color) for color in candidates if re.match(r"^#[0-9A-Fa-f]{6}$", str(color))
    ]
    readable = [color for color in safe_candidates if _contrast_ratio(color, "#ffffff") >= 4.5]
    if readable:
        return min(readable, key=_relative_luminance)
    if safe_candidates:
        return _darken_until_readable(safe_candidates[0])
    return _ensure_white_text_readable(accent)


def _ensure_white_text_readable(color: str) -> str:
    safe = _safe_color(color)
    if _contrast_ratio(safe, "#ffffff") >= 4.5:
        return safe
    return _darken_until_readable(safe)


def _darken_until_readable(color: str) -> str:
    red, green, blue = _hex_to_rgb(color)
    for factor in (0.88, 0.78, 0.68, 0.58, 0.48, 0.38):
        candidate = _rgb_to_hex(int(red * factor), int(green * factor), int(blue * factor))
        if _contrast_ratio(candidate, "#ffffff") >= 4.5:
            return candidate
    return "#1f2933"


def _contrast_ratio(color_a: str, color_b: str) -> float:
    lum_a = _relative_luminance(color_a)
    lum_b = _relative_luminance(color_b)
    lighter = max(lum_a, lum_b)
    darker = min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


def _relative_luminance(color: str) -> float:
    red, green, blue = _hex_to_rgb(color)
    channels = []
    for channel in (red, green, blue):
        value = channel / 255.0
        channels.append(value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    clean = _safe_color(color).lstrip("#")
    return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)


def _rgb_to_hex(red: int, green: int, blue: int) -> str:
    return f"#{max(0, min(red, 255)):02x}{max(0, min(green, 255)):02x}{max(0, min(blue, 255)):02x}"


def _status_class(status: str) -> str:
    clean = _slug(status)
    return clean if clean in {"good", "watch", "risk", "bad", "gap", "bull", "base", "bear"} else ""


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")


def _escape(value: str) -> str:
    return html.escape(value, quote=False)


def _escape_attr(value: str) -> str:
    return html.escape(value, quote=True)
