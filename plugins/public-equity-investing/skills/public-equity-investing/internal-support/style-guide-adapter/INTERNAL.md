---
name: style-guide-adapter
description: Use when extracting or QCing Public Equity Investing artifact style. Do not use as the primary file-editing engine.
---

# Style Guide Adapter

> Internal support playbook. Load through `internal-support/policy.md`; this style capability is bundled with the visible router rather than exposed as a skill entrypoint.

## Deliverable Intake

When invoked as support for an owning workflow, inherit its resolved deliverable preferences and do not re-prompt. Only when this skill independently owns a new substantive standalone style deliverable should it, before source gathering, analysis, or rendering, load `../../../../shared/deliverable-intake-policy.md` and perform its adaptive `request_user_input` preflight for materially unresolved preferences.

## Overview

Load `shared/equity-research-support-standard.md` and `shared/support-layer-routing-contract.md` before substantial source, data, QA, or style work.


Adapt finance artifacts to the target institution's visual, structural, and writing style using explicit style sources first and inferred precedent patterns second. Treat style adaptation as non-destructive by default: preserve facts, numbers, formulas, citations, and source links unless the user explicitly asks to change them.

This is a shared-core Public Equity Investing skill. It can be used on its own or composed with builder/QC skills such as `comps-valuation`, `dcf-model-builder`, `three-statement-model-builder`, `equity-model-update`, `memo-builder`, `long-short-pitch`, `deck-report-qc`, `financial-source-of-truth`, and spreadsheet/modeling skills.

The shipped deterministic helper extracts Office style metadata only; it is not a style-application engine. `scripts/extract_office_style.py` reads `.pptx`, `.docx`, and `.xlsx` metadata and emits a style profile aid. It does not rewrite, reformat, restyle, or save edited Office artifacts.

## Embedded Support Routing

This is an embedded service under an owning workflow unless the user explicitly asks for standalone style extraction, style QC, or style adaptation. Preserve the `owning_workflow` internally, such as `memo-builder`, `long-short-pitch`, `initiating-coverage`, `deck-report-qc`, `dashboard-builder`, `meeting-prep`, `earnings-preview`, `earnings-deep-dive`, `dcf-model-builder`, `three-statement-model-builder`, or `comps-valuation`.

For substantial embedded work, preserve `decision_impact`, `readiness_effect`, `artifact_role`, and `hidden_unless_requested` in internal context or support artifacts. Do not print those internal field names in the owning workflow's user-facing artifact. Do not own the investment conclusion; state in natural language how style choices affect clarity, auditability, source posture, compliance/circulation readiness, or reader trust. Style profiles, JSON, Markdown, logs, and manifests are secondary/support artifacts when invoked by an owning workflow, and style is not evidence.

## Core decision tree

1. **Identify the artifact and mode**
   - **extract style**: build a style profile from precedents, templates, examples, or instructions.
   - **apply style**: produce a concrete change plan and, only when an editing tool is available, apply safe style edits through that artifact-specific tool.
   - **create in style**: produce a new artifact using the target style profile.
   - **style QC**: compare an artifact against a target style and list fixes.
2. **Gather style sources** using the hierarchy below. If sources are missing, proceed with a conservative finance-default style and list what would improve fidelity.
3. **Build a style profile** covering visual system, layout grammar, writing voice, exhibit conventions, citation/footnote norms, and artifact-specific rules.
4. **Apply only style-safe changes by default and only through the correct artifact surface.** Do not delete, overwrite, or materially change content, data, formulas, source links, speaker notes, hidden sheets, comments, tracked changes, or version history unless explicitly requested.
5. **Run style QC** and provide a change log, unresolved ambiguities, and confidence level.

## Source hierarchy

Style is not evidence: precedent decks and memos can define tone, structure, and formatting, but they are not factual support for prices, consensus, estimates, financials, ratings, targets, or investment claims. Use `financial-source-of-truth` for substance.


Use the highest-quality applicable source. For any content, number, market data, or factual claim, delegate to `financial-source-of-truth` rules rather than treating style precedents as factual evidence.
For detailed source and non-deletion rules, use [references/source-and-safety.md](references/source-and-safety.md).

1. **User's explicit instructions in the current task**.
2. **Official style guide / brand book / writing guide / compliance template** supplied by the user or available through callable runtime apps/connectors. If not callable, request the file/export and label the style source gap.
3. **Approved template or master file**: PowerPoint template, Word template, spreadsheet template, memo shell, model shell, or institutional boilerplate.
4. **Current artifact being edited**: existing master slides, named styles, workbook themes, defined names, chart templates, footnote patterns, and repeated internal conventions.
5. **Final / sent / approved precedents** from the same institution, client, team, deal type, committee, or publication series.
6. **Draft or adjacent precedents** from the same institution or similar artifact type.
7. **User-provided description of desired style**.
8. **Public website / brand materials / web search** only when no private style source exists or the user asks for public-brand matching.
9. **Generic institutional finance conventions** only as a fallback.

Resolve conflicts as follows: explicit user instruction beats all; official guide beats precedent; current client style beats generic firm style; final approved precedents beat drafts; repeated patterns beat one-off quirks; recent examples beat stale examples when they are equally authoritative.

## Stale-style and conflict checks

Before applying a style, check whether sources are likely current:

- Prefer files named or labeled current, latest, final, approved, sent, board-ready, client-ready, vfinal, or template.
- Treat files named draft, old, archive, deprecated, backup, prior-year, or sample as lower-confidence unless the user says otherwise.
- Use document content, metadata, and user context to assess freshness; do not rely only on file modified date.
- If two sources conflict materially, state the conflict and use the highest-priority source. Do not blend incompatible styles unless asked.
- If only one weak sample exists, label extracted rules as inferred, not definitive.

