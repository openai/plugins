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

This repo includes the Codex plugin manifest, compact Morningstar workflow skills, and the partner-authored deferred support files under `plugins/morningstar/`.

```text
plugins/
  morningstar/                       # shared plugin source
    .codex-plugin/plugin.json        # Codex plugin manifest
    .app.json                        # Morningstar ChatGPT app reference
    assets/app-icon.png              # Marketplace icon
    skills/                          # Compact Morningstar Codex workflows plus deferred support files
```

## Skills

- `fund-screener` - screen funds and ETFs with normalized Morningstar criteria.
- `fund-summarizer` - produce factual fund summaries and reports.
- `fund-comparison` - compare 2 to 4 funds side by side.

The top-level skills intentionally stay lightweight and route data access through the Morningstar app instead of bundling a separate MCP server. Detailed partner-authored workflow rules live in each skill's `references/full-workflow.md`; the fund summary HTML report support files live under `fund-summarizer/assets/`, `fund-summarizer/references/`, and `fund-summarizer/scripts/`.

Fund summary report rendering always writes the HTML report and attempts a sibling PDF copy when the local environment supports it. Existing rendered HTML files can also be exported directly with `fund-summarizer/scripts/export_report.py`.
