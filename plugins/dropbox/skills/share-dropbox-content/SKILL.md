---
name: share-dropbox-content
description: Share Dropbox files or folders by creating shared links, inspecting existing shared links, or explaining current shared-link state. Use only when the user explicitly asks to create a shared link, check access, or inspect a Dropbox shared link.
---

# Share Dropbox Content

Use this skill to create or inspect Dropbox shared links and explain shared-link state.

## Tools

- `create_shared_link`
- `list_shared_links`
- `get_shared_link_metadata`
- `get_file_metadata`
- `search`
- `list_folder`

## Workflow

1. Identify the target file or folder.
2. If the target is ambiguous, use `search` or `list_folder` and ask the user to choose.
3. Use `get_file_metadata` to confirm the exact target.
4. Use `list_shared_links` when checking current sharing state or before creating a new link if existing links matter; continue while the response indicates has_more or returns a cursor before treating the existing-link state as complete.
5. Use `get_shared_link_metadata` when the user provides or asks about a specific shared link.
6. Before calling `create_shared_link`, summarize the exact sharing plan and ask for explicit confirmation.
7. After sharing, report the resulting URL, effective access settings, and any warnings or partial failures.
8. If the user asks to add viewers, add recipients, or share directly with named people, explain that recipient-sharing is unavailable until those MCP tools are available. Offer to create a shared link instead when appropriate.

## Confirmation Required

Before creating a shared link, confirm:

- Exact target file or folder
- Link/access settings requested by the user
- Expiration, password, or download settings when supported

## Output

After a successful action, include:

- Shared link URL
- Whether the link was newly created or reused
- Effective access settings
- Any warning that existing link settings differ from requested settings
- Whether shared-link pagination was complete when existing links were checked

## Safety

Never create a link automatically after finding, downloading, or creating content. Do not claim access was granted to named recipients or viewers; recipient-sharing tools are not available.

## Good Triggers

- "Create a share link for this Dropbox folder."
- "Create a link to this file."
- "Check who can access this Dropbox link."
- "Send me a share link for the launch deck."

## Do Not Use When

- The user only wants to find a file. Use `find-dropbox-content`.
- The user only wants metadata or content summary. Use `inspect-dropbox-file`.
- The user wants to collect uploads from others. Use `collect-files-with-request`.
- The user wants to add viewers or share directly with named recipients. Explain that recipient-sharing is unavailable until the required MCP tools are exposed.
