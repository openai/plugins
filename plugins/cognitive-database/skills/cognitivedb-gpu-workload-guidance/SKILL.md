---
name: cognitivedb-gpu-workload-guidance
description: >-
  Guide CognitiveDB table design, ingestion mapping, and SQL construction for
  GPU-compatible execution and avoid known unsupported constructs while keeping
  internal execution-routing behavior out of user-facing responses. Use when the
  user requests GPU execution, GPU-oriented design, or GPU compatibility review.
metadata:
  version: "dev-1.5.1"
---

# CognitiveDB GPU Workload Guidance

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

Guide GPU-compatible design and SQL without owning Catalog, ingestion, Compute,
or SQL mutations.

## Boundaries

- Provide GPU compatibility guidance only. Route read-only SQL to
  `cognitivedb-data-analysis`, Compute operations to
  `cognitivedb-manage-computes`, CTAS to `cognitivedb-write-data`, other DDL to
  `cognitivedb-manage-data-assets`, cloud files or external database tables to
  `cognitivedb-manage-ingestion`, or local files to
  `cognitivedb-load-local-files`.
- Route CPU/GPU Compute selection, specification choice, and resource lifecycle
  operations to `cognitivedb-manage-computes`.
- Do not expose internal execution routing, recovery behavior, strict execution
  modes, or related evidence in user-facing responses.
- Do not promise GPU-native execution from Compute selection alone.
- Never enable strict execution modes or change session configuration unless an
  owning live Tool explicitly supports it and the user requests it.

## Core Instructions

- Read [GPU execution support](references/gpu-execution-support.md) when table
  types, ingestion mappings, SQL operators, or functions affect the request.
- For table design, distinguish the user's execution intent:
  - When GPU-native execution is required, identify incompatible or partially
    supported column types before presenting the schema. Do not claim
    compatibility when the required later operations are unknown.
  - When GPU execution is preferred, recommend GPU-native types where business
    semantics are preserved.
  - When execution intent is unspecified, do not require a CPU/GPU choice.
    Do not add unsolicited GPU compatibility commentary.
- Treat GPU compatibility as a property of later queries and operations, not of
  `CREATE TABLE` execution itself.
- For ingestion, preserve GPU-native destination types and flag mappings that
  introduce unsupported types, lossy casts, or runtime parsing.
- Before query execution, use known GPU-native limitations to construct a
  compatible statement when semantics can be preserved.
- Suggest a GPU-compatible rewrite only when it preserves the requested result.
  Otherwise retain the original semantics without exposing internal routing.
- Keep execution-path evidence internal. Report the requested result, supported
  compatibility conclusion, or actionable query limitation.
- For performance comparisons, keep the execution path, data, query semantics,
  Compute, cache state, concurrency, and measurement boundary comparable. Do
  not attribute a timing change to GPU execution unless structured evidence
  verifies comparable routing; do not expose that routing evidence.
