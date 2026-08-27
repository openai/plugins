# Workbook Output Specification

Use this reference when producing an Excel deliverable.

## Default Workbook Tabs

### `Cover`

The first visible tab when producing a polished `.xlsx` deliverable. Required by `shared/workbook-artifact-standard.md`.

Recommended content:

- input file and workbook mode;
- source sheets cleaned;
- clean row and column counts;
- inferred domain/grain where available;
- quality issue count and fatal/warning count;
- major cleaning actions, dedupe policy, header policy, subtotal policy;
- raw-source preservation status;
- workbook map for clean, raw, dictionary, quality, and audit tabs;
- downstream-use limitations, source gaps, unsupported connector/provider gaps, and Credit Markets handoff flags that should remain visible.

### `clean_data`

The primary analysis-ready table.

Requirements:

- One row per intended grain.
- Unique, clear headers.
- Excel table with filters enabled.
- Freeze top row.
- Real dates/numbers/percentages where safe.
- IDs preserved as text.
- No decorative title rows, blank bands, or report-only subtotal rows unless intentionally preserved.
- Add flags for uncertain records rather than hiding them.

### `raw_source`

A copy of the unmodified source data.

Requirements:

- Keep original order and values.
- If multiple input sheets exist, use `raw_source_<sheet>` or preserve all raw sheets with clear names.
- Do not apply cleaning transformations here except minimal formatting for readability.

### `data_dictionary`

A field-level reference for reviewers and downstream users.

Recommended columns:

- `source_sheet`
- `original_field`
- `clean_field`
- `inferred_type`
- `excel_format`
- `null_count`
- `unique_count`
- `example_values`
- `cleaning_notes`
- `business_notes`

### `quality_checks`

A reviewer-oriented issue log.

Recommended columns:

- `severity`: fatal, warning, info.
- `issue_type`: missing_required_field, duplicate_key, mixed_type, outlier, invalid_date, subtotal_row, etc.
- `field`
- `affected_rows`
- `affected_count`
- `description`
- `recommended_action`

Severity guidance:

- **fatal:** prevents reliable use for the stated objective.
- **warning:** usable, but reviewer should inspect or resolve.
- **info:** notable cleaning action or low-risk observation.

### `assumptions_audit`

A transformation and assumption log.

Recommended columns:

- `step`
- `action`
- `basis`
- `affected_sheet`
- `affected_field`
- `affected_rows_or_count`
- `risk_level`
- `notes`

Include both user-directed and inferred assumptions.

### `summary` optional

Use when the user wants a polished deliverable or the data has non-obvious risks.

Recommended content:

- dataset overview.
- key cleaning actions.
- top quality risks.
- recommended next steps.

Do not add analytical conclusions unless requested or naturally part of the task.

## Naming and Formatting

### Sheet names

Use lowercase with underscores, max 31 characters, unique:

- `clean_data`
- `raw_source`
- `data_dictionary`
- `quality_checks`
- `assumptions_audit`
- `summary`

### Header formatting

- Bold header row.
- Filters enabled.
- Freeze top row.
- Wrap header text only when needed.
- Use concise labels.

### Column widths

- Use width based on content with reasonable minimum/maximum.
- IDs and codes: 12-24.
- Names/descriptions/notes: 24-60.
- Amounts/dates/status: 12-18.

### Number formats

- Integer counts: `#,##0`.
- Amounts where currency is known and uniform: `$#,##0` or `$#,##0.00` depending on precision.
- Amounts with multiple currencies: numeric format plus separate currency column; avoid a single currency symbol.
- Percentages: `0.0%` or `0.00%` depending on domain.
- Dates: `yyyy-mm-dd`.
- Month periods: `yyyy-mm` or `mmm-yy` if the value is truly a date bucket.

### Conditional indicators

Use flags and issue sheets instead of relying only on colors. Color formatting can help, but the workbook must remain understandable without it.

## Deliverable QA

Before delivering:

- Open or inspect the workbook after writing.
- Confirm all expected sheets are present.
- Confirm table dimensions and headers are plausible.
- Confirm raw source is preserved.
- Confirm formulas, if any, are not broken.
- Confirm quality checks and audit sheets are populated or explicitly state when no issues were found.
- Confirm file size is reasonable and workbook is not corrupted.


If a workbook includes credit-instrument data, the Cover and `quality_checks` tabs should mark `route_to_credit_markets` unless the credit data is only an equity-risk signal such as refinancing stress or solvency pressure.
