#!/usr/bin/env python3
"""Validate a Public Equity Investing dashboard payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PLUGIN_ROOT))

from shared.dashboard.qa import load_payload, validate_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", help="Path to dashboard payload JSON.")
    parser.add_argument(
        "--profile",
        choices=["draft", "production"],
        default="production",
        help="Validation profile. Production hard-fails missing metadata, sources, readiness, and citations.",
    )
    parser.add_argument("--json", action="store_true", help="Print full validation JSON.")
    args = parser.parse_args()

    payload = load_payload(args.payload)
    report = validate_payload(payload, profile=args.profile)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"status={report['status']}")
        for warning in report["warnings"]:
            print(f"warning: {warning}")
        for failure in report["hard_failures"]:
            print(f"failure: {failure}")
    return 1 if report["hard_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
