#!/usr/bin/env python3
"""Run the deterministic 3-statement model pipeline.

Usage:
  python3 scripts/run_pipeline.py path/to/plan.json [--print-report] [--no-support-note]

Creates relative to the current working directory:
  output/model.xlsx
  output/plan.json
  output/run_log.json
  optional output/support_note.md support note unless --no-support-note is used
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PLUGIN_ROOT = SKILL_ROOT.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from skill_core import (
    assumption_rows,
    check_rows,
    evaluate_hard_failures_and_warnings,
    model_status,
    normalize_plan,
    p0_handoff,
    run_scenarios,
    run_sensitivities,
    source_rows,
    summarize_result,
    summary_rows,
    to_model_rows,
)
from validate_plan import validate
from xlsx_writer import write_xlsx  # noqa: E402

from shared.artifacts import (  # noqa: E402
    artifact_paths as shared_artifact_paths,
)
from shared.artifacts import (
    build_run_log,
    write_run_log_bundle,
)
from shared.artifacts import (
    output_manifest as shared_output_manifest,
)
from shared.workbook_artifacts import three_statement_cover_rows  # noqa: E402


def artifact_paths(output_dir: Path) -> dict[str, str]:
    return shared_artifact_paths(
        output_dir,
        {
            "workbook": "model.xlsx",
            "plan": "plan.json",
            "run_log": "run_log.json",
            "support_note": "support_note.md",
            "legacy_report": "report.md",
            "manifest": "manifest.json",
        },
    )


def output_manifest(
    output_dir: Path,
    *,
    support_note_enabled: bool,
    legacy_report_enabled: bool,
    written: set[str],
) -> list[dict[str, Any]]:
    paths = artifact_paths(output_dir)
    optional = set()
    if not support_note_enabled:
        optional.add("support_note")
    if not legacy_report_enabled:
        optional.add("legacy_report")
    return shared_output_manifest(
        paths,
        optional=optional,
        written=written,
        descriptions={
            "workbook": "Deterministic long-format values workbook.",
            "plan": "Normalized plan actually used by the pipeline.",
            "run_log": "Status, warnings, hard failures, checks, and handoff payload.",
            "support_note": "Markdown support note for review, renderer input, or audit.",
            "legacy_report": "Legacy report.md copy, written only when explicitly requested.",
            "manifest": "Machine-readable output manifest.",
        },
        artifact_roles={
            "workbook": "primary_human_deliverable",
            "support_note": "narrative_support",
            "legacy_report": "narrative_support",
            "plan": "machine_support",
            "run_log": "machine_support",
            "manifest": "machine_support",
        },
        hidden_unless_requested={"support_note", "legacy_report", "plan", "run_log", "manifest"},
    )


def write_manifest(output_dir: Path, run_log: dict[str, Any]) -> None:
    (output_dir / "manifest.json").write_text(
        json.dumps({"outputs": run_log.get("output_manifest", [])}, indent=2),
        encoding="utf-8",
    )


def write_blocked_run_log(
    output_dir: Path,
    errors: list[str],
    *,
    support_note_enabled: bool = True,
    legacy_report_enabled: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = artifact_paths(output_dir)
    run_log: dict[str, Any] = build_run_log(
        hard_failures=[{"code": "validation_error", "message": error} for error in errors],
        warnings=[],
        outputs=paths,
        output_manifest_rows=output_manifest(
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=legacy_report_enabled,
            written={"run_log", "manifest"},
        ),
        checks={"validation_errors": errors},
        p0_handoff={
            "model_status": "not-decision-ready",
            "major_caveats": errors,
            "paths": paths,
        },
        model_status="not-decision-ready",
    )
    write_run_log_bundle(output_dir, run_log)
    return run_log


def format_money(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, str):
        return value
    try:
        val = float(value)
    except Exception:
        return str(value)
    if math.isinf(val) or math.isnan(val):
        return "n/m"
    return f"{val:,.1f}"


def format_pct(value: Any) -> str:
    try:
        val = float(value)
    except Exception:
        return "n/a"
    if math.isinf(val) or math.isnan(val):
        return "n/m"
    return f"{val * 100.0:,.1f}%"


def render_report(
    plan: dict[str, Any],
    scenario_outputs: dict[str, dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
    run_log: dict[str, Any],
) -> str:
    meta = plan.get("meta", {})
    units = meta.get("units", "")
    lines: list[str] = []
    lines.append(f"# Three-Statement Operating Model - {meta.get('company_name', 'Company')}")
    lines.append("")
    lines.append(f"**Model status:** `{run_log['model_status']}`  ")
    lines.append(f"**Workbook mode:** `{run_log['workbook_mode']}`  ")
    lines.append("**Artifact level:** `deterministic_export`  ")
    lines.append(f"**As of:** {meta.get('as_of_date', 'n/a')}  ")
    lines.append(
        f"**Basis:** {meta.get('accounting_basis', 'unspecified')} | {meta.get('currency', '')} | {units}"
    )
    lines.append("")
    lines.append(
        "> This export is a deterministic values workbook, not a fully linked banker formula workbook. Use the run log and QA checks before relying on it for a decision."
    )
    lines.append("")
    lines.append("## Scenario summary")
    lines.append("")
    lines.append(
        "| Scenario | Final Period | Revenue | EBITDA | EBITDA Margin | FCF | Ending Cash | Ending Debt | Liquidity Trough | Peak Net Leverage |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for scenario in ["base", "downside", "upside"]:
        result = scenario_outputs.get(scenario)
        if not result:
            continue
        s = summarize_result(result)
        lines.append(
            f"| {scenario.title()} | {s['final_period']} | {format_money(s['final_revenue'])} | {format_money(s['final_ebitda'])} | {format_pct(s['final_ebitda_margin'])} | {format_money(s['final_fcf'])} | {format_money(s['ending_cash'])} | {format_money(s['ending_debt'])} | {format_money(s['liquidity_trough'])} | {format_money(s['peak_net_leverage'])}x |"
        )
    lines.append("")

    base = scenario_outputs.get("base")
    if base:
        periods = base["periods"]
        is_ = base["income_statement"]
        cf = base["cash_flow_statement"]
        wc = base["working_capital"]
        debt = base["debt"]
        lines.append("## Base case operating read-through")
        lines.append("")
        lines.append("| Metric | First Forecast Period | Final Forecast Period | Senior read |")
        lines.append("|---|---:|---:|---|")
        first = 0
        last = len(periods) - 1
        first_margin = (
            is_["ebitda"][first] / is_["revenue"][first] if is_["revenue"][first] else 0.0
        )
        final_margin = is_["ebitda"][last] / is_["revenue"][last] if is_["revenue"][last] else 0.0
        fcf_first = cf["cash_flow_from_operations"][first] - cf["capex"][first]
        fcf_last = cf["cash_flow_from_operations"][last] - cf["capex"][last]
        lines.append(
            f"| Revenue | {format_money(is_['revenue'][first])} | {format_money(is_['revenue'][last])} | Check whether growth is supported by market, capacity, pipeline, and pricing evidence. |"
        )
        lines.append(
            f"| EBITDA margin | {format_pct(first_margin)} | {format_pct(final_margin)} | Margin expansion must be tied to mix, utilization, pricing, and cost discipline, not just spreadsheet leverage. |"
        )
        lines.append(
            f"| Free cash flow | {format_money(fcf_first)} | {format_money(fcf_last)} | FCF equals CFO less capex; watch working capital and reinvestment drag. |"
        )
        lines.append(
            f"| Net working capital | {format_money(wc['nwc'][first])} | {format_money(wc['nwc'][last])} | DSO/DIO/DPO assumptions drive cash conversion. |"
        )
        lines.append(
            f"| Debt | {format_money(debt['ending_debt'][first])} | {format_money(debt['ending_debt'][last])} | Cash sweep and required amortization determine deleveraging pace. |"
        )
        lines.append("")

    lines.append("## QA and decision posture")
    lines.append("")
    hard = run_log.get("hard_failures", [])
    warns = run_log.get("warnings", [])
    if hard:
        lines.append("### Hard failures")
        for item in hard:
            lines.append(f"- **{item.get('code')}**: {item.get('message')}")
    else:
        lines.append("- No hard failures were generated by the machine checks.")
    if warns:
        lines.append("")
        lines.append("### Warnings")
        for item in warns:
            lines.append(f"- **{item.get('code')}**: {item.get('message')}")
    else:
        lines.append("- No warnings were generated by the senior-review heuristics.")
    lines.append("")

    if sensitivity_rows:
        lines.append("## Sensitivity outputs")
        lines.append("")
        lines.append(
            "| Case | Final Revenue | Final EBITDA | Final FCF | Ending Cash | Liquidity Trough |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|")
        for row in sensitivity_rows[:10]:
            lines.append(
                f"| {row['case']} | {format_money(row['final_revenue'])} | {format_money(row['final_ebitda'])} | {format_money(row['final_fcf'])} | {format_money(row['ending_cash'])} | {format_money(row['liquidity_trough'])} |"
            )
        lines.append("")

    lines.append("## Source posture")
    lines.append("")
    sources = plan.get("source_basis", [])
    if sources:
        lines.append("| Source | Evidence Label | As Of | Confidence | Covers |")
        lines.append("|---|---|---:|---|---|")
        for src in sources:
            covers = ", ".join(src.get("covers", []))
            lines.append(
                f"| {src.get('label', src.get('id', 'source'))} | {src.get('evidence_label', '')} | {src.get('as_of_date', '')} | {src.get('confidence', '')} | {covers} |"
            )
    else:
        lines.append("No source basis was supplied.")
    lines.append("")

    lines.append("## Files produced")
    lines.append("")
    lines.append(
        "- `output/model.xlsx` - long-format deterministic model export with scenario rows, statements, schedules, checks, assumptions, sources, and sensitivities."
    )
    lines.append("- `output/plan.json` - normalized plan actually used.")
    lines.append(
        "- `output/run_log.json` - model status, warnings, hard failures, checks, and P0 handoff."
    )
    lines.append("- `output/support_note.md` - support note when enabled.")
    lines.append("")
    return "\n".join(lines)


def run_pipeline(
    plan_path: Path,
    print_report: bool,
    write_support_note: bool,
    write_legacy_report_md: bool,
) -> dict[str, Any]:
    skill_root = Path(__file__).resolve().parents[1]
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    normalized = normalize_plan(plan, skill_root)

    output_dir = Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    scenario_outputs = run_scenarios(normalized)
    sensitivity_rows = run_sensitivities(normalized)
    hard_failures, warnings, checks = evaluate_hard_failures_and_warnings(
        normalized, scenario_outputs
    )
    status = model_status(hard_failures, warnings, normalized)
    output_paths = artifact_paths(output_dir)
    written = {"workbook", "plan", "run_log", "manifest"}
    if write_support_note:
        written.add("support_note")
    if write_legacy_report_md:
        written.add("legacy_report")

    model_rows: list[dict[str, Any]] = []
    for scenario in ["base", "downside", "upside"]:
        model_rows.extend(to_model_rows(normalized, scenario_outputs[scenario]))

    run_log: dict[str, Any] = build_run_log(
        hard_failures=hard_failures,
        warnings=warnings,
        outputs=output_paths,
        output_manifest_rows=output_manifest(
            output_dir,
            support_note_enabled=write_support_note,
            legacy_report_enabled=write_legacy_report_md,
            written=written,
        ),
        source_basis=normalized.get("source_basis", []),
        assumptions={
            "timeline": normalized.get("timeline", {}),
            "accounting_basis": normalized.get("meta", {}).get("accounting_basis"),
            "units": normalized.get("meta", {}).get("units"),
            "cash_sweep": normalized.get("debt", {}).get("cash_sweep", {}),
        },
        checks=checks,
        p0_handoff=p0_handoff(normalized, scenario_outputs, hard_failures, warnings, status),
        model_status=status,
        extra={
            "primary_human_deliverable": output_paths["workbook"],
            "support_artifacts": [
                output_paths[key] for key in output_paths if key != "workbook" and key in written
            ],
        },
    )

    report = render_report(normalized, scenario_outputs, sensitivity_rows, run_log)

    sheets = {
        "Cover": three_statement_cover_rows(normalized, scenario_outputs, run_log),
        "Summary": summary_rows(normalized, scenario_outputs),
        "Model": model_rows,
        "Sensitivities": sensitivity_rows,
        "Checks": check_rows(scenario_outputs),
        "Assumptions": assumption_rows(normalized),
        "Sources": source_rows(normalized),
        "Run_Log": [
            {"field": "model_status", "value": status},
            {"field": "workbook_mode", "value": "deterministic_export"},
            {"field": "hard_failure_count", "value": len(hard_failures)},
            {"field": "warning_count", "value": len(warnings)},
        ],
    }
    write_xlsx(output_dir / "model.xlsx", sheets)
    (output_dir / "plan.json").write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    write_run_log_bundle(output_dir, run_log)
    if write_support_note:
        (output_dir / "support_note.md").write_text(report, encoding="utf-8")
    if write_legacy_report_md:
        (output_dir / "report.md").write_text(report, encoding="utf-8")

    if print_report:
        print("---BEGIN THREE STATEMENT MODEL SUPPORT NOTE---")
        print(report)
        print("---END THREE STATEMENT MODEL SUPPORT NOTE---")
    return run_log


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic 3-statement model pipeline")
    parser.add_argument("plan_json", help="Path to plan.json")
    parser.add_argument("--print-report", action="store_true", help="Print support note to stdout")
    parser.add_argument(
        "--no-support-note", action="store_true", help="Do not write output/support_note.md"
    )
    parser.add_argument(
        "--no-report-md", action="store_true", help="Deprecated alias for --no-support-note"
    )
    parser.add_argument(
        "--write-report-md",
        action="store_true",
        help="Write legacy output/report.md in addition to support_note.md. Off by default.",
    )
    args = parser.parse_args()
    write_support_note = not (args.no_support_note or args.no_report_md)

    plan_path = Path(args.plan_json)
    output_dir = Path.cwd() / "output"
    if not plan_path.exists():
        print(f"Plan not found: {plan_path}", file=sys.stderr)
        write_blocked_run_log(
            output_dir,
            [f"Plan not found: {plan_path}"],
            support_note_enabled=write_support_note,
            legacy_report_enabled=args.write_report_md,
        )
        return 1
    validation_errors = validate(str(plan_path))
    if validation_errors:
        write_blocked_run_log(
            output_dir,
            validation_errors,
            support_note_enabled=write_support_note,
            legacy_report_enabled=args.write_report_md,
        )
        print("Plan validation FAILED:", file=sys.stderr)
        for item in validation_errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    try:
        run_log = run_pipeline(
            plan_path,
            args.print_report,
            write_support_note,
            args.write_report_md,
        )
    except Exception as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        write_blocked_run_log(
            output_dir,
            [f"Pipeline failed: {exc}"],
            support_note_enabled=write_support_note,
            legacy_report_enabled=args.write_report_md,
        )
        return 1
    if run_log.get("hard_failures"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
