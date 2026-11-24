# Cloud Ingestion

Use these instructions for S3 or Azure Blob Parquet sources.

## Boundaries

- Cloud Ingestion copies source rows into a target. Never infer directory
  recursion, multi-file fan-in, or write modes absent from the live contract.
- For an explicitly requested zero-load registration, generate but do not
  execute one reviewed call per existing target table:

  ```sql
  SELECT * FROM coglake_add_data_files('<catalog>', '<table>',
      ['<exact-parquet-path>', ...], schema => '<schema>');
  ```

  Require the exact Catalog, Schema, existing Table, and complete Parquet file
  list. An owning specialization may instead supply fixed provenance and future
  tables for a deterministic initialization artifact; review that mapping
  without requiring those future Tables to exist or regenerating the complete
  artifact. Include every intended bucket file in the same call for a bucketed
  Table. Never claim registration copies data or execute it through ordinary DML.

## Source Discovery

- If a cloud Parquet import leaves copy behavior ambiguous, ask once whether to
  copy through Cloud Ingestion or generate zero-load registration SQL.
- Browse only with one verified S3 or Azure Blob Connection and returned paths.
- For preview or task mapping, preview one exact Parquet file or directory and
  preserve returned source path, resolved path, sampled file, columns, types,
  and mappings. Stop mapping when types are absent or preview evidence is unsafe.
- Use a returned common parent for multiple files only when they form one
  logical table, including bucket-organized children. Do not assemble unrelated
  paths or create one task per child when the directory is the intended source.
- For a dataset root with distinct logical-table child directories, keep each
  child as a separate logical source. Preview each source selected for task
  creation; a browse-only request needs no destination mapping or task proposal.
- Treat bucket directory names as source organization only. Report target
  distribution only from independent target metadata.

## Copied-Load Task Creation

Apply this section only when creating Cloud Ingestion tasks, not for source
discovery or zero-load SQL generation.

- Require Catalog, Schema, Table, task name, and Compute. For multiple tables,
  recommend valid child-directory names and show one grouped proposal with
  every source-to-table mapping, task name, and Compute for confirmation.

- Without a selected Compute, recommend a compatible runnable CPU Compute. Ask
  before using a lone GPU candidate. A Suspended Compute with Auto Resume is
  runnable only when task creation and execution support automatic resume.
- If the confirmed Compute fails its preflight, stop and propose one verified
  alternative. Require fresh confirmation for the changed Compute.
- Confirm file or directory source, sampled-file evidence, destination,
  Compute, full-load effect, schema assumptions, and impact. Create once per
  source and target. If creation returns warnings, show them and make only one
  confirmed follow-up with the exact acknowledgements.
