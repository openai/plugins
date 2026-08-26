# WACC, Terminal Value, and Valuation Bridge Standards

## Purpose

Use this reference when building or reviewing discount rates, terminal value, and enterprise-to-equity value bridges.

## WACC build

For FCFF DCFs, WACC should reflect the risk of the operating cash flows and the currency of the cash flows.

Required inputs:

- valuation date
- currency
- risk-free rate
- equity risk premium
- beta or business risk assumption
- cost of equity
- pre-tax cost of debt
- marginal tax rate or cash tax rate used for shield
- after-tax cost of debt
- target debt / equity or debt / total capital
- WACC

Challenge each input:

- Risk-free rate: match duration and currency.
- ERP: should be appropriate to market and valuation date.
- Beta: should reflect business risk, leverage, and peer set if used.
- Cost of debt: should reflect current borrowing risk, not stale coupon alone.
- Tax shield: should be available and realistic.
- Capital structure: should reflect target or sustainable structure, not an accidental current mix.

## Cost of equity

Basic CAPM structure:

`cost of equity = risk-free rate + beta * equity risk premium + relevant premiums`

Use relevant premiums cautiously:

- size premium
- country risk premium
- company-specific risk premium
- illiquidity premium

Do not stack premiums without explaining why each is necessary and not double-counted.

## Cost of debt

Cost of debt should generally reflect current market borrowing cost or credit risk, not merely book interest expense.

Adjust for:

- floating vs fixed debt
- current credit spreads
- refinancing risk
- tax deductibility
- distressed or covenant-limited borrowing

## Terminal value by perpetuity growth

Formula:

`terminal value = final-year fcf * (1 + terminal growth) / (discount rate - terminal growth)`

Required checks:

- terminal growth must be below discount rate
- terminal growth should be sustainable in the forecast currency
- final-year FCF should be normalized
- terminal reinvestment must support terminal growth
- terminal margin and ROIC must be economically coherent

Common errors:

- terminal growth too high
- using a non-normalized final year
- applying growth to the wrong year
- not discounting terminal value correctly
- using FCFF terminal value with cost of equity

## Terminal value by exit multiple

Formula:

`terminal value = terminal metric * selected exit multiple`

Common metrics:

- EBITDA
- EBIT
- revenue for some high-growth businesses, with caution
- book value or assets for financials, with caution

Required checks:

- metric definition matches the multiple
- terminal metric is normalized
- selected multiple is supported or clearly marked as an assumption
- implied perpetuity growth is reasonable
- implied ROIC and margin profile are reasonable

Do not use an exit multiple as a shortcut to avoid thinking about sustainable cash flow.

## Discounting convention

State and apply the convention consistently:

- year-end discounting
- mid-year convention
- stub-period discounting for partial forecast years

Common errors:

- applying mid-year convention to FCF but year-end to terminal value without explanation
- discounting terminal value using the wrong period
- ignoring stub periods when valuation date is not fiscal year-end

## Enterprise value to equity value bridge

The valuation bridge must be explicit.

Start with enterprise value and adjust:

- plus cash and cash equivalents, if excess or non-operating treatment is appropriate
- plus non-operating investments
- plus assets held for sale or unconsolidated investments when appropriate
- less debt
- less leases if treated as debt-like
- less preferred equity
- less minority interest
- less pension deficits or other debt-like liabilities
- less restructuring obligations or other claims where appropriate
- plus / less tax assets or liabilities when separately valued

Then divide by:

- diluted shares outstanding for public companies
- fully diluted ownership or capitalization for private companies where relevant

Common bridge errors:

- double-counting cash
- omitting debt-like liabilities
- using basic instead of diluted share count
- ignoring preferred equity or liquidation preferences
- using stale share count or market data
- mixing enterprise-value and equity-value multiples

## Valuation range

Always present a range. The midpoint may be useful, but the range is more honest.

A good valuation range should be based on the assumptions most likely to change value:

- WACC
- terminal growth
- exit multiple
- revenue growth
- margin
- reinvestment / FCF conversion
- share count or bridge items when material

## Equity-Centered Credit Inputs

Cost of debt, leverage, liquidity, and refinancing risk may affect WACC, FCFE, or the EV-to-equity bridge. Do not turn this into a credit-security valuation. Use Credit Markets for spread/yield relative value, covenant-package analysis, recovery waterfall, distressed claim valuation, bond comps, loan comps, CDS, or debt-security valuation.
