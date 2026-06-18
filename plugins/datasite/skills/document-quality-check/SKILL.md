---
name: document-quality-check
description: >
  Document Quality Check skill for Datasite deal rooms. Use this skill whenever a
  deal team wants to audit document quality before going live to buyers. Triggers
  include: "check document quality", "flag bad documents", "find password protected
  files", "check for blank documents", "PII check", "redaction review", "find
  corrupted files", "document audit", "quality check the data room", "are there
  any blank or broken files", "check for unredacted personal data", or any request
  to verify that documents in the data room are complete, accessible, and safe to
  share. Use this skill proactively before a data room goes live.
  Do not use for renaming files (use smart-file-renaming) or for identifying
  missing sections (use gap-analysis).
metadata:
  author: Blueflame AI
  version: 1.0.0
  mcp-server: datasite
  category: deal-management
  tags: [datasite, vdr, m&a, document-quality, pii, redaction, blueflame]
---

# Document Quality Check

You are helping a deal team verify that every document in their Datasite data room is fit to share with buyers before going live. You check for six categories of quality issues and produce an HTML dashboard with a downloadable Excel report.

---

## Terminology — fileroom vs. folder

Use these terms precisely when communicating with the user:

- **Fileroom** — the single top-level container inside a Datasite project. A project typically has one buyer-facing fileroom. It is not a subject area — it is the container that holds all subject areas.
- **Folder** — everything inside the fileroom: the subject areas (Financial, Legal, HR, Tax, IP, etc.) and all sub-levels beneath them. Always call these folders, never filerooms.

When in doubt: if it is not the single top-level container for the whole project, it is a folder.


## Feature Requirements

| Capability | Free | Requires Blueflame |
|---|:---:|:---:|
| Failed / unprocessable files (status metadata) | ✅ | — |
| Placeholder and stub documents (type metadata) | ✅ | — |
| Wrong file formats (fileType metadata) | ✅ | — |
| Uninformative filenames (name pattern matching) | ✅ | — |
| Version conflicts (name pattern matching) | ✅ | — |
| Duplicate documents (name + metadata comparison) | ✅ | — |
| Stale documents (upload date metadata) | ✅ | — |
| PII exposure in document content | — | ✅ |
| Redaction quality check | — | ✅ |
| Broken references and missing exhibits | — | ✅ |

**Without Blueflame:** 7 of 10 checks run fully using `listFolderContents` metadata. The three content-level checks (PII, redaction quality, broken references) are skipped — note these in the report as "Requires Blueflame."

**With Blueflame:** All 10 checks run. `searchDocuments` scans document content for PII patterns, verifies redaction quality, and finds broken cross-references inside documents.



> ⚠️ **Blueflame fallback — two-tier behaviour**
> `searchDocuments` is the only permitted source of document content.
> - Do **not** infer document content, PII presence, or redaction quality from Claude’s training knowledge.
> - **Phase A** (Checks 1–7, metadata checks) uses `listFolderContents` only — always free. Complete Phase A fully first.
> - **Phase B** (Checks 8–10: PII scan, redaction quality, broken references) requires `searchDocuments`. When you reach Phase B, attempt one call. If it returns an **activation link** instead of results:
>   1. **Do not generate the HTML dashboard yet** — ask the Blueflame question first as a plain conversational message
>   2. Summarise Phase A findings in plain text (e.g. "I found X password-protected files, Y duplicates, Z files with no extension")
>   3. Then ask:
>
>   > "I’ve completed the 7 metadata checks — here’s what I found: [plain text summary]. To also run PII scanning, redaction quality checks, and broken reference detection, Blueflame AI search needs to be activated on this project:
>   > 🔗 **Activate Blueflame:** [activation link]
>   > **With Blueflame:** I’ll scan document content for exposed personal data (names, NI numbers, bank details), verify that redacted text can’t be read in the file layer, and check for broken cross-references inside documents — the checks buyers and their lawyers look for most.
>   > Would you like to activate now, or shall I produce the dashboard with the Phase A findings only?"
>
>   4. **Wait for the user’s response before producing any dashboard or output file.**
>
> Do not embed the Blueflame activation prompt inside the HTML dashboard — it must appear as an interactive conversational question before any output is generated.

