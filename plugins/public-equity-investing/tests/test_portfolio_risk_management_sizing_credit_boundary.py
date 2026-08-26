"""Portfolio risk sizing-helper guardrails for credit instruments."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "portfolio-risk-management" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from position_sizing_core import sizing_rows  # noqa: E402


class PortfolioRiskSizingCreditBoundaryTests(unittest.TestCase):
    def test_credit_like_instrument_type_routes_to_credit_markets(self) -> None:
        data = {
            "portfolio": {"nav": 100000000, "max_loss_bps_nav": 50},
            "position": {
                "security": "ACME 2029 Notes",
                "instrument_type": "bond",
                "direction": "long",
                "entry_price": 95,
                "downside_price": 80,
            },
        }

        with self.assertRaisesRegex(ValueError, "Use Credit Markets"):
            sizing_rows(data)

    def test_equity_instrument_still_sizes(self) -> None:
        data = {
            "portfolio": {"nav": 100000000, "max_loss_bps_nav": 50},
            "position": {
                "security": "ACME common stock",
                "instrument_type": "common equity",
                "direction": "long",
                "entry_price": 100,
                "downside_price": 80,
                "confidence": "high",
            },
        }

        rows, summary = sizing_rows(data)

        self.assertTrue(rows)
        self.assertGreater(summary["recommended_size_pct_nav"], 0)
        self.assertNotEqual("insufficient data", summary["raw_binding_constraint"])


if __name__ == "__main__":
    unittest.main()
