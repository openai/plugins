# Quality Control Checklist

Use this checklist before finalizing any `position_sizing` or `integrated_risk_plan` output from `portfolio-risk-management`.

## Source QC

- Are all prices, market data, portfolio values, exposures, betas, volatilities, liquidity, borrow, and options inputs dated?
- Are user-provided facts separated from assumptions and sourced facts?
- Are freshness-sensitive inputs flagged if stale or missing?
- Are source conflicts identified instead of silently averaged?
- Are formulas and units tied out if a workbook was used?

## Sizing QC

- Is the recommended size based on the tightest binding constraint?
- Does the output distinguish a `scenario loss budget` from an `absolute loss cap`, rather than assuming an adverse-move magnitude defines the user's constraint?
- For an ambiguous short loss limit, does an interactive run clarify the interpretation, or does a non-interactive output show conditional branches without recommending initiation?
- Is downside loss shown in dollars and bps/% NAV?
- Is stress loss shown separately from ordinary downside?
- Does the analysis include gross, net, beta-adjusted, and relevant factor exposure?
- Is liquidity/exit capacity calculated using realistic participation rates?
- Are current, proposed, and recommended sizes clearly distinguished?
- Does the output explain whether the trade should be initiated, added to, held, trimmed, hedged, avoided, or watchlisted?
- If executable quote, liquidity/exit capacity, borrow/locate or required option terms are missing, is the output labeled `Conditional risk screen` or `Not implementation-ready` rather than `Initiate`?

## PM judgment QC

- Does the size preserve the intended alpha thesis?
- Does it avoid over-hedging or over-sizing based on false precision?
- Does it recognize catalyst/path risk, not just endpoint valuation?
- Does it account for correlated positions and crowdedness?
- Does it distinguish a starter position from a core position?
- Does it explain what new evidence would justify scaling up?

## Instrument-specific QC

### Long equity

- Downside tied to thesis-break value, not just arbitrary stop.
- Sector/factor/beta exposure visible.
- Liquidity acceptable for the proposed size.

### Short equity

- Borrow cost, availability, recall risk, dividend cost, short interest, days to cover, and squeeze risk addressed when relevant.
- Stress case includes gap-up risk beyond base upside target.
- Size smaller when loss is convex or exit risk is high.
- An absolute loss cap is met only by a priced defined-loss package or no position; an unhedged short is not presented as cap-compliant.

### Pair trade

- Both legs sized consistently by beta, factor, sector, or dollar neutrality.
- Residual net/gross exposure and borrow/liquidity shown.
- The spread is thesis-linked, not merely historically correlated.

### Options

- Premium-at-risk and delta-adjusted exposure are both shown.
- Expiry aligns with catalyst plus buffer.
- IV crush, theta decay, and liquidity are addressed.
- Greeks are not stale.
- A hard-cap hedge for a short uses share-for-share long-call coverage and calculates maximum loss after entry-to-strike loss, premium, borrow/dividend cost, bid/ask and execution reserve, and applicable carry.
- A call spread is not described as an absolute loss cap on a short because loss reopens above its written strike.

### Credit Markets handoff and equity macro proxy

- CDS, bonds, loans, spread DV01/CS01, recovery, covenant, capital-structure, and distressed hedging or sizing questions are routed to Credit Markets.
- CDS/spreads/ratings/maturity/refinancing/covenant headlines are used only as common-equity risk signals.
- Macro proxies are tied to the equity thesis and compared against size-down/no-hedge alternatives.
- Basis between proxy and equity thesis is explained.

## Monitoring QC

- Are add/trim/exit rules specific and measurable?
- Are thesis-break triggers distinguished from price-only stops?
- Is there a review cadence around catalysts or data releases?
- Are portfolio-level triggers included when relevant?

## HTML and presentation QC

- A substantive integrated risk plan defaults to a polished standalone HTML risk decision report unless the user explicitly requests a standardized dashboard.
- The first-read layer shows current action, constraint interpretation, illustrative unhedged size when applicable, hard-cap compliant package, and missing inputs before entry.
- Citations do not fragment tickers, dates, percentages, basis-point amounts, instrument terms such as `GLP-1`, or scenario labels.
- Local HTML has been inspected with local headless-browser screenshots of the opening viewport and decision-critical sections before delivery.

## Common failure modes to avoid

- Sizing entirely from upside/downside without portfolio context.
- Treating a stop loss as executable around binary events.
- Using stale beta/correlation as if stable.
- Ignoring liquidity in small-cap, crowded, event-driven, balance-sheet-stressed, or options positions.
- Ignoring borrow and squeeze risk on shorts.
- Failing to distinguish gross, net, active, and beta-adjusted exposure.
- Recommending a large position while key inputs are assumptions.
- Producing a generic thesis memo instead of a sizing decision.
- Overwriting source data or prior analysis in a workbook.

## Final answer test

A PM should be able to read the final output and immediately know:

1. Whether to put the position on.
2. How large it should be.
3. What loss is being tolerated.
4. What exposure is being added.
5. What would make the PM add, trim, hedge, or exit.
