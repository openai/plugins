"""Equity artifact style contract for style-guide-adapter."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class StyleGuideAdapterEquityArtifactContractTests(unittest.TestCase):
    def test_style_is_not_evidence(self) -> None:
        text = read(
            "skills/public-equity-investing/internal-support/style-guide-adapter/INTERNAL.md"
        )
        self.assertIn("Style is not evidence", text)
        self.assertIn(
            "not factual support for prices, consensus, estimates, financials, ratings, targets, or investment claims",
            text,
        )

    def test_writing_style_targets_equity_artifacts(self) -> None:
        text = read(
            "skills/public-equity-investing/internal-support/style-guide-adapter/references/writing-style-adaptation.md"
        )
        for phrase in [
            "buy-side PM memos",
            "sell-side research notes",
            "public-equity decks",
            "ETF/index diligence notes",
            "client equity deliverables",
        ]:
            self.assertIn(phrase, text)
        self.assertIn("do not style-adapt a public-credit memo as if it were locally owned", text)

    def test_output_template_preserves_source_posture(self) -> None:
        text = read(
            "skills/public-equity-investing/internal-support/style-guide-adapter/references/output-templates.md"
        )
        for phrase in [
            "source posture preserved",
            "numbers/citations preserved",
            "caveats preserved",
            "confidence labels preserved",
            "substantive edits separated from style edits",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
