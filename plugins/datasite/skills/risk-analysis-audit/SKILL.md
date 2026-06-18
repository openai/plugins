---
name: risk-analysis-audit
description: >
  Risk Analysis Audit skill for Datasite deal rooms. Use this skill whenever a sell-side
  deal team wants to audit, review, or flag risks across a data room before going live.
  Triggers include: "run a risk audit", "flag risks in the data room", "risk review",
  "what are the risks in this deal", "audit the data room", "risk analysis", "flag issues
  before we go live", "what should we fix before launch", or any request to analyse deal
  risk by workstream (Tax, Finance, Legal, HR, IP, Commercial, Regulatory, ESG).
  Use this skill proactively whenever the user is preparing a data room for launch and
  wants a structured view of what might concern a buyer.
  Do not use for document quality issues like PII or redaction (use document-quality-check),
  or for identifying missing sections (use gap-analysis).
metadata:
  author: Blueflame AI
  version: 1.0.0
  mcp-server: datasite
  category: deal-management
  tags: [datasite, vdr, m&a, risk, audit, blueflame]
---

# Risk Analysis Audit

You are helping a sell-side deal team identify and understand risks across their Datasite data room before it goes live to buyers. Your job is to find what's there, what's missing, and what the content itself reveals — then present it as a clear, area-by-area risk picture that the team can act on.

The output is an **HTML risk dashboard** rendered in the conversation, giving a visual scorecard by workstream with expandable risk detail.

---

## Terminology — fileroom vs. folder

Use these terms precisely when communicating with the user:

- **Fileroom** — the single top-level container inside a Datasite project. A project typically has one buyer-facing fileroom. It is not a subject area — it is the container that holds all subject areas.
- **Folder** — everything inside the fileroom: the subject areas (Financial, Legal, HR, Tax, IP, etc.) and all sub-levels beneath them. Always call these folders, never filerooms.

When in doubt: if it is not the single top-level container for the whole project, it is a folder.


## Feature Requirements

| Capability | Free | Requires Blueflame |
|---|:---:|:---:|
| Structural presence check (which sections exist or are missing) | ✅ | — |
| Content risk signals (going concern, litigation, tax disputes, etc.) | — | ✅ |
| Per-workstream risk findings with source citations | — | ✅ |

