# Schemas

Plan and normalized CSV contracts for deterministic mode. Templates live in `assets/templates/`.

## Plan

Required top-level keys: `event`, `inputs`, `outputs`. Recommended controls: `allow_call_only_guidance`, `require_gaap_for_non_gaap`, `require_source_tags`, `dry_run`.

Event fields: `ticker`, `company_name`, `fiscal_period`, `event_date`, `timezone`, `base_currency`, `base_scale`.

Inputs:

- `artifact_index_csv`
- `artifacts.press_release`, `sec_filing_10q_or_10k` or equivalent filing key, `sec_filing_8k`, `deck`, `transcript`
- `normalized.metrics_csv`, `estimates_csv`, `guidance_csv`, `quotes_csv`, `driver_updates_csv`
- `model.prior_model_xlsx`, `driver_registry_csv`, `output_registry_csv`

Outputs:

- `output_dir`
- `render.executive_overview`, `tear_sheet`, `deep_dive`
- `model_update.enabled`, `mode` (`packet` or `apply`), `write_diff`

The bundled template defaults to packet/dry-run and writes to `/tmp`. Enable workbook `apply` only when the user supplies a real workbook/registries and explicitly asks for it.

## Normalized Inputs

| CSV | Required columns |
|---|---|
| `metrics.csv` | `MetricName`, `Period`, `Value`, `Units`, `GAAP_Flag`, `Segment`, `IsTearSheet`, `DisplayOrder`, `SourceTag` |
| `estimates.csv` | `MetricName`, `Period`, `EstimateType` (`Consensus`/`Internal`/`Whisper`), `Value`, `Units`, `AsOf`, `Source` |
| `guidance.csv` | `MetricName`, `Period`, `Low`, `High`, `Units`, `GAAP_Flag`, `SourceTag` |
| `quotes.csv` | `Section`, `Speaker`, `Questioner`, `TopicTag`, `QuoteText`, `SourceTag` |
| `driver_updates.csv` | `DriverID`, `Period`, `NewValue`, `Units`, `Why`, `SourceTag` |

Recommended: metric group, comparable GAAP metric and reconciliation source for non-GAAP, assumptions, old value, confidence, and notes. For EPS-related rows, add basis/notes that identify GAAP EPS, adjusted EPS, operating EPS, below-the-line items, tax effects, share-count changes, and any non-recurring items used in the EPS quality screen.

## Model Registry

`driver_registry.csv`: `DriverID`, `DriverName`, `Units`, `Cadence`, `MappingType` (`NamedRange`/`Cell`), `Worksheet`, `Cell` or `NamedRange`, plus definition/owner/source notes when available.

`output_registry.csv`: `OutputID`, `OutputName`, `Units`, `MappingType`, `Worksheet`, `Cell` or `NamedRange`.

## Audit Outputs

`ChangeLog.csv`: timestamp, model version, changed by, section, item, old/new value, why, source tag.

`WhatChanged_Diff.csv`: output/driver ID, old/new value, delta, units, source, why, confidence.

For structured templates, `MISSING` is allowed. For user-facing analysis, use precise labels such as `not guided`, `not disclosed`, `not provided`, or `source not provided`.
