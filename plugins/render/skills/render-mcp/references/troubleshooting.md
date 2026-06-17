# Render MCP Troubleshooting

## Connection Errors

### "MCP server not found" or tool not available

**Cause:** MCP server not configured in the AI tool.

**Fix:** Follow the setup instructions in the main SKILL.md for your specific tool (Cursor, Claude Code, Codex). After adding the config, restart the tool.

### "Connection refused" or timeout

**Cause:** Network issue or incorrect URL.

**Fix:**
- Verify the URL is exactly `https://mcp.render.com/mcp`
- Check internet connectivity
- Some corporate firewalls block MCP connections — try from a different network

### "Transport error" or "SSE not supported"

**Cause:** Using the wrong transport or URL.

**Fix:**
- Use HTTP transport (streamable HTTP), not SSE
- URL should be `https://mcp.render.com/mcp`, not `https://mcp.render.com/sse`
- For Claude Code: use `--transport http` flag

## Authentication Errors

### "Unauthorized" or 401

**Cause:** Missing, invalid, or expired API key.

**Fix:**
1. Generate a new API key: `https://dashboard.render.com/u/*/settings#api-keys`
2. Update the key in your tool's MCP config
3. Restart the tool
4. Verify with `list_services()`

### "Forbidden" or 403

**Cause:** API key doesn't have access to the requested resource, or wrong workspace.

**Fix:**
- Check the active workspace with `get_selected_workspace()`
- Switch workspaces if needed with `list_workspaces()`
- Ensure the API key belongs to an account with access to the workspace

## Tool-Specific Issues

### Cursor

- Config file: `~/.cursor/mcp.json`
- Must be valid JSON (no trailing commas)
- Restart Cursor fully after config changes (not just reload window)
- If multiple MCP servers are configured, ensure the `render` key is unique

### Claude Code

- Added via CLI: `claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <key>"`
- To update: `claude mcp remove render` then re-add
- To list: `claude mcp list`

### Codex

- Requires `RENDER_API_KEY` env var to be set in the shell where Codex runs
- Added via: `codex mcp add render --url https://mcp.render.com/mcp --bearer-token-env-var RENDER_API_KEY`
- If the env var is not set when Codex starts, MCP auth fails

## Workspace Issues

### "No workspace selected"

**Fix:** Run `list_workspaces()` to see available workspaces, then ask the user to select one.

### Operations return empty results

**Cause:** Active workspace has no services, or wrong workspace is selected.

**Fix:** Verify with `get_selected_workspace()` and switch if needed.

## MCP vs CLI Fallback

If MCP cannot be configured (network restrictions, unsupported tool), use the Render CLI as a fallback. See **render-cli** for setup and usage.

| Capability | MCP | CLI |
|-----------|-----|-----|
| List services | `list_services()` | `render services -o json` |
| View logs | `list_logs(...)` | `render logs -r SVC` |
| Deploy | `trigger_deploy(serviceId)` | `render deploys create SVC --wait` |
| Metrics | `get_metrics(...)` | Not available |
| SQL queries | `query_render_postgres(...)` | `render psql DB -c "SQL"` |
| SSH | Not available | `render ssh SVC` |
