---
name: code-connect-components
description: Connects Figma design components to code components using Code Connect. Use when establishing mappings between Figma components and local code components. Requires Figma MCP server connection.
metadata:
  short-description: Connect Figma components to local code
---

# Code Connect Components (Vendored Example Snapshot)

Trimmed snapshot of the `openai/skills` Code Connect workflow.

## Required workflow

1. Parse Figma file key + node ID (convert URL `node-id=1-2` to tool `nodeId=1:2`).
2. Run `get_metadata` to find component nodes.
3. Check existing mappings with `get_code_connect_map`.
4. For unmapped nodes, fetch `get_design_context`.
5. Scan the repo for candidate code components.
6. Confirm ambiguous matches with the user.
7. Create mappings with `add_code_connect_map`.
8. Summarize connected/skipped/unresolved components.

## Mapping heuristics

- Prefer closest prop-interface match over file-name similarity alone.
- Document why a chosen component is the best match when multiple candidates exist.
- Require confirmation before writing mappings when confidence is low.
