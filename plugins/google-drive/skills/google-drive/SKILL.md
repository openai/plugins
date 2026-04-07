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
- Use the base workflow for search, fetch, recent files, folders, sharing, copying, deleting, exporting, and other file-lifecycle work that is not primarily about editing Docs, Sheets, or Slides content.

3. Route to the narrowest sibling skill that matches the file type and job.
- Drive, Docs, Sheets, or Slides comment creation, comment replies, comment resolution, or review-by-comments: use [google-drive-comments](../google-drive-comments/SKILL.md).
- Google Docs content summary, revision planning, prose rewriting, or section edits: use [google-docs](../google-docs/SKILL.md).
- Google Sheets range inspection, table cleanup, data restructuring, or batch updates: use [google-sheets](../google-sheets/SKILL.md).
- Google Sheets formula design or repair: use [google-sheets-formula-builder](../google-sheets-formula-builder/SKILL.md).
- Google Sheets chart creation or repair: use [google-sheets-chart-builder](../google-sheets-chart-builder/SKILL.md).
- Google Slides deck summary, content edits, new deck creation, or import handoff: use [google-slides](../google-slides/SKILL.md).
- Google Slides visual cleanup: use [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md).
- Google Slides PPT/PPTX/ODP import: use [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md).
- Google Slides repeated-layout repair: use [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md).
- Google Slides template migration: use [google-slides-template-migration](../google-slides-template-migration/SKILL.md).

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
- Sheets formulas: [google-sheets-formula-builder](../google-sheets-formula-builder/SKILL.md)
- Sheets charts: [google-sheets-chart-builder](../google-sheets-chart-builder/SKILL.md)
- Slides: [google-slides](../google-slides/SKILL.md)
- Slides visual iteration: [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md)
- Slides import: [google-slides-import-presentation](../google-slides-import-presentation/SKILL.md)
- Slides template surgery: [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md)
- Slides template migration: [google-slides-template-migration](../google-slides-template-migration/SKILL.md)
