# Import Presentation

When to read: local `.ppt`, `.pptx`, or `.odp` input.

## Workflow

1. Confirm the input file is a supported presentation file.
2. Before import, confirm the Google Drive plugin exposes `mcp__codex_apps__google_drive_import_presentation`. If the Google Drive plugin is not installed or unavailable, use the plugin-install/user-elicitation flow to ask the user to install `google-drive@openai-curated`. If the plugin is available but the import action is missing, ask the user to reinstall or refresh the Google Drive plugin.
3. Use `mcp__codex_apps__google_drive_import_presentation` with `upload_mode: "native_google_slides"` to create a native Google Slides deck:
   ```json
   {
     "source_file": "/absolute/path/to/deck.pptx",
     "title": "Deck title",
     "upload_mode": "native_google_slides"
   }
   ```
4. Read the imported deck and record presentation id, title, URL when available, slide count, and major slide titles.
5. Read Drive metadata for the imported file and confirm MIME type is `application/vnd.google-apps.presentation`.
6. Confirm the Google Slides URL or presentation id you will return was observed in the completed import response, connector readback, or Drive metadata readback. Do not synthesize or predict a Google Slides URL, and do not return any URL before readback verification succeeds.
7. Compare imported slide count to the source count when available.
8. Run thumbnail verification for the imported deck before follow-on edits.
9. Continue in this skill with the relevant references for summaries, content edits, visual cleanup, template migration, or structural repair.

## Rules

- Treat import as conversion into a new native Google Slides deck.
- Preserve source slide order and content by default.
- Do not use generic `_upload_file` for "upload as Google Slides"; it preserves `.pptx` instead of converting to native Slides.
- Do not substitute Computer Use, Browser Use, blank-Google-Slides creation followed by Google Slides write APIs, or another direct-to-Slides construction path for net-new Google Slides unless the user explicitly asks for that alternate workflow. If they do, mention first that output quality is expected to be best with this local `.pptx` import path.
- Do not promise perfect fidelity for Office-specific animations, transitions, SmartArt, or effects.
- If import introduces layout drift, fix the native Google Slides deck rather than editing the source file.

## Preservation Mode

Only use a non-native upload when the user explicitly asks to preserve the PowerPoint file, keep the source `.pptx`, or avoid conversion. For that explicit preservation request, use `_import_presentation` with `upload_mode: "keep_source_file_type"` and make clear that the result is a Drive-hosted PowerPoint file, not a native Google Slides deck.

## Output

Return the imported deck title and link or id only after import completion and connector readback verification. Use only a link or id observed in the completed import response, connector readback, or Drive metadata readback. If readback fails, do not present the URL as ready. Note any obvious import drift, and name the follow-on workflow used if more work was requested.
