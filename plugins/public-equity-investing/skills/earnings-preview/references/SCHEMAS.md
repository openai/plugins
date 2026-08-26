# Schemas

Minimum deterministic CSV contract for `scripts/`. Quick chat previews can proceed from ticker/company plus connected or public sources; substantial reusable previews should route through the dashboard/report framework.

## Conventions

- CSV preferred; XLSX is acceptable when scripts support it.
- Column names are normalized case-insensitively to snake_case.
- Use ISO dates/timestamps, explicit `currency_code`, `unit`, `scale`, `ticker`, `fiscal_period_id`, and `metric_id`.
- Canonical event file is `event_calendar.csv`.

## Required Scripted Files

- `company_master.csv`
- `fiscal_period_index.csv`
- `reported_financials.csv`
- `kpi_timeseries.csv`
- `consensus_estimates.csv`
- `guidance_history.csv` (may be empty with headers)
- `event_calendar.csv` (earnings timing at minimum)

Optional: `whisper_estimates.csv`, `price_returns.csv`, `options_snapshot.csv`, `qual_notes.csv`, `scenario_assumptions.csv`.

## Required Columns

| File | Required columns |
|---|---|
| `company_master.csv` | `ticker`, `company_name`, `sector` or `sector_pack`, `currency_code`, `fiscal_year_end_month` |
| `fiscal_period_index.csv` | `ticker`, `fiscal_period_id`, `fiscal_year`, `fiscal_quarter`, `period_start_date`, `period_end_date` |
| `event_calendar.csv` | `ticker`, `event_type`, `event_datetime_utc`, `event_name`; recommended `fiscal_period_id`, `source`, `notes` |
| `reported_financials.csv` | `ticker`, `fiscal_period_id`, `metric_id`, `value`, `unit`, `scale`, `as_reported_date` |
| `kpi_timeseries.csv` | `ticker`, `fiscal_period_id`, `metric_id`, `value`, `unit`, `scale`, `as_reported_date` |
| `guidance_history.csv` | `ticker`, `guidance_date`, `fiscal_period_id`, `metric_id`, `low`, `high`, `unit`, `scale` |
| `consensus_estimates.csv` | `ticker`, `snapshot_datetime`, `fiscal_period_id`, `metric_id`, `statistic`, `estimate_value`, `unit`, `scale` |
| `whisper_estimates.csv` | `ticker`, `asof_datetime`, `fiscal_period_id`, `metric_id`, `whisper_value`, `unit`, `scale` |
| `price_returns.csv` | `ticker`, `date`, `close` |
| `options_snapshot.csv` | `ticker`, `snapshot_datetime`, `spot_price`, and either straddle price or IV/DTE fields |
| `qual_notes.csv` | `ticker`, `fiscal_period_id`, `tag`, `note`, `source`, `note_datetime` |
| `scenario_assumptions.csv` | `ticker`, `fiscal_period_id`, `scenario`, `metric_id`, `value`, `unit`, `scale`, `source_or_assumption` |

Recommended optional columns preserve nuance: GAAP/non-GAAP basis, segment, vendor, high/low, number of estimates, provenance, confidence, notes, restatement or KPI-definition version, exchange/country, shares, net debt.

## Plan Keys

`plan.json` is validated by `assets/plan_schema.json`. Required top-level keys are `ticker`, `fiscal_period_id`, `sector_pack`, `freeze_time`, `input_dir`, and `output_dir`. The deterministic runner reads from local files only and writes outside the packaged skill when using the sample plan.

## QA

Inputs should carry source/as-of metadata sufficient to reproduce the pack. If a required optional source is missing for a requested section, render a precise limitation (`not provided`, `not guided`, `source not provided`) rather than a placeholder.
