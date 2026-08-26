# Core Workflow Contract

Use for full thesis-tracker builds or updates.

## Sequence

1. **Context.** Capture issuer/security, direction, mandate, horizon, exposure, cost basis/rating/target if supplied, benchmark/peers, and output format. If missing, use labeled placeholders.
2. **Sources/freshness.** Inventory source name, type, as-of/reporting period, reliability, coverage, and limitation. Prefer user/connected materials, then official filings/releases/transcripts, vendor market/consensus data, research/news, then assumptions. For a material stock-thesis update, attempt to retrieve current public price and basic market context when accessible; record source and timestamp, and identify missing consensus, model, position, benchmark, and risk inputs separately.
3. **Original underwriting.** Preserve separately: one-sentence thesis, variant perception, market setup, valuation anchor, scenarios, expected return, catalysts, KPIs, kill criteria, position implication, and open diligence.
4. **Pillars.** Convert thesis into prioritized, testable claims with baseline, expected path, confirm/warning/break thresholds, cadence, model linkage, action linkage, and next proof point. Carry forward numeric weights or scoring only when inherited from the prior tracker or requested by the user; otherwise use qualitative priority and no aggregate score chart.
5. **Evidence ledger.** Append material facts with source/date, affected pillar, prior expectation, consensus/market expectation, interpretation, signal, magnitude, quality, model/valuation/confidence/action impact, follow-up, and owner.
6. **KPIs/revisions/catalysts.** Compare actuals to prior period, house model, guidance, consensus, buyside expectation if supplied, thresholds, and peers. Mark unavailable data explicitly.
7. **Model/valuation.** State changed model lines, whether change is timing/cyclical/structural, estimate implications, fair value/target/downside/spread/recovery impact, and whether risk/reward still clears the hurdle. Without current price and required valuation inputs, state that security-thesis readiness is `not decision-grade` rather than making a valuation-led action call.
8. **Status/action.** Assign a company-thesis status of strengthening, intact, watch, impaired, broken, changed, untested, or retired separately from security-thesis readiness of ready, conditional, re-underwrite, or not decision-grade. Reconcile the aggregate status to core-pillar statuses: an inherited core pillar marked `Impaired` requires an explicit evidence-supported override rationale before aggregate status can remain `Watch`; multiple core pillars marked `Impaired` default aggregate company-thesis status to `Impaired`. Recommend add/press, hold, trim, exit/cover, upgrade/downgrade, hedge/pair, wait, re-underwrite, update model, diligence, or escalation. Classify each threshold as `Inherited threshold`, `Draft threshold for PM confirmation`, or `Approved monitoring rule`.
9. **Red-team/log.** Include strongest opposing view, evidence for it, what changes the call, open questions, next review date, and append-only changelog.
10. **Workbook QA.** For XLSX output, lead with a compact decision-facing cover, use detail sheets for audit trails rather than repeating every field on each first-read table, freeze key columns, and visually render every sheet before delivery. Keep full action-rule matrices and full diligence/gap registers on their dedicated tabs; show only action posture, top decision blockers, and next gate on the cover. Reduce or split tables that require excessive horizontal scrolling, and omit score charts unless the scoring basis is inherited or requested.

## Operating Model And Cadence

Every full tracker should name the operating model:

- PM owner and decision authority;
- analyst owner;
- evidence owner;
- KPI owner;
- model owner;
- review cadence;
- post-catalyst update SLA;
- escalation triggers;
- next review gate;
- portfolio role and active weight when supplied;
- decision log owner and append-only changelog process.

Every update should end in one of: `add`, `press`, `hold`, `trim`, `exit`, `cover`, `hedge`, `wait for proof`, `re-underwrite`, `update model`, or `escalate`.

Newly proposed monitoring thresholds are draft decision aids, not approved mandate rules. Preserve inherited thresholds and approved monitoring rules distinctly, including their source and approval status.

## Interpretation Rules

- Evidence direction: strongly confirming, mildly confirming, neutral, mixed, mildly weakening, strongly weakening, invalidating, or untested.
- A thesis can strengthen while the stock becomes less attractive if valuation/expectations moved faster than evidence.
- A headline beat can weaken a thesis if leading KPIs, quality, cash conversion, or guidance disappoint.
- Price action is a signal to decompose, not proof of thesis status.
- Every "monitor" conclusion must specify metric, source, threshold, date, and action.
