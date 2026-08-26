# Insurance Modeling Rules

Deferred reference for `Insurance Sector Analysis`. Load this only for valuation, forecast, model-update, sensitivity, public-equity security context, or downside work.

## Core Lens

Analyze an insurer as a liability writer, investment portfolio, and regulatory/rating-capital structure. Do not start with EBITDA, EV, or generic revenue-growth templates. Start with the promise sold, pricing duration, retained versus ceded risk, reserve adequacy, float investment, solvency/rating constraints, holdco liquidity, and the exact security's claim behind policyholders and regulated opcos.

Reported EPS can be low quality when driven by reserve releases, cat luck, alternative marks, hedge gains, tax items, capital releases, or one-time reinsurance transactions.

## Required Sequence

1. **Liability promise and unit economics.** Classify true risk-bearing versus distribution/fee business; short-tail, long-tail, catastrophe, spread, protection, runoff, or fee-like exposure; and the clean denominator: earned premium, insurance revenue, account values, deposits, policies, exposures, or sums insured.
2. **Underwriting or liability margin.** For P&C/reinsurance, build price, exposure, retention, current accident-year attritional loss, cat/large-loss load, and expense ratio. For life/retirement/protection, build spread-earning assets, base yield, credited rate, fee income, mortality/morbidity, hedging, lapses, surrenders, and expenses.
3. **Reserve adequacy.** Underwrite accident year, line, paid/incurred development, case reserving, IBNR, inflation, social inflation, mass tort, environmental, professional, medical, property-cat reopening, claim closure, discounting, and reinsurance recoverables.
4. **Reinsurance and tail transfer.** Map quota share, XOL, aggregate, cat, stop-loss, ADC, funds-withheld, modco, retrocession, affiliated reinsurance, collateral, counterparty concentration, trapped capital, reinstatement features, and whether protection is economic or optical.
5. **Investment portfolio and ALM.** Separate base yield from variable/mark-sensitive income. Map rating/NAIC mix, duration, liquidity, CRE, structured products, CLOs, private credit, alternatives, AOCI, derivative collateral, and whether asset risk is subsidizing weak underwriting.
6. **Capital, solvency, and holdco liquidity.** Identify the binding regime: RBC, statutory surplus, Solvency II, SST, Bermuda capital, rating-agency capital, leverage, liquidity, or remittance limits. Trace capital through underwriting, spread, reserve changes, cats, OCI, taxes, dividends upstreamed, debt, and reinsurance.
7. **Accounting and normalization.** Bridge reported net income to core economic earnings. Separate underwriting, prior-year development, cat load, investment spread, variable income, gains/losses, hedges, taxes, capital actions, statutory cash generation, GAAP/IFRS, IFRS 17 CSM/service result, and market-risk benefits.
8. **Public-equity security context and Credit Markets handoff.** For equity, anchor on normalized ROE/book compounding and capital return. Route surplus notes, hybrids, preferreds, debt, issuer-entity ranking, coupon flexibility, structural subordination, recovery path, and rating-trigger analysis to Credit Markets.

## Model Guardrails

- Use insurance-native valuation: P/BV or P/TBV adjusted for ROE, normalized operating EPS, embedded value, SOTP, DDM, residual income, and capital adequacy.
- Do not compare written premium, deposits, account values, and IFRS 17 insurance revenue as if they are the same.
- For P&C, separate current accident-year, prior-year development, cat/large loss, attritional loss, expense ratio, and reinsurance effects.
- For life/annuity, separate spread, fee, hedge, market-sensitive accounting, policyholder behavior, statutory capital strain, and distributable cash.
- Treat holdco liquidity separately from opco surplus; upstream capacity often matters more than headline solvency.
- Scenario cat events, reserve strengthening, rate/reinvestment shifts, spread widening, lapse/surrender stress, reinsurance repricing, downgrade, and buyback/dividend constraints.

## Common Misreads

- Treating premium or deposit growth as value creation without rate adequacy and capital strain.
- Accepting favorable prior-year development as recurring earnings.
- Viewing reserve strengthening as clean-up without testing pricing, capital, ratings, and franchise damage.
- Treating RBC or a solvency ratio as the only binding constraint.
- Ignoring CRE, structured/private assets, AOCI, collateral calls, and forced-sale liquidity risk.
- Calling a security "safe" because the insurer is well capitalized without mapping issuer, ranking, policyholder priority, and remittance path.

## Deeper References

- `valuation-rules.md`: valuation hierarchy and public-equity security context; route Credit Markets handoff rules to Credit Markets.
- `model-architecture.md`: driver decomposition, model tabs, and sensitivities.
- `red-flags.md`: rejection tests and failure modes.
