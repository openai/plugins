# Sensitivities, Scenarios, and Pressure Tests

## Purpose

Use this reference to make DCF outputs decision-ready rather than static.

## Scenario design

Build at least base, downside, and upside cases unless the user asks for a narrower model.

A scenario should change the economic drivers, not just the labels.

Base case:

- reasonable forecast supported by history, management inputs, and modeler judgment
- not automatically management's most optimistic plan

Downside case:

- tests the key risks in the investment thesis
- includes adverse revenue, margin, working capital, capex, and discount-rate assumptions where relevant
- should not preserve all upside initiatives while slightly reducing growth

Upside case:

- reflects credible outperformance
- should not assume impossible market share, margin, or capital efficiency

## Required sensitivities

For most DCFs, include:

- WACC x terminal growth
- WACC x exit multiple, if exit multiple method is used
- revenue growth x EBITDA margin or EBIT margin
- FCF conversion or capex sensitivity when capital intensity matters
- downside / base / upside valuation range

For public companies, consider:

- value per share sensitivity
- premium / discount to current market price, if current market price is available and verified

For transaction work, consider:

- purchase price sensitivity
- exit value sensitivity
- leverage or financing sensitivity if linked to valuation use case

## Pressure tests

Run relevant pressure tests before sign-off.

### Directional test

Change a key driver and confirm valuation moves in the expected direction.

Examples:

- higher WACC lowers value
- higher terminal growth raises value
- lower margin lowers value
- higher capex lowers FCFF
- longer working capital days lowers near-term FCF

### Scenario switch test

Confirm that selecting base, downside, or upside changes the actual forecast engine and DCF output.

Flag as High or Blocker if scenario labels change but the calculations do not.

### Sensitivity linkage test

For the shipped deterministic export, confirm sensitivity rows were regenerated from the active plan, scenario outputs, and valuation engine rather than pasted from stale files. For user-provided workbooks or future formula-workbook builders, confirm data tables or sensitivity formulas point to live valuation outputs and active assumption cells.

Flag as High if sensitivity outputs are pasted values, stale, or linked to the wrong case.

### Terminal value concentration test

Calculate terminal value as a percentage of enterprise value.

High terminal value share is not automatically wrong, but it means the conclusion depends heavily on terminal assumptions. Flag when the terminal value share is high and the terminal assumptions are weakly supported.

### Reverse DCF test

When helpful, ask what growth, margin, WACC, or terminal assumptions are required to justify a target valuation or market price.

Use this to distinguish:

- cheap because assumptions are conservative
- expensive because expectations are high
- apparently cheap because the model contains unsupported assumptions

### Downside survivability test

For levered, distressed, or cash-burning companies, test whether the company remains liquid or financeable in downside assumptions.

Flag if the valuation assumes survival but the model does not show the funding path.

## Sensitivity presentation standards

- Label rows and columns clearly.
- State units and assumptions.
- Use regenerated deterministic outputs in the shipped pipeline. Use live formulas or data tables only when reviewing an existing workbook or when a future formula-workbook builder is present.
- Highlight base case within sensitivity tables when possible.
- Avoid sensitivities around immaterial drivers.
- Prioritize the two or three assumptions that determine the valuation conclusion.

## Common weak sensitivity designs

Flag these issues:

- sensitivities only around terminal growth and WACC when the main uncertainty is revenue or margins
- cases that are too close together to matter
- upside and downside cases that are symmetrical despite asymmetric risks
- static sensitivity tables not linked to the model
- sensitivities that use stale terminal values or wrong forecast cases
- too many sensitivities that obscure the few important drivers
