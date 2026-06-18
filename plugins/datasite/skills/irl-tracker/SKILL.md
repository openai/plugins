---
name: irl-tracker
description: >
  Information Request List (IRL) Tracker skill for Datasite deal rooms. Use this
  skill whenever a deal team wants to compare VDR content against a buyer's
  information request list, track document delivery status, or build a due diligence
  tracker dashboard. Triggers include: "map the IRL", "track what's been provided",
  "check the information request list", "information gathering list", "IGL", "what have we delivered", "DD tracker",
  "due diligence tracker", "compare VDR against the request list", "what's still
  outstanding", "build a diligence dashboard", or any request to track document
  delivery against buyer requests. Use proactively whenever a buyer has submitted
  a request list and the deal team needs to manage and track responses.
  Do not use for overall data room structural gap analysis — use gap-analysis for that.
metadata:
  author: Blueflame AI
  version: 1.0.0
  mcp-server: datasite
  category: deal-management
  tags: [datasite, vdr, m&a, irl, due-diligence, tracking, blueflame]
---

# IRL Tracker — Due Diligence Document Tracker

You are helping a deal team map their Datasite data room content against an Information Request List (IRL), assess how well each request is addressed, and produce a live tracking dashboard. The output is a single-file HTML dashboard with no backend required.

---

## Terminology — fileroom vs. folder

Use these terms precisely when communicating with the user:

- **Fileroom** — the single top-level container inside a Datasite project. A project typically has one buyer-facing fileroom. It is not a subject area — it is the container that holds all subject areas.
- **Folder** — everything inside the fileroom: the subject areas (Financial, Legal, HR, Tax, IP, etc.) and all sub-levels beneath them. Always call these folders, never filerooms.

When in doubt: if it is not the single top-level container for the whole project, it is a folder.


## Feature Requirements

| Capability | Free | Requires Blueflame |
|---|:---:|:---:|
| Build document inventory from VDR | ✅ | — |
| Match IRL items to documents semantically | — | ✅ |
| Assess whether document content actually addresses each request | — | ✅ |
| Build HTML tracking dashboard | ✅ | — |

**Without Blueflame:** The skill can build a document inventory and populate the dashboard structure, but cannot match IRL items to documents or assess content relevance. All items will show as Open. The core value of this skill requires Blueflame.

**With Blueflame:** `searchDocuments` semantically matches each IRL requirement to relevant passages in the data room, assigning Available / Partially Complete / Open status with source citations.



> ⚠️ **Blueflame content guard — two-tier behaviour**
> `searchDocuments` is the only permitted source of document content.
> - Do **not** use Claude's training knowledge, general M&A knowledge, or inference from file names for any findings.
> - **Step 3a** (filename and folder matching) is always free. Complete it across all IRL items first.
> - **Steps 3b/3c** (keyword and semantic content search) require `searchDocuments`. Before starting Step 3b, attempt one call. If it returns an **activation link** instead of results, **do not discard Step 3a results**. Present them first, then say:
>
>   > "I've completed filename matching across your [N] IRL items — results above show what I could match by document name and location. To verify that those documents actually address each request (not just exist nearby), Blueflame AI search needs to be activated:
>   > 🔗 **Activate Blueflame:** [activation link]
>   > **With Blueflame:** I'll read inside each document to confirm it covers the right year, entity, or clause — so 'Available' means genuinely addressed, not just 'a file with a matching name exists'. Some items shown as filename-matched may be downgraded or upgraded once content is verified.
>   > Would you like to activate now to complete the content verification?"
>
> - All content findings **must** be sourced exclusively from tool results.

> **`listFolderContents` — efficient traversal**
> - `depth: 1` (default) — immediate children only. Use for targeted lookups.
> - `depth: 5, foldersOnly: true` (default when depth > 1) — full folder tree in one call, no documents. Use for structural checks.
> - `depth: 5, foldersOnly: false` — full folder tree including all document metadata in one call. Use when building a document inventory.
> - When `depth > 1`, the response is a **flat list** with `depth` and `path` columns — not a nested tree.

