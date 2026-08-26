---
name: box-legal-workflows-intake
description: Automate legal client intake and onboarding with Box MCP — review intake documents for completeness against firm requirements, summarize risk for attorney review, route incomplete or high-risk submissions to the right attorney, extract client and matter metadata to Box, and generate engagement letters from Box DocGen templates. Use this skill when the user mentions client intake, client onboarding, new client review, intake documents, or engagement letters.
---

# Client Intake & Onboarding

> **PREREQUISITES:**
> - Read [Box foundation skill](../box/SKILL.md) for Box MCP auth, tool selection, base workflows.
> - Read [shared Box legal workflows](../box-legal-workflows/SKILL.md) for Box collaboration role definitions, Box AI usage boundaries, and reusable confirmation phrasings.

Do client intake *in Box*: inventory the intake folder, check completeness with Box AI against the firm's checklist, extract intake data into Box metadata, route via comments and collaborations, and generate the engagement letter with Box DocGen. This skill is the intake-specific recipe; the underlying Box tool mechanics live in the capability references below. The firm supplies the required-document checklist and risk criteria; conflict, PEP, and sanctions determinations run through the firm's screening system — not the agent or Box AI. Not legal advice.

## Box capability references

Reach for these for tool mechanics rather than restating them here:

- `../box/references/content-workflows.md` — inventory the folder, metadata templates, `set_file_metadata`, file comments
- `../box/references/ai-and-retrieval.md` — completeness checks and data extraction; pacing, limits, citations
- `../box/references/mcp-doc-gen.md` — generate the engagement letter from a template
- `../box/references/collaboration.md` — tag/route the attorney and share with the client
- `../box/references/mcp-search.md` — find/inspect the firm's metadata template

## Box metadata model

Record the intake outcome as file metadata so submissions stay searchable. Find/create the firm's template via `../box/references/mcp-search.md` / `../box/references/content-workflows.md`.

- **Representative fields** (confirm the firm's actual set): `client_name`, `matter_name`, `practice_area`, `matter_owner`, `jurisdiction`, `matter_value`, `intake_status` (complete/incomplete), `risk_rating`, `assigned_attorney`, `decision`, `decision_date`.
- Store the firm/attorney's rating and decision, not the agent's.

## Tool selection

| Intake task | Tool | Notes |
|------|------|-------|
| Inventory submission | `list_folder_content_by_folder_id` | All files in the intake folder |
| Check completeness | `ai_qa_multi_file` | Present/complete/valid vs. firm checklist, with citations |
| Extract intake data | `ai_extract_structured_from_fields_enhanced` | Client, matter, jurisdiction, value |
| Write metadata | `set_file_metadata` | Record status, rating, decision, attorney |
| Tag attorney | `create_file_comment` | Route with the factual summary |
| Grant access | `create_collaboration` | Give the attorney access |
| Generate engagement letter | `create_docgen_batch` | Only if the firm approves |
| Share with client | `add_folder_shared_link` or `create_collaboration` | Confirm audience/expiration |

## Workflow

1. **Inventory**: `list_folder_content_by_folder_id`. **[CONFIRM: intake folder ID]**
2. **Completeness**: `ai_qa_multi_file` — is each required doc (per the firm's checklist) present, complete, and valid, with citations? **[CONFIRM: firm's required-document list]**
3. **Extract intake data**: `ai_extract_structured_from_fields_enhanced` (client_name, matter_name, practice_area, jurisdiction, matter_value, …).
4. **Surface risk indicators (facts only)**: `ai_qa_multi_file` to surface the facts the firm's criteria reference (value, jurisdiction, named parties) with citations. Do **not** use AI to determine conflicts, PEP status, or sanctions — pass names/entities/locations to the firm's screening system.
5. **Persist**: `set_file_metadata` with the firm-confirmed `risk_rating`, `intake_status`, and `decision`.
6. **Route**: `create_file_comment` to tag the attorney with the factual summary; `create_collaboration` for access. **[CONFIRM: who, access level]**
7. **Engagement letter (only if the firm approves)**: `create_docgen_batch` against the firm's template → output to the confirmed folder → share via `create_collaboration` or `add_folder_shared_link`. **[CONFIRM: DocGen template, destination folder, share method/expiration]**

## Legal guardrails

Box mechanics (DocGen template/tag requirements, external-sharing confirmation, AI pacing/limits/citations, metadata writes) are governed by the capability references above and [shared Box legal workflows](../box-legal-workflows/SKILL.md). Specific to intake:

- Conflict, PEP, and sanctions clearance are firm screening + attorney/compliance calls — the agent surfaces the underlying text only and never clears them.
- Risk rating and routing/staffing are firm policy + attorney calls, never the agent's.
- Prompt Box AI to surface facts and cite the source, not to determine risk.
