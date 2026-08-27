#!/usr/bin/env python3
"""Render a standalone Public Equity Investing dashboard HTML file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PLUGIN_ROOT))

from shared.dashboard.qa import load_payload, validate_payload  # noqa: E402
from shared.dashboard.renderer import render_dashboard  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", help="Path to dashboard payload JSON.")
    parser.add_argument("output", help="Path to write standalone HTML.")
    parser.add_argument(
        "--profile",
        choices=["draft", "production"],
        default="production",
        help="Validation profile. Rendering defaults to production because HTML is the user-facing artifact.",
    )
    parser.add_argument("--qa-json", help="Optional path to write validation report JSON.")
    args = parser.parse_args()

    payload = load_payload(args.payload)
    report = validate_payload(payload, profile=args.profile)
    if args.qa_json:
        qa_path = Path(args.qa_json)
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        qa_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["hard_failures"]:
        for failure in report["hard_failures"]:
            print(f"failure: {failure}", file=sys.stderr)
        return 1

    html = render_dashboard(payload, validate=False)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    for warning in report["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
