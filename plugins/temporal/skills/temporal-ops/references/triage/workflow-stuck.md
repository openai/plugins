# Workflow Stuck

A Workflow Execution exists, is reachable, reports an Open status, but is not making progress. This file scopes to what the server sees when that is true: the execution's own state as surfaced by `temporal workflow describe`, the append-only Event History as surfaced by `temporal workflow show`, and the pending-operation sub-structures (pending activities, pending child workflows, pending nexus operations, pending workflow task) that describe exposes.

Prerequisite: the client can reach the Temporal Service, authenticate, and issue data-plane RPCs. If `temporal workflow describe` itself fails, the problem is not in this file — rule out earlier layers via [connectivity.md](connectivity.md), [certificates.md](certificates.md), [authentication.md](authentication.md), and [rate-limits.md](rate-limits.md).

Out of scope here:
- Task Queue has no pollers / workers not polling → [worker-health.md](worker-health.md)
- Replaying recorded history diverges from the compiled Workflow (non-determinism) → [non-determinism.md](non-determinism.md)
- Replaying an Event History locally under a debugger → [replay.md](replay.md)
- gRPC `RESOURCE_EXHAUSTED` when the client call to describe/signal/query was itself rate-limited → [rate-limits.md](rate-limits.md)
- `context deadline exceeded` on the client side → [runtime-errors.md](runtime-errors.md)

## Table of Contents

