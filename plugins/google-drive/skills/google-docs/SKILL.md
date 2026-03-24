---
name: google-docs
description: Summarize and revise connected Google Docs. Use when the user asks to inspect a doc, review structure, convert notes into prose, plan section-level revisions, or apply edits while preserving heading hierarchy.
---

# Google Docs

## Overview

Use this skill to turn document content into clear summaries, revision plans, and structured edits. Read the document first, preserve its organization, and distinguish between summarizing, rewriting, and directly editing content.

## Preferred Deliverables

- Document briefs that summarize purpose, structure, and missing or weak sections.
- Revision plans that show which headings or sections will change and why.
- Rewritten passages that preserve the surrounding structure and audience.

## Workflow

1. Read the document structure before writing. Capture the title, major headings, important sections, and any existing style or organization that should be preserved.
2. Decide whether the request is a summary, a targeted edit, or a broader rewrite. If the scope is unclear, summarize the current state before proposing changes.
3. For larger edits, present a revision plan before applying changes. Make the intended section-level updates easy to review.
4. Preserve the document's structure while drafting. Keep headings, section order, and existing intent unless the user asks for a reorganization.
5. If the user asks for a revision but not direct editing, default to a proposed rewrite or section-by-section plan.
6. Only apply major rewrites or destructive edits when the user has clearly requested them.

## Write Safety

- Preserve exact section names, links, dates, and structured content from the source document unless the user asks to change them.
- Treat long-form rewrites, deletions, and restructuring as explicit actions that should be clearly scoped.
- If a request could be satisfied with either comments, a revision plan, or direct edits, state which path you are taking.
- If the document has multiple sections with similar themes, identify the exact target section before editing.

## Output Conventions

- Reference headings or section names when summarizing or planning changes.
- Use concise revision plans for multi-section edits before presenting rewritten content.
- When presenting rewrites, label the affected section so the user can compare old and new structure easily.
- Keep rewritten text aligned with the existing audience and purpose unless the user asks to change tone or format.
- When summarizing, lead with the main purpose of the document and then list the most important sections or unresolved gaps.

## Example Requests

- "Summarize this project brief and tell me what is still missing before review."
- "Rewrite the executive summary so it is clearer and more concise."
- "Turn these bullet notes into polished prose in the existing document style."
- "Plan the edits needed to make the onboarding doc accurate for the new launch process."

## Light Fallback

If document content is missing, say that Google Docs access may be unavailable or pointed at the wrong document and ask the user to reconnect or clarify which document should be used.
