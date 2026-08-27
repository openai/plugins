"""Sector overlay credit-language classification for Public Equity Investing."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTOR_ROOT = (
    ROOT / "skills/public-equity-investing/internal-support/sector-context-overlay/references"
)
HANDOFF_OUTPUTS = [
    "banks/output-overlays.md",
    "biotech-pharma/output-overlays.md",
    "consumer-internet-marketplaces/output-overlays.md",
    "exchanges-market-infrastructure/output-overlays.md",
    "insurance/output-overlays.md",
    "oil-gas-ep/output-overlays.md",
    "reits/output-overlays.md",
    "saas-subscription-software/output-overlays.md",
]


def read(relative: str) -> str:
    return (SECTOR_ROOT / relative).read_text(encoding="utf-8")


class SectorOverlayCreditLanguageClassificationTests(unittest.TestCase):
    def test_output_overlays_mark_credit_work_as_handoff(self) -> None:
        for relative in HANDOFF_OUTPUTS:
            text = read(relative)
            self.assertIn("Credit Markets handoff", text, relative)
            self.assertIn("Credit Markets owns debt-security", text, relative)
            self.assertIn(
                "Do not turn the sector overlay into a debt-security recommendation", text, relative
            )

    def test_sector_modeling_routes_debt_security_underwriting_to_credit_markets(self) -> None:
        checks = {
            "banks/modeling-rules.md": "Preferred/AT1/T2, holdco debt, and opco debt require Credit Markets",
            "reits/modeling-rules.md": "Route preferred/debt issuing entity",
            "insurance/modeling-rules.md": "Route surplus notes, hybrids, preferreds, debt",
            "oil-gas-ep/modeling-rules.md": "Route unsecured-debt PDP cushion",
            "biotech-pharma/modeling-rules.md": "route claim-seniority, collateral-quality, and recovery underwriting to Credit Markets",
            "saas-subscription-software/modeling-rules.md": "Route debt/convert instrument underwriting",
            "consumer-internet-marketplaces/modeling-rules.md": "route underwriting to Credit Markets",
        }
        for relative, phrase in checks.items():
            self.assertIn(phrase, read(relative), relative)

    def test_legitimate_equity_sector_language_is_preserved(self) -> None:
        banks = read("banks/kpi-cheat-sheet.md")
        reits = read("reits/kpi-cheat-sheet.md")
        biotech = read("biotech-pharma/modeling-rules.md")
        event = (ROOT / "skills/event-driven-analyzer/references/merger_arb_playbook.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("loan yield", banks)
        self.assertIn("leasing spreads", reits)
        self.assertIn("manufacturing", biotech)
        self.assertIn("spread", event)


if __name__ == "__main__":
    unittest.main()
