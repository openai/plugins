---
name: google-docs
description: Prompt- and template-complete Google Docs creation and editing with explicit-instruction-authoritative structural preservation, including semantic roles, relationships, comparison dimensions, and instructed extensions; full-topology native-copy routing; source-grounded per-tab adaptation for past/example references; style-preserving hyperlink and table edits; canonical smart-chip-first authoring for dates and relevant supported people or Google resources; a file-backed advisory trusted read before existing-document writes; automatic protected-control awareness; direct connector APIs by default; DOCX-first import only when no supplied Google Doc template/reference constrains the output; and checked-in code mode only for exact native dropdown mutation. Use when Codex must create, edit, fill, adapt, redesign, or verify Google Docs without overriding explicit user/template instructions, adding unrequested document scope, or carrying stale reference facts into a new deliverable.
---

# Google Docs

Use this opt-in skill for Google Docs work in Codex local-plugin sessions. Draft once to the requested final shape, prove explicit prompt/source/template coverage, then compress repetition without removing unique requirements.

Code mode is preferred for the checked-in helpers below, but it is not a prerequisite for this workflow. If code mode is unavailable, reproduce the same routing, read and inventory, preservation, mutation, and verification workflow with the available connector or app tools; preserve all checks and adapt any operation without a non-code implementation to the closest supported equivalent, clearly disclosing any unavoidable fidelity difference.

### Documents clarification questions

- Ask for new documents or major rewrites. Skip this for edits/conversions.
- Inspect prompt, conversation history, existing file and relevant references to figure out what questions to ask.
- Questions should cover topic, audience, and purpose and come before planning
- When asking questions, focus on consequential dimensions not stated or clearly implied.
- When the artifact is a new analysis, focus on which definition, metric, or lens should drive conclusions.
- Unresolved reference labels or question marks are user-owned: ask, don't infer.
- Once topic, audience, and purpose are clear, proceed without asking. Choose emphasis, format, length, style, details. Use placeholders for missing facts.

Use `request_user_input` once if available, else ask via a message. Have the best suggestion first. Append `(Recommended)` to its label. Have another good alternative second. Have `Use your judgment` as the third and final option. If the request times out or returns no answer, proceed using your best judgment; do not ask again.

## Default Routing

Choose the route only after resolving whether a supplied Google Doc is a template, reference, example, or content-only source:

1. **Supplied Google Doc template or reference:** read `references/reference-template-preservation-and-edit-scope.md`, inspect the native reference signature below, and remain on a native Google Docs route. Do not delegate authoring to DOCX.
   - Exact template replacement: copy the native document and replace content inside the copied structure.
   - Template extension or adaptation: copy the native document, then make only the required native additions, removals, or expansions.
   - Selective reference use: choose this only when the user explicitly asks to borrow selected parts. Use a native copy and prune it, or create a native Google Doc directly when the selected parts contain no native structure that must be carried forward.
   - Multi-tab invariant: when the supplied document has more than one tab, start from a full native copy and preserve the complete tab tree—tab count, titles, order, and parent/nesting—unless the user explicitly requests a single-tab result, identifies selected tabs/parts to borrow, or directs removal. A URL that opens one tab and wording such as “use this as a reference” do not authorize collapsing the document.
   - Structural preservation and content treatment are separate decisions. Structural preservation covers both native form and semantic organization: tab topology, section order, container identity and position, field roles, table row and column roles, comparison dimensions, ordering, dependencies, and operative instructions embedded in or adjacent to retained structures. It does not freeze the initial dimensions; when the user or template directs an extension, deletion, substitution, or reordering, perform that change inside the native structure. Applicable user and template instructions take precedence over this skill's layout, compaction, and styling defaults; those defaults apply only where the governing sources are silent. For a past/example reference used to build a new deliverable, retained tabs preserve their native structure and styling but default to `adapt content`; they do not preserve prior-project facts, people, dates, links, approvals, or copy. A “legacy,” “reference,” or “do not use” label does not make stale content acceptable in the finished artifact.
