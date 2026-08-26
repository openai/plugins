# Hedge Workflow Contract

Use when the task requires PM-grade hedge analysis rather than a short conceptual answer.

## Intake

Collect what is available without blocking: security/position/view, direction, size, entry/P&L/target/downside, thesis/variant view, catalysts/horizon, exposure to keep/reduce, benchmark, gross/net/sector/single-name limits, existing hedges, derivative/short permissions, premium/drawdown/liquidity/tax constraints, and data inputs for prices, risk model, correlations, options, borrow, ADV, catalysts, estimates, and macro variables.

## Objective

State: "Reduce `[unwanted exposure]` over `[horizon/catalyst]` while preserving `[desired thesis exposure]`." Add confidence from data quality.

## Exposure Map

Create columns: Exposure, Direction, Desired, Evidence, Materiality, Treatment.

Inventory market beta, sector/subsector, style/factor, leverage/balance sheet, liquidity/crowding, revenue/margin/estimate/multiple, management/regulatory/litigation, rates/curve, inflation, FX, commodities, CDS/credit-spread signals as equity-risk context, country risk, volatility/liquidity regime, and event/catalyst risk.

Treatments:

- Keep: core return driver; do not hedge or only partially hedge.
- Hedge: material unwanted risk reducible without damaging thesis.
- Reduce: better managed by position size than by hedge.
- Monitor: uncertain/low-confidence exposure; set trigger before forcing hedge.

Senior rule: reject any hedge that removes the reason the position exists.

## Candidate Universe

Consider direct equity instruments, market/index overlays, sector/thematic ETFs, factor baskets, peer/pair hedges, customer/supplier/commodity/FX/rates proxies, listed options, macro/cross-asset hedges, portfolio overlays, Credit Markets handoffs for credit instruments, and no-hedge/size-down.

Evaluate each candidate on exposure fit, thesis preservation, causal logic, regime stability, downside behavior, catalyst/tenor alignment, cost/carry, liquidity/capacity, basis risk, complexity, and exit clarity. Scores can help triage but PM judgment overrides.

## Sizing Methods

- Market/sector beta: target market value x beta to risk / hedge beta, adjusted for desired partial hedge, book constraints, liquidity, correlation instability, and catalyst window.
- Factor: reduce specified factor exposures subject to liquidity, cost, concentration, mandate, and residual exposure constraints.
- Pair/peer: dollar-, beta-, volatility-, factor-, or driver-neutral; check spread logic, valuation/revisions, borrow/dividends, catalyst match, and independent short risk.
- ETF proxy: adjust for look-through overlap, constituent mismatch, market cap/geography/factor mismatch, rebalance drift, and stress liquidity.
- Options: size by premium budget, loss floor, protection amount, delta target, scenario payoff, or event move; include expiry, strike, premium, breakeven, upside give-up, Greeks, liquidity, and monetization.
- Futures: notional / (price x multiplier), adjusted for basis, expiry, roll, margin, and liquidity.
- Credit Markets handoff: route CDS, bond, loan, spread DV01/CS01, recovery, covenant, distressed, and capital-structure hedge construction to Credit Markets. In this workflow, CDS/spread data is only an equity-risk signal that may argue for smaller equity size or a different equity hedge.
- FX/commodity: use net economic exposure or physical/unit sensitivity, not headline revenue alone; check natural hedges, tenor, basis, seasonality, and roll.

For an absolute loss cap on a short equity position, a direct long-call hedge must cover the short share-for-share: one listed call contract per 100 shares short, subject to contract multiplier and corporate-action adjustments. Calculate maximum package loss from the short sale entry price to the call strike plus premium, borrow/dividend cost, bid/ask and execution reserve, and other required carrying costs. A call spread is not a hard-cap solution because loss reopens above the written call strike.

## Cost And Scenario Discipline

Cost/carry items: borrow/dividends/rebate/recall, option premium/theta/skew/bid-ask/open interest/upside give-up, futures roll/basis/margin, swap financing/collateral/counterparty, FX forward points, commodity roll/location/grade basis, ETF expense/holdings drift, and Credit Markets handoff needs if a credit instrument appears.

Run relevant scenarios: thesis right, idiosyncratic downside, market/sector selloff, factor unwind, rates/FX/commodity shock plus CDS/credit-spread signal stress, earnings/catalyst gap, volatility spike/collapse, liquidity stress, correlation break, short squeeze or hedge pain. Include at least one scenario where the hedge fails.

## Basis Risk Ledger

Columns: hedge, basis risk, severity, why it matters, mitigation, monitoring trigger.

Common risks: product, factor, sector/subsector, geography, currency, timing/expiry, liquidity, volatility, catalyst, borrow/locate, crowding/squeeze, ETF constituent, curve/tenor, legal entity/capital-structure signal context. Credit instrument basis belongs in Credit Markets.

Severity: low = direct/causal/monitorable; medium = proxy mismatch acceptable for cost/liquidity; high = may fail in the adverse scenario and should be sized conservatively or rejected.

## Recommendation And Exits

Recommend primary hedge, secondary alternative, tactical/event hedge, portfolio overlay if superior, rejected hedges, implementation checks, and readiness label. Do not recommend implementing an option hedge until strike, expiry, premium, bid/ask, liquidity, Greeks, coverage ratio, and maximum-loss math are available.

Exit triggers: resize when exposure/position/beta/vol changes; roll when expiry/catalyst timing changes; monetize after protection works or vol spikes; remove after risk passes or hedge damages upside; re-underwrite when basis breaks, P&L is abnormal, borrow changes, or correlation fails.

## QA

Confirm objective, retained exposure, candidate breadth, basis risk, cost/liquidity, sizing logic, hedge-failure scenario, readiness label, missing data, and next action are explicit.
