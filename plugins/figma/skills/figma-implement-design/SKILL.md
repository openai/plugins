---
name: figma-implement-design
description: Translates Figma designs into production-ready code with strong visual fidelity. Use when implementing UI from Figma files or when the user provides a Figma URL.
metadata:
  short-description: Paste a Figma URL to implement designs
---

# Implement Design (Vendored Example Snapshot)

Trimmed snapshot of the `openai/skills` workflow for plugin packaging demos.

## Required workflow

1. Ensure Figma MCP is connected.
2. Parse file key + node ID from the Figma URL (or use current selection for desktop MCP).
3. Fetch `get_design_context`.
4. Fetch `get_screenshot`.
5. Download required assets from the MCP payload.
6. Implement using repo conventions and design system tokens.
7. Validate against Figma screenshot and report deltas.

## Rules

- Treat MCP code output as a design representation, not final code style.
- Reuse existing components and tokens whenever possible.
- Avoid hardcoded values when tokens exist.
- Document any required deviations from Figma.

## References

- `references/parity-checklist.md` for the review checklist.
