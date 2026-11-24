# Compute Selection

Use this reference when the user asks which Compute, CPU/GPU type, or
specification to use; when creation has no uniquely determined compatible live
category, type, or specification; or when an owning Skill hands off a material
choice, compatibility problem, or verified resource shortfall. The product
guidance is based on [Manage compute resources](https://docs.transwarp-cloud.com/compute/manage-resources).

## Match the Runtime

- Use a Data Warehouse product for SQL queries, SQL notebook cells, SQL-backed
  dashboards, BI, and ingestion-related SQL execution.
- Use a General Compute product for Python notebook cells or another non-SQL
  runtime. Do not assume that a General Compute product supports SQL or GPU.
- If the workload language is unclear and changes the category, ask for it
  before recommending a product.

## Select CPU or GPU

- For data import, including `INSERT INTO ... SELECT`, prefer a compatible
  CPU Compute, including one that can be started with separate confirmation.
  Recommend GPU only when the user explicitly requests it or live evidence
  shows that CPU cannot meet the workload requirements.
  An already-running GPU Compute alone is not a reason to prefer it. For
  data imports, honor an explicit GPU choice and describe performance
  constraints supported by current evidence.
- For other workloads, honor an explicit user choice or a workload-owning
  Skill's Compute-class or specification-family preference. Otherwise select
  CPU or GPU from current workload requirements and live compatibility evidence.
- For other suitable analytical workloads, consider GPU where active data size,
  latency, repeated BI access, large joins, complex aggregations, or concurrency
  make acceleration material. SQL keywords alone do not establish suitability.
- Ask only for a missing factor that changes the recommendation, such as the
  runtime language, approximate active data size, concurrency, latency target,
  or representative query shape.
- Route operator, type, and table-design compatibility analysis to the matching
  GPU-workload guidance Skill. Keep internal execution-routing behavior out of
  the recommendation.

## Select a Live Specification

- Treat a Started Compute as runnable. Treat a Suspended Compute with Auto Resume
  as usable without a lifecycle transition only when the owning execution Tool's
  live contract supports automatic resume; otherwise hand off an explicit start.
  Never infer usability from the status label or Auto Resume setting alone.
- Use `computeClass`, labels, and the exact product `type` returned by live
  product discovery. Never derive a product type from a display label.
- Use specification-family `description`, `default`, and `recommended` as
  platform guidance, not as a performance or capacity guarantee.
- Select only a spec whose availability was evaluated and is currently true.
  Report its `unavailableReason` when excluding a requested option.
- For GPU, match the requested card count to the returned `gpu` value and pass
  that entry's exact `specCode`. Card count may already be encoded in the code;
  never invent a separate create or update argument.
- When `sizingGuide` provides `maxActiveDataGb`, compare it with the user's
  approximate active data and label the result as planning guidance. Do not
  extrapolate missing card counts or claim a guaranteed maximum. Nominal dataset
  scale, compressed storage size, and a query working set are different measures;
  do not substitute one for another without workload evidence.
- Without sufficient live sizing evidence, present the supported available
  choices and the missing decision evidence instead of claiming an exact fit.
- For an existing workload, retain an exact compatible runnable user-selected
  or session-approved Compute unless the user requests reconsideration or live
  evidence shows a material availability, compatibility, or resource problem.
- Treat repeated resource exhaustion, queueing, memory pressure, spill, or a
  missed latency or concurrency target as sizing evidence only when exposed by
  live execution or monitoring results. First preserve semantics and remove
  avoidable query or batching pressure; then compare supported available specs.
  Do not resize from elapsed time, a single timeout, or a specification name alone.
- Apply the live default, minimum, maximum, and step values for automatic
  suspension settings. Describe retained cache only when supported by live
  configuration evidence.
- For a requested cost comparison, load `cognitivedb-inspect-usage-and-billing`
  to explain billing or metering availability, then finish the supported
  recommendation using the available evidence.
- Compare cost only using compatible units, billing periods, and workload evidence.
  Historical usage is not a quoted rate for another specification. Without comparable
  rates or measured consumption, do not rank options as cheaper or more expensive,
  including qualitative CPU/GPU or card-count rankings. Disclose missing quota,
  consumption, or price; do not derive them from specification names or card counts.

## Present and Verify the Recommendation

When presenting multiple choices with a clear recommendation, mark the
recommended option as `(Recommended)` and list it first. Do not communicate the
recommendation only in separate prose.

Present the resource category, CPU/GPU type, specification family, GPU count,
active-data guidance, availability, selection reason, and automatic-management
settings that live evidence supports. State any missing quota or cost evidence.

After a representative workload runs, use monitoring evidence internally when
evaluating the recommendation. Report duration, failures, and actionable
resource findings, but do not expose engine routing or fallback details.
Recommend reconsidering the product or specification only from observed
evidence. If GPU memory-pool or cross-activation evidence is unavailable, do not
infer utilization.
