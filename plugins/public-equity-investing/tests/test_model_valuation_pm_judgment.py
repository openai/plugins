"""PM judgment contracts for Public Equity model and valuation skills."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUATION_SKILLS = [
    "dcf-model-builder",
    "three-statement-model-builder",
    "comps-valuation",
    "scenario-sensitivity-generator",
    "model-audit-tieout",
    "equity-model-update",
]


class ModelValuationPMJudgmentTests(unittest.TestCase):
    def test_shared_equity_valuation_standard_exists(self) -> None:
        text = (ROOT / "shared" / "equity-valuation-pm-standard.md").read_text(encoding="utf-8")
        for phrase in [
            "What does the current stock price imply?",
            "variant estimate path",
            "What breaks first in downside?",
            "What changes target, rating, sizing, hedge, trim, exit, or watchlist status?",
            "What evidence is missing?",
            "expected return versus hurdle",
            "downside/upside ratio",
        ]:
            self.assertIn(phrase, text)

    def test_model_and_valuation_skills_load_pm_standard(self) -> None:
        for skill in VALUATION_SKILLS:
            text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            lower = text.lower()
            self.assertIn("shared/equity-valuation-pm-standard.md", text, skill)
            self.assertIn("shared/pm-judgment-heuristics.md", text, skill)
            for phrase in [
                "current stock price implies",
                "variant estimate path",
                "what breaks first in downside",
                "target, rating, sizing, hedge, trim, exit, or watchlist",
                "evidence is missing",
            ]:
                self.assertIn(phrase, lower, skill)

    def test_model_dashboard_maps_include_equity_pm_modules(self) -> None:
        checks = {
            "dcf-model-builder/references/dashboard-map.md": [
                "current price versus implied value/share",
                "reverse DCF",
                "scenario skew",
            ],
            "three-statement-model-builder/references/dashboard-map.md": [
                "estimate path",
                "EPS/FCF",
                "what breaks first in downside",
            ],
            "comps-valuation/references/workbook/dashboard-map.md": [
                "selected-multiple bridge",
                "liquidity/float",
                "ETF/index exposure",
            ],
            "model-audit-tieout/references/dashboard-map.md": [
                "PM decision readiness",
                "source posture",
                "missing evidence",
            ],
        }
        for relative, phrases in checks.items():
            text = (ROOT / "skills" / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text, relative)


if __name__ == "__main__":
    unittest.main()
