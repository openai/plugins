---
name: google-drive
description: Use connected Google Drive as the single entrypoint for Drive, Docs, Sheets, and Slides work. Use when the user wants to find, fetch, organize, share, export, copy, or delete Drive files, or summarize and edit Google Docs, Google Sheets, and Google Slides through one unified Google Drive plugin.
---

# Google Drive

Use this as the top-level router for Google file work inside the unified Google Drive plugin. Do not route the user toward separate Google Docs, Google Sheets, or Google Slides plugins.

Start with Google Drive for file discovery and file lifecycle tasks, then route to narrower sibling skills only when the task becomes specific to Docs, Sheets, or Slides.

## Workflow

1. Ground the target file first.
- If the user did not provide an exact file URL or ID, use Google Drive search, recent files, folder listing, or metadata reads to identify the right file.
- If the request starts as "find X and then update it," do the Drive discovery step first instead of guessing the target.

2. Stay in the base Google Drive workflow for Drive-native tasks.
- Use the base workflow for search, fetch, recent files, folders, sharing, copying, deleting, exporting, revision history, file moves, and other file-lifecycle work that is not primarily about editing Docs, Sheets, or Slides content.
- For version-history requests, including "previous version," "revision history," "what changed since the last version," or "compare to the prior revision," ground the file, fetch the current content, use `list_file_revisions`, fetch the immediately previous revision or the user-named revision with `fetch_file_revision`, then compare the fetched revision against the current content. Do not say previous versions are unsupported until you have checked whether revision tools are available for the target file.
- For file move requests, ground the source file and target folder, read the file metadata including its current parents, then use `update_file` with `addParents` for the target folder and `removeParents` for only the verified source parent or parents that should no longer contain it. Preserve unrelated parents, and verify the move by reading metadata or listing the target folder before the final response.

3. Route to the narrowest sibling skill that matches the file type and job.
- Drive, Docs, Sheets, or Slides comment creation, comment replies, comment resolution, or review-by-comments: use [google-drive-comments](../google-drive-comments/SKILL.md).
- Google Docs content summary, revision planning, prose rewriting, or section edits: use [google-docs](../google-docs/SKILL.md).
- Google Sheets creation, range inspection, table cleanup, data restructuring, formula design or repair, chart creation or repair, or batch updates: use [google-sheets](../google-sheets/SKILL.md).
- Google Slides deck summary, content edits, new deck creation, import, visual cleanup, structural repair, or template migration: use [google-slides](../google-slides/SKILL.md).

## Routing Rules

- If the request is ambiguous between Drive and a file-type surface, use the artifact itself as the tie-breaker:
  - Doc -> Docs skill
  - Sheet -> Sheets skill
  - Deck -> Slides skill
- If the user wants to find a file and then edit it, do both in one flow: Drive for discovery, then the file-type skill for the edit.
- If the user wants a Google Workspace outcome but has not named a file type yet, start with Drive discovery instead of asking them to choose among separate Google plugins.

## Write Safety

- Preserve the user's existing file organization, sharing state, and target artifact unless the request clearly asks to change them.
- When a task can be satisfied by a file-level Drive operation alone, do not load heavier Docs, Sheets, or Slides skills.
- For write-heavy Sheets or Slides work, read the specialized skill before the first large update so request shapes stay grounded.

## Related Skills

- Comments: [google-drive-comments](../google-drive-comments/SKILL.md)
- Docs: [google-docs](../google-docs/SKILL.md)
- Sheets: [google-sheets](../google-sheets/SKILL.md)
- Slides: [google-slides](../google-slides/SKILL.md)
