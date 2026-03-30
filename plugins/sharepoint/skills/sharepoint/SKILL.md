---
name: sharepoint
description: Inspect Microsoft SharePoint context and prepare safe changes. Use when the user wants site, page, or file review, ownership and status extraction, or change planning before editing content, navigation, or information architecture.
---

# SharePoint

## Overview

Use this skill to turn SharePoint sites, pages, files, and document-library context into clear summaries and low-risk edit plans. Read the relevant content first, anchor recommendations in the exact site or file, and separate review from write actions.

## Preferred Deliverables

- Site or page briefs that capture purpose, owners, current status, and open issues.
- File summaries that highlight the latest content, gaps, and action items.
- Edit plans that specify what should change, where it should change, and why.

## Workflow Skills

| Workflow | Skill |
| --- | --- |
| Word document edits that must preserve `.docx` structure and styling | [../sharepoint-word-docs/SKILL.md](../sharepoint-word-docs/SKILL.md) |
| Spreadsheet edits that must preserve workbook structure, formulas, and formatting | [../sharepoint-spreadsheets/SKILL.md](../sharepoint-spreadsheets/SKILL.md) |
| Formula design, repair, and rollout in a SharePoint-hosted workbook | [../sharepoint-spreadsheet-formula-builder/SKILL.md](../sharepoint-spreadsheet-formula-builder/SKILL.md) |
| PowerPoint deck edits that must preserve slide style and template fidelity | [../sharepoint-powerpoint/SKILL.md](../sharepoint-powerpoint/SKILL.md) |
| Cross-document synthesis and maintaining shared strategy or roadmap docs | [../sharepoint-shared-doc-maintenance/SKILL.md](../sharepoint-shared-doc-maintenance/SKILL.md) |

## Workflow

1. Read the relevant site, page, file, or library before proposing changes. Capture the current title, location, owners, linked documents, and the content that matters.
2. When the user is exploring, summarize the current information architecture or document state before suggesting edits.
3. Ground every recommendation in the exact SharePoint destination, such as the site name, page name, library, or file path.
4. If the request targets an Office document, determine whether the task is content analysis only or an actual file edit before choosing the workflow.
5. Route specialized Office workflows to the appropriate SharePoint skill:
   - `.docx` edits -> [../sharepoint-word-docs/SKILL.md](../sharepoint-word-docs/SKILL.md)
   - `.xlsx` edits -> [../sharepoint-spreadsheets/SKILL.md](../sharepoint-spreadsheets/SKILL.md)
   - formula-heavy `.xlsx` work -> [../sharepoint-spreadsheet-formula-builder/SKILL.md](../sharepoint-spreadsheet-formula-builder/SKILL.md)
   - style-sensitive `.pptx` edits -> [../sharepoint-powerpoint/SKILL.md](../sharepoint-powerpoint/SKILL.md)
   - maintained strategy, roadmap, planning, or status docs -> [../sharepoint-shared-doc-maintenance/SKILL.md](../sharepoint-shared-doc-maintenance/SKILL.md)
6. When using SharePoint file-update tools, prefer the drive-root-relative file path from the item's metadata rather than guessing a library-prefixed path. A file may appear under `Shared Documents/...` in the web URL while the writable API path is just the filename or another root-relative path.
7. After any write, re-fetch the file from SharePoint and verify the specific intended change in the returned content or metadata rather than assuming the upload succeeded.
8. Treat verification as two separate checks whenever fidelity matters:
   - Content verification: the intended sections, text, cells, or slides are present.
   - Fidelity verification: headings, spacing, theme, layout, formatting, and template conventions still match the source file's visual language.
9. If connector limitations prevent fidelity verification or safe style-preserving upload, say so explicitly before calling the edit complete.
10. If the request is write-oriented, present the intended content change or structure change before applying broad edits.
11. Call out content dependencies such as linked files, navigation references, approvals, or owners when they affect the update.
12. Only change content, structure, metadata, or sharing state when the user has clearly asked for that action.

## Write Safety

- In Codex, treat the Microsoft SharePoint app tools as the primary surface. Do not rely on generic MCP resource listing for SharePoint discovery; the backend wrapper routes through direct connector tools instead.
- Prefer the exact SharePoint result `url` from `search` or `list_recent_documents` when handing a file into `fetch`; the implementation supports browser/sharing URLs too, but that is fallback resolution logic.
- Preserve page titles, document names, file locations, ownership details, and linked references unless the user requests a change.
- Treat page overwrites, navigation changes, library reorganizations, and sharing or permission changes as high-impact actions that require extra clarity.
- If multiple similarly named sites, pages, or files exist, identify the intended destination before drafting or editing.
- When a requested change could affect linked content or downstream readers, call that out before proposing the update.
- For document edits, preserve the file format and existing structure. Do not replace a `.docx` or other Office file with plain text output when the user expects the original document to remain editable.
- Treat SharePoint `update_file` as a whole-file overwrite, not an in-place Office patch. For rich Office edits, make the change locally to the real package, then replace the file deliberately.
- If one failed binary overwrite strongly suggests inline base64 transport fragility, do not keep retrying richer Office packages blindly. Reassess the connector path, reduce scope, or stop and explain the limitation.

## Output Conventions

- Always reference the exact site, page, library, or file when describing findings or planned edits.
- Summaries should lead with the current purpose or status, then list owners, important content, gaps, and next steps.
- Edit plans should state the target, current state, intended change, and reason.
- When the user asks for structure help, present the proposed navigation or information architecture in a short, scannable outline.
- Distinguish clearly between content analysis and a write-ready update.
- For completed file edits, report both the file that was changed and how you verified the updated result.

## Operational Recovery Notes

- Avoid unsupported wrapper patterns for SharePoint fetch or update calls. If a parallelized or delegated form of the same operation is not supported, retry with the direct connector call rather than spending turns debugging the wrapper.
- On SharePoint `429` throttling, wait the stated retry interval and retry once cleanly.
- If a binary overwrite fails with invalid base64 after a rich Office edit, treat that as likely transport fragility rather than proof that the Office file itself is corrupt.
- When a request has both content and fidelity requirements, do not report overall success after content verification alone. Make the fidelity status explicit.

## Example Requests

- "Summarize this SharePoint site and tell me who owns each major section."
- "Review the project page and draft the content changes needed to reflect the new timeline."
- "Tell me what this document library contains and which files look outdated."
- "Plan the information-architecture changes needed for the operations site before we edit it."
- "Update the team roadmap based on any milestone changes in the project docs."
- "Maintain the shared planning document so it reflects the latest source-of-truth timelines."

## Light Fallback

If SharePoint data is missing or incomplete, say that Microsoft SharePoint access may be unavailable or pointed at the wrong site or file, then ask the user to reconnect or clarify the intended destination.
