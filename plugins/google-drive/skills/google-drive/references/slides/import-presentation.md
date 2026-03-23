# Google Slides Import Presentation

## Overview

Use this reference when the source material is a presentation file rather than an existing Google Slides deck. The goal is to create a native Google Slides copy first, then continue work on the imported deck.

## Required Tooling

Confirm the runtime exposes:
- `import_presentation`
- `get_presentation` or `get_presentation_text`
- `get_slide_thumbnail` when visual verification matters

If `import_presentation` is unavailable, stop and say the file cannot be converted into native Google Slides from Codex.

## Workflow

1. Confirm the input file.
- Accept `.ppt`, `.pptx`, or `.odp`.
- Use the uploaded file path directly when available.

2. Import the presentation.
- Use `import_presentation` to create a new native Google Slides deck.
- If the user gives a destination title, use it. Otherwise keep the imported title.

3. Read the imported deck.
- Capture the resulting presentation ID or URL, slide count, and major slide titles.
- Treat the imported deck as the new source of truth for follow-on work.

4. Verify enough to hand it off safely.
- Compare the imported slide count to the source file when that information is available.
- Use thumbnails for spot checks when layout fidelity matters or the user plans formatting cleanup next.

5. Hand off to the right next reference.
- Use [google-slides](./workflows.md) for general summaries or edits.
- Use [google-slides-visual-iteration](./visual-iteration.md) for post-import slide formatting cleanup.
- Use [google-slides-template-migration](./template-migration.md) when the imported deck should move onto a branded template.

## Rules

- Treat import as conversion into a new native Google Slides deck, not in-place editing of the original file.
- Preserve source slide order and content by default.
- Do not promise perfect fidelity for animations, transitions, SmartArt, or other Office-specific features.
- If import introduces layout drift, fix it in the native Google Slides deck rather than editing the source file.
- When the user says "edit this PPTX," import first and then operate on the resulting Google Slides deck.

## Output

- Return the resulting deck title and link or ID when the runtime exposes it.
- Call out any obvious import drift or unsupported formatting that needs follow-up.
- If no further edit was requested, stop after confirming that the native deck is ready.

## Example Requests

- "Import this PPTX into Google Slides so I can edit it."
- "Convert this deck to native Google Slides and then summarize the first five slides."
- "Bring this ODP into Google Slides and clean up any layout drift."

## Light Fallback

If the file is missing, unreadable, or the runtime cannot import it, say that presentation import may be unavailable or the provided file may be invalid, then ask for a valid local file or a connected Google Slides deck instead.