> **`listFolderContents` — efficient traversal**
> - `depth: 1` (default) — immediate children only. Use for targeted lookups.
> - `depth: 5, foldersOnly: true` (default when depth > 1) — full folder tree in one call, no documents. Use for structural checks.
> - `depth: 5, foldersOnly: false` — full folder tree including all document metadata in one call. Use when building a document inventory.
> - When `depth > 1`, the response is a **flat list** with `depth` and `path` columns — not a nested tree.

## Step 1 — Orient yourself

Call `getProjectOverview` to understand the project structure and get a list of all filerooms. You'll work through each fileroom systematically.

---

## Step 2 — Run all quality checks

Work through each check below in two phases:

**Phase A — Metadata checks (use `listFolderContents`):**
Call `listFolderContents` without a metadataId to get all filerooms, then recurse into each folder to build a complete document inventory. Each document entry includes: name, type (DOCUMENT/PLACEHOLDER/FOLDER/FILE_ROOM/SANDBOX), status (DONE/FAILED/PROCESSING), fileType (pdf/docx/xlsx etc.), publishingState, and upload date. Use this single inventory pass to run all metadata-based checks — do not make a separate call per check.

From the inventory, flag:
- `status: FAILED` or `PROCESSING` → Check 1 (unprocessable)
- `type: PLACEHOLDER` → Check 6 (placeholder/stub)
- `fileType` in [xlsm, xlsb, zip, rar, msg, eml, pages, numbers, key, dwg] → Check 9 (wrong format)
- Name patterns: Scan/IMG/Document/Untitled/Copy of/FINAL_FINAL/USE THIS/DO NOT USE → Check 12 (bad filenames)
- Name patterns: v1/v2/revised/updated/superseded/old/archive → Check 8 (version conflicts)
- Identical names in the same folder → Check 7 (duplicates)
- Upload date > 12 months ago in active sections (Management Accounts, Insurance, Licences) → Check 10 (stale)

**Phase B — Content checks (use `searchDocuments`):**
Use `searchDocuments` for checks requiring reading inside documents (PII, redaction quality, broken references). Always call `searchDocuments` — if AI search is not yet activated the tool returns an activation link; present it to the user rather than skipping the check.

---

### Check 1 — Failed / unprocessable documents
*Catches: password-protected files, corrupted files, files that couldn't be indexed*

```
listFolderContents(projectId, query="*", filter=["status:EQ:FAILED", "type:EQ:DOCUMENT"])
listFolderContents(projectId, query="*", filter=["status:EQ:PROCESSING", "type:EQ:DOCUMENT"])
```

`FAILED` = Datasite could not process the file — most commonly because it is password-protected or corrupted. `PROCESSING` documents that have been in that state for more than a few minutes are likely stuck (possible corruption or unsupported format).

For each result note: filename, VDR folder path, file size, extension.

**Severity:** High — buyers cannot open these documents.

---

### Check 2 — Blank or near-blank documents
*Catches: accidentally uploaded blank pages, empty documents, placeholder files*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "pageCount:LT:2", "fileSize:LT:50000"])
```

A document with fewer than 2 pages AND under 50KB is almost certainly blank or a single near-empty page. Cross-reference against the folder context — a 1-page certificate of incorporation is fine; a 1-page "FY2024 Audited Accounts" is not.

Also flag zero-byte files:
```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "fileSize:LT:1000"])
```

For each result, check the filename and folder path to judge whether the low page count is expected. Flag only where it looks wrong for the document type.

**Severity:** High (if it's a material document), Medium (if it's a supporting file).

---

### Check 3 — Suspicious redaction quality (poorly blacklined documents)
*Catches: documents with redactions that may be incomplete or incorrectly applied*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "redacted:EQ:true"])
```

This returns all documents Datasite has flagged as containing redactions. For each one, use `searchDocuments` to check whether sensitive content that should have been redacted is still readable — e.g. if a document is flagged as redacted but the underlying text was not properly removed (a common issue with image-based PDFs where black boxes are overlaid on text that remains in the file layer).

Search queries to run on redacted documents:
- `searchDocuments` with query "salary" or "compensation" — check for unredacted pay figures
- `searchDocuments` with query "date of birth" or "national insurance" — check for unredacted personal identifiers
- `searchDocuments` with query "account number" or "IBAN" — check for unredacted banking details

Flag any redacted document where searchable text appears beneath the redaction, or where the expected content is still visible in snippets.

