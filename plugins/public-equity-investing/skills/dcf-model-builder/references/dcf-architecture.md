# DCF Architecture and Excel Build Standards

## Purpose

Use this reference when creating a new DCF workbook, adding a DCF module to an existing model, or improving the structure of a partial DCF.

Current shipped behavior has two explicit paths: `scripts/build_banker_formula_workbook.py` is the default user-facing path and materializes the bundled live-formula template as `banker_formula_workbook`; the local deterministic pipeline produces a values-based `deterministic_export` support workbook for controlled computed values, smoke tests, explicit lightweight exports, or honest fallback. Do not claim the deterministic pipeline creates a fully linked formula workbook.

## Architecture principles

- Make the model easy to understand before making it complex.
- Keep assumptions visible and editable.
- For formula-workbook builds, keep calculations formula-driven and consistent across periods. In the shipped deterministic export, preserve formula intent through `formula_basis`, checks, and source labels rather than live Excel formulas.
- Keep outputs separated from inputs and calculations.
- Build to the decision, not to a generic template.
- Preserve a sound existing workbook structure where possible.
- Rebuild only when the existing structure prevents reliable valuation.

## Recommended workbook tabs for manual/formula workbooks

Use these tabs for a full standalone DCF, adapting to the complexity of the assignment.

| Tab | Purpose |
| --- | --- |
| `README` or `Model Guide` | Explain purpose, scope, data sources, limitations, and how to use the model. |
| `Control Panel` | Valuation date, currency, units, selected case, discounting convention, output toggles. |
| `Sources` | Source documents, market data, filing references, user assumptions, and unresolved data needs. |
| `Historical` | Historical financials and KPIs, clearly separated from forecasts. |
| `Adjustments` | Normalization adjustments, non-recurring items, accounting changes, restatements. |
| `Assumptions` | Forecast drivers by case. |
| `Forecast` | Revenue, margins, operating expenses, EBIT, taxes, D&A, capex, working capital. |
| `FCF` | FCFF, FCFE, or other cash flow build depending on method. |
| `WACC` | Cost of equity, cost of debt, tax shield, capital structure, discount rate. |
| `Terminal Value` | Perpetuity growth, exit multiple, terminal assumptions, and implied metrics. |
| `Valuation Bridge` | PV of FCF, PV of terminal value, EV, bridge to equity value, per-share value. |
| `Sensitivity` | Data tables and driver sensitivities. |
| `Scenarios` | Base, downside, upside, and custom case logic. |
| `Checks` | Formula, tie-out, scenario, sensitivity, and valuation-control checks. |
| `Dashboard` | Executive summary, valuation range, key drivers, charts, and caveats. |

For an existing 3-statement model, a DCF module may need only `DCF`, `WACC`, `Sensitivity`, and `Checks` tabs if forecast schedules already exist.

## Existing workbook integration

When the user already has a DCF or forecast model:

1. Map the existing forecast engine.
2. Identify the true source of forecast values.
3. Link the DCF to the existing case or scenario control.
4. Preserve existing user inputs that are coherent and labeled.
5. Replace buried hardcodes with linked assumptions when appropriate.
6. Add missing checks and sensitivities.
7. Do not create duplicate valuation engines unless the user asks for a clean rebuilt version.
8. If the existing structure is unreliable, explain why and build a cleaner module.

## Input and formula conventions for manual/future formula workbooks

Use the user's existing convention if it is clear and consistent. Otherwise use these conventions:

- Inputs / assumptions: visually distinct from formulas.
- Formulas: copied consistently across forecast periods.
- Links to other tabs: clearly traceable.
- Hardcodes inside formulas: avoid unless standard constants or explicitly justified.
- Placeholders: visibly marked and included in a missing-data list.
- Source references: add comments or source notes where practical.
- Time periods: use one consistent date spine.
- Units: repeat units on every major tab and output section.
- Cases: scenario switches must change calculation cells, not merely dashboard labels.

## Formula design standards for manual/future formula workbooks

- Use simple formulas over clever formulas.
- Avoid deeply nested logic when helper rows improve auditability.
- Avoid volatile functions unless needed.
- Avoid `INDIRECT` and `OFFSET` where direct links or structured ranges are safer.
- Use named ranges only when they improve readability and are maintained correctly.
- Avoid entire-column references in large models when performance matters.
- Build checks close to the logic they test and summarize them on `Checks` or `Dashboard`.

## Time horizon and granularity

Choose granularity based on the business and decision.

- Annual: typical mature public-company DCF, high-level valuation, board estimate.
- Quarterly: public-company updates, businesses with near-term inflection, covenant or liquidity relevance.
- Monthly: distressed, startup runway, project finance, working-capital-heavy businesses, seasonal businesses, or transaction models needing detailed cash timing.

Choose horizon based on when the company reaches a defensible steady state.

- Mature company: often 5 years.
- High-growth company: often 7 to 10 years if fade to steady state needs time.
- Turnaround: long enough to show stabilization and normalized cash flow.
- Asset / project model: match project life, concession term, or asset economics.

## Dashboard standards

The dashboard should not be decorative. It should answer the senior decision-maker's questions:

- What is the valuation range?
- What drives the value?
- What is the most important assumption?
- How much of value comes from the terminal value?
- Does downside still support the decision?
- What assumptions are unsupported or require diligence?
- What cross-checks support or contradict the DCF?

Recommended dashboard elements:

- valuation range chart
- base / downside / upside valuation table
- WACC x terminal growth sensitivity
- value bridge from enterprise value to equity value
- key operating forecast metrics
- FCF conversion trend
- terminal value share of enterprise value
- key caveats and open questions
