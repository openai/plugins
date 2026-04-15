---
name: google-slides
description: Inspect, create, import, summarize, and update Google Slides presentations through connected Google Slides data. Use when the user wants to find a deck, read slide structure, summarize a presentation or specific slide, understand charts, graphs, or other slide visuals by combining slide text with thumbnail-based image understanding, create a new presentation, import a `.ppt`, `.pptx`, or `.odp`, or make general content edits in Google Slides. For visual polish on an existing deck, such as formatting cleanup, alignment fixes, overflow cleanup, or slide-by-slide deck cleanup, prefer `google-slides-visual-iteration`.
---

# Google Slides

## Overview

Use this skill as the default entrypoint for Google Slides work. Stay here for deck search, summaries, general content edits, imports, native deck copies, and new presentation creation. If the user primarily wants to make an existing deck look better by fixing formatting, overflow, spacing, alignment, or visual polish, prefer [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md).
Use this base skill when the request spans multiple Google Slides workflows or when no more focused Slides skill is a better fit.
Keep chart refresh and chart replacement workflows here when the job is to update a chart area from a connected source, such as Google Sheets, without broader deck redesign.
For slide-reading and summary tasks, combine structural deck reads with slide thumbnails when the slide contains charts, graphs, diagrams, screenshots, or other content that cannot be understood from text alone.
When the request is to replace screenshot placeholders or other static chart content with charts from an existing connected source, such as Google Sheets, stay in this reference unless the job is mainly visual cleanup. If the source is Google Sheets, read [sheets-chart-replacement](./sheets-chart-replacement.md).
When a write can change rendered text flow, geometry, colors, shapes, lines, connectors, charts, arrows, or accent bars on a live slide, read [visual-change-loop](./visual-change-loop.md) before the first write even if the request is not primarily visual cleanup.

## Specialized Skills

- For importing a local presentation file into native Google Slides first, prefer [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md).
- For visual cleanup of an existing deck, prefer [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md).
- For repairing broken repeated layout structure inside a deck, prefer [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md).
- For moving content onto a company or team template deck, prefer [google-slides-template-migration](../google-slides-template-migration/SKILL.md).

## Required Tooling

Confirm the runtime exposes the relevant Google Slides actions before editing:
- `search_presentations` when the user does not provide a target deck
- `get_presentation` or `get_presentation_text`
- `get_slide`
- `batch_update`
- `create_presentation` for new decks
- `create_from_template` when the user wants a translated, branded, or otherwise transformed copy of an existing Google Slides deck
- `import_presentation` when starting from a local `.ppt`, `.pptx`, or `.odp`
- `get_slide_thumbnail` when visual verification matters

## Workflow

1. Identify the target presentation.
- If the user names a deck but does not provide a URL, search for it first.
- If the user wants a new deck that preserves the structure or layout of an existing Google Slides deck, create the working copy with `create_from_template` before editing so the output stays native to Google Slides.
- If the user provides a local presentation file, tell the user you are importing it into native Google Slides first, then use [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md).

2. Read before writing.
- Use `get_presentation` or `get_presentation_text` to capture slide order, titles, and overall structure.
- When the request rewrites, translates, or updates multiple slides, follow [deck-scope-verification](./deck-scope-verification.md) before the first write so the full in-scope slide list is explicit.
- Use `get_slide` before any slide-level write so object IDs and layout context come from the live deck.
- For Q&A, evidence-finding, or "where in the deck is X?" requests, build an explicit candidate slide list first. Do not stop at the first keyword hit if the topic could appear across a section, in appendix evidence, or in both summary and detail slides.
- When answering a topic question such as churn, pipeline, or ARR, inspect every plausible slide in the relevant section before concluding that the answer lives on only one slide.
- For chart refresh or chart replacement work, follow [chart-refresh-workflows](./chart-refresh-workflows.md). Do not rely on `get_presentation_text` alone for chart workflows because chart-only slide elements may be omitted from text-only reads.
- If the task is to swap screenshot placeholders or other static chart content for charts from an existing connected source, keep the source artifacts grounded before the first write. If the source is Google Sheets, also read [sheets-chart-replacement](./sheets-chart-replacement.md) so chart IDs, placeholder geometry, and write scope stay grounded.
- When creating or updating a deck from multiple source presentations, identify the relevant source decks and slides before writing. Keep the source facts tied to the target slide plan so the final synthesis can be checked against the material that supported it.
- For slide summaries or inspection, do not rely on text extraction alone when a slide contains charts, graphs, screenshots, diagrams, or image-heavy content.
- Use `get_slide_thumbnail` alongside text/structure reads when visual evidence matters so the summary reflects both what the slide says and what the slide shows.
- If a candidate slide has little useful extracted text but may still contain relevant evidence in a chart, screenshot, or diagram, inspect its thumbnail before ruling it out.
- If the thumbnail response includes an `image_asset_pointer`, image content part, or other rendered image artifact, inspect that returned image directly as the slide image input.
- If the thumbnail response only exposes a thumbnail URL or `contentUrl`, curl the rendered image to a local PNG, for example `curl -L "$contentUrl" -o /tmp/slides-thumb-<slide-id>.png`, then inspect that local image before making or reporting visual judgments.
- Do not claim visual inspection from slide JSON, text extraction, geometry, or thumbnail metadata alone.
- Treat the slide page size as a hard boundary for every shape, text box, image, and color band you create.
- If the write can change anything visible on the slide, such as text wrapping, shape styling, arrow direction, accent bars, chart placement, or connector styling, follow [visual-change-loop](./visual-change-loop.md) before the first `batch_update`.

