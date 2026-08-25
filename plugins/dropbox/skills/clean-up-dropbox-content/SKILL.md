---
name: clean-up-dropbox-content
description: Clean up Dropbox content by identifying obsolete, duplicate, temporary, or unwanted files and deleting only after explicit review. Use when the user explicitly asks to delete, remove, or clean up Dropbox files or folders.
---

# Clean Up Dropbox Content

Use this skill for careful deletion workflows in Dropbox.

## Tools

- `search`
- `list_folder`
- `get_file_metadata`
- `list_shared_links`
- `copy`
- `delete`
- `check_job_status`

## Workflow

1. Confirm the cleanup goal and scope.
2. Use `search` or `list_folder` to identify candidate content.
3. Use `get_file_metadata` to verify each deletion candidate.
4. Use `list_shared_links` when deleting shared content could affect others.
5. If the user may need rollback context, explain that the current Dropbox MCP tools do not expose revision listing or restore operations.
6. If the user wants to preserve a copy first, confirm the exact destination, call `copy`, and use `check_job_status` for any asynchronous copy job until it completes successfully.
7. After any requested copy has completed successfully, present a deletion review list and ask for explicit confirmation.
8. Call `delete` only for the exact confirmed items.
9. Use `check_job_status` for any asynchronous copy or deletion job until it completes or must be reported as pending.
10. Report every copied, deleted, skipped, pending, or failed item.

## Confirmation Required

Before deleting anything, confirm:

- Exact paths or stable identifiers
- Whether each item is a file or folder
- Whether the item appears shared
- Why it is safe to delete
- Exact copy destination, if the user wants to preserve a copy first

## Output

Before deletion, present:

- Candidate path
- Type
- Modified time when available
- Sharing status when relevant
- Copy destination when preserving a copy first
- Reason it appears safe to delete

After deletion, present:

- Copied items when relevant
- Deleted items
- Pending items and job status when relevant
- Failed items and reason
- Items skipped because they were ambiguous or risky

## Safety

Never delete based only on a broad pattern like "old files" or "duplicates" without listing exact targets. Never delete a parent folder when the user confirmed only child files. If confidence is not high, stop and ask the user to choose.

## Good Triggers

- "Delete these Dropbox files."
- "Clean up duplicate PDFs in this folder."
- "Remove obsolete draft files."
- "Delete temporary exports from Dropbox."

## Do Not Use When

- The user wants to move content to an archive. Use `organize-dropbox-folder`.
- The user wants to recover content. Explain that recovery is unavailable until the Dropbox restore tool is exposed.
- The user only wants a list of cleanup candidates and no deletion. Use `find-dropbox-content` or `inspect-dropbox-file`.
