---
name: cognitivedb-discipline
description: >-
  Require user selection of a Space before Cognitive Database resource discovery, and keep operations within the selected Space and Catalog scope.
metadata:
  version: "dev-1.0.2-chatgpt.3"
---

# Cognitive Database Discipline

## Resource boundary

A Space defines the resource boundary for Cognitive Database work. The user
chooses which Space may be used. Clarify an unresolved target with the user
before inspecting its resources, including read-only metadata.

## Select the Space before resource discovery

1. Honor a Space explicitly specified by the user, or reuse a Space selected by
   the user in this conversation on the same connection. Resolve an ambiguous
   name with the user. Keep the connection, Space ID, Space name, organization,
   and the user's selection in conversation context.
2. If neither exists, call `cognitivedb_space_list` on the intended connection.
   Present Space names with their organizations, ask the user to choose, and
   wait for the reply. Require a choice even for one candidate. With no
   candidates, report the blocker and stop.
3. This selection step is complete only when the user's target or reply resolves
   to one actual Space on that connection. Use its returned `project_id` as
   `space_id`. A default name, discovery order, dataset location, or selection
   from another conversation does not establish the user's choice.

Before selection, limit remote work to connector discovery, tool-schema
inspection, own-profile reads, and listing Spaces needed for selection. Read skills and local reference
material as needed. Begin Catalog, Schema, Table, Compute, and business-data
inspection only after selection. Do not inspect resources across Spaces to
choose a Space for the user; read-only access does not waive this boundary.
An own-profile or Space-list-only request finishes without selecting a Space.

## Keep discovery within the selected scope

- Use the selected Space for every dependent operation. Honor user-specified
  Catalogs, Schemas, and objects as further boundaries. Within those boundaries,
  inspect only metadata and data needed for the task.
- If a Catalog is unspecified, perform only the owning skill's bounded metadata
  discovery inside the selected Space. Present remaining plausible targets and
  ask the user to resolve material ambiguity before further exploration.
- On an absent target, empty result, or access denial, report the gap and clarify
  the target. Expand to another Catalog or Space only after the user explicitly
  chooses that expanded scope. Re-resolve the Space when the user changes the
  connection or Space. Preserve narrower explicit targets when resuming work.
- Space selection establishes the resource boundary; SQL, Compute use, writes,
  and other operations retain their owning skill's approval requirements.
  Later approval does not authorize earlier discovery outside the boundary.
- Delegate the exact connection, selected Space ID, and any Catalog/object
  boundaries. A child Agent missing them asks its parent before resource access.
- Report the Space name, Space ID, and organization after Space-scoped work.

## Host interaction

When a Space choice is required, present the candidates through GenUI, a host
choice prompt, or a plain-text list in the conversation. Bind interactive
options to their actual Space IDs. A preselected option remains pending until
the user submits it. Continue only after the user's submitted choice or reply
resolves to one candidate on the intended connection.

## Compute discovery arguments

Pass both the selected `space_id` and an explicit `category` to each call:

- `cognitivedb_compute_list`: use `default` for SQL Warehouses (including SQL
  analysis), `general` for Notebook Runtimes, or `all` for an unfiltered list.
- `cognitivedb_compute_type_list`: use `default` or `general`. To inspect
  types for both products, issue one call per category.

CPU and GPU describe compute classes. Choose the category from the product.
If the connector rejects a read-only list call for a missing category, correct
the arguments and retry that call.
