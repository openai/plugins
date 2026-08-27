# Equity Model Update Templates

## Model Refresh Summary

```markdown
# [Company] ([Ticker]) Equity Model Update - [Period]

## Bottom line
[What changed, which model lines move, and whether this is ready for analyst review.]

## Source/data-quality note
| Source | Source ID | Date | Label | Freshness | Caveat |
|---|---|---:|---|---|---|

## Source-to-model map
| Source metric | Model section | Model line | Workbook target | Current | Proposed | Delta | Label | Confidence | Workbook status | Issue flags |
|---|---|---|---|---:|---:|---:|---|---|---|---|

## EPS-quality bridge when EPS lines move
Use when any updated model line touches EPS, net income, tax rate, share count, or below-the-line income/expense.

| Step | Source metric / model line | Value | Evidence label | Treatment | Source ID | Confidence |
|---|---|---:|---|---|---|---|
| Reported GAAP diluted EPS |  |  | fact_source_reported | Starting point |  |  |
| Adjusted / operating EPS, if provided |  |  | management_adjusted | Compare definition and reconciliation |  |  |
| Non-operating / non-recurring items |  |  | analyst_adjusted / issuer_management_claim | Exclude, isolate, or monitor |  |  |
| Tax and diluted share-count effects |  |  | derived_calculation | Normalize only with support |  |  |
| Recurring EPS driver change |  |  | analyst_interpretation | Update forward EPS only if recurring |  |  |

## Change log
| Change | Model line | Workbook target | Action | Reason | Source ID | Status | Applied to copy | Tie-out required |
|---|---|---|---|---|---|---|---|---|

## Tie-out checklist
| Check | Area | Model line | Workbook target | Owner | Status | Handoff |
|---|---|---|---|---|---|---|
```

## Pre-Print Model Checklist

```markdown
## Core question
[What will arbitrate the model or stock debate?]

## Threshold table
| Metric | Bear / thesis break | In line | Bull / upside | Model line | Why it matters |
|---|---:|---:|---:|---|---|

## Consensus / guidance / user model
| Metric | Last actual | Company guide | Consensus | User model | User vs street | Importance |
|---|---:|---:|---:|---:|---:|---|

## Post-print update plan
| When | Item to update | Source | Model line | Handoff |
|---|---|---|---|---|
```

## Post-Release / Pre-Call Questions

Use model-linked questions only:

| Question | Model line affected | Why it matters | Bullish answer | Bearish answer |
|---|---|---|---|---|

## Executable Input CSV

Minimum columns:

- `source_id`
- `model_line`
- `mapping_treatment`: `safe_update`, `reference_only`, `missing_model_architecture`, `assumption_required`, or `rebuild_required`

Recommended columns:

- `company`
- `ticker`
- `fiscal_period`
- `model_section`
- `workbook_sheet`
- `workbook_cell`
- `source_metric`
- `source_value`
- `current_model_value`
- `prior_value`
- `proposed_model_value`
- `source_name`
- `source_location`
- `evidence_label`
- `as_of_date`
- `confidence`
- `overwrite_formula_allowed`
- `earnings_basis` or `gaap_flag` for EPS-related rows
- `notes` for tax, share-count, below-the-line, non-operating, or non-recurring EPS issues

Only `safe_update` rows should carry `proposed_model_value`, `new_value`, or estimate-change deltas. Use `reference_only` for source facts that are decision-relevant but not valid replacements for a workbook input, including incompatible period comparisons or facts mapped only to output formulas.

Legacy workbook-intent columns treated as handoff reminders in the support-only helper:

- `workbook_write_requested`
- `direct_workbook_write`
- `write_to_workbook`

## Workbook Output Tabs

When a workbook is supplied, lead with either `updated_model.xlsx` or `model_update_control_pack.xlsx`.

Required review tabs:

- `Update_Cover`: preflight status, applied/blocked/reference-only counts, artifact versus model readiness, warnings, handoff; first visible tab for a control pack.
- `Source_Map`: source-to-model rows with workbook sheet/cell and applied/blocked status.
- `Rebuild_Requirements`: missing architecture, assumption-required, or rebuild-required rows that prevent a refreshed valuation.
- `Change_Log`: change rows with source IDs and tie-out status.
- `Tie_Out`: model-owner checks and handoff skills.
- `Stale_Data`: stale or missing source rows.

Support artifacts:

- `source_to_model.csv`
- `change_log.csv`
- `tieout_checklist.csv`
- `model_update_citations.json`
- `run_log.json`
- `manifest.json`
