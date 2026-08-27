"""Credit-language ownership boundaries for Public Equity Investing."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMBIGUOUS_PHRASES = [
    "credit-" + "market research",
    "credit " + "case",
    "credit " + "workflow",
    "private/" + "public " + "credit",
    "public " + "credit underwriting",
    "Credit Markets / " + "debt",
    "Credit Markets / " + "structured",
    "Credit Markets " + "or structured investor",
    "security-" + "specific underwriting",
    "credit/" + "debt valuation rules",
    "debt underwriting " + "or credit work",
]
CORE_BOUNDARY_FILES = [
    "shared/credit-markets-handoff.md",
    "shared/equity-research-support-standard.md",
    "shared/equity-valuation-pm-standard.md",
    "skills/thesis-tracker/SKILL.md",
    "skills/model-audit-tieout/references/audit-playbook.md",
    "skills/event-driven-analyzer/references/restructuring_special_situations_playbook.md",
    "skills/public-equity-investing/internal-support/excel-data-cleaner/references/examples.md",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class CreditLanguageBoundaryContractTests(unittest.TestCase):
    def test_core_boundary_files_route_credit_instruments_to_credit_markets(self) -> None:
        for relative in CORE_BOUNDARY_FILES:
            text = read(relative)
            self.assertIn("Credit Markets", text, relative)
        self.assertIn("equity-risk context", read("shared/credit-markets-handoff.md"))
        self.assertIn("common-equity", read("shared/equity-valuation-pm-standard.md"))
        self.assertIn("listed-equity decision", read("shared/credit-markets-handoff.md"))

    def test_ambiguous_credit_ownership_phrases_are_removed(self) -> None:
        failures: list[str] = []
        for relative in CORE_BOUNDARY_FILES:
            text = read(relative)
            for phrase in AMBIGUOUS_PHRASES:
                if phrase in text:
                    failures.append(f"{relative}: {phrase}")
        self.assertEqual([], failures)

    def test_thesis_tracker_is_equity_signal_not_credit_workflow(self) -> None:
        text = read("skills/thesis-tracker/SKILL.md")
        self.assertIn("Equity-risk credit signal / Credit Markets handoff", text)
        self.assertIn("route credit-security", text)
        self.assertIn("common-equity downside", text)

    def test_event_driven_restructuring_uses_listed_equity_expression(self) -> None:
        text = read(
            "skills/event-driven-analyzer/references/restructuring_special_situations_playbook.md"
        )
        self.assertIn("dated public-equity event path", text)
        self.assertIn("listed-equity expression", text)
        self.assertIn("route debt-security expression to Credit Markets", text)

    def test_guardrail_scripts_still_detect_credit_instruments_and_route_out(self) -> None:
        sizing = read("skills/portfolio-risk-management/scripts/position_sizing_core.py")
        hedge = read("skills/portfolio-risk-management/scripts/score_hedge_candidates.py")
        cleaner = read(
            "skills/public-equity-investing/internal-support/excel-data-cleaner/scripts/clean_tabular_data.py"
        )
        combined = "\n".join([sizing, hedge, cleaner])
        for phrase in ["route_to_credit_markets", "CDS", "bond", "loan", "DV01"]:
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
