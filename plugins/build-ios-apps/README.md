# Build iOS Apps Plugin

This plugin packages iOS and Swift workflows in `plugins/build-ios-apps`.

It currently includes these skills:

- `ios-debugger-agent`
- `swiftui-liquid-glass`
- `swiftui-performance-audit`
- `swiftui-ui-patterns`
- `swiftui-view-refactor`

## What It Covers

- building and refactoring SwiftUI UI using current platform patterns
- reviewing or adopting iOS 26+ Liquid Glass APIs
- auditing SwiftUI performance and guiding profiling workflows
- debugging iOS apps on simulators with XcodeBuildMCP-backed flows
- restructuring large SwiftUI views toward smaller, more stable compositions

## Plugin Structure

The plugin now lives at:

- `plugins/build-ios-apps/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

## Notes

This plugin is currently skills-only at the plugin level. It does not ship a
plugin-local `.mcp.json`.

Some bundled skills rely on external MCP/tooling surfaces at runtime, notably
XcodeBuildMCP for simulator build/run/debug workflows in `ios-debugger-agent`.
