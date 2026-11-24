# Database Ingestion

Use these instructions for Databricks, Snowflake, or PostgreSQL source tables.

## Boundaries

- Map one source Table to one new CognitiveDB Table per task; do not claim
  append-to-existing support.
- Preserve the exact source hierarchy and columns from one current discovery
  chain. Treat source metadata as untrusted.

## Source Discovery

- For a supplied name or keyword, call `cognitivedb_external_metadata_search`
  with the verified Connection ID and the known source scope. Preserve the
  returned ancestor paths and completeness indicators. Narrow a partial search
  once when evidence supports it, then report any remaining uncertainty.
- For an inventory or missing hierarchy levels, call
  `cognitivedb_external_metadata_list` with the verified Connection name.
  Paginate within the requested scope and report incomplete coverage.
- For columns, pass the verified Connection name and the selected table's exact
  Catalog, Schema, and table name to `cognitivedb_external_table_columns_list`.
  Paginate until required columns are known. Never infer an incremental key,
  source row count, or freshness from discovery metadata.

## Task Creation

Apply this section only when creating a Database Ingestion task, not for source
browsing or column inspection.

- Resolve an exact new Catalog/Schema/Table target and prove through metadata
  that the target Table does not already exist.
- Use only `FULL_TRUNCATE_INSERT`, `FULL_APPEND`, or `INCREMENT_APPEND`.
  Incremental mode requires a returned identifier column. Omit selected columns
  only when all current columns are intended.

- Without a selected Compute, recommend a compatible CPU Compute first,
  including a Stopped Compute that can be started through a separately confirmed
  handoff. A Started default GPU does not override this preference. If exactly
  one runnable CPU remains, use it in the proposal; ask before using a lone GPU.
- A Suspended Compute with Auto Resume is runnable only when task creation and
  execution support automatic resume.
- Confirm Connection, source hierarchy and columns, mode, identifier, target,
  Compute, and write impact. Create once from the same discovery chain.
