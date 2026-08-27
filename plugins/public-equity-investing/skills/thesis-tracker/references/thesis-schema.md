# Thesis Tracker Schema Contract

Use these fields for markdown tables, CSV/XLSX bundles, databases, or structured outputs. Keep blank fields visible rather than inventing values.

## Core Tables

| Table | Required fields |
|---|---|
| Dashboard | issuer/security, direction, mandate/role, company_thesis_status/current_prior, status_override_rationale_if_applicable, security_thesis_readiness, position_action, conviction/change, position/rating, market_data_as_of, base/bull/bear value, upside/downside, risk/reward, horizon, next catalyst, key confirm signal, key concern, recommendation, next review, sources, data gaps |
| Thesis pillars | pillar_id, pillar_name, claim, priority_or_inherited_weight, weighting_origin, current/prior status, KPI/evidence, baseline, expected path, confirm/warning/break thresholds, latest evidence, signal, evidence quality, model linkage, position linkage, next proof point, owner |
| Evidence ledger | evidence_id, date/time, reporting period, source, source_type, citation/file, event, evidence fact, prior house expectation, consensus/market expectation, interpretation, pillar affected, signal, magnitude, quality, model impact, valuation impact, confidence impact, action implication, follow-up, owner/due date |
| KPI tracker | KPI, pillar, source, unit, period, baseline, prior actual, current actual, house estimate, consensus, guidance, threshold, status, trend, PM comment |
| Catalyst calendar | catalyst_id, date/window, event, pillar tested, expected outcome, market setup, upside case, downside case, required prep, actual result, status/action |
| Estimate revisions | date, source, metric, period, prior estimate, new estimate, change, driver, thesis implication, stock reaction link |
| Model changelog | version, date, changed assumption, old value, new value, reason/source, impact, reviewer, status |
| Action rules | action, trigger, threshold/date, threshold_origin, threshold_approval_status, required_source, action_implication, next_review |
| Decision log | date, decision, rationale, evidence IDs, company_thesis_status, security_thesis_readiness, position/rating change, risk/reward snapshot, PM/owner, next review |
| Sources | source_id, name, type, date/as-of, reliability, used for, citation/link, limitation |
| Open questions | question, related pillar/evidence, owner, due date, required source, decision impact |
| Operating model | pm_owner, analyst_owner, evidence_owner, kpi_owner, model_owner, decision_authority, review_cadence, post_catalyst_update_sla, escalation_trigger, next_review_gate, decision_log_owner, portfolio_role, active_weight |

## Status And Scoring

Evidence signal: `+2 strongly confirming`, `+1 mildly confirming`, `0 neutral`, `mixed`, `-1 mildly weakening`, `-2 strongly weakening`, `break/invalidating`, `untested`.

Thesis status guide:

- Strengthening: core pillars confirm and risk/reward remains attractive.
- Intact: core pillars stable with no material contradiction.
- Watch: one core concern or several secondary warnings.
- Impaired: core pillar under pressure or repeated KPI misses.
- Broken: kill criterion hit or original premise failed.
- Changed: original reason no longer governs; needs explicit approval.
- Untested: no decisive proof point.
- Retired: position/coverage closed.

Status reconciliation: an aggregate `Watch` status alongside an inherited core pillar marked `Impaired` requires an explicit evidence-supported override rationale. Multiple core pillars marked `Impaired` default aggregate company-thesis status to `Impaired` unless an override rationale is stated.

Evidence signals are qualitative discipline aids, not an additive scoring framework. Do not aggregate them into pillar scores, weighted directions, or a scored chart unless a user-supplied or inherited methodology defines that calculation. PM judgment overrides mechanical status when explained.

Security-thesis readiness guide:

- Ready: sufficient current market, valuation, and portfolio inputs support the stated action.
- Conditional: the company/security interpretation is usable, but named implementation inputs remain open.
- Re-underwrite: thesis-moving evidence requires a revised model, valuation, or action framework.
- Not decision-grade: missing market, valuation, or portfolio inputs prevent a security conclusion.

Action threshold provenance:

- `Inherited threshold`: present in the supplied original underwriting or existing tracker.
- `Draft threshold for PM confirmation`: created in the current update and not yet approved.
- `Approved monitoring rule`: explicitly accepted by the user or governing portfolio process.

## Public Equity Portfolio Monitoring Fields

Add these fields where relevant:

- Dashboard: `benchmark_weight`, `active_weight`, `portfolio_role`, `liquidity_score`, `crowding_read`, `index_etf_flow_exposure`, `priced_in_status`, `position_action`, `security_thesis_readiness`.
- Thesis pillars: `portfolio_relevance`, `priced_in_status`, `diligence_source_needed`.
- Evidence ledger: `priced_in_read`, `benchmark_or_flow_impact`, `position_action`.
- Portfolio monitor table: ticker, status, active weight, next catalyst, thesis status, setup status, decision required, PM action, owner, due date.

Evidence remains append-only. Do not overwrite prior thesis history without a dated decision-log entry.
