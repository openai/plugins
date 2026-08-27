# Integrity Controls and QA Reference

Use this reference to prove that the 3-statement model works mechanically and behaves sensibly.

## Required control philosophy

A model is not complete because formulas calculate. It is complete only when the checks prove the statements tie, the scenario engine works, and the outputs behave logically under pressure.

Every material control should show:

- pass / fail status
- variance amount
- affected period
- likely source of issue when possible

## Required mechanical checks

Include these checks for every 3-statement model unless clearly irrelevant.

### Balance sheet balance

Check total assets minus total liabilities and equity for every period. Any non-zero balance is a blocker unless immaterial due to rounding and documented.

### Cash tie-out

Check cash flow ending cash equals balance sheet cash in every period.

### Retained earnings rollforward

Beginning retained earnings plus net income minus dividends and distributions equals ending retained earnings.

### Working capital tie

Changes in operating balance sheet accounts reconcile to the cash flow statement.

Typical checks:

- AR change ties to working capital schedule
- inventory change ties to working capital schedule
- AP change ties to working capital schedule
- accrued expense change ties to working capital schedule
- deferred revenue change ties to working capital schedule, if applicable

### PP&E and D&A tie

Beginning PP&E plus capex minus disposals minus D&A equals ending PP&E, adjusted for gross / accumulated presentation if used.

D&A on the income statement and add-back on the cash flow statement should tie to the D&A schedule.

### Debt rollforward tie

Beginning debt plus draws plus PIK interest minus repayments equals ending debt.

Interest expense should tie to the debt schedule or interest calculation.

### Tax tie

Tax expense, cash taxes, deferred taxes, and NOL usage should be internally consistent if modeled.

### Scenario tie

The selected scenario in the control panel must match the scenario driving calculations and dashboard outputs.

### Formula integrity

Check for:

- formulas replaced by hardcoded values
- inconsistent formulas across periods
- broken references
- Excel error values
- hardcoded assumptions inside formula regions
- hidden rows or sheets driving outputs unexpectedly

## Severity framework

Use this severity ladder in the build review.

| Severity | Meaning | Default action |
| --- | --- | --- |
| Blocker | Core output cannot be trusted; the model does not tie or a key formula chain is broken | Must fix before use |
| High | Material logic issue or fragile behavior likely to mislead decisions | Fix immediately |
| Medium | Local issue, missing control, or weak logic that may distort some outputs | Fix soon |
| Low | Maintainability or transparency issue with limited decision impact | Improve when practical |
| Question | Treatment may be intentional but requires confirmation | Flag clearly |

## Pressure tests

Run the lightest set of tests that materially increases confidence. For model builds, include at least scenario-switch, statement-tie, and key-driver sensitivity tests.

### Base-case retest

Recalculate and confirm all required checks pass in the base case.

### Scenario switch test

Switch each scenario and confirm the actual model engine changes, not just dashboard labels.

Expected behavior:

- downside should generally reduce revenue, EBITDA, FCF, liquidity, and covenant cushion
- upside should generally improve economics unless investments absorb gains
- lender / conservative case should stress cash and leverage more than base case

### Revenue sensitivity

Move a key revenue driver and confirm related outputs move correctly.

Expected effects usually include:

- revenue changes
- working capital changes
- COGS and variable opex changes if applicable
- EBITDA changes
- cash flow changes
- taxes and debt paydown may change downstream

### Margin sensitivity

Change gross margin or operating margin and confirm EBITDA, taxes, cash flow, retained earnings, and cash change correctly.

### Working capital stress

Increase DSO, inventory days, or reduce DPO and confirm cash deteriorates.

### Capex stress

Increase capex and confirm cash flow decreases, PP&E increases, D&A may increase over time, and liquidity responds.

### Debt and liquidity stress

Lower cash generation and confirm revolver, cash sweep, debt paydown, interest expense, and minimum cash logic behave correctly.

Debt should not go negative unless explicitly allowed. Revolver draws should respect limits if limits are modeled.

### Circularity test

If the model uses circularity for interest, cash sweeps, or revolver draws, confirm:

- iterative calculation is enabled if required
- circularity is intentional
- loop converges
- outputs are stable
- the loop is documented

If circularity is accidental, treat it as a blocker.

## Control dashboard

Create a `Checks` tab or checks section that includes:

- statement tie checks
- rollforward checks
- formula integrity indicators
- scenario status
- key source-data tie-outs
- major open assumptions
- model status summary

Recommended model status labels:

- `Pass - no issues found in tested scope`
- `Pass with caveats`
- `Needs fixes`
- `Not decision-ready`

## Common blocker issues

Treat these as blocker-level issues unless immaterial and documented:

- balance sheet does not balance
- ending cash does not tie
- debt schedule does not roll
- retained earnings does not roll
- active Excel errors in key outputs
- scenario switch does not drive calculations
- cash or debt behaves impossibly under stress
- hidden plug required to make statements tie
- formulas overwritten inside critical formula blocks

## Common high-risk issues

Treat these as high severity:

- material hardcoded assumptions inside formulas
- margin expansion with no driver or rationale
- working capital movements with wrong sign
- debt paydown based on EBITDA instead of cash flow
- D&A disconnected from asset base
- tax calculation wrong under losses
- sensitivity table references wrong cells
- dashboard retypes outputs instead of linking to model
- inconsistent date periods across schedules

## QA sign-off requirement

Before presenting the model as usable, state:

- which checks passed
- which checks failed
- what was pressure-tested
- what remains assumption-dependent
- what limitations remain due to missing source data, opaque macros, external links, add-ins, or unavailable details
