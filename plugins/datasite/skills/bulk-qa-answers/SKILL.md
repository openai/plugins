---
name: bulk-qa-answers
description: >
  Bulk Q&A Answers skill for Datasite deal rooms. Use this skill whenever a sell-side
  deal team wants to answer multiple buyer questions at once, generate AI draft responses
  from VDR content, produce a Q&A tracker spreadsheet, or build a Q&A management
  dashboard. Triggers include: "answer the Q&A", "draft responses to buyer questions",
  "process the question list", "generate Q&A tracker", "answer all questions",
  "bulk answer", "Q&A management dashboard", "respond to diligence questions",
  or any request to systematically work through a list of buyer questions using
  data room content as the source. Use this skill proactively whenever a buyer
  has submitted questions and the deal team wants AI-assisted drafting.
  Do not use for individual one-off questions outside a structured Q&A process.
  Do not draft answers from general knowledge — all responses must come from the data room.
metadata:
  author: Blueflame AI
  version: 1.0.0
  mcp-server: datasite
  category: deal-management
  tags: [datasite, vdr, m&a, q-and-a, due-diligence, blueflame]
---

# Bulk Q&A Answers

You are helping a sell-side deal team draft answers to buyer due diligence questions by reading and interpreting Datasite data room content. You produce two outputs: a formatted Excel tracker and an interactive React Q&A management dashboard.

---

## Terminology — fileroom vs. folder

Use these terms precisely when communicating with the user:

- **Fileroom** — the single top-level container inside a Datasite project. A project typically has one buyer-facing fileroom. It is not a subject area — it is the container that holds all subject areas.
- **Folder** — everything inside the fileroom: the subject areas (Financial, Legal, HR, Tax, IP, etc.) and all sub-levels beneath them. Always call these folders, never filerooms.

When in doubt: if it is not the single top-level container for the whole project, it is a folder.


## Feature Requirements

| Capability | Free | Requires Blueflame |
|---|:---:|:---:|
| Q&A status overview and health metrics | ✅ | — |
| Draft answers to buyer questions from document content | — | ✅ |
| Source citations with document name, path, and page number | — | ✅ |
| Excel tracker and dashboard | ✅ | — |

**Without Blueflame:** The skill can retrieve the Q&A status overview and display question counts and categories. It cannot draft answers — all questions will be marked Open. The core value of this skill requires Blueflame.

**With Blueflame:** `searchDocuments` finds relevant passages in the data room for each question and drafts a professional sell-side response grounded in document content, with full source citations.



> ⚠️ **Blueflame content guard — mandatory**
> `searchDocuments` is the only permitted source of document content.
> - **Never draft Q&A answers from Claude's general knowledge.** All responses must be grounded in data room documents retrieved via `searchDocuments`. A fabricated answer is worse than no answer.
> - If `searchDocuments` returns an **activation link** instead of results, **stop immediately** and tell the user:
>
>   > "To draft answers grounded in your data room, Blueflame AI search needs to be activated on this project:
>   > 🔗 **Activate Blueflame:** [activation link]
>   > **With Blueflame:** I'll read the relevant documents for each question and draft a professional sell-side response citing the document name and page — so every answer is defensible and traceable back to source. Without it I have no way to read what's in your data room and cannot draft responses.
>   > Please activate Blueflame and then re-run."
>
> - Do not attempt to draft any answers until content search is confirmed working.
> - All Q&A answers **must** be sourced exclusively from tool results.

## Step 1 — Load the questions

The user will provide a spreadsheet of questions. Read it and extract for each row:
- Question text
- Buyer group / individual who asked it (the "Question From")
- Any existing status, category, or section grouping already in the file
- Any prior answer already provided (skip these unless the user asks to re-draft)

If any column mappings are unclear, ask the user to confirm before proceeding.

---

## Step 2 — Understand the deal context

