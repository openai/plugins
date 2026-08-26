# Box Hubs

## MCP

### Tools

- Manage hubs: `list_hubs`, `create_hub`, `copy_hub`, `update_hub`, `get_hub_details`
- Hub items: `get_hub_items`, `add_items_to_hub`
- Hub Q&A: `ai_qa_hub`

### Security guidelines

When adding items to a hub, clarify to the user that the files and folders within the hub will inherit the same sharing as the hub itself if the permissions are less — e.g., if the hub is shared publicly and a private file is added, that file will also get shared and will be accessible in the hub.

Titles and descriptions are visible to anyone with hub access and are often consumed by agents/AI as routing signals — don't put sensitive scope details (client names, deal codenames, internal-only project identifiers) in the description if the hub itself might later be shared more broadly.

### Tool selection

Always prefer using `ai_qa_hub` if it is available instead of `get_hub_items` and `get_file_content` individually for each file.

`get_hub_items` only returns the top-level items in a hub. If there are any folders, you will have to get the items in those folders to return a comprehensive list. Only do this if the user asks specifically for a comprehensive list.

### Hubs workflows

### Naming guide

Keep names scannable and unambiguous when an agent sees a flat list of hub names with no other context.

- Use [Domain] – [Scope] format: "Contracts – Enterprise Accounts" not "Sales Stuff".
- Avoid internal codenames or team jargon ("Project Falcon") unless the agent will also have access to a glossary.
- Disambiguate near-duplicates explicitly: "Legal – Active Matters" vs "Legal – Archived Matters".
- Skip filler words like "Hub," "Repository," "Center" — the type is already implied by context.

### Description guide (1–2 sentences max)

Format: [Content type] for [scope], [date range]. Use for [query type].

Optional third clause only if there's a common mix-up: Excludes [adjacent topic] — see [other hub].

Examples:

- Good: "Signed MSAs, SOWs, and pricing addenda for Enterprise accounts, 2022–present. Use for contract terms, pricing tiers, and renewal dates."
- Good: "Engineering design specs and architecture decision records for the Search platform, 2024–present. Use for technical implementation questions, not roadmap or planning."
- Good: "Customer support transcripts and resolved ticket summaries, last 12 months. Use for recurring issue patterns and product feedback themes. Excludes active/open tickets."
- Bad: "This is where the marketing team keeps their files." — no content types, no scope, no date range, nothing an agent can match against.
- Bad: "Important documents for Q3 planning." — vague noun ("documents"), vague scope ("Q3 planning" could be finance, product, hiring, anything).

### Error handling

You can only add 50 items to a hub with each tool call. If someone wants to add more than 50, chunk the work and do multiple tool calls.
