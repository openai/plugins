---
name: vdr-index-setup
description: >
  VDR Index Setup skill for Datasite deal rooms. Use this skill whenever
  a user wants to create, propose, design, or set up a Virtual Data Room (VDR) index
  or folder structure for a deal. Triggers include: "set up a data room", "create a
  VDR index", "build a deal room structure", "prepare the index", "set up the fileroom",
  "I need a data room for [deal/company]", or any request to organise or structure
  documents for due diligence. Also triggers when a user wants to replicate an existing
  deal room structure or import an index from a spreadsheet or reference deal. This skill
  MUST be used whenever the user is starting a new deal room or wants to customise the
  folder hierarchy before documents are uploaded.
  Do not use to audit or review an existing data room — use gap-analysis,
  document-quality-check, or risk-analysis-audit for that.
metadata:
  author: Blueflame AI
  version: 1.0.0
  mcp-server: datasite
  category: deal-management
  tags: [datasite, vdr, m&a, index, folder-structure, setup]
---

# VDR Index Setup

You are helping a deal team on Datasite create a professional, customised Virtual Data Room (VDR) index — the folder hierarchy buyers and advisors will navigate during due diligence. The goal is to produce an index that feels purpose-built for the specific deal, not a generic template.

## Terminology — fileroom vs. folder

Use these terms precisely when communicating with the user:

- **Fileroom** — the single top-level container inside a Datasite project. A project typically has one buyer-facing fileroom. It is not a subject area — it is the container that holds all subject areas.
- **Folder** — everything inside the fileroom: the subject areas (Financial, Legal, HR, Tax, IP, etc.) and all sub-levels beneath them. Always call these folders, never filerooms.

When in doubt: if it is not the single top-level container for the whole project, it is a folder.


## Feature Requirements

| Capability | Free | Requires Blueflame |
|---|:---:|:---:|
| Propose and create folder index | ✅ | — |
| Read project context and sector | ✅ | — |
| Push structure to Datasite | ✅ | — |
| Invite team members | ✅ | — |

**This skill is fully free.** It uses only `getProjectOverview`, `listSubscriptions`, `setupProject`, `createContent`, and `listFolderContents` — no AI content search is required.



> ℹ️ **No Blueflame required** — this skill uses only `getProjectOverview`, `listSubscriptions`, `setupProject`, `createContent`, and `listFolderContents`. It never calls `searchDocuments`. All functionality is available without Blueflame activation.

> **`listFolderContents` — efficient traversal**
> - `depth: 1` (default) — immediate children only. Use for targeted lookups.
> - `depth: 5, foldersOnly: true` (default when depth > 1) — full folder tree in one call, no documents. Use for structural checks.
> - `depth: 5, foldersOnly: false` — full folder tree including all document metadata in one call. Use when building a document inventory.
> - When `depth > 1`, the response is a **flat list** with `depth` and `path` columns — not a nested tree.

## Step 1 — Read the project context first

**Before asking the user anything**, call `getProjectOverview` on the current project. This will return everything Datasite already knows about the deal from when it was set up. Extract and map the following fields:

| Blueflame field | Maps to | Example values |
|---|---|---|
| `name` | Company / deal name | "Project Falcon" |
| `industryType` | Sector | TECHNOLOGY_MEDIA_TELECOM → Tech/SaaS; LIFE_SCIENCES_HEALTHCARE → Healthcare; CONSUMER → Retail/Consumer; INDUSTRIALS_TRANSPORT_DEFENSE → Manufacturing/Transport; ENERGY_MINING_OIL_GAS → Oil & Gas; FINANCIAL_SERVICES → Financial Services; REAL_ESTATE → Real Estate |
| `useCase` | Transaction type | COMPANY_SALE / DIVESTITURE → M&A sell-side; ACQUISITION → buy-side; MERGER → merger; PRIVATE_EQUITY_FUNDRAISING / ADD_ON → PE; VC_FUNDING_ROUND / FUNDRAISING → capital raise; RESTRUCTURING_OR_INSOLVENCY → restructuring |
| `transactionValue` | Size / complexity | LESS_THAN_US_10_M → SME; BETWEEN_US_10_M_AND_100_M → lower mid-market; BETWEEN_US_100_M_AND_500_M → mid-market; BETWEEN_US_500_M_AND_1_B / GREATER_THAN_US_1_B → large-cap |
| `datacenter` | Geography hint | USA → US/North American; DEU → European (assume GDPR, EU regulatory); AUS → Australian |

