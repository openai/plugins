"""Index, ETF, and passive-flow public-equity contract tests."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOLVER = (
    ROOT
    / "skills"
    / "public-equity-investing"
    / "internal-support"
    / "sector-context-overlay"
    / "scripts"
    / "resolve_sector_lens.py"
)


class IndexETFEventContractTests(unittest.TestCase):
    def test_sector_resolver_detects_etf_index_mandate(self) -> None:
        spec = importlib.util.spec_from_file_location("resolve_sector_lens", RESOLVER)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        result = module.resolve(
            "Assess MSFT as a large ETF/index constituent ahead of an S&P rebalance and passive flow event"
        )
        self.assertIn("etf_index", result["mandate_lenses"])
        self.assertIn("passive flow relevance", result["mandate_output_requirements"]["etf_index"])

    def test_core_docs_cover_etf_index_diligence(self) -> None:
        docs = [
            ROOT / "skills" / "company-tearsheet" / "SKILL.md",
            ROOT / "skills" / "initiating-coverage" / "SKILL.md",
            ROOT / "skills" / "memo-builder" / "SKILL.md",
            ROOT / "skills" / "event-driven-analyzer" / "SKILL.md",
            ROOT / "skills" / "catalyst-calendar" / "SKILL.md",
        ]
        for path in docs:
            text = path.read_text(encoding="utf-8").lower()
            self.assertTrue("etf" in text or "index" in text, str(path))
            self.assertIn("public equity pm judgment layer", text, str(path))


if __name__ == "__main__":
    unittest.main()