## Fact, assumption, and inference labeling

Use these labels in summaries, change logs, and style profiles when relevant:

- **style fact**: directly observed from a guide, template, or repeated precedent pattern.
- **style inference**: inferred from limited examples or repeated but undocumented behavior.
- **style assumption**: chosen because no style source was available.
- **content fact**: sourced number, quote, date, metric, or claim.
- **content assumption**: unsourced or user-supplied assumption used in the artifact.

Do not label everything. Label only rules or assumptions that affect meaningful style, compliance, or interpretation.

## Style profile structure

Create or update a style profile before applying changes. Use the detailed extraction guidance in [references/style-extraction-playbook.md](references/style-extraction-playbook.md). Include only fields that are supported by sources or useful for the task.

Minimum style profile:

- **source basis**: files, links, pages/slides/tabs, or user instructions used; source priority and confidence.
- **visual system**: colors, fonts, typography hierarchy, spacing, grid, margins, logo/branding, icons, imagery, and accessibility constraints.
- **layout grammar**: title style, subtitle/kicker style, page/slide structure, section dividers, exhibit placement, chart/table positioning, callout boxes, footers, page numbers, confidential labels, and appendix conventions.
- **exhibit conventions**: chart types, table style, unit placement, decimal precision, period labeling, currency conventions, negative numbers, variance colors, footnote/source placement, and annotation density.
- **writing voice**: sentence length, tone, level of assertiveness, headline style, so-what structure, bullet grammar, tense, jargon tolerance, and caveat style.
- **artifact-specific rules**: deck, memo, spreadsheet/model, research note, PM memo, sell-side note, ETF/index diligence note, client equity report, or committee-pack requirements. Credit memo style belongs in Credit Markets unless the artifact is only a public-equity read-through.
- **do-not-change rules**: content, data, formulas, citations, hidden tabs, notes, comments, tracked changes, source links, or legal/compliance language that must remain intact.

## Non-destructive editing rules

- Work on a copy unless the environment provides explicit safe edit/versioning behavior.
- Preserve all formulas, linked data, named ranges, cell comments, hidden sheets, footnotes, citations, speaker notes, alt text, tracked changes, embedded objects, and source URLs unless explicitly asked to modify them.
- Do not delete slides, sections, rows, columns, sheets, notes, comments, exhibits, citations, or appendix content unless the user explicitly asks.
- Do not overwrite firm/client templates, masters, or original precedents. Use them as references or create a derived copy.
- Keep the same factual content unless asked to rewrite. When tightening language, preserve meaning and mark substantive edits separately from style edits.
- If a requested style change would reduce readability, accessibility, auditability, or factual clarity, flag the tradeoff and apply the safer variant.

## Artifact-specific routing

Use artifact-specific tools/skills for actual file edits. If those tools are not available, provide a style profile, exact edit checklist, and before/after text examples rather than implying that the extractor changed the file.

- **PowerPoint / slides**: use the presentation/deck editing tool when available. Preserve master slides, layout IDs, notes, charts, embedded Excel links, footers, logos, and page numbers. Prefer native theme/layout changes over manual per-shape hacks when possible. See [references/artifact-application-rules.md](references/artifact-application-rules.md).
- **Word / memos / reports**: use the document editing tool when available. Preserve styles, headings, bookmarks, comments, tracked changes, footnotes/endnotes, citations, tables of contents, and cross-references.
- **Excel / Sheets / models**: use the spreadsheet/model-builder tool when available. Preserve formulas, formats tied to model semantics, named ranges, validations, comments, hidden tabs, grouping, and source tabs. Never hardcode formulas or paste values over formulas for style reasons.
- **Text-only outputs**: adapt voice, structure, headings, bullets, caveats, and source presentation without inventing visual styling.

For uploaded Office files, optionally run `scripts/extract_office_style.py` to extract theme colors, fonts, style names, slide counts, and workbook/document style metadata before deeper visual review. The helper defaults to JSON for downstream tooling; use `--format markdown` only when the user explicitly wants a style-profile support note.

## Applying writing style

When the task involves prose, use [references/writing-style-adaptation.md](references/writing-style-adaptation.md). Preserve meaning and evidence posture.

Common finance writing defaults when no stronger style is available:

- Use title headlines with a clear so-what, not generic labels.
- Lead with the implication, then supporting data.
- Prefer concise bullets and parallel structure.
- Use active voice and avoid marketing adjectives unless the source language uses them.
- Separate facts, assumptions, management claims, and analyst judgment.
- Keep caveats crisp and decision-useful.

## Output requirements

Choose the format that matches the user request. For complete templates, use [references/output-templates.md](references/output-templates.md).

Always provide, at minimum:

1. **What was used**: style sources and confidence.
2. **What changed**: concise change log separating visual/layout edits from writing/content edits.
3. **What was preserved**: data, formulas, citations, source links, notes, comments, hidden sheets, or other sensitive elements.
4. **Open issues**: missing sources, conflicts, stale-style concerns, or style assumptions.
5. **Next best input** if fidelity is limited: template, final approved example, brand guide, master deck, memo precedent, or client-specific sample.

If delivering an edited artifact through an artifact-specific tool, also provide the output file and a short QA summary. If only advising or using the bundled extractor, provide a style profile, recommended edits, and sample before/after transformations.

## Quality bar

Before finalizing, verify:

- Style choices are traceable to the selected source hierarchy.
- The artifact still says the same thing unless substantive edits were requested.
- Numbers, signs, units, footnotes, formulas, and source citations were not altered accidentally.
- The output is internally consistent across pages/slides/tabs: titles, fonts, colors, spacing, chart/table treatment, footers, and source lines.
- Style assumptions are visible and reasonable.
- The result looks/sounds like the target institution without copying confidential text beyond what the user supplied or has access to.
