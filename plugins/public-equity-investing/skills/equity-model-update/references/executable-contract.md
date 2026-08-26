# Equity Model Update Executable Contract

Use `scripts/materialize_workbook_update.py` when the user supplies an Excel model and source/model mapping rows. Use `scripts/materialize_model_update.py` only when no workbook is supplied or the user explicitly wants support/control artifacts only.

## Boundary

The workbook helper creates a copied workbook package. It does not fetch market data, mutate the original workbook, choose investment assumptions, rebuild formulas, or replace `model-audit-tieout`.

Formula integrity, external links, circularity, model checks, and final workbook reliability still route to `model-audit-tieout`. When mapped cells are unsafe, the helper produces a workbook control pack instead of editing model cells.

## Workbook Command

```bash
python scripts/materialize_workbook_update.py input.csv --workbook uploaded_model.xlsx --out output --run-date 2026-05-12 --stale-days 45
```

Workbook modes:

- `xlsx_update_copy`: writes safe mapped input-cell updates into `updated_model.xlsx`.
- `xlsx_control_pack`: writes review/control tabs into `model_update_control_pack.xlsx`, opens on `Update_Cover`, and leaves model cells unchanged.

## Support-Only Command

```bash
python scripts/materialize_model_update.py input.csv --out output --run-date 2026-05-12 --stale-days 45
```

## Input CSV

Required columns:

- `source_id`
- `model_line`
- `source_metric`
- `source_value`

Recommended columns:

- `company`
- `ticker`
- `fiscal_period`
- `model_section`
- `workbook_sheet`
- `workbook_cell`
- `current_model_value`
- `prior_value`
- `source_name`
- `source_location`
- `evidence_label`
- `as_of_date`
- `confidence`
- `update_action`
- `mapping_treatment`: `safe_update`, `reference_only`, `missing_model_architecture`, `assumption_required`, or `rebuild_required`
- `overwrite_formula_allowed`
- `earnings_basis` or `gaap_flag` for EPS/net-income rows
- `notes` for tax, share-count, below-the-line, non-operating, or non-recurring EPS items

Legacy workbook-intent columns:

- `workbook_write_requested`
- `direct_workbook_write`
- `write_to_workbook`

Any truthy value in a legacy workbook-intent column is treated as a handoff reminder in the support-only helper. For workbook editing, use `materialize_workbook_update.py`; it always writes to a copy.

Workbook updater safety behavior:

- Only `safe_update` rows carry proposed values and deltas into the update/change path. `reference_only` rows remain informational, while missing-architecture and rebuild-required rows remain blocked without becoming estimate changes.
- Updates mapped target cells only when `workbook_sheet` and `workbook_cell` are exact and present.
- Preserves the original uploaded workbook.
- Blocks protected sheets, missing sheets, missing cells, merged cells, stale prior values, missing new values, and formula cells unless `overwrite_formula_allowed` is explicit.
- Adds review tabs: `Update_Cover`, `Source_Map`, `Rebuild_Requirements`, `Change_Log`, `Tie_Out`, and `Stale_Data`.
- Emits `model_update_citations.json` with workbook/sheet/cell provenance for applied and blocked targets.

## Outputs

`updated_model.xlsx`

Primary human deliverable when at least one mapped model-input cell was safely updated in the copied workbook.

`model_update_control_pack.xlsx`

Primary human deliverable when no model cells could be safely edited. It preserves the workbook and adds review/control tabs.

If a reader-facing workbook is restyled, renamed, or re-exported after this helper runs, it replaces the intermediate workbook as `primary_human_deliverable`. Before handoff, update `run_log.json`, `manifest.json`, and `model_update_citations.json` to use the final workbook path and any final sheet names.

`source_to_model.csv`

Maps each supplied source row to a model line with treatment, source value, proposed value and delta only when updateable, workbook target, applied/blocked/reference-only status, freshness status, confidence, and issue flags.

`change_log.csv`

Includes only rows that require update, add/map, or input-required review. Every change row marks `requires_model_audit_tieout=yes`.

`tieout_checklist.csv`

Always includes a first-row handoff to `model-audit-tieout`, plus per-line source/model tie-out checks and freshness checks where needed. `reference_only` rows are informational/caveated rather than blocked update failures.

`run_log.json`

Records status, artifact readiness, model readiness, generated time, input path, output paths, warnings, hard failures, workbook preflight, update counts, and the capability boundary. A review-ready control pack does not imply an updated model.

## Failure Rules

Hard failure:

- missing `source_id`
- missing `model_line`
- malformed or empty input CSV

Warning / issue flag:

- stale source data
- missing `as_of_date`
- missing `source_metric`
- missing/non-numeric proposed value
- EPS/net-income row missing basis
- EPS/net-income row whose notes indicate non-operating or non-recurring items that require EPS-quality review
- workbook update requested through the support-only helper

Workbook control-pack blockers:

- target sheet or cell missing
- protected sheet
- merged target cell
- formula target without explicit overwrite approval
- supplied prior value does not match the workbook cell
- macro-enabled workbook requiring manual review
- input validation failures

## Handoff

After materialization, send workbook formula integrity, output reliability, and final model tie-out to `model-audit-tieout`. Send source hierarchy or stale-source conflicts to `financial-source-of-truth`.