## Step 1 — Load the IRL

The user provides a spreadsheet or document containing the IRL. Read it and extract for each item:
- **Item ID** (e.g. 1.1, 2.3 — or assign sequentially if not present)
- **Requirement text** — the exact request
- **Section** — the workstream grouping (Finance, Tax, Legal, HR, Commercial, IP, Operations, etc.)
- **Stage** — if the IRL has phases/stages (Stage 1 = initial, Stage 2 = follow-up, Stage 3 = confirmatory). If not present, assign Stage 1 to all items.

If category/section is not in the IRL, infer it from the requirement text using these groupings: Financial Performance, Tax, Legal & Regulatory, Commercial & Customers, HR & Employment, Intellectual Property & Technology, Operations, ESG, Corporate & Governance, Other.

---

## Step 2 — Scan the VDR

Call `getProjectOverview` for deal context. Then call `listFolderContents` with `depth: 5, foldersOnly: false` to build the complete document inventory in a single call. The flat response gives you every document's name, metadata ID, path, file type, status, and page count:
- Document name
- Metadata ID
- Full VDR path (folder index + folder name)
- File size, page count

This is your document inventory. You'll reference it throughout the matching process.


---

## Step 3 — Match each IRL item to VDR documents

For each IRL requirement, find the best matching document(s) in the VDR. Use a layered approach — don't rely on filename alone:

### 3a — File-name & folder matching (free, no Blueflame required)
Before any content search, check whether the document inventory already contains a file whose name or folder path clearly matches the requirement. This step costs zero Blueflame credits.

- Exact or near-exact name match (e.g. IRL asks for "Management Accounts" → file called "Management Accounts Q3 2025.xlsx" in the Finance folder) → provisionally mark **Available (filename match)** at `low` confidence pending content confirmation.
- Folder-level match (e.g. IRL asks for "Employment Contracts" → HR/Employment Contracts folder exists with files) → provisionally mark **Partially Complete (folder match)**.
- No name or folder match → move to content search below.

> If Blueflame is not available, stop here. Complete the filename-matching pass, then proceed to Step 5 to offer the dashboard. If the user confirms, produce it with filename-only matches — clearly label all statuses as **"(filename only — unverified)"** and note that content confirmation requires Blueflame.

### 3b — Keyword search (targeted, lower cost)
Run `searchDocuments` for specific terms in the requirement (dates, entity names, contract parties, regulation names). Keyword search is more targeted than semantic search and should run first to catch exact matches cheaply before triggering a full semantic pass.

### 3c — Semantic search (comprehensive, higher cost)
Run `searchDocuments` with the requirement text (or a distilled version of it) as the query, with `decompose: true` for complex multi-part requests. This returns text passages with document names and page numbers. The passage content confirms whether the document actually addresses the request — not just whether it exists nearby. Only run this step if 3a and 3b did not return a high-confidence match.

### 3d — Content analysis for scattered information
Some requests cannot be satisfied by a single document — the information is distributed. Examples:
- "Customer revenue breakdown" → may require reading invoicing files and aggregating
- "List of all subsidiaries" → may require reading multiple corporate documents
- "Total headcount by location" → may require reading HR files across multiple folders

When this applies, note it explicitly in the source reference: "Information available through analysis of [Doc A] + [Doc B] — not available as a single file."

### 3e — Assess match quality and assign status

For each IRL item, assign one of three statuses based on how well the VDR content addresses the request:

| Status | Meaning | Criteria |
|--------|---------|----------|
| **Available** | Document fully addresses the request | You found a clear, directly responsive document and can cite the relevant passage/page |
| **Partially Complete** | Some but not all of the request is covered | e.g. one tax return found but request covers 3 years; one customer contract found but request asks for the top 10 |
| **Open** | No responsive document found after searching | Neither semantic nor keyword search returned relevant content |

