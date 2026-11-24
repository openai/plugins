---
name: cognitivedb-manage-spaces
description: >-
  Inspect current CognitiveDB Space information for questions about its identity,
  name, description, or other returned metadata. Space updates are unsupported.
metadata:
  version: "dev-1.5.2-codex.2"
---

# Inspect CognitiveDB Spaces

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

Use the CognitiveDB Space already resolved for the current task. Here, workspace
means the CognitiveDB Space, not the Agent local project directory. Never invent
Space identity, values, permissions, or unavailable fields.

## Boundaries

- Own only current-Space information reads. Name and description updates are
  unsupported by the current MCP contract.
- Route membership and access to `cognitivedb-administer-access`; route usage
  and billing to `cognitivedb-inspect-usage-and-billing`.
- Never change CognitiveDB Space context or bypass missing MCP capability with another
  interface.

## Core Instructions

- Use the current task's resolved CognitiveDB Space and supply its context as
  required by the live Tool schema. The local working directory does not identify
  a Space. Stop on missing, inconsistent, or cross-Space context.
- Return only the requested non-secret fields. Report an unavailable field as
  unavailable rather than inferring its value.

## Allowed MCP Tools

- `cognitivedb_space_current_get`
