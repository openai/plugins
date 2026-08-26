"""Credit Markets handoff boundaries for Public Equity risk workflows."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    "shared/credit-markets-handoff.md",
    "skills/portfolio-risk-management/SKILL.md",
    "skills/portfolio-risk-management/references/sizing-framework.md",
    "skills/portfolio-risk-management/references/strategy-nuance.md",
    "skills/portfolio-risk-management/references/hedge-workflow.md",
    "skills/portfolio-risk-management/references/instrument-playbooks.md",
    "skills/portfolio-risk-management/references/hedge-scorecard-schema.md",
]

CREDIT_TERMS = [
    "CDS",
    "bonds",
    "loans",
    "spread DV01",
    "CS01",
    "capital-structure",
    "distressed",
    "recovery",
    "covenant",
]


class CreditMarketsHandoffForRiskTests(unittest.TestCase):
    def test_each_target_routes_credit_work_to_credit_markets(self) -> None:
        for relative_path in TARGETS:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("Credit Markets", text, relative_path)
            self.assertRegex(text.lower(), r"route|handoff|use credit markets", relative_path)

    def test_combined_boundary_names_credit_instrument_family(self) -> None:
        combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in TARGETS)
        for term in CREDIT_TERMS:
            self.assertIn(term, combined)

    def test_cds_and_spreads_are_signal_context_only(self) -> None:
        combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in TARGETS).lower()
        for phrase in [
            "cds/spreads only as common-equity risk context",
            "only as equity-risk signals",
            "use here only as public-equity risk context",
            "common-equity downside context",
        ]:
            self.assertIn(phrase, combined)

    def test_credit_macro_template_was_removed_from_position_sizing_mode(self) -> None:
        script = (
            ROOT
            / "skills"
            / "portfolio-risk-management"
            / "scripts"
            / "create_position_sizing_templates.py"
        ).read_text(encoding="utf-8")
        output_templates = (
            ROOT
            / "skills"
            / "portfolio-risk-management"
            / "references"
            / "position-sizing-output-templates.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("credit_macro_inputs.csv", script)
        self.assertNotIn("credit_macro_inputs.csv", output_templates)
        self.assertIn("macro_proxy_inputs.csv", script)
        self.assertIn("macro_proxy_inputs.csv", output_templates)


if __name__ == "__main__":
    unittest.main()
