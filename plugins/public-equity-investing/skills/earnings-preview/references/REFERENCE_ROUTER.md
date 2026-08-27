# Reference Router

Load only what the request requires.

| Need | Load |
|---|---|
| Default full preview report or explicit summary compression | `OUTPUT_SPEC.md`, then `QA_RULES.md` |
| Scripted pack or local CSV inputs | `SCHEMAS.md`, `quickstart.md`, `assets/plan_schema.json` |
| Formulas, whisper rules, reaction/options logic | `METRICS_LIBRARY.md` |
| Sector KPI selection | `SECTOR_KPI_PACKS.md`, then `assets/sector_kpi_packs.yaml` |
| Call questions | `CALL_QUESTION_BANK.md` |
| Standalone HTML full preview report | `OUTPUT_SPEC.md`, then `QA_RULES.md`; apply `../../../shared/html-artifact-standard.md` |
| Explicit standardized dashboard / payload-driven render | `OUTPUT_SPEC.md`, `DASHBOARD_PACK.md`, then `QA_RULES.md` |

Fast route:

- Full preview is the default and usually needs `OUTPUT_SPEC.md`, `METRICS_LIBRARY.md`, and `QA_RULES.md`.
- Summary/short output is explicit-only and should compress the full preview structure rather than using a separate tear-sheet contract.
- Deterministic export always needs `SCHEMAS.md`, `quickstart.md`, and the JSON schema.
- Standalone HTML full preview reports follow the flexible artifact standard and keep the expectation bar and reaction debate as the primary visual objects.
- Standardized dashboard output keeps `earnings-preview` as the analysis owner and uses `dashboard-builder` only for its selected schema-driven rendering path.