3. Apply default creation polish when making a new presentation.
- Do not ask the user to specify visual styling unless the request depends on a specific brand, template, or aesthetic.
- First create the base version of each slide with the right structure, content, and layout. Then do a second polish pass before moving on.
- Make the slides feel pretty and visually appealing by default, not merely correct.
- Make new decks look intentionally designed by default rather than leaving them as raw black text on white slides.
- Keep the styling lightweight but visibly designed: use a restrained color palette, clear title/body hierarchy, comfortable spacing, and simple visual accents that improve scanability.
- Do not default to a plain white background with only colored title text. Use background color, tinted sections, colored bands, or colored cards so most slides have visible color surfaces, not just colored text.
- Add graphics, icons, diagrams, or simple visual motifs when they help explain the point or make the slide feel designed, but do not add decorative elements that overwhelm the content.
- In the polish pass, improve color, spacing, hierarchy, alignment, and slide-level composition without changing the meaning of the content.
- Keep all content inside a safe content frame inset from the slide edges, including a visible bottom margin. If you use a full-bleed header band, footer band, or background block, size it exactly to the slide bounds rather than past them.
- Keep slide titles to one line at most. If a title would wrap, shorten it or split the content across slides instead of using a multi-line title.
- When content is naturally a list of points, render it as an actual bullet list instead of stacked prose lines or repeated paragraph blocks.
- When using bullets, put each bullet on its own line. Do not combine multiple bullets into one paragraph or line, and do not fake bullets with plain paragraphs when true list formatting is available.
- If body text, cards, or labels would run wide or tall, shorten them, reduce density, or split the content across slides instead of letting any element exceed the slide frame.
- Use color to create structure such as title emphasis, section separators, callout boxes, light background shapes, or full-slide background treatment, but do not overdecorate the deck.
- Preserve user control over substantive design choices. Apply a clean default look, but do not invent a heavy brand system or overly specific theme unless the user asks.

4. Route only when the job is narrower than general Slides work.
- Stay in this skill for deck summaries, slide-by-slide reviews, new presentation creation, chart refresh or chart replacement from a connected chart source such as Google Sheets, small content edits, and isolated formatting fixes on specific slides.
- Use [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md) when the source is a local presentation file.
- Use [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md) when the user asks to fix a slide visually, clean up formatting, make a deck look better, or correct spacing, overlap, alignment, cropping, density, overflow, or other layout cleanup where the slide image matters.
- Stay in this skill when the request spans narrow source-data edits, such as Google Sheets edits, plus chart replacement in Slides, and route to visual iteration only when post-replacement layout cleanup is the primary job.
- Use [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) when the repeated layout structure is broken.
- Use [google-slides-template-migration](../google-slides-template-migration/SKILL.md) when content should move onto a company or team template deck.

