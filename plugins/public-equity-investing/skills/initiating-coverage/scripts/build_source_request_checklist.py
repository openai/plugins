#!/usr/bin/env python3
"""Generate a source request checklist for initiating coverage.

Usage:
    python build_source_request_checklist.py [mode] [sector]
"""

import sys

BASE = [
    "latest annual report / 10-K / 20-F",
    "latest quarterly report / 10-Q / interim filing",
    "latest earnings release and transcript",
    "latest investor presentation",
    "current share price, market cap, diluted shares, and net debt",
    "consensus estimates and revisions history",
    "historical segment financials and KPIs",
    "peer set and trading multiples",
    "existing model or forecast assumptions",
    "management guidance and long-term targets",
]

MODE_EXTRA = {
    "sell_side_initiation": [
        "rating framework",
        "disclosure language",
        "publishing/compliance requirements",
    ],
    "buy_side_deep_dive": [
        "portfolio constraints",
        "position sizing framework",
        "existing PM view",
        "risk/hedge constraints",
    ],
    "hedge_fund_initiation": [
        "near-term catalyst calendar",
        "short interest / positioning if available",
        "borrow/liquidity context if short",
    ],
    "credit_adjacent_initiation": [
        "debt schedule",
        "ratings reports",
        "bond/loan prices",
        "maturity wall",
        "covenants if relevant",
    ],
    "sector_initiation": [
        "coverage universe",
        "sector KPI data",
        "industry market-size and share data",
        "sector factor exposures",
    ],
}

SECTOR_EXTRA = {
    "saas": [
        "ARR / RPO / billings",
        "NRR and gross retention",
        "CAC payback",
        "cohort and sales efficiency data",
    ],
    "banks": [
        "NII / NIM data",
        "deposit beta",
        "loan growth and credit costs",
        "CET1 / TBV / ROTCE",
    ],
    "insurance": [
        "combined ratio",
        "reserve development",
        "investment income",
        "book value and capital data",
    ],
    "reit": ["NOI", "occupancy", "leasing spreads", "AFFO", "NAV and cap rate assumptions"],
    "energy": ["production volumes", "realized prices", "hedges", "reserves", "capex and FCF"],
    "biotech": [
        "pipeline assets",
        "trial data",
        "probability assumptions",
        "cash runway",
        "patent/market exclusivity",
    ],
}


def main():
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print("Usage: python build_source_request_checklist.py [mode] [sector]")
        print("Prints an initiating-coverage source request checklist.")
        return 0
    mode = sys.argv[1] if len(sys.argv) > 1 else "sell_side_initiation"
    sector = (sys.argv[2] if len(sys.argv) > 2 else "").lower()
    items = list(BASE)
    items += MODE_EXTRA.get(mode, [])
    items += SECTOR_EXTRA.get(sector, [])
    print(f"# Source request checklist: {mode}" + (f" / {sector}" if sector else ""))
    for item in items:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
