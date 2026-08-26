# Cash Flow Methods and Model Selection

## Purpose

Use this reference to select the right valuation method and build the cash flow schedule correctly.

## FCFF DCF

Use FCFF for most non-financial operating companies when valuing enterprise value.

Core formula:

`ufcf = ebit * (1 - cash tax rate) + d&a - capex - change in net working capital - other required reinvestment`

FCFF should exclude financing effects:

- no interest expense in unlevered FCF
- no debt repayment in unlevered FCF
- no dividends in unlevered FCF
- use WACC as the discount rate
- bridge from enterprise value to equity value after calculating EV

Common FCFF errors:

- using net income instead of NOPAT without adjusting for interest
- double-counting tax shield through both WACC and cash flows
- subtracting debt paydown inside FCFF and again in the EV-to-equity bridge
- mixing levered and unlevered cash flows
- terminal value based on EBITDA while FCF method uses inconsistent assumptions

## FCFE DCF

Use FCFE when valuing equity cash flows directly, especially when leverage is stable or intentionally modeled.

General formula:

`fcfe = net income + d&a - capex - change in net working capital + net debt issuance - preferred dividends and other equity-claim cash flows`

Discount FCFE using cost of equity, not WACC.

Common FCFE errors:

- discounting FCFE at WACC
- ignoring debt maturity or refinancing needs
- assuming net borrowing is permanent without support
- treating levered FCF as comparable to enterprise-value DCF output

## Dividend Discount Model

Use DDM when dividends are the meaningful distributable cash flow, especially for regulated financial institutions or stable dividend-paying companies.

Build around:

- earnings
- dividend payout ratio
- regulatory capital or capital adequacy constraints
- sustainable ROE
- growth
- cost of equity

Common DDM errors:

- treating dividends as discretionary when capital rules constrain them
- using payout ratios that do not support growth
- ignoring buybacks when material
- using DDM for companies whose dividends are not tied to cash generation

## Financial institutions

For banks, insurers, asset managers, and similar businesses, do not force a standard enterprise-value FCFF DCF unless the user explicitly asks and the limitations are stated.

Prefer:

- DDM
- FCFE
- excess return model
- price-to-book / ROE cross-check
- embedded value or other sector method where applicable

Key drivers:

- net interest margin
- loan / asset growth
- credit losses
- regulatory capital
- ROE
- payout capacity
- book value growth
- cost of equity

## Private companies

For private companies, clearly separate:

- company-specific assumptions
- market-derived assumptions
- placeholders
- diligence questions

Additional considerations:

- illiquidity or size premium, if justified
- management add-backs and normalization
- customer concentration
- owner compensation adjustments
- debt-like items
- working capital peg or transaction adjustments
- option pool, preferred equity, or liquidation preferences where relevant

## Distressed or turnaround companies

A DCF for a distressed company must include liquidity and downside realism.

Consider:

- short-term cash runway
- debt maturities
- covenant issues
- restructuring costs
- asset sales
- refinancing risk
- terminal value after stabilization, not before
- going-concern uncertainty

Flag valuations that assume a clean recovery without modeling the cash cost and timing of getting there.

## Project or asset DCF

For infrastructure, real estate, energy, mining, or project finance, match the forecast to asset life or contract life.

Key drivers:

- project life
- production or utilization
- pricing / tariffs
- operating costs
- maintenance capex
- abandonment or decommissioning costs
- tax depreciation
- debt sculpting
- residual value

Do not use a perpetuity terminal value for finite-life assets unless there is a defensible renewal or residual-value assumption.

## Credit Markets Boundary

For Public Equity Investing, liquidity stress and debt maturity risk are included only to judge common-equity impairment, survivability, and dilution/refinancing risk. If the user asks for recovery value, claim priority, covenant remedies, debt trading value, restructuring waterfall, or public/private credit underwriting, route to Credit Markets.
