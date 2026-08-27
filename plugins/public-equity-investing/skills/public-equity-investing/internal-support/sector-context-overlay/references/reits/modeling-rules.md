# REIT Modeling Guardrails

Deferred reference for `REIT Sector Analysis`. Load this when the task needs forecast, valuation, downside, credit, or security-specific modeling detail.

## Property-Cash-Flow Posture

Treat a REIT as a portfolio of property cash flows, a liability/capital-market structure, and an external-growth engine that only works when underwriting discipline and cost of capital align. Do not lead with GAAP EPS, generic revenue growth, or corporate margin templates.

Start with property type, lease model, supply/demand cycle, cash NOI, same-store growth, embedded rent mark-to-market, recurring leakage from NOI to AFFO, capital access, dividend safety, and where the security sits in the stack. GAAP net income is usually noisy because depreciation, straight-line rent, gains on sale, lease intangibles, JV accounting, and financing items distort cash earnings power.

## Analysis Path

1. Property type and lease model: identify the economic unit of account, whether cash flow is contractual or operating, and how quickly leases, occupancy, street rates, RevPAR, SHOP rates, data-center commencements, or tower billings reset.
2. Portfolio quality: map market, asset quality, age, competitive set, replacement cost, supply pipeline, tenant/operator quality, and asset-level moat; separate resilient assets from obsolete or capex-heavy assets.
3. Leasing and same-store NOI: bridge revenue through occupancy, cash rent spreads, commencements, free-rent burn-off, bad debt, recoveries, percentage rent, lease termination income, and expense inflation; separate cash leasing spreads from GAAP spreads.
4. Capex and embedded growth: haircut rent mark-to-market for downtime, TI/LC, commissions, free rent, and asset quality; split defensive redevelopment from true value creation; identify recurring building capex and turn costs before AFFO.
5. External growth: break growth into same-store, acquisitions, development, redevelopment, dispositions, JVs, and capital markets; test acquisition/development yields against fully loaded marginal cost of capital, not stale hurdle rates.
6. Balance sheet and liquidity: map debt maturity, fixed/floating mix, secured/unsecured status, covenant room, rating access, unencumbered asset pool, JV/preferred exposure, revolver capacity, forward equity, and asset-sale optionality.
7. FFO/AFFO and dividend quality: bridge GAAP net income to Nareit FFO and company AFFO/CAD; normalize gains, straight-line rent, lease-intangible amortization, transaction costs, one-time recoveries, noncash financing items, recurring capex, TI/LC, and leasing commissions.
8. Public-equity security context and Credit Markets handoff: for equity, anchor on asset quality, AFFO durability, NAV, external-growth runway, leverage, and dividend. Route preferred/debt issuing entity, claim priority, maturity, coverage, covenants, collateral, and stressed recovery analysis to Credit Markets.

## Model Must Show

- Same-store NOI bridge, occupancy, leasing spreads, rent roll, lease expirations, property mix, and market exposure.
- NOI-to-FFO-to-AFFO bridge with recurring capex, TI/LC, straight-line rent, lease intangibles, and nonrecurring items separated.
- NAV or implied-cap-rate bridge with property-level NOI, cap rates by segment, debt/preferreds/JVs, and development value.
- Debt maturity ladder, fixed/floating exposure, secured debt, unencumbered NOI, fixed-charge coverage, liquidity, and refinancing assumptions.
- Sensitivities for cap rates, occupancy, cash leasing spreads, expense inflation, TI/LC, development yield, rates, refinancing access, and dividend payout.

## Do Not

- Use GAAP EPS, EBITDA margin, or generic DCF shortcuts as the lead valuation frame.
- Treat same-store NOI as clean without occupancy, rent spread, bad-debt, recovery, and expense detail.
- Call external growth accretive without marginal cost of capital and funding-source math.
- Underwrite dividend safety only from management payout ratios without AFFO normalization and balance-sheet context.

## Deferred Modeling Layers

Load deeper files only when the task needs that layer:

- `valuation-rules.md`: valuation hierarchy and public-equity security context; route Credit Markets handoff rules to Credit Markets.
- `model-architecture.md`: required model structure, driver decomposition, and sensitivities.
