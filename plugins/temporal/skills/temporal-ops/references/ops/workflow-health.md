# Workflow Health Queries

Data-plane commands for **finding** unhealthy Workflow Executions.
Backend-agnostic (works on Temporal Cloud and self-hosted).

> **Scope.** This file covers *locating* stuck/hung/failed workflows.
> To *diagnose why* a specific workflow is stuck, see `../triage/workflow-stuck.md`.

---

## 1. List Filter fundamentals

`temporal workflow list` accepts an optional `--query` (`-q`) flag whose value is an SQL-like List Filter string.

### Supported operators

`=, !=, >, >=, <, <=` | `AND, OR, ()` | `BETWEEN ... AND` | `IN` | `STARTS_WITH`

Additional filter expressions: `IS NULL`, `IS NOT NULL`

> **ORDER BY is not supported in Temporal Cloud.**
> The default ordering is `ClosedTime DESC NULL FIRST`, `StartTime DESC`.

### Key Search Attributes for health queries

All of the following are default (built-in) Search Attributes:

| Attribute | Type | Notes |
|-----------|------|-------|
| `ExecutionStatus` | Keyword | Current state. Values: `Running`, `Completed`, `Failed`, `Canceled`, `Terminated`, `ContinuedAsNew`, `TimedOut` |
| `WorkflowType` | Keyword | The type of Workflow |
| `WorkflowId` | Keyword | Identifies the Workflow Execution |
| `TaskQueue` | Keyword | Task Queue used by Workflow Execution |
| `StartTime` | Datetime | Time the Workflow Execution started |
| `CloseTime` | Datetime | Time the Workflow Execution completed (closed workflows only) |
| `ExecutionTime` | Datetime | Actual begin time; differs from `StartTime` for cron/retry |
| `ExecutionDuration` | Int | Time to run in nanoseconds (closed workflows only) |
| `HistoryLength` | Int | Event count (closed workflows only) |
| `HistorySizeBytes` | Long | Size of Event History |
| `StateTransitionCount` | Int | Number of state persists (closed workflows only) |

Search Attribute names are case sensitive.

Datetime attributes accept RFC3339Nano strings (e.g. `"2024-01-15T10:00:00Z"`) or epoch-nanosecond integers.

`ExecutionDuration` accepts nanosecond integers, Golang duration format, or `"hh:mm:ss"` format.

---

## 2. Listing workflows by status

### All running workflows

```
temporal workflow list \
    --query "ExecutionStatus = 'Running'"
```

### All failed workflows

```
temporal workflow list \
    --query "ExecutionStatus = 'Failed'"
```

### All timed-out workflows

```
temporal workflow list \
    --query "ExecutionStatus = 'TimedOut'"
```

### All terminated workflows

```
temporal workflow list \
    --query "ExecutionStatus = 'Terminated'"
```

### Non-running workflows (any closed status)

```
temporal workflow list \
    --query "ExecutionStatus != 'Running'"
```

---

## 3. Finding stuck/long-running workflows

### Running longer than a time threshold

Workflows that started more than 24 hours ago and are still running:

```
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND StartTime < '2024-01-14T00:00:00Z'"
```

Replace the timestamp with the appropriate cutoff for your use case.

### Running workflows on a specific Task Queue

```
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND TaskQueue = 'my-task-queue'"
```

### Running workflows of a specific type

```
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND WorkflowType = 'MyWorkflow'"
```

### Combining conditions

```
temporal workflow list \
    --query "WorkflowType = 'OrderWorkflow' AND ExecutionStatus = 'Running' AND StartTime < '2024-01-14T00:00:00Z'"
```

### Workflows started in a time window

```
temporal workflow list \
    --query "StartTime BETWEEN '2024-01-01T00:00:00Z' AND '2024-01-02T00:00:00Z'"
```

### Matching Workflow IDs by prefix

```
temporal workflow list \
    --query "WorkflowId STARTS_WITH 'order-'"
```

`STARTS_WITH` is only available for Keyword Search Attributes.

---

## 4. Counting workflows

`temporal workflow count` returns a count of Workflow Executions regardless of execution state. Use `--query` to filter:

```
temporal workflow count \
    --query "ExecutionStatus = 'Running'"
```

```
temporal workflow count \
    --query "ExecutionStatus = 'Failed'"
```

```
temporal workflow count \
    --query "ExecutionStatus = 'Running' AND TaskQueue = 'my-task-queue'"
```

