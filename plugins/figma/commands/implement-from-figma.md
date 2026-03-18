# /implement-from-figma

Implement a Figma frame or component into project code.

## Arguments

- `figma_url`: Figma link with `node-id` (required unless using `figma-desktop` MCP selection)
- `target`: optional file/component target hint
- `mode`: `component` or `screen` (optional; infer if omitted)

## Workflow

1. Parse the Figma link and extract node ID.
2. Run `get_design_context` and `get_screenshot`.
3. Download MCP-provided assets (no placeholder/icon package substitutions).
4. Implement using project conventions and reusable components.
5. Run local verification and summarize parity + known deltas.

## Escalation

Delegate to `figma-implementation-agent` for substantial UI work or multi-file changes.