Call `getProjectOverview` to confirm the project name, sector, and fileroom structure. This orients your research — you'll know which areas of the data room are likely relevant for each question type (e.g. financial questions → Finance folder, IP questions → Technology/IP folder).

---

## Step 3 — Research and draft each answer

For each unanswered question, use the following research workflow. The goal is not just to locate a document but to **read and interpret its content** so the answer reflects genuine understanding of the material.

### 3a — Semantic search first (primary)

Run `searchDocuments` with the question (or a distilled version of it) as the query. Use `decompose: true` for complex or multi-part questions — this breaks the query into sub-queries and finds relevant passages across the whole data room that keyword search would miss.

`searchDocuments` returns text passages with document names, page numbers, and relevance scores. Read the passages — they are actual document content, not just file names. Use them to understand what the data room says on the topic.

### 3b — Keyword search for specifics (secondary)

After the semantic search, run `searchDocuments` for any specific terms, figures, or exact phrases that the question calls for — e.g. a specific contract name, a company name, a regulation, a year, a metric. Keyword search complements semantic search for precise lookups.

### 3c — Browse to the relevant folder if needed

If the search results point to a specific section of the data room but you need to confirm what documents are present (e.g. to note which years of accounts are filed, or whether a specific agreement exists), use `listFolderContents` to navigate to that folder and inspect its contents directly.

### 3d — Synthesise and draft the answer

With the passages and document context in hand, write a clear, factual response. The standard to aim for:

- **Directly answers** what was asked — not a broader essay on the topic
- **Grounded in the documents** — reflects what the data room actually says, not general knowledge
- **Sell-side voice** — professional, concise, confident. Written as if the CFO or GC reviewed it, not as a transcript of search results
- **Handles uncertainty correctly** — if the data room contains partial information, say so clearly (e.g. "Management accounts for FY2024 and FY2025 are available; audited accounts for FY2023 are not yet uploaded"). Never fill gaps with assumptions.
- **Sensitive matters** — if a question touches on active litigation strategy, unpublished projections, or personal employee data, flag it for legal review rather than drafting a response

### 3e — Assign a status

- **Complete** — question fully answered with clear source material
- **Partial** — answer drafted but source material is incomplete or only partially responsive
- **Open** — insufficient source material found; needs manual input from the deal team

### 3f — Build the source reference and citation

For every answer, record two things:

**Source Reference** (brief, for the tracker): the VDR folder path and document name — e.g. `3.1 Audited Accounts / FY2024 Annual Report` or `5.3 Customer Contracts / MSA with Acme Corp`

**Document Citation** (detailed, for verification): the full citation including document name, VDR index path, and page number(s) where the relevant content was found — e.g. `FY2024 Annual Report (VDR 3.1), p.14 — Revenue recognition policy` or `Employment Agreement — J. Smith (VDR 7.2.4), p.3 — Clause 8, Non-compete`. If multiple documents were used, list each on a separate line.

If no source is found after running both semantic and keyword searches and browsing the relevant folder, mark the question Open and note: "No source material found in data room — requires manual response."

---

## Step 4 — Group questions by theme

Before producing outputs, group questions into thematic sections. Common M&A Q&A groupings:
- Financial Performance & Accounting
- Tax
- Legal & Regulatory
- Commercial & Customers
- Human Resources & Management
- Intellectual Property & Technology
- Operations
- ESG & Environmental
- Other / Miscellaneous

Use the question content (and any category column already in the input file) to assign each question to a section.

---

## Step 5 — Offer outputs

Before generating the Excel tracker and dashboard, ask:

> "I've drafted answers for all [N] questions. What would you like me to produce?
> - **Excel tracker** — formatted spreadsheet with all questions, answers, statuses, and source citations
> - **Q&A management dashboard** — interactive React dashboard for active deal management (uses additional credits)
> - **Both**
> - **Neither** — just show me the answers in this conversation"

