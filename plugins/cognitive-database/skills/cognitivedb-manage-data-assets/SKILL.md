---
name: cognitivedb-manage-data-assets
description: >-
  Inspect and manage CognitiveDB Catalogs, Schemas, Tables, and other supported
  Catalog-contained data assets, including metadata lifecycles and non-CTAS SQL
  DDL with exact targets, confirmed mutations, and read-back verification.
metadata:
  version: "dev-1.19.0-codex.1"
---

# Manage CognitiveDB Data Assets

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

Never invent IDs, fields, cascade behavior, ownership, or workspace context.
Treat the live SQL DDL Tool description and input schema as authoritative for
supported statement classes, syntax, and validation.

## Boundaries

- Own Catalog/Schema lifecycle and metadata plus live-supported SQL DDL for
  Catalog-contained data assets, except CTAS. Route CTAS to
  `cognitivedb-write-data` for its combined table-creation and data-write impact.
- Route ownership and permissions to `cognitivedb-administer-access`, Computes to `cognitivedb-manage-computes`, and SQL files elsewhere.
- Prefer dedicated MCP tools. Never use browser or HTTP.

## Core Instructions

- Bind the selected Space. For an operation on an existing object, resolve one
  exact Catalog, Schema, or data asset. Stop on zero, inconsistent, or cross-Space
  matches. Disambiguate multiple matches with the user before acting.
- Identify the signed-in user from `cognitivedb_user_current_get` when identity matters;
  this profile read needs no Space and does not establish roles or capabilities.
  The current Space's creator identifies that resource's creator, not the user.
- For creation-history claims, require an explicit creator field or authoritative
  creation audit for each object. Load `cognitivedb-administer-access` for audit
  evidence when needed; if it cannot establish the creator, report unknown.
  Current ownership neither proves nor disproves
  who created it, including after ownership transfer. Check Catalogs and Schemas
  independently; do not infer a Schema's creator from its parent Catalog.
  If creator evidence is unavailable, mark creation history unknown. An ownership
  inventory may be offered only as a clearly labeled alternative, not as the
  answer to which objects the user created.
- Read an exact supplied Catalog or Schema path directly. For a named asset
  without a complete path, search using its supplied name and verify the full
  returned path before acting.
- If the supplied Catalog or Schema scope cannot be enforced by search, browse
  within that scope.
- For a business topic or keyword with no selected source, use
  `cognitivedb_catalog_metadata_search` to find candidates. Search across Catalogs
  only within the user's selected scope. Group candidates by Catalog and Schema,
  disclose incomplete or truncated coverage, and let the user select the source.
- For an explicit hierarchy or inventory request, use the Catalog, Schema, and
  Table list tools. Search results do not establish a complete hierarchy.
- When the user has not chosen a target for a new Table, prefer a suitable
  Catalog whose live owner matches the current user. Otherwise disclose the
  recommended Catalog's owner or that ownership is unverified. Visibility and
  effective capabilities do not establish ownership.
- For `CREATE TABLE` without `AS SELECT` or table-schema design, load
  `cognitivedb-gpu-workload-guidance` before presenting the DDL and follow its
  compatibility guidance.
- Before a Catalog mutation read [Catalog lifecycle
  details](references/catalog-lifecycle.md). Reject duplicate creation, submit
  only requested update fields, and reject empty updates.
- Before every Catalog, Schema, or data-asset mutation, including creation,
  resolve the exact operation first. For inline DDL, prepare the statement and
  Compute before asking; target selection alone is not execution approval.
  Present one approval question binding the target and change, including
  visible dependencies, cascade behavior, and impact when applicable. Present
  that question directly through the host's available interaction mechanism, and do not call
  the mutation until the user explicitly approves it. The original request, an
  execution announcement, or Tool confirmation metadata is not approval; a
  runtime-provided confirmation remains an additional gate. Stop when unknown
  cascade behavior materially changes the risk. Reuse an existing explicit
  approval for that pending operation with identical statement, target, Compute, and impact
  within the current task; do not ask a second generic approval before the exact
  DDL approval. Preserve any additional live runtime confirmation.
- Before Catalog deletion, inspect the dedicated impact result for contained
  objects, grants, affected grantees, and current-Space visibility. Include that
  evidence in confirmation and do not substitute generic discovery.
- Use dedicated lifecycle tools when available. For Schema SQL, read [Schema
  lifecycle SQL](references/schema-ddl.md). Execute SQL DDL only when its class
  is explicitly supported by the live tool description.
- For an inline DDL mutation, show and confirm one exact statement and execute
  it once unchanged. Do not manually decompose an explicitly requested
  multi-statement initialization or migration when the task's SQL preparation
  workflow or an owning specialization supplies a complete deterministic SQL
  artifact and validation summary. In
  that case, load `cognitivedb-manage-sql-files` and hand off the unchanged
  artifact for snapshot-bound asynchronous execution. Use inline DDL when no
  such reviewed artifact workflow is available; never create a SQL File merely
  to hide statements or reduce confirmation. After an eligible artifact handoff,
  stop the inline workflow; resume it only if the SQL File owner rejects a
  specific statement as unsupported.
- Bind inline SQL DDL execution to one exact runnable Compute. Reuse an exact
  user-selected Compute or a still-runnable session-approved Compute without
  reopening the choice. Load `cognitivedb-manage-computes` when the user has not
  selected a Compute, CPU/GPU or specification guidance is required, multiple
  runnable candidates create a material choice, the selected Compute is
  incompatible or not runnable, or any lifecycle action is required. Treat
  Suspended with Auto Resume as runnable only when the live DDL contract supports
  automatic resume. Bind the DDL confirmation to the selected Compute; SQL
  approval is not Compute approval.
  Treat the result as authoritative for authorization and validation. Never
  treat ownership, grants, or asset capabilities such as `edit_remote` as SQL
  DDL authorization unless the live DDL Tool contract defines that preflight.
  Preserve and manage only its exact execution reference. Read status once per turn. For a requested
  cancellation, present the exact execution, target, completed-statement impact, and
  partial-change risk; present the confirmation directly, cancel once after
  approval, and read status once. Only `CANCELED` confirms cancellation. Never
  resubmit an unknown execution.
- Verify each mutation from the exact target's live metadata or absence. Do not
  use Query History to recover a dedicated Catalog-tool mutation, claim hidden
  dependencies, or retry an uncertain result without exact state evidence.

## Allowed MCP Tools

- `cognitivedb_catalog_create`
- `cognitivedb_catalog_delete`
- `cognitivedb_catalog_delete_impact_check`
- `cognitivedb_catalog_list`
- `cognitivedb_catalog_metadata_search`
- `cognitivedb_catalog_schemas`
- `cognitivedb_catalog_table_columns`
- `cognitivedb_catalog_tables`
- `cognitivedb_catalog_update`
- `cognitivedb_compute_describe`
- `cognitivedb_compute_list`
- `cognitivedb_query_history_list`
- `cognitivedb_query_history_show`
- `cognitivedb_space_current_get`
- `cognitivedb_space_list`
- `cognitivedb_sql_ddl_execute`
- `cognitivedb_sql_execution_cancel`
- `cognitivedb_sql_execution_results_get`
- `cognitivedb_sql_execution_status_get`
- `cognitivedb_user_current_get`
