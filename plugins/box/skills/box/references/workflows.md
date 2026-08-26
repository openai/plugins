# Workflow Router

## Table of Contents

- Box MCP tool usage
- Box CLI local verification
- Direct REST fallback
- Content workflows
- Collaboration and sharing
- Search
- AI and retrieval
- Hubs
- Doc Gen
- Bulk operations
- Webhooks and events
- Troubleshooting

Use this file when the task is ambiguous and you need to decide which targeted reference to open next.

## Box MCP tool usage

See the MCP section in `SKILL.md` for:

- General MCP guidelines (who_am_i, pagination, least-privilege)
- MCP category routing table (which reference to open for each tool category)

## Box CLI local verification

Open `references/box-cli.md` for:

- CLI-first smoke tests
- Safe CLI auth checks
- `--as-user` verification
- Quick local reads and writes without changing app code

## Direct REST fallback

Open `references/rest-calls.md` for:

- Last-resort REST usage after MCP and CLI setup paths fail
- Required explicit user confirmation before REST calls
- `BOX_ACCESS_TOKEN` setup and safe token handling
- Canonical `curl` templates and error/backoff guidance

## Content workflows

Open `references/content-workflows.md` for:

- Uploading files
- Creating folders
- Listing folder items
- Downloading or previewing files
- Moving files or folders
- Reading or writing metadata

## Collaboration and sharing

Open `references/collaboration.md` for:

- Inviting collaborators (users or groups)
- Collaborator role matrix and least-privilege selection
- Creating and updating shared links
- External-sharing confirmation rules

## Search

Open `references/mcp-search.md` for:

- Keyword and natural-language file search
- Folder-name search
- Metadata-based search (contract value, status, dates)
- Search scoping and disambiguation

## AI and retrieval

Open `references/ai-and-retrieval.md` for:

- Search-first retrieval strategy
- Box AI Q&A, extraction, and agents (MCP tools)
- Box AI via CLI commands
- Content understanding preference order
- External AI pipelines over Box content
- Traceability and citation requirements

## Hubs

Open `references/mcp-hubs.md` for:

- Creating, copying, and updating hubs
- Adding items to a hub
- Hub-level Q&A with Box AI
- Hub naming and description best practices

## Doc Gen

Open `references/mcp-doc-gen.md` for:

- Registering Doc Gen templates
- Single-document and batch generation
- Template tag requirements and limitations

## Bulk operations

Open `references/bulk-operations.md` for:

- Organizing or reorganizing files across folders
- Batch-moving files into a structured hierarchy
- Creating folder trees for classification schemes
- Bulk metadata tagging
- Serial execution constraints and rate-limit handling

## Webhooks and events

Open `references/webhooks-and-events.md` for:

- Push-based notifications
- Catch-up syncs with the events APIs
- Signature verification
- Idempotent event consumers

## Troubleshooting

Open `references/troubleshooting.md` for:

- 401, 403, 404, 409, and 429 failures
- Wrong-actor bugs
- Search result mismatches
- Webhook verification failures
