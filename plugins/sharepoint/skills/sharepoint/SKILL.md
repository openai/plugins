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

## Workflow

1. Read the relevant site, page, file, or library before proposing changes. Capture the current title, location, owners, linked documents, and the content that matters.
2. When the user is exploring, summarize the current information architecture or document state before suggesting edits.
3. Ground every recommendation in the exact SharePoint destination, such as the site name, page name, library, or file path.
4. If the request is write-oriented, present the intended content change or structure change before applying broad edits.
5. Call out content dependencies such as linked files, navigation references, approvals, or owners when they affect the update.
6. Only change content, structure, metadata, or sharing state when the user has explicitly asked for that action.

## Write Safety

- Preserve page titles, document names, file locations, ownership details, and linked references unless the user requests a change.
- Treat page overwrites, navigation changes, library reorganizations, and sharing or permission changes as high-impact actions that require extra clarity.
- If multiple similarly named sites, pages, or files exist, identify the intended destination before drafting or editing.
- When a requested change could affect linked content or downstream readers, call that out before proposing the update.

## Output Conventions

- Always reference the exact site, page, library, or file when describing findings or planned edits.
- Summaries should lead with the current purpose or status, then list owners, important content, gaps, and next steps.
- Edit plans should state the target, current state, intended change, and reason.
- When the user asks for structure help, present the proposed navigation or information architecture in a short, scannable outline.
- Distinguish clearly between content analysis and a write-ready update.

## Example Requests

- "Summarize this SharePoint site and tell me who owns each major section."
- "Review the project page and draft the content changes needed to reflect the new timeline."
- "Tell me what this document library contains and which files look outdated."
- "Plan the information-architecture changes needed for the operations site before we edit it."

## Light Fallback

If SharePoint data is missing or incomplete, say that Microsoft SharePoint access may be unavailable or pointed at the wrong site or file, then ask the user to reconnect or clarify the intended destination.
