# Output Specification

## Default generated files

The default model-build path is the banker formula workbook path. It writes:

- `banker_formula_workbook.xlsx`
- `banker_formula_workbook_run_log.json`
- `model_citations.json`
- `manifest.json`

The deterministic support pipeline remains available for explicit lightweight runs, controlled computed values, smoke tests, and honest fallback exports. It must produce:

- `output/model.xlsx`
- `output/plan.json`
- `output/run_log.json`
- `output/manifest.json`

It may also produce:

- `output/support_note.md` as an optional support note or renderer input. Legacy `output/report.md` is written only with `--write-report-md`. Do not use Markdown as the lead user-facing deliverable when the workbook is the requested artifact.

## Workbook mode

Two workbook modes are supported:

- `banker_formula_workbook`: default live formula workbook produced only by `scripts/build_banker_formula_workbook.py`.
- `deterministic_export`: values-based support workbook produced by `scripts/run_pipeline.py` for controlled computed values, smoke tests, explicit lightweight exports, or clearly labeled fallback.

Do not call the deterministic workbook a fully linked banker model. Formula mode may be claimed only when `banker_formula_workbook_run_log.json` confirms `workbook_mode: "banker_formula_workbook"`, required sheets/formulas/styles/no-external-link checks pass, and `model_citations.json` exists.

## Formula-mode files

Formula mode is the default for user-facing model builds and writes:

- `banker_formula_workbook.xlsx`
- `banker_formula_workbook_run_log.json`
- `model_citations.json`
- `manifest.json`

`model_citations.json` contains source-to-cell provenance for key operating-model outputs. Each record should include workbook path, sheet, cell/range, formula, value when known, scenario, section, line item, source ID, evidence label, source label, source date/freshness, and optional URL.

If formula mode fails its truthfulness gate, do not call the fallback a banker workbook. Either fix formula mode, mark the run `not-decision-ready`, or use `deterministic_export` with the limitation stated loudly.

## Deterministic support workbook sheets

`model.xlsx` contains:

- `Cover`: first visible PM/analyst dashboard tab required by `shared/workbook-artifact-standard.md`; includes model status, workbook mode, source posture, warnings/hard failures, base/downside/upside final-period metrics, liquidity trough, driver summary, QA posture, and workbook map.
- `Summary`: scenario-level final-period outputs.
- `Model`: long-format model rows for all scenarios.
- `Sensitivities`: selected stress/sensitivity cases.
- `Checks`: machine-computed tie-out checks.
- `Assumptions`: source-labeled assumptions from the normalized plan.
- `Sources`: source basis entries.
- `Run_Log`: status and issue counts.

`output/manifest.json` mirrors `run_log.json.output_manifest` and records required artifacts, paths, and whether each artifact was written.

## Long-format schema

The `Model` sheet uses:

- `scenario`
- `statement`
- `section`
- `line_item`
- `period`
- `value`
- `unit`
- `evidence_label`
- `source_id`
- `formula_basis`
- `notes`

Required statement groups:

- `IS`
- `BS`
- `CF`
- `DEBT`
- `WORKING_CAPITAL`
- `PPE`
- `COVENANTS_LIQUIDITY`
- `CHECKS`

Required line items include:

Income statement:
- revenue
- COGS
- gross profit
- opex
- EBITDA
- D&A
- EBIT
- interest
- EBT
- taxes
- net income

Balance sheet:
- cash
- AR
- inventory
- other current assets
- PP&E
- debt
- AP
- accrued expenses
- deferred revenue
- common equity
- retained earnings
- total assets
- total liabilities and equity
- balance check

Cash flow:
- net income
- D&A
- deferred tax
- change in working capital
- CFO
- capex
- debt draws
- debt repayments
- dividends
- buybacks
- issuance
- cash change
- ending cash

Debt:
- beginning debt
- scheduled draws
- required draws
- total draws
- mandatory repayment
- optional repayment
- interest
- ending debt
- revolver availability
- minimum cash

Working capital:
- AR days
- inventory days
- AP days
- NWC
- change in NWC

PP&E:
- beginning PP&E
- capex
- depreciation
- disposals
- ending PP&E

Checks:
- balance sheet check
- cash tie check
- retained earnings roll-forward
- debt roll-forward
- PP&E roll-forward
- NWC roll-forward

## Run log schema

`run_log.json` must contain:

```json
{
  "status": "completed",
  "model_status": "screen-grade",
  "workbook_mode": "deterministic_export",
  "artifact_level": "deterministic_export",
  "source_basis": [],
  "hard_failures": [],
  "warnings": [],
  "assumptions": {},
  "checks": {},
  "outputs": {},
  "output_manifest": [],
  "p0_handoff": {}
}
```

`status` is `completed` when the helper ran without hard failures and `failed` when validation or execution blocks decision use.

Allowed `model_status` values:

- `decision-grade`
- `senior-review-ready`
- `screen-grade`
- `not-decision-ready`
- `blocked`

If `hard_failures` is non-empty, `status` must be `failed` and `model_status` must be `not-decision-ready`.

## Support report template

When `output/support_note.md` is enabled, it is a review support note. The workbook `Cover` is the first user-facing landing page. The support note should include:

1. Model status, workbook mode, artifact level, as-of date, accounting basis, and units.
2. Scenario summary table for base/downside/upside.
3. Base case operating read-through.
4. QA hard failures and warnings.
5. Sensitivity outputs.
6. Source posture.
7. Files produced.

## Downstream P0 handoff

`p0_handoff` must include:

- operating forecast summary
- base/downside/upside revenue, EBITDA, FCF, and ending cash
- liquidity trough
- key operating drivers
- checks passed/failed
- model status
- paths to workbook, plan, run log, manifest, and optional support note/report
