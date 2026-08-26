#!/usr/bin/env python3
"""Validate plan.json for the earnings deep dive pipeline.

This validator is intentionally strict on *structure* and *mode gating*,
while allowing values to be 'MISSING' to preserve no-hallucination discipline.

Exit codes:
  0 = valid (may still have warnings)
  1 = errors found
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

if __name__ == "__main__" and any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
    print("Usage: python scripts/validate_plan.py plan.json")
    print("Validate an earnings deep-dive plan.json.")
    raise SystemExit(0)

try:
    from .utils.io_utils import read_json, write_text
    from .utils.validation_utils import is_missing
except ImportError:
    from utils.io_utils import read_json, write_text
    from utils.validation_utils import is_missing


def _p(x: Any) -> str:
    return str(x)


def validate_plan(plan: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    # Required top-level keys
    for key in ["event", "inputs", "outputs"]:
        if key not in plan:
            errors.append(f"Missing top-level key: '{key}'")

    if errors:
        return {"errors": errors, "warnings": warnings}

    event = plan.get("event", {})
    inputs = plan.get("inputs", {})
    outputs = plan.get("outputs", {})
    controls = plan.get("controls", {})

    # Event fields (presence)
    for key in ["ticker", "fiscal_period", "event_date", "timezone", "base_currency", "base_scale"]:
        if key not in event:
            errors.append(f"event.{key} is required")

    # Inputs: artifact index
    if "artifact_index_csv" not in inputs:
        warnings.append(
            "inputs.artifact_index_csv missing; recommend recording ArtifactIndex.csv for audit"
        )

    # Inputs: normalized
    normalized = inputs.get("normalized", {})
    for k in ["metrics_csv", "estimates_csv", "guidance_csv", "quotes_csv", "driver_updates_csv"]:
        if k not in normalized:
            errors.append(f"inputs.normalized.{k} is required (path)")

    # Outputs
    if "output_dir" not in outputs:
        errors.append("outputs.output_dir is required")

    render = outputs.get("render", {})
    if not isinstance(render, dict):
        errors.append("outputs.render must be an object")

    model_update = outputs.get("model_update", {})
    if model_update.get("enabled"):
        mode = model_update.get("mode", "apply")
        model = inputs.get("model", {})
        prior = model.get("prior_model_xlsx")
        driver_reg = model.get("driver_registry_csv")

        if mode not in ("apply", "packet"):
            errors.append("outputs.model_update.mode must be 'apply' or 'packet'")

        if mode == "apply":
            if is_missing(prior):
                errors.append(
                    "Model update mode=apply requires inputs.model.prior_model_xlsx (or set mode=packet)"
                )
            if is_missing(driver_reg):
                errors.append(
                    "Model update mode=apply requires inputs.model.driver_registry_csv (or set mode=packet)"
                )

        # Output registry needed only if diff enabled
        if model_update.get("write_diff"):
            out_reg = model.get("output_registry_csv")
            if is_missing(out_reg):
                warnings.append(
                    "Diff requested but inputs.model.output_registry_csv is MISSING; diff will include drivers only"
                )

    # Controls sanity
    if controls.get("require_source_tags") is False:
        warnings.append(
            "controls.require_source_tags=false conflicts with skill MUST rules; expect refusal or forced true"
        )

    return {"errors": errors, "warnings": warnings}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_plan.py plan.json")
        return 1

    plan_path = sys.argv[1]
    try:
        plan = read_json(plan_path)
    except Exception as e:
        print(f"ERROR: failed to read plan: {e}")
        return 1

    result = validate_plan(plan)
    errors = result["errors"]
    warnings = result["warnings"]

    report_lines: list[str] = []
    report_lines.append("# Plan Validation Report\n")
    report_lines.append(f"Plan: `{plan_path}`\n")

    if warnings:
        report_lines.append("## Warnings\n")
        for w in warnings:
            report_lines.append(f"- {w}")
        report_lines.append("")

    if errors:
        report_lines.append("## Errors\n")
        for e in errors:
            report_lines.append(f"- {e}")
        report_lines.append("")

    report_text = "\n".join(report_lines)

    # Write to output folder if available
    out_dir = None
    try:
        out_dir = plan.get("outputs", {}).get("output_dir")
    except Exception:
        out_dir = None

    if out_dir:
        report_path = Path(out_dir) / "audit" / "ValidationReport_Plan.md"
        write_text(report_text, str(report_path))

    # Console summary
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print("\nPlan is NOT valid.")
        return 1

    print("Plan is valid (warnings may exist).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
