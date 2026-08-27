# Exchange And FMI Modeling Rules

Deferred reference for `Exchanges Market Infrastructure Sector Analysis`. Load this only for valuation, forecast, model-update, sensitivity, public-equity security context, or downside work.

## Core Lens

Analyze an exchange or financial-market-infrastructure company as a regulated network, a monetization stack, and a critical-risk utility. Do not start with generic fintech, asset-manager, or software templates. Start with the exact revenue mix, benchmark or proprietary product strength, volume/mix/price/rate exposure, collateral economics, regulatory perimeter, and failure mode.

Raw activity is not enough. Low-yield contracts, compression, portfolio trading, rebated cash-equity flow, collateral spread, and recurring data or workflow revenue each deserve different durability and multiple treatment.

## Required Sequence

1. **Business mix and perimeter.** Split transaction, clearing, data, connectivity, index, listings, workflow/software, and pass-through lines. Map holdco, exchange, CCP, CSD/settlement, data, broker/intermediary, and regulator exposures.
2. **Volume quality and franchise.** Decompose ADV/ADNV by product, asset class, protocol, customer channel, geography, and open interest. Separate benchmark/proprietary franchises from fungible or rebated activity.
3. **Monetization quality.** Bridge volume to net revenue using RPC, net capture, FPM, rebates, liquidity payments, direct costs, royalties, and mix. Treat reported peer capture metrics as non-comparable until definitions are reconciled.
4. **Recurring revenue.** Separate data, connectivity, index, annual listings, workflow, and subscription-like streams from transaction-adjacent revenue tied to AUM, issuance, redistribution, terminal counts, or market activity.
5. **Clearing and collateral.** Distinguish initial margin, variation margin, default fund, eligible collateral, client clearing, cross-margining, netting, and collateral investment policy. Test whether margin cash or spread income is durable, rate-sensitive, passed through, or trapped.
6. **Market structure and moat.** Identify whether the moat is liquidity, benchmark status, regulation, data, workflow integration, colocation/connectivity, clearing efficiency, or capital relief. Check open access, interoperability, fee scrutiny, and rationality of share gains.
7. **Technology and resilience.** Underwrite uptime, major outages, data latency, cyber history, cloud migrations, capitalized software, resiliency spend, and whether operating leverage reflects scale or underinvestment.
8. **Growth and M&A.** Separate structural electronification, new products, new channels, automation, all-to-all, cross-sell, and workflow embedding from volatility, issuance, rates, or acquired growth.
9. **Capital and security stack.** Map debt by entity and upstreaming capacity. Test leverage, buybacks, dividends, acquisition policy, regulated-subsidiary ring-fencing, indirect CCP support expectations, and event risk for equity, debt, and hybrids.
10. **Normalization and scenarios.** Build calm, volatile, rate-cut, rate-rise, listings/issuance recovery, fee-pressure, outage/cyber, and regulatory scenarios. Value through-cycle volume, capture, recurring growth, collateral income, and required resilience investment.

## Model Guardrails

- Use segment-first models, not one-line revenue CAGRs.
- Model transaction lines from activity times monetization, with separate mix and rebate assumptions.
- Model clearing/collateral lines from balances, eligible collateral, default resources, investment policy, and earned spread or fees.
- Model recurring lines from price, contracts, linked assets, issuer count, subscription units, or workflow penetration, not generic ARR.
- Apply SOTP for hybrids and security-level analysis when economics are ring-fenced.
- Do not capitalize peak volatility, crisis volume, or high-rate collateral income as recurring revenue.

## Common Misreads

- Treating all volume as equal.
- Confusing gross share gain with profitable net capture.
- Missing fee schedule, rebate tier, protocol mix, or contract-value changes.
- Comparing company-defined ARR, market share, or FPM mechanically.
- Ignoring default-waterfall design, member concentration, margin methodology, recovery tools, or mutualization risk in a CCP.
- Underweighting outages, data integrity, cyber incidents, cloud migrations, and regulatory remediation because the business looks asset-light.

## Deeper References

- `valuation-rules.md`: valuation hierarchy, public-equity security context and Credit Markets handoff, and Credit Markets handoff rules.
- `model-architecture.md`: driver decomposition, model tabs, and sensitivities.
- `red-flags.md`: rejection tests and failure modes.
