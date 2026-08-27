"""Dashboard kind contract regressions for Public Equity Investing."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shared.dashboard.qa import EXPECTED_KIND, validate_payload  # noqa: E402

PUBLIC_EQUITY_KIND = "public_equity_investing_dashboard.v1"
LEGACY_KIND = "public_" + "markets_dashboard.v1"
LEGACY_MARKERS = [
    LEGACY_KIND,
    "public_" + "markets_dashboard",
    "Public " + "Markets " + "dashboard",
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def minimal_payload(kind: str = PUBLIC_EQUITY_KIND) -> dict[str, object]:
    return {
        "kind": kind,
        "title": "Issuer dashboard",
        "issuer": {"ticker": "ACME"},
        "tabs": [
            {
                "id": "overview",
                "label": "Overview",
                "modules": [
                    {"type": "decision_box", "data": {"stance": "Watch"}},
                ],
            }
        ],
        "sources": [{"id": "S1", "title": "Company release"}],
    }


class DashboardKindContractTests(unittest.TestCase):
    def test_validator_and_schema_use_public_equity_kind(self) -> None:
        schema = load_json(ROOT / "shared/dashboard/schema/dashboard_payload.schema.json")
        self.assertEqual(PUBLIC_EQUITY_KIND, EXPECTED_KIND)
        self.assertEqual(PUBLIC_EQUITY_KIND, schema["properties"]["kind"]["const"])

    def test_public_equity_kind_validates_for_minimal_payload(self) -> None:
        report = validate_payload(minimal_payload(), profile="draft")
        self.assertEqual("passed", report["status"], report)

    def test_default_validation_is_production_safe(self) -> None:
        report = validate_payload(minimal_payload())
        failures = "\n".join(report["hard_failures"])

        self.assertEqual("failed", report["status"])
        self.assertIn("production dashboards must include layout", failures)
        self.assertIn("production dashboards must include metadata", failures)

    def test_old_dashboard_kind_is_rejected(self) -> None:
        report = validate_payload(minimal_payload(LEGACY_KIND))
        self.assertEqual("failed", report["status"])
        self.assertTrue(
            any(
                "kind must be" in failure and PUBLIC_EQUITY_KIND in failure
                for failure in report["hard_failures"]
            ),
            report,
        )

    def test_all_dashboard_examples_use_public_equity_kind(self) -> None:
        payload_dir = (
            ROOT
            / "skills/public-equity-investing/internal-support/dashboard-builder/assets/example_payloads"
        )
        payloads = sorted(payload_dir.glob("*.json"))
        self.assertTrue(payloads, "expected dashboard example payloads")
        for payload_path in payloads:
            payload = load_json(payload_path)
            self.assertEqual(PUBLIC_EQUITY_KIND, payload.get("kind"), payload_path.name)

    def test_no_legacy_dashboard_identity_in_public_equity_plugin(self) -> None:
        failures: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".xlsx", ".xls", ".pdf"}:
                continue
            if "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for marker in LEGACY_MARKERS:
                if marker in text:
                    failures.append(str(path.relative_to(ROOT)))
                    break
        self.assertEqual([], failures)

    def test_hero_deliverable_policy_remains_html_xlsx_first(self) -> None:
        framework = read("shared/final-deliverable-framework.md")
        packager = read("shared/artifact_packager.py")
        dashboard_builder = read(
            "skills/public-equity-investing/internal-support/dashboard-builder/INTERNAL.md"
        )
        combined = "\n".join([framework, packager, dashboard_builder])

        for phrase in [
            "HTML dashboard or report",
            "XLSX workbook",
            "JSON, CSV, Markdown, logs, and manifests as secondary files only",
            "The JSON payload is an internal handoff contract, not the final user-facing artifact",
            "the rendered HTML is the user-facing artifact",
        ]:
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
