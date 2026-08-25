# Section Completeness And Final Pass

When to read: before final handoff, and before any large section replacement.

## Critical Invariant

Final output quality is not just structural completeness. Connector readback of what exists is not proof that nothing required is missing. The task is unfinished until the final readback reconciles the in-memory coverage map and, when applicable, the template/reference semantic inventory.

Do not use PDF or HTML checks as completeness checks. They verify rendered or structural presentation after semantic coverage passes. If a quality property cannot be verified, report it as unverified rather than complete.

## Final Readback Checklist

1. Re-read the document text and full structure from the connector once content has settled.
2. Confirm the document id, title, and `tabId` when applicable.
3. Reconcile every coverage-map obligation as present, unavailable-with-disclosure, or omitted-by-explicit-user-direction.
4. For template/reference work, compare every semantic-inventory component with the final structure and confirm the source remains unchanged.
5. Confirm requested sections and source content appear in the intended order and destination.
6. Confirm explicit output forms use the required native table/list/control/figure shape or carry an approved limitation.
7. Confirm requested facts, citations, and source links appear with exact native hyperlink ranges.
8. Confirm headings, body paragraphs, table cells, and lists have the intended content, style, and native list state.
9. Confirm supported chips and building-block-like regions preserve expected element types; visible text alone is not enough.
10. When dropdowns are in scope, verify provider identity, ordered options, selected value, location, and anchors.
11. Confirm figures/images are present and no placeholders, instruction text, duplicate sections, empty bullets, or scaffolding remain.
12. Only after semantic coverage passes, run one representation-and-density pass: remove duplicated rationale, consolidate genuinely comparable repeated records into a readable native table, and keep source links inline or in a compact source block when a separate source page adds no value. Never remove a unique obligation.
13. For layout-sensitive work, run PDF-export visual QA; state any unavailable rendered property plainly.

## Repair Scope

- Semantic reconciliation may reopen content scope to repair a prompt/content omission, source/template omission, or native-structure fidelity defect.
- Formatting repair may not reopen content scope unless it exposes a semantic omission.
- Re-read only repaired ranges unless the repair changes the containing structure; re-export only an affected layout-sensitive result.
- During evaluation, record repairs as prompt/content omission, source/template omission, native-structure fidelity, targeting, formatting, or pagination/layout.

## HTML Export Proxy

When the Google Drive export action is available, export the native Google Doc as `text/html` after connector readback. Treat this as a rendered-structure proxy, not as a screenshot.

Use the HTML export to verify:

1. heading tags and heading text are present in the expected order
2. body paragraphs use expected CSS such as font family, font size, line height, and text alignment
3. table rows, columns, cell text, fills, borders, padding, and widths appear in generated markup
4. content after a table is outside the closing `</table>` rather than inside the final row
5. expected header and stripe colors appear as CSS values
6. page-body hints such as `max-width` and table column widths are reasonable

The export response may wrap HTML inside a JSON string. Parse the wrapper before checking markup when needed. Prefer simple string or structured checks over fragile regexes when escaping is ambiguous.

Do not use HTML export to claim pixel-perfect layout, crop quality, exact page breaks, or final on-screen appearance. It is stronger than raw Docs structure for style sanity checks, but weaker than actual rendered visual inspection.

## PDF Export Visual QA

For layout-sensitive, table-heavy, figure-heavy, polished, or final-deliverable edits, run the workflow in `reference-pdf-export-visual-qa.md` when Google Drive PDF export and local PDF page rasterization are available.

PDF export plus page raster inspection is the preferred rendered-page check for native Google Docs in this environment. It verifies the exported document pages, not the live browser editing canvas. Do not use Drive thumbnails as a substitute for this workflow; thumbnails are only a low-resolution first-page smoke signal.

## Connector-Observable Quality Checks

1. Reject a document whose major sections are present only as undifferentiated body paragraphs. The heading skeleton must be visible in connector structure.
2. Reject any template-fill result that preserved section order but abandoned the template's actual answer containers or table structure.
3. Reject inserted content that picked up connector default font or mismatched typography when nearby style metadata exposes the correct local baseline.
4. Reject tables whose schema is too wide to be reasonable from the column count and text lengths, even if rendered fit cannot be inspected.
5. Reject header cells with partial hyperlinks, partial bolding, or mixed styling inside a single intended label when connector ranges expose the mismatch.
6. Reject any required figure that is absent from connector readback or only represented by placeholder text.
7. Reject a targeted edit that rebuilt the document, changed sampled out-of-scope structure, or modified a reusable source template.
8. Reject a result that replaced a dropdown or other native control with visible text or a placeholder glyph.
9. Reject an intended list represented only by typed bullet or number characters.
10. Prefer a connector-verified clean text-first document over optional visual work that cannot be inserted or verified safely.

## Design Quality Checks

Use these checks for presentation-oriented documents such as plans, briefs, reports, strategy docs, handoffs, and executive summaries. Keep them general; do not force a decorative layout when the task is a narrow edit or the source template has a stricter structure.

1. Do not treat section count, heading count, table count, or zero placeholders as proof of design quality.
2. When asked to make a document more visual, choose the right device for each idea: prose for explanation, bullets for short lists, tables for comparison, cards for key metrics or decisions, and figures only when they add meaning.
3. Avoid table monoculture. A long sequence of similarly styled tables can be less readable than concise prose plus a few high-value tables.
4. Avoid monotone styling unless the existing template requires it. Vary hierarchy through section headings, spacing, table width, table shape, restrained color accents, and callout/card treatment.
5. Prefer fewer, wider, more readable tables over many narrow grids. Two or three columns are usually safer for narrative business documents than four or more columns.
6. Keep cell copy short. If a table cell needs multiple sentences, split the idea into prose plus a smaller table or convert the table into a board/card pattern.
7. For multi-section deliverables, check that each section has a distinct role and rhythm. Repeating the same pattern in every section is a design smell.
8. If connector readback shows many tables, repeated column counts, or repeated first-row/header treatment, review scanability and remove structures that do not improve comprehension.
9. Use HTML export, when available, to inspect generated CSS and markup for repeated table patterns, over-wide grids, identical colors, and weak hierarchy.
10. If design quality cannot be verified directly, be conservative: simplify the structure, reduce grid density, and report which rendered properties remain unverified.
11. Treat a sparsely occupied trailing page containing only source links, continued bullets, or an orphaned note as an observed layout defect unless the prompt or source requires an appendix. Repair it by consolidating repeated text, integrating links, or tightening local spacing—not by omitting obligations or violating typography floors.

## Final Pass Order

1. Re-read the settled document once and reconcile the coverage map.
2. Compare template/reference semantic inventory and preservation anchors when applicable.
3. Verify required native forms, evidence links, figures, controls, and connector-visible formatting.
4. Repair semantic omissions or fidelity defects.
5. After coverage passes, perform the single representation-and-density pass from the checklist; do not create a later rewrite cycle.
6. Run design checks and optional HTML structure sanity checks.
7. Run PDF-export visual QA for layout-sensitive work; PDF verifies layout, not completeness.
8. Repair observed visual defects and re-read/re-export only the affected result.
9. In the final response, distinguish connector facts, semantic/native verification, HTML/PDF checks, and unverified properties.
10. If source notes were unavailable, describe the result as a skeleton rather than substantive notes.
