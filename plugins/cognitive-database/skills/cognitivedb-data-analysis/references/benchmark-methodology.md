# Benchmark Methodology

Use this guidance for performance comparisons, not ordinary business analysis.

## Define the Measurement

- Identify the workload, dataset and scale, table layout, query count, Compute,
  concurrency, and measurement boundary supported by current evidence.
- Before the baseline, bind one exact compatible Compute through the analysis
  Skill's first-use approval. When Compute type or specification is the factor
  under test, explicitly select and approve every compared Compute ID; never
  carry approval across IDs or choose a comparison candidate implicitly.
- Distinguish engine execution time, per-query wall time, and complete suite
  wall time. Do not compare unlike boundaries or present suite time as database
  execution time.
- Before promising timing or variance, identify the structured timing evidence
  exposed by the live contract, including Query History when an execution provides
  a history reference. If unavailable, disclose that limitation; do not fetch
  result rows merely to look for undocumented timing fields.
- Calculate benchmark summaries such as mean, variance, and speedup from the
  complete structured execution evidence for the compared runs; retain execution
  identities, units, measurement boundaries, sample counts, and missing-run coverage.
  These calculations do not require another business-data query or writing timing
  evidence into database tables. Missing timings cannot support a complete-run summary.
- Record the observed result, expected result, and run-to-run variance from
  repeated comparable runs. One faster run is not sufficient evidence of an
  improvement.
- Keep query semantics, data, cache state, concurrency, Compute, and measurement
  boundaries stable. Change one factor per comparison when its individual
  effect can be measured.

## Separate Observable Costs

- Keep execution-status coverage, timing coverage, and data-correctness checks
  distinct for each run. Prefer a supported summary covering every statement
  over result rows when it supplies the required evidence. Fetch rows only for
  a defined correctness check or when required by the live contract; do not
  assume a summary or projection capability that the contract does not expose.
- Use structured query evidence for execution duration and queue time only when
  those fields are available.
- Treat client startup, connection establishment, orchestration, output writing,
  and external timing commands as suite overhead, not database execution.
- When suite overhead may dominate, report the limitation and hand inspection
  of the external benchmark harness back to the user or an applicable code
  workflow. Do not inspect or modify host scripts through CognitiveDB tools.

## Diagnose Without Guessing

- Compare Query History and bounded query results for the exact executions when
  available. Do not infer import history, storage-file layout, host
  configuration, or log level from elapsed time.
- Use a semantics-preserving query rewrite only when it tests a stated
  hypothesis. Keep the original query as the baseline and disclose any changed
  execution or measurement boundary.
- If current tools cannot observe the suspected layer, state the evidence gap.
  Do not substitute browser automation, host shell access, configuration SQL,
  or undocumented interfaces.

## Report

Report the baseline and comparison distributions, exact changed factor,
measurement boundary, and remaining uncertainty. Distinguish query optimization
from benchmark-harness optimization.
