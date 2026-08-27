#!/usr/bin/env python3
"""Build a deterministic standalone Public Equity Investing memo package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from shared.artifact_packager import (  # noqa: E402
    artifact_item,
    support_dir,
    write_artifact_manifest,
    write_report_html,
)
from shared.office_artifacts import write_structured_docx  # noqa: E402


def load_payload(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def as_rows(value: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    return fallback


def text(value: Any, fallback: str = "Not provided") -> str:
    candidate = str(value).strip() if value is not None else ""
    return candidate or fallback


def write_support_payload(outdir: Path, payload: Mapping[str, Any]) -> Path:
    target = support_dir(outdir) / "memo_plan.json"
    target.write_text(json.dumps(dict(payload), indent=2) + "\n", encoding="utf-8")
    return target


def row_lines(rows: Sequence[Mapping[str, Any]], first: str, second: str = "") -> list[str]:
    lines: list[str] = []
    for row in rows:
        left = text(row.get(first))
        right = text(row.get(second), "") if second else ""
        lines.append(f"- {left}: {right}" if right else f"- {left}")
    return lines


def memo_sections(
    payload: Mapping[str, Any],
    thesis: Sequence[Mapping[str, Any]],
    risks: Sequence[Mapping[str, Any]],
    catalysts: Sequence[Mapping[str, Any]],
    open_items: Sequence[Mapping[str, Any]],
) -> list[tuple[str, list[str]]]:
    return [
        (
            "Recommendation / Decision Ask",
            [
                text(
                    payload.get("recommendation"),
                    "Treat this as screen-grade until source support, valuation work, and thesis disconfirmers are complete.",
                ),
                f"Decision hinge: {text(payload.get('decision_hinge'), 'The thesis depends on whether the variant view is supported by evidence and priced attractively.')}",
            ],
        ),
        (
            "Executive Summary",
            [
                text(
                    payload.get("executive_summary"),
                    "Investment view, valuation skew, and source posture require review before committee or client use.",
                )
            ],
        ),
        (
            "Thesis And Evidence",
            row_lines(thesis, "point", "evidence_status"),
        ),
        (
            "Valuation / Scenario Work",
            [
                text(
                    payload.get("valuation_view"),
                    "Valuation, scenario, or estimate support was not provided in the memo input.",
                )
            ],
        ),
        (
            "Risks, Disconfirmers, And Mitigants",
            row_lines(risks, "risk", "mitigant"),
        ),
        (
            "Catalysts And Monitoring",
            row_lines(catalysts, "catalyst", "watch_item"),
        ),
        (
            "Open Items / Data Requests",
            row_lines(open_items, "item", "decision_impact"),
        ),
        (
            "Source Posture",
            [
                text(
                    payload.get("source_posture"),
                    "Sources, market data, estimates, and model outputs must be checked before decision-grade use.",
                )
            ],
        ),
    ]


def memo_markdown(title: str, sections: Sequence[tuple[str, Sequence[str]]]) -> str:
    parts = [f"# {title}"]
    for heading, paragraphs in sections:
        parts.append(f"\n## {heading}")
        parts.extend(str(paragraph) for paragraph in paragraphs)
    return "\n\n".join(parts)


def print_summary(
    json_run_log: bool, quiet: bool, summary: Mapping[str, Any], human_lines: Sequence[str]
) -> None:
    if json_run_log:
        print(json.dumps(dict(summary), indent=2))
    elif not quiet:
        for line in human_lines:
            print(line)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--primary-format",
        choices=("docx", "html"),
        default="docx",
        help="Select which human artifact is primary after format intake.",
    )
    parser.add_argument("--json-run-log", "--json", dest="json_run_log", action="store_true")
    parser.add_argument("--quiet-human-output", action="store_true")
    args = parser.parse_args()

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    payload = load_payload(args.input)
    issuer = text(payload.get("issuer") or payload.get("company"), "Subject Company")
    ticker = text(payload.get("ticker"), "")
    title = f"{issuer} Investment Memo" + (f" ({ticker})" if ticker else "")
    thesis = as_rows(
        payload.get("thesis_points"),
        [{"point": "Variant view requires source-backed support", "evidence_status": "Needs review"}],
    )
    risks = as_rows(
        payload.get("risks"),
        [{"risk": "Source/model support incomplete", "mitigant": "Run source and model gates"}],
    )
    catalysts = as_rows(
        payload.get("catalysts"),
        [{"catalyst": "Next thesis validation event not provided", "watch_item": "Confirm timing"}],
    )
    open_items = as_rows(
        payload.get("open_items"),
        [{"item": "Complete source and valuation tie-out", "decision_impact": "Blocks decision-grade use"}],
    )

    sections = memo_sections(payload, thesis, risks, catalysts, open_items)
    support = write_support_payload(out, payload)
    docx = write_structured_docx(out / "investment_memo.docx", title, sections)
    html = write_report_html(
        out / "investment_memo.html",
        title,
        memo_markdown(title, sections),
        "Public Equity Investing memo package. The selected surface is the primary deliverable.",
    )
    primary = docx if args.primary_format == "docx" else html
    companion = html if args.primary_format == "docx" else docx
    artifact_mode = "native_document" if args.primary_format == "docx" else "html_report"
    write_artifact_manifest(
        out,
        "memo-builder",
        artifact_mode,
        primary,
        companion_deliverables=[
            artifact_item(
                companion,
                "companion_deliverable",
                "html" if args.primary_format == "docx" else "native_document",
                "HTML memo companion." if args.primary_format == "docx" else "Native DOCX memo companion.",
                True,
                True,
            )
        ],
        support_artifacts=[
            artifact_item(
                support,
                "support_artifact",
                "json",
                "Memo plan and structured input payload.",
                False,
                True,
                "Memo-plan JSON is internal support material.",
            )
        ],
        blocked_or_partial_status={
            "status": "partial",
            "reason": "Requires current source, model, valuation, and thesis-disconfirmation checks before decision-grade use.",
            "missing_inputs": ["source support", "valuation/model tie-out", "PM or committee review as applicable"],
        },
    )
    summary = {
        "primary_human_deliverable": str(primary),
        "companion_deliverable": str(companion),
        "manifest": str(out / "manifest.json"),
    }
    print_summary(
        args.json_run_log,
        args.quiet_human_output,
        summary,
        [
            "Public Equity Investing memo package complete",
            f"Open first: {primary}",
            f"Companion deliverable: {companion}",
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
