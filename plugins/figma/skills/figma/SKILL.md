---
name: figma
description: Connect to Figma using the Figma MCP. Use when working with Figma files.
---

# Figma MCP (Vendored Example Snapshot)

This is a trimmed plugin-bundled snapshot of the `openai/skills` Figma skill.

## Required flow (non-skippable)

1. Run `get_design_context` for the exact node.
2. If the response is too large, run `get_metadata` and re-fetch targeted nodes.
3. Run `get_screenshot` for a visual reference.
4. Only then download assets and begin implementation.
5. Translate MCP output into project conventions and tokens.
6. Validate visual parity before marking complete.

## Asset handling

- Use MCP-provided localhost assets directly when present.
- Do not introduce new icon packages when assets are in the Figma payload.
- Do not use placeholders if a Figma asset is provided.

## References

- `references/figma-flow.md` for quick reminders and URL/node parsing notes.