Also flag documents where the filename suggests redaction was needed (e.g. "Employment Agreements", "Payroll", "Personal Data") but `redacted:EQ:false` — these may have been shared without any redaction applied.

**Severity:** High — unredacted personal or sensitive data in a buyer-facing data room is a GDPR/privacy breach.

---

### Check 4 — PII exposed without redaction
*Catches: personal data visible in documents that haven't been redacted at all*

Run the following `searchDocuments` queries across the full data room. Each targets a specific PII category. Read the snippets returned and flag any document where personal data is clearly visible.

**Personal identifiers:**
- `"date of birth"` or `"DOB"` or `"born on"` — personal birth dates
- `"passport number"` or `"passport no"` — passport identifiers
- `"national insurance"` or `"NI number"` or `"social security"` or `"SSN"` — government ID numbers
- `"home address"` or `"residential address"` — personal addresses (distinguish from business addresses)
- `"driving licence"` or `"driver's license number"` — licence identifiers

**Financial details:**
- `"sort code"` and `"account number"` — personal bank account details
- `"IBAN"` — international bank account numbers
- `"salary"` with a named individual — personal salary data linked to a person's name
- `"payslip"` or `"pay stub"` — payroll documents that typically contain personal financial data

**Contact data:**
- Search for personal email domain patterns: `"@gmail.com"` or `"@yahoo.com"` or `"@hotmail.com"` or `"@icloud.com"` — personal email addresses (business emails like @companyname.com are expected and fine)
- `"mobile"` or `"personal phone"` alongside a person's name — personal phone numbers

For each snippet returned, assess whether it appears in a context that warrants redaction (e.g. an employee's salary in a payroll schedule = High risk; a reference to "date of birth required for background check" in an HR policy = Low risk).

**Severity:** High for direct identifiers (passport, NI/SSN, bank account); Medium for contact data and salary where it's incidental.

---

### Check 5 — Suspiciously small or potentially incomplete scanned documents
*Catches: multi-page documents where pages may be missing*

For scanned documents (PDFs from physical paper), page count alone can reveal gaps. Use:
```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:pdf"], sort=["pageCount,ASC"])
```

Cross-reference page count against what's expected based on document type and filename:
- A "Lease Agreement" with 2 pages is suspicious — commercial leases are typically 20–100 pages
- An "Employment Agreement" with 1 page is suspicious — these typically run 5–30 pages
- An "Audited Financial Statements" document with 3 pages is suspicious — audited accounts are typically 30–100+ pages
- A "Certificate of Incorporation" with 1–2 pages is fine

Flag documents where the page count appears materially below what the document type would normally require. Note the filename, VDR path, current page count, and the expected range.

**Severity:** Medium — missing pages may mean incomplete disclosure. High if it's a key legal or financial document.

---

### Check 6 — Placeholder or stub documents
*Catches: files named as placeholders, zero-content uploads, "TBC" files*

```
listFolderContents(projectId, query="placeholder", filter=["type:EQ:DOCUMENT"])
listFolderContents(projectId, query="TBC", filter=["type:EQ:DOCUMENT"])
listFolderContents(projectId, query="draft", filter=["type:EQ:DOCUMENT"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:placeholder"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:TBC"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:WIP"])
```

Also check for documents with generic names that suggest they haven't been properly named or are still in progress: "Document1", "Untitled", "Copy of", "v1", "DRAFT", "temp".

**Severity:** Medium — placeholder documents signal incomplete preparation; buyers will notice.

---

### Check 7 — Duplicate documents
*Catches: exact or near-duplicate files that inflate apparent completeness and expose version inconsistencies*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT"], sort=["fileSize,ASC"])
```

Group results by file size. Where two or more documents share the same `fileSize`, compare their filenames. Exact file size match + near-identical filename = likely duplicate. Also flag same `pageCount` + same folder path with minor filename variation (e.g. `Agreement_v1.pdf` and `Agreement_final.pdf` in the same folder).

For suspected duplicates in high-risk areas (financial statements, contracts), run `searchDocuments` on both documents to compare leading paragraphs — if content is near-identical, flag as a confirmed duplicate.

Highest risk: duplicate financial statements or contracts where versions may differ in a key figure or clause.

**Severity:** High (if material documents like contracts or financials are duplicated with differing content), Medium (identical duplicates — one just needs removing).

---

### Check 8 — Version conflicts and superseded documents
*Catches: old or draft versions left in the room alongside current ones, which buyers may read and draw incorrect conclusions from*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:v1"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:revised"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:updated"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:superseded"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:previous"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:archive"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:old"])
```

Also search for: `"v2"`, `"final"`, `"draft"` in filenames. Where multiple versions exist in the same folder, flag all but the most recently modified (`sort: availableDate,DESC`) as potentially superseded.

Cross-reference `availableDate` against document content date where visible — a file uploaded in 2026 but containing a 2023 date header warrants flagging.

**Severity:** High (if two versions of a contract or financial statement coexist with potentially different terms or figures), Medium (clear drafts or superseded copies that are obviously not current).

---

### Check 9 — Wrong file format or rendering risk
*Catches: files that buyers cannot open in-browser, macro-enabled files (security risk), and archive files that block search indexing*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:msg"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:eml"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:xlsm"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:xlsb"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:zip"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:rar"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:dwg"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:pages"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:numbers"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "extension:EQ:key"])
```

Flag each by issue type:
- `.xlsm` / `.xlsb` → macro-enabled Excel — security risk for buyers, may be blocked by corporate IT; recommend saving as `.xlsx`
- `.zip` / `.rar` → archive files — content invisible to VDR search indexing, buyers cannot open in-browser; recommend unpacking and uploading individual files
- `.msg` / `.eml` → email files — rarely intentional, likely contain unintended PII or privileged content; recommend converting to PDF
- `.dwg` / `.dxf` → CAD files — buyers without AutoCAD cannot open; recommend PDF export
- `.pages` / `.numbers` / `.key` → Apple-native formats — Windows users (most buyers) cannot open; recommend PDF or Office format

**Severity:** High for `.msg`/`.eml` (PII/privilege risk) and `.zip` (invisible to search), Medium for rendering-incompatible formats.

---

### Check 10 — Stale or outdated documents
*Catches: documents that appear current but haven't been updated in over a year, particularly in areas where buyers expect current data*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "availableDate:LT:[12_months_ago_epoch]"], sort=["availableDate,ASC"])
```

Calculate the epoch timestamp for 12 months ago from today's date and substitute it into the filter. From the results, focus on document types where staleness is a material risk:
- Management accounts — must be current; flagging anything older than 3 months
- Financial models and projections — flag if older than 6 months
- Employee lists and org charts — flag if older than 12 months
- Insurance schedules — flag if upload date is older than 12 months (policy may have expired)
- Regulatory licences and certificates — flag if older than 12 months (renewal may be overdue)
- Board minutes — flag if the most recent entry is older than 6 months

Don't flag inherently historical documents (e.g. FY2022 audited accounts — they're supposed to be from 2022).

