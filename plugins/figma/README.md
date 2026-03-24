# Figma Plugin

This plugin packages Figma-driven design-to-code workflows in
`plugins/figma`.

It currently includes these skills:

- `implement-design`
- `code-connect-components`
- `create-design-system-rules`

## What It Covers

- translating Figma frames and components into production-ready UI code
- inspecting design context and screenshots through the connected Figma tools
- connecting published Figma components to matching code components with Code Connect
- generating project-specific design system rules for Figma-to-code workflows

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

This plugin is app-backed through `.app.json` and uses the connected Figma
integration for the bundled skills. The workflows assume that the Figma tools
are available and that the user can supply Figma URLs with node IDs when
needed.

The current skill set is focused on three workflows:

- implementing designs from Figma with high visual fidelity
- creating Code Connect mappings between published Figma components and code
- generating durable project rules for future Figma-to-code work

This public repo keeps the bundled skills plus the example command, hook, and
UI scaffolding alongside the app-backed plugin wiring.
