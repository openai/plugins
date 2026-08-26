# Dashboard Map: Model Audit Tie-Out

Use `dashboard-builder` only when the user explicitly requests a standardized model-health dashboard, reusable validated template, model-health cockpit, remediation tracker, or structured payload-driven render. For an ordinary substantial workbook audit, produce a polished standalone HTML model-audit report following `../../../shared/html-artifact-standard.md`; finding count alone does not require a standardized dashboard.

## Decision Question

Is the uploaded or generated model reliable enough for the public-equity-investing decision, and what breaks confidence?

## Recommended Payload

- `kind`: `public_equity_investing_dashboard.v1`
- `mode`: `model_audit_tieout`
- `metadata.citation_policy`: `strict`
- `model_citations_path`: include when audited outputs cite workbook cells
- `sources`: include uploaded workbook, filings, releases, market data, consensus, and model-output ledgers where applicable

## Recommended Tabs And Modules

1. Overview: `decision_box`, `metric_tiles`, `missing_evidence`.
2. Formula And Workbook Controls: `table`, `bar_chart`, `cards`.
3. Source Tie-Out: `table`, `source_list`, `missing_evidence`.
4. Scenario And Sensitivity Review: `scenario_map`, `table`.
5. Remediation: `timeline`, `question_list`.

## Required Evidence

Every finding needs workbook location, evidence basis, why it matters, suggested fix, and owner route. Model-derived claims should cite workbook/sheet/cell/range via `model_citations` records.

Use reader-facing finding types that keep mechanics separate from underwriting and scope: `Formula/control defect`, `Source contradiction`, `Unsupported assumption`, `Missing forecast refresh`, `Missing decision output`, and `Not comparable without bridge`. Label auditor-created stress calculations `Illustrative audit sensitivity`, not corrected forecast output.

## Do Not

- Do not mark the model decision-ready based on static inspection alone.
- Do not bury missing model/source files in the bottom source ledger.
- Do not lead with CSV/JSON support files when an HTML audit dashboard or issue workbook exists.
- Do not treat the absence of valuation within a standalone operating model as a defect when a linked valuation/scenario layer may be the intended package design; determine whether the package lacks the decision output needed for its stated use.


## Equity Model Audit Dashboard Modules

Dashboards should surface PM decision readiness, current-price or target-price relevance, valuation/model output affected, issue severity by decision impact, source posture, scenario/downside weakness, action rules, and missing evidence.
