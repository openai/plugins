#!/usr/bin/env python3
"""Create blank CSV templates for the portfolio-risk-management sizing mode."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

TEMPLATES = {
    "trade_setup.csv": [
        "analysis_date",
        "security",
        "ticker",
        "instrument",
        "direction",
        "entry_price",
        "target_price",
        "base_price",
        "downside_price",
        "stress_price",
        "holding_period",
        "catalyst",
        "thesis_summary",
        "source",
        "confidence",
    ],
    "portfolio_context.csv": [
        "portfolio_name",
        "nav",
        "currency",
        "benchmark",
        "current_gross_exposure_pct",
        "current_net_exposure_pct",
        "current_active_weight_pct",
        "max_single_name_pct_nav",
        "max_sector_exposure_pct_nav",
        "benchmark_active_weight_limit_pct",
        "factor_limit_pct_nav",
        "correlated_exposure_limit_pct_nav",
        "borrow_squeeze_capacity_pct_nav",
        "max_loss_bps_nav",
        "target_position_vol_contribution_bps",
        "notes",
    ],
    "exposure_impact.csv": [
        "exposure_type",
        "before",
        "incremental",
        "after",
        "limit",
        "status",
        "source",
    ],
    "liquidity.csv": [
        "security",
        "price",
        "adv_shares",
        "adv_dollars",
        "position_shares",
        "position_dollars",
        "normal_participation_rate",
        "stress_participation_rate",
        "required_exit_days",
        "borrow_cost_pct",
        "short_interest_pct_float",
        "days_to_cover",
        "borrow_availability",
        "crowding_read",
        "notes",
    ],
    "scenarios.csv": [
        "scenario",
        "probability",
        "price_or_return",
        "pnl_dollars",
        "pnl_pct_nav",
        "time_horizon",
        "liquidity_assumption",
        "action_rule",
        "notes",
    ],
    "options_overlay.csv": [
        "underlying",
        "option_type",
        "strike",
        "expiry",
        "contracts",
        "premium",
        "delta",
        "gamma",
        "vega",
        "theta",
        "implied_volatility",
        "open_interest",
        "bid_ask_spread",
        "catalyst_alignment",
        "notes",
    ],
    "pair_legs.csv": [
        "leg",
        "ticker",
        "direction",
        "price",
        "current_size_pct_nav",
        "proposed_size_pct_nav",
        "beta",
        "factor_exposure",
        "borrow_cost_pct",
        "adv_shares",
        "liquidity_notes",
        "thesis_link",
        "source",
    ],
    "factor_exposures.csv": [
        "factor",
        "before",
        "incremental",
        "after",
        "limit",
        "factor_exposure_per_1pct_position",
        "correlation_to_existing_book",
        "source",
        "as_of",
        "notes",
    ],
    "etf_index_context.csv": [
        "ticker",
        "index_or_etf",
        "benchmark_weight",
        "active_weight",
        "constituent_weight",
        "etf_ownership_or_flow_signal",
        "rebalance_event",
        "liquidity_notes",
        "source",
    ],
    "macro_proxy_inputs.csv": [
        "proxy",
        "risk_driver",
        "direction",
        "notional_or_exposure",
        "price_or_level",
        "rate_fx_commodity_or_index_level",
        "equity_sensitivity",
        "correlation_window",
        "basis_risk",
        "liquidity_notes",
        "source",
    ],
    "monitoring_rules.csv": [
        "trigger_type",
        "metric",
        "threshold",
        "action",
        "owner",
        "cadence",
        "source",
    ],
    "sources.csv": ["item", "source_name", "source_type", "date", "confidence", "notes"],
}

README = """# Risk Position Sizing Templates\n\nFill these CSV templates with the data available for the trade. Leave unknown fields blank rather than guessing.\n\nMinimum useful inputs: instrument/ticker, direction, entry price, downside/stress case, portfolio NAV, loss budget, liquidity/ADV, exit-window requirement, intended alpha, unwanted risk, and binding constraint. PM constraints should include gross/net/beta, active weight, factor exposure, correlated exposure, ADV/exit days, borrow/squeeze/crowding, catalyst gap risk, options Greeks when relevant, and size-down vs hedge. CDS, bond, loan, spread DV01/CS01, recovery, covenant, and capital-structure sizing belongs in Credit Markets.\n"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="risk_position_sizing_templates")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, headers in TEMPLATES.items():
        with (out / name).open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    (out / "README.md").write_text(README)
    print(f"Created {len(TEMPLATES)} templates in {out}")


if __name__ == "__main__":
    main()
