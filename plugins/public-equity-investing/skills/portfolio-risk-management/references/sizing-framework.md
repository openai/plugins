# Sizing Framework

## Purpose

This framework converts a thesis into a position size by combining math, market structure, and PM judgment. The recommended size should be the maximum prudent size, not the maximum possible size.

## The six sizing lenses

### 1. Loss-budget sizing

Use when the user provides maximum loss tolerance, stop level, downside price, or portfolio loss limit.

Formula:

- Position value = loss budget dollars / absolute downside return
- Percent NAV = position value / NAV

For a long:

- Downside return = (downside price / entry price) - 1

For a short:

- Adverse return = (upside squeeze price / entry price) - 1
- Loss budget should include borrow cost, dividends, financing, and forced-cover risk if material.

Interpret the loss constraint before converting it into a position size:

- `Scenario loss budget`: the user accepts a stated stress case as the sizing boundary. Show the adverse-move assumption explicitly and describe the result as conditional on that scenario.
- `Absolute loss cap`: loss cannot exceed the stated NAV amount even if a short squeezes beyond the modeled move. An unhedged short cannot meet this constraint; require priced defined-loss protection or recommend no position.
- `Ambiguous constraint`: for an interactive request, clarify which interpretation applies before recommending entry. For a non-interactive run, show both branches and do not label an assumed-stress size as ready to initiate.

PM judgment:

- Use thesis-break downside if better than a mechanical stop.
- Do not let a tight stop justify an oversized illiquid or gap-risk position.
- For catalyst trades, use gap-loss sizing, not stop-loss sizing.
- For shorts with an absolute cap, size the combined short-plus-call package from its maximum loss, not from an arbitrary squeeze percentage.

### 2. Volatility-budget sizing

Use when the user has volatility, target risk contribution, or risk-system output.

Simple approximation:

- Volatility contribution dollars = position value x annualized volatility x correlation adjustment
- Position value = volatility budget dollars / annualized volatility

If beta or factor volatility matters more than total volatility, use beta-adjusted or factor-adjusted exposure instead.

PM judgment:

- Volatility can understate risk for event-driven, crowded short, litigation, biotech, merger arb, and balance-sheet-stressed equity trades.
- Historical beta and correlation can break during regime shifts or company-specific events.

### 3. Liquidity sizing

Use when ADV, float, trading volume, options open interest, ETF liquidity, or exit window matters.

Formula:

- Exit capacity = ADV x participation rate x exit days
- Liquidity-constrained size = exit capacity x price, or notional capacity for listed options and approved macro proxies.

Default participation rate assumptions if absent:

- Highly liquid large-cap equity: 10-20% ADV for ordinary execution.
- Mid-cap equity: 5-10% ADV.
- Small-cap/illiquid equity: 2.5-5% ADV.
- Balance-sheet-stressed equity or event-driven names: lower unless block liquidity is verified.

PM judgment:

- Use stressed liquidity for downside cases.
- For shorts, liquidity must include borrow availability and recall risk.
- For options, open interest and market depth can bind before underlying ADV.

### 4. Exposure-limit sizing

Use when mandate or portfolio constraints matter.

Check:

- Single-name max.
- Sector/industry max.
- Country/currency max.
- Gross and net exposure.
- Beta-adjusted gross/net.
- Factor exposure and active risk.
- Long/short book balance.
- Liquidity buckets.
- Benchmark active weight and tracking error, for long-only or mutual fund contexts.

Formula examples:

- Single-name capacity = max single-name % NAV - current issuer exposure % NAV.
- Sector capacity = max sector exposure - current sector exposure.
- Beta capacity = beta budget / security beta.

PM judgment:

- Limits are not a target. A position can be below limit and still be too large.
- Add correlated positions and related instruments before applying limits.

### 5. Conviction and thesis-quality sizing

Use to scale the mathematically permitted size up or down based on quality of evidence.

Conviction ladder:

- **Starter**: thesis still forming, data incomplete, catalyst uncertain, high basis risk. Size small enough to learn.
- **Core**: thesis is well-evidenced, downside understood, liquidity acceptable, monitoring rules clear.
- **High-conviction**: variant view is strong, evidence is current, skew is favorable, path is robust, exit plan credible.
- **Special situation / event**: size by event outcome distribution, not by ordinary beta/vol.
- **No position / watchlist**: risk is unbounded, liquidity poor, thesis not falsifiable, or data insufficient.

