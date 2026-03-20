# Content Workflows

## Table of Contents

- Upload a file
- Create folders
- List folder items
- Download or preview a file
- Generate a shared link
- Invite collaborators
- Move a file or folder
- Read or write metadata

Read `references/auth-and-setup.md` first when the acting identity or SDK vs REST choice is unclear.

For local or manual verification, prefer `scripts/box_cli_smoke.py` when Box CLI is available and authenticated. Fall back to `scripts/box_rest.py` when the task is token-first or Box CLI is unavailable.

## Upload a file

- Primary docs:
  - https://developer.box.com/reference/post-files-content/
- Use for local-disk uploads, form uploads, or pushing generated artifacts into Box.
- Decide whether the input is a file path, in-memory upload, or generated artifact.
- Set the destination folder ID first.
- Treat file-name conflicts explicitly.
- Start with standard upload; use chunked upload only when file size or resumable behavior requires it.
- Minimal smoke check:
  - Upload the file, then list the destination folder with the same actor and confirm returned `id` and `name`.

## Create folders

- Primary docs:
  - https://developer.box.com/reference/post-folders/
- Use for customer, project, case, employee, or workflow roots.
- Decide the parent folder and canonical naming scheme before coding.
- Handle duplicate-name conflicts intentionally.
- Persist the returned folder ID instead of reconstructing paths later.
- Minimal smoke check:
  - Create the folder, then list the parent folder and confirm the child folder ID and name.

## List folder items

- Primary docs:
  - https://developer.box.com/reference/get-folders-id-items/
- Use for dashboards, file pickers, sync views, or post-upload verification.
- Request only the fields the app actually needs.
- Handle pagination instead of assuming a single page.
- Filter server-side where practical before adding client-side transforms.
- Minimal smoke check:
  - Read the folder with a limited field set and confirm the app can process pagination metadata.

## Download or preview a file

- Primary docs:
  - https://developer.box.com/reference/get-files-id-content/
  - https://developer.box.com/guides/embed/ui-elements/preview/
- Download when the app truly needs raw bytes for processing or export.
- Use preview patterns when the app needs an embedded viewer.
- Preserve filename, content type, and auth context in tests and logs.
- Minimal smoke check:
  - Fetch the file metadata first; only then download or preview the exact file ID you intend to use.

## Generate a shared link

- Primary docs:
  - https://developer.box.com/reference/put-files-id/
  - https://developer.box.com/reference/put-folders-id/
- Use for external sharing, customer handoff, or quick verification outside the app.
- Add or update `shared_link` on the target file or folder, not on an unrelated object.
- Set access level, download permissions, and expiration intentionally.
- Confirm the user explicitly wants the audience widened before enabling or broadening sharing.
- Minimal smoke check:
  - Read the file or folder after the update and confirm the resulting `shared_link` fields.

## Invite collaborators

- Primary docs:
  - https://developer.box.com/reference/post-collaborations/
- Use for team, vendor, or customer access to a shared workspace.
- Prefer folder collaboration when multiple files should inherit the same access.
- Choose the narrowest role that satisfies the request.
- Verify the acting identity is allowed to invite collaborators before coding the flow.
- Minimal smoke check:
  - Create the collaboration, then fetch or list collaborations to confirm the collaborator and role.

## Move a file or folder

- Primary docs:
  - https://developer.box.com/reference/put-files-id/ (update parent to move a file)
  - https://developer.box.com/reference/put-folders-id/ (update parent to move a folder)
- Use for reorganizing content, filing into project or category folders, or migrating between folder structures.
- A move is a PUT on the item that sets `parent.id` to the new folder.
- Moving a folder moves all of its contents recursively.
- Handle name conflicts in the target folder — Box returns `409` if a same-named item already exists in the destination.
- For bulk moves (more than a handful of items), read `references/bulk-operations.md` for the inventory-plan-execute-verify workflow, serial execution constraints, and rate-limit handling.
- Minimal smoke check:
  - Move the item, then list the target folder and confirm the item appears with the correct ID and name. Also list the source folder to confirm the item is gone.

## Read or write metadata

- Primary docs:
  - https://developer.box.com/reference/post-files-id-metadata-global-properties/
- Use for invoice IDs, customer names, case numbers, review states, or other business context.
- Read the template definition or existing metadata instance before writing values.
- Keep template identifiers and field names in config, not scattered through the codebase.
- Validate keys and value types in code before calling Box.
- Minimal smoke check:
  - Write the metadata, then read the same instance back and confirm only the expected keys changed.
