---
name: google-slides
description: Inspect, create, import, summarize, and update Google Slides presentations through connected Google Slides data. Use when the user wants to find a deck, read slide structure, summarize a presentation, create a new presentation, import a `.ppt`, `.pptx`, or `.odp`, update slide text or layout, or route a Slides task to a more specific workflow.
---

# Google Slides

## Overview

Use this skill as the default entrypoint for Google Slides work. Stay here for deck search, summaries, light content edits, and new presentation creation. Route to a narrower sibling skill only when the task is specifically import, visual cleanup, structural repair, or template migration.

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
- If the user provides a local presentation file, import it before trying to edit slides.

2. Read before writing.
- Use `get_presentation` or `get_presentation_text` to capture slide order, titles, and overall structure.
- Use `get_slide` before any slide-level write so object IDs and layout context come from the live deck.

3. Route only when the job is narrower than general Slides work.
- Use [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md) when the source is a local presentation file.
- Use [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md) for spacing, overlap, alignment, and visual polish.
- Use [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) when the repeated layout structure is broken.
- Use [google-slides-template-migration](../google-slides-template-migration/SKILL.md) when content should move onto a company or team template deck.

4. Keep writes grounded.
- Restate the target slide numbers, titles, or object IDs before making changes.
- Prefer small `batch_update` requests over large speculative batches.
- Use thumbnails for verification whenever the task is visual, not just textual.

## Write Safety

- Preserve slide order, titles, body text, charts, notes, and supporting evidence unless the user asks for a change.
- Use live object IDs from the current deck state. Never guess IDs or request shapes.
- Treat deck-wide rewrites, slide deletions, and broad template changes as explicit actions that should be clearly scoped.
- If the user asks to edit a `.pptx`, convert it into native Google Slides first instead of promising in-place Office edits.
- Do not promise pixel-perfect fidelity when importing Office formats into Google Slides.

## Output

- Reference slide numbers and titles when summarizing or planning edits.
- Distinguish clearly between a proposed plan and changes that were actually applied.
- Say which presentation and slides were read or changed.
- Call out any remaining issues that need a narrower workflow or human design judgment.

## Example Requests

- "Find the Q2 board deck and summarize the storyline slide by slide."
- "Create a new Google Slides presentation from this outline."
- "Import this PPTX into Google Slides and then clean up the layout."
- "Update slide 6 so the title and chart description match the latest numbers."

## Light Fallback

If the presentation is missing or the Google Slides connector does not return deck data, say that Google Slides access may be unavailable, the wrong deck may be in scope, or the file may need to be imported first.
