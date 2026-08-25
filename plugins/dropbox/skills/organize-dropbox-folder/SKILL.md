---
name: organize-dropbox-folder
description: Organize Dropbox files and folders by creating folders, copying content, or moving content into a cleaner structure. Use when the user asks to organize, archive, consolidate, restructure, copy, or move Dropbox content.
---

# Organize Dropbox Folder

Use this skill to safely organize Dropbox content through folder creation, copying, and moving.

## Tools

- `list_folder`
- `search`
- `get_file_metadata`
- `create_folder`
- `copy`
- `move`
- `check_job_status`

## Workflow

1. Understand the desired organization goal and target scope.
2. Use `list_folder` or `search` to inventory the relevant content.
3. Use `get_file_metadata` for items that may be moved or copied.
4. Draft a proposed change plan before any mutation.
5. If needed, create destination folders with `create_folder` after confirmation.
6. Use `copy` when preserving the original location matters or when the user says copy/duplicate.
7. Use `move` only when the user explicitly wants content relocated or archived.
8. Use `check_job_status` for any asynchronous copy or move job until it completes or must be reported as pending.
9. After changes, summarize all created, copied, moved, and pending paths.

## Confirmation Required

Before any mutation, confirm:

- Source paths
- Destination paths
- Whether the operation is copy or move
- Whether destination folders should be created
- Expected result after the operation

## Output

Before mutation, present a plan:

- Folders to create
- Files or folders to copy
- Files or folders to move
- Items that need clarification

After mutation, report:

- Successfully created folders
- Successfully copied items
- Successfully moved items
- Pending jobs and current status when relevant
- Any failures or skipped items

## Safety

Prefer copy over move when the user intent is ambiguous. Do not move shared folders or high-level team folders without extra confirmation. Do not delete anything; use `clean-up-dropbox-content` only when deletion is explicitly requested.

## Good Triggers

- "Organize these files into folders by client."
- "Archive last year's project folder."
- "Copy these assets into the launch folder."
- "Move all final PDFs into the Final folder."

## Do Not Use When

- The user only wants to search or inspect content. Use `find-dropbox-content` or `inspect-dropbox-file`.
- The user asks to delete content. Use `clean-up-dropbox-content`.
- The user asks to restore content. Explain that recovery is unavailable until the Dropbox restore tool is exposed.
