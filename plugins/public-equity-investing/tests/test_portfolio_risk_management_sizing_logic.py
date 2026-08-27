"""Executable PM sizing-constraint tests for portfolio-risk-management."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "portfolio-risk-management" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from position_sizing_core import sizing_rows  # noqa: E402


class PortfolioRiskSizingLogicTests(unittest.TestCase):
    def test_short_borrow_squeeze_constraint_can_bind_below_loss_vol_liquidity(self) -> None:
        rows, summary = sizing_rows(
            {
                "portfolio": {
                    "nav": 100_000_000,
                    "max_loss_bps_nav": 150,
                    "target_position_vol_contribution_bps": 500,
                    "max_single_name_pct_nav": 10,
                    "borrow_squeeze_capacity_pct_nav": 1.25,
                },
                "position": {
                    "security": "Crowded Short Co",
                    "ticker": "CSC",
                    "instrument_type": "common equity",
                    "direction": "short",
                    "entry_price": 50,
                    "downside_price": 65,
                    "stress_price": 80,
                    "annualized_volatility_pct": 40,
                    "confidence": "high",
                    "short_interest_pct_float": 35,
                    "days_to_cover": 8,
                    "borrow_cost_pct": 12,
                },
                "liquidity": {"adv_shares": 2_000_000, "price": 50, "required_exit_days": 5},
            }
        )
        lenses = {row["sizing_lens"]: row for row in rows}
        self.assertIn("borrow_squeeze_capacity", lenses)
        self.assertEqual("borrow_squeeze_capacity", summary["raw_binding_constraint"])
        self.assertAlmostEqual(1.25, summary["recommended_size_pct_nav"])

    def test_benchmark_factor_constraint_can_bind_below_simple_limits(self) -> None:
        rows, summary = sizing_rows(
            {
                "portfolio": {
                    "nav": 100_000_000,
                    "max_loss_bps_nav": 200,
                    "target_position_vol_contribution_bps": 500,
                    "max_single_name_pct_nav": 10,
                    "benchmark_active_weight_limit_pct": 2.0,
                    "factor_limit_pct_nav": 1.0,
                },
                "position": {
                    "security": "Benchmark Risk Co",
                    "ticker": "BRC",
                    "instrument_type": "common equity",
                    "direction": "long",
                    "entry_price": 40,
                    "downside_price": 30,
                    "stress_price": 24,
                    "annualized_volatility_pct": 35,
                    "confidence": "high",
                    "current_active_weight_pct": 0.5,
                    "current_factor_exposure_pct_nav": 0.4,
                    "factor_exposure_per_1pct_position": 1.0,
                },
                "liquidity": {"adv_shares": 2_000_000, "price": 40, "required_exit_days": 5},
            }
        )
        lenses = {row["sizing_lens"]: row for row in rows}
        self.assertIn("benchmark_active_weight_capacity", lenses)
        self.assertIn("factor_limit_capacity", lenses)
        self.assertEqual("factor_limit_capacity", summary["raw_binding_constraint"])
        self.assertAlmostEqual(0.6, summary["recommended_size_pct_nav"])


if __name__ == "__main__":
    unittest.main()
