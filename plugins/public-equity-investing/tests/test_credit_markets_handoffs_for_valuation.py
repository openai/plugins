"""Credit Markets handoff boundaries for Public Equity valuation skills."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    "dcf-model-builder/SKILL.md",
    "three-statement-model-builder/SKILL.md",
    "comps-valuation/SKILL.md",
    "scenario-sensitivity-generator/SKILL.md",
    "model-audit-tieout/SKILL.md",
    "equity-model-update/SKILL.md",
]
OLD_TABLE = "credit_liquidity_stress"


class CreditMarketsHandoffForValuationTests(unittest.TestCase):
    def test_skill_contracts_route_credit_security_work_to_credit_markets(self) -> None:
        for relative in TARGETS:
            text = (ROOT / "skills" / relative).read_text(encoding="utf-8")
            self.assertIn("Use Credit Markets", text, relative)
            for phrase in [
                "bond comps",
                "loan comps",
                "CDS",
                "spread/yield relative value",
                "covenant-package analysis",
                "debt-security valuation",
                "recovery waterfall",
            ]:
                self.assertIn(phrase, text, relative)

    def test_scenario_materializer_uses_equity_liquidity_downside_not_credit_table(self) -> None:
        script = (
            ROOT
            / "skills"
            / "scenario-sensitivity-generator"
            / "scripts"
            / "materialize_public_equity_sensitivities.py"
        ).read_text(encoding="utf-8")
        self.assertIn("equity_liquidity_downside", script)
        self.assertNotIn(OLD_TABLE, script)
        taxonomy = (
            ROOT
            / "skills"
            / "scenario-sensitivity-generator"
            / "references"
            / "public-equity-investing-sensitivity-taxonomy.md"
        ).read_text(encoding="utf-8")
        self.assertIn("equity_liquidity_downside", taxonomy)
        self.assertIn("Route credit-security valuation", taxonomy)


if __name__ == "__main__":
    unittest.main()
