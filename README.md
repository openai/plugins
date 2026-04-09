# Plugins

This repository contains a curated collection of Codex plugin examples.

Each plugin lives under `plugins/<name>/` with a required
`.codex-plugin/plugin.json` manifest and optional companion surfaces such as
`skills/`, `.app.json`, `.mcp.json`, plugin-level `agents/`, `commands/`,
`hooks.json`, `assets/`, and other supporting files.

For app-backed plugins, `.app.json` is also the source of truth for connector
identity. When a plugin is the canonical 1:1 curated plugin for a connector,
set `apps.<app-name>.canonical` to `true`. This allows downstream consumers to
derive a definitive `connector id -> plugin` mapping without assuming every
plugin that references a connector is the official base plugin for that
connector.

Highlighted richer examples in this repo include:

- `plugins/figma` for `use_figma`, Code to Canvas, Code Connect, and design system rules
- `plugins/notion` for planning, research, meetings, and knowledge capture
- `plugins/build-ios-apps` for SwiftUI implementation, refactors, performance, and debugging
- `plugins/build-macos-apps` for macOS SwiftUI/AppKit workflows, build/run/debug loops, and packaging guidance
- `plugins/build-web-apps` for deployment, UI, payments, and database workflows
- `plugins/netlify`, `plugins/render`, and `plugins/google-slides` for additional public skill- and MCP-backed plugin bundles
