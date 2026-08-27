"""Static contract tests for the Public Equity Investing PM judgment layer."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_SUPPORT_ROOT = ROOT / "skills" / "public-equity-investing" / "internal-support"

CORE_SKILLS = [
    "earnings-preview",
    "earnings-deep-dive",
    "initiating-coverage",
    "company-tearsheet",
    "idea-generation",
    "long-short-pitch",
    "memo-builder",
    "thesis-tracker",
    "catalyst-calendar",
    "event-driven-analyzer",
    "sector-context-overlay",
]

AUDIENCE_MODES = [
    "long_only_pm",
    "long_short_hf",
    "sell_side_research",
    "etf_index_diligence",
    "public_equity_diligence",
]

PM_TERMS = [
    "variant wedge",
    "what is priced in",
    "downside mechanism",
    "falsifiers",
    "action discipline",
]


class PMJudgmentLanguageTests(unittest.TestCase):
    def test_shared_pm_judgment_standard_exists(self) -> None:
        text = (ROOT / "shared" / "pm-judgment-heuristics.md").read_text(encoding="utf-8")
        for mode in AUDIENCE_MODES:
            self.assertIn(mode, text)
        for term in PM_TERMS:
            self.assertIn(term, text.lower())

    def test_core_skills_reference_shared_pm_standard_and_modes(self) -> None:
        for skill in CORE_SKILLS:
            path = (
                INTERNAL_SUPPORT_ROOT / skill / "INTERNAL.md"
                if skill == "sector-context-overlay"
                else ROOT / "skills" / skill / "SKILL.md"
            )
            text = path.read_text(encoding="utf-8")
            self.assertIn("shared/pm-judgment-heuristics.md", text, skill)
            self.assertIn("Public Equity PM Judgment Layer", text, skill)
            for mode in AUDIENCE_MODES:
                self.assertIn(mode, text, skill)

    def test_plugin_scope_mentions_index_etf_and_sell_side(self) -> None:
        combined = (
            (ROOT / "shared" / "pm-judgment-heuristics.md").read_text(encoding="utf-8")
            + "\n"
            + (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        ).lower()
        for phrase in ["etf/index", "constituent", "benchmark", "sell-side", "factor exposure"]:
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
