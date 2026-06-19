from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


image_gen = load_module(
    "image_gen",
    PLUGIN_ROOT / "skills" / "imagegen-cli" / "scripts" / "image_gen.py",
)
remove_chroma_key = load_module(
    "remove_chroma_key",
    PLUGIN_ROOT / "skills" / "imagegen" / "scripts" / "remove_chroma_key.py",
)


class ImageGenCliTests(unittest.TestCase):
    def test_parse_size(self) -> None:
        self.assertEqual(image_gen._parse_size("1024x1536"), (1024, 1536))
        self.assertIsNone(image_gen._parse_size("wide"))

    def test_gpt_image_2_size_validation(self) -> None:
        image_gen._validate_gpt_image_2_size("1024x1024")
        with self.assertRaises(SystemExit):
            image_gen._validate_gpt_image_2_size("1000x1000")

    def test_prompt_augmentation(self) -> None:
        prompt = image_gen._augment_prompt_fields(
            True,
            "A ceramic mug",
            {"style": "product photography", "constraints": "no text"},
        )
        self.assertIn("Primary request: A ceramic mug", prompt)
        self.assertIn("Style/medium: product photography", prompt)
        self.assertIn("Constraints: no text", prompt)


class RemoveChromaKeyTests(unittest.TestCase):
    def test_parse_key_color(self) -> None:
        self.assertEqual(remove_chroma_key._parse_key_color("#00ff7f"), (0, 255, 127))
        with self.assertRaises(SystemExit):
            remove_chroma_key._parse_key_color("green")

    def test_soft_alpha_bounds(self) -> None:
        self.assertEqual(remove_chroma_key._soft_alpha(5, 12, 220), 0)
        self.assertEqual(remove_chroma_key._soft_alpha(230, 12, 220), 255)
        self.assertLess(remove_chroma_key._soft_alpha(100, 12, 220), 255)


if __name__ == "__main__":
    unittest.main()