**Without Blueflame:** The skill can confirm which risk workstream sections are present, sparse, or missing — but cannot find risk signals inside document text. The report will show structural observations only. The core value of this skill (surfacing what's in the documents) requires Blueflame.

**With Blueflame:** `searchDocuments` scans content across all six workstreams (Finance, Tax, Legal, HR, Commercial, IP/ESG) and surfaces specific risk signals with document source and page references.



> ⚠️ **Blueflame content guard — two-tier behaviour**
> `searchDocuments` is the only permitted source of document content.
> - Do **not** use Claude's training knowledge, general M&A knowledge, or inference from file names for any findings.
> - **Pass 1** (folder presence per workstream) uses `listFolderContents` only — always free. Complete Pass 1 across all workstreams first.
> - **Pass 2** (content search for risk signals) requires `searchDocuments`. Before starting Pass 2, attempt one call. If it returns an **activation link** instead of results, **do not discard Pass 1 findings**. Present them first, then say:
>
>   > "I've completed the structural review. Summary: [list which workstream sections are present, sparse, or missing in plain text — e.g. 'Finance: 3-year accounts present', 'Legal: litigation folder empty']. To scan document content for actual risk signals, Blueflame AI search needs to be activated:
>   > 🔗 **Activate Blueflame:** [activation link]
>   > **With Blueflame:** I'll run targeted searches across Finance, Tax, Legal, HR, Commercial, and IP workstreams and surface specific flags with document source and page references — these are the signals that matter most to buyers in due diligence.
>   > Would you like to activate now, or shall I produce a structural-only risk dashboard?"
>
> **Do not generate the HTML risk dashboard until after the user responds to this question.**
> - All content findings **must** be sourced exclusively from tool results.

> **`listFolderContents` — efficient traversal**
> - `depth: 1` (default) — immediate children only. Use for targeted lookups.
> - `depth: 5, foldersOnly: true` (default when depth > 1) — full folder tree in one call, no documents. Use for structural checks.
> - `depth: 5, foldersOnly: false` — full folder tree including all document metadata in one call. Use when building a document inventory.
> - When `depth > 1`, the response is a **flat list** with `depth` and `path` columns — not a nested tree.

## Step 1 — Orient yourself in the project

Call `getProjectOverview` to understand the deal context: company name, sector, transaction type, deal size, and what filerooms exist. This shapes which risk areas matter most and how deeply to search.

Note the fileroom structure. You'll use `listFolderContents` to navigate it and `searchDocuments` to find risk signals within document content.

---

## Step 2 — Two-pass analysis per risk area

Work through each of the six risk workstreams below. For each one, run **two passes**:

**Pass 1 — Presence check (structural)**
Use `listFolderContents` to navigate the relevant section of the data room. For each expected document category, note:
- ✓ Present — folder exists and contains documents
- ⚠ Sparse — folder exists but appears empty or has fewer documents than expected
- ✗ Missing — folder or document category absent entirely

**Pass 2 — Content scan (substantive)**
Use `searchDocuments` with targeted queries (listed per workstream below) to surface risk signals from within document text. The tool returns snippets — read them for red flags. You don't need to read every document; targeted searches surface what matters.

Combine both passes to form your findings for that workstream.

---

> **Reference material:** Read `references/workstream-queries.md` before starting Pass 2 for any workstream. It contains the full search query lists and risk signal definitions for all six workstreams. Load only the sections relevant to the current deal.

## Workstream 1 — Financial & Accounting

**What to look for structurally:**
- Audited financial statements (last 3 years minimum — or 5 for large-cap)
- Management accounts (recent months)
- Financial model / projections
- Debt schedule and loan agreements
- Working capital analysis

For Pass 2 search queries and risk signal definitions, see `references/workstream-queries.md → Workstream 1`.

---

## Workstream 2 — Tax

**What to look for structurally:**
- Filed federal/national tax returns (last 3 years)
- State/local returns (US) or VAT returns (UK/EU)
- Correspondence with tax authorities
- Tax disputes and assessments

For Pass 2 search queries and risk signal definitions, see `references/workstream-queries.md → Workstream 2`.

---

## Workstream 3 — Legal, Litigation & Regulatory

**What to look for structurally:**
- Pending/threatened litigation schedule
- Material contracts (particularly change of control clauses)
- Regulatory licences and their expiry dates
- Regulatory correspondence and enforcement history
- Insurance schedule

For Pass 2 search queries and risk signal definitions, see `references/workstream-queries.md → Workstream 3`.

---

## Workstream 4 — HR & Employment

**What to look for structurally:**
- Employee list (especially senior/licensed staff)
- Key employment agreements
- Non-compete and non-solicitation agreements
- Benefits, pension, and incentive plans
- Any redundancy, grievance, or disciplinary records

For Pass 2 search queries and risk signal definitions, see `references/workstream-queries.md → Workstream 4`.

---

## Workstream 5 — Commercial & Contracts

**What to look for structurally:**
- Top customer contracts (especially top 5–10 by revenue)
- Supplier and vendor agreements
- Distribution and agency agreements
- Contract expiry/renewal schedule

For Pass 2 search queries and risk signal definitions, see `references/workstream-queries.md → Workstream 5`.

---

## Workstream 6 — IP, Technology & ESG

**What to look for structurally (IP & Technology):**
- IP ownership documentation (patents, trademarks, registered rights)
- IP assignments from founders and employees
- Open-source software inventory
- Data privacy and cybersecurity policies
- IT system and licence agreements

**What to look for structurally (ESG):**
- Environmental compliance certificates and violation history
- Health & safety incident records
- Diversity and inclusion policies
- Modern Slavery Act statement (required for UK businesses >£36M turnover)

For Pass 2 search queries and risk signal definitions for both IP/Technology and ESG, see `references/workstream-queries.md → Workstream 6`.

---

## Step 3 — Compile findings

After completing all six workstreams, compile your findings into a structured list:

```
findings = [
  {
    area: "Tax",
    severity: "High",
    title: "Open IRS audit for FY2023",
    detail: "Correspondence in folder 3.6 references an open IRS examination for tax year 2023. No resolution letter found.",
    source: "3.6 IRS Correspondence / Letter dated March 2024"
  },
  ...
]
```

Also track structural gaps separately:
```
gaps = [
  { area: "Finance", item: "Working capital analysis — folder empty" },
  { area: "HR", item: "Non-compete agreements — folder missing entirely" },
  ...
]
```

Count risks by severity per area — this drives the dashboard scorecard.

---


## Step 3b — Cross-document data consistency checks

Run the following consistency checks across the data room. These use `searchDocuments` to pull specific figures from different document types and compare them. Discrepancies are flagged as **Medium** risks minimum; large discrepancies are **High**.

### Headcount / FTE consistency
Find headcount figures in the following document types and compare them:
- P&L or financial statements (FTE cost line or employee note)
- HR employee list or org chart
- Board presentations or management accounts (FTE KPI)
- Any regulatory filings that reference employee numbers

Flag if the figures differ by more than 10% across sources, or if any source gives a materially different total. Note the specific sources and figures found.

### Top customer list consistency
If a "top 20 / top 50 customers" list exists, cross-check customer names and revenue figures against:
- Financial statements or revenue schedules
- CRM or sales data (if present)
- Any investor presentation or board pack referencing customer concentration

Flag customers who appear in one list but not another, or where revenue attributions differ materially.

### Top vendor / supplier spend consistency
If a vendor spend list exists, cross-check against:
- P&L cost line items (COGS, OpEx breakdown)
- Any procurement or spend analysis document

Flag if total vendor spend implied by the list is materially inconsistent with cost lines in the financials.

### Board and management roster consistency
Cross-check board member and senior management names across:
- Corporate documents (articles, board minutes, Companies House / registry filings)
- Org chart
- Employment contracts or service agreements
- Any investor or management presentation

Flag any person who appears in one source but not another (e.g. listed as a director in board minutes but absent from the org chart, or named in a management presentation but with no service agreement).

### Financial figures cross-check
Pick the 3 most prominent financial metrics in the data room (typically revenue, EBITDA, and headcount/FTE). Verify they are stated consistently across:
- Audited accounts
- Management accounts
- Board presentations / investor decks
- Any teaser or information memorandum

Flag any material discrepancy (>5% difference) as a **High** risk — buyers will spot these immediately and it will undermine confidence in the whole data room.

---

## Step 3c — External news intelligence on top customers and vendors

> This step uses web search, not `searchDocuments`. It is always free — no Blueflame credits required.

Extract the names of the top 5–10 customers and top 5–10 vendors from the data room (use the customer/vendor lists found in Step 3b, or from commercial documents identified in Workstream 5). Then run a targeted web news search for each name.

**For each top customer, search for:**
- Recent M&A activity (acquisition of the customer by a competitor or PE firm, merger with another entity, or the customer itself being sold) — any of these can trigger contract renegotiation or termination
- Financial distress signals (credit rating downgrades, profit warnings, restructuring announcements, insolvency rumours)
- Strategic pivots that could reduce dependency on the target's product/service (e.g. in-housing, switching to a competitor)
- Leadership changes (new CEO/CPO/CTO) — often precede vendor reviews
- Regulatory or legal issues that could disrupt the customer's own operations

**For each top vendor, search for:**
- M&A activity (vendor acquired by a competitor, merged, or restructuring) — may affect pricing, continuity, or exclusivity
- Financial distress or supply chain disruption signals
- Geopolitical exposure (sanctions, trade restrictions, country-of-origin risk)
- Price escalation announcements or force majeure notices

**How to run the search:**
Use web search with queries in the format: `"[Customer/Vendor Name]" news 2024 2025 acquisition OR merger OR restructuring OR insolvency OR "strategic review"`. Run a separate query for each name. If a name is generic (e.g. "Global Logistics Ltd"), add the sector or country to disambiguate.

**Risk signals to flag:**
- Top customer acquired by a known competitor of the target → **High** (high probability of contract review or termination post-close)
- Top customer in financial distress or undergoing restructuring → **High** (revenue at risk)
- Top customer announced vendor consolidation or platform shift → **High**
- Top vendor acquired by a company with conflicting interests → **High** (supply continuity risk)
- Top vendor subject to sanctions or trade restrictions → **High**
- M&A activity in the customer or vendor base with no change of control provision in the relevant contract → **Medium** (contract does not protect the target)
- New leadership at a key customer with no relationship established → **Medium**
- Any news (positive or negative) about a customer or vendor that is not reflected anywhere in the data room → **Medium** (disclosure gap — buyer will find it)

**Present findings as:** a table with columns: Name | Type (Customer/Vendor) | News Found | Risk Level | Source URL | Recommended Action.

If no material news is found for a name, record "No material news found" and continue. Do not skip this step — a clean result is itself a valuable finding.

---

## Step 4 — Offer outputs

Before generating the dashboard, ask:

> "I've completed the risk audit. Would you like me to generate the interactive HTML risk dashboard, or would a plain text risk summary in this conversation be enough? The dashboard uses additional credits to render — the plain text summary is free."

Only build the dashboard if the user confirms. If they decline, go to Step 5 and deliver a plain text summary.

### Dashboard specification (build only on user confirmation)

Generate a self-contained HTML page and write it as an artifact. The dashboard should include:

**Header:**
- Deal name, date of audit, total risk counts (High / Medium / Low)

**Risk Scorecard (top section):**
- Six area tiles, each showing: area name, risk counts (H/M/L), and a colour signal:
  - Any High → red tile border
  - Only Medium/Low → amber tile border
  - No findings → green tile border

**Detailed findings (below the scorecard):**
- Grouped by workstream
- Each finding shows: severity badge (colour-coded), title, detail text, and source reference
- A "Structural gaps" sub-section per area listing missing or sparse folders

**Style guidance:**
- Clean, professional — this will be shared in deal team meetings
- White background, dark headings, muted colour palette
- Severity badges: High = red (#DC2626), Medium = amber (#D97706), Low = grey (#6B7280)
- No external dependencies — fully self-contained HTML/CSS/JS

---

## Step 5 — Present to the user

After rendering the dashboard, give a brief verbal summary:

> "I've audited [N] sections of the data room and found [X] High, [Y] Medium, and [Z] Low risks. The areas with the most critical issues are [list]. Each finding is tagged with its source document so you can locate it directly in the data room."

Then offer:
> "Want me to export this as an Excel risk register, or shall we work through any of the High risks in more detail?"

---

## Operating principles

**Search intelligently, not exhaustively.** Run the targeted queries from `references/workstream-queries.md`. Don't attempt to read every document — the snippets are sufficient. If a snippet is ambiguous, run a follow-up search to confirm before flagging.

**Be specific about sources.** Every finding must reference the folder path or document name. Vague findings ("there may be tax issues") are not useful — deal teams need to go straight to the source.

**Calibrate to deal size.** A risk that is High for a £10M SME may be Medium for a £500M transaction where diligence coverage is deeper and warranties are broader. Use `transactionValue` from the project metadata to calibrate.

**Don't over-flag.** Not everything unusual is a risk. A non-compete that looks standard, or a customer contract that's long-dated and unconditional, should not be flagged just because it appeared in a search. Flag what a diligent buyer's counsel would genuinely raise.

**Sell-side framing.** This audit is for the team preparing the room, not buyers. Frame findings as things to address, disclose, or explain — not as reasons to walk away.

## Performance Notes

- **Fewer, well-evidenced findings are more valuable than many speculative ones.** Every finding must have a source citation — folder path, document name, and where possible a page reference.
- Run the targeted search queries listed per workstream. Do not attempt to read every document.
- Calibrate severity to deal size using `transactionValue` from the project overview.
- Do not over-flag. A non-compete that looks standard or a customer contract that is long-dated and unconditional should not be flagged just because it appeared in a search.

---

## Common Issues

**`getProjectOverview` fails or returns the wrong project**
Check that the Datasite MCP connector is connected (Settings → Extensions → Datasite should show "Connected"). If you have multiple projects open, confirm with the user which project to use.

**`listFolderContents` returns no results**
The fileroom may be empty or unpublished. Re-run `listFolderContents` without a `metadataId` to list all filerooms from the root. If a fileroom exists but shows 0 documents, the content may not yet be published — note this to the user and proceed with what is available.

**`searchDocuments` returns an activation link instead of results**
Blueflame AI search is not yet active on this project. Follow the Blueflame prompt in the skill instructions above. Do not attempt to answer using Claude's training knowledge.

**MCP disconnects mid-workflow**
Reconnect via Settings → Extensions → Datasite. Resume from the last completed step — results already gathered do not need to be re-fetched.

**`updateContent` or `createContent` returns a permissions error**
The user's Datasite account may not have Editor permissions on this project. Ask them to check their role in Datasite project settings.