With these four fields you already know the company name, sector, deal type, approximate size, and a geography signal. **Do not ask the user to repeat this information.**

### What to ask about (only the genuine gaps)

After reading the project, there may be a small number of things worth clarifying. Ask only what you actually need, in a single short message — not a form:

- **Specific industry sub-type** if `industryType` is broad and it meaningfully changes the index. For example: TECHNOLOGY_MEDIA_TELECOM could be SaaS, hardware, media/publishing, or telecoms — each has different IP and revenue sections. CONSUMER could be retail, food & beverage, or e-commerce. If the project name makes it obvious (e.g. "Project Falcon — CloudSoft Ltd"), skip this.
- **Jurisdiction precision** if the datacenter alone is ambiguous. DEU datacenter but a UK-domiciled company is common — in that case you'd want HMRC/FCA references not BaFin. A single question like "Is the company UK or continental EU domiciled, or cross-border?" is enough.
- **Carve-out or subsidiary** flag if the `useCase` doesn't reveal it — a carve-out needs Transition Services Agreement, shared services, and stranded costs sections that a clean M&A sale doesn't.

If none of these gaps exist (e.g. the project is clearly "US SaaS company, COMPANY_SALE, mid-market"), go straight to generating the index. Don't ask questions for the sake of it.

### Optional: reference structure

Also offer this once, briefly: "If you'd like me to base the index on an existing deal structure, you can attach the index as a spreadsheet or give me a deal name and I'll read it from the platform." If the user provides one, go to **Step 1b** before generating.

> **If the user has already attached a file or referenced another VDR at the start of the conversation, skip this offer entirely — go directly to Step 1b.** Do not propose your own sector-based index if a reference has been provided. The reference is the authoritative starting point; your role is to adapt it for the current deal, not to replace it.

## Step 1b — Read a reference index (if provided)

**If the user uploads a spreadsheet:**
Read the file. Extract the folder hierarchy from the Index and Title columns.

**If the user names a reference deal:**
Call `listFolderContents` with `depth: 5` (leave `foldersOnly` at its default of `true`) to retrieve the full folder hierarchy in a single call. The response is a flat list with `depth` and `path` columns — read through it to extract the complete structure.

After reading either source, **ask the user one question before proceeding:**

> "I've read the reference structure — [N] folders across [N] levels. How would you like me to use it?
> - **Use as-is** — push it to the data room exactly as provided, no changes
> - **Suggest additions** — keep the reference intact and flag any sections that are typically expected for a [sector] deal but aren't currently included
> - **Full adaptation** — use it as a base and apply deal-specific tailoring for [company name] ([sector], [deal type])"

Wait for the user's choice before doing anything else.

- If **use as-is**: skip Step 2 entirely, go straight to Step 4 (confirm and push). Do not modify, rename, or reorder anything.
- If **suggest additions**: present the reference index as-is, then append a clearly separated section: *"Suggested additions for [sector]:"* listing only what is missing. The user decides what to include before anything is pushed.
- If **full adaptation**: proceed to Step 2 and generate the tailored index using the reference as the base structure.

## Step 2 — Generate the proposed index

Using the project profile you've assembled, produce a complete, numbered folder hierarchy. Read `references/sector-templates.md` for the relevant sector(s) before generating — don't rely on memory for the sub-folder detail.

**How to tailor the index:**

