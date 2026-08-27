"""Monitoring, catalyst, and event contract tests for public-equity PM workflows."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicEquityMonitoringContractTests(unittest.TestCase):
    def test_thesis_tracker_has_portfolio_monitoring_contract(self) -> None:
        text = (
            (ROOT / "skills" / "thesis-tracker" / "SKILL.md").read_text(encoding="utf-8")
            + "\n"
            + (ROOT / "skills" / "thesis-tracker" / "references" / "thesis-schema.md").read_text(
                encoding="utf-8"
            )
        ).lower()
        for phrase in [
            "portfolio monitoring mode",
            "benchmark_weight",
            "active_weight",
            "portfolio_role",
            "index_etf_flow_exposure",
            "position_action",
            "company_thesis_status",
            "security_thesis_readiness",
            "threshold_origin",
            "threshold_approval_status",
            "status_override_rationale_if_applicable",
            "append-only",
            "re-underwrite",
        ]:
            self.assertIn(phrase, text)

    def test_catalyst_calendar_has_index_etf_decision_pressure_contract(self) -> None:
        text = (
            (ROOT / "skills" / "catalyst-calendar" / "SKILL.md").read_text(encoding="utf-8")
            + "\n"
            + (
                ROOT
                / "skills"
                / "catalyst-calendar"
                / "references"
                / "catalyst-taxonomy-and-fields.md"
            ).read_text(encoding="utf-8")
            + "\n"
            + (
                ROOT / "skills" / "catalyst-calendar" / "references" / "source-and-data-protocol.md"
            ).read_text(encoding="utf-8")
        ).lower()
        for phrase in [
            "decision_pressure",
            "index_rebalance",
            "passive_flow",
            "flow_vs_adv",
            "confirmed dates",
            "inferred windows",
            "do not export inferred windows as exact",
        ]:
            self.assertIn(phrase, text)

    def test_event_driven_has_passive_flow_event_contract(self) -> None:
        text = (
            (ROOT / "skills" / "event-driven-analyzer" / "SKILL.md").read_text(encoding="utf-8")
            + "\n"
            + (
                ROOT / "skills" / "event-driven-analyzer" / "references" / "source_hierarchy.md"
            ).read_text(encoding="utf-8")
            + "\n"
            + (
                ROOT / "skills" / "event-driven-analyzer" / "references" / "scenario_math.md"
            ).read_text(encoding="utf-8")
        ).lower()
        for phrase in [
            "index / etf / passive flow event",
            "flow_event",
            "flow-vs-adv",
            "trade expression menu",
            "base-rate awareness",
            "liquidity",
            "borrow",
            "exit plan",
        ]:
            self.assertIn(phrase, text)

    @unittest.skipUnless(
        importlib.util.find_spec("openpyxl"), "openpyxl required for XLSX thesis tracker smoke test"
    )
    def test_thesis_tracker_xlsx_manifest_is_primary_human_deliverable(self) -> None:
        script = ROOT / "skills" / "thesis-tracker" / "scripts" / "materialize_thesis_tracker.py"
        payload = {
            "dashboard": {
                "company_issuer": "Example Co",
                "ticker_security": "EXM",
                "direction": "long",
                "current_thesis_status": "intact",
                "conviction": "medium",
                "position_rating": "add on proof",
                "base_bull_bear_value": "$80 / $110 / $55",
                "next_catalyst": "Q2 earnings",
                "action_recommendation": "hold",
            },
            "sources": [
                {
                    "source_id": "S1",
                    "source_name": "Company release",
                    "source_type": "company filing",
                    "date_as_of": "2026-05-01",
                    "reliability": "high",
                    "used_for": "dashboard",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / "tracker_input.json"
            output_dir = tmp_path / "tracker_output"
            workbook_path = output_dir / "thesis_tracker.xlsx"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(input_path),
                    "--output-dir",
                    str(output_dir),
                    "--xlsx-out",
                    str(workbook_path),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((output_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(str(workbook_path), run_log["primary_human_deliverable"])
            self.assertEqual("workbook", run_log["artifact_mode"])
            self.assertEqual("xlsx_tracker_workbook", run_log["workbook_mode"])
            self.assertEqual(str(workbook_path), manifest["primary_human_deliverable"])
            self.assertEqual([str(workbook_path)], manifest["human_deliverables"])
            self.assertFalse(manifest["support_artifacts_user_visible_default"])

            xlsx_rows = [row for row in run_log["output_manifest"] if row["key"] == "xlsx"]
            self.assertEqual(1, len(xlsx_rows))
            self.assertEqual("primary_human_deliverable", xlsx_rows[0]["artifact_role"])
            self.assertFalse(xlsx_rows[0]["hidden_unless_requested"])
            self.assertTrue(
                all(
                    row["artifact_role"] != "primary_human_deliverable"
                    for row in run_log["output_manifest"]
                    if row["key"] != "xlsx"
                )
            )


if __name__ == "__main__":
    unittest.main()
