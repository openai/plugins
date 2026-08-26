"""Sector overlay mandate and PM judgment contract tests."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTOR_SKILL_ROOT = (
    ROOT / "skills" / "public-equity-investing" / "internal-support" / "sector-context-overlay"
)
SECTOR_ROOT = SECTOR_SKILL_ROOT / "references"
MANDATE_HEADINGS = [
    "### Long-only",
    "### Long/short",
    "### Sell-side / initiation",
    "### ETF / index",
    "### Public equity diligence",
    "### Model / valuation",
    "### Earnings / catalyst",
    "### Source discipline",
]


class SectorContextOverlayContractTests(unittest.TestCase):
    def test_sector_shared_contract_files_exist(self) -> None:
        for filename in ["pm-judgment-heuristics.md", "research-output-overlay-contract.md"]:
            path = SECTOR_ROOT / filename
            self.assertTrue(path.exists(), filename)
            text = path.read_text(encoding="utf-8")
            self.assertIn("PM", text)

    def test_all_sector_output_overlays_have_mandate_sections(self) -> None:
        paths = sorted(SECTOR_ROOT.glob("*/output-overlays.md"))
        self.assertGreaterEqual(len(paths), 8)
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for heading in MANDATE_HEADINGS:
                self.assertIn(heading, text, str(path))

    def test_sector_skill_requires_overlay_handoff_fields(self) -> None:
        text = (SECTOR_SKILL_ROOT / "INTERNAL.md").read_text(encoding="utf-8")
        for phrase in [
            "sector_overlay.selected_lens",
            "issuer_archetype",
            "mandate_lens",
            "pm_debate",
            "dashboard_modules_to_add",
            "source_gaps",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
