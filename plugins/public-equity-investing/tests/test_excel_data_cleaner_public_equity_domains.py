"""Public-equity domains for excel-data-cleaner."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ExcelDataCleanerPublicEquityDomainsTests(unittest.TestCase):
    def test_skill_focuses_on_public_equity_domains(self) -> None:
        text = read(
            "skills/public-equity-investing/internal-support/excel-data-cleaner/INTERNAL.md"
        )
        for phrase in [
            "market/security data",
            "portfolio/risk",
            "ETF/index",
            "consensus/provider exports",
            "Credit tables may be profiled only as `credit_markets_handoff`",
        ]:
            self.assertIn(phrase, text)

    def test_domain_playbook_routes_credit_and_adds_etf_index(self) -> None:
        text = read(
            "skills/public-equity-investing/internal-support/excel-data-cleaner/references/domain-playbook.md"
        )
        self.assertIn("Credit Markets handoff / equity-risk signal", text)
        self.assertIn("route_to_credit_markets", text)
        self.assertIn("## ETF / Index Data", text)
        self.assertNotIn("## Public " + "Credit / Distressed", text)

    def test_scripts_use_credit_handoff_domain(self) -> None:
        profile = read(
            "skills/public-equity-investing/internal-support/excel-data-cleaner/scripts/profile_tabular_data.py"
        )
        cleaner = read(
            "skills/public-equity-investing/internal-support/excel-data-cleaner/scripts/clean_tabular_data.py"
        )
        combined = profile + "\n" + cleaner
        self.assertIn("credit_markets_handoff", combined)
        self.assertIn("route_to_credit_markets", combined)
        self.assertNotIn("public_credit_distressed", combined)
        self.assertNotIn('"public_credit"', combined)


if __name__ == "__main__":
    unittest.main()
