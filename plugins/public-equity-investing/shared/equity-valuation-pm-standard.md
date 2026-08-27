# Equity Valuation PM Standard

Use this standard whenever Public Equity Investing work produces a model, valuation, scenario table, model update, comps package, or model audit. Pair it with `shared/pm-judgment-heuristics.md`.

## Required PM Questions

Every valuation artifact should answer these before it asks the reader to trust the math:

1. What does the current stock price imply?
2. What is the variant estimate path?
3. Is upside driven by fundamentals, multiple expansion, mix, capital return, sentiment, or a one-time event?
4. What breaks first in downside?
5. What changes target, rating, sizing, hedge, trim, exit, or watchlist status?
6. What evidence is missing?

## Equity Valuation Taste Rules

- Anchor to spot: show current price, market data as-of date, implied value per share, upside/downside to spot, and whether the current stock price already discounts the base case.
- Separate model correctness from investment usefulness. A mechanically clean workbook can still be useless if the estimate path, multiple, source posture, or downside mechanism is wrong.
- Bridge the Street: compare model drivers to consensus, guidance, and the market-implied path when available. State where the model is variant and where it is simply consensus repackaged.
- Explain the rerating mechanism. Multiple expansion requires a reason: faster growth durability, margin confidence, ROIC improvement, capital return, mix shift, risk premium change, or positioning/catalyst reset.
- Treat debt as an equity input unless the security is credit. Net debt, cost of debt, maturity risk, liquidity, and refinancing can affect common-equity value; bond, loan, CDS, covenant, recovery, spread/yield, and credit-security valuation belongs in Credit Markets.
- Make downside mechanical. Identify the first driver to fail, the model line it hits, the stock-price effect, and the observable falsifier.
- Convert output to action. Label the PM implication as `add`, `press`, `hold`, `trim`, `exit`, `hedge`, `watchlist`, `wait for proof`, or `re-underwrite`.

## Minimum Valuation Output

- `Current price / as-of`: price, date, source, and market-data freshness.
- `Implied value / share`: base, upside, downside, and probability-weighted value when supported.
- `What is priced in`: market-implied revenue, margin, EPS, FCF, multiple, or event expectation.
- `Variant estimate path`: the few model lines that must differ from consensus for the stock to work.
- `Valuation bridge`: peer median or DCF base to selected value, with growth, margin, ROIC/quality, leverage, liquidity, cyclicality, index/ETF/ownership, and source-confidence adjustments where relevant.
- `Scenario skew`: expected return versus hurdle, downside/upside ratio, break-even probability when applicable, and underwriteable-vs-optical upside label.
- `Action rules`: add/trim/exit/watchlist thresholds tied to observable evidence.
- `Missing evidence`: unresolved source, consensus, market-data, model, or diligence gaps.

## Credit Markets Handoff

Use Credit Markets when the user asks for bond comps, loan comps, CDS, spread or yield relative value, covenant-package analysis, debt-security valuation, recovery waterfall, restructuring valuation, creditworthiness, private-credit / public-credit instruments underwriting, or distressed claim valuation. Public Equity Investing may cite those outputs only as common-equity risk context.