5. Keep writes grounded.
- Restate the target slide numbers, titles, or object IDs before making changes.
- Prefer small `batch_update` requests over large speculative batches.
- Send `batch_update` requests as structured request objects in the expected tool shape, not as JSON strings or stringified arrays.
- For chart refresh or chart replacement requests, inspect the live slide structure first and decide whether the slide contains a linked chart, a shape placeholder, or static chart content.
- If the slide already contains a linked chart and the user wants the existing chart updated in place, prefer a raw chart refresh request in `batch_update`, then verify with a thumbnail that the chart itself updated.
- If the slide contains a shape placeholder or static chart content and the user wants the chart graphic updated, treat that as a chart replacement workflow rather than a failed refresh.
- When a source workbook already contains matching charts, reuse those existing charts before creating temporary or new charts. Only create a new source chart when no suitable existing chart is available.
- For shape placeholders, replace the placeholder object with the chart graphic directly and preserve the intended chart-area footprint.
- For static chart content, preserve the existing chart footprint as closely as possible and replace the old graphic rather than layering a second chart on top.
- If the user does not require the result to stay linked to the source workbook, prefer a non-linked chart insertion path when it reduces extra link behavior without changing the visible result.
- Remove chart-area instructional text that becomes obsolete after replacement, such as text containing `PLACEHOLDER`, `INSERT`, or explicit directions to replace the static content, unless the user explicitly asks to keep it.
- After chart replacement, verify both that the chart rendered in the intended area and that obsolete placeholder or instructional text no longer remains on the slide.
- For deck-wide or multi-slide content edits such as translation, terminology normalization, or repeated copy updates, work in explicit slide spans and re-read the edited span before advancing.
- When the user asks to review, show, summarize, or confirm edited content, re-read the affected slides after the write and base the response on the post-edit deck state rather than the intended diff or a successful `batch_update` response.
- In multi-slide mode, confirm the last slide in the just-edited span actually changed before starting the next span. Do not assume coverage from object ID numbering or from a successful write response alone.
- Before calling a multi-slide edit done, reconcile the final deck against the original slide checklist so no slide in scope was skipped.
- When the user asked for a live Google Slides deck, keep the workflow native. Do not export to a downloadable file or ask for a local re-upload when `create_from_template`, `create_presentation`, or `import_presentation` can keep the work inside Google Slides.
- If the task depends on how the slide looks, fetch a thumbnail before editing and verify again after the write.
- If the task is to summarize, interpret, or sanity-check a visual slide, fetch a thumbnail and use it as evidence for charts, graphs, screenshots, diagrams, and other non-textual content rather than summarizing only the extracted text.
- When fixing slide formatting, use a tight loop: take a thumbnail, identify visible spacing/alignment/cropping/regression issues, send a focused `batch_update`, then take another thumbnail to verify the result.
- Run at least 3 verified formatting passes when layout or styling changed, and continue to a fourth only if the slide still has meaningful issues. Switch to [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md) if the job turns into slide-by-slide formatting across a larger set of slides.
- After creating a new slide or applying layout-heavy changes, immediately verify that no text, shape, image, or color band extends beyond the slide boundary. If the editor would require horizontal or vertical scrolling to see the whole slide, or if the lowest text sits in the bottom safety margin, treat that as a failure and fix it before moving on.
- When supplying `objectId` values in `batch_update`, use valid Google Slides IDs that are 5-50 characters long and start with an alphanumeric character or `_`. Prefer descriptive IDs like `slide02`, `slide02_title`, or `slide02_body`; do not use very short IDs like `s2` or `i0`.
- If you need to create a slide and edit its placeholders in the same `batch_update`, create the slide with valid placeholder ID mappings first, then reference those placeholder IDs in later requests in the same batch.
- Any write that can change visible layout or styling must follow [visual-change-loop](./visual-change-loop.md). Do not stop at a successful API response without thumbnail verification.

## Write Safety

- Preserve slide order, titles, body text, charts, notes, and supporting evidence unless the user asks for a change.
- Use live object IDs from the current deck state. Never guess IDs or request shapes.
- Before deleting slides, rewriting multiple slides, or changing the layout pattern across a section, state exactly which slides will change and what kind of change you are about to make.
- Do not promise pixel-perfect fidelity when importing Office formats into Google Slides.
- When creating a new deck, default to readable structure plus visible color treatment, not a bare text dump.
- Never leave text boxes, shapes, or header bands hanging outside the slide frame unless they are intentional full-bleed elements sized exactly to the slide edges.

## Output

- Reference slide numbers and titles when summarizing or planning edits.
- For slide summaries that involve charts, graphs, or other visuals, distinguish clearly between what comes from extracted text and what comes from thumbnail-based visual understanding.
- For Q&A or evidence-location requests, say which slide range or candidate slides were inspected before giving the answer. Do not imply exhaustive coverage if you only checked one likely slide.
- For chart update requests, say explicitly whether the chart itself was refreshed, whether a placeholder or static chart content block was replaced from an existing source chart such as a Google Sheets chart, whether a new source chart had to be created first, or whether only surrounding text changed.
- Say whether any placeholder or instructional chart text remained after the update.
- Distinguish clearly between a proposed plan and changes that were actually applied.
- Say which presentation and slides were read or changed.
- For multi-source synthesis, name the source presentations and slides used plus the final presentation and slides that contain the synthesized material, with enough concise evidence for the user to verify the result.
- When reporting edited content, use the post-edit readback if the task asked to review, show, summarize, or confirm the result.
- Call out any remaining issues that need a narrower workflow or human design judgment.

## Example Requests

- "Find the Q2 board deck and summarize the storyline slide by slide."
- "Read slide 8 and summarize both the chart and the surrounding text."
- "Which slides in this deck discuss churn, and what does each one say?"
- "Refresh the linked chart on slide 6 from its source workbook and verify the updated visual."
- "Replace the ARR, churn, and pipeline static chart content with charts from the metrics spreadsheet without leaving placeholder text behind."
- "Open this Google Sheet and Google Slides deck, make a few targeted chart-data edits, and replace the chart placeholder screenshots with the existing Sheets charts."
- "Create a new Google Slides presentation from this outline."
- "Translate this deck into Japanese and save it as a new Google Slides deck without leaving Slides."
- "Import this PPTX into Google Slides and then clean up the layout."
- "Update slide 6 so the title and chart description match the latest numbers."

## Light Fallback

If the presentation is missing or the Google Slides connector does not return deck data, say that Google Slides access may be unavailable, the wrong deck may be in scope, or the file may need to be imported first.

## References

- [deck-scope-verification](./deck-scope-verification.md)
- [chart-refresh-workflows](./chart-refresh-workflows.md)
- [sheets-chart-replacement](./sheets-chart-replacement.md)
- [visual-change-loop](./visual-change-loop.md)
