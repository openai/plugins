# Figma Plugin

This plugin packages the Figma MCP server and Figma-driven workflows in
`plugins/figma`.

It currently includes these skills:

- `figma-implement-design`
- `figma-code-connect`
- `figma-create-design-system-rules`
- `figma-create-new-file`
- `figma-generate-design`
- `figma-generate-library`
- `figma-use`

## What It Covers

- translating Figma frames and components into production-ready UI code
- inspecting design context, variables, metadata, and screenshots through Figma MCP
- creating parserless Code Connect template files for published Figma components
- generating project-specific design system rules for Figma-to-code workflows
- creating or updating full screens and design system libraries in Figma
- creating new Figma or FigJam files when needed for a workflow

## Plugin Structure

The plugin now lives at:

- `plugins/figma/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `.app.json`
  - plugin-local app dependency manifest
  - points Codex at the connected Figma integration used by the bundled skills

- `.mcp.json`
  - plugin-local MCP server configuration
  - points Codex at the official Figma MCP server at `https://mcp.figma.com/mcp`

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

- `assets/`
  - plugin-level icons referenced by the manifest

- `commands/`, `hooks.json`, `scripts/`, and `ui/`
  - example convention directories kept alongside the imported workflow bundle

## Notes

This plugin is app-backed through `.app.json` and also includes Figma MCP
configuration through `.mcp.json`. The workflows assume that Figma tools are
available and that the user can supply Figma URLs with node IDs when needed.

The current skill set is focused on these workflows:

- implementing designs from Figma with high visual fidelity
- creating parserless Code Connect templates for published Figma components
- generating durable project rules for future Figma-to-code work
- creating or updating Figma files, screens, and design system libraries

Use of the Figma skills and related files is governed by the Figma Developer
Terms. See `LICENSE.txt` and the per-skill license files for details.

This public repo keeps the bundled skills plus the example command, hook, and UI
scaffolding alongside the app-backed and MCP-backed plugin wiring.
