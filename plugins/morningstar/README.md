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

This repo includes the Codex plugin manifest and shared Morningstar skills under `plugins/morningstar/`.

```text
plugins/
  morningstar/                       # shared plugin source
    .codex-plugin/plugin.json        # Codex plugin manifest
    .app.json                        # Morningstar ChatGPT app reference
    skills/                          # Morningstar Codex skills
```
