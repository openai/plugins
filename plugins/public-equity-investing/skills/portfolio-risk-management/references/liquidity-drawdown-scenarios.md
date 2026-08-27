# Liquidity, Drawdown, and Scenario Analysis

## Purpose

Position sizing is only useful if the user understands how much can be lost, how quickly, and whether the position can be exited or reduced during stress.

## Liquidity analysis

### Core equity liquidity metrics

- Average daily volume (ADV), preferably 30-day and 90-day.
- Dollar ADV = ADV x price.
- Free float and float-adjusted volume.
- Position as percent of ADV and percent of float.
- Days to exit at 5%, 10%, and 20% ADV participation.
- Bid/ask spread and block liquidity, if available.

### Short liquidity and borrow

- Borrow availability and borrow cost.
- Utilization and short interest.
- Days to cover.
- Dividend cost.
- Recall risk.
- Squeeze/crowding risk.

### Options liquidity

- Open interest and daily option volume.
- Bid/ask width.
- Strike/expiry depth.
- Market maker liquidity around catalyst.
- Assignment/exercise considerations if relevant.

### Credit Markets handoff / equity risk read-through

- Do not analyze TRACE volumes, dealer depth, bid lists, lot size, issue size, spread DV01/CS01, recovery, or debt-security liquidity as a local sizing lane.
- If credit liquidity matters, use it only as a common-equity stress signal: refinancing access, maturity wall, covenant headline, liquidity squeeze, or solvency risk that could force a smaller equity position.
- Route credit instrument liquidity, debt exit capacity, and recovery/default sizing to Credit Markets.

## Participation-rate discipline

Use normal and stressed participation rates:

- Normal exit: 5-15% ADV depending on liquidity.
- Stress exit: 2.5-10% ADV, lower for event-driven, small-cap, crowded, balance-sheet-stressed, or options-heavy equity positions.
- For positions with catalyst gap risk, assume exit happens after adverse move, not before.

## Scenario design

### Baseline scenarios

At minimum:

1. **Base case**: thesis works or unfolds as expected.
2. **Downside case**: thesis delayed or partly wrong.
3. **Stress case**: thesis wrong plus market/liquidity/regime pressure.

### Scenario fields

Each scenario should include:

- Description.
- Probability, if user provided or explicitly assumed.
- Price/return move.
- P&L dollars.
- P&L as percent NAV.
- Time horizon.
- Liquidity/exit implication.
- Decision rule.

### Event scenarios

Include:

- Positive event outcome.
- Neutral/delay outcome.
- Negative event outcome.
- Adverse market backdrop at event date.
- Financing/borrow/liquidity impact.

### Earnings scenarios

Include:

- Beat/raise, in-line, miss/lower.
- Multiple expansion/contraction.
- Estimate revision path.
- Implied move/options market if available.
- Post-print liquidity and gap risk.

### Options scenarios

Include:

- Underlying price move.
- Implied volatility change.
- Time to expiry / theta decay.
- Delta/gamma change.
- Premium remaining and maximum loss.

### Equity-risk credit signal scenarios

Include only when they affect common equity:

- CDS or credit-spread widening as an equity-downside warning signal.
- Rating action, refinancing pressure, maturity wall, covenant headline, or liquidity squeeze as an equity impairment input.
- Whether the signal changes add/trim/exit/hedge/re-underwrite status.
- Route recovery/default valuation, spread DV01/CS01, bond, loan, CDS, and covenant-security analysis to Credit Markets.

## Drawdown framing

Calculate:

- Ordinary downside loss.
- Stress downside loss.
- Loss as bps of NAV.
- Contribution to expected portfolio drawdown if correlations rise.
- Number of other correlated positions that may lose simultaneously.

PM interpretation:

- A position can be acceptable on standalone downside but unacceptable when correlated book losses are included.
- A position can have attractive expected value but unacceptable path risk if it can force de-risking before payoff.
- Stop-loss levels are less useful when liquidity is poor, catalyst is binary, or borrow can be recalled.

## Monitoring triggers

Good triggers are specific and connected to thesis or risk. Include:

- Price levels: add, trim, review, stop, thesis break.
- Fundamental KPIs: revenue, margins, orders, churn, same-store sales, credit metrics, cash burn, utilization.
- Estimate revisions and consensus changes.
- Factor/macro triggers: rates, FX, commodities, CDS/credit-spread signals tied to equity risk, inflation, curve, and funding markets.
- Liquidity triggers: ADV decline, borrow cost spike, options liquidity deterioration.
- Catalyst triggers: event date change, adverse legal/regulatory signal, deal spread widening.
- Portfolio triggers: sector exposure breach, factor exposure breach, drawdown threshold, correlation spike.

Avoid vague triggers like "monitor earnings" or "watch macro."
