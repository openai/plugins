---
name: deck-report-qc
description: Use when running first-pass QC on Public Equity Investing decks or reports. Do not use as external-circulation certification.
---

# Deck & Report QC

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Portfolio Models & Trackers`
- `Internal Research`
- `Company Filings & IR`
- `Market Data & Estimates`

## Deliverable Intake

When invoked as support for an owning workflow, inherit its resolved deliverable preferences and do not re-prompt. Only when this skill independently owns a new substantive standalone QC deliverable should it, before source gathering, analysis, or rendering, load `../../shared/deliverable-intake-policy.md` and perform its adaptive `request_user_input` preflight for materially unresolved preferences. For a substantive standalone QC review of an existing deck or report with supporting materials, resolve the presentation surface to a polished standalone HTML senior-review QC report unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In interactive runs, ask only remaining material questions such as depth, circulation stage, audience, or review focus; in non-interactive runs, default to the HTML QC report and `Full working analysis` while disclosing those assumptions outside the artifact.

## Purpose

Load `shared/equity-research-support-standard.md` and `shared/support-layer-routing-contract.md` before substantial source, data, QA, or style work.


Use this skill as the P0 first-pass quality-control gate for Public Equity Investing deliverables. The default job is to identify issues, prioritize fixes, and produce a senior-review QA pack. Do not imply a deliverable is externally circulable from the heuristic script alone, and do not rewrite, rebuild, or redesign the deliverable unless the user explicitly asks for remediation.

For a substantial standalone HTML QC report, load `../../shared/html-artifact-standard.md`. Let the evidence, circulation question, and highest-impact findings determine the hierarchy rather than forcing the review into a fixed dashboard module inventory.

## Embedded Support Routing

This is an embedded service under the owning workflow unless the user explicitly asks for standalone deck/report QC. Preserve the `owning_workflow` internally, such as `memo-builder`, `long-short-pitch`, `initiating-coverage`, `earnings-preview`, `earnings-deep-dive`, `economic-impact-report`, `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `thesis-tracker`, `meeting-prep`, or `dashboard-builder`.

For substantial embedded work, preserve `decision_impact`, `readiness_effect`, `artifact_role`, and `hidden_unless_requested` in internal context or support artifacts. Do not print those internal field names in the owning workflow's user-facing artifact. Do not own the recommendation or rewrite the thesis; state in natural language how QC issues change valuation, EPS, target/rating support, benchmark weight, catalyst read, source support, model confidence, client trust, or circulation readiness. A polished standalone HTML senior-review QC report is the default human deliverable for substantive explicit QC-only work; CSV, JSON, Markdown, issue logs, extraction logs, payloads, and manifests remain secondary/support artifacts unless requested.

## Operating principles

1. Treat every number, unit, footnote, chart, and conclusion as something that must tie to an identified source or model output.
2. Separate deterministic findings from judgment calls. Mark uncertain items as `needs_review` rather than overclaiming.
3. Prioritize issues by decision impact. A mismatched EBITDA value, leverage multiple, share price, EPS, revenue/KPI, price target, rating, benchmark weight, catalyst, market-data, or valuation range is more important than minor formatting polish.
4. Preserve the original artifact. QC should create an issue log and suggested fixes first; edit only when asked.
5. Apply `financial-source-of-truth` standards for source hierarchy, stale-data checks, citation format, source conflicts, and fact/assumption labels.
6. Route model-level issues to `model-audit-tieout` and data-shaping issues to `excel-data-cleaner` instead of trying to solve them inside this skill.

## Workflow

### 1. Classify the deliverable

Identify the file type and purpose:
- investor presentation, research deck, senior-style research deck, valuation deck, sell-side initiation, PM pitch deck, ETF/index diligence note, or circulation draft
- public-equity IC memo, investment memo, earnings note, macro note, research report, client note, or tearsheet
- model output deck or report linked to DCF, comps, three-statement, equity-model-update, event-driven, ETF/index, or macro analysis
- mixed pack with PPTX/PDF/DOCX/XLSX support files

If the user provides multiple files, identify the controlling artifact and the source artifacts. Example: deck is controlling output; model, evidence ledger, filing, release, transcript, and source tables are supporting materials.

### 2. Extract first-pass text, numbers, and sources

For PPTX, DOCX, XLSX, CSV, TXT, or markdown files, run the bundled first-pass scan script when available:

