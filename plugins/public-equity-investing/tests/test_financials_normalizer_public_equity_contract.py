"""Public-equity contract for financials-normalizer."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class FinancialsNormalizerPublicEquityContractTests(unittest.TestCase):
    def test_skill_reframes_to_public_equity_inputs(self) -> None:
        text = read("skills/financials-normalizer/SKILL.md")
        for phrase in [
            "public-company source financials",
            "consensus/guidance inputs",
            "share-count support",
            "net-debt and capital-allocation support",
            "ETF/index constituent support",
        ]:
            self.assertIn(phrase, text)
        self.assertNotIn("Classify job. Public " + "markets, Credit Markets", text)

    def test_integration_guide_routes_credit_security_work_out(self) -> None:
        text = read("skills/financials-normalizer/references/integration-guide.md")
        self.assertIn("Credit Markets handoff / equity-risk debt and liquidity context", text)
        self.assertIn("Route covenant packages, recovery waterfalls", text)
        self.assertNotIn("## Credit Markets and distressed", text)

    def test_schema_uses_equity_risk_debt_context_not_debt_schedule(self) -> None:
        text = read("skills/financials-normalizer/references/normalization-schema.md")
        self.assertIn("equity_risk_debt_liquidity_context", text)
        self.assertIn("Credit-security schedules", text)
        self.assertNotIn(
            "`statement`: `income_statement`, `balance_sheet`, `cash_flow`, `kpi_schedule`, `segment`, `debt_schedule`",
            text,
        )

    def test_standalone_model_ready_package_requires_comparability_and_validation(self) -> None:
        skill = read("skills/financials-normalizer/SKILL.md")
        schema = read("skills/financials-normalizer/references/normalization-schema.md")
        qa = read("skills/financials-normalizer/references/qa-rules.md")
        for phrase in [
            "model-loading package",
            "disclosure/comparability bridge",
            "Validation_Checks",
            "Do not infer fiscal period-end dates",
            "reserve `consensus_estimate`",
            "`comparable_rounded`",
        ]:
            self.assertIn(phrase, skill)
        for phrase in [
            "Standalone model-ready package",
            "Disclosure_Comparability_Bridge",
            "Validation_Checks",
            "company guidance as consensus",
            "`comparable_rounded`",
        ]:
            self.assertIn(phrase, schema)
        self.assertIn("Do not report a number of passed checks", qa)
        self.assertIn("changed cash-and-securities presentation", qa)

    def test_helper_enforces_fiscal_dates_guidance_and_source_typing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            input_csv = tmp / "financials.csv"
            fieldnames = [
                "entity",
                "source_id",
                "statement",
                "line_item_original",
                "line_item_standard",
                "line_item_id",
                "period_label",
                "source_value",
                "source_location",
                "evidence_label",
                "source_name",
                "source_type",
            ]
            rows = [
                {
                    "entity": "NVDA",
                    "source_id": "SRC-001",
                    "statement": "income_statement",
                    "line_item_original": "Revenue",
                    "line_item_standard": "Revenue",
                    "line_item_id": "revenue",
                    "period_label": "Q1 FY2027",
                    "source_value": "100",
                    "source_location": "p. 1",
                    "evidence_label": "fact_source_reported",
                },
                {
                    "entity": "NVDA",
                    "source_id": "SRC-001",
                    "statement": "consensus_estimate",
                    "line_item_original": "Revenue outlook",
                    "line_item_standard": "Revenue guidance midpoint",
                    "line_item_id": "guidance_revenue_midpoint",
                    "period_label": "Q2 FY2027 outlook",
                    "source_value": "110",
                    "source_location": "p. 2",
                    "evidence_label": "issuer_management_claim",
                },
                {
                    "entity": "NVDA",
                    "source_id": "SRC-001",
                    "statement": "consensus_estimate",
                    "line_item_original": "Revenue consensus",
                    "line_item_standard": "Revenue consensus",
                    "line_item_id": "consensus_revenue",
                    "period_label": "Q2 FY2027 estimate",
                    "source_value": "109",
                    "source_location": "consensus p. 1",
                },
                {
                    "entity": "NVDA",
                    "source_id": "SRC-001",
                    "statement": "debt_schedule",
                    "line_item_original": "Debt due after five years",
                    "line_item_standard": "Debt due after five years",
                    "line_item_id": "debt_due_after_five_years",
                    "period_label": "Q1 FY2027",
                    "source_value": "50",
                    "source_location": "p. 3",
                    "evidence_label": "fact_source_reported",
                },
                {
                    "entity": "NVDA",
                    "source_id": "SRC-002",
                    "statement": "kpi_schedule",
                    "line_item_original": "Provenance marker",
                    "line_item_standard": "Provenance marker",
                    "line_item_id": "provenance_marker",
                    "period_label": "Q1 FY2027",
                    "source_value": "1",
                    "source_location": "source_note.md",
                    "evidence_label": "fact_source_reported",
                    "source_type": "user_prompt",
                },
            ]
            with input_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            out_dir = tmp / "out"
            script = (
                ROOT
                / "skills"
                / "financials-normalizer"
                / "scripts"
                / "normalize_extracted_financials.py"
            )
            result = subprocess.run(
                [sys.executable, str(script), str(input_csv), "--output-dir", str(out_dir)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            with (out_dir / "Normalized_Financials_Long.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                normalized = list(csv.DictReader(handle))
            self.assertEqual("", normalized[0]["period_end"])
            self.assertEqual("forecast", normalized[1]["period_type"])
            self.assertEqual("kpi_schedule", normalized[1]["statement"])
            self.assertIn("separately from external consensus", normalized[1]["normalization_note"])
            self.assertEqual("consensus_estimate", normalized[2]["statement"])
            self.assertEqual("estimate_consensus", normalized[2]["evidence_label"])
            self.assertIn("verify external source", normalized[2]["normalization_note"])
            self.assertEqual("equity_risk_debt_liquidity_context", normalized[3]["statement"])
            self.assertIn("legacy debt_schedule migrated", normalized[3]["normalization_note"])
            with (out_dir / "Source_Index.csv").open(newline="", encoding="utf-8") as handle:
                sources = {row["source_id"]: row for row in csv.DictReader(handle)}
            self.assertEqual("uploaded_file", sources["SRC-002"]["source_type"])
            issues = (out_dir / "Normalization_Issues.csv").read_text(encoding="utf-8")
            self.assertIn("missing_period_end", issues)

            validator = (
                ROOT
                / "skills"
                / "financials-normalizer"
                / "scripts"
                / "validate_normalized_financials.py"
            )
            valid = subprocess.run(
                [sys.executable, str(validator), str(out_dir / "Normalized_Financials_Long.csv")],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, valid.returncode, valid.stderr + valid.stdout)

            normalized[1]["statement"] = "consensus_estimate"
            with (out_dir / "Normalized_Financials_Long.csv").open(
                "w", newline="", encoding="utf-8"
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=normalized[0].keys())
                writer.writeheader()
                writer.writerows(normalized)
            invalid = subprocess.run(
                [sys.executable, str(validator), str(out_dir / "Normalized_Financials_Long.csv")],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, invalid.returncode)
            self.assertIn("consensus_estimate is reserved", invalid.stdout)


if __name__ == "__main__":
    unittest.main()