Use count to detect anomalies: a rising count of `Running` workflows with a stable `Failed` count may indicate workers are not processing tasks (check poller status below).

---

## 5. Describing a specific workflow

`temporal workflow describe` displays information about a specific Workflow Execution:

```
temporal workflow describe \
    --workflow-id YourWorkflowId
```

Key flags:

| Flag | Description |
|------|-------------|
| `--workflow-id`, `-w` | **(required)** Workflow ID |
| `--run-id`, `-r` | Run ID (optional, defaults to latest run) |
| `--reset-points` | Show auto-reset points only |
| `--raw` | Print properties without format changes |

The output includes execution status, start/close times, task queue, workflow type, search attributes, and pending activities/child workflows.

### Viewing Event History

`temporal workflow show` displays the full Event History:

```
temporal workflow show \
    --workflow-id YourWorkflowId
```

Key flags:

| Flag | Description |
|------|-------------|
| `--workflow-id`, `-w` | **(required)** Workflow ID |
| `--run-id`, `-r` | Run ID |
| `--follow`, `-f` | Follow progress in real time (not for JSON output) |
| `--reverse` | Fetch newest events first (cannot combine with `--follow`) |
| `--detailed` | Display events as detailed sections |
| `--output json` | JSON output (usable for SDK replay) |

Export history for replay:

```
temporal workflow show \
    --workflow-id YourWorkflowId \
    --output json
```

---

## 6. Stack trace

Get the current stack trace of a running Workflow's threads/routines:

```
temporal workflow stack \
    --workflow-id YourWorkflowId
```

This performs a `__stack_trace`-type Query on the Workflow Execution.

Flags:

| Flag | Description |
|------|-------------|
| `--workflow-id`, `-w` | **(required)** Workflow ID |
| `--run-id`, `-r` | Run ID |
| `--reject-condition` | Reject based on Workflow state. Values: `not_open`, `not_completed_cleanly` |

---

## 7. Task Queue poller status

`temporal task-queue describe` displays active Workers that have recently polled a Task Queue.

```
temporal task-queue describe \
    --task-queue YourTaskQueue
```

**Interpreting poller results:**

- The Temporal Server records each poll request time.
- A `LastAccessTime` over one minute may indicate the Worker is at capacity or has shut down.
- Workers are removed if 5 minutes have passed since the last poll request.

### Workflow vs. Activity pollers

Workflow and Activity polling use separate Task Queues. Specify the type to check Activity pollers:

```
temporal task-queue describe \
    --task-queue YourTaskQueue \
    --task-queue-type "activity"
```

The `--task-queue-type` flag accepts: `workflow`, `activity`, `nexus`. If not specified, all types are reported.

### Backlog statistics

The describe output includes the following statistics:

| Statistic | Description |
|-----------|-------------|
| `ApproximateBacklogCount` | Approximate tasks backlogged. May count expired tasks but eventually converges. |
| `ApproximateBacklogAge` | Approximate age of the oldest backlogged task (seconds), based on creation time. |
| `TasksAddRate` | Approximate tasks added per second, averaged over the last 30 seconds. Includes sync-matched tasks. |
| `TasksDispatchRate` | Approximate tasks dispatched per second, averaged over the last 30 seconds. Includes sync-matched tasks. |
| `BacklogIncreaseRate` | Approximate rate of backlog growth (positive) or shrinkage (negative), in tasks per second. Roughly `TasksAddRate - TasksDispatchRate`. |

> **Note:** `TasksAddRate` and `TasksDispatchRate` may differ from actual rates because eagerly dispatched or sticky tasks are not counted. The derived `BacklogIncreaseRate` is accurate for backlogs older than a few seconds.

To disable statistics and show only poller info, use `--disable-stats`.

### What to look for

- **No pollers**: No Workers are running (or recently running) for this Task Queue. Workflows on this queue will not make progress.
- **Stale `LastAccessTime`**: Workers may be overloaded or shutting down.
- **Growing `ApproximateBacklogCount` / positive `BacklogIncreaseRate`**: Workers cannot keep up with the incoming task rate. Scale up Workers or investigate slow activities.

---

## 8. Workflow tracing

Display progress of a Workflow Execution and its child workflows in real time:

```
temporal workflow trace \
    --workflow-id YourWorkflowId
```

Key flags:

