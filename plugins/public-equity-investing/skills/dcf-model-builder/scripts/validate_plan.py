#!/usr/bin/env python3
"""Validate a dcf-model-builder plan.json file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from skill_core import load_json, validate_plan_structure  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DCF plan.json")
    parser.add_argument("plan_path", help="Path to plan.json")
    args = parser.parse_args()

    try:
        plan = load_json(args.plan_path)
    except FileNotFoundError:
        print(f"ERROR: plan file not found: {args.plan_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(
            f"ERROR: invalid JSON in {args.plan_path}: line {exc.lineno}, column {exc.colno}: {exc.msg}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"ERROR: could not read plan: {exc}", file=sys.stderr)
        return 1

    errors = validate_plan_structure(plan)
    if errors:
        print("INVALID DCF PLAN")
        for idx, error in enumerate(errors, start=1):
            print(f"{idx}. {error}")
        return 1

    print(f"VALID DCF PLAN: {args.plan_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
