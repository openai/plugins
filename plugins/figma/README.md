# Figma Plugin

This plugin packages Figma-driven design-to-code workflows in
`plugins/figma`.

It currently includes these skills:

- `implement-design`
- `code-connect-components`
- `create-design-system-rules`

## What It Covers

- translating Figma frames and components into production-ready UI code
- inspecting design context and screenshots through the Figma MCP server
- connecting published Figma components to matching code components with Code Connect
- generating project-specific design system rules for Figma-to-code workflows

## Plugin Structure

The plugin now lives at:

- `plugins/figma/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `.mcp.json`
  - plugin-local MCP dependency manifest
  - bundles the Figma MCP endpoint used by the bundled skills

- `.app.json`
  - plugin-local app dependency manifest
  - keeps the public Figma connector wiring explicit alongside the bundled
    MCP-backed workflows

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

This plugin is MCP-backed through `.mcp.json` and currently depends on the
Figma MCP server at `https://mcp.figma.com/mcp`. The bundled skills assume that
the Figma MCP tools are available and that the user can supply Figma URLs with
node IDs when needed.

The current skill set is focused on three workflows:

- implementing designs from Figma with high visual fidelity
- creating Code Connect mappings between published Figma components and code
- generating durable project rules for future Figma-to-code work

This public repo keeps the older connector wiring in `.app.json` while adding
the MCP config, bundled skills, and example command or hook scaffolding that
ship with the richer workflow bundle.
