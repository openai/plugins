"""Markdown sidecar policy regressions for Public Equity Investing scripts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RISK_SKILL = ROOT / "skills" / "portfolio-risk-management"
IDEA_SKILL = ROOT / "skills" / "idea-generation"
HEDGE_SKILL = ROOT / "skills" / "portfolio-risk-management"
LONG_SHORT_SKILL = ROOT / "skills" / "long-short-pitch"
SCENARIO_SKILL = ROOT / "skills" / "scenario-sensitivity-generator"


def run_command(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)


class MarkdownSupportPolicyTests(unittest.TestCase):
    def test_risk_position_sizing_writes_support_note_not_report_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "risk"
            result = run_command(
                [
                    sys.executable,
                    str(RISK_SKILL / "scripts" / "position_sizing_calculator.py"),
                    "--input",
                    str(RISK_SKILL / "references" / "example-risk-position-input.json"),
                    "--out",
                    str(output_dir),
                ],
                cwd=ROOT,
            )

            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            self.assertTrue((output_dir / "support_note.md").exists())
            self.assertFalse((output_dir / "report.md").exists())

            run_log = json.loads((output_dir / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual("csv_support_note_export", run_log["workbook_mode"])
            self.assertIsNone(manifest["primary_human_deliverable"])
            self.assertTrue(
                any(
                    row["key"] == "support_note"
                    and row["artifact_role"] == "narrative_support"
                    and row["hidden_unless_requested"]
                    for row in manifest["outputs"]
                )
            )
            for row in manifest["outputs"]:
                if row["path"].endswith((".md", ".json", ".csv")):
                    self.assertNotEqual("primary_human_deliverable", row["artifact_role"])

    def test_scorecard_helpers_write_support_notes_not_markdown_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            idea_csv = tmp_path / "ideas.csv"
            idea_csv.write_text(
                "ticker,company,idea_type,variant_perception_score,catalyst,source_as_of\n"
                "ABC,ABC Co,long,4.0,Earnings revisions,2026-05-01\n",
                encoding="utf-8",
            )
            idea_out = tmp_path / "ideas_out"
            idea_result = run_command(
                [
                    sys.executable,
                    str(IDEA_SKILL / "scripts" / "score_ideas.py"),
                    str(idea_csv),
                    "--output-dir",
                    str(idea_out),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )
            self.assertEqual(0, idea_result.returncode, idea_result.stderr + idea_result.stdout)
            self.assertTrue((idea_out / "idea_scorecard_support_note.md").exists())
            self.assertFalse((idea_out / "idea_scorecard.md").exists())

            hedge_csv = tmp_path / "hedges.csv"
            hedge_csv.write_text(
                "hedge,hedge_type,risk_hedged,exposure_fit_score,as_of,source,live_pricing_status,borrow_status,option_chain_status,risk_model_status\n"
                "SPY put,option,market beta,4.0,2026-05-01,user supplied,available,not_applicable,available,validated\n",
                encoding="utf-8",
            )
            hedge_out = tmp_path / "hedge_out"
            hedge_result = run_command(
                [
                    sys.executable,
                    str(HEDGE_SKILL / "scripts" / "score_hedge_candidates.py"),
                    str(hedge_csv),
                    "--output-dir",
                    str(hedge_out),
                ],
                cwd=ROOT,
            )
            self.assertEqual(0, hedge_result.returncode, hedge_result.stderr + hedge_result.stdout)
            self.assertTrue((hedge_out / "hedge_scorecard_support_note.md").exists())
            self.assertFalse((hedge_out / "hedge_scorecard.md").exists())

    def test_long_short_scenario_helper_defaults_to_support_note_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            scenario_csv = tmp_path / "scenarios.csv"
            scenario_csv.write_text(
                "scenario,probability,current_value,target_value,key_drivers,timing,source_as_of\n"
                "Base,60%,100,120,Multiple recovery,12 months,2026-05-01\n"
                "Downside,40%,100,80,Estimate cut,6 months,2026-05-01\n",
                encoding="utf-8",
            )
            markdown_out = tmp_path / "trade_scenarios_support_note.md"
            json_out = tmp_path / "trade_scenarios.json"
            result = run_command(
                [
                    sys.executable,
                    str(LONG_SHORT_SKILL / "scripts" / "materialize_trade_scenarios.py"),
                    str(scenario_csv),
                    "--markdown-out",
                    str(markdown_out),
                    "--json-out",
                    str(json_out),
                    "--run-date",
                    "2026-05-18",
                ],
                cwd=ROOT,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            self.assertTrue(markdown_out.exists())
            self.assertTrue(json_out.exists())
            self.assertFalse((tmp_path / "trade_scenarios.md").exists())

    def test_scenario_sensitivity_defaults_to_json_support_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            output = tmp_path / "scenario_tables.json"
            result = run_command(
                [
                    sys.executable,
                    str(SCENARIO_SKILL / "scripts" / "materialize_public_equity_sensitivities.py"),
                    "--tables",
                    "price_target_scenario",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("tables", payload)

            run_log = json.loads((tmp_path / "run_log.json").read_text(encoding="utf-8"))
            manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("json_export", run_log["workbook_mode"])
            self.assertIsNone(run_log["primary_human_deliverable"])
            self.assertTrue(
                all(
                    row["artifact_role"] != "primary_human_deliverable"
                    for row in manifest["outputs"]
                )
            )


if __name__ == "__main__":
    unittest.main()
