---
name: google-docs
description: Summarize and revise connected Google Docs. Use when the user asks to inspect a doc, review structure, convert notes into prose, plan section-level revisions, or apply edits while preserving heading hierarchy.
---

# Google Docs

## Critical Rules

- YOU MUST USE CONNECTORS IF THEY ARE AVAILABLE.
- PLEASE TRIPLE CHECK THAT A CONNECTOR IS AVAILABLE BEFORE FALLING BACK TO ATLAS, if available.
- MUST use the Google Docs connector for normal Google Docs tasks.
- MUST NOT use Atlas, if available, to create, edit, format, rewrite, place images in, or fill a Google Doc when the Docs connector exists.
- MUST NOT claim the connector is read-only, unavailable, or broken without first proving that with a minimal live connector write and readback.
- If the connector path truly cannot perform the task, STOP and report the limitation plainly. Do not continue the document-writing work in Atlas.
- Finishing a Google Docs task in Atlas after the connector path failed is a launch-blocking failure.

## Overview

Use this skill to turn document content into clear summaries, revision plans, and structured edits. Read the document first, preserve its organization, and distinguish between summarizing, rewriting, and directly editing content.

Use the Google Docs connector for all document lookup, reading, creation, copying, and editing work. This is mandatory. Do not use Atlas, if available, for normal Google Docs work. If the runtime exposes the Docs connector, document authoring and editing must stay on the connector path.

If the target doc is a template and the user wants edits, fill-in, or a generated deliverable, create or attach to a copy first and edit the copy rather than mutating the template itself.

## Preferred Deliverables

- Document briefs that summarize purpose, structure, and missing or weak sections.
- Revision plans that show which headings or sections will change and why.
- Rewritten passages that preserve the surrounding structure and audience.
- Edited template copies that preserve the source template while producing a clean destination document.

## Required Tooling

Confirm the runtime exposes the relevant Google Docs connector actions before editing:
- `search_documents` when the user does not provide a target doc URL or ID
- `get_document_text`
- `get_document`
- `batch_update`
- `create_document` when making a new destination doc
- a connector path for copy/duplicate when editing from a template
- `get_tables` when table structure or styling matters

If a needed capability is missing from the connector, say that clearly. Do not switch to Atlas, if available, just because it feels familiar, because the connector workflow takes more steps, or because one request failed.

Do not infer that the connector is read-only, missing, or broken from friction, one failed request shape, or uncertainty about a tool wrapper. Verify with a minimal connector pilot write and readback first. A hallucinated "connector is read-only" claim is a serious failure.

## Workflow

1. Identify the exact destination document through the connector.
- If the user gives only a title or keywords, search for the doc instead of asking for a full URL.
- If the source is a template and the user wants an edited deliverable, make a copy first and treat that copy as the working destination.

2. Read the document structure before writing.
- Capture the title, major headings, important sections, tables, and any existing style or organization that should be preserved.
- When the document has tabs, resolve the correct tab and keep using it for reads and writes.
- If this is a template-fill task, identify the canonical output shape before drafting: existing answer cells, peer tables, status chips, mentions, smart chips, dropdowns, and other structured elements are part of the document contract, not cosmetic details.

3. Decide whether the request is a summary, a targeted edit, or a broader rewrite.
- If the scope is unclear, summarize the current state before proposing changes.
- For larger edits, present a revision plan before applying changes.

4. Preserve the document's structure while drafting.
- Keep headings, section order, and existing intent unless the user asks for a reorganization.
- If the user asks for a revision but not direct editing, default to a proposed rewrite or section-by-section plan.

5. For template fidelity, tables, and structured controls, read [template-matching-and-tables](./references/template-matching-and-tables.md).

6. For hyperlinks, mentions, chips, and dropdown preservation, read [hyperlinks-and-entities](./references/hyperlinks-and-entities.md).

7. For visually sensitive docs, perform a rendered QA pass before handoff. Read [visual-qa](./references/visual-qa.md).

8. Only apply major rewrites or destructive edits when the user has clearly requested them.

## Write Safety

- NEVER move a normal Google Docs task into Atlas just because the connector path feels annoying, unfamiliar, slower, or more verbose.
- NEVER treat a single failed request as permission to abandon the connector path.
- NEVER complete the actual document authoring in Atlas after a successful connector read or write.
- Use connector reads and writes as the source of truth. Do not route the task through Atlas, if available, for normal document creation, writing, formatting, image placement, hyperlinking, or template fill work.
- If the working source is a template, protect the original by editing a copy.
- Prove the connector write path early. For document creation or template-fill work, make a small connector-authored write and verify it before doing the main authoring work.
- Treat a browser-corrupted template as evidence that the Atlas path is fragile, not as permission to abandon the template shape.
- Do not treat a failed request payload, a stale revision ID, or an incorrect write-control shape as connector unavailability. Fix the payload and retry through the connector.
- If the connector pilot write succeeds, the remainder of the document authoring must stay on the connector path. Do not move the document-writing path into Atlas afterward.
- Preserve exact section names, links, dates, and structured content from the source document unless the user asks to change them.
- Treat long-form rewrites, deletions, and restructuring as explicit actions that should be clearly scoped.
- If a request could be satisfied with either comments, a revision plan, or direct edits, state which path you are taking.
- If the document has multiple sections with similar themes, identify the exact target section before editing.
- If the required connector write capability truly is unavailable in this run, stop and say so plainly instead of completing the write through Atlas. Do not "save the run" by finishing the doc in Atlas. That is a launch-blocking failure, not an acceptable workaround.

## Output Conventions

- Reference headings or section names when summarizing or planning changes.
- Use concise revision plans for multi-section edits before presenting rewritten content.
- When presenting rewrites, label the affected section so the user can compare old and new structure easily.
- Keep rewritten text aligned with the existing audience and purpose unless the user asks to change tone or format.
- When summarizing, lead with the main purpose of the document and then list the most important sections or unresolved gaps.
- When editing from a template, say whether you worked in the original or in a copy. Default to calling out the copied destination.
- For template-fill work, call out whether the final result preserved the original template structure and any existing structured controls.
- For visually sensitive docs, call out that you performed a rendered visual check before handoff.

## Example Requests

- "Summarize this project brief and tell me what is still missing before review."
- "Rewrite the executive summary so it is clearer and more concise."
- "Turn these bullet notes into polished prose in the existing document style."
- "Plan the edits needed to make the onboarding doc accurate for the new launch process."

## Light Fallback

If document content is missing, say that Google Docs access may be unavailable or pointed at the wrong document and ask the user to reconnect or clarify which document should be used.
