# /connect-figma-components

Create or update Figma Code Connect mappings for components.

## Arguments

- `figma_url`: Figma URL with `node-id` (required unless using `figma-desktop` selection)
- `component_path`: optional local component path if already known

## Workflow

1. Fetch metadata and identify component nodes.
2. Check existing Code Connect mappings.
3. For unmapped components, inspect the codebase for candidate implementations.
4. Present matches and create mappings after confirmation when needed.
5. Summarize connected/skipped/unresolved components.

## Escalation

Delegate to `figma-code-connect-agent` when mapping many components in one pass.
