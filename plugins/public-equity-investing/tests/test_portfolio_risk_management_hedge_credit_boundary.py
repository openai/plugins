"""Portfolio risk hedge-design helper guardrails for credit instruments."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "portfolio-risk-management" / "scripts" / "score_hedge_candidates.py"


class PortfolioRiskHedgeCreditBoundaryTests(unittest.TestCase):
    def test_credit_hedge_types_route_to_credit_markets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            input_csv = tmp / "hedges.csv"
            input_csv.write_text(
                "hedge,hedge_type,risk_hedged,exposure_fit_score,thesis_preservation_score,basis_risk,implementation_status,as_of,source,live_pricing_status,borrow_status,option_chain_status,risk_model_status\n"
                "ACME CDS,CDS,refinancing stress,5,4,entity basis,screen only,2026-05-18,user supplied,available,not_applicable,not_applicable,validated\n"
                "SPY put,option,market beta,4,4,index basis,screen only,2026-05-18,user supplied,available,not_applicable,available,validated\n",
                encoding="utf-8",
            )
            output_dir = tmp / "out"

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_csv), "--output-dir", str(output_dir)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            with (output_dir / "hedge_scorecard.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            by_hedge = {row["hedge"]: row for row in rows}
            self.assertEqual("route_to_credit_markets", by_hedge["ACME CDS"]["readiness_status"])
            self.assertEqual(
                "route_to_credit_markets", by_hedge["ACME CDS"]["implementation_status"]
            )
            self.assertIn(
                "Credit hedge construction belongs in Credit Markets",
                by_hedge["ACME CDS"]["warnings"],
            )
            self.assertNotEqual("route_to_credit_markets", by_hedge["SPY put"]["readiness_status"])


if __name__ == "__main__":
    unittest.main()
