---
name: mcp-tool-hint-justifications
description: Inspect an MCP server codebase and generate tool-hint-justifications.json for Apps SDK submission review, with concise justifications for readOnlyHint, openWorldHint, and destructiveHint.
---

# MCP Tool Hint Justifications

Use this skill when a developer needs a `tool-hint-justifications.json` file for a ChatGPT Apps submission. The file is uploaded in the Apps submission form to fill out the MCP tool hint justification fields.

## Workflow

1. Inspect the MCP server codebase from the current working directory.
2. Find every exposed MCP tool and its declared `readOnlyHint`, `openWorldHint`, and `destructiveHint` annotations.
3. Read each tool implementation and any called helper functions needed to understand side effects.
4. Compare the explicit hints against the tool's actual behavior. If any hint is missing or wrong, ask the developer for approval before updating the MCP tool definition.
5. Generate one concise review-facing justification for each hint of each tool.
6. Write `tool-hint-justifications.json` in the current working directory.

Do not infer behavior from the tool name alone. Use the real tool implementation and declared annotations. If a tool calls into another module or API client, inspect enough of that path to know whether it reads, writes, deletes, sends, publishes, or changes external state.

## Hint Rules

Use the Apps SDK review meanings:

- `readOnlyHint`: `true` only when the tool strictly fetches, looks up, lists, retrieves, or computes data without changing state. `false` if it can create, update, delete, send, enqueue, run jobs, write logs, start workflows, or otherwise mutate state.
- `destructiveHint`: `true` if the tool can delete, overwrite, send irreversible messages or transactions, revoke access, or perform destructive admin actions, including via some modes or parameters. Otherwise `false`.
- `openWorldHint`: `true` if the tool can change publicly visible internet state or external third-party systems, such as sending emails or messages, posting/publishing content, creating public tickets/issues, pushing code/content, or submitting external forms. `false` if it only operates in closed/private systems.

ChatGPT Apps submissions require every tool to set all three hints explicitly. Missing or null hints are submission blockers, even if MCP clients may have protocol-level defaults.

If a hint is missing, null, or does not match the actual behavior you found in code, stop before writing the JSON and ask the developer for approval to update the MCP server source. In the approval request, list each affected tool, the missing/current hint value, the behavior you observed, and the recommended explicit hint value. If the developer approves, make the smallest source change that sets the correct hint explicitly, then generate JSON using the updated values. If the developer does not approve or the correct edit location is ambiguous, do not generate misleading JSON; report the mismatch and the blocked update.

## Output Contract

Write exactly one JSON file named `tool-hint-justifications.json`:

```json
{
  "$schema": "https://developers.openai.com/apps-sdk/schemas/tool-hint-justifications.v1.json",
  "schema_version": 1,
  "tools": {
    "tool_name": {
      "annotations": {
        "readOnlyHint": true,
        "openWorldHint": false,
        "destructiveHint": false
      },
      "justifications": {
        "read_only_justification": "Only retrieves matching records and does not modify data.",
        "open_world_justification": "Does not write to public internet state or third-party systems.",
        "destructive_justification": "Does not delete, overwrite, revoke access, or perform irreversible actions."
      }
    }
  }
}
```

`$schema` identifies the import file shape for editors and importers; Codex does not need to fetch it. `tools` is the only v1 import surface.

## Writing Justifications

- Keep each justification to one sentence.
- Be specific about the actual behavior, not the annotation itself.
- For write tools, state what system is changed and whether the change is bounded/private or public/external.
- For destructive tools, name the irreversible action and mention any real safeguard only if it exists in the code.
- Do not include source snippets, secrets, tokens, request IDs, local paths, stack traces, or private implementation details in the JSON.

Good examples:

- `Only retrieves project metadata and returns it without creating or updating records.`
- `Creates a private task in the user's workspace and cannot publish content to public URLs.`
- `Deletes the selected workspace document, which cannot be recovered after confirmation.`

Bad examples:

- `readOnlyHint is true because the tool is read-only.`
- `Probably safe.`
- `The function calls client.delete_item(...) in src/server.py.`

## Final Response

After writing the file, summarize the number of tools covered and list any tool names that required especially careful judgment. If generation is blocked, lead with the exact missing hints or source ambiguity.
