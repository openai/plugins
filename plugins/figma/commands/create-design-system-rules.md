# /create-design-system-rules

Generate project-specific Figma-to-code rules and prepare them for `AGENTS.md`.

## Workflow

1. Verify Figma MCP access.
2. Run the Figma MCP `create_design_system_rules` tool with project language/framework hints.
3. Analyze the repo for component paths, tokens, naming, and styling approach.
4. Produce copy-ready rules and a short validation plan.

## Output requirements

- Include explicit component and token paths from this repo.
- Mark hard constraints (`IMPORTANT`) separately from preferences.
- Provide the exact `AGENTS.md` section heading to use.
