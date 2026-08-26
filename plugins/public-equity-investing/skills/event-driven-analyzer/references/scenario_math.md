# Scenario Math and Calculation Frameworks

Use this reference when calculating dated event spread, annualized return, market-implied probability, stock-deal hedge ratio, scenario EV, CVR value, spin SOTP, and payoff math. For capital structure, covenants, priority, fulcrum-security, and recovery-waterfall analysis, use Credit Markets; this skill may consume those outputs as terminal-value assumptions.

For repeatable calculations, use `scripts/event_math.py` when available. It accepts JSON input and emits JSON output.

## Basic return math

### Gross return

`gross_return = terminal_value / current_price - 1`

### Annualized return

`annualized_return = (1 + gross_return) ** (365 / days_to_resolution) - 1`

Use simple annualization only if the user expects it:

`simple_annualized_return = gross_return * 365 / days_to_resolution`

Caveat: Annualized return can mislead for binary trades. Always pair annualized spread with downside and expected value.

## Cash merger arbitrage

Inputs:
- Current target price.
- Cash deal price.
- Estimated close date or days to close.
- Break price/downside.
- Dividends, financing cost, borrow if relevant.

Core outputs:
- Gross spread.
- Annualized spread.
- Market-implied close probability.
- Probability-weighted expected return.

Formula:

`market_implied_probability = (current_price - break_price) / (deal_price - break_price)`

Interpretation:
- If implied probability is lower than the analyst's probability and downside is defensible, spread may be attractive.
- If implied probability is low because downside is understated, the trade may be a value trap.

Adjustments:
- Add expected dividends if holder receives them.
- Subtract financing/carry costs.
- Adjust terminal values for recut or remedy scenarios.
- Use delay scenarios when timing is uncertain.

## Stock-for-stock merger arbitrage

Inputs:
- Target price.
- Acquirer price.
- Exchange ratio.
- Collar terms if any.
- Expected dividends.
- Borrow cost and hedge availability.
- Days to close.

Formulas:
- `deal_value = acquirer_price * exchange_ratio`
- `gross_spread = deal_value / target_price - 1`
- `hedge_shares = target_shares * exchange_ratio`

Adjust for:
- Fixed exchange ratio vs floating exchange ratio.
- Collars and walk-away thresholds.
- Proration and election mechanics.
- Dividend mismatch.
- Borrow cost on short acquirer leg.
- Acquirer vote risk and acquirer fundamental risk.
- Residual exposure if hedge ratio is partial or collar-dependent.

## CVR valuation

Inputs by milestone:
- Payment amount.
- Probability of achievement.
- Expected payment date.
- Discount rate.
- Transferability/liquidity discount.
- Enforcement or sponsor incentive risk.

Formula:

`cvr_value = sum(payment_i * probability_i / (1 + discount_rate) ** years_i) - liquidity_discount`

Senior checks:
- Are milestones independent or conditional?
- Does management/control party have incentive to maximize or minimize payout?
- Is there reporting transparency?
- Is the CVR tradeable?
- Are there comparable outcomes?

## Scenario tree EV

Each scenario must include:
- Scenario name.
- Probability.
- Timing in days or months.
- Terminal value.
- Rationale.
- Signposts.

Formulas:
- `expected_terminal_value = sum(probability_i * terminal_value_i)`
- `expected_return = expected_terminal_value / current_price - 1`
- `expected_annualized_return = time-weighted or scenario-weighted annualized return`

Probabilities must sum to 100%. `scripts/event_math.py --mode scenario_ev` hard-fails bad sums by default. Use `--allow-probability-sum-mismatch` only for diagnostic output, and do not present probability-weighted conclusions until the tree is corrected or explicitly caveated as non-normalized.

## Downside / break price methods

Use at least two methods for high-stakes trades:

1. Unaffected price.
2. Peer-adjusted unaffected price.
3. Market-adjusted unaffected price.
4. Fundamental standalone value.
5. Historical trading range.
6. Bear-case valuation.
7. Debt recovery or liquidation value from Credit Markets when capital structure, covenants, priority, or recovery waterfalls drive the terminal case.
8. Litigation loss or damages-adjusted value.

Preferred merger break-price formula:

`peer_adjusted_break = unaffected_price * (1 + peer_return_since_unaffected_date) + idiosyncratic_adjustment`

Do not accept the unaffected price blindly if there was deal leakage, sector movement, earnings, guidance, macro shock, or unrelated company-specific news.

## Spin-off SOTP

Inputs:
- SpinCo revenue, EBITDA, EBIT, FCF, net debt.
- RemainCo revenue, EBITDA, EBIT, FCF, net debt.
- Peer multiples.
- Dis-synergies, stranded costs, separation costs.
- Tax leakage, pension, litigation, environmental liabilities.
- Share count and distribution ratio.

Formula:

`enterprise_value = metric * selected_multiple`

`equity_value = enterprise_value - net_debt - other_claims`

`per_share_value = equity_value / pro_forma_share_count`

Senior checks:
- Which shareholder base will own SpinCo after distribution?
- Is forced selling likely?
- Is the best entry pre-spin, when-issued, or post-distribution?
- Is the balance sheet fair or value-shifting?

## Distressed event bridge

When a dated distressed catalyst depends on capital structure or recovery, do not build the credit stack inside this skill. Hand off to or rely on Credit Markets for:
- Enterprise value range, cash, debt, secured/unsecured status, guarantees, collateral, DIP/new-money claims, rights offering economics, covenants, maturity wall, priority, and recovery waterfall.
- Fulcrum security, value-break location, priming risk, structural subordination, intercreditor terms, class vote dynamics, and court/process recovery risks.

This skill then owns the event bridge:
1. Identify the dated catalyst or process step.
2. Convert sourced credit/recovery outputs into terminal payoffs.
3. Assign scenario probabilities and timing.
4. Compute expected return, annualized return where useful, and monitoring thresholds.

## Position sizing bridge

A simple event-driven sizing conversation should include:
- Expected return.
- Downside gap.
- Probability of adverse scenario.
- Liquidity and ability to exit.
- Correlation to existing book.
- Mark-to-market path volatility.
- Catalyst date certainty.
- Borrow/financing constraints.

Possible language:
`The expected value is attractive, but the break downside and regulatory path argue for a starter position until the next gating item clears.`

## Flow Event Math

Add `flow_event` fields for estimated shares to buy/sell, ADV, days-to-trade, flow-vs-ADV, impact bands, assumed participation rate, borrow/financing cost, expected reversal, and liquidity exit plan. The helper is math-only; PM probability and market impact remain judgment.
