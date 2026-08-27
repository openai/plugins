---
name: financial-source-of-truth
description: Use when enforcing Public Equity Investing source discipline. Do not use as the primary memo, model, earnings, or pitch owner.
---

# Financial Source Of Truth

> Internal support playbook. Load through `internal-support/policy.md`; this evidence-control capability is bundled with the visible router rather than exposed as a skill entrypoint.

## Deliverable Intake

When invoked as support for an owning workflow, inherit its resolved deliverable preferences and do not re-prompt. Only when this skill independently owns a new substantive standalone source-review deliverable should it, before source gathering, analysis, or rendering, load `../../../../shared/deliverable-intake-policy.md` and perform its adaptive `request_user_input` preflight for materially unresolved preferences.

## Purpose

Load `shared/equity-research-support-standard.md` and `shared/support-layer-routing-contract.md` before substantial source, data, QA, or style work.


Act as the evidence-control layer for Public Equity Investing analysis: public-equity research notes, PM memos, sell-side notes, earnings work, models, ETF/index diligence, public-company diligence, risk workflows, and decks. This skill ranks sources, checks freshness, resolves conflicts, labels facts versus assumptions, and creates citation-ready evidence ledgers for downstream equity workflows.

This is not the primary valuation, earnings, event, risk, deck, style, pitch, or memo skill. Use it before or alongside those skills when evidence quality affects the public-equity decision.

## Embedded Support Routing

