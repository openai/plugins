# Morningstar Plugin

The Morningstar plugin extends Codex with fund and ETF research workflows using Morningstar's proprietary data and ratings through the reviewed Morningstar ChatGPT app. It gives the assistant access to institutional-grade financial data and layers analytical workflows on top for screening, comparison, and summary reports.

## ChatGPT App

This plugin points Codex at the reviewed Morningstar app snapshot:

```text
asdk_app_69248819fa4c81918047c4b42b1f8823
```

App URL: https://chatgpt.com/apps/morningstar/asdk_app_69248819fa4c81918047c4b42b1f8823

Installing the plugin connects the Morningstar ChatGPT app, and authentication happens through that app.

## Layout

This repo includes the Codex plugin manifest and compact Morningstar workflow skills under `plugins/morningstar/`.

```text
plugins/
  morningstar/                       # shared plugin source
    .codex-plugin/plugin.json        # Codex plugin manifest
    .app.json                        # Morningstar ChatGPT app reference
    assets/app-icon.png              # Marketplace icon
    skills/                          # Compact Morningstar Codex workflows
```

## Skills

- `fund-screener` - screen funds and ETFs with normalized Morningstar criteria.
- `fund-summarizer` - produce factual fund summaries and reports.
- `fund-comparison` - compare 2 to 4 funds side by side.

The skills intentionally stay lightweight and route data access through the Morningstar app instead of bundling a separate MCP server, local renderer, or large static datapoint catalog.
