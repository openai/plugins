# Banker Formula Workbook Contract

Formula mode is the default user-facing model-build path. It materializes `assets/templates/banker_formula_workbook_template.xlsx`, preserves the template's formulas, tabs, styles, and checks, then writes plan-derived inputs, source labels, scenario controls, and Public Equity Investing posture warnings.

Run with:

```bash
python3 scripts/build_banker_formula_workbook.py path/to/plan.json --output-dir output
```

Formula-mode outputs:

- `banker_formula_workbook.xlsx`
- `banker_formula_workbook_run_log.json`
- `model_citations.json`
- `manifest.json`

The workbook is the human deliverable. The run log, manifest, and citation ledger are support/audit artifacts. The JSON artifacts are not the user-facing deliverable unless the user asks for the audit files directly. `model_citations.json` must validate against the Public Equity Investing model-citation schema before dashboard handoff.

## Truthfulness Gate

Only call an artifact `banker_formula_workbook` when all of the following are true:

- the formula builder ran;
- `banker_formula_workbook.xlsx` exists;
- required sheets are present;
- formula count clears the model-specific inspection threshold;
- required formula-bearing sheets are populated;
- `Cover` is the first visible sheet;
- named ranges or `model_citations.json` provide a stable source-to-cell anchor map;
- styles are preserved;
- no external workbook links are present;
- the formula run log says `workbook_mode: "banker_formula_workbook"`;
- `model_citations.json` exists with sheet/cell-level provenance for key outputs.

If any gate fails, do not label the deterministic export or partial output as a banker formula workbook. Fall back honestly to `deterministic_export`, or mark the formula-mode run `not-decision-ready`.

## Required Workbook Shape

Required sheets:

- `Cover`
- `Executive Summary`
- `Control Panel`
- `Historical Financials`
- `Revenue Build`
- `Expense Build`
- `Income Statement`
- `Working Capital`
- `PP&E D&A`
- `Debt Interest`
- `Tax`
- `Balance Sheet`
- `Cash Flow Statement`
- `Scenarios`
- `Checks`
- `Source Notes`

The `Cover` sheet must remain first and must carry public-company operating-model context: issuer/ticker when available, forecast date, source posture, placeholder warnings, model mode, final-period outputs, liquidity/debt posture, checks, and workbook map.

## Source-To-Cell Provenance

`model_citations.json` is the handoff from workbook generation to dashboards. Each record should include workbook path, sheet, cell or range, value when known, formula where available, scenario/case, line item, section, source ID, evidence label, source label, source date/freshness, and optional URL.

Dashboards may cite model cells such as `Income Statement!I6`, `Balance Sheet!I22`, or `Checks!C6` instead of generic "model output." Keep the citation ledger as a support artifact; hero the workbook or rendered dashboard for the end user.

## Limitations

Formula mode preserves and populates the bundled three-statement template. It does not synthesize arbitrary new tabs, evaluate Excel formulas in Python, or guarantee every user-specific model architecture. Use formula mode by default for user-facing model builds; use deterministic mode only for controlled computed values, smoke tests, explicit lightweight support exports, or honest fallback when formula mode is unavailable.
