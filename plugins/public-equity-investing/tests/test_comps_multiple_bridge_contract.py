"""Comps workbook PM bridge contract checks."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "comps-valuation" / "scripts" / "create_comps_template.py"


class CompsMultipleBridgeContractTests(unittest.TestCase):
    def test_template_includes_pm_bridge_and_action_sections(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in [
            "Multiple_Bridge",
            "PM_Action_Box",
            "Peer Median To Selected Multiple Bridge",
            "Current price",
            "Implied value / share",
            "Upside/downside to spot",
            "What is priced in",
            "Variant estimate path",
            "PM action implication",
            "Missing evidence",
        ]:
            self.assertIn(phrase, text)

    def test_peer_universe_tracks_public_equity_investability_filters(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in [
            "Liquidity / Float",
            "Index Membership",
            "ETF Ownership / Flow",
            "Short Interest / Borrow",
            "ADR / Share-Class Issue",
            "Consensus Coverage",
            "Estimate Revision Relevance",
            "Sector KPI Regime",
        ]:
            self.assertIn(phrase, text)

    def test_comps_references_require_selected_multiple_bridge(self) -> None:
        text = (
            ROOT / "skills" / "comps-valuation" / "references" / "workbook" / "comps-framework.md"
        ).read_text(encoding="utf-8")
        self.assertIn("selected-multiple bridge", text)
        self.assertIn("growth, margin, ROIC/quality", text)
        self.assertIn("debt comps", text)
        self.assertIn("Credit Markets", text)


if __name__ == "__main__":
    unittest.main()
