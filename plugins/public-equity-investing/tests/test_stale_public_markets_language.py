"""Stale legacy branding regressions for Public Equity Investing."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_MARKERS = [
    "Public " + "Markets",
    "public-" + "markets",
    "public_" + "markets",
]

SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".xlsx", ".xls", ".pdf", ".ico"}


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix in SKIP_SUFFIXES or "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


class StalePublicMarketsLanguageTests(unittest.TestCase):
    def test_no_legacy_branding_in_plugin_tree(self) -> None:
        failures: list[str] = []
        for path in iter_text_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for marker in LEGACY_MARKERS:
                if marker in text:
                    failures.append(f"{path.relative_to(ROOT)}: {marker}")
                    break
        self.assertEqual([], failures)

    def test_plugin_manifest_uses_replacement_branding(self) -> None:
        plugin_json = (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        self.assertIn("public-equity-investing", plugin_json)


if __name__ == "__main__":
    unittest.main()