2. **Blank or basic net-new native creation without a constraining Google Doc template/reference:** read `references/reference-native-create-direct.md`, create the file with `mcp__codex_apps__google_drive._create_file`, and use direct Docs `batchUpdate` requests when content is requested.
3. **Polished or layout-sensitive net-new creation without a constraining Google Doc template/reference:** use `[@documents](plugin://documents@openai-primary-runtime)` with the `google_docs_default` preset, then read `references/reference-import-docx-to-native-docs.md` and import as native Google Docs. A supplied Google Doc template/reference disqualifies this route even when the requested result is polished; a content-only source does not. After import, replace mandatory chip-eligible values with native chips during post-import normalization.
4. **Existing document reads, summaries, edits, comments, and preservation-only work:** use Google Docs connector or app tools directly. Before the first write to an existing document, use the checked-in file-backed trusted read described in `references/reference-trusted-read-wrapper.md`; inspect its compact control warning immediately and read normalized document content from the returned file path. Targeted follow-up reads may use connector tools directly.
5. **Exact native dropdown creation, option replacement, or selected-value mutation:** use the checked-in Google Docs dropdown workflow for every mutation in the task after capability discovery. Read `references/reference-dropdown-code-mode.md`.

When the prompt is ambiguous, default to native copy-and-adapt rather than selective borrowing or DOCX reconstruction. Do not create a blank destination or begin a DOCX draft before this decision.

### Native reference signature

Before planning content for a supplied Google Doc template/reference:

1. Read full document metadata and enumerate every tab before reading a single tab in depth: tab id, title, parent, nesting, and order. A URL ending in `?tab=t.0` identifies the initially visible tab, not the full reference scope.
2. Record a compact signature for relevant heading roles: named style, font family, size, weight, color, and spacing.
3. Record each relevant table's tab, shape, semantic row and column roles, comparison dimensions, applicable instructions in or adjacent to the table, borders, fills, padding, widths, and representative text styling.
4. Record relevant native elements and their locations: people/date/rich-link chips, links, images, lists, controls, headers, and footers.
5. Give every tab two treatments: a structural treatment (`retain`, `extend`, `reorder by user direction`, or `remove by user direction`) and a content treatment (`carry current content`, `adapt`, `replace`, or `clear`). Unmentioned tabs default to `retain structure`; when the reference describes a different project, event, product, experiment, incident, or time period, their content defaults to `adapt`, never carry.
6. Record reference-only factual signatures that must not leak into a new deliverable: prior names and organizations, product/project identifiers, dates and times, venues, links and chips, owners and approvers, claims, metrics, statuses, and distinctive copy. The user prompt governs the requested outcome; applicable instructions in the selected template/reference govern how retained structures must be used or adapted; designated content sources govern facts. Skill defaults apply only where those authorities are silent. A template/reference governs facts only when the user explicitly makes its content authoritative.

Do not flatten paragraphs across tabs until the tab tree is recorded. If a full response is too large or truncated, request `tabs(tabProperties)` first and inspect relevant tabs individually. For exact-template and template-adaptation work, use the Drive copy action exposed by the current runtime, then run the file-backed trusted read on the copied destination before its first write. If native copy is unavailable and tabs, styles, chips, controls, or other native semantics matter, stop rather than silently rebuild through DOCX.

Do not block blank or basic eligible creation on the Documents plugin. For eligible DOCX-first work, keep staging untracked and non-user-visible, clean it after successful native import and readback, and return only the Google Docs link unless the user requested local files.

### Documents location

Use/create `ChatGPT` at My Drive root. Place new documents created from scratch or from a template there.
Edit existing documents in place.

Respect user-specified locations.

## Coverage-First Authoring Contract

1. Derive completeness only from explicit user requirements, supplied source content the user asks to carry forward, and applicable template/reference instructions, fields, containers, or functional sections.
2. Before drafting, keep a compact in-memory coverage map with: obligation, authority (`prompt`, `source`, or `template/reference`), required output form, planned destination, and final state (`present`, `unavailable-with-disclosure`, or `omitted-by-explicit-user-direction`). Distinguish factual authority from structural authority: a past/example reference may authorize form, semantic organization, instructions, and style without authorizing any of its facts. Do not persist, serialize, count, hash, or script-validate the map.
3. Use document archetypes only to organize requested material. They never create obligations, sections, evidence requirements, or depth by themselves.
4. Draft once toward the intended final shape; do not create an intentionally maximal draft. Prove coverage before optimizing length.
5. Research externally only when requested, when current/time-sensitive facts are material, or when supplied sources cannot support required factual accuracy. For requested evidence, follow `references/reference-citations-and-hyperlinks.md`.
6. Include methodology, assumptions, alternatives, risks, or sensitivity only when requested or materially necessary to satisfy an obligation.
7. Compress repeated wording and duplicated rationale only after coverage passes. Never remove or merge a unique requirement, requested fact/citation/source, template instruction, field or functional section, distinct decision/owner/dependency/risk/action, comparison dimension, or requested native structure merely to shorten the document.
8. If complete content cannot meet an explicit page limit without unreadable text or a typography-floor violation, report the conflict rather than silently omit content.
9. Never fill a missing fact from a past/example reference merely because its slot needs content. Use the current source, a clearly labeled recommendation, or an explicit unavailable/TBD disclosure. Do not carry a reference-only schedule time, person, link, metric, status, or claim into the new artifact.

