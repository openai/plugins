"""Rename and routing guardrails for equity-model-update."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_SKILL = "public-model-update"
NEW_SKILL = "equity-model-update"


class EquityModelUpdateRenameTests(unittest.TestCase):
    def test_skill_folder_and_front_matter_are_renamed(self) -> None:
        old_path = ROOT / "skills" / OLD_SKILL
        new_path = ROOT / "skills" / NEW_SKILL
        self.assertFalse(old_path.exists())
        self.assertTrue(new_path.exists())
        text = (new_path / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: equity-model-update", text)
        self.assertIn("# Equity Model Update", text)
        self.assertIn("target-price implications", text)

    def test_no_stale_old_model_update_slug_remains(self) -> None:
        stale = []
        for path in ROOT.rglob("*"):
            if path == Path(__file__):
                continue
            if not path.is_file() or path.suffix not in {
                ".md",
                ".py",
                ".json",
                ".yaml",
                ".yml",
                ".csv",
                ".txt",
            }:
                continue
            text = path.read_text(encoding="utf-8")
            if (
                OLD_SKILL in text
                or ("Public " + "Model Update") in text
                or ("public " + "model update") in text
            ):
                stale.append(str(path.relative_to(ROOT)))
        self.assertEqual([], stale)


if __name__ == "__main__":
    unittest.main()
