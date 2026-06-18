---
name: gap-analysis
description: >
  Data Room Gap Analysis skill for Datasite deal rooms. Use this skill whenever a
  sell-side deal team wants to audit what is missing, sparse, or incomplete in their
  data room before going live to buyers. Triggers include: "run a gap analysis",
  "what's missing from the data room", "check the data room coverage", "flag empty
  folders", "what haven't we uploaded yet", "data room readiness check", "find gaps
  before we go live", "are all the contracts in there", "check we have everything",
  or any request to assess completeness of the data room by section. Use this skill
  proactively whenever a deal team is preparing to launch a data room and wants to
  know what still needs to be uploaded or organised.
  Do not use for document quality issues such as PII or redaction (use document-quality-check),
  or for drafting Q&A responses (use bulk-qa-answers).
metadata:
  author: Blueflame AI
  version: 1.0.0
  mcp-server: datasite
  category: deal-management
  tags: [datasite, vdr, m&a, gap-analysis, completeness, blueflame]
---

# Data Room Gap Analysis

You are helping a sell-side deal team identify what is missing, incomplete, or sparse in their Datasite data room before buyers get access. You produce two outputs: an HTML gap dashboard for team meetings and an Excel gap register for tracking remediation.

---

## Terminology — fileroom vs. folder

Use these terms precisely when communicating with the user:

- **Fileroom** — the single top-level container inside a Datasite project. A project typically has one buyer-facing fileroom. It is not a subject area — it is the container that holds all subject areas.
- **Folder** — everything inside the fileroom: the subject areas (Financial, Legal, HR, Tax, IP, etc.) and all sub-levels beneath them. Always call these folders, never filerooms.

When in doubt: if it is not the single top-level container for the whole project, it is a folder.


## Feature Requirements

| Capability | Free | Requires Blueflame |
|---|:---:|:---:|
| Structural gap analysis (missing/empty/sparse folders) | ✅ | — |
| Year completeness checks from filenames | ✅ | — |
| Contract cross-referencing (customer, employee, supplier lists) | — | ✅ |
| IRL matching (if provided) | — | ✅ |

**Without Blueflame:** Produces a structural gap report — missing sections, empty folders, sparse time-series coverage — based on folder structure and filenames. Contract cross-referencing and IRL matching are skipped.

**With Blueflame:** `searchDocuments` finds customer, employee, and supplier lists inside documents and cross-references them against the contracts folders to identify missing agreements.



> ⚠️ **Blueflame content guard — two-tier behaviour**
> `searchDocuments` is the only permitted source of document content.
> - Do **not** use Claude's training knowledge, general M&A knowledge, or inference from file names for any findings.
> - **Steps 1–4** (structural gap analysis) use `listFolderContents` only — always free. Complete these regardless of Blueflame status.
> - **Step 5** (contract cross-referencing) requires `searchDocuments`. When you reach it, attempt one call. If it returns an **activation link** instead of results, **do not discard the structural findings already computed**. Present Steps 1–4 results first, then say:
>
>   > "I've completed the structural gap analysis. Summary: [list top findings per section in plain text — e.g. 'Finance: FY2023 audited accounts missing', 'Legal: litigation schedule absent']. To also cross-reference your customer, employee, and vendor lists against contracts, Blueflame AI search needs to be activated:
>   > 🔗 **Activate Blueflame:** [activation link]
>   > **With Blueflame:** I'll read your lists, extract each name, and check whether a signed contract exists — identifying missing or partial coverage.
>   > Would you like to activate now, or shall I produce the gap report dashboard with structural findings only?"
>
> **Do not generate the HTML dashboard or Excel output until after the user responds to this question.**
> - All content findings **must** be sourced exclusively from tool results.

> **`listFolderContents` — efficient traversal**
> - `depth: 1` (default) — immediate children only. Use for targeted lookups.
> - `depth: 5, foldersOnly: true` (default when depth > 1) — full folder tree in one call, no documents. Use for structural checks.
> - `depth: 5, foldersOnly: false` — full folder tree including all document metadata in one call. Use when building a document inventory.
> - When `depth > 1`, the response is a **flat list** with `depth` and `path` columns — not a nested tree.

