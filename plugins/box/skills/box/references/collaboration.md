# Collaboration and Sharing

## Table of Contents

- MCP
  - Tools
  - Box Collaborator Roles
  - Security guidelines
  - Tool selection
  - Collaboration workflows
  - Error handling
- CLI / REST
  - Invite collaborators
  - Generate a shared link
- Primary docs

## MCP

### Tools

- Collaborations: `create_collaboration`, `update_collaboration`, `list_item_collaborations`
- Shared links: `add_file_shared_link`, `add_folder_shared_link`

### Box Collaborator Roles

| Capability | Co-owner | Editor | Viewer Uploader | Previewer Uploader | Viewer | Previewer | Uploader |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Upload | ✓ | ✓ | ✓ | ✓ | — | — | ✓ |
| Download | ✓ | ✓ | ✓ | — | ✓ | — | — |
| Preview | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Edit & rename | ✓ | ✓ | — | — | — | — | — |
| Delete & move | ✓ | ✓ | — | — | — | — | — |
| Invite collaborators | ✓ | ✓ | — | — | — | — | — |
| Advanced folder settings | ✓ | — | — | — | — | — | — |

**Plan note:** Editor and Viewer are available on all accounts. All other roles require Business/Enterprise and apply to folders only.

**Co-owner** cannot be set via MCP and must be set in browser.

### Security guidelines

Always require human in the loop when adding external collaborators or when generating open shared links. When a user tries to share a file or folder externally, give a description of what is in the file or folder and require human confirmation before continuing.

When sharing internally (the target has the same email domain as the authenticated user) or generating shared links that are scoped to internal-only access, you can share without requiring human in the loop.

When overwriting a shared link (adding a shared link to a file or folder when one already exists), provide the old settings and confirm with the user whether they want to continue.

When creating open shared links, confirm with the user whether they want a password or expiration before creating. Treat folder shared links with extra caution since they expose everything inside, including content added after link creation.

### Tool selection

When generating shared links, fill `vanity_name` to create a custom URL slug (box.com/v/my-custom-name) for easier sharing.

If the user asks to update a shared link, you can call `add_file_shared_link` or `add_folder_shared_link` again — it's a PUT under the hood, is idempotent, and will overwrite the current shared link settings.

### Collaboration workflows

### Invite a user to a file or folder

`create_collaboration` with `target_type: "file"` or `"folder"`, `target_id`, `collaborator_type: "user"`, `collaborator_email` or `collaborator_id`, and `role` (e.g. "editor", "viewer", "uploader").

For folders only, optionally set `can_view_path` if the collaborator needs visibility into the folder's parent path.

Capture the returned `collaboration_id` for any future update — this is an item-collaboration ID.

### Group-based access

Resolve the `group_id` ahead of time (the tool takes an ID, not a group name).

`create_collaboration` with `collaborator_type: "group"`, `collaborator_id`, the appropriate `target_type`/`target_id`, and `role`.

Note that role changes via `update_collaboration` on a group apply to every member at once — confirm scope before downgrading or upgrading.

### Create a basic shared link on a file or folder

`add_file_shared_link` or `add_folder_shared_link` with the item ID and desired access level.

Check whether the enterprise enforces a password or expiration requirement on shared links before assuming an open link will be accepted.

### Update an existing shared link's settings

Re-call `add_file_shared_link`/`add_folder_shared_link` on the same item with updated access, password, or expiration — these tools create-or-update in place rather than requiring a separate update call.

If tightening access (e.g., from "open" to "company-only"), confirm no external party currently relies on the old link before changing it.

### Error handling

Adding co-owners via MCP is not supported. If the user wants to add a co-owner, direct them to do so on box.com in the browser. Provide them a link to the object that they were attempting to modify.

When creating open shared links, the `unshared_at` time has to be within 90 days. If the user wants to generate a permanent open shared link, direct them to do so in the browser and provide them with a link to Box for the object they were trying to modify.

## CLI / REST

### Invite collaborators (general)

- Primary docs:
  - https://developer.box.com/reference/post-collaborations/
- Use for team, vendor, or customer access to a shared workspace.
- Prefer folder collaboration when multiple files should inherit the same access.
- Choose the narrowest role that satisfies the request.
- Verify the acting identity is allowed to invite collaborators before coding the flow.
- Minimal smoke check:
  - Create the collaboration, then fetch or list collaborations to confirm the collaborator and role.

### Generate a shared link (general)

- Primary docs:
  - https://developer.box.com/reference/put-files-id/
  - https://developer.box.com/reference/put-folders-id/
- Use for external sharing, customer handoff, or quick verification outside the app.
- Add or update `shared_link` on the target file or folder, not on an unrelated object.
- Set access level, download permissions, and expiration intentionally.
- Confirm the user explicitly wants the audience widened before enabling or broadening sharing.
- Minimal smoke check:
  - Read the file or folder after the update and confirm the resulting `shared_link` fields.

## Primary docs

- Collaborations:
  - https://developer.box.com/reference/post-collaborations/
- Shared links:
  - https://developer.box.com/reference/put-files-id/
  - https://developer.box.com/reference/put-folders-id/
