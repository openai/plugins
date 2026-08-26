# E&P Modeling Guardrails

Deferred reference for `Oil Gas E&P Sector Analysis`. Load this when the task needs forecast, valuation, downside, credit, or security-specific modeling detail.

## Reserve-First Posture

Treat an E&P issuer as a depleting reserve base, commodity/differential exposure machine, decline-curve business, capital-allocation engine, and reserve-backed balance sheet. Do not lead with generic revenue growth, simple EBITDA margin, or blended BOE heuristics.

Start with molecule, basin, asset quality, reserve credibility, development control, realized pricing, cost/capex intensity, and the claim position of the security being analyzed. Treat reported EPS as lower quality when it is driven by commodity price moves, unrealized hedge marks, price-led reserve revisions, ceiling-test accounting, gains on sale, acquisition accounting, or tax noise.

## Analysis Path

1. Molecule and basin: separate oil, gas, and NGL volumes and margins; map basin, play, bench, asset cluster, working interest, NRI, operated exposure, and benchmark-to-realized price bridge.
2. Reserves and inventory: bridge proved reserves through production, extensions, discoveries, revisions, purchases, and sales; split PDP, PDNP, and PUD; test PUD funding, aging, and development timing; risk inventory by tier, type curve, lateral length, spacing, and parent-child interference.
3. Production and maintenance capital: bridge volumes through base decline, wells turned in line, downtime, acquisitions, divestitures, and timing; estimate PDP and corporate decline; distinguish maintenance capital from growth capital and acquisition carryover.
4. Realized pricing and obligations: build realized price by commodity from benchmark, basis, quality, transport, marketing, and hedge settlements; map hedge tenor, strike, volume coverage, and counterparty; treat firm transport, gathering, MVCs, and processing bottlenecks as quasi-fixed constraints.
5. Costs and capital efficiency: separate LOE, GPT, production taxes, cash G&A, interest, D&C, facilities, workover, and water-handling costs; compare half-cycle and full-cycle economics; clean FD&A and recycle ratio before using them; build corporate break-even, not only wellhead break-even.
6. Balance sheet and allocation: map debt, maturity wall, secured versus unsecured status, RBL terms, borrowing-base sensitivity, covenant room, liquidity after letters of credit and working capital, ARO, transport commitments, dividends, buybacks, M&A, and debt paydown.
7. Earnings quality and reserve accounting: separate price from volume, cost, and reserve-quality change; distinguish cash hedge settlements from derivative marks; split price revisions from geology or performance revisions; reconcile standardized measure/PV-10 to management NAV language.
8. Public-equity security context and Credit Markets handoff: for equity, anchor on strip and mid-cycle NAV, inventory duration, maintenance capex, and per-share value creation. Route unsecured-debt PDP cushion, maturity runway, secured-debt leakage, secured/RBL collateral, reserve-engineer assumptions, redetermination risk, and debt hedge requirements to Credit Markets.

## Model Must Show

- Commodity-separated production, realized prices, differentials, hedge settlements, and unhedged exposure.
- Reserve bridge, PDP/PUD mix, inventory duration, decline rates, and maintenance versus growth capex.
- LOE, GPT, production taxes, D&C/facilities cost, cash G&A, interest, ARO, and transport commitments as separate drivers.
- NAV or valuation bridge with price deck, decline assumption, reserve category, development timing, tax treatment, and fixed obligations.
- Sensitivities for WTI, Brent, Henry Hub, basin basis, NGL price, well cost, decline, downtime, borrowing base, and abandonment cost.

## Do Not

- Use blended BOE growth as a value proxy without molecule and margin mix.
- Treat reserve replacement from acquisitions, price revisions, or low-quality PUDs as drill-bit success.
- Use EV/EBITDAX or FCF yield without decline, inventory duration, maintenance capital, transport commitments, and maturity-wall context.
- Assume undeveloped inventory protects creditors unless it is financeable, economic, and likely to be developed.

## Deferred Modeling Layers

Load deeper files only when the task needs that layer:

- `valuation-rules.md`: valuation hierarchy and public-equity security context; route Credit Markets handoff rules to Credit Markets.
- `model-architecture.md`: required model structure, driver decomposition, and sensitivities.