```bash
python scripts/inspect_deck_report.py <file1> <file2> --outdir qc_out
```

Use the script output as a first-pass map only. It is not a substitute for visual review, chart inspection, model tie-out, source-of-truth review, or PDF rendering.

For PDFs, screenshots, image-heavy slides, or scanned materials, use PDF/rendering tools to inspect pages visually before finalizing QC. If charts are embedded as images, state that the underlying chart data could not be extracted unless the model/source file is provided.

For each `critical` or `high` finding that relies on visible content, render and inspect the cited source pages or slides. Keep a plain-language record of what pages, workbook tabs, and support files were inspected, and of what could not be independently verified.

### 3. Build the QC map

Create or infer:
- page/slide/section list
- main title and thesis by page
- all repeated metrics and key claims
- source footnotes and citation coverage
- chart titles, axes, units, legends, and cited data source
- model-output tables and valuation/returns ranges
- section-level narrative conclusions

Consult `references/qc-playbook.md` for QC categories and `references/extraction-and-tieout.md` for extraction and tie-out guidance.

### 4. Run issue checks

Check at minimum:
- repeated numbers: same metric, company, period, and unit should match unless there is a disclosed reason
- units: millions/billions, dollars/local currency, percentages/bps, turns, multiples, per-share, nominal/real, annualized/LTM/NTM should be explicit and consistent
- source footnotes: each data-heavy page should identify source, as-of date, period, and whether data is company-reported, regulator-filed, market/vendor, broker/consensus, management-provided, model-derived, or internal estimate
- charts: chart title, axis units, legends, series labels, chart numbers, and narrative takeaway should agree
- narrative consistency: executive summary, page titles, subtitles, bullets, charts, and conclusion should not contradict each other
- formatting: titles, subtitles, page numbers, fonts, alignment, table formatting, footnote style, decimal precision, capitalization, and repeated labels should be consistent
- caveats: preliminary, unaudited, company-provided, non-filed, promotional, model-derived, and assumption-led items should be labeled
- compliance hygiene: do not add legal disclaimers unless requested, but flag missing caveats/disclosures where the analysis relies on uncertain or restricted inputs

Consult `references/issue-taxonomy.md` for severity and issue-type definitions.

### 5. Assign evidence confidence

Classify each consequential issue using one of these reader-facing confidence descriptions:
- `confirmed internal mismatch`: proved by contradictory values, labels, calculations, or statements within the supplied artifacts
- `externally verified error`: proved against a controlling primary or trusted dated external source
- `needs review`: suspected issue or unresolved conflict that requires a source, model, data export, or user confirmation

Do not state that an identifier, market fact, source claim, or company fact is confirmed wrong merely because supplied materials conflict or appear unlikely. Without a controlling source, state the internal conflict and route it for confirmation.

### 6. Decide the review posture

Assign one of these postures:
- `first-pass-clear`: no heuristic blockers were identified, but visual/source/model review may still be required
- `senior-review-ready`: mostly ready, with limited open questions or judgement calls
- `needs-targeted-fixes`: specific corrections are required before circulation
- `not-circulable`: material numerical, source, chart, or narrative issues remain
- `blocked`: necessary source/model files are missing

Medium source gaps, repeated-number mismatches, and unit/period ambiguity usually mean `needs-targeted-fixes`, not `senior-review-ready`.

### 7. Produce the QC output

Default output should be a senior-review QC readout. Use chat for narrow reviews. For substantial standalone QC-only work, produce a polished standalone HTML senior-review QC report following `../../shared/html-artifact-standard.md`. When the script is used, the reader-facing artifact should be `public_equity_investing_deck_qc_report.html`; CSV, JSON, manifests, payloads, and support notes are audit/import support unless the user asks for them.

Use `dashboard-builder`, `references/DASHBOARD_PACK.md`, and `references/dashboard-map.md` only when the user explicitly asks for a standardized dashboard, reusable dashboard template, issue cockpit, remediation tracker, or structured payload-driven render. On that optional path, `deck-report-qc` owns issue identification, severity, tie-out judgment, circulation posture, and remediation sequence; `dashboard-builder` owns the shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV support files behind the HTML dashboard unless explicitly requested.

The QC readout should include:
1. Executive QC verdict
2. Circulation posture
3. Review scope and evidence limitations: what was inspected, tied out, externally verified, and not independently verified
4. Decision-critical tie-out or recommendation support, when applicable
5. Top issues by severity and remediation sequence
6. Issue log table with confidence descriptions
7. Repeated metric / number tie-out table
8. Source and footnote coverage table
9. Chart and narrative tie-out findings
10. Formatting/presentation polish findings
11. Open questions / missing support files

