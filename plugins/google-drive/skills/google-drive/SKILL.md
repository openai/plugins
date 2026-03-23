---
name: google-drive
description: Use connected Google Drive as the single entrypoint for Drive, Docs, Sheets, and Slides work. Use when the user wants to find, fetch, organize, share, export, copy, or delete Drive files, or summarize and edit Google Docs, Google Sheets, and Google Slides through one unified Google Drive plugin.
---

# Google Drive

Use this as the only top-level skill for Google file work. Do not route the user toward separate Google Docs, Google Sheets, or Google Slides plugins.

Start with Google Drive for file discovery and file lifecycle tasks, then read narrower references only when the task becomes specific to Docs, Sheets, or Slides.

## Workflow

1. Ground the target file first.
- If the user did not provide an exact file URL or ID, use Google Drive search, recent files, folder listing, or metadata reads to identify the right file.
- If the request starts as "find X and then update it," do the Drive discovery step first instead of guessing the target.

2. Stay in the base Google Drive workflow for Drive-native tasks.
- Use the base workflow for search, fetch, recent files, folders, sharing, copying, deleting, exporting, and other file-lifecycle work that is not primarily about editing Docs, Sheets, or Slides content.

3. Route to the narrowest reference that matches the file type and job.
- Google Docs content summary, revision planning, prose rewriting, or section edits: read [docs/workflows.md](./references/docs/workflows.md).
- Google Sheets range inspection, table cleanup, data restructuring, or batch updates: read [sheets/workflows.md](./references/sheets/workflows.md).
- Google Sheets formula design or repair: read [sheets/formulas.md](./references/sheets/formulas.md).
- Google Sheets chart creation or repair: read [sheets/charts.md](./references/sheets/charts.md).
- Google Slides deck summary, content edits, new deck creation, or import handoff: read [slides/workflows.md](./references/slides/workflows.md).
- Google Slides visual cleanup: read [slides/visual-iteration.md](./references/slides/visual-iteration.md).
- Google Slides PPT/PPTX/ODP import: read [slides/import-presentation.md](./references/slides/import-presentation.md).
- Google Slides repeated-layout repair: read [slides/template-surgery.md](./references/slides/template-surgery.md).
- Google Slides template migration: read [slides/template-migration.md](./references/slides/template-migration.md).

## Routing Rules

- If the request is ambiguous between Drive and a file-type surface, use the artifact itself as the tie-breaker:
  - Doc -> Docs reference
  - Sheet -> Sheets reference
  - Deck -> Slides reference
- If the user wants to find a file and then edit it, do both in one flow: Drive for discovery, then the file-type reference for the edit.
- If the user wants a Google Workspace outcome but has not named a file type yet, start with Drive discovery instead of asking them to choose among separate Google plugins.

## Write Safety

- Preserve the user's existing file organization, sharing state, and target artifact unless the request clearly asks to change them.
- When a task can be satisfied by a file-level Drive operation alone, do not load heavier Docs, Sheets, or Slides references.
- For write-heavy Sheets or Slides work, read the specialized reference before the first large update so request shapes stay grounded.

## References

- Docs workflows: [docs/workflows.md](./references/docs/workflows.md)
- Sheets workflows: [sheets/workflows.md](./references/sheets/workflows.md)
- Sheets formulas: [sheets/formulas.md](./references/sheets/formulas.md)
- Sheets charts: [sheets/charts.md](./references/sheets/charts.md)
- Slides workflows: [slides/workflows.md](./references/slides/workflows.md)
- Slides visual iteration: [slides/visual-iteration.md](./references/slides/visual-iteration.md)
- Slides import: [slides/import-presentation.md](./references/slides/import-presentation.md)
- Slides template surgery: [slides/template-surgery.md](./references/slides/template-surgery.md)
- Slides template migration: [slides/template-migration.md](./references/slides/template-migration.md)
