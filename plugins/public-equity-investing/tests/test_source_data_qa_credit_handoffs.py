"""Credit Markets routing for source/data/QA support skills."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATHS = [
    "shared/equity-research-support-standard.md",
    "skills/public-equity-investing/internal-support/financial-source-of-truth/INTERNAL.md",
    "skills/public-equity-investing/internal-support/financial-source-of-truth/references/evidence-hierarchy.md",
    "skills/public-equity-investing/internal-support/financial-source-of-truth/references/fact-assumption-labeling.md",
    "skills/financials-normalizer/SKILL.md",
    "skills/financials-normalizer/references/integration-guide.md",
    "skills/public-equity-investing/internal-support/excel-data-cleaner/INTERNAL.md",
    "skills/public-equity-investing/internal-support/excel-data-cleaner/references/domain-playbook.md",
    "skills/deck-report-qc/SKILL.md",
    "skills/public-equity-investing/internal-support/style-guide-adapter/references/writing-style-adaptation.md",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class SourceDataQACreditHandoffTests(unittest.TestCase):
    def test_credit_terms_route_or_remain_equity_context(self) -> None:
        combined = "\n".join(read(path) for path in TARGET_PATHS)
        for phrase in [
            "Credit Markets handoff",
            "equity-risk context",
            "common-equity",
            "route to Credit Markets",
            "CDS/spread",
            "debt-security",
        ]:
            self.assertIn(phrase, combined)

    def test_old_public_credit_ownership_phrases_are_absent(self) -> None:
        combined = "\n".join(read(path) for path in TARGET_PATHS)
        for phrase in [
            "public-credit pack",
            "IC/credit recommendation",
            "Public " + "Credit / Distressed",
            "public_credit_distressed",
            "Classify job. Public " + "markets, Credit Markets",
            "Credit Markets trading sheet",
        ]:
            self.assertNotIn(phrase, combined)

    def test_public_credit_memo_mentions_are_handoff_only(self) -> None:
        combined = "\n".join(read(path) for path in TARGET_PATHS).lower()
        for line in combined.splitlines():
            if "public-credit memo" in line or "credit memo" in line:
                self.assertTrue(
                    "route" in line or "credit markets" in line or "not style-adapt" in line,
                    line,
                )


if __name__ == "__main__":
    unittest.main()
