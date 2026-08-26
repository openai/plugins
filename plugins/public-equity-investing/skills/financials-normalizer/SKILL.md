---
name: financials-normalizer
description: Use when normalizing public-company financials from source materials. Do not use for private data rooms or non-financial cleanup.
---

# Financials Normalizer

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Company Filings & IR`
- `Portfolio Models & Trackers`
- `Market Data & Estimates`

## Deliverable Intake

When invoked as support for an owning workflow, inherit its resolved deliverable preferences and do not re-prompt. Only when this skill independently owns a new substantive standalone normalization deliverable should it, before source gathering, analysis, or rendering, load `../../shared/deliverable-intake-policy.md` and perform its adaptive `request_user_input` preflight for materially unresolved preferences.

## Purpose

Load `shared/equity-research-support-standard.md` and `shared/support-layer-routing-contract.md` before substantial source, data, QA, or style work.


Turn messy public-company source financials into auditable, model-ready normalized statements, KPI schedules, consensus/guidance inputs, segment schedules, share-count support, net-debt and capital-allocation support, source citations, assumptions, conflicts, and QA flags for downstream Public Equity Investing workflows.

Boundary: shipped scripts create `Source_Index.csv`, `Normalized_Financials_Long.csv`, and `Normalization_Issues.csv`. Wide statements, KPI schedules, adjustment logs, conflict logs, assumption registers, and workbook/deck-ready tabs are instruction-led unless explicitly built from staging data.

For a standalone request for **model-ready normalized financials**, do not treat a long-form staging CSV alone as the analyst deliverable. Create a model-loading package from the staged rows: full-scope wide schedules relevant to the supplied financials, a disclosure/comparability bridge when definitions or presentation changed, material QA flags, and logged validation checks. Use XLSX when the user requests a workbook or will load/review the output in a workbook; otherwise a clearly organized CSV package plus a concise review summary is appropriate. This is a data-first skill; do not force an HTML artifact unless the user requests one.

## Embedded Support Routing

This is an embedded service under the owning workflow unless the user explicitly asks for standalone normalization. Preserve the `owning_workflow` internally, such as `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `earnings-preview`, `earnings-deep-dive`, `memo-builder`, `thesis-tracker`, `scenario-sensitivity-generator`, `portfolio-risk-management`, or `dashboard-builder`.

For substantial embedded work, preserve `decision_impact`, `readiness_effect`, `artifact_role`, and `hidden_unless_requested` in internal context or support artifacts. Do not print those internal field names in the owning workflow's user-facing artifact. Do not own the valuation, memo, earnings, or recommendation; state in natural language how normalization issues change estimate confidence, valuation support, target support, sizing, model readiness, or circulation readiness. `Source_Index.csv`, `Normalized_Financials_Long.csv`, `Normalization_Issues.csv`, run logs, manifests, and support notes are secondary/support artifacts when invoked by an owning workflow.

## Non-Negotiables

- Preserve raw/source materials.
- Prefer user files/context, callable runtime apps/connectors when actually available, primary public sources, user-provided provider exports, then labeled assumptions. Never imply live provider access when it is unavailable.
- Never invent missing financials; mark unavailable values as `missing_required_source`.
- Keep normalized values traceable to source ID, source name/location, retrieved-at date, period, units, currency, and evidence label.
- Missing `source_id` must remain visible as `SRC-UNSPECIFIED`, produce a QA flag, and block decision-grade handoff.
- Retain conflicts rather than silently choosing values.
- Flag stale, preliminary, unaudited, OCR-derived, or low-confidence data.
- Do not infer fiscal period-end dates from quarter labels alone; use an explicit source date or mark the date missing and flag it.
- Keep issuer outlook or guidance in `kpi_schedule` with `issuer_management_claim`; reserve `consensus_estimate` with `estimate_consensus` for externally sourced consensus estimates.
- When a segment, KPI, non-GAAP definition, or balance-sheet presentation changes, preserve both bases and create a comparability bridge before calling any series model-loadable.
- Apply comparability status at the affected series or line-item level. A changed cash presentation does not recast unrelated balance-sheet rows.
- Use `comparable_rounded` when an unchanged reported series is comparable across periods but only available in rounded narrative units; disclose that it is unsuitable for exact tie-out.
- Do not backsolve an undisclosed comparable value from rounded amounts or percentage growth for model loading. A labeled directional calculation may appear separately only when useful.
- Material open exceptions must be surfaced in `QA_Flags` and in the readiness summary; an empty technical `Normalization_Issues` file does not mean the financials are clear for downstream use.

