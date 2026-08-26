"""Connector/provider honesty regressions for Public Equity support skills."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class UnsupportedConnectorPromisesTests(unittest.TestCase):
    def test_shared_standard_forbids_implied_vendor_access(self) -> None:
        text = read("shared/equity-research-support-standard.md")
        for phrase in [
            "Never imply live Bloomberg",
            "unless that connector/app/tool is actually callable",
            "use user-provided exports",
            "request the export",
            "missing_required_source",
        ]:
            self.assertIn(phrase, text)

    def test_source_protocol_requires_callable_or_exported_provider_data(self) -> None:
        text = read("skills/financials-normalizer/references/source-protocol.md")
        self.assertIn("Callable connected internal system", text)
        self.assertIn("Trusted financial data provider export or callable provider connector", text)
        self.assertIn("Do not imply live access", text)

    def test_style_sources_do_not_promise_connected_apps(self) -> None:
        text = (
            read("skills/public-equity-investing/internal-support/style-guide-adapter/INTERNAL.md")
            + "\n"
            + read(
                "skills/public-equity-investing/internal-support/style-guide-adapter/references/source-and-safety.md"
            )
        )
        self.assertNotIn("available in connected apps", text)
        self.assertIn("callable runtime apps/connectors", text)
        self.assertIn("Do not imply live access", text)


if __name__ == "__main__":
    unittest.main()
