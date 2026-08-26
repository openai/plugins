# Bulk Operations

## Table of Contents

- When this applies
- Constraints
- Workflow: inventory, classify, plan, execute, verify
- Step 1 — Inventory
- Step 2 — Classify (when content-based sorting is needed)
- Step 3 — Plan the target hierarchy
- Step 4 — Create folders
- Step 5 — Move files
- Step 6 — Verify
- Rate-limit and backoff handling
- REST vs CLI for bulk work
- Partial failure recovery

Read `references/auth-and-setup.md` first when the acting identity or SDK vs REST choice is unclear.

## When this applies

Use this reference when the task involves more than a handful of files or folders in a single operation:

- Organizing or reorganizing files across folders (by type, date, project, etc.)
- Batch-moving files from a flat folder into a structured hierarchy
- Creating a folder tree for a classification or filing scheme
- Bulk-tagging files with metadata
- Migrating content between folder structures

## Constraints

### Box CLI must run serially

The Box CLI does not support concurrent invocations against the same environment. Launching multiple CLI processes in parallel causes auth conflicts, dropped operations, and unpredictable errors. **Always run CLI commands one at a time, waiting for each to complete before starting the next.**

### Box API rate limits

Box enforces per-user and per-app rate limits. Bulk operations that send requests too quickly will receive `429 Too Many Requests` responses. The response includes a `Retry-After` header with the number of seconds to wait. See [Rate-limit and backoff handling](#rate-limit-and-backoff-handling) below.

### Folder name uniqueness

Box enforces unique names within a parent folder. Creating a folder that already exists returns a `409 Conflict`. Check for existing folders before creating, or handle 409 by looking up the existing folder and reusing its ID.

## Workflow: inventory, classify, plan, execute, verify

Bulk operations follow this pattern. Do not skip ahead — moving files without a verified plan leads to misplaced content that is painful to undo.

```
Inventory → Classify (if needed) → Plan → Execute (serial) → Verify
```

Skip the classify step when files can be sorted by filename, extension, or existing metadata alone.

## Step 1 — Inventory

List everything in the source folder(s). Paginate fully — do not assume a single page covers all items.

```bash
# CLI — list up to 1000 items
python3 scripts/box_cli_smoke.py list-folder-items <FOLDER_ID> --max-items 1000 --fields id name type

# REST — paginate with offset
python3 scripts/box_rest.py get-folder-items --folder-id <FOLDER_ID> --limit 1000 --fields id name type
```

For folders with more items than one page returns, increment the offset and repeat until all items are captured.

Capture each item's `id`, `name`, and `type` into a working list before proceeding.

## Step 2 — Classify (when content-based sorting is needed)

Skip this step if files can be categorized by filename, extension, or existing metadata. Use it when the documents are unstructured and their content determines the category — for example, a folder of mixed invoices, receipts, contracts, and reports that all share the same file type.

### Preference order for content understanding

1. **Box AI Q&A or Extract** (preferred) — ask Box AI to classify or extract structured fields from each file. This keeps content server-side, requires no downloads, and leverages Box's own document understanding.
2. **Metadata inspection** — check existing Box metadata templates or properties already applied to the files.
3. **Previews or thumbnails** — use Box preview representations for lightweight visual inspection without downloading the full file.
4. **Local analysis (OCR, agent-side parsing)** — download the file and process it locally. Use only when Box AI is unavailable, not authorized, or insufficient for the document type.

### Sample-first strategy

Do not classify every file up front. Box AI calls are slower than metadata reads and have tighter rate limits.

1. **Pick a small sample** (5–10 files) that appear representative of the mix.
2. **Classify the sample** using Box AI to discover the category set and validate the prompt.
3. **Check for cheaper signals.** After seeing the sample results, determine whether filename patterns, extensions, or metadata can sort some or all of the remaining files without additional AI calls.
4. **Classify the remainder** — use AI only for files that cannot be sorted by cheaper signals. Pace AI calls at least 1–2 seconds apart.
5. **Record each classification** (file ID → category) as it completes so an interrupted run can resume without re-classifying finished files.

### Box AI classification via CLI

**Before the first AI call**, run `box ai:ask --help` to confirm the command exists in the installed CLI version and to check for any flag changes.

Use `box ai:ask` to classify a single file by asking a direct question:

```bash
box ai:ask --items=id=<FILE_ID>,type=file \
  --prompt "What type of document is this? Reply with exactly one of: invoice, receipt, contract, report, other." \
  --json --no-color
```

Use `box ai:extract` when you need key-value extraction via a freeform prompt:

```bash
box ai:extract --items=id=<FILE_ID>,type=file \
  --prompt "document_type, vendor_name, date" \
  --json --no-color
```

Use `box ai:extract-structured` when you have a metadata template or want typed fields with options:

```bash
box ai:extract-structured --items=id=<FILE_ID>,type=file \
  --fields "key=document_type,type=enum,options=invoice;receipt;contract;report;other" \
  --json --no-color
```

Reference: https://github.com/box/boxcli/blob/main/docs/ai.md

### Handling failures during classification

- **Exit code 2 or "Unexpected Error" with no HTTP body** can mean the installed CLI version does not have AI commands, Box AI is not enabled for the account, or the file type is not supported. Run `box ai:ask --help` to verify the command exists. If the command exists but still fails, try a known-supported file type (PDF, DOCX) to distinguish account-level unavailability from file-type incompatibility.
- If the first AI call returns a 403, feature-not-available, or similar authorization error, stop attempting AI classification for the remaining files and switch to the next method in the preference order immediately.
- If an individual file fails (unsupported format, empty content, timeout), log it and continue. Classify it manually or by fallback method after the batch finishes.
- On 429, wait for the `Retry-After` period and retry the same file before moving to the next one.
- Box AI support for file types varies by account tier. Image files (`.jpg`, `.png`) may not be supported for text-based Q&A. If the sample files are images, try `box ai:extract` first or check whether the account has image-understanding capabilities before falling back to local OCR.

## Step 3 — Plan the target hierarchy

Decide the target folder structure before creating or moving anything.

1. Define the classification rule (by file-name pattern, extension, date, metadata, or content).
2. Map each inventoried item to its target folder path.
3. Identify which target folders already exist and which need to be created.
4. Write the plan as a structured list or table — folder path, folder ID (if existing), and the file IDs that belong there.

Example plan:

```
Target folder          | Parent ID | Needs creation | File IDs
-----------------------|-----------|----------------|------------------
/SEC Filings/10-K      | 0         | yes            | 111, 112, 113 ...
/SEC Filings/10-Q      | 0         | yes            | 211, 212, 213 ...
/Research/AI            | 0         | yes            | 311, 312, 313 ...
```

Confirm the plan with the user before executing if the operation is large or the classification is ambiguous.

## Step 4 — Create folders

Create target folders **one at a time, serially**. After each creation, record the returned folder ID — you need it for moves.

```bash
# CLI
python3 scripts/box_cli_smoke.py create-folder <PARENT_ID> "SEC Filings"
# then
python3 scripts/box_cli_smoke.py create-folder <SEC_FILINGS_ID> "10-K"

# REST
python3 scripts/box_rest.py create-folder --parent-folder-id <PARENT_ID> --name "SEC Filings"
```

Handle `409 Conflict` by listing the parent folder to find the existing folder's ID rather than failing the entire operation.

Create parent folders before child folders. Process the tree top-down.

## Step 5 — Move files

Move files into their target folders **one at a time, serially**. Each move is a PUT that updates the file's parent.

```bash
# REST (preferred for bulk — more reliable than CLI for high-volume moves)
python3 scripts/box_rest.py move-item --item-type file --item-id <FILE_ID> --parent-folder-id <TARGET_FOLDER_ID>

# CLI
python3 scripts/box_cli_smoke.py move-item <FILE_ID> file --parent-id <TARGET_FOLDER_ID>
```

After each successful move, record it. If a move fails, log the file ID and error and continue with the remaining files — do not abort the entire batch.

### Pacing

Insert a short delay between operations when working with large batches (100+ items). A 200–500ms pause between requests helps stay within rate limits without dramatically increasing total time.

When using REST directly in application code (not via the scripts), implement proper 429 backoff instead of fixed delays.

## Step 6 — Verify

After all moves complete:

1. List each target folder and confirm it contains the expected file IDs and count.
2. List the source folder and confirm it is empty or contains only the items that were intentionally left behind.
3. Report any items that failed to move and the error encountered.

```bash
python3 scripts/box_cli_smoke.py list-folder-items <TARGET_FOLDER_ID> --max-items 1000 --fields id name
```

## Rate-limit and backoff handling

When Box returns `429 Too Many Requests`:

1. Read the `Retry-After` header (value in seconds).
2. Wait that many seconds before retrying the same request.
3. Do not retry other requests during the wait — the limit is typically per-user or per-app, so other requests will also be throttled.
4. After a successful retry, resume normal pacing.

In application code, implement exponential backoff with jitter starting at the `Retry-After` value. In script-based or CLI-based operations, a simple sleep-and-retry is sufficient.

## REST vs CLI for bulk work

| Factor | REST (`box_rest.py` or SDK) | CLI (`box_cli_smoke.py`) |
| --- | --- | --- |
| Concurrency safety | Can handle controlled concurrency with proper rate-limit handling | Must run serially — no parallel invocations |
| Overhead per call | Lower — direct HTTP | Higher — process spawn per command |
| Error handling | Structured JSON responses, easy to parse and retry | Exit codes and mixed output, harder to automate |
| Best for | Bulk moves, batch metadata writes, any operation over ~50 items | Quick verification, small batches, interactive debugging |

**Default to REST for bulk operations.** Fall back to CLI when REST auth is unavailable or the operator specifically prefers CLI-based workflows.

## Partial failure recovery

Bulk operations can fail partway through. Design for recovery:

- Track which operations succeeded (keep a log of completed item IDs).
- On failure, report what completed, what failed, and what remains.
- Make the operation resumable: use the inventory list minus completed items as the input for a retry pass.
- Moves are idempotent in practice — moving a file to a folder it is already in returns the file unchanged. Re-running a move pass is safe.