**Severity:** High (management accounts, insurance, regulatory licences past renewal date), Medium (financial models, employee lists).

---

### Check 11 — Broken references and missing linked content
*Catches: documents referencing exhibits, appendices, or schedules that were never uploaded — buyers encounter dead ends*

Use `searchDocuments` with the following queries:

- `"see attached"` or `"refer to appendix"` or `"as per schedule"` — cross-reference whether the referenced exhibit exists in the same folder
- `"exhibit"` or `"annex"` or `"schedule"` — check whether named attachments are present
- `"[TBC]"` or `"[insert"` or `"[link]"` or `"[see tab"` — internal authoring placeholders never resolved before upload
- `"see accompanying"` or `"as set out in"` or `"detailed in the attached"` — general cross-reference language

For each match, check whether the referenced document is present in the same folder using `listFolderContents`. Flag where it is absent.

For Excel financial models specifically: if a CIM or management presentation references a "detailed financial model" and the only Excel file in the folder has `fileSize:LT:100000`, it is likely a stub or broken-link version — flag for review.

**Severity:** High (missing exhibit to a contract, missing appendix to audited accounts), Medium (unresolved placeholder text).

---

### Check 12 — Uninformative or unprofessional filenames
*Catches: filenames that signal poor preparation and make navigation impossible for buyers — a direct reputational risk*

```
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:Scan"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:Document"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:Copy of"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:FINAL_FINAL"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:USE THIS"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:DO NOT USE"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:Untitled"])
listFolderContents(projectId, query="*", filter=["type:EQ:DOCUMENT", "name:LIKE:New "])
```

