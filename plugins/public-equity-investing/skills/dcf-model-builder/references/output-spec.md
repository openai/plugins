# Output Specification

## Default generated files

The default model-build path is the banker formula workbook path. It writes:

- `banker_formula_workbook.xlsx`
- `banker_formula_workbook_run_log.json`
- `model_citations.json`
- `manifest.json`

The deterministic support pipeline remains available for explicit lightweight runs, controlled computed values, smoke tests, and honest fallback exports. It writes:
- `output/model.xlsx`
- `output/plan.json`
- `output/run_log.json`
- `output/manifest.json`

It may also write `output/support_note.md` as an optional support note or renderer input. Legacy `output/report.md` is written only with `--write-report-md`. Do not use the Markdown note as the lead user-facing deliverable when the workbook is the requested artifact.

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

`model_citations.json` contains source-to-cell provenance for key valuation outputs. Each record should include workbook path, sheet, cell/range, formula, value when known, scenario, section, line item, source ID, evidence label, source label, source date/freshness, and optional URL.

If formula mode fails its truthfulness gate, do not call the fallback a banker workbook. Either fix formula mode, mark the run `not-decision-ready`, or use `deterministic_export` with the limitation stated loudly.

## Deterministic support XLSX sheets
The bundled workbook uses value-based long-format sheets:

### `Cover`
First visible workbook tab. Required by `shared/workbook-artifact-standard.md`.

The cover is a PM/analyst dashboard, not a raw data table. It must summarize company, model type, valuation date, currency/units, model status, workbook mode, hard failures, warnings, selected valuation range, scenario value/share outputs, base-case DCF bridge, WACC/terminal assumptions, sensitivity drivers, source posture, and a workbook map.

If the stdlib writer cannot create native charts, the cover must still include chart-ready scenario, bridge, and sensitivity rows.

### `Summary`
One row per scenario with EV, equity value, value per share, WACC/cost of equity, terminal value, PV of FCF, PV of terminal value, and terminal value percent of EV.

### `Model`
Long-format valuation rows. Required columns:
- `section`
- `line_item`
- `scenario`
- `period`
- `value`
- `units`
- `evidence_label`
- `source_id`
- `notes`

Required sections/rows include:
- `IS`: revenue, EBITDA, EBIT, taxes
- `FCF`: NOPAT, D&A, capex, change in NWC, unlevered FCF or FCFE
- `WACC`: cost of equity, cost of debt, tax rate, target capital structure, WACC
- `TV`: terminal value, PV of terminal value, TV percent of EV
- `VALUATION`: PV of FCF, EV, equity value, diluted shares, value per share
- `CHECKS`: DCF QA checks
- `ASSUMPTIONS`: source-labeled assumptions

### `Sensitivities`
Long-format sensitivity outputs. Required columns:
- `sensitivity`
- `x_axis`
- `x_value`
- `y_axis`
- `y_value`
- `metric`
- `value`
- `units`

The pipeline emits WACC/terminal growth, WACC/exit multiple, and revenue-growth/EBIT-margin sensitivity rows.

### `Checks`
Machine-computed hard failures, warnings, and informational checks.

### `Assumptions`
Material source basis and key assumption values.

### `Run Log`
Top-level run status, model status, generated paths, and caveats.

## `run_log.json` schema
The runner writes this shape:

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

`status` is `completed` when the helper ran without hard failures and `failed` when validation or execution blocks decision use. `output_manifest` mirrors `output/manifest.json` and records required artifacts, paths, and whether each artifact was written.

Allowed `model_status` values:
- `decision-grade`
- `senior-review-ready`
- `screen-grade`
- `not-decision-ready`
- `blocked`

Use `blocked` only for pre-run messaging when no run log can be produced. If `hard_failures` is non-empty, `model_status` must be `not-decision-ready`.

## P0 handoff fields
`p0_handoff` must include:
- `selected_valuation_range`
- `scenarios`: base/downside/upside EV, equity value, value per share
- `wacc_and_terminal_assumptions`
- `key_value_drivers`
- `major_caveats`
- `model_status`
- `paths`: workbook, plan, run log, manifest, and optional support note

Formula-mode handoffs must also expose `model_citations` or `model_citations_path` when a dashboard cites workbook cells.

## Support Note Template
When `output/support_note.md` is enabled, it is a support note for review, renderer input, or audit. The workbook `Cover` remains the first user-facing landing page. The support note should include:
1. Model status and artifact level.
2. Valuation range and scenario table.
3. Base-case DCF bridge.
4. WACC and terminal assumptions.
5. Sensitivity summary and key drivers.
6. QA checks: hard failures and warnings.
7. Source-basis notes and caveats.
8. Generated artifact paths, led by the workbook.

The support note must not claim decision-grade status when placeholders, stale data, unsupported WACC, missing source basis, or hard failures are present.
