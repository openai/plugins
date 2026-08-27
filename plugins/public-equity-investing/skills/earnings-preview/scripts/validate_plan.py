#!/usr/bin/env python3
"""Validate a plan.json and its referenced inputs.

Exit codes:
- 0: PASS (warnings may exist)
- 1: FAIL

Writes next to the plan file:
- validation_report.json
- validation_report.md

Example:
  python scripts/validate_plan.py path/to/plan.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


SKILL_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_path", help="Path to plan.json")
    args = ap.parse_args()

    from lib.io_utils import read_json, write_json
    from lib.qa import validate_inputs, validate_plan

    plan_path = Path(args.plan_path).resolve()

    plan = read_json(plan_path)
    if not isinstance(plan, dict):
        raise SystemExit("plan.json must be a JSON object")

    errors, warnings = validate_plan(plan)
    e2, w2, _dfs = validate_inputs(plan, SKILL_ROOT)
    errors.extend(e2)
    warnings.extend(w2)

    status = "PASS" if not errors else "FAIL"

    report = {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "plan_path": str(plan_path),
    }

    out_dir = plan_path.parent
    write_json(out_dir / "validation_report.json", report)

    md_lines = [f"# Validation report ({status})", "", f"Plan: {plan_path}", ""]
    if errors:
        md_lines.append("## Errors (must fix)")
        md_lines.extend([f"- {e}" for e in errors])
        md_lines.append("")
    if warnings:
        md_lines.append("## Warnings (review)")
        md_lines.extend([f"- {w}" for w in warnings])
        md_lines.append("")

    (out_dir / "validation_report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(status)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