Initial status in the dashboard is set by AI matching:
- Available → displayed as **"Provided (AI)"** (AI found it; human must confirm to become Complete)
- Partially Complete → displayed as **"Provided (AI)"** with lower confidence
- Open → displayed as **"Open"**

Human can then transition:
- Provided (AI) → **Complete** (click "✓ Confirm")
- Provided (AI) → **Open** (click "↩ Reopen")
- Complete → **Provided (AI)** (click "↩ Un-confirm")
- Open → **N/A** (click "Mark N/A")
- N/A → **Open** (click "↩ Reopen")

### 3f — Build the source reference
For each matched document record:
- Filename
- VDR index path (e.g. `3.1 Audited Financial Statements`)
- Page number(s) where relevant content was found
- Confidence: `high` (clear direct match), `med` (probable match), `low` (partial or inferred)
- Source type: `ai_match`

One IRL item can map to multiple documents. One document can satisfy multiple IRL items.

---

## Step 4 — Compile the full mapping table

Produce a structured dataset with one row per IRL item:

```
{
  id: "1.1",
  requirement: "Audited financial statements for the last 3 years",
  section: "Financial Performance",
  stage: 1,
  status: "Provided (AI)",          // Open / Provided (AI) / Complete / N/A
  ai_status: "Partially Complete",   // Available / Partially Complete / Open
  confidence: "med",
  documents: [
    {
      filename: "Apex Ltd - Audited Accounts - FY2024.pdf",
      vdr_path: "3.1 Audited Financial Statements",
      page: 1,
      source: "ai_match"
    }
  ],
  gap_note: "FY2023 and FY2022 not found in data room",
  category: "Financial Performance",
  date_matched: "2026-04-07"
}
```

---

## Step 5 — Offer the dashboard

Before generating the dashboard, ask:

> "I've completed the IRL mapping. Would you like me to generate the full interactive HTML tracking dashboard now? It includes status views, a gap report, and CSV/PDF export — but rendering it will use additional credits. Alternatively I can give you a plain text summary now."

Only build the dashboard if the user confirms. If they decline, go to Step 6 and deliver a plain text summary.

### Dashboard specification (build only on user confirmation)

Generate a single-file, self-contained HTML artifact. No backend, no frameworks. All state via vanilla JS. Use a clean, professional style — white cards, dark navy headings, green/amber/red status colours, subtle borders and shadows.

Status badge colours:
- Open → red
- Provided (AI) → amber
- Complete → green
- N/A → grey

### Layout
- **Fixed header**: project name, search bar (filters across all requirements), Export CSV button, PDF Report button
- **Fixed left sidebar**: navigation links to each of the 7 views, section list with open-item counts
- **Main content area**: right of sidebar, scrollable

### Completion calculation
- **Overall %** = (Complete + N/A) / Total × 100
- "Provided (AI)" does NOT count toward completion — only human-confirmed items do

---

### View 1 — Status Dashboard (default)

- **Donut/ring chart** showing overall completion %
- **4 status pills**: Open (count), Provided AI (count), Complete (count), N/A (count)
- **Stage overview row**: 3 cards for Stage 1 / 2 / 3, each with count, progress bar, completion %
- **Section cards grid**: one card per section with stacked progress bar (complete + provided + n/a + open) and counts
- **"Confirm All" button** per section — marks all Provided (AI) items in that section as Complete in one click

---

### View 2 — Master Tracker

- Full table of all requirements with sortable columns:
  `ID | Requirement | Category | Stage | Status (badge) | Documents Provided (filenames with confidence dots) | Date Matched`
- Click column headers to sort ascending/descending
- Filter bar: Status dropdown, Section dropdown, Stage dropdown, free-text search
- Shows "X of Y requirements" count
- **"Confirm All"** button — marks all currently visible Provided (AI) items as Complete
- Each row expandable to show full document list with VDR paths and page numbers

---

### View 3 — Coverage Heatmap

- Grid of section tiles, colour-coded by completion %:
  - ≥80% → green | 50–79% → amber | <50% → red
  - Background fill height = % provided (including AI-matched)
