#!/usr/bin/env python3
"""Run the deterministic DCF pipeline."""

from __future__ import annotations

import argparse
import json
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

from skill_core import (  # noqa: E402
    build_p0_handoff,
    build_workbook_sheets,
    compute_checks,
    determine_model_status,
    load_json,
    normalize_plan,
    render_report,
    run_scenario,
    run_sensitivities,
    validate_plan_structure,
    write_json,
)
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
from shared.workbook_artifacts import dcf_cover_rows  # noqa: E402


def _artifact_paths(output_dir: Path) -> dict[str, str]:
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


def _output_manifest(
    output_dir: Path,
    *,
    support_note_enabled: bool,
    legacy_report_enabled: bool,
    written: set[str],
) -> list[dict[str, Any]]:
    paths = _artifact_paths(output_dir)
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


def _write_manifest(output_dir: Path, run_log: dict[str, Any]) -> None:
    write_json(output_dir / "manifest.json", {"outputs": run_log.get("output_manifest", [])})


def _blocked_run_log(
    errors: list[str],
    output_dir: Path,
    *,
    support_note_enabled: bool = True,
    legacy_report_enabled: bool = False,
) -> dict[str, Any]:
    paths = _artifact_paths(output_dir)
    return build_run_log(
        hard_failures=errors,
        warnings=[],
        outputs=paths,
        output_manifest_rows=_output_manifest(
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=legacy_report_enabled,
            written={"run_log", "manifest"},
        ),
        checks={"validation_errors": errors},
        model_status="not-decision-ready",
        p0_handoff={
            "selected_valuation_range": {},
            "scenarios": {},
            "wacc_and_terminal_assumptions": {},
            "key_value_drivers": [],
            "major_caveats": errors,
            "model_status": "not-decision-ready",
            "paths": paths,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DCF deterministic export pipeline")
    parser.add_argument("plan_path", help="Path to plan.json")
    parser.add_argument(
        "--output-dir",
        default=str(SKILL_ROOT / "output"),
        help="Output directory; default skill_root/output",
    )
    parser.add_argument(
        "--print-report", action="store_true", help="Print support note between clear markers"
    )
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
    support_note_enabled = not (args.no_support_note or args.no_report_md)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        raw_plan = load_json(args.plan_path)
    except FileNotFoundError:
        errors = [f"plan file not found: {args.plan_path}"]
        run_log = _blocked_run_log(
            errors,
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=args.write_report_md,
        )
        write_run_log_bundle(output_dir, run_log)
        print("BLOCKED DCF PIPELINE")
        for e in errors:
            print(f"- {e}")
        return 1
    except json.JSONDecodeError as exc:
        errors = [f"invalid JSON: line {exc.lineno}, column {exc.colno}: {exc.msg}"]
        run_log = _blocked_run_log(
            errors,
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=args.write_report_md,
        )
        write_run_log_bundle(output_dir, run_log)
        print("BLOCKED DCF PIPELINE")
        for e in errors:
            print(f"- {e}")
        return 1
    except Exception as exc:
        errors = [f"could not read plan: {exc}"]
        run_log = _blocked_run_log(
            errors,
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=args.write_report_md,
        )
        write_run_log_bundle(output_dir, run_log)
        print("BLOCKED DCF PIPELINE")
        for e in errors:
            print(f"- {e}")
        return 1

    validation_errors = validate_plan_structure(raw_plan)
    if validation_errors:
        run_log = _blocked_run_log(
            validation_errors,
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=args.write_report_md,
        )
        write_run_log_bundle(output_dir, run_log)
        print("BLOCKED DCF PIPELINE")
        for e in validation_errors:
            print(f"- {e}")
        return 1

    plan = normalize_plan(raw_plan, SKILL_ROOT)
    write_json(output_dir / "plan.json", plan)

    scenario_results: dict[str, dict[str, Any]] = {}
    execution_errors: list[str] = []
    for scenario_name in ["base", "downside", "upside"]:
        try:
            scenario_results[scenario_name] = run_scenario(plan, scenario_name)
        except Exception as exc:
            execution_errors.append(f"scenario {scenario_name} failed: {exc}")

    try:
        sensitivity_result = run_sensitivities(plan)
    except Exception as exc:
        sensitivity_result = {
            "rows": [],
            "directionality": {
                "passed": False,
                "details": [{"check": "sensitivity run", "passed": False, "detail": str(exc)}],
            },
        }
        execution_errors.append(f"sensitivities failed: {exc}")

    checks = compute_checks(plan, scenario_results, sensitivity_result)
    if execution_errors:
        checks.setdefault("hard_failures", [])
        checks["hard_failures"].extend(execution_errors)
        # Deduplicate while preserving order.
        checks["hard_failures"] = list(dict.fromkeys(checks["hard_failures"]))

    hard_failures = checks.get("hard_failures", [])
    warnings = checks.get("warnings", [])
    model_status = determine_model_status(plan, hard_failures, warnings)

    assumptions = {
        "company": plan.get("meta", {}).get("company"),
        "model_type": plan.get("meta", {}).get("model_type"),
        "valuation_date": plan.get("meta", {}).get("valuation_date"),
        "horizon_years": plan.get("timeline", {}).get("horizon_years"),
        "terminal_method": plan.get("terminal_value", {}).get("method"),
        "cash_flow_basis": plan.get("forecast", {}).get("cash_flow_basis"),
    }

    p0_handoff = build_p0_handoff(
        plan, scenario_results, sensitivity_result, model_status, warnings, output_dir
    )
    outputs = _artifact_paths(output_dir)
    written = {"workbook", "plan", "run_log", "manifest"}
    if support_note_enabled:
        written.add("support_note")
    if args.write_report_md:
        written.add("legacy_report")
    run_log = build_run_log(
        hard_failures=hard_failures,
        warnings=warnings,
        outputs=outputs,
        output_manifest_rows=_output_manifest(
            output_dir,
            support_note_enabled=support_note_enabled,
            legacy_report_enabled=args.write_report_md,
            written=written,
        ),
        source_basis=plan.get("source_basis", []),
        assumptions=assumptions,
        checks=checks,
        p0_handoff=p0_handoff,
        model_status=model_status,
        extra={
            "primary_human_deliverable": outputs["workbook"],
            "support_artifacts": [
                outputs[key] for key in outputs if key != "workbook" and key in written
            ],
        },
    )

    workbook_sheets = {
        "Cover": dcf_cover_rows(plan, scenario_results, sensitivity_result, checks, run_log),
        **build_workbook_sheets(plan, scenario_results, sensitivity_result, checks, run_log),
    }
    write_xlsx(output_dir / "model.xlsx", workbook_sheets)
    write_run_log_bundle(output_dir, run_log)

    report = render_report(plan, scenario_results, checks, run_log)
    if support_note_enabled:
        (output_dir / "support_note.md").write_text(report, encoding="utf-8")
    if args.write_report_md:
        (output_dir / "report.md").write_text(report, encoding="utf-8")

    if args.print_report:
        print("---DCF_MODEL_SUPPORT_NOTE_START---")
        print(report.rstrip())
        print("---DCF_MODEL_SUPPORT_NOTE_END---")
    else:
        print(f"DCF pipeline complete. model_status={model_status}. Output: {output_dir}")

    return 0 if not hard_failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
