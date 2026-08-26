# Output Contracts

Use these full structures by default; keep all decision-critical rows. Compress only when the user explicitly asks for a summary, quick read, one-pager, brief, TL;DR, or one section.

## Workbook-First Tracker Update

For an attached or existing thesis tracker update, the default hero deliverable is a polished XLSX workbook. The `Cover` tab must make the decision legible before the audit trail:

| First-read block | Required content |
|---|---|
| Company thesis | Prior status, current status, what confirmed, what weakened, next fundamental proof point |
| Security thesis readiness | `Ready`, `Conditional`, `Re-underwrite`, or `Not decision-grade`; current price and market-data as-of; valuation readiness and blocked inputs |
| Position action | `Add`, `Hold`, `Trim`, `Exit`, `Wait for proof`, or `Re-underwrite`, with the action condition clearly stated |
| Action-rule summary | Current action, approval posture of applicable rules, and next review gate; full triggers, provenance, and required sources remain on `Action Rules` |
| Evidence-gap summary | Top decision blockers and their readiness consequence; the full diligence/open-question register remains on its dedicated tab |

Keep the first-read pillar view compact: pillar, priority or inherited weight, prior/current status, thesis-moving evidence, next proof point, and action implication. Put detailed threshold definitions, citations, model impacts, and follow-ups into the dedicated monitoring or evidence tabs rather than expanding the pillar sheet horizontally.

When an inherited core pillar is `Impaired`, an aggregate company-thesis status of `Watch` requires an explicit evidence-supported override rationale. When multiple core pillars are `Impaired`, default aggregate company-thesis status to `Impaired` unless that rationale is stated.

Keep `Cover` concise: do not duplicate the full action-rule matrix or full diligence/open-question register on it.

Use `Inherited threshold`, `Draft threshold for PM confirmation`, or `Approved monitoring rule` for every action trigger. Do not display a generated threshold as an approved hold, trim, or exit rule.

Do not add an aggregate pillar score or scored chart unless the prior tracker contains a defined scoring methodology or the user explicitly requests one. Qualitative signal/status formatting is sufficient by default.

## Default Update Memo

```markdown
# [Company / Ticker] Thesis Tracker Update
As of: [date/time] | Direction/mandate: [long/short/rating/etc.] | Company thesis status: [current vs prior] | Security thesis readiness: [readiness] | Recommendation: [action] | Next decision point: [date/catalyst/threshold]

## PM Summary
[3-6 sentences: what changed, whether evidence confirms or weakens the company thesis, whether the security thesis is decision-grade, whether risk/reward improved or deteriorated, and what action follows.]

## What Changed
| Item | Prior house view | Consensus / market setup | New evidence | Thesis read-through |
|---|---|---|---|---|

## Pillar Tracker
| Pillar | Weight | Prior | Current | Latest evidence | Signal | Next proof point |
|---|---:|---|---|---|---|---|

## KPI / Estimate / Catalyst Update
[Only metrics, revisions, and events that affect the decision.]

## Model, Valuation, Risk/Reward
[Changed assumptions, target/fair-value/downside impact, estimate vs multiple read-through, hurdle clearance.]

## Action Thresholds
| Trigger | Threshold/date | Origin | Approval status | Required source | Action |
|---|---|---|---|---|---|

## Operating Model
| Role / cadence item | Owner / value | Decision responsibility | Next date / SLA | Escalation trigger |
|---|---|---|---|---|
| PM owner |  | decision authority |  |  |
| Analyst owner |  | evidence synthesis |  |  |
| Evidence owner |  | source updates |  |  |
| KPI owner |  | KPI thresholds |  |  |
| Model owner |  | estimate/model changes |  |  |
| Review cadence |  | tracker refresh |  |  |
| Post-catalyst update SLA |  | rapid update |  |  |

## Red-Team / Open Questions / Changelog
Best opposing view: [view]. What makes it right: [evidence]. Open questions: [asks].
| Date | Change | Source | Rationale | Owner/next step |
|---|---|---|---|---|
```

## Blank Tracker Shell

Use when no thesis is provided; invent no facts.

Required sections/tables: Dashboard, Original Underwriting, Thesis Pillars, Evidence Ledger, KPI Tracker, Catalyst Calendar, Estimate Revisions, Model Changelog, Decision Log, Sources, Open Questions.

Minimum fields:

- Dashboard: issuer/security, direction, mandate, horizon, company-thesis status, security-thesis readiness, position action, market-data as-of, base/bull/bear value if supportable, next catalyst, recommendation, next review, and blocked inputs.
- Operating model: PM owner, analyst owner, evidence owner, KPI owner, model owner, decision authority, review cadence, post-catalyst update SLA, escalation triggers, next review gate, and decision log owner.
- Underwriting: thesis, variant perception, market setup, valuation anchor, catalysts, risks, kill criteria, diligence.
- Pillars: pillar, priority or inherited weight and its origin, claim, KPI/evidence, confirm/warning/break thresholds, status, next proof point.
- Evidence: date, source, fact, pillar, signal, magnitude, model impact, action implication, follow-up.
- Action rules: trigger, threshold/date, threshold origin, threshold approval status, required source, action, next review.
- Decision log: date, decision, rationale, evidence, company-thesis status, security-thesis readiness, position/rating change, next review.

## PM Dashboard

```markdown
Company thesis: [status/change] | Security readiness: [readiness] | Action: [recommendation] | Conviction: [level/change] | Risk/reward: [upside/downside/skew or blocked] | Next catalyst: [event/date] | Key call: [one sentence]

| Dimension | Current read | PM judgment |
|---|---|---|
| Fundamentals / estimates / valuation / setup / catalyst path / thesis risk |  |  |
```

## Portfolio Review

Include: priority actions, names with deterioration, names with improved evidence but worse risk/reward, upcoming catalyst watchlist.

## Mandate-Specific Language

- Sell-side: rating/target implication, estimate changes, valuation bridge, key risks, client debate.
- Long/short: trade read-through, positioning/setup, catalyst path, borrow/squeeze/factor risk, hedge/trim thresholds.
- Equity-risk credit signal: liquidity, maturities, covenant pressure, CDS/spread warning signal, and common-equity downside action; route credit-security and recovery work to Credit Markets.

## Tone Examples

Prefer: "Thesis is playing out, but valuation rerated faster than estimates; business thesis is stronger, stock thesis is less attractive."

Avoid: "Earnings were good and the stock was up. Continue to monitor."