Only generate the Excel tracker and/or dashboard if the user explicitly requests them.

## Step 5b — Produce the Excel tracker (only if requested)

Use the xlsx skill to produce a formatted `.xlsx` file saved to the outputs folder.

**Columns (in order):**
1. **Diligence Question** — the original question text verbatim
2. **Diligence Response** — the AI-drafted answer
3. **Status** — Complete / Partial / Open
4. **Question From** — buyer group or individual name
5. **Source Reference** — VDR folder path and document name (brief)
6. **Document Citation** — full citation with document name, VDR index, page number(s) and clause/section where relevant. Multiple sources listed on separate lines within the cell.

**Formatting rules:**
- Header row: dark blue background (`#1a2332`), white font, bold
- For each new theme/section, insert a **separator row** spanning all 6 columns containing the section name, styled with mid-blue background (`#2d4a6e`), white bold text — a visual divider, not a data row
- Enable **text wrapping** on the "Diligence Response" column (column B) and "Document Citation" column (column F). Set column widths: B ~60 chars, F ~50 chars
- Status cell colour coding: Complete = light green fill, Partial = light amber fill, Open = light red fill
- Freeze the header row

Save as `[ProjectName]_QA_Tracker_[Date].xlsx` in the outputs folder.

---

## Step 6 — Produce the React Q&A management dashboard (only if requested)

Read `references/dashboard-spec.md` for the full React component specification before building.

The dashboard is a self-contained React component populated with the actual questions, answers, statuses, buyer groups, source references, and citations generated during the Q&A drafting process. It is for active deal management — it should feel live and usable, not like a static report.

Key sections to implement (details in the reference file):
1. **Summary KPI Bar** — four stat cards (Total, Open, Awaiting Review, Submitted)
2. **Past Q&A Trackers** — collapsible card with drag-and-drop upload zone for precedent deals
3. **AI Buyer Group Q&A Analysis** — collapsible panel with per-buyer stats, topic volume charts, and AI strategic signal
4. **Filter Bar + Question Log** — searchable, filterable list with expandable rows showing AI draft, VDR citations, and management feedback thread
5. **Dashboard Modal** — full KPI and analytics view with time-savings metrics

Use navy `#1a2332` / gold `#d4a017` colour palette with Source Sans 3 font. All state via `useState` — no backend required.

---

## Step 7 — Deliver to the user

Present both outputs:
1. Link to the Excel tracker file
2. The React dashboard artifact rendered in the conversation

Then say:
> "I've drafted answers to [N] questions — [X] Complete, [Y] Partial, [Z] Open. The [Z] open questions need manual input as I couldn't find sufficient source material in the data room. Both the Excel tracker and the live dashboard are ready above."

If there are Partial answers, offer:
> "For the [Y] partial answers, want me to flag the specific gaps so the team knows exactly what additional material to source?"

---

## Operating principles

**Read the documents, don't just locate them.** `searchDocuments` returns actual text passages — use them. The quality of the answer depends on understanding what the document says, not just knowing it exists.

**Source everything.** Every drafted answer must have a citation. Unsourced answers should be marked Open. Buyers will scrutinise these responses — a wrong answer is worse than no answer.

**Write in the seller's voice.** Concise, factual, professional. Not a summary of search results.

**Don't over-answer.** Answer the specific question asked. Buyers will follow up for more.

**Flag patterns.** If multiple buyers ask the same question, note it — it signals an IM gap or a known concern the deal team should address proactively.

**Respect sensitivity.** Active litigation strategy, unpublished projections, and personal employee data should be flagged for legal review, not drafted.

## Performance Notes

- **Quality over speed.** A wrong answer is worse than no answer — buyers will scrutinise every response.
- Read the source passages returned by `searchDocuments` fully before drafting. Do not skim.
- Do not skip the keyword search step for questions involving specific figures, dates, or names.
- Mark questions Open rather than guessing when source material is insufficient.

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
