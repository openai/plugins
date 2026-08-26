#!/usr/bin/env python3
"""Build an initiating coverage Markdown support note from structured JSON."""

import argparse
import json
from pathlib import Path

PLACEHOLDER_TERMS = ("TBD", "TODO", "MISSING", "[PLACEHOLDER]")


def fmt(value, default="not provided"):
    if value is None or value == "":
        return default
    return str(value)


def rows(items, columns):
    if not items:
        return "_No entries provided._\n"
    out = []
    out.append("| " + " | ".join(columns) + " |")
    out.append("|" + "|".join(["---"] * len(columns)) + "|")
    for item in items:
        out.append("| " + " | ".join(fmt(item.get(c, "")) for c in columns) + " |")
    return "\n".join(out) + "\n"


def build(data):
    company = fmt(data.get("company"))
    ticker = data.get("ticker")
    title = f"{company}"
    if ticker:
        title += f" ({ticker})"
    title += " Initiating Coverage"
    prepared = fmt(data.get("prepared_date"))
    cutoff = fmt(data.get("data_cutoff"))
    mode = fmt(data.get("report_mode"))
    evidence = fmt(data.get("evidence_confidence"))
    rating = fmt(data.get("rating_or_view") or data.get("user_view"))
    target = fmt(data.get("target_price"))
    currency = fmt(data.get("currency"), "")

    md = []
    md.append(f"# {title}\n")
    md.append(
        f"Prepared: {prepared} | Data cut-off: {cutoff} | Mode: {mode} | Evidence confidence: {evidence}\n"
    )
    md.append(f"Rating/View: {rating} | Target price: {currency}{target}\n")
    md.append("## MD / PM-level answer\n")
    md.append(
        fmt(
            data.get("md_pm_answer"),
            "not provided - add the core recommendation, central debate, valuation implication, and what would change the view.",
        )
        + "\n"
    )

    md.append("## Investment thesis\n")
    thesis = data.get("thesis_pillars") or []
    if thesis:
        for i, item in enumerate(thesis, 1):
            md.append(
                f"{i}. **{fmt(item.get('title'))}** - {fmt(item.get('claim'))} "
                f"[{fmt(item.get('evidence_label'))}; {fmt(item.get('confidence'))}]\n"
            )
            if item.get("disconfirming_signal"):
                md.append(f"   - Disconfirming signal: {item['disconfirming_signal']}\n")
    else:
        md.append("_No thesis pillars provided._\n")

    md.append("\n## Key debates and variant perception\n")
    md.append(
        rows(
            data.get("key_debates", []),
            ["debate", "consensus_view", "our_view", "evidence", "what_would_change_our_mind"],
        )
    )

    md.append("\n## Model and forecast drivers\n")
    md.append(
        rows(
            data.get("model_drivers", []),
            [
                "driver",
                "historical_baseline",
                "forecast_assumption",
                "sensitivity",
                "evidence_label",
            ],
        )
    )

    valuation = data.get("valuation") or {}
    md.append("\n## Valuation and target price\n")
    if valuation:
        md.append(f"- Primary method: {fmt(valuation.get('primary_method'))}\n")
        md.append(f"- Target price math: {fmt(valuation.get('target_price_math'))}\n")
        md.append(f"- Implied multiple: {fmt(valuation.get('implied_multiple'))}\n")
        md.append(f"- Upside case: {fmt(valuation.get('upside_case'))}\n")
        md.append(f"- Downside case: {fmt(valuation.get('downside_case'))}\n")
    else:
        md.append("_No valuation block provided._\n")

    md.append("\n## Catalysts and timeline\n")
    md.append(
        rows(
            data.get("catalysts", []),
            ["timing", "catalyst", "expected_read_through", "evidence", "risk"],
        )
    )

    md.append("\n## Risks and disconfirming evidence\n")
    md.append(
        rows(
            data.get("risks", []),
            ["risk", "thesis_impact", "leading_indicator", "downside_case", "monitoring_plan"],
        )
    )

    md.append("\n## Source register, conflicts, and assumptions\n")
    sources = data.get("source_register") or data.get("sources") or []
    md.append(
        rows(
            sources, ["source_id", "source_name", "source_type", "date_published", "period_covered"]
        )
    )

    if data.get("stale_data_flags"):
        md.append("\n### Stale data flags\n")
        for flag in data["stale_data_flags"]:
            md.append(f"- {flag}\n")
    if data.get("open_questions"):
        md.append("\n### Open questions\n")
        for q in data["open_questions"]:
            md.append(f"- {q}\n")

    return "".join(md)


def contains_placeholder(text):
    upper = text.upper()
    return any(term in upper for term in PLACEHOLDER_TERMS)


def main():
    parser = argparse.ArgumentParser(
        description="Build an initiating coverage Markdown support note from structured JSON."
    )
    parser.add_argument("input_json", help="Path to structured initiating coverage JSON")
    parser.add_argument("output_md", help="Output Markdown support-note path")
    parser.add_argument(
        "--publication-ready",
        action="store_true",
        help="Fail if generated support note contains unresolved placeholders.",
    )
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        output = build(data)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.publication_ready and contains_placeholder(output):
        print("ERROR: generated support note contains unresolved placeholder text")
        return 1
    Path(args.output_md).write_text(output, encoding="utf-8")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
