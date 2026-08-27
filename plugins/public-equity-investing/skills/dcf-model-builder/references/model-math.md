# DCF Model Math

## FCFF forecast
For each forecast period:

```text
Revenue_t = Revenue_(t-1) * (1 + Growth_t)
EBIT_t = Revenue_t * EBIT Margin_t
Cash Taxes_t = max(EBIT_t * Tax Rate_t, 0)
NOPAT_t = EBIT_t - Cash Taxes_t
D&A_t = Revenue_t * D&A % Revenue_t
Capex_t = Revenue_t * Capex % Revenue_t
NWC_t = Revenue_t * NWC % Revenue_t
Change in NWC_t = NWC_t - NWC_(t-1)
Unlevered FCF_t = NOPAT_t + D&A_t - Capex_t - Change in NWC_t
EBITDA_t = EBIT_t + D&A_t
```

## FCFE support
When `forecast.cash_flow_basis = fcfe`, the pipeline values equity cash flows directly using cost of equity. Required scenario support is `net_income_margin` or sufficient assumptions to derive net income, and `net_borrowing` when leverage changes.

```text
Net Income_t = Revenue_t * Net Income Margin_t
FCFE_t = Net Income_t + D&A_t - Capex_t - Change in NWC_t + Net Borrowing_t
```

The FCFE path is useful for stable-leverage companies and some financial-style analyses. Banks and insurers usually need dividend discount, excess capital, or residual income models; route those to a sector overlay or specialized valuation workflow.

## Cost of equity and WACC

```text
Cost of Equity = Risk-Free Rate + Beta * Equity Risk Premium + Size Premium + Country Risk Premium + Company-Specific Premium
After-Tax Cost of Debt = Pre-Tax Cost of Debt * (1 - Marginal Tax Rate)
WACC = Target Equity % * Cost of Equity + Target Debt % * After-Tax Cost of Debt + Preferred % * After-Tax Cost of Preferred
```

For FCFF, discount at WACC. For FCFE, discount at cost of equity.

## Present value
The pipeline discounts explicit FCF using mid-year convention when `forecast.mid_year_convention = true`:

```text
PV FCF_t = FCF_t / (1 + Discount Rate)^(t - 0.5)
```

Terminal value is discounted at the end of the final forecast year:

```text
PV Terminal Value = Terminal Value / (1 + Discount Rate)^n
```

## Terminal value
Perpetual growth:

```text
Terminal FCF = Final Forecast FCF * (1 + g)
Terminal Value = Terminal FCF / (Discount Rate - g)
```

Exit multiple:

```text
Terminal Value = Final Forecast EBITDA * Exit EBITDA Multiple
```

Always cross-check terminal value with:
- terminal value as percent of enterprise value;
- implied terminal EBITDA multiple;
- implied terminal FCF yield;
- terminal growth vs discount rate;
- terminal margin vs history and peers;
- reinvestment and ROIC coherence where data is available.

## Enterprise-to-equity bridge
For FCFF:

```text
Equity Value = Enterprise Value
             + Cash
             + Non-Operating Assets
             + Associates
             - Debt
             - Leases
             - Minorities
             - Pensions
             - Preferred Stock
             - Options / Net Settlement
             - Other Debt-Like Items
```

For FCFE, the present value is equity value directly. The pipeline still calculates an implied enterprise value by adding debt-like items and subtracting cash/non-operating assets for comparability.

## Per-share value

```text
Value per Share = Equity Value / Diluted Shares
```

Use diluted shares, options, warrants, RSUs, convertibles, and buyback treatment carefully. Do not ignore dilution for high-SBC or option-heavy companies.
