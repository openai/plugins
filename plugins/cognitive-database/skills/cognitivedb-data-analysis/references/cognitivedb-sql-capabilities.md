# CognitiveDB SQL Capabilities

Use this reference only when a CognitiveDB-specific SQL capability may be
needed or materially better than an equivalent PostgreSQL-compatible form, or
when the user requests a waiting or cancellation test.
This is an initial conservative catalog pending confirmation against the
current product contract. Treat an unlisted form as unverified, not unsupported.

## Selection Rules

- Prefer portable SQL when it expresses the same result without material loss.
- Use a listed CognitiveDB-specific form only after verifying its source,
  arguments, and required object types from live evidence.
- Do not probe syntax by submitting speculative SQL. If the necessary evidence
  is unavailable, use a portable equivalent or report the limitation.
- Do not emit internal planner operators as user-writable SQL.

## User-Writable Capabilities

| Capability | Use when | Known constraint |
| --- | --- | --- |
| `generate_series` | Generating an integer series materially simplifies the query | Verify accepted signatures |
| `range` | An exclusive-stop integer series is required and the function is verified | CognitiveDB/DuckDB-specific syntax |
| `read_parquet` / `parquet` | The user has identified an authorized Parquet source | Verify the registered function name, source URI, and arguments |
| `read_csv` | Direct analysis of an authorized CSV source is required | Verify explicit columns and accepted CSV options |
| `quantify_*` | The requested analysis matches a verified CognitiveDB function and signature | Verify the exact function and arguments |
| `PIVOT` | Pivoted output materially simplifies the requested result | Verify current syntax |
| `ASOF JOIN` | Temporal nearest-match semantics are explicitly required | Verify current syntax |
| Positional join | Row-position semantics are explicitly required | Verify current syntax |
| `SAMPLE` | The user requests sampling and exact syntax is verified | Verify current syntax |
| Percentage or expression `LIMIT` | The requested semantics cannot be represented by a constant row limit | Verify current syntax |

## Bounded Waiting Tests

- Use a verified native wait for a requested delay or cancellation test, not a
  large generated series, expensive joins, or business-table scans. This does not
  restrict workloads whose purpose is to measure actual computation.
- `pg_sleep(seconds)` has been verified with fractional seconds and a 60-second
  wait. A bounded example is `SELECT pg_sleep(60) AS waited`; choose a duration
  within the user's requested limit and retain the normal first-use approval.
- `sleep_ms(milliseconds)` has been verified with `SELECT sleep_ms(0) AS waited`.
  That establishes the zero-duration call, not nonzero timing or cancellability;
  use the verified `pg_sleep` example for a waiting test until nonzero
  `sleep_ms` behavior is validated. Do not substitute unverified `sleep()`.
- For cancellation testing, obtain evidence that this execution is running before
  requesting its cancellation. Follow SKILL.md for confirmation and bounded status
  tracking. Natural completion before cancellation does not validate cancellation;
  report that outcome instead of silently increasing the workload or repeating it.

## Planner-Only Names

Do not generate the following names as SQL syntax unless a separately verified
user-writable form exists:

- Empty, Dummy, Expression, and Column-data Scan
- Hash Join and Nested Loop Join
- Delim Join
- IEJoin and Piecewise Merge Join
- Mark, Single, Any, and Blockwise Join
- CTE ref and Top-N fusion

Generate supported source SQL instead.

## Ownership Boundaries

`INSERT`, `UPDATE`, `DELETE`, `MERGE`, and CTAS are not read-only analysis; route
them to `cognitivedb-write-data`. Route other supported DDL to
`cognitivedb-manage-data-assets`. `COPY TO` and database export are unsupported
when no loaded Skill explicitly owns them. Preserve the named Skill's
confirmation and verification contract.
