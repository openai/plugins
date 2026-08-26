# Strategy Nuance and PM Judgment

## Purpose

Use this reference when adapting position sizing to the type of public-equity-investing strategy. The right size is context-dependent: the same security can be a 50 bps event-driven stub, a 300 bps core long, a 100 bps short, or no position depending on mandate, catalyst, liquidity, and portfolio construction.

## Long/short equity

Key sizing judgment:

- Size idiosyncratic alpha, not accidental net exposure.
- Check long book and short book factor balance separately.
- Avoid using a low-quality short as a beta hedge if it adds squeeze/crowding risk.
- Treat earnings gaps, factor rotations, and borrow recalls as real loss events.
- Use starter sizes when thesis evidence is not yet falsifiable.

Best output:

- Recommended gross and net contribution.
- Beta-adjusted exposure.
- Factor/crowding risks.
- Add/trim triggers tied to thesis data and risk limits.

## Long-only / mutual fund

Key sizing judgment:

- Benchmark active weight can matter more than absolute weight.
- A position may be a risk-reducing add if the portfolio is structurally underweight a large benchmark constituent.
- Liquidity and capacity matter because redemptions can force sales.
- Drawdown and tracking error should be framed for the portfolio and mandate.

Best output:

- Absolute weight, active weight, and tracking-error implication if available.
- Position rank in portfolio.
- Benchmark-relative risk and sector/country impact.
- Add/trim plan around valuation and thesis milestones.

## Event-driven / special situations

Key sizing judgment:

- Size to adverse gap and timing delay, not ordinary volatility.
- Stop-losses are often not executable around binary events.
- Deal break, regulatory block, litigation, financing, shareholder vote, and timing risk dominate.
- High expected value can still be too large if adverse outcome is severe or liquidity vanishes.

Best output:

- Probability-weighted outcome table.
- Break price/adverse gap P&L.
- Timeline and catalyst calendar.
- Exit plan if event slips or spread widens.

## Merger arbitrage

Key sizing judgment:

- Size by downside to unaffected/break price and probability of close.
- Consider antitrust/regulatory, financing, shareholder, litigation, and timing risks.
- Annualized spread can be misleading if downside is large or timeline uncertain.
- Include borrow for stock deals and factor/market exposure for acquirer shares.

Best output:

- Gross spread, annualized spread, break spread, break price P&L.
- Close probability and timing cases.
- Hedge ratio if stock consideration exists.
- Risk limit based on break loss.

## Equity options / volatility

Key sizing judgment:

- Size premium-at-risk and delta/gamma/vega exposure separately.
- Match expiry to catalyst with buffer; avoid false precision in short-dated options.
- Consider IV crush after earnings/events and theta decay while waiting.
- Options can cap downside but still be poor expressions if skew and liquidity are punitive.

Best output:

- Premium budget.
- Delta-adjusted notional and Greeks.
- Catalyst/expiry alignment.
- Breakeven and scenario table with IV/time changes.

## Credit Markets handoff / equity-risk signals

Key sizing judgment:

- Public Equity Investing does not size CDS, bonds, loans, distressed claims, recovery waterfalls, covenant trades, spread DV01/CS01, or capital-structure hedges.
- CDS levels, credit spreads, rating actions, maturity walls, refinancing stress, and covenant headlines can still matter because they can impair common-equity value, liquidity, and downside gap risk.
- If the next action is to buy, sell, hedge, or size a credit security, route to Credit Markets.

Best output:

- Equity impairment read-through from the credit signal.
- Whether common-equity size should be smaller, hedged with equity instruments, or re-underwritten.
- What evidence would restore equity sizing confidence.
- Explicit Credit Markets handoff for any credit instrument, recovery, covenant, or spread DV01/CS01 work.

## Equity macro proxies

Key sizing judgment:

- Rates, FX, commodities, inflation, country risk, volatility, and curve proxies belong here only when they are causal to a listed-equity thesis or portfolio exposure.
- Size by equity scenario sensitivity, beta/regression, position notional, option premium, or factor exposure rather than standalone rates DV01 or credit CS01.
- Correlations can invert in crisis or policy-shock regimes, so the proxy can fail exactly when the equity position is stressed.
- A smaller equity position may be cleaner than a loose macro proxy.

Best output:

- Equity P&L sensitivity to the macro driver.
- Proxy instrument, hedge ratio logic, basis risk, and liquidity caveat.
- Scenario P&L for the equity book and proxy together.
- Data/catalyst monitoring plan and size-down/no-hedge alternative.

## Portfolio manager override principles

Use these principles when the math and judgment disagree:

- Do not scale simply because the upside/downside looks attractive if liquidity, gap risk, or source confidence is weak.
- Do not cut a high-quality position solely because short-term volatility is high if downside is fundamental and tolerable.
- Do not use a hedge or pair leg that removes the actual alpha driver.
- Do not let a model produce a size that the team cannot psychologically or operationally hold through normal volatility.
- Do not ignore concentration just because the name is liquid.
- Do not recommend a core position until the thesis has explicit disconfirming evidence and exit rules.

## Watchlist vs starter vs core

- **Watchlist**: data incomplete, catalyst uncertain, liquidity/borrow poor, valuation not compelling, or risk not quantifiable.
- **Starter**: enough evidence to begin learning; size small enough that being wrong is cheap.
- **Core**: thesis, downside, liquidity, and portfolio fit are all sufficiently underwritten.
- **High conviction / oversized only with governance**: requires exceptional evidence, favorable skew, clear risk controls, mandate fit, and explicit PM/risk approval.
