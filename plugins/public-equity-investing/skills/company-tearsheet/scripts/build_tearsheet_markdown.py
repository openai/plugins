#!/usr/bin/env python3
"""Build a markdown company tearsheet from structured JSON.

This utility is intentionally simple and offline. It helps produce consistent
one-page profile formatting after the assistant has gathered and labeled facts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def fmt(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return ""
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        padded = list(row)[: len(headers)] + [""] * max(0, len(headers) - len(row))
        out.append("| " + " | ".join(fmt(cell) for cell in padded) + " |")
    return "\n".join(out)


def build_markdown(data: dict[str, Any]) -> str:
    entity = fmt(data.get("entity", "Entity"))
    profile_type = fmt(data.get("profile_type", "profile"))
    as_of = fmt(data.get("as_of_date", ""))
    scope = fmt(data.get("scope", ""))
    caveat = fmt(data.get("source_caveat", ""))
    sections = data.get("sections", {}) if isinstance(data.get("sections"), dict) else {}

    lines: list[str] = []
    lines.append(f"# {entity} Tearsheet")
    lines.append(f"**Profile type:** {profile_type}  ")
    if as_of:
        lines.append(f"**As of:** {as_of}  ")
    if scope:
        lines.append(f"**Scope:** {scope}  ")
    if caveat:
        lines.append(f"**Source caveat:** {caveat}  ")

    one_line = sections.get("one_line_view") or data.get("one_line_view")
    if one_line:
        lines.extend(["", "## One-line view", fmt(one_line)])

    snapshot_rows: list[list[Any]] = []
    snapshot = sections.get("business_snapshot") or data.get("business_snapshot", [])
    if isinstance(snapshot, list):
        for item in snapshot:
            if isinstance(item, dict):
                snapshot_rows.append(
                    [
                        item.get("field", ""),
                        item.get("detail", ""),
                        item.get("source", ""),
                        item.get("evidence", ""),
                        item.get("confidence", ""),
                    ]
                )
    if snapshot_rows:
        lines.extend(
            [
                "",
                "## Business snapshot",
                table(["Field", "Detail", "Source", "Evidence", "Confidence"], snapshot_rows),
            ]
        )

    metric_rows: list[list[Any]] = []
    metrics = data.get("metrics", [])
    if isinstance(metrics, list):
        for metric in metrics:
            if isinstance(metric, dict):
                metric_rows.append(
                    [
                        metric.get("metric", ""),
                        metric.get("period", ""),
                        metric.get("value", ""),
                        metric.get("units", ""),
                        metric.get("source", ""),
                        metric.get("evidence", ""),
                        metric.get("confidence", ""),
                    ]
                )
    if metric_rows:
        lines.extend(
            [
                "",
                "## Key metrics",
                table(
                    ["Metric", "Period", "Value", "Units", "Source", "Evidence", "Confidence"],
                    metric_rows,
                ),
            ]
        )

    developments = sections.get("recent_developments") or data.get("recent_developments", [])
    if isinstance(developments, list) and developments:
        lines.extend(["", "## Recent developments"])
        for dev in developments:
            lines.append(f"- {fmt(dev)}")

    relevance = sections.get("workflow_relevance") or data.get("workflow_relevance", [])
    if isinstance(relevance, list) and relevance:
        lines.extend(["", "## Relevance for this workflow"])
        for item in relevance:
            lines.append(f"- {fmt(item)}")
    elif relevance:
        lines.extend(["", "## Relevance for this workflow", fmt(relevance)])

    risks = (
        sections.get("risks_gaps_flags")
        or data.get("risks_gaps_flags")
        or data.get("data_quality_flags", [])
    )
    if isinstance(risks, list) and risks:
        lines.extend(["", "## Risks, gaps, and evidence flags"])
        for risk in risks:
            lines.append(f"- {fmt(risk)}")
    elif risks:
        lines.extend(["", "## Risks, gaps, and evidence flags", fmt(risks)])

    sources = data.get("sources", [])
    if isinstance(sources, list) and sources:
        source_rows: list[list[Any]] = []
        for source in sources:
            if isinstance(source, dict):
                source_rows.append(
                    [
                        source.get("source_id", ""),
                        source.get("source_name", ""),
                        source.get("source_type", ""),
                        source.get("as_of_date", ""),
                        source.get("freshness_status", ""),
                        source.get("source_location", ""),
                    ]
                )
        lines.extend(
            [
                "",
                "## Source notes",
                table(["ID", "Source", "Type", "As of", "Freshness", "Location"], source_rows),
            ]
        )

    next_step = data.get("recommended_next_step") or sections.get("recommended_next_step")
    if next_step:
        lines.extend(["", "## Recommended next step", fmt(next_step)])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build markdown company tearsheet from JSON")
    parser.add_argument("input_json", type=Path, help="Path to tearsheet JSON")
    parser.add_argument("output_md", type=Path, help="Output markdown path")
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("top-level json must be an object")
    args.output_md.write_text(build_markdown(data), encoding="utf-8")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
