# Output and Review Standards

## Purpose

Use this reference when presenting the completed DCF, reviewing an existing DCF, or summarizing pressure-test results.

## Final model deliverables

When building or completing a DCF workbook, produce or preserve:

- clean input sections
- cash flow schedule
- WACC / discount rate schedule
- terminal value schedule
- enterprise-to-equity bridge
- per-share or ownership value output
- sensitivity tables
- scenario outputs
- visible checks
- executive dashboard or summary
- notes on source status and open items

## Written summary format

Use this structure unless the user asks for something else.

### 1. Header

State:

- company / asset
- valuation date
- currency and units
- method used
- model mode: built from scratch, completed existing DCF, repaired, updated, pressure-tested, or reviewed
- overall result: decision-ready, usable with caveats, needs fixes, or not decision-ready

### 2. Executive conclusion

Write a short senior-level paragraph covering:

- valuation range
- base case conclusion
- most important value drivers
- biggest risks or assumptions requiring diligence
- whether the model is ready to rely on

### 3. Key valuation outputs

Include:

- enterprise value
- equity value
- value per share or ownership stake value, if relevant
- PV of forecast FCF
- PV of terminal value
- terminal value as percentage of EV
- WACC / discount rate
- terminal growth or exit multiple
- base / downside / upside outputs

### 4. Assumption summary

Summarize:

- revenue growth assumptions
- margin assumptions
- tax assumptions
- working capital assumptions
- capex and D&A assumptions
- WACC assumptions
- terminal value assumptions
- bridge items and share count assumptions

Separate:

- sourced facts
- user-provided assumptions
- modeler assumptions
- placeholders / open items

### 5. Sensitivity and scenario summary

State:

- most important sensitivity
- downside valuation range
- upside valuation range
- whether sensitivities are linked and working
- where the valuation conclusion is fragile

### 6. Model checks

Report pass / fail / not tested for:

- formula errors
- cash flow method consistency
- WACC linkage
- terminal value linkage
- EV-to-equity bridge
- scenario switch
- sensitivity linkage
- placeholder inputs
- external links / macros / opaque dependencies

### 7. Issues and remediation

When reviewing or repairing a model, use this table:

| # | Severity | Type | Sheet / Range | Issue | Evidence | Valuation impact | Recommended fix |
| --- | --- | --- | --- | --- | --- | --- | --- |

Sort by severity and valuation impact.

### 8. Open questions

List the specific questions that must be answered before relying on the model.

Examples:

- What is the correct diluted share count at the valuation date?
- Are leases treated as debt-like items in the EV bridge?
- Should management add-backs be normalized or excluded?
- What peer set supports the selected beta or exit multiple?
- What terminal margin is defensible given competition?

### 9. Sign-off statement

Use one of these styles:

- **This DCF is not decision-ready until the blocker and high-severity issues above are fixed and retested.**
- **This DCF appears usable with caveats in the tested scope, subject to the limitations and open items above.**
- **No material issues were found in the tested scope, but this is not a guarantee outside the reviewed workbook, linked logic, and tested scenarios.**
- **The model is directionally useful for discussion, but the valuation conclusion should not be relied on until the unsupported assumptions are sourced and sensitivities are retested.**

## Tone standard

Write like a senior analyst briefing a Managing Director or Portfolio Manager.

- Be direct.
- Quantify where possible.
- Separate fact from judgment.
- Avoid false precision.
- Explain what matters most.
- Identify what could break the conclusion.
- Do not bury caveats in footnotes.

## Examples of strong comments

- "The base-case valuation is most sensitive to terminal margin and WACC; the downside case still assumes margin expansion, so it is not a true stress case."
- "The model uses FCFF but subtracts debt repayment inside the FCF schedule, which mixes enterprise and equity cash flow logic and overstates the conservatism of the valuation bridge."
- "Terminal value represents 78% of enterprise value. That is not automatically wrong for this growth profile, but the terminal margin and reinvestment assumptions need support before the range can be relied on."
- "The selected WACC appears reverse-engineered relative to the company's risk profile. The workbook needs a transparent cost-of-capital build or a clearly stated assumption range."

## Examples of weak comments to avoid

- "Looks good."
- "DCF seems reasonable."
- "Maybe check WACC."
- "Terminal value might be high."
- "The valuation is $52.17 per share" without a range, support, or sensitivity context.