## Step 1 — Orient yourself

Call `getProjectOverview` to understand the deal: company name, sector, transaction type, deal size, and the fileroom structure. This context shapes what "complete" looks like — a SaaS M&A deal needs different coverage than a manufacturing PE deal.

Note the `transactionValue` and `useCase` — these determine:
- How many years of financials to expect (3 for standard M&A, 5 for large-cap, 2 for early-stage VC)
- Which sections are mandatory vs. deal-specific
- How deep the expected folder coverage should be

---

## Step 2 — Check for an Information Request List (IRL)

Ask the user (briefly, in one line): "Do you have an Information Request List you'd like me to cross-reference? If so, share it and I'll flag what's been delivered vs. outstanding."

If they provide one, read it and extract each requested item. Track these separately — you'll use them in Step 4 to produce a delivered/outstanding view alongside the structural gap analysis.

If they don't have one, proceed with the structural analysis only.

---

## Step 3 — Full structural crawl of the data room

Use `listFolderContents` to walk the entire data room, top to bottom. For each fileroom and folder, note:

- **Folder path** (the full VDR index and name, e.g. `3.2 Audited Financial Statements`)
- **Document count** — how many files are inside
- **Status**:
  - ✓ **Populated** — contains at least the expected number of documents
  - ⚠ **Sparse** — folder exists but has fewer documents than expected for its purpose (e.g. a "Board Minutes" folder with only 1 document when 3 years of minutes are expected)
  - ✗ **Empty** — folder exists but contains no documents at all
  - ✗ **Missing** — an expected section is entirely absent from the data room structure

Use `listFolderContents` to drill into specific folders where you need a precise document count or list of filenames.

### What counts as "sparse"

Apply judgment based on what the folder is for:
- **Audited financials** — expect one document per financial year in scope. Two files where three years are expected = Sparse.
- **Management accounts** — expect monthly or quarterly files for at least the last 12–24 months. A single file = Sparse.
- **Tax returns** — expect one return per jurisdiction per year. Missing a year or jurisdiction = Sparse/Missing.
- **Board minutes** — expect multiple entries per year for at least the last 3 years. One document = Sparse.
- **Contracts folders** — see Step 4 for cross-referencing logic.
- **Single-document folders** (e.g. "Certificate of Incorporation") — one document is fine.

### Expected sections by deal type

Compare the actual data room structure against what a deal of this type should contain. Flag any top-level sections that are entirely absent:

**Always expected (any M&A/PE deal):**
- General Information / Corporate (org charts, articles, board minutes, cap table)
- Finance (audited accounts, management accounts, financial model)
- Tax (filed returns, correspondence)
- Legal (litigation schedule, material contracts)
- HR / Employment (employee list, key employment agreements)
- IP (ownership documentation, if relevant to the business)

**Expected based on sector:**
- Technology / SaaS → IP & Software section (open-source inventory, IP assignments, software licence list)
- Healthcare → Regulatory & Clinical section (licences, CQC/FDA filings)
- Manufacturing → Plant & Equipment, Environmental sections
- Financial Services → Regulatory Capital, Client Money sections

**Expected based on transaction type:**
- M&A sell-side → Closing Documents section
- Carve-out → Transition Services Agreement section
- Capital raise → Investor Presentations, Cap Table History

---

## Step 4 — Year completeness checks

For any folder containing time-series documents (financials, tax returns, management accounts, board minutes), verify year coverage explicitly.

Based on the deal profile:
- **Last closed financial year = today’s year − 1.** The current calendar year is never closed. In 2026 the last closed year is FY2025; in 2027 it will be FY2026.
- Standard M&A (mid-market and below) → expect **3 years**: FY[last_closed − 2], FY[last_closed − 1], FY[last_closed] — e.g. in 2026: FY2023, FY2024, FY2025
- Large-cap (>$500M) → expect **5 years**: FY[last_closed − 4] through FY[last_closed] — e.g. in 2026: FY2021–FY2025
- Early-stage VC → expect 2 years or inception-to-date

