"""Support-layer contract tests for Public Equity Investing."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_SUPPORT_PATH = "skills/public-equity-investing/internal-support"
SUPPORT_SKILLS = [
    "financial-source-of-truth",
    "financials-normalizer",
    "excel-data-cleaner",
    "deck-report-qc",
    "style-guide-adapter",
]
INTERNAL_SUPPORT_SKILLS = {
    "financial-source-of-truth",
    "excel-data-cleaner",
    "style-guide-adapter",
}
OWNING_SKILLS_WITH_SUPPORT_BLOCKS = [
    "company-tearsheet",
    "memo-builder",
    "long-short-pitch",
    "dcf-model-builder",
    "three-statement-model-builder",
    "comps-valuation",
    "equity-model-update",
    "thesis-tracker",
    "meeting-prep",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class EquityResearchSupportLayerContractTests(unittest.TestCase):
    def test_shared_support_standard_exists(self) -> None:
        text = read("shared/equity-research-support-standard.md")
        for phrase in [
            "Support-Layer Role",
            "Not-Owner Rule",
            "PM Judgment Layer",
            "Connector Honesty Rule",
            "Credit Markets Boundary",
            "missing_required_source",
            "Embedded Services Contract",
        ]:
            self.assertIn(phrase, text)
        routing = read("shared/support-layer-routing-contract.md")
        for phrase in [
            "Embedded Service Rule",
            "owning_workflow",
            "decision_impact",
            "readiness_effect",
            "artifact_role",
            "hidden_unless_requested",
            "Hero Artifact Policy",
        ]:
            self.assertIn(phrase, routing)

    def test_all_support_skills_reference_shared_standard(self) -> None:
        for skill in SUPPORT_SKILLS:
            relative_path = (
                f"{INTERNAL_SUPPORT_PATH}/{skill}/INTERNAL.md"
                if skill in INTERNAL_SUPPORT_SKILLS
                else f"skills/{skill}/SKILL.md"
            )
            text = read(relative_path)
            self.assertIn("shared/equity-research-support-standard.md", text, skill)
            self.assertIn("shared/support-layer-routing-contract.md", text, skill)
            self.assertIn("Embedded Support Routing", text, skill)
            for phrase in [
                "owning_workflow",
                "decision_impact",
                "readiness_effect",
                "artifact_role",
                "hidden_unless_requested",
                "secondary/support artifacts",
            ]:
                self.assertIn(phrase, text, skill)

    def test_support_standard_lists_public_equity_personas_and_not_owner_rule(self) -> None:
        text = read("shared/equity-research-support-standard.md")
        for phrase in [
            "long-only PMs",
            "long/short hedge funds",
            "sell-side equity research",
            "ETF/index diligence",
            "do not own the investment conclusion",
            "do not own memos, pitches, valuation, earnings calls, trade construction, credit research, or investment recommendations",
        ]:
            self.assertIn(phrase, text)

    def test_owning_skills_have_support_invocation_blocks(self) -> None:
        for skill in OWNING_SKILLS_WITH_SUPPORT_BLOCKS:
            text = read(f"skills/{skill}/SKILL.md")
            self.assertIn("When To Invoke Support", text, skill)
            self.assertIn("shared/support-layer-routing-contract.md", text, skill)
            self.assertIn("support", text.lower(), skill)

    def test_internal_support_has_no_selectable_skill_metadata(self) -> None:
        for skill in INTERNAL_SUPPORT_SKILLS:
            self.assertFalse((ROOT / "skills" / skill).exists())
            self.assertTrue((ROOT / INTERNAL_SUPPORT_PATH / skill / "INTERNAL.md").exists())

    def test_support_scripts_mark_artifacts_secondary_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            input_csv = tmp / "financials.csv"
            with input_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "entity",
                        "source_id",
                        "statement",
                        "line_item_original",
                        "period_label",
                        "source_value",
                        "source_name",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "entity": "ACME",
                        "source_id": "SRC-001",
                        "statement": "income_statement",
                        "line_item_original": "Revenue",
                        "period_label": "FY2026",
                        "source_value": "100",
                        "source_name": "Company release",
                    }
                )
            out_dir = tmp / "norm"
            script = (
                ROOT
                / "skills"
                / "financials-normalizer"
                / "scripts"
                / "normalize_extracted_financials.py"
            )
            result = subprocess.run(
                [sys.executable, str(script), str(input_csv), "--output-dir", str(out_dir)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertIsNone(manifest["primary_human_deliverable"])
            self.assertFalse(manifest["support_artifacts_user_visible_default"])
            self.assertTrue(
                all(
                    row["artifact_role"] != "primary_human_deliverable"
                    for row in manifest["outputs"]
                )
            )


if __name__ == "__main__":
    unittest.main()
