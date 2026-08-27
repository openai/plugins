"""PM/risk workflow contracts for Public Equity Investing."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class PMRiskWorkflowContractTests(unittest.TestCase):
    def test_shared_pm_risk_lens_exists(self) -> None:
        text = read("shared/pm-judgment-heuristics.md").lower()
        for phrase in [
            "pm/risk workflow lens",
            "alpha vs unwanted exposure",
            "retained exposure",
            "binding constraint",
            "hedge-failure scenario",
            "size-down/no-hedge alternative",
            "add/trim/exit/cover/resize/roll/remove rules",
        ]:
            self.assertIn(phrase, text)

    def test_portfolio_risk_skill_references_shared_standards(self) -> None:
        skill = "portfolio-risk-management"
        text = read(f"skills/{skill}/SKILL.md")
        self.assertIn("shared/pm-judgment-heuristics.md", text, skill)
        self.assertIn("shared/credit-markets-handoff.md", text, skill)
        lowered = text.lower()
        for phrase in [
            "position_sizing",
            "hedge_design",
            "integrated_risk_plan",
            "intended alpha",
            "unwanted risk",
            "retained exposure",
            "binding constraint",
            "size-down/no-hedge",
        ]:
            self.assertIn(phrase, lowered, skill)

    def test_equity_risk_taxonomy_is_first_class(self) -> None:
        combined = read("skills/portfolio-risk-management/SKILL.md").lower()
        for phrase in [
            "equity longs",
            "equity shorts",
            "pair trades",
            "etfs/index",
            "listed options",
            "factor hedges",
            "macro proxies",
        ]:
            self.assertIn(phrase, combined)

    def test_dashboard_packs_surface_pm_risk_decision_layer(self) -> None:
        relative_path = "skills/portfolio-risk-management/references/DASHBOARD_PACK.md"
        text = read(relative_path).lower()
        for phrase in [
            "pm decision box",
            "intended alpha",
            "unwanted risk",
            "retained exposure",
            "basis risk",
            "gross/net/beta/factor",
            "size-down/no-hedge",
            "credit markets handoff",
        ]:
            self.assertIn(phrase, text, relative_path)


if __name__ == "__main__":
    unittest.main()