**Sector** — pull the relevant sector section from the reference templates. Key distinctions:
- SaaS / Technology → deep IP section (registered/unregistered rights, open-source, licensing in/out, domain names, software asset list), ARR/MRR in Finance, data privacy prominent under IT
- Healthcare → add Regulatory & Clinical section (licences, CQC/FDA filings, clinical contracts), careful separation of NHS vs. private revenue
- Manufacturing → add Plant & Equipment, Supply Chain, and Environmental sections
- Oil & Gas → add Reserves, Environmental & Regulatory, Concession Agreements sections
- Retail → add Leasehold Properties, Brand & Licensing, Supplier Contracts sections
- Financial Services → add Regulatory Capital, FCA/SEC authorisations, Client Money sections

**Transaction type:**
- M&A sell-side (COMPANY_SALE, DIVESTITURE) → include Closing Documents section at the end
- PE / add-on (PRIVATE_EQUITY_FUNDRAISING, ADD_ON) → stronger management/governance sections, lighter closing docs, include Management Accounts and KPIs
- Carve-out (DIVESTITURE where partial) → add Transition Services Agreement, Shared Services, Stranded Costs, and Intercompany Agreements sections
- Capital raise (VC_FUNDING_ROUND, FUNDRAISING) → include Investor Presentations, Cap Table History, Use of Proceeds, Funding History
- Restructuring → include Insolvency Proceedings, Creditor Agreements, Security Documents

**Geography:**
- US / USA datacenter → IRS/SEC/EIN references, Federal/State/Local tax split, FCPA under Compliance
- European / DEU datacenter → GDPR sub-folder prominent under IT/Data, EU regulatory references, VAT returns in Tax
- UK-domiciled → HMRC references, FCA/CMA in Regulatory, Companies House in Corporate, use "Articles of Association" not "By-Laws"
- Cross-border → duplicate Tax and Legal sections per jurisdiction (e.g. "Tax — UK", "Tax — Germany")

**Size / complexity:**
- SME (< $10M) → 2–3 levels, combine Accounting into Finance, lighter HR section
- Lower mid-market ($10–100M) → standard 3 levels, most sections present but not fully expanded
- Mid-market ($100–500M) → full 3–4 levels as in the base templates
- Large-cap (> $500M) → maximum depth, consider splitting into multiple filerooms by workstream

