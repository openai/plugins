# DCF Integrity Controls and QA

## Purpose

Use this reference to verify that a DCF is mechanically reliable before presenting results.

## Minimum checks

Every DCF must include visible checks for:

- no active Excel errors in output-impacting cells
- valuation method and discount rate match cash flow type
- FCF links to forecast schedules
- terminal value uses the correct forecast year
- discounting convention is consistent
- WACC inputs flow to valuation formulas
- terminal value inputs flow to valuation formulas
- EV-to-equity bridge ties
- share count and per-share value tie
- selected scenario feeds the forecast and valuation
- sensitivity tables link to live outputs
- missing inputs and placeholders are flagged

## FCFF-specific checks

- EBIT or NOPAT base excludes financing effects.
- Tax calculation is on operating profit, not post-interest profit.
- D&A is added back only if it was included in EBIT or EBITDA logic correctly.
- Capex is subtracted with correct sign.
- Change in net working capital sign is correct.
- Debt repayment is not subtracted from unlevered FCF.
- WACC is used as discount rate.
- Enterprise value is bridged to equity value after DCF output.

## FCFE-specific checks

- Net income is the starting point or levered cash flow logic is otherwise clear.
- Net borrowing is included or excluded deliberately.
- Debt maturity and refinancing assumptions are coherent.
- Cost of equity is used as discount rate.
- Output is equity value, not enterprise value.

## Terminal value checks

- Terminal growth is less than discount rate.
- Terminal growth is reasonable for the currency and business maturity.
- Terminal year is normalized.
- Terminal margin is sustainable.
- Terminal capex and working capital are not artificially low.
- Exit multiple applies to the correct metric.
- Implied perpetuity growth from exit multiple is reasonable when cross-checked.
- Terminal value is discounted using the correct period.

## WACC checks

- Risk-free rate currency matches cash flow currency.
- ERP and beta assumptions are documented or marked as placeholders.
- Cost of debt reflects the right risk and timing.
- Tax shield is realistic.
- Capital structure is target or justified.
- WACC is not reverse-engineered to force a desired valuation.

## Equity bridge checks

- Cash treatment is clear: excess cash vs operating cash.
- Debt and debt-like items are captured.
- Preferred equity and minority interest are not ignored.
- Lease treatment is consistent with EBITDA and EV conventions.
- Diluted shares are used when appropriate.
- Per-share value divides by the correct share count.

## Formula QA

Check for:

- formula errors such as `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#NUM!`, `#N/A`, `#SPILL!`
- hardcoded assumptions inside formula regions
- formula inconsistencies across forecast periods
- overwritten formulas
- broken named ranges
- external links that are stale or broken
- circular references that are not intentional
- manual calculation mode causing stale outputs
- hidden tabs or rows affecting valuation

## Severity framework

| Severity | Meaning | Examples |
| --- | --- | --- |
| Blocker | Valuation cannot be trusted. | FCFF includes debt repayment; terminal value not discounted; WACC disconnected; equity bridge missing debt. |
| High | Material issue likely to mislead decisions. | Unsupported WACC; stale share count; sensitivities linked to wrong case; terminal assumptions unrealistic. |
| Medium | Issue could affect outputs or confidence. | Missing source note; weak downside case; limited working capital support; missing cross-check. |
| Low | Hygiene or maintainability issue. | Formatting inconsistency; unclear label; overly complex formula. |
| Question | Could be valid but requires confirmation. | Tax rate, capital structure, terminal multiple, or add-back treatment may be intentional. |

## QA workflow after building or fixing

1. Recalculate the workbook.
2. Confirm no output-impacting formula errors.
3. Test scenario switch behavior.
4. Test at least one sensitivity table.
5. Trace FCFF / FCFE to forecast schedules.
6. Trace WACC to discounting formulas.
7. Trace terminal value to final or normalized forecast year.
8. Trace enterprise value to equity value and per-share value.
9. Run directional pressure tests.
10. Summarize limitations and open items.

## Decision-ready sign-off standard

A DCF is decision-ready only when:

- the valuation method matches the company and purpose
- key assumptions are visible and supported or flagged
- formulas are reliable and auditable
- controls pass
- sensitivities cover the true value drivers
- downside case is meaningful
- terminal value is defensible
- valuation bridge is complete
- limitations are disclosed

If any of these fail, say the model is not decision-ready and identify the remediation order.
