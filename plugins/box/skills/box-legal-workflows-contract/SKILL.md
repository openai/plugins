---
name: box-legal-workflows-contract
description: Automate contract review and monitoring with Box MCP — find new or expiring contracts, compare them against firm templates to flag material variances, write structured contract metadata back to Box for searchability, and produce variance reports with citations. Use this skill when the user mentions contract review or monitoring, NDA or MSA review, contract expiration or renewals, contract metadata, or variance analysis, even if they don't name a specific Box tool.
---

# Contract Review Agent

> **PREREQUISITES:**
>
> - Read [Box foundation skill](../box/SKILL.md) for Box MCP auth, tool selection, base workflows.
> - Read [shared Box legal workflows](../box-legal-workflows/SKILL.md) for Box collaboration role definitions, Box AI usage boundaries, and reusable confirmation phrasings.

Do contract review *in Box*: find contracts with Box search, compare against the firm's template with Box AI, persist results as Box metadata so they stay searchable, and monitor dates with metadata search. This skill is the contract-specific recipe; the underlying Box tool mechanics live in the capability references below. Materiality, risk, and favorability are firm-supplied criteria confirmed by an attorney — the agent extracts facts, stores them, and routes. It does not provide legal advice or decide risk.

## Box capability references

Reach for these for tool mechanics rather than restating them here:

- `../box/references/mcp-search.md` — find contracts; metadata vs. keyword search, folder scoping, template schema lookup
- `../box/references/ai-and-retrieval.md` — compare to template and extract fields; pacing, text-rep/file limits, citations
- `../box/references/content-workflows.md` — metadata templates, `set_file_metadata`, report uploads, file comments
- `../box/references/collaboration.md` — grant the reviewing attorney access

## Box metadata model

Persist review results as file metadata so contracts stay searchable. Find/inspect the firm's template via `../box/references/mcp-search.md`; create one via `../box/references/content-workflows.md` if none exists.

- **Representative fields** (confirm the firm's actual set): `counterparty_name`, `contract_type`, `execution_date`, `effective_date`, `expiration_date`, `auto_renewal`, `notice_period_days`, `contract_value`, `governing_law`, `status` (active/expired/terminated/under_negotiation), `risk_rating`, `review_date`, `next_review_date`, `expiration_alert_date`. Link to matters with `matter_id`, `practice_area`, `matter_owner`.
- The `risk_rating` value is the firm/attorney's determination — store it, don't decide it.

## Contract search recipes

Once contracts carry metadata, use `search_files_metadata` (mechanics in `../box/references/mcp-search.md`; otherwise `search_files_keyword` with date filters):

- New since last review: `execution_date >= 'YYYY-MM-DD' AND execution_date <= 'YYYY-MM-DD'`
- Expiring window: `expiration_date >= 'YYYY-MM-DD' AND expiration_date <= 'YYYY-MM-DD' AND status = 'active'`
- By counterparty / rating: `counterparty_name = 'Acme Corp'` · `risk_rating = 'High'`

## Tool selection


| Contract task               | Tool                                           | Notes                                                                      |
| --------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------- |
| Find new contracts (date)   | `search_files_metadata`                        | Query `execution_date`; fall back to `search_files_keyword` if no metadata |
| Find expiring               | `search_files_metadata`                        | Query `expiration_date` within 30/60/90 days                               |
| Compare to template         | `ai_qa_multi_file`                             | Contract + firm template in one call                                       |
| Extract metadata (template) | `ai_extract_structured_from_metadata_template` | If a template exists                                                       |
| Extract metadata (custom)   | `ai_extract_structured_from_fields_enhanced`   | Define fields at runtime                                                   |
| Write metadata              | `set_file_metadata`                            | Persist extracted/confirmed fields                                         |
| Create variance report      | `upload_file`                                  | Write the summary doc                                                      |
| Tag attorney                | `create_file_comment`                          | Notify for review/expiration                                               |
| Grant attorney access       | `create_collaboration`                         | If they lack access                                                        |


## Workflow

1. **Find**: `search_files_metadata` or `search_files_keyword`. **[CONFIRM: folder ID, date range/cadence]**
2. **Compare to template**: `ai_qa_multi_file` (contract + firm template) → extract clauses that differ, with citations. **[CONFIRM: template file ID]**
3. **Extract metadata**: `ai_extract_structured_from_metadata_template`, or `ai_extract_structured_from_fields_enhanced` if no template.
4. **Persist**: `set_file_metadata`, including the firm-confirmed `risk_rating`. **[CONFIRM: which fields]**
5. **Report**: `upload_file` — factual differences + citations + firm-confirmed rating (observations for attorney review, not recommendations).
6. **Route**: `create_file_comment` to tag the attorney; `create_collaboration` if they need access. **[CONFIRM: attorney, access]**
7. **Monitor expirations**: `search_files_metadata` on the expiration window → `create_file_comment` reminders → `set_file_metadata` (`expiration_alert_sent: yes`).

## Legal guardrails

Box mechanics (external-sharing confirmation, AI pacing/limits/citations, metadata writes) are governed by the capability references above and [shared Box legal workflows](../box-legal-workflows/SKILL.md). Specific to contracts:

- Risk, materiality, and favorability are firm + attorney calls, never the agent's. If the firm has no documented criteria, route to an attorney rather than rating.
- Prompt Box AI to extract differences and cite section/page — not to judge materiality or legal risk.
- Record decisions in Box as the audit trail: the firm-confirmed rating in metadata plus the uploaded summary.
