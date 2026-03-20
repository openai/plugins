---
name: google-slides
description: Inspect, create, import, summarize, and update Google Slides presentations through connected Google Slides data. Use when the user wants to find a deck, read slide structure, summarize a presentation or specific slide, understand charts, graphs, or other slide visuals by combining slide text with thumbnail-based image understanding, create a new presentation, import a `.ppt`, `.pptx`, or `.odp`, or make general content edits in Google Slides. For deck reading and summarization, stay on the Google Slides read-tool path rather than detouring into generic code execution or export fallbacks. For visual polish on an existing deck, such as formatting cleanup, alignment fixes, overflow cleanup, or slide-by-slide deck cleanup, prefer `google-slides-visual-iteration`.
---

# Google Slides

## Overview

Use this skill as the default entrypoint for Google Slides work. Stay here for deck search, summaries, general content edits, imports, and new presentation creation. If the user primarily wants to make an existing deck look better by fixing formatting, overflow, spacing, alignment, or visual polish, prefer [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md).
Use this base skill when the request spans multiple Google Slides workflows or when no more focused Google Slides skill is a better fit.
For slide-reading and summary tasks, combine structural deck reads with slide thumbnails when the slide contains charts, graphs, diagrams, screenshots, or other content that cannot be understood from text alone.

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
- `import_presentation` when starting from a local `.ppt`, `.pptx`, or `.odp`
- `get_slide_thumbnail` when visual verification matters

## Workflow

1. Identify the target presentation.
- If the user names a deck but does not provide a URL, search for it first.
- If the user provides a local presentation file, tell the user you are importing it into native Google Slides first, then use [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md).

2. Read before writing.
- Use `get_presentation` or `get_presentation_text` to capture slide order, titles, and overall structure.
- For deck reading, slide finding, and summarization, use Google Slides read tools directly rather than generic code execution such as `js_repl`.
- Use `get_presentation_text` to find candidate slides, then inspect the relevant slides with `get_slide` and `get_slide_thumbnail` when visual evidence matters.
- Use `get_slide` before any slide-level write so object IDs and layout context come from the live deck.
- For slide summaries or inspection, do not rely on text extraction alone when a slide contains charts, graphs, screenshots, diagrams, or image-heavy content.
- Use `get_slide_thumbnail` alongside text/structure reads when visual evidence matters so the summary reflects both what the slide says and what the slide shows.
- If the thumbnail response includes inline image content, base64 image data, or an image-bearing data wrapper, ingest that directly as slide image input. The response may also include `contentUrl` metadata, but if inline image data is present, inspect that directly instead of downloading the URL or relying only on metadata.
- Treat the slide page size as a hard boundary for every shape, text box, image, and color band you create.

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
- Stay in this skill for deck summaries, slide-by-slide reviews, new presentation creation, small content edits, and isolated formatting fixes on specific slides.
- Use [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md) when the source is a local presentation file.
- Use [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md) when the user asks to fix a slide visually, clean up formatting, make a deck look better, or correct spacing, overlap, alignment, cropping, density, overflow, or other layout cleanup where the slide image matters.
- Use [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) when the repeated layout structure is broken.
- Use [google-slides-template-migration](../google-slides-template-migration/SKILL.md) when content should move onto a company or team template deck.

5. Keep writes grounded.
- Restate the target slide numbers, titles, or object IDs before making changes.
- Prefer small `batch_update` requests over large speculative batches.
- Send `batch_update` requests as structured request objects in the expected tool shape, not as JSON strings or stringified arrays.
- Do not use `export` as the default path for finding content, summarizing slides, or understanding visuals. Use it only when the user explicitly asks for an exported file or a downstream step truly requires exported bytes.
- If the task depends on how the slide looks, fetch a thumbnail before editing and verify again after the write.
- If the task is to summarize, interpret, or sanity-check a visual slide, fetch a thumbnail and use it as evidence for charts, graphs, screenshots, diagrams, and other non-textual content rather than summarizing only the extracted text.
- When fixing slide formatting, use a tight loop: take a thumbnail, identify visible spacing/alignment/cropping/regression issues, send a focused `batch_update`, then take another thumbnail to verify the result.
- Run 2-4 verified formatting passes when needed. Stop earlier once the slide is clearly clean, and switch to [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md) if the job turns into slide-by-slide formatting across a larger set of slides.
- After creating a new slide or applying layout-heavy changes, immediately verify that no text, shape, image, or color band extends beyond the slide boundary. If the editor would require horizontal or vertical scrolling to see the whole slide, or if the lowest text sits in the bottom safety margin, treat that as a failure and fix it before moving on.
- When supplying `objectId` values in `batch_update`, use valid Google Slides IDs that are 5-50 characters long and start with an alphanumeric character or `_`. Prefer descriptive IDs like `slide02`, `slide02_title`, or `slide02_body`; do not use very short IDs like `s2` or `i0`.
- If you need to create a slide and edit its placeholders in the same `batch_update`, create the slide with valid placeholder ID mappings first, then reference those placeholder IDs in later requests in the same batch.

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
- Distinguish clearly between a proposed plan and changes that were actually applied.
- Say which presentation and slides were read or changed.
- Call out any remaining issues that need a narrower workflow or human design judgment.

## Example Requests

- "Find the Q2 board deck and summarize the storyline slide by slide."
- "Read slide 8 and summarize both the chart and the surrounding text."
- "Create a new Google Slides presentation from this outline."
- "Import this PPTX into Google Slides and then clean up the layout."
- "Update slide 6 so the title and chart description match the latest numbers."

## Light Fallback

If the presentation is missing or the Google Slides connector does not return deck data, say that Google Slides access may be unavailable, the wrong deck may be in scope, or the file may need to be imported first.
