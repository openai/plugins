# QA Checks

## Hard failures

Hard failures make the model `not-decision-ready`:

- Balance sheet does not balance.
- Ending cash does not tie to the cash flow statement.
- Retained earnings roll-forward fails.
- Debt roll-forward fails.
- PP&E roll-forward fails.
- Working capital roll-forward fails.
- Scenario switch changes labels but not model outputs.
- `source_basis` is missing for material historicals or forecast drivers.
- Required plan schema fields are absent or impossible.

## Warnings

Warnings lower confidence but may still allow a useful screen:

- Aggressive revenue ramp.
- Unsupported margin expansion.
- Working capital release inconsistent with history.
- Capex too low for growth.
- Liquidity trough or covenant issue.
- Placeholder assumptions still active.
- Negative cash or heavy revolver dependence.
- Historical source dates and forecast assumptions are stale or mismatched.

## Status logic

- Any hard failure: `not-decision-ready`.
- Placeholder assumptions active but no hard failures: `screen-grade`.
- No hard failures but warnings remain: `senior-review-ready`.
- No hard failures, no warnings, and high-quality source labels: `decision-grade`.

## Senior review checklist

A veteran reviewer should inspect:

- Whether revenue is tied to the actual business engine.
- Whether gross margin expansion is supported by mix, pricing, utilization, procurement, or cost evidence.
- Whether opex leverage is organizationally plausible.
- Whether DSO, DIO, and DPO changes are supportable.
- Whether capex supports growth and replacement needs.
- Whether cash taxes differ materially from book taxes.
- Whether the debt schedule, interest, revolver availability, and cash sweep behave correctly.
- Whether downside assumptions are correlated rather than simplistic.
- Whether the model explains what breaks first.
