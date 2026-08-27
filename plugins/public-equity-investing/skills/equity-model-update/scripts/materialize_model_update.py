#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_update_core import materialize, output_paths
from model_update_dates import parse_date
from model_update_io import write_run_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize equity-model-update source-to-model artifacts from a supplied CSV."
    )
    parser.add_argument("input_csv", type=Path, help="CSV with source/model mapping rows.")
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory.")
    parser.add_argument(
        "--run-date",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="Run date used by freshness checks, YYYY-MM-DD.",
    )
    parser.add_argument("--stale-days", type=int, default=45, help="Stale threshold in days.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_date = parse_date(args.run_date)
    if run_date is None:
        print("ERROR: --run-date must be parseable as YYYY-MM-DD")
        return 1
    try:
        return materialize(args.input_csv, args.out, run_date, args.stale_days)
    except Exception as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        write_run_log(
            args.out / "run_log.json",
            status="failed",
            input_path=args.input_csv,
            row_count=0,
            outputs=output_paths(args.out),
            warnings=[],
            failures=[str(exc)],
        )
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
