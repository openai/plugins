# Thesis Tracker Dashboard Pack

Use this only when the user explicitly requests an HTML dashboard/report or a reusable presentation view for a thesis tracker, monitoring update, evidence ledger, KPI/catalyst review, or portfolio thesis status package. Ordinary tracker builds and updates lead with the XLSX workbook when available.

## Producer Role

`thesis-tracker` owns thesis status, pillar evidence, KPI/catalyst monitoring, estimate/model change logs, decision logs, and update cadence. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `thesis_tracker`
- `layout`: `single_page` for reusable tracker reviews unless the user explicitly requests tabs
- `hero.callout`: company-thesis status, security-thesis readiness, and position action
- `snapshot`: company-thesis status, security-thesis readiness, conviction/rating, base/bull/bear value if supportable, current price and market-data as-of when accessible, next catalyst, evidence density, open-question count
- `sources`: tracker input/user files first, then filings/releases/transcripts, market/consensus data, model outputs, and assumptions
- Raw JSON, Markdown notes, CSV exports, run logs, and manifests are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `thesis-status`
   - `decision_box`: current thesis status, recommendation/action, conviction, next catalyst, and break condition
   - `metric_tiles`: status, value/range if sourced, evidence density, source confidence, open questions, next review
2. `pillars-evidence`
   - `cards`: thesis pillars, supporting/refuting evidence, confidence, and what changed
   - `table`: evidence ledger with source, date, implication, status, and owner
3. `kpi-catalyst-monitor`
   - `key_metrics`: KPIs, thresholds, current values, trend, and read
   - `timeline`: catalysts, review dates, and monitoring events
   - `market_events`: source-backed developments affecting thesis status
4. `model-decision-log`
   - `table`: estimate revisions, model changes, decisions, dates, owners, and rationale
5. `open-items`
   - `question_list`: diligence questions and next evidence checks
   - `missing_evidence`: stale sources, missing KPIs, unresolved conflicts, possible restricted/MNPI flags, and open model fields

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every thesis-moving event, KPI, estimate revision, model change, catalyst date, and decision log item.
- Label source type, as-of date, stale data, assumptions, PM judgment, possible restricted material, and missing evidence.
- Label generated action thresholds as `Draft threshold for PM confirmation` until approved; do not present them as inherited or approved monitoring rules.
- Reconcile the hero company-thesis status to core-pillar states; any aggregate `Watch` status above an inherited core pillar marked `Impaired` must state an explicit evidence-supported override rationale.
- Do not include a scored pillar summary or score chart unless a scoring method is inherited from the existing tracker or explicitly requested.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not overwrite an existing tracker unless the user explicitly authorizes it.
- Do not use possible MNPI/restricted material for public-equity trading recommendations; flag it for review.
- Do not make raw JSON, Markdown notes, CSV sidecars, run logs, or manifests the lead user-facing artifact unless explicitly requested.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm company-thesis status, security-thesis readiness, evidence changes, KPI/catalyst monitor, decision log, threshold origin/approval status, and open questions are visible.
- Confirm tracker support files stay behind the dashboard or workbook hero artifact.

## PM Judgment Dashboard Slot

When this skill produces or hands off a `public_equity_investing_dashboard.v1` payload, surface the PM judgment layer inside existing supported modules rather than inventing a custom shell.

Required dashboard content where relevant:
- PM decision box: use `decision_box` for actionability, position action, or rating/target implication.
- Variant wedge and what is priced in: use `text_block`, `key_metrics`, or `table`.
- Estimate/revision bridge: use `table`, `metric_tiles`, or `financial_trend_chart` when source-backed.
- Scenario skew and downside mechanism: use `scenario_map`.
- Catalyst timeline and decision pressure: use `timeline` or `market_events`.
- Disconfirmers and action rules: use `question_list`, `table`, or `text_block`.
- Benchmark/factor/ETF exposure: use `table` or `key_metrics` when relevant and source-backed.
- Source posture and missing evidence: include `source_list` and `missing_evidence` in all production-ready dashboards.

Sector context belongs in the owning skill dashboard through hero debate, snapshot KPI, key metrics, valuation table, risk/falsifier cards, missing evidence, and source ledger. Do not create a standalone sector dashboard.