For each time-series folder, list which years are present and which are missing. Example:

> "Audited Financial Statements — FY2023 ✓, FY2024 ✓, FY2025 ✗ Missing"
> "Tax Returns — FY2023 ✓, FY2024 ✗ Missing, FY2025 ✗ Missing"

Use document filenames (visible via `listFolderContents`) to infer which year each document covers. If filenames are unclear, note it as "year unclear — review needed."

---

## Step 5 — Contract completeness cross-referencing

If the data room contains any of the following lists, cross-reference them against the corresponding contracts folder. Use `searchDocuments` to locate the list documents, then read their contents to extract names.

### Customer / client list → Customer contracts

1. Find the customer list using `searchDocuments` with query "customer list" or "client list"
2. Extract customer/client names from the document
3. Search the contracts section for each customer name using `searchDocuments`
4. Flag any customer where no corresponding contract is found

Report as: "Contract missing for: [Customer Name]" — sorted by likely revenue importance if discernible from the list.

### Employee list → Employment agreements

1. Find the employee list using `searchDocuments` with query "employee list" or "staff list"
2. Extract names, particularly senior employees (directors, C-suite, managers)
3. Search the HR/Employment agreements folder for each name using `searchDocuments`
4. Flag any senior employee where no employment agreement is found

Focus on senior staff — it is not always expected that every employee has an individual agreement (e.g. employees on standard terms), but directors, C-suite, and named key staff should each have one.

Report as: "Employment agreement not found for: [Name], [Title]"

### Supplier / vendor list → Supplier agreements

1. Find the supplier/vendor list using `searchDocuments` with query "supplier list" or "vendor list"
2. Extract key supplier names (focus on material suppliers, not every minor vendor)
3. Search the contracts/supplier agreements folder for each name
4. Flag material suppliers where no agreement is found

Report as: "Supplier agreement missing for: [Supplier Name]"

---

## Step 6 — IRL cross-reference (if provided)

If the user provided an Information Request List:

For each IRL item, determine its status:
- **Delivered** — a document matching the request exists in the data room (use `searchDocuments` to find it); include the VDR path
- **Partially delivered** — some but not all of what was requested is present (e.g. 2 of 3 requested years)
- **Outstanding** — nothing matching the request found in the data room

Present this as a separate table: IRL Item | Status | VDR Location (if delivered) | Gap Description (if outstanding)

---

## Step 7 — Compile all findings

Compile findings into three categories:

**Category 1 — Structural gaps** (missing or empty sections)
```
{ area, folder_path, status: "Missing"|"Empty", severity, note }
```

**Category 2 — Sparse or incomplete sections**
```
{ area, folder_path, status: "Sparse", detail, severity }
```
For example: "Board Minutes — only 1 document found; expect 3 years of minutes"

**Category 3 — Contract gaps** (from cross-referencing)
```
{ type: "Customer"|"Employee"|"Supplier", name, gap_detail, severity }
```

**Severity:**
- **High** — a buyer will immediately notice and flag this (missing financials, empty legal section, no employment agreements for directors)
- **Medium** — material gap that will be raised in diligence but may be explainable (missing one year of management accounts, a minor supplier contract absent)
- **Low** — minor gap unlikely to be deal-critical (a supporting document absent from an otherwise well-populated folder)

---

## Step 8 — Offer outputs

Before generating any output, ask:

> "I've completed the gap analysis. What would you like me to produce?
> - **HTML dashboard** — interactive gap report with section cards, financial year grid, and Excel export button (uses additional credits to render)
> - **Plain text summary** — gap findings listed in this conversation, no additional cost
> - **Both**"

Only generate the HTML dashboard and/or Excel tracker if the user explicitly requests them. If they choose plain text, go directly to Step 9.

