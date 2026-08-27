"""Dashboard-map coverage for workbook/model-output Public Equity Investing workflows."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_SUPPORT_ROOT = ROOT / "skills" / "public-equity-investing" / "internal-support"

MODEL_OUTPUT_MAPS = [
    "comps-valuation/references/workbook/dashboard-map.md",
    "dcf-model-builder/references/dashboard-map.md",
    "deck-report-qc/references/dashboard-map.md",
    "model-audit-tieout/references/dashboard-map.md",
    "equity-model-update/references/dashboard-map.md",
    "three-statement-model-builder/references/dashboard-map.md",
]


class DashboardMapCoverageTests(unittest.TestCase):
    def test_model_output_dashboard_maps_exist_and_have_contract_sections(self) -> None:
        for relative in MODEL_OUTPUT_MAPS:
            path = ROOT / "skills" / relative
            self.assertTrue(path.exists(), relative)
            text = path.read_text(encoding="utf-8")
            for phrase in [
                "## Decision Question",
                "## Recommended Payload",
                "## Recommended Tabs And Modules",
                "## Required Evidence",
                "## Do Not",
            ]:
                self.assertIn(phrase, text, relative)
            self.assertIn("public_equity_investing_dashboard.v1", text, relative)

    def test_dashboard_builder_indexes_model_output_maps(self) -> None:
        text = (INTERNAL_SUPPORT_ROOT / "dashboard-builder" / "INTERNAL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Model-output dashboard maps", text)
        for relative in [
            item for item in MODEL_OUTPUT_MAPS if not item.startswith("deck-report-qc")
        ]:
            self.assertIn(relative, text)


if __name__ == "__main__":
    unittest.main()
