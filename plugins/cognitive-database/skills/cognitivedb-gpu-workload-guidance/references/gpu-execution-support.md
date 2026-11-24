# GPU Execution Support

## Internal Compatibility Evidence

Use this section only for compatibility decisions. Do not expose internal
execution-path or recovery details in user-facing responses.

- A successful query or a GPU Compute alone does not establish compatibility.
- Use structured compatibility evidence for the exact types, operators,
  functions, and argument shapes in the workload.
- Treat specialized table functions as function-specific paths; do not infer
  compatibility from their dispatch layer alone.

## Table Design

Prefer GPU-native column types where they preserve business semantics:

- `BOOLEAN`
- signed and unsigned 8/16/32/64-bit integers
- `HUGEINT` for storage and supported operations; not every INT128 operation is covered
- `FLOAT` and `DOUBLE`
- `DECIMAL` with precision up to 38
- `DATE`, `TIME`, and supported `TIMESTAMP` variants
- `VARCHAR`
- `BLOB` for transport; do not assume arbitrary binary values support string operations
- `LIST`, `ARRAY`, and `STRUCT` only where the required operators support their
  nested child types

Flag GPU risk for `VARIANT`, `UUID`, `MAP`, `UNION`, `TIME_TZ`, `BIT`, `ENUM`,
`UHUGEINT`, `SQLNULL`, and operations over incompletely supported nested types.
For `INTERVAL` arithmetic, the supported shape requires a non-NULL constant
with `months=0`; nested `INTERVAL` loading is unsupported.

## Ingestion

- Parquet and ordinary CognitiveDB or DuckLake Tables have native scan paths.
- Direct CSV GPU scanning requires explicit columns plus single-byte delimiter
  and quote settings; this does not describe the execution engine of an import task.
- Preserve destination types rather than relying on query-time string parsing
  or unsupported casts.
- Ingestion success does not prove that later queries will execute on GPU.

## Query Compatibility Constraints

Treat these common constructs as compatibility constraints before execution:

- `UNNEST` and `SAMPLE`
- native `ASOF JOIN`
- positional, any, and blockwise joins
- recursive CTE and `PIVOT`
- IEJoin or piecewise merge plans produced by multiple range conditions
- `EXCEPT ALL`, `INTERSECT ALL`, and general table-in/table-out functions
- unsupported window functions such as `percent_rank`, `cume_dist`, `ntile`,
  `first_value`, and `nth_value`
- direct window `FILTER`, aggregate-argument `ORDER BY`, `EXCLUDE`, and the
  third `lead` or `lag` default argument
- partition windows without `ORDER BY` beyond supported basic aggregates
- residual non-equality joins without an equality key, complex-type join keys,
  and unsupported join-type or condition-count combinations
- aggregates whose input type, ordering, `FILTER`, DISTINCT, executor-splitting,
  or merge requirements are unsupported
- unsupported function overloads, input types, or required-constant arguments
- bound parameters that reach the GPU expression executor
- `generate_series` or `range` arguments outside verified constant `BIGINT` forms
- expression `LIMIT`, percentage `LIMIT`, and unsupported nested-type operations

Evaluate the full query plan as one compatibility unit. Treat
single-GPU, distributed GPU, and specialized fused table-function support as
distinct execution paths. A single physical input or intermediate column may
also be rejected above the underlying 32-bit row-index limit.
