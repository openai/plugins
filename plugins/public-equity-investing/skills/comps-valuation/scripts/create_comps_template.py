#!/usr/bin/env python3
"""Create a comparable company analysis workbook template.

Usage:
    python create_comps_template.py --output comps_template.xlsx --target "ExampleCo" --ticker EXM
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

PEER_ROWS = 20


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def pick(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = clean(row.get(key))
        if value:
            return value
    return ""


def load_input_rows(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [
            {clean(k).lower().replace(" ", "_"): clean(v) for k, v in row.items()}
            for row in csv.DictReader(handle)
        ][:PEER_ROWS]


def numeric_or_string(ws, row: int, col: int, value: str, fmt) -> None:
    value = clean(value)
    if not value:
        ws.write_blank(row, col, None, fmt)
        return
    try:
        ws.write_number(row, col, float(value.replace(",", "")), fmt)
    except ValueError:
        ws.write(row, col, value, fmt)


def population_status(rows: list[dict[str, str]]) -> dict[str, object]:
    if not rows:
        return {
            "workbook_mode": "template_shell",
            "model_status": "template-ready",
            "status_label": "Template shell",
            "warning": "Template shell only; populate with sourced market data, financials, and peer rationale before investment use.",
            "missing_required_fields": [],
            "populated_peer_count": 0,
        }
    required = [
        "ticker",
        "company",
        "peer_tier",
        "price",
        "basic_shares",
        "revenue_ltm",
        "source_name",
        "market_data_date",
    ]
    missing: list[str] = []
    for index, row in enumerate(rows, start=1):
        for field in required:
            if not pick(row, field):
                missing.append(f"row_{index}:{field}")
    return {
        "workbook_mode": "populated_supplied_data",
        "model_status": "screen-grade" if missing else "senior-review-ready",
        "status_label": "Populated supplied data",
        "warning": "Supplied rows populated; verify live market data, estimate dates, source definitions, peer rationale, and formula tie-out before investment use.",
        "missing_required_fields": missing,
        "populated_peer_count": len(rows),
    }


def write_title(ws, title: str) -> None:
    ws.write("A1", title)


def add_table(ws, row: int, col: int, headers: list[str], rows: int, header_fmt, body_fmt) -> None:
    for idx, header in enumerate(headers):
        ws.write(row, col + idx, header, header_fmt)
    for r in range(row + 1, row + rows + 1):
        for c in range(col, col + len(headers)):
            ws.write_blank(r, c, None, body_fmt)
    ws.autofilter(row, col, row + rows, col + len(headers) - 1)
    ws.freeze_panes(row + 1, 0)


def create_workbook(
    output: Path,
    target: str,
    ticker: str,
    currency: str,
    valuation_date: str,
    input_rows: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    try:
        import xlsxwriter
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("XlsxWriter is required. Install with: pip install XlsxWriter") from exc

    wb = xlsxwriter.Workbook(str(output))
    title_fmt = wb.add_format({"bold": True, "font_size": 16})
    header_fmt = wb.add_format(
        {
            "bold": True,
            "font_color": "white",
            "bg_color": "#1F4E78",
            "border": 1,
            "text_wrap": True,
            "align": "center",
        }
    )
    subheader_fmt = wb.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1})
    body_fmt = wb.add_format({"border": 1, "text_wrap": True, "valign": "top"})
    input_fmt = wb.add_format(
        {"bg_color": "#FFF2CC", "border": 1, "text_wrap": True, "valign": "top"}
    )
    formula_fmt = wb.add_format(
        {"bg_color": "#DDEBF7", "border": 1, "text_wrap": True, "valign": "top"}
    )
    output_fmt = wb.add_format(
        {"bg_color": "#E2F0D9", "border": 1, "text_wrap": True, "valign": "top"}
    )

    input_rows = input_rows or []
    status = population_status(input_rows)
    target_input = input_rows[0] if input_rows else {}
    current_price = pick(target_input, "price", "share_price", "current_price")

    # Cover
    cover_ws = wb.add_worksheet("Cover")
    cover_ws.hide_gridlines(2)
    cover_ws.write("A1", "Comparable Company Analysis Dashboard Cover", title_fmt)
    cover_ws.write(
        "A2",
        "First-tab review page: populate the workbook, then use this cover to read the target, peer set, valuation range, source posture, and QA status.",
        body_fmt,
    )
    cover_ws.write_row(3, 0, ["Section", "Metric", "Value", "Notes"], header_fmt)
    cover_rows = [
        ("Header", "Target company", target, "Subject company"),
        ("Header", "Ticker", ticker, "Subject ticker/security"),
        (
            "Header",
            "Valuation date",
            valuation_date,
            "Market data and sources should tie to this date",
        ),
        (
            "Header",
            "Currency / units",
            f"{currency} / USD millions except per-share data",
            "Update if non-USD or mixed units are used",
        ),
        (
            "Status",
            "Model status",
            status["status_label"],
            "Decision grade requires sourced market data, financials, definitions, and QA",
        ),
        (
            "Status",
            "Workbook mode",
            status["workbook_mode"],
            "Formula-ready workbook populated only from supplied rows when provided",
        ),
        (
            "Peer universe",
            "Total tickers loaded",
            "=COUNTA(Universe!A2:A21)",
            "Includes target and any watchlist/excluded names",
        ),
        (
            "Peer universe",
            "Core peers",
            '=COUNTIF(Universe!C2:C21,"Core")',
            "Use only true comparables for selected statistics",
        ),
        (
            "Valuation output",
            "Selected multiple",
            "=Valuation!B3",
            "Document rationale against peer statistics",
        ),
        (
            "Valuation output",
            "Low implied value / share",
            "=Valuation!H13",
            "Chart-ready valuation range",
        ),
        (
            "Valuation output",
            "Mid implied value / share",
            "=Valuation!H14",
            "Primary reference case",
        ),
        (
            "Valuation output",
            "High implied value / share",
            "=Valuation!H15",
            "Upside valuation case",
        ),
        (
            "PM judgment",
            "Current price",
            "=PM_Action_Box!B3",
            "Anchor valuation to spot and market-data as-of date",
        ),
        (
            "PM judgment",
            "Implied upside/downside",
            "=PM_Action_Box!B5",
            "Do not leave valuation disconnected from stock price",
        ),
        (
            "PM judgment",
            "What is priced in",
            "=PM_Action_Box!B6",
            "State market-implied expectation before action",
        ),
        (
            "PM judgment",
            "Variant estimate path",
            "=PM_Action_Box!B7",
            "Identify the estimate line that must differ from consensus",
        ),
        ("PM judgment", "PM action box", "=PM_Action_Box!B8", "Add/trim/exit/watchlist rule"),
        (
            "Source posture",
            "Source entries",
            "=COUNTA(Sources!A2:A41)",
            "Every market/financial input should have source support",
        ),
        (
            "Source posture",
            "Source caveat",
            "Supplied rows; verify" if input_rows else "Needs support",
            "Populate Sources with retrieval date, data date, and confidence",
        ),
        (
            "QA posture",
            "Open QA checks",
            '=COUNTIF(QA_Log!B2:B31,"Not run")',
            "Resolve before senior review",
        ),
        (
            "QA posture",
            "Denominator review",
            "Required",
            "Flag negative EBITDA/EPS, non-comparable calendars, leverage, and one-time adjustments",
        ),
        (
            "Workbook map",
            "Control",
            "Inputs and model status",
            "Set valuation date, currency, fiscal basis, and status",
        ),
        (
            "Workbook map",
            "Universe / Market_Data / Financials",
            "Peer definitions and source inputs",
            "Do not hide excluded or weak-fit companies",
        ),
        (
            "Workbook map",
            "Multiples / Benchmarking",
            "Trading multiple and fit analysis",
            "Use outlier flags before calculating conclusions",
        ),
        (
            "Workbook map",
            "Multiple_Bridge",
            "Peer median to selected multiple",
            "Bridge growth, margin, quality, leverage, liquidity, and source confidence",
        ),
        (
            "Workbook map",
            "Valuation / Sensitivity",
            "Conclusion and range",
            "Tie final selected range to peer evidence",
        ),
        (
            "Workbook map",
            "PM_Action_Box",
            "PM decision and action rules",
            "Anchor value to current price and missing evidence",
        ),
        (
            "Workbook map",
            "Sources / QA_Log",
            "Evidence and review trail",
            "Source gaps stay visible",
        ),
    ]
    for r, (section, metric, value, notes) in enumerate(cover_rows, 4):
        cover_ws.write(r, 0, section, body_fmt)
        cover_ws.write(r, 1, metric, body_fmt)
        if isinstance(value, str) and value.startswith("="):
            cover_ws.write_formula(r, 2, value, output_fmt)
        else:
            cover_ws.write(r, 2, value, output_fmt)
        cover_ws.write(r, 3, notes, body_fmt)
    cover_ws.write("F3", "Chart 1: implied value / share range", subheader_fmt)
    cover_ws.write("F19", "Chart 2: peer EV / CY1 revenue once populated", subheader_fmt)
    cover_ws.set_column("A:A", 22)
    cover_ws.set_column("B:B", 28)
    cover_ws.set_column("C:C", 28)
    cover_ws.set_column("D:D", 72)
    cover_ws.set_column("F:M", 16)

    # README
    ws = wb.add_worksheet("README")
    ws.hide_gridlines(2)
    ws.write("A1", "Comparable Company Analysis Model Guide", title_fmt)
    rows = [
        (
            "Purpose",
            "Institutional trading comps workbook shell for valuation and peer benchmarking.",
        ),
        ("Target", target),
        ("Ticker", ticker),
        ("Valuation date", valuation_date),
        ("Currency", currency),
        (
            "Cover workflow",
            "Use the Cover tab as the first senior-review page. It should show the target snapshot, peer set, valuation range, source posture, and QA status after the workbook is populated.",
        ),
        (
            "Update instructions",
            "Populate Control, Universe, Market_Data, Financials, Adjustments, then review Cover, Multiples, Benchmarking, Valuation, Sensitivity, Sources, and QA_Log.",
        ),
        (
            "Model limitations",
            "Template only. Replace placeholder peers and assumptions with sourced data.",
        ),
    ]
    for r, (label, value) in enumerate(rows, 2):
        ws.write(r, 0, label, subheader_fmt)
        ws.write(r, 1, value, body_fmt)
    ws.set_column("A:A", 24)
    ws.set_column("B:B", 120)

    # Control
    ws = wb.add_worksheet("Control")
    ws.hide_gridlines(2)
    ws.write("A1", "Control Panel", title_fmt)
    controls = [
        ("Target company", target),
        ("Target ticker", ticker),
        ("Valuation date", valuation_date),
        ("Reporting currency", currency),
        ("Units", "USD millions except per-share data"),
        ("Fiscal basis", "Calendarized"),
        ("Primary use case", "Price target / valuation range"),
        ("Selected peer tier", "Core"),
        ("Model status", status["status_label"]),
    ]
    for r, (label, value) in enumerate(controls, 2):
        ws.write(r, 0, label, subheader_fmt)
        ws.write(r, 1, value, input_fmt)
        ws.write_comment(r, 1, "Input cell: update or link to a clearly sourced assumption.")
    ws.set_column("A:A", 28)
    ws.set_column("B:B", 44)

    # Universe
    ws = wb.add_worksheet("Universe")
    ws.hide_gridlines(2)
    headers = [
        "Ticker",
        "Company",
        "Peer Tier",
        "Country",
        "Business Description",
        "Revenue Mix / Segment Notes",
        "Geography / End Market",
        "Size Fit",
        "Growth Fit",
        "Margin Fit",
        "Liquidity / Float",
        "Index Membership",
        "ETF Ownership / Flow",
        "Short Interest / Borrow",
        "ADR / Share-Class Issue",
        "Consensus Coverage",
        "Estimate Revision Relevance",
        "Sector KPI Regime",
        "Inclusion Rationale",
        "Exclusion Rationale",
        "Data Confidence",
        "Analyst Notes",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS, header_fmt, body_fmt)
    if input_rows:
        for r, row in enumerate(input_rows, 1):
            ws.write_row(
                r,
                0,
                [
                    pick(row, "ticker") or ticker,
                    pick(row, "company") or target,
                    pick(row, "peer_tier") or ("Target" if r == 1 else "Core"),
                    pick(row, "country"),
                    pick(row, "business_description", "business_model"),
                    pick(row, "revenue_mix", "segment_notes"),
                    pick(row, "geography", "end_market"),
                    pick(row, "size_fit"),
                    pick(row, "growth_fit"),
                    pick(row, "margin_fit"),
                    pick(row, "liquidity_float", "float", "adv"),
                    pick(row, "index_membership"),
                    pick(row, "etf_ownership_flow", "etf_ownership", "passive_ownership"),
                    pick(row, "short_interest_borrow", "short_interest", "borrow"),
                    pick(row, "adr_share_class_issue"),
                    pick(row, "consensus_coverage"),
                    pick(row, "estimate_revision_relevance"),
                    pick(row, "sector_kpi_regime"),
                    pick(row, "inclusion_rationale", "peer_rationale"),
                    pick(row, "exclusion_rationale"),
                    pick(row, "confidence", "data_confidence"),
                    pick(row, "analyst_notes", "notes"),
                ],
                input_fmt,
            )
    else:
        ws.write_row(
            1,
            0,
            [
                ticker,
                target,
                "Target",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Subject company",
                "",
                "",
                "",
            ],
            input_fmt,
        )
    ws.set_column("A:A", 12)
    ws.set_column("B:B", 26)
    ws.set_column("C:C", 16)
    ws.set_column("E:N", 28)

    # Market_Data
    ws = wb.add_worksheet("Market_Data")
    ws.hide_gridlines(2)
    headers = [
        "Ticker",
        "Company",
        "Peer Tier",
        "Price",
        "Basic Shares",
        "Dilution Adj.",
        "Diluted Shares",
        "Equity Value",
        "Debt",
        "Preferred",
        "Minority Interest",
        "Cash & Equiv.",
        "Other Non-op Assets",
        "Enterprise Value",
        "Market Data Date",
        "Source",
        "Confidence",
        "Notes",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS, header_fmt, body_fmt)
    for r in range(1, PEER_ROWS + 1):
        excel_row = r + 1
        ws.write_formula(r, 0, f"=Universe!A{excel_row}", formula_fmt)
        ws.write_formula(r, 1, f"=Universe!B{excel_row}", formula_fmt)
        ws.write_formula(r, 2, f"=Universe!C{excel_row}", formula_fmt)
        ws.write_formula(r, 6, f'=IFERROR(E{excel_row}+F{excel_row},"")', formula_fmt)
        ws.write_formula(r, 7, f'=IFERROR(D{excel_row}*G{excel_row},"")', formula_fmt)
        ws.write_formula(
            r,
            13,
            f'=IFERROR(H{excel_row}+I{excel_row}+J{excel_row}+K{excel_row}-L{excel_row}-M{excel_row},"")',
            formula_fmt,
        )
    for r, row in enumerate(input_rows, 1):
        for col, key_set in {
            3: ("price", "share_price", "current_price"),
            4: ("basic_shares", "shares", "shares_outstanding"),
            5: ("dilution_adj", "dilution_adjustment"),
            8: ("debt", "total_debt"),
            9: ("preferred", "preferred_equity"),
            10: ("minority_interest",),
            11: ("cash", "cash_equiv", "cash_and_equivalents"),
            12: ("other_non_op_assets", "non_operating_assets"),
            14: ("market_data_date", "as_of_date"),
            15: ("source_name", "source"),
            16: ("confidence", "data_confidence"),
            17: ("notes",),
        }.items():
            numeric_or_string(ws, r, col, pick(row, *key_set), input_fmt)
    ws.set_column("A:R", 16)
    ws.set_column("B:B", 26)
    ws.set_column("R:R", 34)

    # Financials
    ws = wb.add_worksheet("Financials")
    ws.hide_gridlines(2)
    headers = [
        "Ticker",
        "Company",
        "Peer Tier",
        "LTM Revenue",
        "CY1 Revenue",
        "CY2 Revenue",
        "LTM EBITDA",
        "CY1 EBITDA",
        "CY2 EBITDA",
        "LTM EBIT",
        "CY1 EBIT",
        "CY2 EBIT",
        "LTM Net Income",
        "CY1 EPS",
        "CY2 EPS",
        "LTM FCF",
        "CY1 FCF",
        "Revenue Growth CY1",
        "Revenue Growth CY2",
        "EBITDA Margin LTM",
        "EBITDA Margin CY1",
        "FCF Margin CY1",
        "Source",
        "Confidence",
        "Notes",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS, header_fmt, body_fmt)
    for r in range(1, PEER_ROWS + 1):
        excel_row = r + 1
        ws.write_formula(r, 0, f"=Universe!A{excel_row}", formula_fmt)
        ws.write_formula(r, 1, f"=Universe!B{excel_row}", formula_fmt)
        ws.write_formula(r, 2, f"=Universe!C{excel_row}", formula_fmt)
        ws.write_formula(r, 17, f'=IFERROR(E{excel_row}/D{excel_row}-1,"NM")', formula_fmt)
        ws.write_formula(r, 18, f'=IFERROR(F{excel_row}/E{excel_row}-1,"NM")', formula_fmt)
        ws.write_formula(r, 19, f'=IFERROR(G{excel_row}/D{excel_row},"NM")', formula_fmt)
        ws.write_formula(r, 20, f'=IFERROR(H{excel_row}/E{excel_row},"NM")', formula_fmt)
        ws.write_formula(r, 21, f'=IFERROR(Q{excel_row}/E{excel_row},"NM")', formula_fmt)
    for r, row in enumerate(input_rows, 1):
        for col, key_set in {
            3: ("revenue_ltm", "ltm_revenue"),
            4: ("revenue_cy1", "cy1_revenue", "ntm_revenue"),
            5: ("revenue_cy2", "cy2_revenue"),
            6: ("ebitda_ltm", "ltm_ebitda"),
            7: ("ebitda_cy1", "cy1_ebitda", "ntm_ebitda"),
            8: ("ebitda_cy2", "cy2_ebitda"),
            9: ("ebit_ltm", "ltm_ebit"),
            10: ("ebit_cy1", "cy1_ebit"),
            11: ("ebit_cy2", "cy2_ebit"),
            12: ("net_income_ltm", "ltm_net_income"),
            13: ("eps_cy1", "cy1_eps", "ntm_eps"),
            14: ("eps_cy2", "cy2_eps"),
            15: ("fcf_ltm", "ltm_fcf"),
            16: ("fcf_cy1", "cy1_fcf", "ntm_fcf"),
            22: ("source_name", "source"),
            23: ("confidence", "data_confidence"),
            24: ("notes",),
        }.items():
            numeric_or_string(ws, r, col, pick(row, *key_set), input_fmt)
    ws.set_column("A:Y", 16)
    ws.set_column("B:B", 26)
    ws.set_column("Y:Y", 34)

    # Adjustments
    ws = wb.add_worksheet("Adjustments")
    ws.hide_gridlines(2)
    headers = [
        "Ticker",
        "Company",
        "Period",
        "Adjustment Type",
        "Reported Metric",
        "Reported Value",
        "Adjustment",
        "Normalized Value",
        "Rationale",
        "Source",
        "Confidence",
        "Notes",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS, header_fmt, body_fmt)
    ws.set_column("A:L", 18)
    ws.set_column("I:I", 40)
    ws.set_column("L:L", 34)

    # Multiples
    ws = wb.add_worksheet("Multiples")
    ws.hide_gridlines(2)
    headers = [
        "Ticker",
        "Company",
        "Peer Tier",
        "EV",
        "EV / LTM Rev",
        "EV / CY1 Rev",
        "EV / CY2 Rev",
        "EV / LTM EBITDA",
        "EV / CY1 EBITDA",
        "EV / CY2 EBITDA",
        "EV / LTM EBIT",
        "EV / CY1 EBIT",
        "P / CY1 EPS",
        "P / CY2 EPS",
        "FCF Yield CY1",
        "Rule of 40 / Sector KPI",
        "Outlier Flag",
        "Notes",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS, header_fmt, body_fmt)
    for r in range(1, PEER_ROWS + 1):
        excel_row = r + 1
        ws.write_formula(r, 0, f"=Universe!A{excel_row}", formula_fmt)
        ws.write_formula(r, 1, f"=Universe!B{excel_row}", formula_fmt)
        ws.write_formula(r, 2, f"=Universe!C{excel_row}", formula_fmt)
        ws.write_formula(r, 3, f"=Market_Data!N{excel_row}", formula_fmt)
        formulas = [
            f'=IFERROR(IF(Financials!D{excel_row}>0,D{excel_row}/Financials!D{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!E{excel_row}>0,D{excel_row}/Financials!E{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!F{excel_row}>0,D{excel_row}/Financials!F{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!G{excel_row}>0,D{excel_row}/Financials!G{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!H{excel_row}>0,D{excel_row}/Financials!H{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!I{excel_row}>0,D{excel_row}/Financials!I{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!J{excel_row}>0,D{excel_row}/Financials!J{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!K{excel_row}>0,D{excel_row}/Financials!K{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!N{excel_row}>0,Market_Data!D{excel_row}/Financials!N{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!O{excel_row}>0,Market_Data!D{excel_row}/Financials!O{excel_row},"NM"),"NM")',
            f'=IFERROR(IF(Financials!Q{excel_row}>0,Financials!Q{excel_row}/Market_Data!H{excel_row},"NM"),"NM")',
            f'=IFERROR(Financials!R{excel_row}+Financials!V{excel_row},"")',
        ]
        for c, formula in enumerate(formulas, 4):
            ws.write_formula(r, c, formula, formula_fmt)
    stats_row = PEER_ROWS + 3
    ws.write(stats_row, 0, "Peer Statistics", subheader_fmt)
    labels = ["All Peer Median", "Core Peer Median", "25th Percentile", "75th Percentile"]
    for idx, label in enumerate(labels, stats_row + 1):
        ws.write(idx, 0, label, subheader_fmt)
    ws.set_column("A:R", 16)
    ws.set_column("B:B", 26)
    ws.set_column("R:R", 34)

    # Benchmarking
    ws = wb.add_worksheet("Benchmarking")
    ws.hide_gridlines(2)
    headers = [
        "Ticker",
        "Company",
        "Peer Tier",
        "Revenue Growth",
        "EBITDA Margin",
        "FCF Margin",
        "Leverage",
        "ROIC / Quality KPI",
        "Business Quality Notes",
        "Premium / Discount Rationale",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS, header_fmt, body_fmt)
    for r in range(1, PEER_ROWS + 1):
        excel_row = r + 1
        ws.write_formula(r, 0, f"=Universe!A{excel_row}", formula_fmt)
        ws.write_formula(r, 1, f"=Universe!B{excel_row}", formula_fmt)
        ws.write_formula(r, 2, f"=Universe!C{excel_row}", formula_fmt)
        ws.write_formula(r, 3, f"=Financials!R{excel_row}", formula_fmt)
        ws.write_formula(r, 4, f"=Financials!U{excel_row}", formula_fmt)
        ws.write_formula(r, 5, f"=Financials!V{excel_row}", formula_fmt)
    ws.set_column("A:J", 18)
    ws.set_column("I:J", 42)

    # Multiple bridge
    ws = wb.add_worksheet("Multiple_Bridge")
    ws.hide_gridlines(2)
    ws.write("A1", "Peer Median To Selected Multiple Bridge", title_fmt)
    bridge_headers = [
        "Bridge Item",
        "Direction",
        "Adjustment",
        "Rationale",
        "Source",
        "PM Judgment",
    ]
    for c, h in enumerate(bridge_headers):
        ws.write(2, c, h, header_fmt)
    bridge_rows = [
        (
            "Peer median starting point",
            "Base",
            "",
            "Use clean core peer median before judgment",
            "Multiples / Benchmarking",
            "Do not anchor to min/max without reason",
        ),
        (
            "Growth premium / discount",
            "Input",
            "",
            "Relative revenue/EPS/FCF growth versus peers",
            "Financials / consensus",
            "Only pay for durable growth",
        ),
        (
            "Margin and FCF quality",
            "Input",
            "",
            "Quality of earnings and cash conversion",
            "Financials / adjustments",
            "EBITDA without cash conversion deserves a lower multiple",
        ),
        (
            "ROIC / business quality",
            "Input",
            "",
            "ROIC, moat, recurrence, cyclicality, and reinvestment runway",
            "Benchmarking",
            "Quality premium needs proof",
        ),
        (
            "Leverage and balance sheet",
            "Input",
            "",
            "Net debt, refinancing risk, dilution risk as common-equity factors",
            "Market_Data / filings",
            "Route debt-security valuation to Credit Markets",
        ),
        (
            "Liquidity / float",
            "Input",
            "",
            "Capacity, float, ADV, and trading liquidity",
            "Market data",
            "Illiquidity can limit PM action",
        ),
        (
            "Index / ETF ownership",
            "Input",
            "",
            "Passive ownership, rebalance flow, and factor exposure",
            "Index / ETF source",
            "Flow can affect timing, not intrinsic value alone",
        ),
        (
            "Data confidence",
            "Input",
            "",
            "Freshness and source support",
            "Sources",
            "Weak data caps decision grade",
        ),
        (
            "Selected multiple",
            "Output",
            "",
            "Final selected multiple after bridge",
            "PM judgment",
            "Must tie to current price and action rule",
        ),
    ]
    for r, row in enumerate(bridge_rows, 3):
        for c, value in enumerate(row):
            ws.write(r, c, value, input_fmt if c in {1, 2, 3, 4, 5} else body_fmt)
    ws.set_column("A:F", 28)

    # Valuation
    ws = wb.add_worksheet("Valuation")
    ws.hide_gridlines(2)
    ws.write("A1", "Valuation Conclusion", title_fmt)
    vals = [
        ("Selected multiple", "EV / CY1 Revenue"),
        ("Low multiple", ""),
        ("Mid multiple", ""),
        ("High multiple", ""),
        ("Target financial metric", ""),
        ("Net debt / (cash)", ""),
        ("Diluted shares", ""),
    ]
    for r, (label, value) in enumerate(vals, 2):
        ws.write(r, 0, label, subheader_fmt)
        ws.write(r, 1, value, input_fmt)
        ws.write_comment(
            r,
            1,
            "Valuation input: support with peer evidence, source data, or documented judgment.",
        )
    headers = [
        "Case",
        "Selected Multiple",
        "Target Metric",
        "Implied EV",
        "Net Debt",
        "Implied Equity Value",
        "Diluted Shares",
        "Implied Value / Share",
    ]
    for c, h in enumerate(headers):
        ws.write(11, c, h, header_fmt)
    cases = [("Low", "=B4"), ("Mid", "=B5"), ("High", "=B6")]
    for i, (case, mult_formula) in enumerate(cases, 12):
        excel_row = i + 1
        ws.write(i, 0, case, output_fmt)
        ws.write_formula(i, 1, mult_formula, formula_fmt)
        ws.write_formula(i, 2, "=B7", formula_fmt)
        ws.write_formula(i, 3, f'=IFERROR(B{excel_row}*C{excel_row},"")', formula_fmt)
        ws.write_formula(i, 4, "=B8", formula_fmt)
        ws.write_formula(i, 5, f'=IFERROR(D{excel_row}-E{excel_row},"")', formula_fmt)
        ws.write_formula(i, 6, "=B9", formula_fmt)
        ws.write_formula(i, 7, f'=IFERROR(F{excel_row}/G{excel_row},"")', formula_fmt)
    ws.write("A18", "Executive conclusion", subheader_fmt)
    ws.write(
        "A19", "State selected range, key rationale, confidence level, and major risks.", body_fmt
    )
    ws.set_column("A:H", 22)

    # PM action box
    ws = wb.add_worksheet("PM_Action_Box")
    ws.hide_gridlines(2)
    ws.write("A1", "PM Action Box", title_fmt)
    action_rows = [
        ("Current price", current_price, "Market data as-of and source required"),
        ("Implied value / share", "=Valuation!H14", "Base valuation output"),
        ("Upside/downside to spot", "", "Compare implied value range to current stock price"),
        ("What is priced in", "", "Market-implied expectation before recommending action"),
        (
            "Variant estimate path",
            "",
            "Revenue, margin, EPS, FCF, or KPI line that must differ from consensus",
        ),
        (
            "PM action implication",
            "",
            "add / press / hold / trim / exit / hedge / watchlist / wait for proof",
        ),
        ("Add / trim / exit rule", "", "Observable threshold tied to model line and source"),
        ("Missing evidence", "", "Unresolved source, consensus, market-data, or diligence gaps"),
    ]
    ws.write_row(2, 0, ["Metric", "Value", "Notes"], header_fmt)
    for r, row in enumerate(action_rows, 3):
        ws.write(r, 0, row[0], subheader_fmt)
        if isinstance(row[1], str) and row[1].startswith("="):
            ws.write_formula(r, 1, row[1], output_fmt)
        else:
            ws.write(r, 1, row[1], input_fmt)
        ws.write(r, 2, row[2], body_fmt)
    ws.set_column("A:A", 28)
    ws.set_column("B:B", 32)
    ws.set_column("C:C", 80)

    # Sensitivity
    ws = wb.add_worksheet("Sensitivity")
    ws.hide_gridlines(2)
    ws.write("A1", "Sensitivity Analysis", title_fmt)
    ws.write("A3", "Multiple vs Target Metric", subheader_fmt)
    metrics = ["Metric -10%", "Metric -5%", "Base Metric", "Metric +5%", "Metric +10%"]
    multiples = ["Low - 0.5x", "Low", "Mid", "High", "High + 0.5x"]
    for c, label in enumerate(metrics, 1):
        ws.write(3, c, label, header_fmt)
    for r, label in enumerate(multiples, 4):
        ws.write(r, 0, label, header_fmt)
        for c in range(1, 6):
            ws.write_formula(r, c, "=NA()", formula_fmt)
    ws.set_column("A:F", 18)

    # Sources
    ws = wb.add_worksheet("Sources")
    ws.hide_gridlines(2)
    headers = [
        "Company/Ticker",
        "Metric",
        "Period",
        "Source Name",
        "Connector Path / URL / Accession",
        "Retrieval Date",
        "Data Date",
        "Source Type",
        "Confidence",
        "Definition Notes",
    ]
    add_table(ws, 0, 0, headers, PEER_ROWS * 2, header_fmt, body_fmt)
    for r, row in enumerate(input_rows, 1):
        ws.write_row(
            r,
            0,
            [
                pick(row, "ticker"),
                "market and financial inputs",
                pick(row, "period", "market_data_date", "as_of_date"),
                pick(row, "source_name", "source"),
                pick(row, "source_url", "url", "connector_path"),
                pick(row, "retrieval_date", "retrieved_at"),
                pick(row, "market_data_date", "as_of_date", "source_date"),
                pick(row, "source_type"),
                pick(row, "confidence", "data_confidence"),
                pick(row, "definition_notes", "notes"),
            ],
            input_fmt,
        )
    ws.set_column("A:J", 20)
    ws.set_column("E:E", 48)
    ws.set_column("J:J", 42)

    # QA_Log
    ws = wb.add_worksheet("QA_Log")
    ws.hide_gridlines(2)
    headers = ["Check", "Status", "Finding", "Fix / Action", "Owner", "Date", "Notes"]
    add_table(ws, 0, 0, headers, 30, header_fmt, body_fmt)
    checks = [
        "Workbook structure",
        "Source log complete",
        "Formula consistency",
        "Broken formula/errors",
        "External links",
        "Peer rationale",
        "Denominator treatment",
        "Market data freshness",
        "Normalization documented",
        "Valuation range rationale",
    ]
    for r, check in enumerate(checks, 1):
        ws.write(r, 0, check, body_fmt)
        ws.write(r, 1, "Review required" if input_rows else "Not run", input_fmt)
    ws.set_column("A:G", 24)
    ws.set_column("C:D", 44)

    value_chart = wb.add_chart({"type": "column"})
    value_chart.add_series(
        {
            "name": "Implied value / share",
            "categories": "=Valuation!$A$13:$A$15",
            "values": "=Valuation!$H$13:$H$15",
            "fill": {"color": "#5B9BD5"},
        }
    )
    value_chart.set_title({"name": "Implied Value / Share"})
    value_chart.set_y_axis({"name": f"{currency} / share"})
    value_chart.set_legend({"none": True})
    cover_ws.insert_chart("F4", value_chart, {"x_scale": 1.15, "y_scale": 1.05})

    peer_chart = wb.add_chart({"type": "column"})
    peer_chart.add_series(
        {
            "name": "EV / CY1 Revenue",
            "categories": "=Multiples!$A$2:$A$21",
            "values": "=Multiples!$F$2:$F$21",
            "fill": {"color": "#70AD47"},
        }
    )
    peer_chart.set_title({"name": "Peer EV / CY1 Revenue"})
    peer_chart.set_y_axis({"name": "x"})
    peer_chart.set_legend({"none": True})
    cover_ws.insert_chart("F20", peer_chart, {"x_scale": 1.15, "y_scale": 1.05})

    wb.close()
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a comparable company analysis workbook template."
    )
    parser.add_argument(
        "--output", default="comps_analysis_template.xlsx", help="Output .xlsx path."
    )
    parser.add_argument("--target", default="TargetCo", help="Target company name.")
    parser.add_argument("--ticker", default="TGT", help="Target company ticker.")
    parser.add_argument("--currency", default="USD", help="Model currency.")
    parser.add_argument(
        "--valuation-date", default=date.today().isoformat(), help="Valuation date YYYY-MM-DD."
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        help="Optional supplied target/peer data CSV to populate the workbook.",
    )
    return parser.parse_args()


def artifact_manifest(
    output: Path, *, status: str, workbook_written: bool
) -> list[dict[str, object]]:
    output_dir = output.parent
    return [
        {
            "key": "workbook",
            "path": str(output),
            "required": True,
            "written": workbook_written,
            "description": "Comparable-company analysis workbook template.",
            "artifact_role": "primary_human_deliverable"
            if workbook_written
            else "support_artifact",
            "hidden_unless_requested": not workbook_written,
            "user_visible_default": workbook_written,
            "support_reason": ""
            if workbook_written
            else "Workbook was not written because generation failed.",
        },
        {
            "key": "run_log",
            "path": str(output_dir / "run_log.json"),
            "required": True,
            "written": True,
            "description": "Status, warnings, hard failures, dependency status, and output paths.",
            "artifact_role": "machine_support",
            "hidden_unless_requested": True,
            "user_visible_default": False,
            "support_reason": "Run log is automation/audit support for the workbook.",
        },
        {
            "key": "manifest",
            "path": str(output_dir / "manifest.json"),
            "required": True,
            "written": True,
            "description": "Machine-readable output manifest.",
            "artifact_role": "machine_support",
            "hidden_unless_requested": True,
            "user_visible_default": False,
            "support_reason": "Manifest is routing support, not the comps deliverable.",
        },
    ]


def write_run_artifacts(output: Path, payload: dict[str, object]) -> None:
    output_dir = output.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_log.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "primary_human_deliverable": payload.get("primary_human_deliverable"),
        "artifact_mode": payload.get("artifact_mode", "workbook"),
        "support_artifacts_user_visible_default": False,
        "final_response_guidance": payload.get(
            "final_response_guidance",
            {
                "lead_with": "primary_human_deliverable",
                "mention_support_artifacts": "only_briefly_unless_requested",
            },
        ),
        "outputs": payload["output_manifest"],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        input_rows = load_input_rows(args.input_csv)
        status_info = create_workbook(
            output, args.target, args.ticker, args.currency, args.valuation_date, input_rows
        )
    except RuntimeError as exc:
        run_log = {
            "status": "failed",
            "model_status": "not-decision-ready",
            "artifact_level": "template_workbook",
            "workbook_mode": "template_shell",
            "artifact_mode": "blocked",
            "source_basis": [],
            "warnings": [],
            "hard_failures": [str(exc)],
            "dependency_status": {"XlsxWriter": "missing"},
            "outputs": {
                "workbook": str(output),
                "run_log": str(output.parent / "run_log.json"),
                "manifest": str(output.parent / "manifest.json"),
            },
            "primary_human_deliverable": None,
            "support_artifacts_user_visible_default": False,
            "final_response_guidance": {
                "lead_with": "blocked_status",
                "mention_support_artifacts": "include run log for repair",
            },
            "output_manifest": artifact_manifest(output, status="failed", workbook_written=False),
        }
        write_run_artifacts(output, run_log)
        print(f"ERROR: {exc}")
        return 1

    run_log = {
        "status": "completed",
        "model_status": status_info["model_status"],
        "artifact_level": "template_workbook",
        "workbook_mode": status_info["workbook_mode"],
        "artifact_mode": "workbook",
        "source_basis": [],
        "warnings": [status_info["warning"]],
        "hard_failures": [],
        "populated_peer_count": status_info["populated_peer_count"],
        "missing_required_fields": status_info["missing_required_fields"],
        "dependency_status": {"XlsxWriter": "available"},
        "outputs": {
            "workbook": str(output),
            "run_log": str(output.parent / "run_log.json"),
            "manifest": str(output.parent / "manifest.json"),
        },
        "primary_human_deliverable": str(output),
        "support_artifacts_user_visible_default": False,
        "final_response_guidance": {
            "lead_with": "primary_human_deliverable",
            "mention_support_artifacts": "only_briefly_unless_requested",
        },
        "output_manifest": artifact_manifest(output, status="completed", workbook_written=True),
    }
    write_run_artifacts(output, run_log)
    print(f"Created comps workbook template: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