This is an embedded service under an owning workflow unless the user explicitly asks for a standalone source-of-truth pass. Preserve the `owning_workflow` internally, such as `memo-builder`, `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `long-short-pitch`, `economic-impact-report`, `thesis-tracker`, `meeting-prep`, `deck-report-qc`, or `dashboard-builder`.

For substantial embedded work, preserve `decision_impact`, `readiness_effect`, `artifact_role`, and `hidden_unless_requested` in internal context or support artifacts. Do not print those internal field names in the owning workflow's user-facing artifact. Do not own recommendations; instead, show in natural language how stale, missing, conflicted, or weak evidence changes confidence, valuation support, rating/target support, sizing, hedge posture, watchlist status, or circulation readiness. Evidence ledgers, CSV, JSON, Markdown, and logs are secondary/support artifacts unless the user explicitly asks for them.

## Public Equity Investing Boundary

Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis. This skill may track debt, liquidity, rating, maturity, CDS, or spread facts only as evidence for a listed-equity decision, and must label them as equity-risk context rather than local credit research.


Private-market workflows such as CIM teardowns, QoE bridges, LBO sponsor models, private credit underwriting, or deal diligence are non-local to this plugin. If the user provides those materials, label them as user-provided evidence and avoid advertising unavailable downstream handoffs.

## Core Rule

Never let an assumption, issuer claim, management statement, stale source, inference, or estimate masquerade as a verified fact.

Practicality rule: do not stop at policy language. Even when evidence is incomplete, return a usable source posture that separates supported facts, assumptions, limitations, conflicts, source hierarchy, and next actions. Be concrete about what is known and what is missing, but never invent precision to make the answer feel complete.

Use the canonical evidence labels in `references/fact-assumption-labeling.md`, including `fact_source_reported`, `fact_provider_standardized`, `derived_calculation`, `issuer_management_claim`, `analyst_interpretation`, `assumption_user_provided`, `assumption_inferred`, `estimate_consensus`, `stale_source`, `contradicted_source`, `missing_required_source`, and `unknown`.

## Workflow

1. **Define decision context.** Identify the artifact, decision, and minimum evidence required.
2. **Build source inventory.** Assign source IDs and capture owner, date, period, as-of date, access date, type, and intended use.
3. **Apply hierarchy.** Use `references/evidence-hierarchy.md`; prefer primary, filed, executed, audited, or source-nearest evidence over summaries and marketing materials.
4. **Check staleness.** Use `references/staleness-and-conflicts.md`; missing as-of dates are quality issues, especially for market-sensitive data.
5. **Resolve conflicts.** Do not average conflicting sources without explanation. Prefer the source most authoritative for the exact claim or escalate the conflict.
6. **Label claims.** Mark facts, assumptions, estimates, inferences, issuer/management claims, stale sources, contradicted sources, missing required sources, and unknowns.
7. **Protect EPS quality.** For EPS claims, identify GAAP versus adjusted/operating basis, consensus basis, reconciliation source, below-the-line items, tax/share-count effects, and whether the claim is recurring or one-time.
8. **Attach citations.** Cite load-bearing metrics, dates, quotes, market data, debt terms, valuation inputs, guidance, consensus, and key claims.
9. **Apply connector honesty.** Use live/vendor/connector data only when the runtime provides it; otherwise request the user export and label the gap `missing_required_source`.
9. **State evidence posture.** Use decision-grade, research-grade, preliminary, assumption-led, or not supportable.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: source hierarchy, freshness/currentness, conflict resolution, assumption labeling, and evidence register. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.

When embedded in a broader workflow, "lead" means lead for source discipline only; the owning workflow remains the investment-artifact owner.


## Minimum Useful Answer

When the user asks for source discipline, source review, evidence quality, or a source-of-truth pass, include these components unless the task is explicitly narrower:

1. `Evidence posture`: decision-grade, research-grade, preliminary, assumption-led, or not supportable.
2. `Supported facts`: what current evidence actually supports, with source IDs or native citations.
3. `Assumptions and inferences`: what is assumed, inferred, estimated, or user-provided.
4. `Limitations and conflicts`: stale data, missing as-of dates, contradictory sources, weak issuer claims, and unsupported precision.
5. `Source hierarchy`: which sources should govern the disputed or load-bearing claims.
6. `Next actions`: exact source requests or tie-outs needed to upgrade the work.

If no adequate source is available, still produce the framework above with `not sourced`, `unknown`, or `missing_required_source` labels. The output should help the user continue the analysis rather than simply saying more sources are needed.

## Output Contract

Default to a full source posture for source-discipline requests. Use a compact evidence note only when the user explicitly asks for a short answer or one disputed claim.

- Evidence posture block.
- Source inventory.
- Evidence ledger.
- Assumption register.
- Conflict register.
- Evidence request list.
- Compact evidence note for explicitly short or single-claim answers.

For ledger formatting and examples, load `references/citation-and-ledger-format.md`. For practical response patterns under partial, conflicting, or weak source context, load `references/source-discipline-output-patterns.md`.

## Optional Validation

When a task produces or receives a CSV/JSON evidence ledger, run:

```bash
python scripts/validate_evidence_ledger.py path/to/evidence_ledger.csv
```

The script catches missing claim labels, source IDs, freshness labels, as-of dates for market-sensitive claims, and high-impact assumptions. It is a QA aid, not a substitute for judgment.

## Local Handoffs

Use this skill as source discipline for:

- `comps-valuation`: peer rationale, EV bridge support, market-data timestamps, and definition consistency.
- `dcf-model-builder` and `three-statement-model-builder`: sourced facts versus forecast assumptions.
- `equity-model-update`: reported actuals, guidance, consensus, model changes, and analyst/user assumptions.
- `earnings-preview` and `earnings-deep-dive`: consensus, guidance, release, filing, transcript, quote support, and EPS-quality / reconciliation evidence.
- `economic-impact-report`, `event-driven-analyzer`, `long-short-pitch`, and `memo-builder`: evidence posture, source conflicts, and assumptions.
- `deck-report-qc`: citations, footnotes, units, dates, and repeated metrics that support the exact deck narrative.

## Reference Map

- `references/evidence-hierarchy.md`: source hierarchy by workflow.
- `references/fact-assumption-labeling.md`: label definitions and edge cases.
- `references/staleness-and-conflicts.md`: freshness thresholds and conflict handling.
- `references/citation-and-ledger-format.md`: evidence posture, source inventory, ledger, assumption, and conflict formats.
- `references/source-discipline-output-patterns.md`: concise output patterns that balance source rigor with actionable next steps.

## Final QA

Confirm the evidence posture is stated or obvious, material numbers and quotes are cited or labeled, source/as-of dates are visible, issuer and management claims are not treated as verified facts, EPS surprise is not treated as recurring without a source-backed quality screen, conflicts are reconciled or flagged, stale data is not buried, and evidence requests are specific enough to act on.