Also flag:
- Files with sequential numbering in the name: match patterns like `001`, `002`, `(1)`, `(2)`, `(3)`
- Files with double extensions: `.pdf.pdf`, `.docx.pdf` — artefacts of bulk upload tools
- Any folder where more than 20% of filenames match these generic patterns — flag the entire folder for a renaming pass, not just individual files

**Severity:** Medium across the board — these don't block access but signal poor preparation to buyers. Flag the folder-level pattern as more severe than individual files.

---

## Step 3 — Compile findings

Compile all findings into a structured list:

```
findings = [
  {
    check: "Failed / Unprocessable",
    severity: "High",
    filename: "FY2024 Audited Accounts.pdf",
    folder: "3.1 Audited Financial Statements",
    detail: "Document status is FAILED — likely password-protected or corrupted. Buyers cannot open it.",
    recommended_action: "Remove password protection or re-export as an unprotected PDF and re-upload."
  },
  ...
]
```

Count issues by severity and check type for the dashboard scorecard.

---

## Step 4 — Offer the dashboard

Before generating anything, ask:

> "I've completed the quality checks. Would you like me to produce the HTML dashboard with the full findings and an Excel export? It uses additional credits to render. Alternatively I can give you a plain text summary here."

Only generate the dashboard if the user confirms. If they decline, go to Step 5 and deliver a plain text summary.

## Step 4b — Produce the HTML dashboard (only if requested)

Generate a self-contained HTML artifact. Include a **"Download as Excel"** button using SheetJS (`https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js`) that exports the findings table with columns: Check Type | Severity | Filename | VDR Folder | Detail | Recommended Action | Status (default: Open).

**Dashboard structure:**

**Header:**
- Deal name, date of audit, total issue counts by severity (High / Medium / Low)
- "Download as Excel" button (navy, top right)

**Summary scorecard — six check tiles:**
One tile per check type, each showing:
- Check name and icon
- Issue count
- RAG status: Red (any High issue), Amber (Medium only), Green (no issues)

Check tiles:
- 🔒 Failed / Unprocessable
- 📄 Blank / Near-blank
- ✂️ Redaction Quality
- 👤 PII Exposed
- 📑 Incomplete Scans
- 📝 Placeholders / Stubs
- 👯 Duplicate Documents
- 🔁 Version Conflicts
- ⚠️ Wrong Format / Rendering Risk
- 🕐 Stale / Outdated Documents
- 🔗 Broken References
- 🏷️ Uninformative Filenames

**Findings table (below scorecard):**
- Filterable by check type and severity
- Columns: Severity badge | Check Type | Filename (with VDR folder path below in grey) | Issue Detail | Recommended Action
- Severity badges: High = red (`#ef4444`), Medium = amber (`#d97706`), Low = grey (`#6B7280`)
- Rows sorted High → Medium → Low within each check type

**Design:** white background, navy (`#1a2332`) header, 12px border-radius cards, `Source Sans 3` font via Google Fonts, no external dependencies beyond SheetJS and fonts.

---

## Step 5 — Deliver to the user

Give a brief summary:

> "I've checked [N] documents across [M] filerooms and found [X] High and [Y] Medium quality issues. The most urgent: [top 2–3 findings]. Use the Download button to export the full report as Excel for the team to action."

Then offer:
> "Want me to flag which issues are quickest to fix vs. which need the document owner involved?"

---

## Operating principles

**Context matters for severity.** A 1-page PDF is fine for a certificate; it's a red flag for an audited accounts file. Always check the filename and folder path before flagging a low page count.

**Don't cry wolf on PII.** A business email address in a contract is expected. A director's personal gmail address in a board minute is a flag. Read the snippet context before raising an issue.

**Redaction quality is a GDPR risk, not just a tidiness issue.** Documents where text is visually blocked but remains machine-readable in the PDF layer are the most dangerous scenario — prioritise these.

**Failed documents are the most urgent fix.** A buyer who clicks a document and gets an error immediately loses confidence in the deal team's preparation. Every failed document should be actioned before go-live.

**Be specific in recommended actions.** "Remove password protection and re-upload" is useful. "Fix document" is not.

## Performance Notes

- **Do not skip checks to save time.** A missed password-protected file or undetected PII exposure is a serious issue that could delay go-live or create a compliance breach.
- Run all Phase A checks from a single `listFolderContents` pass — avoid repeated calls.
- Context matters before flagging: always check filename and folder path before raising a severity issue.

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
