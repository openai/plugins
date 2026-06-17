# Hex plugin

`hex` is a Codex plugin wrapper for the Hex ChatGPT app / MCP connector.

It currently includes:

- one Hex routing skill
- a minimal `.app.json` connector manifest

## Commands

- `hex`
  Search Hex projects and use Hex Threads when the user explicitly asks for Hex or an existing Hex workspace asset.

## Notes

- Use `search_projects` before creating a new thread when the user is looking for existing Hex work.
- Treat `create_thread` and `continue_thread` as write actions that require user confirmation and an appropriate Hex workspace context.
- Do not use Hex as the default owner for generic company metrics, KPI reporting, dashboard creation, report generation, metric diagnostics, or notebook-backed analysis. Route those through the relevant analytics or Data Science skills unless the user asks to do the work in Hex.
- Use Hex for explicit Hex workspace questions, not for generic web search or Hex product documentation questions.