PM judgment:

- Increase size only when downside is both quantified and tolerable.
- A great thesis with poor liquidity or bad asymmetry deserves a smaller size.
- A position with high expected return but unclear thesis-break rules should not be core size.

### 6. Portfolio-fit sizing

Use when the existing book already has overlapping exposure.

Check:

- Correlated longs/shorts.
- Supply-chain and competitor exposure.
- Same macro factor or thematic basket.
- Same catalyst or regulatory outcome.
- Crowded institutional ownership or hedge-fund hotel risk.
- Short book squeeze correlation.
- Benchmark and factor overlap.

PM judgment:

- Size incremental exposure, not the isolated line item.
- If the thesis is a pure idiosyncratic view but the position adds significant factor risk, consider a hedge or lower gross size.

## Recommended size construction

1. Compute size under each lens.
2. Identify the tightest binding constraint.
3. Adjust for confidence and catalyst path.
4. Compare to current/proposed size.
5. Recommend action: initiate, add, hold, trim, hedge, avoid, or watchlist.
6. Explain why the recommendation is not merely formulaic.

## Sizing language

Use precise language:

- "Recommended starter size: 1.0-1.5% NAV, capped by downside loss budget and liquidity."
- "Could scale to 3.0% only if the next data point confirms margin recovery and ADV remains above threshold."
- "Proposed 5.0% size is too large because the stress case would cost 150 bps of NAV and require 12 trading days to exit at 10% ADV."
- "Do not use a price stop as the primary control because catalyst gap risk makes the stop non-executable."
- "Illustrative unhedged size under a +150% squeeze scenario: 20 bp NAV; not implementation-ready until the loss-cap interpretation, borrow, and liquidity checks are confirmed."

Avoid weak language:

- "Position looks attractive."
- "Size according to conviction."
- "Risk/reward is favorable" without quantification.
- "Beta is low" without date, window, or regime caveat.

## Situation-specific guidance

### Long equity

- Size by downside to thesis-break value, not just stop-loss.
- Include market beta, sector, factor, and liquidity impact.
- If upside is long-duration, avoid over-sizing into near-term estimate/catalyst risk.

### Short equity

- Size smaller than equivalent long when upside risk is uncapped, borrow is tight, catalyst timing uncertain, or squeeze risk is high.
- Include borrow cost, dividends, recall, short interest, days to cover, and crowding.
- Use stress case above mechanical upside target.

### Pair trade

- Size each leg by beta/factor/sector neutrality target and borrow/liquidity constraints.
- Confirm the spread is linked to the thesis, not just historical correlation.
- Include gross exposure and residual net exposure.

### Options

- Size premium-at-risk separately from delta-adjusted exposure.
- Match expiry to catalyst timing with buffer.
- Include IV crush, skew, theta, liquidity, and roll plan.
- Do not recommend options only because downside is limited; premium decay and poor liquidity can make them bad hedges or bad expressions.

### Event-driven

- Size by probability-weighted outcome and adverse gap.
- Include timing delay, break price, regulatory/legal outcomes, financing risk, borrow, and liquidity under stress.
- Stop-losses can be unreliable around binary events.

### Credit Markets handoff / equity-risk signals

- Do not size CDS, bonds, loans, debt securities, distressed claims, recovery waterfalls, covenant trades, spread DV01/CS01, or capital-structure hedges in this plugin.
- Use Credit Markets when the security being sized is credit or the recommended action is a credit trade.
- Inside Public Equity Investing, CDS levels, credit spreads, rating actions, maturity walls, refinancing pressure, or covenant headlines may only lower equity size, change downside cases, trigger a hedge review, or force a re-underwrite of the common-equity thesis.
- Best output: explain how the credit signal changes common-equity downside, liquidity, or sizing. Do not produce credit notional, spread DV01/CS01, recovery, or debt-security sizing.

### Equity macro proxies

- Use rates, FX, commodities, inflation, country risk, or volatility proxies only when they are causal to the public-equity thesis or portfolio exposure.
- Size the equity position or approved macro proxy by scenario sensitivity, beta/regression, exposure mapping, option premium, or notional risk to the equity book.
- Route standalone rates DV01, credit CS01, bond futures basis, loan hedges, CDS, or credit spread implementation to Credit Markets or the relevant macro workflow.
- Include basis risk between the proxy and the equity thesis, and compare the proxy to a smaller equity size.
