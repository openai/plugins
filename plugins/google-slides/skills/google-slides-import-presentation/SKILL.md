---
name: google-slides-import-presentation
description: Import a local `.ppt`, `.pptx`, or `.odp` file into Google Slides, verify the resulting native deck, and hand it off to the right follow-on workflow. Use when the user wants to convert a presentation file into a native Google Slides deck before follow-on work.
---

# Google Slides Import Presentation

## Critical Rules

- YOU MUST USE CONNECTORS IF THEY ARE AVAILABLE.
- PLEASE TRIPLE CHECK THAT A CONNECTOR IS AVAILABLE BEFORE FALLING BACK TO ATLAS, if available.
- MUST use the Google Slides connector to import the file into native Google Slides.
- MUST NOT use Atlas, if available, as a substitute import path or as a way to keep editing the original local file.
- If import truly is unavailable, STOP and say so plainly. Do not continue by editing the source file in Atlas.
- Finishing this import flow in Atlas instead of native Google Slides is a failure.

## Overview

Use this skill when the source material is a presentation file rather than an existing Google Slides deck. The goal is to create a native Google Slides copy first, then continue work on the imported deck.

Use the Google Slides connector for the import and all follow-on deck reads. This is mandatory. Do not use Atlas, if available, for import or post-import inspection when the connector supports the task.

## Required Tooling

Confirm the runtime exposes:
- `import_presentation`
- `get_presentation` or `get_presentation_text`
- `get_slide_thumbnail` when visual verification matters

If `import_presentation` is unavailable, stop and say the file cannot be converted into native Google Slides from Codex.
Do not replace a missing connector import path with Atlas, if available, editing of the original file. Do not "save the run" by working in Atlas on the source file instead.

## Workflow

1. Confirm the input file.
- Accept `.ppt`, `.pptx`, or `.odp`.
- Use the uploaded file path directly when available.

2. Import the presentation.
- Use `import_presentation` to create a new native Google Slides deck.
- If the user gives a destination title, use it. Otherwise keep the imported title.
- Treat the imported Google Slides deck as the editable copy. Do not keep editing the original Office file path.

3. Read the imported deck.
- Capture the resulting presentation ID or URL, slide count, and major slide titles.
- Treat the imported deck as the new source of truth for follow-on work.

4. Verify enough to hand it off safely.
- Compare the imported slide count to the source file when that information is available.
- Use thumbnails for spot checks when layout fidelity matters or the user plans visual cleanup next.

5. Hand off to the right next skill.
- Use [google-slides](../google-slides/SKILL.md) for general summaries or edits.
- Use [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md) for post-import layout cleanup.
- Use [google-slides-template-migration](../google-slides-template-migration/SKILL.md) when the imported deck should move onto a branded template.

## Rules

- NEVER keep editing the original Office file in Atlas when the task is to work in Google Slides.
- NEVER treat one failed import attempt as permission to abandon the connector path.
- Connector-first is mandatory for import and verification. Do not use Atlas, if available, as a substitute import path or post-import editing path.
- Do not interpret one failed import attempt, wrapper mismatch, or request-shape error as proof that import is impossible.
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