| Flag | Description |
|------|-------------|
| `--workflow-id`, `-w` | **(required)** Workflow ID |
| `--depth` | Depth for child Workflow fetches. `-1` fetches all depths. |
| `--fold` | Fold away child Workflows with specified statuses. Values: `running`, `completed`, `failed`, `canceled`, `terminated`, `timedout`, `continueasnew`. |
| `--no-fold` | Disable folding; fetch and display all child Workflows within depth. |
| `--concurrency` | Number of Workflow Histories to fetch concurrently. |

---

## 9. Pagination and output control

### Limiting results

```
temporal workflow list \
    --query "ExecutionStatus = 'Running'" \
    --limit 50
```

### Page size

```
temporal workflow list \
    --query "ExecutionStatus = 'Running'" \
    --page-size 100
```

### JSON output

Use `--output json` or `--output jsonl` on any command for machine-readable output.

### Archived workflows

```
temporal workflow list --archived
```

This is an experimental feature.

---

## 10. Common health-check patterns

### Pattern: "Are any workflows stuck?"

```bash
# Count running workflows that started more than 1 hour ago
temporal workflow count \
    --query "ExecutionStatus = 'Running' AND StartTime < '2024-01-15T09:00:00Z'"

# If count > 0, list them
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND StartTime < '2024-01-15T09:00:00Z'" \
    --limit 20
```

### Pattern: "Are workers healthy?"

```bash
# Check pollers on the task queue
temporal task-queue describe \
    --task-queue my-task-queue

# Check activity pollers separately
temporal task-queue describe \
    --task-queue my-task-queue \
    --task-queue-type activity
```

Look for: active pollers present, `LastAccessTime` within the last minute, no growing backlog.

### Pattern: "What failed recently?"

```bash
temporal workflow list \
    --query "ExecutionStatus = 'Failed' AND CloseTime > '2024-01-15T00:00:00Z'"

temporal workflow count \
    --query "ExecutionStatus = 'Failed' AND CloseTime > '2024-01-15T00:00:00Z'"
```

To break failures down by Workflow Type, add a `WorkflowType` filter to the same query. Run a count per type across your known types:

```bash
temporal workflow count \
    --query "ExecutionStatus = 'Failed' AND WorkflowType = '<YourWorkflowType>'"
```

This identifies which Workflow Type is contributing the most failures rather than returning a flat list. `GROUP BY` in the Count API only supports grouping by `ExecutionStatus`, not by `WorkflowType` or other attributes — use per-type filtered counts instead.

### Pattern: "Workflows approaching history limits"

The server terminates a Workflow Execution when its Event History exceeds 51,200 events, contains more than 2,000 Updates, or more than 10,000 Signals. The `HistoryLength` Search Attribute surfaces the event count for running workflows.

```bash
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND HistoryLength > 40000"
```

Long-lived workflows that grow history without using Continue-As-New will eventually hit these limits. This is common in agent-loop or orchestrator patterns. Workflows returned by this query need either Continue-As-New or a redesign to bound history growth.

### Pattern: "Drill into a specific stuck workflow"

```bash
# 1. Describe it (status, pending activities, search attributes)
temporal workflow describe --workflow-id <id>

# 2. View its event history (newest first)
temporal workflow show --workflow-id <id> --reverse

# 3. Get its stack trace (running workflows only)
temporal workflow stack --workflow-id <id>
```

For diagnosing *why* a workflow is stuck, see `../triage/workflow-stuck.md`.

---

## Quick reference: List Filter examples from docs

The following examples are taken directly from the docs:

```sql
WorkflowType = "main.YourWorkflowDefinition" and ExecutionStatus != "Running" and (StartTime > "2021-06-07T16:46:34.236-08:00" or CloseTime > "2021-06-07T16:46:34-08:00")
```

```sql
WorkflowId = '<workflow-id>'
```

```sql
WorkflowId = '<workflow-id>' or WorkflowId = '<another-workflow-id>'
```

```sql
WorkflowId IN ('<workflow-id>', '<another-workflow-id>')
```

```sql
WorkflowId = '<workflow-id>' and ExecutionStatus = 'Running'
```

```sql
WorkflowId = '<workflow-id>' and StartTime > '2021-08-22T15:04:05+00:00'
```

```sql
ExecutionTime between '2021-08-22T15:04:05+00:00' and '2021-08-28T15:04:05+00:00'
```

```sql
WorkflowType STARTS_WITH '<workflow-type-prefix>'
```
