# Schema Lifecycle SQL

Use this reference only for Schema lifecycle operations that the live runtime
supports through `cognitivedb_sql_ddl_execute`. Prefer a dedicated
live Tool when it implements the same operation. Never use SQL to emulate
ownership, permission, or platform-only metadata behavior.

## Resolve and qualify the target

Bind the current Space and resolve one exact Catalog before preparing SQL. Use
an unquoted live name only when it is a safe regular identifier. Otherwise
require exact dialect-compatible SQL from the user or report that it cannot be
prepared safely; never guess quoting rules. Do not copy the angle-bracket
placeholders below into SQL or interpolate untrusted text.

Use `cognitivedb_catalog_schemas` for a known Catalog. When the requested Schema is
described but unnamed, use metadata search and resolve only direct
matches. Schema display-name or description updates require a dedicated live
Tool. When none is available, report that limitation; never emulate platform
metadata changes with SQL.

## Statement templates

Use the live DDL Tool description only to determine whether the requested
statement class is listed. Let the Tool validate the complete SQL syntax during
the single execution call because deployed dialects and clauses can differ.

```sql
CREATE SCHEMA <catalog_identifier>.<schema_identifier>
```

Before creation, verify that the exact qualified name does not exist. After
execution, verify that it appears under the intended Catalog.

```sql
DROP SCHEMA <catalog_identifier>.<schema_identifier>
```

Before deletion, inspect visible tables and dependencies, state recovery or
irreversibility, and confirm the exact qualified target. Do not add `CASCADE`
unless the user explicitly requests the known dependent-object impact and
confirms it. Verify absence after execution.

## Execute and recover

Prepare one ready approval question containing the exact statement, target,
Compute ID, and impact. Present it directly through the host's available interaction mechanism,
and call `cognitivedb_sql_ddl_execute` once only after the user explicitly approves.
The original request, an execution announcement, or Tool confirmation metadata
is not approval. Let the MCP server validate the complete AST and perform any
additional runtime confirmation. A change to the statement, target, Compute, or
impact requires a new check, question, and approval.
When the live Tool contract exposes no reliable pre-execution authorization
check, do not infer authorization or denial from role names or incomplete
entity-permission evidence. Available permission evidence may explain access,
but the execution result is authoritative. Report a permission denial without
retrying.

After a timeout or lost response, use the exact Query History entry and
independent Catalog metadata to determine whether the mutation occurred. If the
postcondition is not observable there, report the verification limitation.
Never blindly resubmit an unknown Schema mutation.
