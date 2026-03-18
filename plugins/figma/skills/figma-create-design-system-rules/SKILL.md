---
name: create-design-system-rules
description: Generates custom design system rules for the user's codebase and prepares AGENTS.md guidance for Figma-to-code workflows. Requires Figma MCP server connection.
metadata:
  short-description: Update AGENTS.md with design system rules
---

# Create Design System Rules (Vendored Example Snapshot)

Trimmed snapshot of the `openai/skills` rule-generation workflow.

## Required workflow

1. Verify Figma MCP is available.
2. Call `create_design_system_rules` with language/framework hints.
3. Analyze the codebase for component layout, tokens, styling, and architecture patterns.
4. Generate project-specific rules (components, styling, Figma flow, assets).
5. Prepare copy-ready content for `AGENTS.md`.
6. Suggest a small validation implementation and iterate.

## Output expectations

- Rules should be specific to the repo (paths, tokens, naming conventions).
- Separate hard constraints from preferences.
- Include the exact `AGENTS.md` section placement.
