# Section Completeness And Final Pass

When to read: before final handoff, and before any large section replacement.

## Critical Invariant

Final output quality is not just structural completeness. In this blind environment, the task is unfinished until connector readback verifies the inserted content, target location, document structure, tab identity, links, tables, chips, and connector-visible style fields.

Do not claim rendered visual checks, page fit, crop quality, or visible alignment from connector readback or HTML export alone. If PDF export and page raster inspection are available, use `reference-pdf-export-visual-qa.md` for rendered-page verification. If a quality property cannot be verified, report it as unverified rather than complete.

## Final Readback Checklist

1. Re-read the document text and full structure from the connector.
2. Confirm the document id, title, and `tabId` when applicable.
3. Confirm every requested section is present in the intended order.
4. Confirm new headings use the intended named style and connector-visible text style fields.
5. Confirm body paragraphs, lists, and bullets have the intended text and list state.
6. Confirm links cover the exact intended labels, with no missing or extra neighboring characters.
7. Confirm new or edited tables have the intended row count, column count, cell text, table anchor, and connector-visible styling.
8. Confirm existing template containers were filled in place instead of bypassed with a parallel draft section.
9. Confirm supported smart chips and building-block-like regions preserve expected element types such as `dateElement`, `person`, and `richLink`; visible text alone is not enough.
10. Confirm inserted figures or images are present in connector readback if the task required them.
11. Confirm no placeholder text, unintended empty bullets, duplicate answer sections, or unintended leftover scaffolding remains.
12. For layout-sensitive, table-heavy, figure-heavy, polished, or final-deliverable edits, run PDF-export visual QA when available.
13. If connector metadata, HTML export, and PDF-export visual QA are insufficient to judge a rendered visual property, state the limitation plainly.

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
7. Prefer a connector-verified clean text-first document over optional visual work that cannot be inserted or verified safely.

## Design Quality Checks

Use these checks for presentation-oriented documents such as plans, briefs, reports, strategy docs, handoffs, and executive summaries. Keep them general; do not force a decorative layout when the task is a narrow edit or the source template has a stricter structure.

1. Do not treat section count, heading count, table count, or zero placeholders as proof of design quality.
2. When asked to make a document more visual, choose the right device for each idea: prose for explanation, bullets for short lists, tables for comparison, cards for key metrics or decisions, and figures only when they add meaning.
3. Avoid table monoculture. A long sequence of similarly styled tables can be less readable than concise prose plus a few high-value tables.
4. Avoid monotone styling unless the existing template requires it. Vary hierarchy through section headings, spacing, table width, table shape, restrained color accents, and callout/card treatment.
5. Prefer fewer, wider, more readable tables over many narrow grids. Two or three columns are usually safer for narrative business documents than four or more columns.
6. Keep cell copy short. If a table cell needs multiple sentences, split the idea into prose plus a smaller table or convert the table into a board/card pattern.
7. For multi-section deliverables, check that each section has a distinct role and rhythm. Repeating the same pattern in every section is a design smell.
8. If connector readback shows many tables, repeated column counts, or repeated first-row/header treatment, run an explicit density and monotony review before handoff.
9. Use HTML export, when available, to inspect generated CSS and markup for repeated table patterns, over-wide grids, identical colors, and weak hierarchy.
10. If design quality cannot be verified directly, be conservative: simplify the structure, reduce grid density, and report which rendered properties remain unverified.

## Final Pass Order

1. Re-read the target document and resolve `tabId` if needed.
2. Check section order and completeness.
3. Check headings, body text, lists, links, citations, tables, and figures through connector data.
4. Run the design quality checks when the document is presentation-oriented or the user asked for polish, visuals, charts, tables, or readability.
5. Export `text/html` when available and check generated markup/CSS for rendered-structure sanity.
6. Run PDF-export visual QA when the task is layout-sensitive, table-heavy, figure-heavy, polished, or final-deliverable and the export/raster toolchain is available.
7. Apply focused repair writes for any connector-observable, design-quality, HTML-export, or PDF visual mismatch.
8. Re-read the repaired ranges and re-export HTML/PDF if the repair changed layout-sensitive content.
9. In the final response, distinguish connector facts, HTML-export checks, PDF-export visual checks, and unverified rendered properties.
10. If the edit created a skeleton because source notes were unavailable, say that it created a notes skeleton rather than saying it added substantive meeting notes.
11. If smart-chip or building-block-like content was involved, state whether chip parity was preserved, approximated, or not applicable.