Do not use required-unit or evidence ledgers, evidence-level classifications, archetype completeness budgets, document-mode contracts, typography exception ledgers, density-trigger ledgers, a draft-everything-then-compress workflow, or automatic depth based only on document category.

## Native Smart-Chip Authoring Invariant

Use native smart chips whenever the connector supports them and the source contains the required semantic value. The following cases are mandatory, not optional polish:

1. Insert every concrete semantic date added to the document as a `dateElement` with `insertDate`, including dates in prose, metadata fields, lists, and tables. Do not newly type a date as plain text. If the source does not identify the date precisely enough to produce a faithful timestamp, do not invent missing date components; preserve an existing ambiguous value or surface the ambiguity.
2. First decide whether a person belongs in the finished document. For every template/reference person chip, classify the role as `carry forward`, `replace from source`, or `remove as example/project-specific content`. Do not preserve a person merely to retain a chip count, and do not discard a reusable/current template contact merely because the task source omits them. When a relevant person name remains or is added and a verified email address is available, use a `person` chip with `insertPerson`. Use plain text only when no email is available, and never guess an address.
3. When a Google Calendar event URL is available, represent the event with a `richLink` chip using `insertRichLink`. Keep descriptive context outside the chip rather than duplicating the raw URL.
4. Represent every link to a Google Doc, Google Sheet, or Google Slides presentation as a `richLink` chip using `insertRichLink`, including links in narrative text, tables, citations, source lists, and appendices. This applies to copied existing links as well as newly inserted links. Canonicalize every retained Workspace URI with `scripts/canonicalize_google_workspace_url.mjs`; replace relevant noncanonical rich links, remove irrelevant reference-era links, and use the canonical file URL without account-routing segments, share parameters, tab/range/heading/slide queries, or fragments. When a location-specific deep link is materially useful, keep the canonical file chip and add a separate readable ordinary hyperlink for that location. Never leave an ordinary Workspace hyperlink as the sole representation.

For other supported Google resource URLs, prefer a `richLink` when it is convenient and improves scanning. Plan chip positions while composing the text skeleton, account for each chip's one-code-unit range, and verify the native element type and properties after writing. These requirements apply to direct-native, copied-template, existing-document, and post-import workflows. Read `references/reference-smart-chips-and-building-blocks.md` and the request examples in `references/reference-direct-request-composition.md` before the first chip write.

## Launch-Blocking Output Invariant

A result is incomplete if it silently omits an explicit requirement, requested source content, template/reference field, required link or figure, requested native structure, mandatory smart chip, or distinct functional section. Matching visible text is not enough when native semantics are required. These are content failures, not optional polish.

Unavailable information may remain visibly TBD or be disclosed only when the source truly lacks it. Preserve unsupported native structures by copy, use an explicitly approved fallback, or stop before destructive work. A shorter document is not automatically better.

## Runtime And Dropdown Route

Direct connector execution is the default. Do not use ad hoc code-mode bridges, subprocess connector writers, private Google RPCs, browser/UI writers, model-authored executable helpers, or `google-docs-cm`.

Resolve dropdown intent before the first write:

| Task | Route |
| --- | --- |
| No dropdown involvement | Direct connector |
| Preserve an existing dropdown | Direct connector with targeted preservation |
| Create a native dropdown | Checked-in Google Docs dropdown code mode |
| Replace dropdown options | Checked-in Google Docs dropdown code mode |
| Change selected value | Checked-in Google Docs dropdown code mode |
| Text/table edits plus dropdown mutation | Dropdown code mode owns every mutation |
| Required dropdown tools unavailable | Stop before exact mutation |

Exact mutation requires runtime discovery of both `getDocumentDropdowns` and `updateDocumentDropdown`. Public Docs `batchUpdate` cannot prove dropdown semantics. Once dropdown code mode is selected, do not switch writers mid-task.

## Direct-Request Workflow

For native copies, connector-created docs with content, existing-document edits, and post-import repairs:

1. Gather the requested source material.
2. Copy, create, or attach to the destination document according to the resolved route.
3. Resolve the exact document id, URL, complete tab tree, active `tabId`, and current revision where exposed.
4. For the first full read before writing an existing document, invoke `host/docs-trusted-read-file-bridge.mjs` exactly as described in `references/reference-trusted-read-wrapper.md`. It persists the raw response, control inventory, machine-readable outline, and annotated model-readable text while returning automatic advisory control awareness. Do not transport the raw response with `text()` or `apply_patch`.
5. Read the returned `document_text` artifact, inspect `controlAwareness`, and record compact working notes for target ranges, nearby styles, table coordinates, native elements, revision, and preservation warnings. Read the raw result only when normalized artifacts omit a required field.
6. For template/reference work, compare the copied destination against the native reference signature before drafting. If the source has multiple tabs, confirm the destination already has the same complete tab topology before any content write; do not proceed from a blank or single-tab destination. Apply the separate structural/content treatment for every tab, and do not finish one tab while leaving other retained tabs as historical reference material. For structured existing-document work, use the targeted snapshot in `references/reference-template-preservation-and-edit-scope.md`.
7. Classify every planned and copied semantic date, relevant known-email person, Google Calendar event URL, and Google Docs/Sheets/Slides URL; canonicalize retained Workspace file URLs and allocate mandatory `insertDate`, `insertPerson`, or `insertRichLink` requests rather than emitting plain text or ordinary hyperlinks.
8. Compose the smallest clear `batchUpdate` request batch. Split large or fragile edits into verified batches.
9. Use `write_control.requiredRevisionId` when a fresh revision should fail fast on collaborator conflicts.
10. Re-read after substantive or index-shifting writes and continue from live indexes.
11. Reconcile the coverage map, then verify and repair requested content and connector-observable presentation before final handoff.

Do not rebuild an entire document to perform a targeted edit. If a native component cannot be safely preserved or verified, stop before destructive work and report the limitation.

## Stateful Operation

Keep the target URL, document id, tab tree, active `tabId`, source materials, relevant readback, live ranges, write batches, and verification status current. Refresh state after document switches, source gathering, connector errors, or runtime resets.

## Meeting-Notes Fast Path

For calendar-backed meeting-notes requests, read only `references/reference-meeting-notes-direct.md` unless the task adds tables, figures, citations, import/export, or other requirements. Use connector readback—not HTML or PDF—as the verification surface for this text-only path.

## Universal Completion Checks

Before handoff, verify:

1. the target document and complete tab topology are correct; for a multi-tab template/reference, every source tab has both its planned structural treatment and its completed content treatment, or an explicit user-authorized removal
2. every coverage-map obligation is present, explicitly unavailable, or omitted only by user direction
3. required source content and template/reference fields are in the intended location and form
4. relevant heading and table style signatures match the template/reference except for intentional changes; expanded tables reuse the canonical peer's header/body cell styles, borders, fills, padding, widths, and typography
5. headings, body text, native links, tables, figures, and lists are coherent and readable
6. every mandatory chip opportunity is represented by `dateElement`, `person`, or canonical `richLink` as applicable; copied relevant rich links are canonicalized, no ordinary Docs/Sheets/Slides hyperlink is the sole representation, each retained person chip passed the relevance decision, and relevant existing chips, native controls, and other native elements read back with the correct connector-visible semantics
7. each retained tab is source-current; no reference-only facts, obsolete names/chips, dates, times, links, claims, statuses, distinctive prior-project copy, placeholders, duplicate sections, accidental empty bullets, or scaffolding remain. Historical content may remain only when the user explicitly requested it
8. every ordinary hyperlink preserves the sampled surrounding font family, size, weight, emphasis, color, underline state, and paragraph role after readback
9. no unrelated source or template structure changed
10. layout-sensitive work passed final PDF visual QA, or the unavailable verification is stated plainly

Run feature-specific checks only for features used: evidence targets, template/reference semantic inventory, dropdown metadata, table-cell native lists, explicit global formatting, branded furniture, figures, or layout-sensitive rendering. Semantic reconciliation may reopen content scope to repair an omission; formatting repair may not unless it exposes one. During evaluation, classify repairs as prompt/content omission, source/template omission, native-structure fidelity, targeting, formatting, or pagination/layout.

## Required Read Order

Before writing, read only the references selected by the active route:

