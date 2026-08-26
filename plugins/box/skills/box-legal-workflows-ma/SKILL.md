---
name: box-legal-workflows-ma
description: Build and manage M&A virtual data rooms with Box MCP — create secure due-diligence folder structures, scope role-based access for internal teams and external parties, validate permissions before sharing, and answer cross-document due-diligence questions with Box AI. Use this skill when the user mentions M&A, deal rooms, data rooms, VDRs, due diligence, or mergers and acquisitions.
---

# M&A Deal Room Management

> **PREREQUISITES:**
> - Read [Box foundation skill](../box/SKILL.md) for Box MCP auth, tool selection, base workflows.
> - Read [shared Box legal workflows](../box-legal-workflows/SKILL.md) for Box collaboration role definitions, Box AI usage boundaries, and reusable confirmation phrasings.

Build and run an M&A data room *in Box*: create the folder hierarchy, scope role-based access with Box collaborations, validate permissions before sharing, and answer due-diligence questions with Box AI plus citations. This skill is the deal-room-specific recipe; the underlying Box tool mechanics live in the capability references below. Deal risk, materiality, and terms are attorney calls. Not legal advice.

## Box capability references

Reach for these for tool mechanics rather than restating them here:

- `../box/references/content-workflows.md` — create the folder hierarchy, upload/copy, classify-and-file submissions
- `../box/references/collaboration.md` — role-based access, shared links, permission audits (`list_item_collaborations`)
- `../box/references/mcp-search.md` — locate documents, folder-scoped search
- `../box/references/ai-and-retrieval.md` — due-diligence Q&A and term extraction with citations

## Folder structure

Create the tree using the MCP tools in `../box/references/content-workflows.md` (top-down, parent before child; reuse the existing folder on a `409` name conflict). Confirm the firm's template first. Example numbered structure — numeric prefixes keep ordering consistent and segregate external submissions:

```
[Deal Name] M&A Deal Room/
├── 01 - Financial Statements/
├── 02 - Legal Documents/
├── 03 - HR & Employment/
├── 04 - Intellectual Property/
├── 05 - Commercial Contracts/
├── 06 - Real Estate & Assets/
├── 07 - IT & Cybersecurity/
└── 08 - External Submissions/
```

## Access model

Scope access least-privilege and folder-specific rather than root (role capabilities and external-sharing confirmation rules are in `../box/references/collaboration.md` and [shared Box legal workflows](../box-legal-workflows/SKILL.md)). Example deal-room mapping (confirm with the user):

- Internal: Deal Lead → Editor/Co-Owner on root; Finance → Viewer on Financial Statements; Legal → Editor on Legal Documents.
- External: External Counsel → Uploader on their own folder; Auditors → Viewer on Financial Statements; Prospective Buyer → Viewer on a curated subset, not the full room.

## Tool selection

| Deal-room task | Tool | Notes |
|------|------|-------|
| Create folders | `create_folder` | Batch the hierarchy, top-down |
| Add files | `upload_file` / `copy_file` | New uploads or copy existing Box files |
| Grant access | `create_collaboration` | Confirm first for any external party |
| Shared link | `add_folder_shared_link` | Confirm audience/expiration |
| Audit/verify access | `list_item_collaborations` | Before and after external changes |
| Find docs | `search_files_keyword` | Scope with `ancestor_folder_id` |
| Due-diligence Q&A | `ai_qa_multi_file` | Cross-document; surface citations |
| Extract terms | `ai_extract_structured_from_fields_enhanced` | Persist with `set_file_metadata` |
| Classify submissions | `ai_qa_single_file` | Then `copy_file` into the right folder |

## Workflow

1. **Setup**: create the folder tree → grant internal access with `create_collaboration`. **[CONFIRM: structure, emails/roles]**
2. **Populate**: `upload_file`/`copy_file`; classify submissions with `ai_qa_single_file`, then `copy_file` into the right category folder.
3. **External access**: `list_item_collaborations` (audit) → **[CONFIRM: who, folders, permission, expiration]** → `create_collaboration` or `add_folder_shared_link` → `list_item_collaborations` (verify).
4. **Due diligence**: `search_files_keyword` (folder-scoped) → `ai_qa_multi_file` → present the answer with citations; `ai_extract_structured_from_fields_enhanced` for terms → `set_file_metadata` to persist.

## Legal guardrails

Box mechanics (external-sharing confirmation, shared-link settings, AI pacing/limits/citations) are governed by the capability references above and [shared Box legal workflows](../box-legal-workflows/SKILL.md). Specific to deal rooms:

- Deal risk, materiality, and term interpretation are attorney calls, never the agent's.
- Validate permissions with `list_item_collaborations` before *and* after external changes — a folder grant exposes everything inside it, including files added later.
- Audit trail: record returned folder/file/collaboration IDs and write DD summaries back to Box.
