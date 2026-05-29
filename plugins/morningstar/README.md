# Morningstar Plugin

The Morningstar plugin extends Codex with fund and ETF research workflows using Morningstar's proprietary data and ratings. It gives the assistant access to institutional-grade financial data and layers analytical workflows on top for screening, comparison, and summary reports.

## MCP Server

Connects to the Morningstar MCP server at `https://mcp.morningstar.com/mcp`. A Morningstar Direct subscription or MCP server license is required; you will be prompted to authenticate on first use.

## Layout

This repo includes the Codex plugin manifest and shared Morningstar skills under `plugins/morningstar/`.

```text
plugins/
  morningstar/                       # shared plugin source
    .codex-plugin/plugin.json        # Codex plugin manifest
    .mcp.json                        # MCP server config
    skills/                          # Morningstar Codex skills
```
