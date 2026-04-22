# Import Presentation

When to read: local `.ppt`, `.pptx`, or `.odp` input.

## Workflow

1. Confirm the input file is a supported presentation file.
2. Use `mcp__codex_apps__google_drive_import_presentation` with `upload_mode: "native_google_slides"` to create a native Google Slides deck:
   ```json
   {
     "source_file": "/absolute/path/to/deck.pptx",
     "title": "Deck title",
     "upload_mode": "native_google_slides"
   }
   ```
3. Read the imported deck and record presentation id, title, URL when available, slide count, and major slide titles.
4. Read Drive metadata for the imported file and confirm MIME type is `application/vnd.google-apps.presentation`.
5. Compare imported slide count to the source count when available.
6. Run thumbnail verification for the imported deck before follow-on edits.
7. Continue in this skill with the relevant references for summaries, content edits, visual cleanup, template migration, or structural repair.

## Rules

- Treat import as conversion into a new native Google Slides deck.
- Preserve source slide order and content by default.
- Do not use generic `_upload_file` for "upload as Google Slides"; it preserves `.pptx` instead of converting to native Slides.
- Do not promise perfect fidelity for Office-specific animations, transitions, SmartArt, or effects.
- If import introduces layout drift, fix the native Google Slides deck rather than editing the source file.

## Output

Return the imported deck title and link or id when available, note any obvious import drift, and name the follow-on workflow used if more work was requested.