- [What "stuck" means](#what-stuck-means)
- [Workflow Execution Status values](#workflow-execution-status-values)
- [The primary inspection command: `temporal workflow describe`](#the-primary-inspection-command-temporal-workflow-describe)
- [Inspecting the Event History: `temporal workflow show`](#inspecting-the-event-history-temporal-workflow-show)
- [Pending activities](#pending-activities)
- [Pending child workflows](#pending-child-workflows)
- [Pending signals, cancellations, and updates](#pending-signals-cancellations-and-updates)
- [Pending Nexus Operations](#pending-nexus-operations)
- [Pending Workflow Task and WorkflowTaskFailed loops](#pending-workflow-task-and-workflowtaskfailed-loops)
- [Timer-based waits](#timer-based-waits)
- [Pending-operation per-Workflow limits](#pending-operation-per-workflow-limits)
- [Recovery commands](#recovery-commands)
- [Quick routing](#quick-routing)

## What "stuck" means

"Stuck" is not a Temporal-defined state. It is a user observation that requires server evidence to classify. The three shapes of evidence that reliably separate "stuck" from "running as designed":

- **Event History has grown recently, but the last non-bookkeeping event is a scheduling event with no corresponding terminal event.** For example, `ActivityTaskScheduled` appears with no `ActivityTaskCompleted` / `ActivityTaskFailed` / `ActivityTaskTimedOut` appended for an interval longer than expected.
- **`temporal workflow describe` shows a pending activity, child workflow, nexus operation, or workflow task whose attempt count is climbing and whose last failure reason is reported.** Per the Activity Operations observability guide: "`temporal workflow describe` shows the current state of each pending Activity, including whether it's Paused, its current attempt count, and last failure."
- **Event History has not grown for longer than the longest timer or timeout currently outstanding.** A workflow can legitimately wait years on a Timer or indefinitely on a signal. Absence of progress is only evidence of stuck-ness when it exceeds the longest outstanding deadline the Workflow itself established.

All three rely on comparing the Workflow's own records (history + describe output) against expectations. Neither the SDK nor the server synthesises a single "Workflow is stuck" signal — the evidence lives in the fields below.

## Workflow Execution Status values

A Workflow Execution is either _Open_ or _Closed_. The full canonical set of statuses surfaced through the `ExecutionStatus` Search Attribute is: `Running, Completed, Failed, Canceled, Terminated, ContinuedAsNew, TimedOut`.

| Status | Open/Closed | Meaning | Source |
|---|---|---|---|
| `Running` | Open | "The only Open status for a Workflow Execution. When the Workflow Execution is Running, it is either actively progressing or is waiting on something." | |
| `Completed` | Closed | "The Workflow Execution has completed successfully." | |
| `Failed` | Closed | "The Workflow Execution returned an error and failed." | |
| `Canceled` | Closed | "The Workflow Execution successfully handled a cancellation request." | |
| `Terminated` | Closed | "The Workflow Execution was terminated." | |
| `ContinuedAsNew` | Closed | "The Workflow Execution Continued-As-New." | |
| `TimedOut` | Closed | "The Workflow Execution reached a timeout limit." | |

A "stuck" Workflow is almost always in `Running`. The phrase *"either actively progressing or waiting on something"* is the core ambiguity this file exists to resolve: `Running` alone cannot distinguish "working" from "wedged." The describe output and history are what distinguish them.

Transitions terminate the run:

- A Workflow Execution retry caused by its Retry Policy ends the failed run with `Failed` (status `Failed`, `retryState=IN_PROGRESS`, `newExecutionRunId` set) and spawns a new run.
- Continue-As-New closes the current run with `ContinuedAsNew` and starts a new run in the same Workflow Execution Chain.
- A Workflow Execution Timeout produces status `TimedOut`.
- The Event History reaching 51,200 events, 2,000 Updates, or 10,000 Signals terminates the Workflow Execution.

If the user reports a stuck workflow whose describe output shows a Closed status, they are not describing a stuck workflow — they are describing a completed or failed one, and the rest of this file does not apply.

## The primary inspection command: `temporal workflow describe`

`temporal workflow describe` is the one command that reports the server's current view of a single Workflow Execution's state. This file's diagnosis rests on the shape of its output.

```bash
temporal workflow describe \
    --workflow-id YourWorkflowId
```

 Flags:

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--run-id`, `-r` | No | Run ID. If omitted, the most recent run in the Workflow Execution Chain is described. |
| `--reset-points` | No | "Show auto-reset points only." |
| `--raw` | No | "Print properties without changing their format." |
| `--output`, `-o` | No (global) | Output format. Accepted values: `text, json, jsonl, none`. |

### Reading the output

The text example shown in the CLI docs for a minimal Running execution exposes these top-level fields: `executionConfig`, `workflowExecutionInfo` (containing `execution.workflowId`, `execution.runId`, `type.name`, `startTime`, `status`, `historyLength`, `executionTime`, `memo`, `autoResetPoints`, `stateTransitionCount`), and `pendingWorkflowTask` (containing `state`, `scheduledTime`, `originalScheduledTime`, `attempt`).

The Nexus-operations and pending-activities text examples in the encyclopedia show an alternative tabular shape under the same command — `Pending Activities: N`, `Pending Child Workflows: N`, `Pending Nexus Operations: N`, each followed by an indented block.

Which sections appear depends on the Workflow's current state: a Workflow with no pending operations simply won't show those sections.

### What to look at first

Per the intake shape above, the three checks that partition the problem:

1. **`workflowExecutionInfo.status`** — if it's anything other than `Running`, the workflow is Closed, not stuck. See [Workflow Execution Status values](#workflow-execution-status-values).
2. **Pending sections present** — are there `Pending Activities`, `Pending Child Workflows`, `Pending Nexus Operations`, or a `pendingWorkflowTask`? Each maps to a section below.
3. **`historyLength`** — stored in `workflowExecutionInfo.historyLength`. If it is climbing between successive describes but the pending sections don't resolve, events are being written but the Workflow is cycling. If it is flat with no pending operations, the Workflow is asleep on something with no visible pending work (typically a Timer — see [Timer-based waits](#timer-based-waits)).

## Inspecting the Event History: `temporal workflow show`

`temporal workflow show` returns the Event History, the append-only log of Events that drives replay.

```bash
temporal workflow show \
    --workflow-id YourWorkflowId \
    --output json
```

 Flags:

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--run-id`, `-r` | No | Run ID. |
| `--detailed` | No | "Display events as detailed sections instead of table. Does not apply to JSON output." |
| `--follow`, `-f` | No | "Follow the Workflow Execution progress in real time. Does not apply to JSON output." |
| `--output json` | No (global) | Emits the JSON shape an SDK would replay. |

Event types are enumerated in the [Events reference](https://docs.temporal.io/references/events); the canonical list is the `EventType` proto enum. A Command issued by the Workflow code produces a corresponding Event on the server — the Command/Event mapping is documented in the [Commands reference](https://docs.temporal.io/references/commands).

### Finding the last meaningful event

Within each Workflow Task execution, the server records `WorkflowTaskScheduled`, `WorkflowTaskStarted`, and `WorkflowTaskCompleted` bookkeeping around the state changes the Workflow code produced. When diagnosing stuck-ness, the event type that exposes *why* the workflow is waiting is the last non-bookkeeping event — the scheduling event (e.g., `ActivityTaskScheduled`, `StartChildWorkflowExecutionInitiated`, `TimerStarted`, `NexusOperationScheduled`) with no matching terminal event yet.

Asymmetric recording: per the event encyclopedia, "While the Activity is running and retrying, `ActivityTaskScheduled` is the only Activity-related Event in History: `ActivityTaskStarted` is written along with a terminal Event like `ActivityTaskCompleted` or `ActivityTaskFailed`." So a long gap between `ActivityTaskScheduled` and its terminal event does *not* imply the Activity is unpicked — it may be running and retrying. Use `temporal workflow describe`'s Pending Activities section to see retry state, not the Event History alone.

## Pending activities

A Pending Activity is an Activity whose `ActivityTaskScheduled` event has been appended but whose terminal event has not. The retry state of the in-flight Activity Execution (attempt count, last failure, paused status) is only visible via `temporal workflow describe`; it is not re-written to Event History on each retry.

### Fields surfaced by describe for a pending activity

Docs state that describe surfaces "the current state of each pending Activity, including whether it's Paused, its current attempt count, and last failure." A Pending Activity block's exact text-output field names are not enumerated in a single docs location in this repo's snapshot. Treat the fields below as conceptual checkpoints for the diagnosis, and read the live describe output for exact field names.

Things to check on a pending activity:

- **Attempt count.** If retries are climbing and the Activity has a Retry Policy with a finite `Maximum Attempts`, the Activity will eventually be recorded as `ActivityTaskFailed` and the Workflow will proceed (or fail) accordingly.  If Maximum Attempts is unlimited and each attempt is failing for the same reason, the Workflow will loop indefinitely on this Activity.
- **Last failure.** The `last_failure` field of `ActivityTaskStarted` carries "Details from the most recent failure Event. Only assigned values if the Task has previously failed and been retried." The describe output exposes the equivalent information for pending activities.
- **Scheduled vs. Started.** If the Activity has never been picked up (only `ActivityTaskScheduled` in the history, no retry attempts in the pending block), the problem is almost certainly worker-side — no Worker is polling the Task Queue the Activity was scheduled on, or pollers exist but none match the Build ID routing the Workflow expects. Route to [worker-health.md](worker-health.md).
- **Timeouts on the scheduling attributes.** The `activityTaskScheduledEventAttributes` record includes `schedule_to_close_timeout`, `schedule_to_start_timeout`, `start_to_close_timeout`, and `heartbeat_timeout`. A long-running Activity without heartbeats and a missing `start_to_close_timeout` or `heartbeat_timeout` can block indefinitely: "The Temporal Server doesn't detect failures when a Worker loses communication with the Server or crashes. Therefore, the Temporal Server relies on the Start-To-Close Timeout to force Activity retries."
- **Paused state.** If the Activity was explicitly paused via `temporal activity pause`, retries are server-side suspended. Unpause via `temporal activity unpause`.

### Heartbeating

For long-running activities, heartbeating is the only mechanism by which the server detects a dead worker. A missed heartbeat within the `heartbeat_timeout` results in `ActivityTaskTimedOut` and a retry. Activities without heartbeating cannot be killed server-side mid-execution; they run until `start_to_close_timeout` (or forever, if neither start-to-close nor schedule-to-close is set).

## Pending child workflows

A Pending Child is one whose `StartChildWorkflowExecutionInitiated` or `ChildWorkflowExecutionStarted` event has been appended but whose terminal event (`ChildWorkflowExecutionCompleted`, `ChildWorkflowExecutionFailed`, `ChildWorkflowExecutionCanceled`, `ChildWorkflowExecutionTimedOut`, `ChildWorkflowExecutionTerminated`) has not.

Things to check:

- **Extract the child's Workflow ID and Run ID from the parent's describe output**, then recurse into describe on the child. The parent is only stuck in the sense that the child is — the root cause lives in the child's describe / history.
- **The child may be in a different Namespace.** Child Workflows can cross Namespaces; if the parent's describe shows a child that doesn't appear in the current Namespace's `temporal workflow list`, re-run describe with the correct `--namespace`.
- **Parent Close Policy.** When a parent closes, Temporal "propagates Cancellation Requests or Terminations to Child Workflow Executions depending on the Child's Parent Close Policy." A child that is stuck because its parent was terminated but used the `Abandon` close policy is a different shape — the child is independently running.

## Pending signals, cancellations, and updates

A Workflow's handling of Signals and Updates is Workflow-code-directed — the SDK's `await` / `workflow.wait_condition` APIs block the workflow until the condition becomes true. "Pending Signals" (server-side) are distinct from "Signals the Workflow is waiting for" (SDK / code-side):

- **`SignalExternalWorkflowExecutionInitiated`** is an Event type recorded when *this* Workflow signals *another*. The terminal events are `ExternalWorkflowExecutionSignaled` (success) and `SignalExternalWorkflowExecutionFailed`. A stalled outgoing signal is a pending operation from the caller's perspective.
- **`WorkflowExecutionSignaled`** is the Event type recorded when an external party (client, another Workflow, `temporal workflow signal`) sends a signal *to* this Workflow. If a Workflow is blocked waiting on a signal that has never been sent, no `WorkflowExecutionSignaled` event will appear — *absence* of the event is the symptom.
- **`WorkflowExecutionUpdateAcceptedEvent`** / **`WorkflowExecutionUpdateCompletedEvent`** record Update lifecycle. A pending Update (accepted but not completed) keeps the Workflow responsible for resolving it.

Things to check for "waiting on a signal" stuck-ness:

- **Inspect the call stack.** `temporal workflow stack` runs the `__stack_trace` Query and returns "a stack trace of the threads and routines currently in use by the Workflow for troubleshooting." This works only when a Worker is running and available to respond to queries. The stack trace will show which `await` or `wait_condition` the Workflow is blocked on, which identifies the signal/update name.
- **Send a test signal** to confirm the handler is wired correctly: `temporal workflow signal --workflow-id YourWorkflowId --name YourSignal --input '{"key": "value"}'`.
- **Check the sender side.** If the signal is being sent but not received, three app-code patterns account for most cases. All three are diagnosable from describe/show output:

  1. **Stale Run ID after Continue-As-New.** The sender targets a specific Run ID that belongs to a now-closed run (status `ContinuedAsNew`). The server accepts the signal — it is valid for the closed run — but the new run never sees it because it has a different Run ID. Symptom: `WorkflowExecutionSignaled` appears in the *old* run's history but not the current run's. Fix: the sender should omit the Run ID (letting the server route to the latest run in the chain) or re-resolve the Workflow ID to the current Run ID before signaling.
  2. **Continue-As-New fires before in-flight handlers finish.** The Workflow calls Continue-As-New without waiting for `all_handlers_finished` (Python) / the SDK-equivalent guard. In-flight signal and update handlers on the closing run are silently dropped — they never run to completion, and the new run has no record of them. Symptom: the sender sees success (the signal was delivered), but the Workflow behaves as if the signal never arrived. The old run's history shows `WorkflowExecutionSignaled` followed by `WorkflowExecutionContinuedAsNew` with no evidence the handler acted. Fix: the Workflow must await the all-handlers-finished condition before issuing Continue-As-New.
  3. **Handler name mismatch.** The sender uses a signal name that doesn't match any registered handler (e.g., `order_shipped` vs. `orderShipped`). The server accepts the signal — it does not validate handler names — so `WorkflowExecutionSignaled` appears in history, but no handler runs. The Workflow blocks forever on a condition that will never be satisfied. Symptom: history contains the `WorkflowExecutionSignaled` event with the signal name, but `temporal workflow stack` shows the Workflow still blocked on the same `wait_condition`. Fix: align the signal name in the sender with the name registered in the Workflow Definition.

The workflow has per-Workflow-Execution pending-signal limits documented in [Pending-operation per-Workflow limits](#pending-operation-per-workflow-limits).

## Pending Nexus Operations

A pending Nexus Operation is a Nexus call issued from this Workflow that has been scheduled (`NexusOperationScheduled`) and may have been started (`NexusOperationStarted`) but has not reached a terminal event (`NexusOperationCompleted`, `NexusOperationFailed`, `NexusOperationTimedOut`, `NexusOperationCanceled`).

`temporal workflow describe` surfaces pending Nexus Operations with these fields (from the docs' own example): `Endpoint`, `Service`, `Operation`, `OperationToken`, `State`, `Attempt`, `ScheduleToCloseTimeout`, `NextAttemptScheduleTime`, `LastAttemptCompleteTime`, `LastAttemptFailure`, and — when the per-destination circuit breaker is open — `BlockedReason`.

Things to check:

- **`State`.** The docs' two text examples show `BackingOff` (retrying after a retryable error) and `Blocked` (circuit breaker open for the destination pair). `Blocked` with a `BlockedReason` of "The circuit breaker is open" means the handler side (or the network path to it) has produced enough consecutive timeouts / retryable errors to trip the breaker; handler Workers must recover before pending Operations resume.
- **`LastAttemptFailure`.** Non-retryable errors resolve the Operation with a `NexusOperationFailed` / `NexusOperationTimedOut` / `NexusOperationCanceled` event. Retryable errors surface in the pending Operation with `LastAttemptFailure` filled in.
- **Pending Callbacks.** Separate from Pending Operations, Nexus completion callbacks have their own pending view, surfaced as `Callbacks: N` with `URL`, `Trigger`, `State`, `Attempt`, `RegistrationTime`.

## Pending Workflow Task and WorkflowTaskFailed loops

A Pending Workflow Task is a Workflow Task scheduled for this Workflow but not yet completed by a Worker. The JSON describe example shows the shape: `pendingWorkflowTask.state`, `pendingWorkflowTask.scheduledTime`, `pendingWorkflowTask.originalScheduledTime`, `pendingWorkflowTask.attempt`.

### Distinguishing pending Workflow Task shapes

- **`pendingWorkflowTask.attempt` = 1, recently scheduled, no `WorkflowTaskFailed` in history.** A Worker has not yet picked up the task. If this persists, route to [worker-health.md](worker-health.md): confirm pollers on the Workflow Task Queue.
- **`pendingWorkflowTask.attempt` > 1 and the Event History contains repeating `WorkflowTaskFailed` events.** The task is being retried server-side after worker-reported failures.
- **`pendingWorkflowTask` absent while history has a recent `WorkflowTaskCompleted`.** The last Workflow Task completed cleanly — the Workflow is not blocked on running Workflow code, it is blocked on an awaitable from that completed task (Activity, Child, Signal, Update, Timer, Nexus).

### The WorkflowTaskFailed retry loop

`WorkflowTaskFailed` "indicates that the Workflow Task encountered a failure." The event's `workflow_task_failed_event_attributes` include `scheduled_event_id`, `started_event_id`, `failure`, `identity`, and (for Reset-initiated failures) `base_run_id`, `new_run_id`, `fork_event_version`, and `binary_checksum`. The `failure` field carries the detail of the failure.

Each `WorkflowTaskFailed` corresponds to a value of the `WorkflowTaskFailedCause` enum (referenced in Event attributes as `cause`). The error reference enumerates the causes; these are the ones relevant to stuck-ness:

| Cause (in the `errors.mdx` reference) | Interpretation | Route |
|---|---|---|
| Nondeterminism Error | Replay diverged from recorded history | [non-determinism.md](non-determinism.md) |
| Workflow Worker Unhandled Failure | An unhandled failure (panic, exception) from the Workflow Definition | Worker logs for stack trace; fix and redeploy |
| Unhandled Command | The Workflow attempted to close without handling new Events; can occur under Signal load | Drain signal channel; inspect Worker logs |
| Pending Activities Limit Exceeded | Workflow reached the per-Workflow pending-Activity cap | [Pending-operation per-Workflow limits](#pending-operation-per-workflow-limits) |
| Pending Child Workflows Limit Exceeded | Reached pending-Child cap | Same as above |
| Pending Signals Limit Exceeded | Reached pending external-Signal cap | Same as above |
| Pending Nexus Operations Limit Exceeded | Reached pending Nexus Operation cap | Same as above |
| Bad Search Attributes | Invalid Search Attributes cause Workflow Tasks "to continue to retry without success." | Fix Workflow code or attribute definitions |

### Detecting WFT-failure loops at scale with Task Issue detection

Rather than inspecting individual Workflows, use the `TemporalReportedIssue` search attribute to find all Workflows currently experiencing Workflow Task failures:

```bash
temporal workflow list \
    --query "TemporalReportedIssue IS NOT NULL" \
    --namespace <ns>
```

The `TemporalReportedIssue` search attribute is automatically set by the server when it detects a Workflow Task issue (e.g., repeated `WorkflowTaskFailed` events). This surfaces problems proactively without needing to inspect each Workflow individually.

### Why a Workflow stays Running through WFT-failure loops

Workflow Tasks do not fail the Workflow Execution. The server retries failed Workflow Tasks so that once the Worker code is fixed and redeployed, the Workflow resumes. This is by design: the Event History is durable, and a bad deploy that causes a WFT to fail can be rolled back or patched without losing the Workflow's progress. The visible effect is that the Workflow stays `Running`, the Event History grows a tail of `WorkflowTaskFailed` events, and the attempt count climbs.

## Timer-based waits

Timers are persisted server-side: "even if your Worker or Temporal Service is down when the time period completes, as soon as your Worker and Temporal Service become available, the call that is awaiting the Timer in your Workflow code will resolve." A Workflow that is waiting on a timer is not stuck; it is asleep. Fire time is deterministic from history.

The `TimerStarted` event carries `timer_id`, `start_to_fire_timeout`, and `workflow_task_completed_event_id`. The fire time is the `eventTime` of the `TimerStarted` event plus `start_to_fire_timeout`. If that fire time is in the future, the Workflow is working as designed; report the resume time rather than treating the Workflow as stuck.

"The duration of a Timer is fixed, and your Workflow might specify a value as short as one second or as long as several years." Multi-year timer waits are legitimate.

The terminal events are `TimerFired` (with `timer_id` and `started_event_id`) and `TimerCanceled`.

## Pending-operation per-Workflow limits

The server enforces per-Workflow caps on the number of incomplete operations of each kind. Exceeding a cap fails the Workflow Task that attempted to add another operation of that kind — the Workflow Execution does not close, but the WFT will fail and retry until the pending count drains.

| Operation | Default limit | Source |
|---|---|---|
| Pending Activities | 2,000 |  |
| Pending Child Workflow Executions | 2,000 |  |
| Pending Signals (external) | 2,000 | |
| Pending Cancel Requests | 2,000 | |
| Pending Nexus Operations | 30 | |

The Event-History caps are a separate ceiling that terminates the Workflow when crossed: "The Workflow Execution is terminated when the Event History exceeds 51,200 Events, contains more than 2000 Updates, or contains more than 10000 Signals." A stuck-looking Workflow approaching these limits will not stay Running — it will close with `Terminated` when it crosses them.

## Recovery commands

These commands alter the Workflow's state or flow. Use them once the diagnosis identifies the shape of the stuck-ness.

### `temporal workflow signal`

Send a Signal to unblock a Workflow that is waiting on one.

```bash
temporal workflow signal \
    --workflow-id YourWorkflowId \
    --name YourSignal \
    --input '{"key": "value"}'
```

### `temporal workflow terminate`

Terminate a Workflow that cannot be recovered. Terminal events become the closing event of the Execution History. "Workflow code cannot see or respond to terminations. To perform clean-up work in your Workflow code, use `temporal workflow cancel` instead."

```bash
temporal workflow terminate \
    --workflow-id YourWorkflowId \
    --reason YourReason
```

### `temporal workflow cancel`

Request cancellation. A `WorkflowExecutionCancelRequested` event is appended, and the Workflow runs any cleanup paths its code supports.

```bash
temporal workflow cancel \
    --workflow-id YourWorkflowId
```

### `temporal workflow reset`

Reset the Workflow to a point in its Event History so it can resume from there without losing progress up to that point. Valid reset points per the Event encyclopedia are "`WorkflowTaskStarted`, `WorkflowTaskCompleted`, `WorkflowTaskTimedOut`, and `WorkflowTaskFailed`." A Reset terminates the current Run and creates a new Run with history copied up to the reset point.

```bash
temporal workflow reset \
    --workflow-id YourWorkflowId \
    --event-id YourLastEvent
```

 To reset to where the current Run continued-as-new:

```bash
temporal workflow reset \
    --workflow-id YourWorkflowId \
    --type LastContinuedAsNew
```

 The `--type` flag's `LastContinuedAsNew` value appears in the reset example. The batch-reset guidance in the same section mentions `FirstWorkflowTask`, `LastWorkflowTask`, and `BuildId` as the only `--type` values permitted for batch resets. A companion flag `--reapply-type` controls which Events are reapplied after the reset point; accepted values are `Signal, None`.

Because the new Run replays history only up to the reset point, everything after it
*happens again* —
Activities with external side effects re-execute, so a reset past a payment, an
email, a provisioning call, or a non-idempotent write performs it a second time.
`--reapply-type None` suppresses Signal reapplication; it does not prevent Activity
re-execution. Establish where the side effects are relative to the candidate reset
point, say so in the proposal, and prefer the latest reset point that still clears
the problem.

### `temporal workflow pause` / `unpause`

Experimental.

```bash
temporal workflow pause --workflow-id YourWorkflowId --reason YourReason
temporal workflow unpause --workflow-id YourWorkflowId --reason YourReason
```

### `temporal activity pause` / `unpause` / `reset`

For stuck pending *activities*, Activity Operations are the surgical tool: pause to stop retries, unpause to resume, reset to clear attempt state. These operations are in Public Preview (Server v1.28.0+). Activity Operations don't produce Event History events — they leave no audit trail beyond the current describe output.

## Quick routing

| Evidence | Go to |
|---|---|
| `workflowExecutionInfo.status` is not `Running` | [Workflow Execution Status values](#workflow-execution-status-values) — the workflow is Closed, not stuck |
| Pending activity present, no attempts yet, Event History shows `ActivityTaskScheduled` only | [worker-health.md](worker-health.md) — check pollers on the Activity's Task Queue |
| Pending activity present, attempts climbing, `LastAttemptFailure` reported | [Pending activities](#pending-activities) |
| Pending child workflow present | [Pending child workflows](#pending-child-workflows) — recurse into the child |
| Waiting on a signal that never arrives | [Pending signals, cancellations, and updates](#pending-signals-cancellations-and-updates); use `temporal workflow stack` |
| Pending Nexus Operation with `State: Blocked` or `BackingOff` | [Pending Nexus Operations](#pending-nexus-operations) |
| `pendingWorkflowTask.attempt` > 1, `WorkflowTaskFailed` events accumulating | [Pending Workflow Task and WorkflowTaskFailed loops](#pending-workflow-task-and-workflowtaskfailed-loops) |
| `TemporalReportedIssue` search attribute set on Workflow(s) | [Detecting WFT-failure loops at scale](#detecting-wft-failure-loops-at-scale-with-task-issue-detection) |
| WFT failure cause is `NonDeterministicError` | [non-determinism.md](non-determinism.md) |
| Last non-bookkeeping event is `TimerStarted`, fire time is in the future | [Timer-based waits](#timer-based-waits) — not stuck |
| WFT fails with `Pending Activities Limit Exceeded` / `Pending Child Workflows Limit Exceeded` / `Pending Signals Limit Exceeded` / `Pending Nexus Operations Limit Exceeded` | [Pending-operation per-Workflow limits](#pending-operation-per-workflow-limits) |
| Need to reproduce the failure locally under a debugger | [replay.md](replay.md) |
| `temporal workflow describe` itself fails (cannot reach / authenticate / authorize) | [connectivity.md](connectivity.md), [certificates.md](certificates.md), [authentication.md](authentication.md), [rate-limits.md](rate-limits.md) |

See the whole-stack picture in [diagnostic-ladder.md](diagnostic-ladder.md).
