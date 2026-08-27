"""Equity-research contract for deck-report-qc."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class DeckReportQCEquityResearchContractTests(unittest.TestCase):
    def test_skill_classifies_equity_artifacts_not_credit_packs(self) -> None:
        text = read("skills/deck-report-qc/SKILL.md")
        for phrase in [
            "sell-side initiation",
            "PM pitch deck",
            "ETF/index diligence note",
            "public-equity IC memo",
            "price target",
            "benchmark weight",
        ]:
            self.assertIn(phrase, text)
        self.assertNotIn("public-credit pack", text)
        self.assertNotIn("credit memo, earnings note", text)

    def test_issue_taxonomy_focuses_on_equity_decision_impact(self) -> None:
        text = read("skills/deck-report-qc/references/issue-taxonomy.md")
        self.assertIn("price target or rating support conflicts with source", text)
        self.assertNotIn("recovery or spread data overstated", text)

    def test_standalone_html_qc_is_default_with_optional_dashboard(self) -> None:
        skill = read("skills/deck-report-qc/SKILL.md")
        output_templates = read("skills/deck-report-qc/references/output-templates.md")
        tieout = read("skills/deck-report-qc/references/extraction-and-tieout.md")
        dashboard_pack = read("skills/deck-report-qc/references/DASHBOARD_PACK.md")

        for phrase in [
            "../../shared/html-artifact-standard.md",
            "polished standalone HTML senior-review QC report",
            "only when the user explicitly asks for a standardized dashboard",
            "confirmed internal mismatch",
            "externally verified error",
            "local headless-browser screenshots",
        ]:
            self.assertIn(phrase, skill)
        self.assertIn("Review scope and evidence limitations", output_templates)
        self.assertIn("Decision-critical tie-out", output_templates)
        self.assertIn("must appear before a narrative `Top Issues`", output_templates)
        self.assertIn(
            "document.documentElement.scrollWidth <= document.documentElement.clientWidth",
            output_templates,
        )
        self.assertIn("Completion record", tieout)
        self.assertIn("document itself must not horizontally overflow", tieout)
        self.assertIn("Use this pack only when", dashboard_pack)

    def test_optional_dashboard_pack_surfaces_equity_qc_decision_layer(self) -> None:
        text = read("skills/deck-report-qc/references/DASHBOARD_PACK.md")
        for phrase in [
            "public-equity research support layer",
            "EPS/revenue/KPI support",
            "price-target support",
            "benchmark/ETF/index exposure",
            "market-data freshness",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
