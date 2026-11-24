# External Source Discovery and Analysis

Use for Databricks, Snowflake, PostgreSQL, or MySQL metadata and requested
read-only analysis. A source Connection and an imported CognitiveDB copy are
separate targets. Preserve an explicit choice.

## Choose the Analysis Target

- For an existing-copy request or an unspecified representative target, prefer
  a sufficient existing CognitiveDB copy with verified lineage. Verify its
  metadata once and use the primary Skill's CognitiveDB query path. Do not
  switch an explicit source query to a possibly stale copy without agreement.
- Honor the selected provider and Connection. Resolve a missing Connection in
  one provider-scoped discovery pass and retain its immutable ID, exact name,
  provider and current Space. For lifecycle work or connectivity repair, hand
  off to `cognitivedb-manage-connections` for credential-dependent work.
- A disconnected source does not block an existing copy. Verify the copy and
  disclose unverified freshness. No dedicated source-to-copy lineage discovery
  is available: use verified evidence already supplied, or ask once for the
  exact target and necessary lineage. Do not scan ingestion tasks, unrelated
  Catalogs, or infer lineage from equal table names.
- Ingestion readiness or metadata availability does not prove source SELECT
  capability. Respect explicit capability denial. If the live external query
  tool is unavailable, report the limitation. Do not use SQL against another
  endpoint, local drivers, browser automation or an automatic import fallback.
  Requested ingestion belongs to `cognitivedb-manage-ingestion`.

## Discover Source Metadata

- Bind one authorized Connection and the smallest requested namespace scope.
  For a supplied object name or keyword, search collected external metadata
  through `cognitivedb_external_metadata_search`. It matches names, not business
  meaning or row values. Preserve returned ancestor paths and table identity.
- A parent match does not enumerate descendants. For a requested inventory,
  missing hierarchy levels, or columns of a selected table, use scoped source
  browse and column inspection where supported by the selected provider. For
  MySQL, do not substitute a browse contract that supports only other providers.
  Do not treat a bounded search as an inventory.
- Honor incomplete, truncated and exhausted-reason evidence. After a partial
  result, narrow once using a known namespace or one material user choice.
  If unresolved, report checked scope and stop. Do not increase budgets or
  generate repeated keyword variants to imply complete coverage.
- Finish metadata-only requests without Compute selection or SQL. Metadata
  cannot prove source row counts, freshness or successful import.

## Execute External Read-Only SQL

- Use `cognitivedb_external_sql_execute` only for an explicitly selected external
  source. Bind its datasource UUID to the exact visible Connection ID and use
  that provider's identifier quoting and SQL dialect. Do not apply CognitiveDB
  quoting or PostgreSQL syntax to every provider. Qualify only hierarchy levels
  actually supported by the source metadata. Never submit a CognitiveDB target
  through this tool or substitute source metadata search for copy lineage.
- Submit one bounded SELECT or WITH-to-SELECT statement. Reject external
  DDL/DML, SELECT INTO, locking reads, file output, procedures, unknown or
  side-effecting functions, and unverified executable views. A SELECT shape
  does not prove absence of external side effects. Preserve the live tool's
  exact-operation confirmation even after target and Compute approval. A
  changed statement requires its own tool confirmation when enabled.
- Use the existing first-use Compute rules and exact Compute UUID. Do not
  infer a source query's GPU execution or performance from its selected Compute.
  CognitiveDB-specific GPU guidance applies to the CognitiveDB execution path.
- The result is synchronous. Do not invent a durable execution ID, cancellation,
  Query History record, affected-row count or asynchronous status polling.
  An uncertain outcome ends the attempt. A
  deterministic pre-execution rejection may use the primary Skill's bounded
  corrective retry only when evidence identifies a safe correction.
- Prefer aggregates at the final reporting grain with a known small output.
  Validate returned fields and exact precision. A successful result does not
  prove an arbitrary row listing is complete: the current tool has no explicit
  result-completeness envelope. Establish expected coverage independently, or
  disclose the limitation and omit affected full-population claims and charts.