- **Integrated Gap Report** below the grid: grouped by Stage, listing every Open item with ID, requirement text, and section

---

### View 4 — IRL by Section

- Section card grid → click to drill into a section
- **Section detail view**: section header with item count, filter bar, and all requirements as document item cards
- Each card shows: ID, requirement text, status badge, matched documents with confidence dots, gap note if Partially Complete
- Upload zone per card: drag-drop to add a document manually (stores filename + metadata only, not binary)
- **"Confirm All"** button per section

---

### View 5 — IRL by Stage

- 3 stage tabs at top (Stage 1 / Stage 2 / Stage 3) with counts
- Filter bar + document item cards for the selected stage
- **"Confirm All"** button per stage — marks all Provided (AI) items in the stage as Complete

---

### View 6 — Gap Analysis

- **3 gap cards**: Critical (Stage 1 Open), Moderate (Stage 2 Open), Low (Stage 3 Open) — with counts
- Section-by-section rows: progress bar, completion %, stage breakdown badges, open count
- Drill-down per section showing individual open items with requirement text and gap note

---

### View 7 — Document Index

Full list of all VDR documents scanned, with:
- VDR index number
- Document name
- IRL item ID(s) it addresses (can be multiple)
- Status of those IRL items

Sorted by VDR index. Filterable by section and status.

---

### Export: CSV

Button in header → downloads `DD_Tracker_[ProjectName]_[YYYY-MM-DD].csv` with columns:
`Item ID, Requirement, Category, Stage, Status, Files Uploaded, Confidence, Date Matched`

---

### Export: PDF Report

Button in header → opens new window with print-ready HTML, triggers `window.print()`:

- **Header**: "Due Diligence Tracker Report" + deal name + generation date
- **Executive summary**: 4 status cards (Open / Provided AI / Complete / N/A) + overall completion %
- **Section overview table**: Section | Open | Provided | Complete | N/A | %
- **Per-section detail tables** (with page breaks between sections): ID | Requirement | Stage | Status badge | Documents Provided
- **Footer**: "Due Diligence Tracker | Confidential | [date]"
- Print CSS: `@page { size: A4; margin: 20mm }`, hide sidebar/header, show only report content

---

## Step 6 — Deliver to the user

After rendering the dashboard, summarise:

> "I've mapped **[N] IRL items** against the data room. **[X] are Available** (matched with high/med confidence), **[Y] are Partially Complete**, and **[Z] are Open** with no document found. Overall AI-assisted coverage: **[%]**.
>
> Use ✓ Confirm to validate AI matches and move items to Complete. The dashboard tracks completion in real time — only human-confirmed items count toward overall progress."

---

## Operating principles

**Content beats filename.** A document called `Q4_Report.pdf` in the Finance folder might satisfy an IRL request for management accounts — or it might not. Always use `searchDocuments` to read the content before marking as Available.

**One document, many requests.** The same audited accounts file might satisfy the request for "annual financials", "revenue figures", "EBITDA history", and "depreciation policy" simultaneously. Map it to all relevant items.

**Partial is honest.** If a request asks for 3 years of tax returns and you found 2, mark it Partially Complete and note the gap. Don't mark it Available — the buyer will notice.

**AI matches are provisional.** Every item starts as "Provided (AI)" at best. The deal team's confirmation step is what makes it Complete. This distinction is important — it protects the deal team from inadvertently representing incomplete coverage as confirmed.

**Store metadata, not binaries.** The dashboard stores filenames, paths, confidence scores, and timestamps — not the actual file content. This keeps the HTML lightweight and shareable.

## Performance Notes

- **Accurate status is more valuable than high completion percentages.** Mark items Partially Complete or Open rather than stretching a weak match to Available.
- Content beats filename — always use `searchDocuments` to confirm a document actually addresses the request before marking Available.
- AI matches are provisional by design. The deal team's confirmation step is what makes an item Complete.

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