## Workflow

1. **Classify job.** Public-equity issuer financials, earnings/model update, consensus/provider export, ETF/index constituent support, portfolio/market-data support, or equity-risk debt/liquidity context.
2. **Build source index.** Capture source ID, name/type, owner/provider, period, as-of date, retrieved-at date, location, source rank, freshness, and notes.
3. **Extract long-form staging.** Use `Normalized_Financials_Long` before wide statements; preserve original line labels beside canonical labels.
4. **Normalize periods, scale, currency, signs, and labels.** Keep reported, adjusted, pro forma, provider-standardized, estimated, and analyst-adjusted values separate.
5. **Reconcile disclosure changes.** Identify renamed, regrouped, newly introduced, discontinued, recast, or definition-changed segments/KPIs/non-GAAP lines; preserve legacy and new bases; create a disclosure/comparability bridge with model treatment.
6. **Reconcile and QA.** Check subtotals, roll-forwards, balance sheet balance, cash flow bridge, units/currency, duplicate periods, missing sources, stale/conflicting values, signs, unsupported KPIs, and completeness of the intended model-loading scope. Log performed checks and results; do not claim a check count that is not preserved in an output.
7. **Produce package.** For standalone model-ready work, produce loadable wide schedules plus `QA_Flags` and `Validation_Checks` from the audited staging layer; include a disclosure/comparability bridge whenever presentation changed. For narrower extraction/support work, return only the deterministic CSV outputs or instruction-led tabs actually created.
8. **Hand off.** State what is loadable, what is audit-only, and what remains partial or blocked before routing to models, earnings, comps, memo, thesis, scenario, risk, ETF/index, or deck/report skills. Route covenant/recovery/debt-security normalization to Credit Markets.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: source inventory, line-item mapping, period/unit normalization, conflict log, and QA. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.

When embedded in a broader workflow, "lead" means lead for normalization only; the owning workflow remains the investment-artifact owner.


## Evidence Labels

Use exact labels from `references/normalization-schema.md`, including `fact_source_reported`, `fact_provider_standardized`, `derived_calculation`, `issuer_management_claim`, `management_adjusted`, `analyst_adjusted`, `analyst_interpretation`, `assumption_user_provided`, `assumption_inferred`, `estimate_consensus`, `stale_source`, `contradicted_source`, `missing_required_source`, and `unknown`.

Confidence labels are `high`, `medium`, or `low`.

## Scripts

```bash
python scripts/normalize_extracted_financials.py path/to/input.csv --output-dir output
python scripts/validate_normalized_financials.py output/Normalized_Financials_Long.csv
```

For workbook inputs, first extract the relevant tab/range with spreadsheet tools into a table/CSV; scripts must not destructively modify workbooks.

## Final Response

Return:

1. what was normalized: entity, sources, periods, units, currency, scope;
2. outputs created;
3. what can be loaded into a model and what remains audit-only, partial, or blocked;
4. material QA findings and disclosure/comparability breaks;
5. fact versus assumption summary and validation checks actually performed;
6. recommended next step or missing source.

## Reference Map

- `references/source-protocol.md`: hierarchy, stale data, citations, conflicts.
- `references/normalization-schema.md`: output schema, signs, scales, labels.
- `references/line-item-taxonomy.md`: statement/KPI mappings.
- `references/qa-rules.md`: reconciliation tests and red flags.
- `references/integration-guide.md`: downstream Public Equity Investing handoffs.
