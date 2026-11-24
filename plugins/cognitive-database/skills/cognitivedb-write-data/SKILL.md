---
name: cognitivedb-write-data
description: >-
  Safely execute confirmed INSERT, UPDATE, DELETE, MERGE, or CTAS statements in
  CognitiveDB with exact SQL, impact assessment, recovery, and verification.
metadata:
  version: "dev-1.17.1-codex.3"
---

# Write Data in CognitiveDB

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

Never invent workspace, objects, Compute settings, SQL dialect, credentials, or
confirmation behavior. Execute exactly one visible statement per inline call.

## Boundaries

- Own supported DML and CTAS. Load `cognitivedb-manage-data-assets` and hand
  off other inline SQL DDL or Catalog, Schema, and data-asset metadata lifecycle
  to it; never prepare or execute other DDL under this Skill.
- Reject view changes, maintenance statements, and unsupported DML.
- Never hide SQL in transactions, files, procedures, encoding, dynamic SQL, or
  side-effecting functions. Python may prepare SQL but never connect or write.
- Route simple file mapping to `cognitivedb-load-local-files`; use ingestion for
  bulk writes when exact review, privacy, atomicity, or retry safety is weak.
- Do not manually decompose an explicitly requested generated dataset or other
  multi-statement initialization when the task's SQL preparation workflow or an
  owning specialization supplies a complete deterministic SQL artifact and
  validation summary. Load
  `cognitivedb-manage-sql-files` and hand off that unchanged artifact for
  snapshot-bound asynchronous execution. Use inline DML when no such reviewed
  artifact workflow is available; never create a SQL File merely to hide row
  values, weaken impact review, or reduce confirmation. After an eligible
  artifact handoff, stop the inline workflow; resume it only if the SQL File
  owner rejects a specific statement as unsupported.
- Never bypass MCP with browser, drivers, shell clients, or direct APIs.
- Never expose secrets or unnecessary row values.

## Core Instructions

- When the user requests GPU execution or selects a GPU Compute, load
  `cognitivedb-gpu-workload-guidance` before proposing DML and follow its
  compatibility guidance.
- Gate the requested statement class through its live execution Tool and bind
  the current Space. Use a permission preflight only when that Tool contract
  defines it; never treat ownership, grants, or asset capabilities such as
  `edit_remote` as authorization on their own. Otherwise let the execution Tool
  make the authorization decision.
- Resolve the exact target, Compute, intended effect, and recovery. Inspect
  schema, keys, and visible dependencies. Load `cognitivedb-data-analysis` for
  bounded previews and counts; for UPDATE or DELETE, use the same predicate.
- Prepare one deterministic inline INSERT, UPDATE, DELETE, or MERGE statement
  with explicit columns and the narrowest predicate. Reject unbounded UPDATE or
  DELETE unless full-table impact and recovery are explicitly accepted.
- For CTAS, load `cognitivedb-gpu-workload-guidance`, resolve one exact absent
  destination table, and validate the source query and expected result grain
  through `cognitivedb-data-analysis` before presenting one exact statement.
  Treat creation and population as one mutation; never split them to avoid a
  confirmation.
- Check INSERT duplication and retry risk, UPDATE before/after and unrelated
  rows, DELETE recovery and post-count, and MERGE source uniqueness and branches.
- When the user explicitly requests a persistent change record or a retained
  artifact, reuse the specified format and destination; resolve missing material
  choices once. A request to show before/after values does not itself require
  creating a file or asking for a retention destination.
  Capture only requested keys and values. For a personal SQL File, load
  `cognitivedb-manage-sql-files` with the exact target, keys, and verified
  before/after values to retain as literal read-only content independent of
  the source object. That Skill owns file creation and read-back.
- Prepare one ready approval question containing the exact SQL, target, Compute
  ID, estimated impact, transaction boundary, and recovery or irreversibility.
  Identify the Compute only by name, ID, runnable status, and whether the user
  must choose one; omit generic GPU, performance, or sizing guidance unless the
  Compute choice requires it.
  For CTAS, include the new table and expected rows in the impact and state
  that the statement creates and populates it. Present that question directly
  through the host's available interaction mechanism, and do not call
  the mutation until the user explicitly approves it. The original
  request, an execution announcement, or the Tool's confirmation metadata is
  not approval. Any material change requires a new question and approval; a
  runtime-provided confirmation remains an additional gate.
- Execute the same statement once through the live DML Tool or, for CTAS, the
  live DDL Tool, and preserve its execution identity. On an
  uncertain or nonterminal result, preserve and manage only its exact execution;
  for a nonterminal result, check status at the Tool's recommended interval
  (otherwise use 2–10 second backoff), at most six times per turn within the
  user's wait budget or 60 seconds when absent. Stop on terminal status or
  non-actionable failure; at the limit, report the observed state and execution
  reference without claiming completion. For a requested cancellation, present the exact execution, target, and
  partial-write risk; present the confirmation directly, cancel once after
  approval, and read status once. Only `CANCELED` confirms cancellation. Never
  resubmit without proof that no execution started.
- Verify counts, constraints, intended state, and unchanged out-of-scope rows
  with bounded reads. For CTAS, verify the exact new table in metadata and
  hand off result-content verification to `cognitivedb-data-analysis`. Report
  returned permission denial without retry or speculation.
- A requested retained artifact is complete only after verified creation;
  conversation prose does not substitute for that artifact. If retention fails
  after the write, report both outcomes and never repeat the data mutation to
  repair retention. Do not create an artifact when retention was not requested.

## Compute Guardrails

- Bind execution to one exact runnable Compute. Reuse an exact user-selected
  Compute or a still-runnable session-approved Compute without reopening the
  choice.
- For `INSERT` or CTAS imports without a selected Compute, prefer compatible CPU,
  including one startable after separate confirmation. Ask before using a lone
  GPU candidate; a running GPU alone does not override CPU preference.
- For `INSERT` or CTAS imports, if the user explicitly chooses a GPU Compute, honor
  that choice and describe performance constraints supported by current evidence.
- Load `cognitivedb-manage-computes` when the user has not selected a Compute,
  CPU/GPU or specification guidance is required, multiple runnable candidates
  create a material choice, the selected Compute is incompatible or not runnable,
  or any lifecycle action is required. Combine its live product and sizing
  evidence with GPU-workload compatibility guidance; do not recommend GPU from
  SQL text alone. Treat Suspended with Auto Resume as runnable only when the live
  execution Tool contract supports automatic resume.
- Hand required Compute startup or replacement to that owner with the exact target
  and write need. Resume only with verified runnable state. Bind the final write
  confirmation to the selected Compute; SQL approval is not Compute approval.

## Allowed MCP Tools

- `cognitivedb_catalog_list`
- `cognitivedb_catalog_schemas`
- `cognitivedb_catalog_table_columns`
- `cognitivedb_catalog_tables`
- `cognitivedb_compute_describe`
- `cognitivedb_compute_list`
- `cognitivedb_query_history_list`
- `cognitivedb_query_history_show`
- `cognitivedb_space_current_get`
- `cognitivedb_sql_ddl_execute`
- `cognitivedb_sql_dml_execute`
- `cognitivedb_sql_execution_cancel`
- `cognitivedb_sql_execution_results_get`
- `cognitivedb_sql_execution_status_get`
