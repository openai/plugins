"""Scenario skew outputs for Public Equity valuation work."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "scenario-sensitivity-generator"
    / "scripts"
    / "materialize_public_equity_sensitivities.py"
)
sys.path.insert(0, str(ROOT))
OLD_TABLE = "credit_liquidity_stress"


class ScenarioSkewContractTests(unittest.TestCase):
    def run_script(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=str(SCRIPT.parent),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_price_target_scenario_outputs_pm_skew_columns(self) -> None:
        payload = {
            "base": {
                "share_price": 100,
                "upside_price_target": 140,
                "base_price_target": 118,
                "downside_price_target": 82,
                "upside_probability": 0.3,
                "base_probability": 0.5,
                "downside_probability": 0.2,
                "required_return": 0.12,
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assumptions.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_script(
                ["--input", str(path), "--tables", "price_target_scenario", "--format", "json"]
            )
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        table = data["tables"][0]
        for column in [
            "required_return",
            "expected_return_vs_hurdle",
            "downside_upside_ratio",
            "break_even_probability",
            "skew_label",
            "action_rule",
        ]:
            self.assertIn(column, table["columns"])
        self.assertTrue(any(row["scenario"] == "probability_weighted" for row in table["rows"]))

    def test_equity_liquidity_downside_replaces_credit_liquidity_table(self) -> None:
        ok = self.run_script(["--tables", "equity_liquidity_downside", "--format", "json"])
        self.assertEqual(0, ok.returncode, ok.stderr)
        self.assertIn("equity_liquidity_downside", ok.stdout)
        old = self.run_script(["--tables", OLD_TABLE, "--format", "json"])
        self.assertNotEqual(0, old.returncode)
        self.assertIn("Unknown table", old.stderr)

    def test_scenario_html_default_and_optional_dashboard_are_pm_decision_contracts(self) -> None:
        pack = (
            ROOT / "skills" / "scenario-sensitivity-generator" / "references" / "DASHBOARD_PACK.md"
        ).read_text(encoding="utf-8")
        skill = (ROOT / "skills" / "scenario-sensitivity-generator" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        intake = (ROOT / "shared" / "deliverable-intake-policy.md").read_text(encoding="utf-8")

        for phrase in [
            "expected return versus hurdle",
            "downside/upside ratio",
            "break-even probability",
            "skew label",
            "PM action",
            "Source posture",
            "Missing evidence",
            "HTML dashboard/report is the human deliverable",
            "metadata.payload_stage",
            "Use this pack only when",
            "polished standalone HTML scenario report",
            "citation rendering readable",
        ]:
            self.assertIn(phrase, pack)

        self.assertIn("../../shared/html-artifact-standard.md", skill)
        self.assertIn("polished standalone HTML scenario report", skill)
        self.assertIn("explicitly asks for a standardized dashboard", skill)
        self.assertIn("sourced discrete-event success/delay/break overlay", skill)
        self.assertIn("local headless-browser screenshots", skill)
        self.assertIn("primary transaction documents", skill)
        self.assertIn("freshest accessible market-data source", skill)
        self.assertIn("agreement-verified ticking-fee", skill)
        self.assertIn("exact assumed close or break date", skill)
        self.assertIn("lead with market-implied probabilities", skill)
        self.assertIn("probability-weighted value secondary", skill)
        self.assertIn("freshest accessible market-data source", pack)
        self.assertIn("sample probability-weighted value secondary", pack)
        self.assertIn("polished standalone HTML scenario report", intake)
        self.assertIn("public_equity_investing_dashboard.v1", skill)
        self.assertIn("references/DASHBOARD_PACK.md", skill)
        self.assertIn("JSON/Markdown/CSV/run-log support files behind the HTML dashboard", skill)

    def test_materializer_manifest_keeps_tables_as_support_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "scenario_tables.json"
            result = self.run_script(
                ["--tables", "price_target_scenario", "--format", "json", "--output", str(output)]
            )

            self.assertEqual(0, result.returncode, result.stderr)
            run_log = json.loads((Path(tmp) / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((Path(tmp) / "manifest.json").read_text(encoding="utf-8"))

            self.assertIsNone(run_log["primary_human_deliverable"])
            self.assertFalse(run_log["support_artifacts_user_visible_default"])
            self.assertFalse(manifest["support_artifacts_user_visible_default"])
            self.assertEqual("not-decision-ready", run_log["model_status"])
            self.assertIn("base.share_price", run_log["missing_required_inputs"])
            self.assertTrue(
                all(
                    row["artifact_role"] != "primary_human_deliverable"
                    for row in run_log["output_manifest"]
                )
            )

    def test_complete_but_unsourced_scenario_is_capped_at_screen_grade(self) -> None:
        payload = {
            "base": {
                "share_price": 100,
                "upside_price_target": 140,
                "base_price_target": 118,
                "downside_price_target": 82,
                "upside_probability": 0.3,
                "base_probability": 0.5,
                "downside_probability": 0.2,
                "required_return": 0.12,
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "assumptions.json"
            output = tmp_path / "scenario_tables.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                [
                    "--input",
                    str(input_path),
                    "--tables",
                    "price_target_scenario",
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((tmp_path / "run_log.json").read_text(encoding="utf-8"))
            self.assertEqual("screen-grade", run_log["model_status"])
            self.assertEqual("screen_grade", run_log["readiness_effect"])
            self.assertTrue(
                any("Source/as-of posture" in warning for warning in run_log["warnings"])
            )

    def test_invalid_probabilities_are_not_decision_ready(self) -> None:
        payload = {
            "base": {
                "share_price": 100,
                "upside_price_target": 140,
                "base_price_target": 118,
                "downside_price_target": 82,
                "upside_probability": 0.5,
                "base_probability": 0.5,
                "downside_probability": 0.5,
            },
            "metadata": {"as_of": "2026-05-18", "source_name": "User supplied scenario packet"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "assumptions.json"
            output = tmp_path / "scenario_tables.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                [
                    "--input",
                    str(input_path),
                    "--tables",
                    "price_target_scenario",
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            run_log = json.loads((tmp_path / "run_log.json").read_text(encoding="utf-8"))
            self.assertEqual("not-decision-ready", run_log["model_status"])
            self.assertIn("scenario.probabilities", run_log["missing_required_inputs"])
            self.assertNotEqual("ok", run_log["probability_validation"])

    def test_incomplete_dashboard_payload_is_draft_not_senior_review_ready(self) -> None:
        from shared.dashboard.qa import validate_payload

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_path = tmp_path / "scenario_dashboard.json"
            run_log_path = tmp_path / "run_log.json"

            result = self.run_script(
                [
                    "--tables",
                    "price_target_scenario",
                    "--format",
                    "json",
                    "--dashboard-output",
                    str(output_path),
                    "--run-log",
                    str(run_log_path),
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            dashboard_payload = json.loads(output_path.read_text(encoding="utf-8"))
            report = validate_payload(dashboard_payload, profile="draft")
            self.assertEqual("passed", report["status"], report)
            self.assertEqual("draft", dashboard_payload["metadata"]["payload_stage"])
            self.assertEqual("warn", dashboard_payload["metadata"]["citation_policy"])
            self.assertNotEqual(
                "senior_review_ready", dashboard_payload["metadata"]["readiness_posture"]
            )
            self.assertIn(
                "base.share_price", dashboard_payload["metadata"]["missing_required_inputs"]
            )

    def test_materializer_can_emit_production_dashboard_payload(self) -> None:
        from shared.dashboard.qa import validate_payload

        payload = {
            "base": {
                "share_price": 100,
                "upside_price_target": 145,
                "base_price_target": 118,
                "downside_price_target": 78,
                "upside_probability": 0.25,
                "base_probability": 0.55,
                "downside_probability": 0.20,
                "required_return": 0.12,
            },
            "metadata": {
                "ticker": "ACME",
                "issuer": "ACME Software",
                "as_of": "2026-05-18",
                "source_name": "User supplied scenario packet",
                "missing_evidence": ["Need current consensus export before circulation."],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "assumptions.json"
            output_path = tmp_path / "scenario_dashboard.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                [
                    "--input",
                    str(input_path),
                    "--tables",
                    "price_target_scenario",
                    "--format",
                    "json",
                    "--dashboard-output",
                    str(output_path),
                ]
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            dashboard_payload = json.loads(output_path.read_text(encoding="utf-8"))
            report = validate_payload(dashboard_payload, profile="production")

            self.assertEqual("public_equity_investing_dashboard.v1", dashboard_payload["kind"])
            self.assertEqual("scenario_sensitivity", dashboard_payload["mode"])
            self.assertEqual("strict", dashboard_payload["metadata"]["citation_policy"])
            self.assertEqual(
                "senior_review_ready", dashboard_payload["metadata"]["readiness_posture"]
            )
            self.assertEqual("passed", report["status"], report)
            self.assertEqual([], report["hard_failures"], report)


if __name__ == "__main__":
    unittest.main()
