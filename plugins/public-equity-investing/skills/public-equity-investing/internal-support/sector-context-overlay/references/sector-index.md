# Sector Index

Use this index to select one primary sector lens before loading deeper references. If more than one sector could apply, pick the economics that drive the investment case and state the ambiguity.

If a prompt contains a stale legacy skill label or a misleading sector label, do not follow the label blindly. Classify from issuer economics, KPIs, products, revenue model, and risk drivers. Use `scripts/resolve_sector_lens.py` when the prompt is cross-sector, sparse, or ambiguous.

## Cross-Sector Decision Rules

- Business-model clues beat stale labels. A consumption data platform with product revenue, RPO, net retention, AI workload margin, and large-customer growth is `saas-subscription-software`, even if a surrounding filename or legacy label says REIT.
- Security-underwriting objective matters, but it does not override issuer economics. A credit view on leveraged cybersecurity software still uses `saas-subscription-software` for KPIs, with Credit Markets owning credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis.
- Real-asset wrappers matter only when landlord cash-flow economics dominate. Data center landlords are `reits`; data platforms using cloud infrastructure are `saas-subscription-software`.
- If two lenses genuinely matter, select the lens that drives forecast and valuation mechanics, then include `Secondary Sector Checks` for the other lens.
- If no supported lens fits, say no local overlay is installed and route back to the owning Public Equity Investing skill.

## Minimum Overlay Output

Every sector-context output should include selected lens, issuer archetype, first questions, KPI set, modeling or valuation conventions that matter, red flags, and missing sources. This minimum output applies even when the prompt is sparse.

## Banks

Reference folder: `references/banks/`

Use when the issuer is primarily a regulated bank, thrift, BHC, custody/trust bank, card lender, CRE-heavy lender, online bank, or deposit-funded specialty lender.

Do not use for insurers, asset managers, exchanges, card networks, payment processors, brokers, or generic specialty finance unless the entity is fundamentally being underwritten as a bank.

First questions: deposits, funding confidence, liquidity, asset quality, capital, NII sensitivity, AOCI/TBV, and regulatory constraints.

## Biotech Pharma

Reference folder: `references/biotech-pharma/`

Use when the case depends on clinical assets, commercial drugs, regulatory catalysts, launch curves, loss of exclusivity, BD economics, royalties, manufacturing, or cash runway.

Do not use for medtech, CRO/CDMO, healthcare services, tools, diagnostics, or distributors unless drug-asset economics are the primary underwriting driver.

First questions: asset/platform archetype, probability of technical/regulatory success, label, launch curve, gross-to-net, LOE, royalty/milestone burden, and financing runway.

## Consumer Internet Marketplaces

Reference folder: `references/consumer-internet-marketplaces/`

Use when marketplace or platform economics drive the case: ecommerce marketplaces, classifieds, resale, travel, delivery, mobility, local services, labor marketplaces, or hybrid ad/services platforms.

Do not use for pure SaaS, payment processors, first-party retail, media, or fintech unless marketplace matching and transaction-network economics are primary.

First questions: scarce side, liquidity, take rate, GMV/GOV/GMS/bookings bridge, cohort quality, incentives, fraud/trust, and contribution margin.

## Exchanges Market Infrastructure

Reference folder: `references/exchanges-market-infrastructure/`

Use when the issuer is an exchange, CCP, cash-equity/options network, derivatives venue, electronic FI/FX/repo venue, listings/index/data franchise, or integrated market infrastructure group.

Do not use for brokers, investment banks, asset managers, card networks, payment processors, or fintech software unless FMI economics dominate.

First questions: volume/open-interest regime, RPC/net capture, data/index quality, clearing/default waterfall, collateral spread, outage/cyber risk, and regulatory constraints.

## Insurance

Reference folder: `references/insurance/`

Use when the company is primarily a risk-bearing insurer or reinsurer and the case depends on underwriting, reserves, reinsurance, investment spread, capital, ratings, or holdco/opco structure.

Do not use for brokers, asset managers, healthcare services, mortgage REITs, or services companies unless insurance reserving and solvency economics dominate.

First questions: liability duration, distribution, reserve adequacy, accident-year margin, cat load, investment income, ALM, capital regime, and dividend capacity.

## Oil Gas E&P

Reference folder: `references/oil-gas-ep/`

Use when the issuer is an independent upstream producer, oil- or gas-weighted E&P, shale producer, offshore/conventional producer, or diversified independent dominated by upstream economics.

Do not use for refiners, midstream, oilfield services, integrated majors dominated by downstream/chemicals, or mineral/royalty vehicles unless upstream reserve economics dominate.

First questions: basin, commodity mix, PDP/PUD, decline curve, inventory depth, realized pricing, hedges, differentials, maintenance capex, RBL risk, and abandonment liabilities.

## REITs

Reference folder: `references/reits/`

Use when the issuer is primarily an equity REIT or listed landlord across net lease, industrial, apartments, retail, office, storage, healthcare, lodging, gaming, data centers, towers, or specialty property sectors.

Do not use for mortgage REITs, homebuilders, brokers, asset managers, or real-estate service businesses unless landlord cash-flow economics dominate.

First questions: property type, same-store NOI, leasing spreads, occupancy, FFO/AFFO, recurring capex, NAV, dividend sustainability, debt maturity wall, and cost of capital.

## SaaS Subscription Software

Reference folder: `references/saas-subscription-software/`

Use when the issuer is primarily recurring software: enterprise apps, SMB apps, workflow software, collaboration, dev tools, cybersecurity, data platforms, vertical SaaS, or license-to-cloud/consumption hybrids.

Do not use for semiconductors, IT services, marketplaces, ad tech, hardware, or payments unless recurring software economics are primary.

First questions: ARR/revenue bridge, billings/RPO, GRR/NRR, churn, expansion, CAC payback, gross margin, SBC, cash conversion, consumption exposure, AI cost/monetization, and rule of 40.

## PM Overlay Minimum Output

Every sector overlay should state selected sector lens, issuer archetype, mandate lens, core PM debate, KPI hierarchy, valuation sensitivity, benchmark/sector exposure relevance, source posture, thesis-break checks, source gaps, and secondary lenses considered.

For ETF/index work, distinguish company fundamentals, sector exposure, factor/rate/commodity sensitivity, index mechanics, liquidity, passive ownership, constituent concentration, and rebalance/flow relevance.
