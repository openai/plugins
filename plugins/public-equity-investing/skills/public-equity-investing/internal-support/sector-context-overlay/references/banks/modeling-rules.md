# Bank Modeling Rules

Deferred reference for `Bank Sector Analysis`. Load this only for bank valuation, forecast, model-update, sensitivity, public-equity security context, or downside work.

## Core Lens

Analyze a bank as a leveraged portfolio of financial assets funded by confidence-sensitive liabilities inside a regulatory wrapper. Do not start with EBITDA, EV, or industrial DCF templates. Start with funding, asset repricing, credit, capital, liquidity, and the exact security's claim in the stack.

## Required Sequence

1. **Franchise and funding quality.** Split deposits by type, cost, relationship quality, uninsured share, concentration, seasonality, and marginal funding source. Purchased liquidity is not the same as franchise growth.
2. **Asset mix and NII.** Build NII from average balances, asset yields, deposit/funding costs, fixed/floating mix, floors, repricing lag, hedge roll-off, purchase accounting accretion, and securities reinvestment.
3. **Credit quality and reserves.** Underwrite by portfolio, vintage, collateral, geography, borrower type, criticized/classified migration, delinquencies, NCOs, ACL/ECL coverage, and reserve assumptions.
4. **Securities, AOCI, and duration.** Reconcile AFS/HTM marks, duration, runoff, hedges, pledgability, encumbrance, TCE/TBV impact, and whether liquidity stress could force uneconomic sales.
5. **Capital constraints.** Identify the binding regime: CET1, leverage, SLR, SCB, G-SIB surcharge, TLAC/MREL, local ring-fence, or rating pressure. Bridge capital through earnings, OCI, provisions, RWAs, dividends, buybacks, and M&A.
6. **Liquidity and confidence risk.** Map cash, reserves, unencumbered securities, central bank/FHLB capacity, secured funding, debt maturities, deposit runoff, collateral calls, and contingency funding credibility.
7. **Fees and expenses.** Separate recurring fees from market-dependent income; adjust efficiency ratios for business mix; identify regulatory remediation, technology, branch, litigation, FDIC, and underinvestment risks.
8. **Public-equity security context and Credit Markets handoff.** For equity, specify the issuer entity and how funding, capital, and resolution risk affect common-equity value. Preferred/AT1/T2, holdco debt, and opco debt require Credit Markets for instrument-level economics, triggers, subordination, resolution path, or recovery.

## Model Guardrails

- Use bank-native valuation: P/TBV, normalized EPS, ROTCE versus COE, residual income, and DDM where appropriate.
- Use residual income or DDM before forcing FCFF/EV methods.
- For equity, tie value to tangible book compounding, normalized ROTCE, through-cycle credit costs, capital return, and deposit franchise durability.
- Route preferreds, AT1, T2, hybrids, and debt-security analysis to Credit Markets; retain only common-equity read-through such as capital access, dilution, funding cost, and confidence risk.
- In downside, test deposit beta/outflow, wholesale funding substitution, NII compression, credit normalization, CRE stress, securities marks, capital buffers, liquidity coverage, and regulatory capital return restrictions.

## Common Misreads

- Treating lagged deposit repricing benefit as durable NII.
- Celebrating reserve releases without checking forward credit risk.
- Ignoring HTM marks because they are outside reported earnings.
- Using one capital ratio as proof of excess capital.
- Treating reported liquidity as usable without haircutting encumbrance and monetization friction.
- Applying generic peer multiples without normalizing ROTCE, credit risk, funding quality, capital, and business mix.

## Deeper References

- `valuation-rules.md`: valuation hierarchy and public-equity security context; route Credit Markets handoff rules to Credit Markets.
- `model-architecture.md`: driver decomposition, model tabs, and sensitivities.
- `red-flags.md`: rejection tests and failure modes.