**Years of financial and corporate history** — set automatically, never ask the user:
- Standard M&A sell-side (mid-market and below) → **3 years** audited financials (last 3 closed years, i.e. today's year − 1, − 2, − 3) + current-year management accounts to date
- Large-cap (> $500M) → **5 years** audited financials; buyers and their advisors will expect this
- VC / early-stage fundraise (`VC_FUNDING_ROUND` + `LESS_THAN_US_10_M`) → **2 years**, or inception-to-date if the company is younger; note this in the folder label
- Restructuring / distressed → **3 years** but lead with management accounts over audited, since audits may be delayed or qualified
- **Last closed financial year = today's year − 1.** Never use the current calendar year as a closed year — it is not yet complete. In 2026, the last closed year is FY2025.
- Always use actual closed years (e.g. in 2026: FY2023, FY2024, FY2025 for standard M&A) — never write "[Year]" or include the current year as closed.
- If the company is less than 3 years old, include all available years and add a note: e.g. "Audited Financial Statements (FY2024, FY2025 — include inception-to-date accounts if prior history unavailable)"
- Apply the same year logic to corporate history folders (board minutes, tax returns, regulatory filings) — use the same horizon as financials for consistency

**Format of the proposal:**
Present the index as a clean numbered hierarchy with indentation:

```
1. General Information
   1.1 Corporate Organisation
       1.1.1 Group Structure Chart
       1.1.2 Certificate of Incorporation
       1.1.3 Articles of Association
       1.1.4 Board Minutes and Resolutions (last 3 years)
   1.2 Shareholders
       1.2.1 Shareholder Register
       1.2.2 Shareholder Agreements
       1.2.3 Cap Table
2. Finance
   2.1 Audited Financial Statements (FY2023, FY2024, FY2025)  ← example using 2026 as today; always use actual last-3-closed-years
   2.2 Management Accounts (monthly, last 24 months)
   ...
```

Where years are relevant, always use actual calendar years based on today's date — never write "[Year]".

Close with: "This is my proposed index for [Company Name]. You can ask me to modify any part — add or remove sections, rename or move folders, or adjust the depth. Once you're happy I can push it to the data room, or export it to Excel first."

## Step 3 — Iterate with the user

Handle all edit requests conversationally:

- **Add a section** → insert in a logical position and renumber. Briefly note where you've placed it if it's not obvious.
- **Remove a section** → confirm and renumber. If it has children, confirm those go too.
- **Rename** → apply to that folder only, unless the user says otherwise.
- **Move** → relocate and renumber throughout. Adjust child numbering if the hierarchy level changes.
- **Adjust depth** → "collapse HR to one level" flattens sub-folders; "expand Contracts" prompts for the desired sub-sections.

After each change, show the updated portion (or the full index if it's a large restructure). Confirm the complete final state before moving to Step 4.

## Step 4 — Confirm before pushing

Show a clear confirmation gate before creating anything:

> "Here's the final index for **[Company Name]** — **[N] folders** across **[N] levels**. Ready to create this in the **[Fileroom Name]** data room. Shall I go ahead?"

Also offer: "Or I can export it as an Excel file in the Datasite import format if you'd prefer to import it manually."

Only proceed once the user confirms.

## Step 5 — Push the index to Datasite

> ⚠️ **PREPARE projects:** These use a Staging Folder (sandbox) exclusively. All content must be created within the Staging Folder — do not create filerooms or folders outside it. Use `listFolderContents` to locate the sandbox (type: SANDBOX, name: "Staging Folder") before creating any content.


**Two options — choose based on whether the project already exists:**

**Option A — New project (project does not yet exist):**
Use `listSubscriptions` to find the available subscription, then call `setupProject` with the confirmed folder tree as a `contentTree` JSON array. This creates the project and the entire folder hierarchy in a single call. Example structure:
```
[{"name":"Financial","children":[{"name":"Audited Financial Statements"},{"name":"Management Accounts"}]},{"name":"Legal"}]
```
Top-level nodes in `contentTree` become filerooms; nested nodes become folders.

**Option B — Project already exists:**
1. `listFolderContents` (no `metadataId`, `depth: 1`) — check if a fileroom already exists. Returns immediate top-level items only. If a fileroom exists, ask the user whether to add the index inside it or create a new one.
2. `createContent` — create folders inside the existing fileroom. Pass the full tree as `contentTree` with the fileroom's `metadataId` as `parentId`.

**Workflow:**
1. `listFolderContents` (no `metadataId`, `depth: 1`) — check if a fileroom already exists.
2. `createContent` — create the top-level fileroom if needed.
3. `createContent` — pass the full folder tree as `contentTree` so the entire hierarchy is created in one call.

**Error handling:** if a folder fails, note it and continue. Report failures at the end with the folder path so the user can investigate.

**On completion:**
> "Done ✓ — **[N] folders** created in **[Fileroom Name]**. Top-level sections: [list].
> 🔗 Open in Datasite: `https://app.global.datasite.com/en/platform/prepare/[projectId]/overview`
> Let me know if you’d like to adjust anything or invite team members."

**Important:** Always use the URL format above when linking to a Datasite project — `https://app.global.datasite.com/en/platform/prepare/{projectId}/overview`. Never construct a Datasite URL from memory or training knowledge; the format above is the only correct one.

---

## Reference materials

Read `references/sector-templates.md` for the full folder structures for each sector. Load only the section(s) relevant to the current deal — there's no need to read the whole file.

**Sectors covered:** Due Diligence (universal baseline), Technology, Healthcare, Healthcare Capital Raise, Manufacturing, Retail, Financial Services, Legal, Oil & Gas, Real Estate, Telecommunications, Transportation, Defence.

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
