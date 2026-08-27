"""Populated comps workbook expectations."""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "comps-valuation" / "scripts" / "create_comps_template.py"


@unittest.skipUnless(
    importlib.util.find_spec("xlsxwriter") and importlib.util.find_spec("openpyxl"),
    "xlsxwriter and openpyxl required for populated comps workbook smoke test",
)
class CompsModelPopulatedExpectationsTests(unittest.TestCase):
    def test_supplied_csv_populates_comps_workbook_but_caps_missing_data_status(self) -> None:
        from openpyxl import load_workbook

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            input_csv = tmp / "peers.csv"
            output = tmp / "comps.xlsx"
            with input_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "ticker",
                        "company",
                        "peer_tier",
                        "price",
                        "basic_shares",
                        "debt",
                        "cash",
                        "market_data_date",
                        "revenue_ltm",
                        "revenue_cy1",
                        "ebitda_ltm",
                        "ebitda_cy1",
                        "source_name",
                        "confidence",
                        "inclusion_rationale",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "ticker": "ACME",
                        "company": "ACME Software",
                        "peer_tier": "Target",
                        "price": "100",
                        "basic_shares": "50",
                        "debt": "200",
                        "cash": "100",
                        "market_data_date": "2026-05-18",
                        "revenue_ltm": "900",
                        "revenue_cy1": "1000",
                        "ebitda_ltm": "180",
                        "ebitda_cy1": "220",
                        "source_name": "User export",
                        "confidence": "medium",
                        "inclusion_rationale": "Subject company",
                    }
                )
                writer.writerow(
                    {
                        "ticker": "PEER",
                        "company": "Peer Co",
                        "peer_tier": "Core",
                        "price": "80",
                        "basic_shares": "40",
                        "debt": "50",
                        "cash": "20",
                        "market_data_date": "2026-05-18",
                        "revenue_ltm": "700",
                        "revenue_cy1": "820",
                        "ebitda_ltm": "160",
                        "ebitda_cy1": "190",
                        "source_name": "User export",
                        "confidence": "medium",
                        "inclusion_rationale": "Close public peer",
                    }
                )
                writer.writerow(
                    {
                        "ticker": "MISS",
                        "company": "Missing Data Co",
                        "peer_tier": "Core",
                        "price": "",
                        "basic_shares": "30",
                        "debt": "40",
                        "cash": "10",
                        "market_data_date": "",
                        "revenue_ltm": "500",
                        "revenue_cy1": "",
                        "ebitda_ltm": "90",
                        "ebitda_cy1": "",
                        "source_name": "",
                        "confidence": "low",
                        "inclusion_rationale": "Needs source work",
                    }
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output",
                    str(output),
                    "--target",
                    "ACME Software",
                    "--ticker",
                    "ACME",
                    "--input-csv",
                    str(input_csv),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((tmp / "run_log.json").read_text(encoding="utf-8"))
            workbook = load_workbook(output, data_only=False)

            self.assertEqual("populated_supplied_data", run_log["workbook_mode"])
            self.assertEqual("screen-grade", run_log["model_status"])
            self.assertEqual(3, run_log["populated_peer_count"])
            self.assertTrue(run_log["missing_required_fields"])
            self.assertEqual("ACME", workbook["Universe"]["A2"].value)
            self.assertEqual("Peer Co", workbook["Universe"]["B3"].value)
            self.assertEqual(100, workbook["Market_Data"]["D2"].value)
            self.assertEqual(1000, workbook["Financials"]["E2"].value)
            self.assertTrue(str(workbook["Multiples"]["F2"].value).startswith("="))
            self.assertEqual("User export", workbook["Sources"]["D2"].value)
            self.assertNotEqual("decision-grade", run_log["model_status"])


if __name__ == "__main__":
    unittest.main()
