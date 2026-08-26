#!/usr/bin/env python3
"""Generate a plan.json for the Earnings Preview Pack pipeline.

This is a convenience helper. You can always edit the generated plan.json by hand.

Example:
  python scripts/make_plan.py --input_dir ./input --ticker ACME --fiscal_period_id FY2026Q1 --sector_pack saas --out_dir ./run
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input_dir", required=True, help="Folder containing input CSV/XLSX files")
    p.add_argument("--ticker", required=True, help="Ticker (uppercase recommended)")
    p.add_argument("--fiscal_period_id", required=True, help="Format FY2026Q1")
    p.add_argument(
        "--sector_pack", required=True, help="One of the packs in assets/sector_kpi_packs.yaml"
    )
    p.add_argument("--out_dir", required=True, help="Folder where plan.json will be written")
    p.add_argument("--company_name", default="", help="Optional company name")
    p.add_argument(
        "--freeze_time", default="", help="Optional ISO8601 timestamp; default is now (UTC)"
    )
    p.add_argument(
        "--consensus_statistic",
        default="median",
        choices=["median", "mean", "last"],
        help="Consensus statistic",
    )
    p.add_argument("--scenario_file", default="", help="Optional scenario assumptions CSV")

    args = p.parse_args()

    from lib.io_utils import write_json

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    plan = {
        "ticker": args.ticker.strip(),
        "company_name": args.company_name.strip(),
        "fiscal_period_id": args.fiscal_period_id.strip(),
        "sector_pack": args.sector_pack.strip(),
        "freeze_time": args.freeze_time.strip() or now_utc_iso(),
        "consensus_statistic": args.consensus_statistic,
        "input_dir": str(Path(args.input_dir)),
        "output_dir": str(out_dir / "output"),
        "kpi_overrides": {"include": [], "exclude": []},
        "templates": {
            "preview_note": "assets/templates/preview_note_template.md",
        },
        "scenarios": {"file": args.scenario_file.strip()} if args.scenario_file.strip() else {},
        "options": {"enabled": False},
    }

    plan_path = out_dir / "plan.json"
    write_json(plan_path, plan)
    print(f"Wrote plan: {plan_path}")


if __name__ == "__main__":
    main()
