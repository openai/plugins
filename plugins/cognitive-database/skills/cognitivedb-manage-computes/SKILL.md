---
name: cognitivedb-manage-computes
description: >-
  Select, inspect, and manage CognitiveDB Compute resources, including
  workload-based CPU/GPU and specification guidance, connection details,
  monitoring, configuration, lifecycle transitions, cache cleanup, and deletion.
metadata:
  version: "dev-1.14.0-codex.1"
---

# Manage CognitiveDB Computes

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

Never invent fields, enums, force flags, IDs, or transitions. Never substitute
SQL, browser, or HTTP.

## Boundaries

- Own Compute selection, inspection, configuration, lifecycle, cache cleanup,
  and Notebook Runtime SQL binding. Do not manage data, Catalogs, connections,
  ingestion, access, quotas, or SQL files. Route GPU query compatibility and
  table design to `cognitivedb-gpu-workload-guidance`.
- Return endpoint details only for one exact Compute and Catalog and never claim
  that credentials are included. Use monitoring only for the current activation;
  route cross-activation investigation to Query History.
- Manual suspension is unavailable. Do not substitute stop or change
  automatic suspension settings for a manual suspension request.

## Core Instructions

- Bind the current Space. Before mutating an existing Compute, resolve its
  immutable ID and current state. Describe a supplied ID directly. If the ID
  is missing, list and disambiguate. Stop on conflicting, missing, or cross-Space
  evidence.
- Read [create](references/create.md) for SQL Warehouse or Notebook Runtime
  creation and for Notebook Runtime SQL binding,
  [selection](references/selection.md) for workload, CPU/GPU, or specification
  recommendations,
  [update/default](references/update-and-default.md) for update or set-default,
  [transitions](references/lifecycle-transitions.md) for start, stop, or cache
  cleanup, and [delete/recovery](references/delete-and-recovery.md) for delete
  or an ambiguous mutation result. Load the reference for the current operation.
- For creation, reject a duplicate name. Clarify SQL Warehouse versus Notebook
  Runtime when the workload does not establish the product.
- Base every recommendation on current product, specification, availability,
  sizing-guide, and configuration evidence. Preserve the selected `specCode`;
  do not invent a separate GPU-count argument or promise a capacity limit.
- For update or default selection, validate the requested value against current
  live options and show the exact diff.
- Before a mutation, confirm the exact target, change, and known cost or
  availability impact. Execute once and verify using the operation reference.
  Report the exact ID, effective change, observed state, and any uncertainty.

## Allowed MCP Tools

- `cognitivedb_catalog_list`
- `cognitivedb_compute_clear_cache`
- `cognitivedb_compute_create`
- `cognitivedb_compute_delete`
- `cognitivedb_compute_describe`
- `cognitivedb_compute_endpoint_details`
- `cognitivedb_compute_global_configuration_get`
- `cognitivedb_compute_list`
- `cognitivedb_compute_monitoring_list`
- `cognitivedb_compute_set_default`
- `cognitivedb_compute_spec_list`
- `cognitivedb_compute_start`
- `cognitivedb_compute_stop`
- `cognitivedb_compute_type_list`
- `cognitivedb_compute_update`
- `cognitivedb_notebook_runtime_create`
- `cognitivedb_notebook_runtime_sql_bind`
- `cognitivedb_space_current_get`
