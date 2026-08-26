"""Artifact packaging and QC script regressions for Public Equity Investing."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shared.artifact_packager import artifact_item, write_artifact_manifest  # noqa: E402

DECK_QC = ROOT / "skills" / "deck-report-qc" / "scripts" / "inspect_deck_report.py"


class ArtifactPackagingAndQCTests(unittest.TestCase):
    def test_support_formats_cannot_be_primary_without_explicit_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir)
            primary = out / "scan.json"
            primary.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_artifact_manifest(out, "unit-test", "html_report", primary)

    def test_deck_qc_script_heroes_html_and_hides_support_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            source = tmp / "memo.txt"
            source.write_text(
                "Revenue was $100m in FY2026. EBITDA was $20m. Source: company filing as of 2026-05-01. "
                "Revenue was $105m in FY2026 on another page without clear reconciliation.",
                encoding="utf-8",
            )
            outdir = tmp / "qc"
            result = subprocess.run(
                [sys.executable, str(DECK_QC), str(source), "--outdir", str(outdir)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            report = outdir / "public_equity_investing_deck_qc_report.html"
            manifest = json.loads((outdir / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(report.exists())
            self.assertEqual(
                report.resolve(), Path(manifest["primary_human_deliverable"]).resolve()
            )
            self.assertEqual("html_report", manifest["artifact_mode"])
            self.assertFalse(manifest["support_artifacts_user_visible_default"])
            self.assertTrue((outdir / "support" / "qc_issue_log.csv").exists())
            self.assertTrue((outdir / "support" / "repeated_number_tieout.csv").exists())
            for item in manifest["support_artifacts"]:
                self.assertFalse(item["user_visible_default"])
                self.assertTrue(item["support_reason"])
                self.assertNotEqual("human_deliverable", item["role"])

    def test_deck_qc_finalize_promotes_polished_report_and_reconciles_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            source = tmp / "memo.txt"
            source.write_text(
                "Revenue was $100m in FY2026. Revenue was $105m in FY2026.",
                encoding="utf-8",
            )
            output_dir = tmp / "completed_review"
            scan_dir = output_dir / "qc_support"
            scan = subprocess.run(
                [sys.executable, str(DECK_QC), str(source), "--outdir", str(scan_dir)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, scan.returncode, scan.stderr + scan.stdout)
            self.assertTrue((scan_dir / "logs" / "deck_report_qc_dashboard_contract.json").exists())

            final_report = output_dir / "public_equity_investing_deck_qc_report.html"
            final_report.parent.mkdir(parents=True, exist_ok=True)
            final_report.write_text(
                "<html><body>Final reviewed QC report</body></html>", encoding="utf-8"
            )
            review_record = output_dir / "qc_review_record.json"
            review_record.write_text(
                json.dumps(
                    {
                        "status": "partial",
                        "reason": "Internal QC completed; primary source confirmation remains open.",
                        "completed_reviews": [
                            "PDF pages rendered and material pages inspected",
                            "Supporting workbook valuation tabs inspected",
                        ],
                        "missing_inputs": ["Dated external market-data source"],
                    }
                ),
                encoding="utf-8",
            )
            finalize = subprocess.run(
                [
                    sys.executable,
                    str(DECK_QC),
                    "--finalize",
                    "--outdir",
                    str(output_dir),
                    "--scan-dir",
                    str(scan_dir),
                    "--primary-report",
                    str(final_report),
                    "--review-record",
                    str(review_record),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, finalize.returncode, finalize.stderr + finalize.stdout)

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(
                final_report.resolve(), Path(manifest["primary_human_deliverable"]).resolve()
            )
            status = manifest["blocked_or_partial_status"]
            self.assertEqual(["Dated external market-data source"], status["missing_inputs"])
            self.assertIn(
                "Supporting workbook valuation tabs inspected", status["completed_reviews"]
            )
            self.assertFalse((scan_dir / "public_equity_investing_deck_qc_report.html").exists())
            self.assertFalse((scan_dir / "manifest.json").exists())
            self.assertFalse(
                (scan_dir / "logs" / "deck_report_qc_dashboard_contract.json").exists()
            )
            support_paths = {Path(item["path"]).name for item in manifest["support_artifacts"]}
            self.assertIn("scan.json", support_paths)
            self.assertIn("qc_review_record.json", support_paths)

    def test_workbook_manifest_support_artifact_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir)
            workbook = out / "model.xlsx"
            workbook.write_bytes(b"placeholder")
            run_log = out / "run_log.json"
            run_log.write_text("{}", encoding="utf-8")
            manifest = write_artifact_manifest(
                out,
                "unit-test",
                "workbook",
                workbook,
                support_artifacts=[
                    artifact_item(
                        run_log, "support_artifact", "json", "Run log", False, True, "Audit support"
                    )
                ],
            )
            self.assertEqual(str(workbook), manifest["primary_human_deliverable"])
            self.assertEqual("primary_human_deliverable", manifest["first_read"]["role"])
            self.assertEqual(
                "only_briefly_unless_requested",
                manifest["final_response_guidance"]["mention_support_artifacts"],
            )


if __name__ == "__main__":
    unittest.main()