- Blank native doc: `references/reference-native-create-direct.md`.
- Basic native doc with content: `references/reference-native-create-direct.md` and `references/reference-direct-request-composition.md`.
- Supplied Google Doc template/reference: `references/reference-template-preservation-and-edit-scope.md` before choosing a construction route; do not use DOCX-first import.
- DOCX-first import for eligible reference-free creation: the Documents skill and `references/reference-import-docx-to-native-docs.md`; use task-specific references for requested shapes, evidence, or post-import repairs.
- Calendar-backed meeting notes: `references/reference-meeting-notes-direct.md`.
- Simple text or supported-chip edit: `references/reference-direct-request-composition.md`.
- Any output containing a semantic date, a person whose verified email is available, a Google Calendar event URL, or a Google Docs/Sheets/Slides URL: `references/reference-smart-chips-and-building-blocks.md` and `references/reference-direct-request-composition.md`.
- Any Google Docs/Sheets/Slides URL with account-routing, sharing, tab, range, heading, bookmark, or slide-specific parameters: run `scripts/canonicalize_google_workspace_url.mjs` before `insertRichLink`.
- First write to an existing Google Doc: `references/reference-trusted-read-wrapper.md`; use the file-backed bridge for the initial full read, then continue on the selected direct or dropdown route.
- Non-meeting structural edit: `references/reference-connector-runtime-and-safety.md`, `references/reference-foreground-guard.md`, `references/reference-request-shapes-and-write-safety.md`, and `references/reference-direct-request-composition.md`.
- Existing structured document, template/reference adaptation, tab duplication, branded furniture, or work near native controls: also `references/reference-template-preservation-and-edit-scope.md` and, when an explicit output form is requested, `references/reference-request-shapes-and-write-safety.md`.
- Research, current facts, metrics, citations, benchmarks, or source links: `references/reference-citations-and-hyperlinks.md`.
- Non-simple chip, dropdown, or building-block work: also `references/reference-smart-chips-and-building-blocks.md`.
- Exact dropdown create/options/selection mutation: `references/reference-dropdown-code-mode.md`, `references/reference-template-preservation-and-edit-scope.md`, and `references/reference-smart-chips-and-building-blocks.md`.
- List inside a table cell or boxed section: also `references/reference-response-and-list-format.md` and `references/reference-table-formatting-deep-dive.md`.
- Explicit formatting of all/every/throughout analogous tables: `references/reference-request-shapes-and-write-safety.md` and `references/reference-table-formatting-deep-dive.md`.
- Layout-sensitive, table-heavy, figure-heavy, polished, or final-deliverable work: `references/reference-section-completeness-and-final-pass.md` and `references/reference-pdf-export-visual-qa.md` before handoff.

Do not bulk-read the reference folder. Do not execute content writes until route-required references are read in the current turn.

## Connector Safety

1. Confirm the exact target document, complete tab tree, and active `tabId` before writes.
2. Resolve the section, table, cell, paragraph, or native control from current connector readback.
3. Use full `get_document` when styles, lists, tables, chips, tabs, headers, footers, or native controls matter; use targeted reads only for simple unambiguous text.
4. Use `get_tables` before table creation, population, list-in-cell work, or global table formatting.
5. Re-read after insertions, deletions, table changes, native-control changes, or other index-shifting operations.
6. Create a native copy before adapting a reusable Google Doc template/reference; edit an explicitly targeted working document in place.
7. Never claim a connector or native feature is unavailable without current-run capability evidence.

## Task Reference Map

| Task area | Reference |
| --- | --- |
| Blank/basic native creation | `references/reference-native-create-direct.md` |
| Runtime attachment and recovery | `references/reference-connector-runtime-and-safety.md` |
| File-backed trusted read, automatic control awareness, and normalized document content | `references/reference-trusted-read-wrapper.md` |
| DOCX import without a constraining Google Doc template/reference | `references/reference-import-docx-to-native-docs.md` |
| Target confirmation | `references/reference-foreground-guard.md` |
| Request shapes and range safety | `references/reference-request-shapes-and-write-safety.md` |
| Direct request examples and supported chips | `references/reference-direct-request-composition.md` |
| Headings and question formatting | `references/reference-headings-and-question-format.md` |
| Lists, including lists inside table cells | `references/reference-response-and-list-format.md` |
| Citations and hyperlinks | `references/reference-citations-and-hyperlinks.md` |
| Template and edit-surface preservation | `references/reference-template-preservation-and-edit-scope.md` |
| Chips, dropdown preservation, and building blocks | `references/reference-smart-chips-and-building-blocks.md` |
| Exact dropdown mutation | `references/reference-dropdown-code-mode.md` |
| Tables and explicit global table formatting | `references/reference-table-formatting-deep-dive.md` |
| Figures and images | `references/reference-figures-and-image-insertion.md` |
| Final structural and visual QA | `references/reference-section-completeness-and-final-pass.md` |
| Native PDF visual QA | `references/reference-pdf-export-visual-qa.md` |