Use `references/output-templates.md` for default templates.

For standalone HTML, keep the first screen focused on the verdict, circulation posture, evidence scope, and the few findings that change senior reliance. When a valuation, target-price, recommendation, rating, benchmark-weight, or other decision-critical tie-out exists, place the `Decision-Critical Tie-Out` section before `Top Issues`, `Must Fix Before Circulation`, or the full issue log; do not make the reader pass through the broader findings register before seeing the central control failure. Place comprehensive registers, source-coverage tables, and presentation-polish findings lower in the report.

Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, at both desktop and narrow/mobile widths. Tables may scroll horizontally inside a clearly bounded table wrapper on narrow screens, but they must not widen the entire page. In mobile QA, verify that the document viewport itself has no horizontal overflow, for example `document.documentElement.scrollWidth <= document.documentElement.clientWidth`; use constrained grid/section children and `max-width: 100%; overflow-x: auto` table wrappers where needed. Iterate on hierarchy, table density, clipping, contrast, and whitespace before delivery.

When `scripts/inspect_deck_report.py` was used before a substantive standalone HTML review, write a small JSON review record identifying `completed_reviews` and remaining `missing_inputs`, then finalize the existing output path after HTML visual inspection:

```bash
python scripts/inspect_deck_report.py --finalize \
  --outdir <final-output-dir> \
  --scan-dir <first-pass-output-dir> \
  --primary-report <final-output-dir>/public_equity_investing_deck_qc_report.html \
  --review-record <final-output-dir>/qc_review_record.json
```

Finalization must make the polished HTML the sole primary human deliverable, reconcile manifest status to the work actually performed, and remove the provisional dashboard contract for ordinary standalone HTML reviews. Add `--keep-dashboard-contract` only when the user explicitly selected the standardized-dashboard path.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: source and number tie-out, chart/visual review, narrative consistency, formatting/circulation posture, and issue log. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.

When embedded in a broader workflow, "lead" means lead for QC only; the owning workflow remains the investment-artifact owner.


## Severity rules

Use these severities:
- `critical`: could change investment decision, valuation, rating, price target, sizing, market read, or client trust
- `high`: material inconsistency or missing support that must be fixed before circulation
- `medium`: localized inconsistency, unclear caveat, formatting issue, or missing source detail that should be fixed
- `low`: polish item that does not affect substance
- `needs_review`: possible issue that requires visual, model, source, or user confirmation

Never hide uncertainty. If a number may be wrong but cannot be proven wrong from available files, label it `needs_review` and ask for the model/source support.

## P0 skill routing

Use `references/p0-integrations.md` when deciding whether an issue belongs in this skill or should be routed to another P0 skill.

Common routes:
- source hierarchy, stale data, citation standard, source conflict, fact/assumption labeling -> `financial-source-of-truth`
- workbook formula, model logic, sensitivity, scenario, source tie-out -> `model-audit-tieout`
- messy tabular data, duplicated rows, bad date/number formats -> `excel-data-cleaner`
- valuation model construction or repair -> `dcf-model-builder`, `comps-valuation`, or `three-statement-model-builder`
- public issuer, equity event, or thesis support -> `event-driven-analyzer`, `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, or `long-short-pitch`; credit-first packs, public-credit memos, bond/loan/CDS decks, covenant/recovery packs, and debt-security materials route to Credit Markets
- final IC synthesis -> `memo-builder`

## Final checks before responding

Before final output, verify:
- every critical/high issue has location, evidence, why it matters, and suggested fix
- every consequential issue identifies whether it is a `confirmed internal mismatch`, an `externally verified error`, or `needs review`
- every repeated metric table distinguishes exact mismatch from possible period/unit mismatch
- source gaps are not presented as factual errors unless a controlling source proves the issue
- formatting findings are separated from investment-substance findings
- the final posture matches the severity of remaining issues
- the response does not imply the deck/report is fully verified if charts, screenshots, PDFs, or source models were not inspectable
- the HTML report and any support manifest or review note agree on what was visually inspected, tied out, and still unverified
- standalone HTML keeps any decision-critical tie-out above the broader issue register and does not introduce page-level horizontal overflow at narrow/mobile widths
