# Output and Review Reference

Use this reference to produce final outputs that meet CFO, Portfolio Manager, Managing Director, board, lender, or investment committee expectations.

## Executive summary standard

After building or updating a model, provide a concise but decision-oriented written summary.

Include:

- what was built or changed
- model purpose and scope
- forecast horizon and scenario set
- key assumptions
- key outputs
- major sensitivities
- checks passed / failed
- open questions and limitations
- recommended next steps

Avoid vague language such as "looks good" or "seems fine." Use evidence.

## Recommended final response structure

Use this structure unless the user asks for another format.

### 1. Build summary

State:

- workbook / model created or updated
- scope
- company / business model if known
- forecast horizon and granularity
- scenarios included
- whether formulas and checks were added

### 2. Key assumptions

Summarize the most important assumptions by category:

- revenue
- gross margin / COGS
- opex
- working capital
- capex and D&A
- debt / interest / liquidity
- tax
- scenario-specific assumptions

Label assumptions as:

- source-based
- user-provided
- historical-trend-based
- modeler placeholder
- open question

### 3. Model outputs

Summarize the outputs that matter for the decision, such as:

- revenue growth
- EBITDA and EBITDA margin
- net income
- free cash flow
- ending cash
- debt and leverage
- liquidity runway
- covenant headroom
- capital need
- scenario downside risk

### 4. Controls and QA

Report:

- balance sheet balance status
- cash tie status
- retained earnings tie status
- debt rollforward status
- PP&E / D&A tie status
- working capital tie status
- scenario switch status
- sensitivity status
- Excel error scan status

Use pass / fail / not tested / not applicable.

### 5. Senior judgment notes

Call out what a CFO, Portfolio Manager, lender, or IC member would challenge first.

Examples:

- revenue ramp depends heavily on sales capacity expansion
- margin improvement assumes procurement savings not yet sourced
- working capital release is aggressive relative to historical DSO / DIO / DPO
- capex may be too low to support planned growth
- debt paydown depends on downside case not materializing
- liquidity is tight even before covenant pressure

### 6. Open questions and limitations

List missing inputs that affect reliability. Be explicit about whether limitations reduce confidence.

Common limitations:

- incomplete historical financials
- missing KPI data
- unavailable debt agreement details
- missing capex plan
- unknown tax attributes
- no source for management assumptions
- external links, macros, add-ins, or queries not fully inspectable

### 7. Recommended next steps

Prioritize actions, such as:

1. Replace placeholder assumptions with source data.
2. Confirm debt terms and covenant definitions.
3. Validate revenue drivers with sales / operations leadership.
4. Review working capital assumptions against actual aging reports.
5. Add sensitivities for the highest-risk drivers.
6. Re-run QA after updates.

## Sign-off statements

Use one of these styles.

- `This model is not decision-ready until the blocker and high-severity issues above are fixed and retested.`
- `This model appears usable with caveats in the tested scope, subject to the limitations noted above.`
- `No issues found in tested scope, but this is not a guarantee outside the reviewed scope, linked logic, and tested scenarios.`
- `The model is mechanically tied in the tested scenarios, but output reliability depends on replacing the placeholder assumptions noted above.`

## Findings table format

When reporting issues, use this table.

| # | Severity | Type | Sheet / Range | Issue | Evidence | Impact | Recommended fix |
| --- | --- | --- | --- | --- | --- | --- | --- |

Severity options:

- Blocker
- High
- Medium
- Low
- Question

Issue type options:

- formula error
- hardcode / override
- broken link
- inconsistent formula
- range boundary issue
- missing control
- statement tie failure
- scenario issue
- sensitivity issue
- assumption risk
- reasonableness concern
- missing source data

## Dashboard output standards

A senior-quality dashboard should include the most decision-relevant metrics.

Common dashboard sections:

- scenario selector / active case
- revenue, EBITDA, FCF, cash, debt, leverage
- period-over-period growth and margins
- liquidity and covenant indicators
- key assumptions
- downside vs base variance
- top sensitivities
- check status

Dashboard outputs should link to the model engine, not retype values.

## Model review questions

Before final sign-off, answer internally:

- Do the financial statements tie?
- Are assumptions visible and editable?
- Can a reviewer trace output back to drivers?
- Does downside stress affect liquidity and leverage correctly?
- Are open questions listed clearly?
- Are unsupported assumptions labeled as placeholders?
- Are the most important risks obvious to a senior reader?

If the answer to any question is no, improve the workbook or flag the limitation.

## Equity PM Review Output

Review output should lead with estimate revision path, EPS/FCF sensitivity, valuation handoff, current-price relevance, downside equity impairment, and action rules. Do not lead with lender-style covenant headroom unless that is the proximate common-equity risk; if covenant mechanics are the deliverable, use Credit Markets.
