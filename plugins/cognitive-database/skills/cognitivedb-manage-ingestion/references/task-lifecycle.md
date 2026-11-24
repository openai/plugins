# Ingestion Task Lifecycle

Use these instructions for Cloud or Database Ingestion task and execution
lifecycle operations. Reject DAG tasks.

## Execution

- Resolve one exact Task or Execution. Read logs only for a `resultId` returned
  by that execution and only as much as diagnosis requires.
- Before execution, check every target: require `CREATE_DATA_ASSET` for a new
  Table and `MODIFY` for an existing Table. Stop if any mapping fails.
- Confirm the exact Task and write impact before publishing or executing. One
  confirmation may cover publishing and one immediate execution only when both
  actions are explicit. Verify publication before executing.
- Execute an ONLINE Task once, preserve the returned `executionId`, and wait on
  that ID. A timeout does not cancel it.
- For multiple independent Tasks on one Compute, when capacity is unknown,
  execute one confirmed representative Task and verify terminal success before
  submitting the remaining confirmed Tasks in bounded batches. Stop further
  submissions if the representative Task fails or remains unresolved. Preserve
  every ID and report completed, active, queued, and failed counts separately.
- On repeated structured queueing or resource-shortfall evidence, stop new
  submissions and hand the exact Compute and Executions to
  `cognitivedb-manage-computes`. Resume only after that Skill verifies the same
  Compute remains suitable or completes a confirmed lifecycle or specification
  change. Never resubmit an active or unknown execution, replace its Compute
  implicitly, or imply that an existing Task was rebound.

## Monitoring and Recovery

- After a wait timeout, inspect the exact Execution once. For a request to
  complete an import, wait again on the same ID until terminal or the configured
  deadline. If no deadline can be determined, stop after the second timeout.
  For submit-only requests, stop after the first timeout unless monitoring was
  requested.
- Cancel only a PENDING or RUNNING execution after confirming partial-write
  impact. Rerun only an eligible terminal execution of an ONLINE Task after
  confirming duplicate-write risk. Omit result IDs for Cloud reruns and use
  exact returned result IDs for Database reruns.
- Taking a Task offline neither cancels execution nor removes configuration.
  Delete only an OFFLINE Task with no active or unresolved execution, after
  confirming its exact paired `taskId` and `expectedName`.
- Inspect exact Task and Execution state before retrying an uncertain mutation.
  Report publication and execution separately, including returned table
  results, warnings, failures, and unresolved state.
