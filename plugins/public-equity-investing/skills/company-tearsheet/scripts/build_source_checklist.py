#!/usr/bin/env python3
"""Create a missing-source checklist for common tearsheet profile types."""

from __future__ import annotations

import argparse

CHECKLISTS = {
    "public_company": [
        "Latest annual and interim financial statements or filings",
        "Latest investor presentation or management overview",
        "Business segment and geography breakdown",
        "Current ticker, exchange, share count, and listing identifiers",
        "Recent press releases or material announcements",
        "Key operating KPIs by business model",
    ],
    "equity_issuer_profile": [
        "Latest filing, prospectus, indenture, credit agreement, or offering document if available",
        "Debt stack, ratings, maturities, and spread/price context",
        "Recent earnings release and transcript if public",
        "Liquidity and covenant disclosures",
        "Recovery, collateral, guarantee, or priority information if distressed",
    ],
    "public_sector_peer": [
        "Ticker, exchange, fiscal year-end, and peer rationale",
        "Latest filing, earnings release, and investor presentation",
        "Key operating KPIs comparable to the focus company",
        "Current market cap, EV, share price, and valuation multiples",
        "Recent catalysts, guidance, and consensus context",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a source checklist for a tearsheet profile type"
    )
    parser.add_argument("profile_type", choices=sorted(CHECKLISTS), help="Profile type")
    args = parser.parse_args()

    print(f"# Source checklist: {args.profile_type}")
    for item in CHECKLISTS[args.profile_type]:
        print(f"- [ ] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
