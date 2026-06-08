---
name: setup
description: Verify Daloopa MCP connection and show available skills
---

Walk the user through verifying their Daloopa setup for Codex or ChatGPT. Be conversational and helpful.

## Step 1: Verify Runtime
Confirm the user is working in Codex, ChatGPT, or another OpenAI environment that can use skills. Explain that this skill checks whether the Daloopa MCP tools are available.

## Step 2: Verify MCP Connection
This plugin connects to two Daloopa MCP servers:
- **daloopa** (`mcp.daloopa.com/server/mcp`) - Financial data (fundamentals, KPIs, SEC filings)
- **daloopa-docs** (`docs.daloopa.com/mcp`) - Daloopa knowledgebase (API docs, how-tos, usage help)

Run a quick test by calling `discover_companies` with a well-known ticker like "AAPL" to confirm the data MCP server is connected and responding. Show the user the result.

If this fails:
- Check that `.mcp.json` is present and configured for the Daloopa MCP servers.
- In Codex, reinstall or reload the plugin after changing MCP configuration.
- In ChatGPT, verify that the Daloopa MCP connector or equivalent tool access is enabled.
- If the server returns `401` or `Reauthentication required`, restart the Daloopa OAuth/login flow in the current environment.
- On first use, OAuth may open a browser window for Daloopa login.

## Step 3: Quick Tour
Tell the user about the available analysis skills. Use natural-language examples such as:
- "Create a tearsheet for AAPL."
- "Review MSFT earnings and guidance."
- "Build a DCF valuation for NVDA."
- "Create an industry comp sheet for AAPL and peers."

Each reporting skill saves generated files to the `reports/` directory when file access is available.

## Step 4: Note on Enhanced Features
For file-heavy workflows such as Word research notes, Excel models, and pitch decks, use the local document, spreadsheet, or presentation generation workflow available in the current OpenAI environment. If a file cannot be generated in the current environment, provide the complete structured content and explain the limitation.