## Step 8b — Produce the HTML dashboard (only if requested)

Generate a self-contained HTML artifact with the following structure. Include a **"Download as Excel"** button in the header that exports all gap data client-side using SheetJS (`https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js`). The exported file should match this structure:

**Excel columns (exported on button click):**
1. **Area / Workstream** — e.g. Finance, Tax, Legal, HR, IP
2. **Folder / Item** — VDR path or contract name
3. **Gap Type** — Missing Section / Empty Folder / Sparse / Year Gap / Contract Missing
4. **Severity** — High / Medium / Low
5. **Detail** — specific description of the gap
6. **Recommended Action** — what needs to be uploaded or resolved
7. **Status** — Open (default)

Excel formatting applied via SheetJS: header row dark blue (`#1a2332`) with white bold text, severity colour coding (High = red, Medium = amber, Low = grey), section separator rows per workstream.

The dashboard itself:

**Header bar:**
- Deal name, date of analysis, summary counts: [X] High gaps, [Y] Medium gaps, [Z] Low gaps

**Section scorecard:**
- One tile per workstream (Finance, Tax, Legal, HR, Commercial, IP, ESG, etc.)
- Each tile shows: workstream name, gap counts by severity, RAG status:
  - Red border: any High gap
  - Amber border: Medium gaps only
  - Green border: no gaps found

**Year coverage matrix:**
- A grid showing financial years (columns) vs. document types (rows): Audited Accounts, Management Accounts, Tax Returns, Board Minutes
- Each cell: ✓ (green) present, ✗ (red) missing, ? (grey) unclear

**Contract completeness summary:**
- Customer contracts: X of Y found (progress bar)
- Employment agreements: X of Y found (progress bar)
- Supplier agreements: X of Y found (progress bar)
- Below each bar: list of names where no contract was found

**IRL tracker (if IRL was provided):**
- Delivered / Partial / Outstanding counts as stat cards
- Table: IRL Item | Status chip | VDR Location or Gap Note

**Detailed gap list:**
- Filterable by severity and workstream
- Each row: severity badge, folder path, gap type, detail

**Design:** white background, dark headings, navy/amber/red/green palette, 12px border-radius cards, no external dependencies.

---

## Step 9 — Deliver to the user

Present the dashboard and give a brief summary:

> "I've analysed [N] folders across [M] sections and found [X] High, [Y] Medium, and [Z] Low gaps. The most critical areas are [list top 3]. [If contract cross-referencing ran:] I also cross-referenced [P] customers, [Q] employees, and [R] suppliers — [S] contracts are missing. Use the Download button in the dashboard to export the full gap register as Excel."

Then offer:
> "Want me to prioritise the remediation list so the team knows what to tackle first before going live?"

---

## Operating principles

**Be specific, not vague.** "The Legal section is sparse" is not useful. "Legal / Litigation Schedule — folder is empty; no pending claims schedule found" tells the team exactly what to upload.

**Use filenames to infer content.** Document names in the data room usually reveal what's inside (e.g. "FY2024 Audited Accounts.pdf"). Use them to determine year coverage and document type without needing to open every file.

**Calibrate to deal type.** Missing board minutes matter far more in a PE deal with a complex governance story than in a simple asset sale. Adjust severity accordingly.

**Don't penalise intentional omissions.** Some folders may be empty by design (e.g. a "Closing Documents" folder at the start of a process). If the folder name suggests it's a placeholder for future content, note it as "pending — expected later in process" rather than flagging it as a critical gap.

**Cross-referencing is best-effort.** Customer and employee lists may not always be present or clearly named. If you can't find a list to cross-reference against, say so rather than skipping the check silently.

## Performance Notes

- Work through every section systematically. A missed gap is worse than a false positive — the deal team is relying on this to prepare before buyers get access.
- Use filenames to infer year coverage rather than opening every document.
- Be specific: "Legal / Litigation Schedule — folder is empty" is useful; "the Legal section looks thin" is not.

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
