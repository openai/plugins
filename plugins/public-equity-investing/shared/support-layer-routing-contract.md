# Support-Layer Routing Contract

Use this contract for `financial-source-of-truth`, `financials-normalizer`,
`excel-data-cleaner`, `deck-report-qc`, and `style-guide-adapter`. Read `skills/public-equity-investing/internal-support/policy.md` through the `public-equity-investing` router to resolve internal capability labels to their bundled playbooks.

## Embedded Service Rule

These five capabilities are embedded services inside Public Equity Investing.
`financials-normalizer` and `deck-report-qc` remain visible when explicitly requested as standalone jobs; `financial-source-of-truth`,
`excel-data-cleaner`, and `style-guide-adapter` load as internal playbooks.
They normally support an owning workflow rather than becoming the final investment owner. The owning workflow can be `earnings-preview`, `earnings-deep-dive`,
`company-tearsheet`, `initiating-coverage`, `memo-builder`,
`long-short-pitch`, `equity-model-update`, `dcf-model-builder`,
`three-statement-model-builder`, `comps-valuation`,
`scenario-sensitivity-generator`, `portfolio-risk-management`,
`event-driven-analyzer`, `economic-impact-report`, `thesis-tracker`,
`meeting-prep`, or the internal `dashboard-builder` capability.

Standalone use is allowed only when the user explicitly asks for source review, normalization, data cleaning, QC, or style adaptation as the task itself. Even then, the support skill should state what downstream investment workflow it is preparing or de-risking.

## Internal Support Handoff Fields

Every substantial embedded support pass should preserve these fields in working context, a structured handoff, a manifest, or a support/audit artifact when one exists:

- `owning_workflow`: the Public Equity skill that owns the final investment artifact or `standalone_support_request` when the support task is explicit.
- `decision_impact`: how the source, data, QC, or style issue changes confidence, valuation, target, estimate path, sizing, hedge posture, watchlist status, or circulation readiness.
- `readiness_effect`: `decision_grade`, `research_grade`, `screen_grade`, `needs_targeted_fixes`, `not_circulable`, `not_decision_ready`, or `blocked`.
- `artifact_role`: `embedded_support_artifact`, `standalone_support_artifact`, `human_qc_report`, or `primary_workbook_when_explicitly_requested`.
- `hidden_unless_requested`: `true` for CSV, JSON, Markdown, logs, manifests, profiles, ledgers, and other machine-readable or audit sidecars unless the user explicitly asks for them.

## Hero Artifact Policy

When embedded, support outputs should feed the owning workflow's hero deliverable: HTML dashboard/report, XLSX workbook, memo/report, meeting brief, thesis tracker, or QC report. CSV, JSON, Markdown, run logs, profiles, ledgers, and manifests remain support artifacts behind that hero deliverable unless the user asks for those formats.

Do not display internal handoff field names or implementation values in the owning workflow's user-facing hero artifact. Translate material implications into plain reader-facing language, such as an evidence limitation, readiness caveat, or next source needed, while keeping the metadata available for audit or downstream processing.

When standalone, the support skill may lead with the appropriate human artifact:

- `financial-source-of-truth`: source posture and evidence ledger summary.
- `financials-normalizer`: normalized workbook or source-index package only when explicitly requested as the deliverable.
- `excel-data-cleaner`: cleaned workbook only when the task is standalone cleanup.
- `deck-report-qc`: HTML QC report for explicit QC-only work.
- `style-guide-adapter`: style profile, edit checklist, or edited artifact only when a safe artifact editor is available.

## Invocation Rules For Owning Skills

Owning skills should invoke support services when the risk is decision-changing:

- Use `financial-source-of-truth` before final claims, citations, source conflicts, stale market data, or issuer/management assertions.
- Use `financials-normalizer` before model, comps, memo, earnings, or thesis work depends on messy issuer financials, consensus/provider exports, guidance, segment tables, share count, net debt, or capital allocation inputs.
- Use `excel-data-cleaner` before workbook/model/dashboard work depends on messy tables, duplicate rows, mixed fiscal periods, malformed dates/numbers, or ambiguous identifiers.
- Use `deck-report-qc` before circulation of decks, reports, model-output packs, source-heavy memos, or dashboard/report packets.
- Use `style-guide-adapter` after substance is source-supported, when the task is to match institutional style without changing facts, formulas, citations, caveats, or source posture.

## Not-Owner Boundary

Support services do not own recommendations, rating changes, trade construction, valuation conclusions, earnings calls, or public-equity thesis decisions. If support work uncovers a decision-changing issue, it should name the issue, name the owning workflow, and state the handoff needed.
