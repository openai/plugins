# Non-Determinism

This file scopes to one specific Workflow Task failure subtype: the one whose `WorkflowTaskFailedCause` is the Nondeterminism cause — i.e. the Workflow Task failed because replaying the recorded Event History against the currently-loaded Workflow code produced a Command that did not match the next Event.

Non-determinism is a subtype of the WFT-failure loop documented in [workflow-stuck.md](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops). For the taxonomy of *other* WFT-failure causes (Unhandled Command, Pending Activities Limit Exceeded, Bad Search Attributes, Workflow Worker Unhandled Failure), start there.

Out of scope here:
- Workflow stuck in general, including other WFT-failure causes → [workflow-stuck.md](workflow-stuck.md)
- Replaying an Event History locally under a debugger → [replay.md](replay.md)
- Worker not polling the Workflow Task Queue at all → [worker-health.md](worker-health.md)
- gRPC `RESOURCE_EXHAUSTED` on the client that tries to describe or reset → [rate-limits.md](rate-limits.md)
- The bottom-up layer model for routing between files → [diagnostic-ladder.md](diagnostic-ladder.md)

## Table of Contents

- [What determinism means in Temporal](#what-determinism-means-in-temporal)
- [How replay detection works](#how-replay-detection-works)
- [The WFT-failure signature of non-determinism](#the-wft-failure-signature-of-non-determinism)
- [Why ND does not fail the Workflow](#why-nd-does-not-fail-the-workflow)
- [What the docs call out as ND-inducing patterns](#what-the-docs-call-out-as-nd-inducing-patterns)
- [Per-SDK error shape](#per-sdk-error-shape)
- [Identifying ND from the Event History](#identifying-nd-from-the-event-history)
- [Reproducing ND locally via replay](#reproducing-nd-locally-via-replay)
- [Remediation: Worker Versioning (preferred)](#remediation-worker-versioning-preferred)
- [Remediation: per-SDK patching](#remediation-per-sdk-patching)
- [Remediation: fix and redeploy, or reset past the divergence](#remediation-fix-and-redeploy-or-reset-past-the-divergence)
- [Quick routing](#quick-routing)

## What determinism means in Temporal

The Temporal Platform requires that Workflow code is deterministic. A Replay "recreates the exact state of a Workflow Execution" by running the Workflow code against the recorded Event History, and "Replay succeeds only if the Workflow Definition is compatible with the provided history from a deterministic point of view."

Per the encyclopedia's formal definition: "The use of certain Workflow APIs in the function is what generates Commands. Commands tell the Temporal Service which Events to create and add to the Workflow Execution's Event History. When the Workflow's code replays, the Commands that are emitted are compared with the existing Event History. If a corresponding Event already exists within the Event History that matches that command, then the Execution progresses."

"If a generated Command doesn't match what it needs to in the existing Event History, then the Workflow Execution returns a non-deterministic error."

Two reasons a Command may not match: (1) code changes to a Workflow Definition that is in use by a running Workflow Execution, or (2) intrinsic non-deterministic logic such as inline random branching.

## How replay detection works

Replay is "the method by which a Workflow Execution resumes making progress. During a Replay the Commands that are generated are checked against an existing Event History." Replay happens whenever a Worker picks up a Workflow Task for a Workflow Execution whose in-memory state is not already present on that Worker — i.e. after a Worker restart, after a sticky-cache eviction, or when a different Worker picks up the next Workflow Task.

At Command-emission time, the Worker compares the Command it is about to emit against the next non-bookkeeping Event in the recorded history. A mismatch at any point (wrong Command type, wrong attributes like Activity name, or a Command appearing where none was recorded) surfaces as a non-determinism error inside the Worker. The Worker reports the Workflow Task as failed; the server appends a `WorkflowTaskFailed` Event with `cause` set to the Nondeterminism value of the `WorkflowTaskFailedCause` enum.

## The WFT-failure signature of non-determinism

Each `WorkflowTaskFailed` Event corresponds to a value of the `WorkflowTaskFailedCause` enum, exposed in the Event's `workflow_task_failed_event_attributes` as `cause`. The Nondeterminism cause is documented in `errors.mdx` as:

> The Workflow Task failed due to a nondeterminism error.

The event attributes schema — `scheduled_event_id`, `started_event_id`, `failure`, `identity`, `base_run_id`, `new_run_id`, `fork_event_version`, `binary_checksum` — is shared with every other `WorkflowTaskFailed` cause. The Nondeterminism-specific detail (which Command diverged from which Event) is carried inside the `failure` field, produced by the SDK.

## Why ND does not fail the Workflow

Workflow Task failures do not fail the Workflow Execution. The server retries failed Workflow Tasks so that, once the Worker code is fixed and redeployed, the Workflow resumes. The observable effect of a Nondeterminism WFT failure is:

- The Workflow Execution stays in the `Running` status.
- `pendingWorkflowTask.attempt` (shown by `temporal workflow describe`) climbs.
- The Event History accumulates repeating `WorkflowTaskFailed` Events with `cause` = Nondeterminism.
- Worker logs repeat an SDK-specific non-determinism exception (see [Per-SDK error shape](#per-sdk-error-shape)).

This "the Workflow is durable, the bad deploy is not" behavior is intentional: fixing the Worker code and redeploying, or resetting the Workflow past the divergence point, resumes the execution without losing its progress to that point.

Contrast with ordinary Workflow failures. An unhandled exception inside an Activity produces `ActivityTaskFailed` and, depending on the Activity's Retry Policy, either retries or propagates to the Workflow. An unhandled exception inside the Workflow function itself produces the distinct `Workflow Worker Unhandled Failure` WFT cause, which is routed out of this file (worker logs for stack trace, fix and redeploy; see [workflow-stuck.md](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops)). Neither of those is a Nondeterminism error — the classification lives in the `cause` field.

## What the docs call out as ND-inducing patterns

Two categories, per the encyclopedia:

### Code changes to a Workflow Definition in use

"The Workflow Definition can change in very limited ways once there is a Workflow Execution depending on it." The canonical example in the docs: a Workflow that was started under a definition of *Timer then Activity* cannot be migrated to a definition of *Activity then Timer* without versioning; on the next Workflow Task, "the first Command the Worker sees would be ScheduleActivityTask Command, which wouldn't match up to the expected TimerStarted Event. The Workflow Execution would fail and return a nondeterminism error."

Minor changes that do *not* cause ND on replay of histories that already contain the corresponding Events:

- Changing the duration of a Timer, with language-specific exceptions: "In Java, Python, and Go, changing a Timer's duration from or to 0 is a non-deterministic behavior. In .NET, changing a Timer's duration from or to -1 (which means 'infinite') is a non-deterministic behavior."
- Changing arguments to Activity Options, Child Workflow Options, or the Signal External Workflow Execution call.
- Adding a Signal Handler for a Signal Type that has not been sent to this Workflow Execution.

### Intrinsic non-determinism in the Workflow function

"Intrinsic non-determinism is when a Workflow Function Execution might emit a different sequence of Commands on re-execution, regardless of whether all the input parameters are the same." "A Workflow Definition can not have inline logic that branches (emits a different Command sequence) based off a local time setting or a random number."

Each SDK exposes replay-safe alternatives. The per-SDK constraint lists documented in `develop/<sdk>/workflows/basics.mdx`:

- **Go.** "Iterate over maps using `range`, because with `range` the order of the map's iteration is randomized." Use sorted keys, a Side Effect, or an Activity instead. Direct calls to external APIs, file I/O, or other services must be wrapped in Activities. Replay-safe substitutes include `workflow.Now()` (for `time.Now()`), `workflow.Sleep()`, `workflow.GetLogger()`, `workflow.Go()` (for the `go` statement), `workflow.Channel` (for native `chan`), `workflow.Selector` (for `select`), and `workflow.Context`. Go's map iteration order is not specified by the language spec.
- **Python.** "Workflow code must be deterministic because the Temporal Server may replay your Workflow to reconstruct its state. This means: no threading, no randomness, no external calls to processes, no network I/O, no global state mutation, no system date or time." Replay-safe substitutes: `workflow.random()` (for `random.random()`), `workflow.uuid4()` (for `uuid.uuid4()`), `workflow.now()` (for `datetime.now()` / `time.time()`), `workflow.logger` (for `print()` / `logging`).
- **TypeScript, Java, .NET, Ruby, PHP.** Per-SDK constraint lists and replay-safe APIs are linked from the encyclopedia.

Also documented: changes to "Patched or GetVersion calls for Versioning (although they may be added or removed according to the patching rules)" are among the minor allowed changes. In other words, patching and removing patches have documented rules; ad-hoc additions of non-patched activity calls in the middle of a Workflow do not.

What the docs do *not* prescribe here: a ranked list of "most common causes." Treat the two categories above as exhaustive framings. Any diagnosis that does not map to one of them should be escalated to a VERIFY.

## Per-SDK error shape

The error class or message that the Worker emits when replay diverges differs per SDK. Only the names actually verified in the docs are listed:

- **TypeScript.** "When an Event History is replayed and non-determinism is detected (that is, the Workflow code is incompatible with the History), `DeterminismViolationError` is thrown. If replay fails for any other reason, `ReplayError` is thrown."
- **Go.** The Go SDK emits a non-determinism error through the Workflow Task failure path; the docs for versioning describe the condition as "cause the Workflow to fail with a nondeterminism error" without pinning a public class name.
- **Java.** The Java versioning doc describes the condition as "This would cause the Workflow to fail with a nondeterminism error" without pinning a public exception class.
- **Python.** The Python versioning doc describes the condition as "cause a nondeterminism error" without pinning a public exception class.
- **.NET, Ruby, PHP.** Per-SDK class names are not documented in the files consulted.

Server-side, regardless of SDK, the cause surfaces as the Nondeterminism `WorkflowTaskFailedCause` in the Event History. Rely on that server-side cause for cross-SDK classification; rely on the per-SDK error class only when debugging from worker logs.

## Identifying ND from the Event History

The server-side signal that unambiguously marks ND is a `WorkflowTaskFailed` Event whose attributes carry the Nondeterminism `cause`. Extract via:

```bash
temporal workflow show \
    --workflow-id YourWorkflowId \
    --output json > history.json
```

 Then filter the JSON for `WorkflowTaskFailed` events and inspect each one's `workflowTaskFailedEventAttributes.cause` and `workflowTaskFailedEventAttributes.failure` fields. The exact JSON field names come from the server proto; the encyclopedia identifies them as `workflow_task_failed_event_attributes`.

`temporal workflow describe` also surfaces a `pendingWorkflowTask` with a rising `attempt` when WFT failures are looping. A rising attempt count plus `WorkflowTaskFailed` Events with Nondeterminism cause is the confirming two-signal match.

If `describe` shows WFT failures but the history JSON does not report Nondeterminism as the cause, the WFT is failing for a different reason — return to [workflow-stuck.md §Pending Workflow Task and WorkflowTaskFailed loops](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops) and match the actual cause.

## Reproducing ND locally via replay

Running the recorded history through a local replayer against a Worker source tree is the canonical reproducer. "Replay recreates the exact state of a Workflow Execution. You can replay a Workflow from the beginning of its Event History. Replay succeeds only if the Workflow Definition is compatible with the provided history from a deterministic point of view."

Per-SDK replay APIs (names transcribed from the testing-suite pages; cross-check against the SDK version in use):

- **Go.** `worker.NewWorkflowReplayer()` + `replayer.ReplayWorkflowHistory(logger, history)`.
- **Python.** `Replayer(workflows=[YourWorkflow])` + `replayer.replay_workflow(WorkflowHistory.from_json(history_json_str))`, or `replayer.replay_workflows(histories)` for bulk.
- **TypeScript.** `Worker.runReplayHistory(options, history)` for single histories, `Worker.runReplayHistories(...)` for bulk.
- **Java.** `WorkflowReplayer.replayWorkflowExecution(file, MyWorkflow.class)` for single histories, `WorkflowReplayer.replayWorkflowExecutions(...)` for bulk.

For an interactive reproducer with breakpoints over the same replayer APIs, see [replay.md](replay.md).

Fetch the history with the SDK client in the same test that replays it — per-SDK calls in [replay.md → Step 1](replay.md#step-1--get-the-event-history). Where a file is needed instead:

```bash
temporal workflow show \
    --workflow-id YourWorkflowId \
    --run-id YourRunId \
    --output json > history.json
```

If local replay *succeeds* against the checked-out source but production Workers keep failing, the deployed Worker code is different from the local checkout. Find the deployed build and either roll it back or patch it forward.

If local replay *fails* with the same error, iterate on the Workflow source until replay succeeds.

## Remediation: Worker Versioning (preferred)

"For most teams, Worker Versioning should be the default recommendation for deploying Workflow code changes in production. If you can run versioned worker deployments, prefer Worker Versioning over patching."

The mechanism: "Worker Versioning introduces Workflow Pinning. For pinned Workflow Types, each execution runs entirely on the Worker Deployment Version where it started. You need not worry about making breaking code changes to running, pinned Workflows." "Pinned Workflows don't need to be patched, as they run on the same worker and build until they complete."

Minimum versions for Worker Versioning (Public Preview as of the docs snapshot): Go v1.35.0, Python v1.11, Java v1.29, TypeScript v1.12, .NET v1.7.0, Ruby v0.5.0; Temporal CLI v1.4.1, Server v1.29.1, UI v2.38.0.

Adoption in the middle of triaging an ND incident is not a remediation — it is a prevention for future changes. For Workflows that are *already* in the ND loop and were started before Worker Versioning was enabled for their Workflow Type, use patching or reset.

## Remediation: per-SDK patching

Patching lets Workflow code branch on whether it is replaying history recorded before or after a specific change. Patching APIs per SDK (each citation links to the canonical docs page; only names present in those pages are listed):

- **Go.** `workflow.GetVersion(ctx, "change-id", workflow.DefaultVersion, 1)`. "When `workflow.GetVersion()` is run for the new Workflow Execution, it records a marker in the Event History so that all future calls to `GetVersion` for this change Id ... will always return the given version number." A Workflow that has already passed this `GetVersion()` call before it was introduced returns `DefaultVersion`.
- **TypeScript.** `patched('change-id')` to branch, `deprecatePatch('change-id')` to mark a patch as deprecated. "Using `patched` inserts a marker into the Workflow History. During Replay, if a Worker encounters a history with that marker, it will fail the Workflow task when the Workflow code doesn't produce the same patch marker."
- **Java.** `Workflow.getVersion("change-id", Workflow.DEFAULT_VERSION, 1)`. "Each call to `Workflow.getVersion` automatically upserts the `TemporalChangeVersion` Search Attribute with a keyword list of `"<Change ID>-<Version>"` entries."
- **Python.** `workflow.patched('change-id')` to branch, `workflow.deprecate_patch('change-id')` to mark deprecated.
- **.NET.** `Workflow.Patched("change-id")`, `Workflow.DeprecatePatch("change-id")`.

The three-phase lifecycle, per each SDK's versioning page:

1. Patch in new code using the branching API alongside the old code.
2. Once no open Workflow Executions are on the old code, switch to the deprecate-patch API.
3. Once all patched Workflows have left retention, remove the patch call entirely.

The patching behavior at replay time is documented in detail in `docs/encyclopedia/workflow/patching.mdx`. Key consequence: if the execution hits a `patched()` call during replay but the marker is *after* the current execution point in history, "it will throw a non-deterministic exception because the replay and original event histories don't match." Put the newest code at the top of patch blocks: "when patching in new code, always put the newest code at the top of an if-patched-block."

## Remediation: fix and redeploy, or reset past the divergence

Because ND WFT failures retry server-side, there are two live-incident paths:

### Fix the Worker code and redeploy

If the divergence was introduced by a recent deploy and the broken Worker can be replaced with one whose code matches the recorded history (either by reverting the change or by adding a patch branch), redeploy and let the server-retried Workflow Tasks succeed on the new Workers. The Workflow resumes from the point where it started failing; history up to that point is intact.

### Reset the Workflow past the divergence

If the divergence is already embedded in the history (e.g. new workflows have executed the broken path and recorded it) and a simple redeploy cannot recover them, `temporal workflow reset` rewinds a Workflow to an earlier Event ID, terminates the current run, and starts a new run with history copied up to the reset point.

```bash
temporal workflow reset \
    --workflow-id YourWorkflowId \
    --event-id YourLastGoodEventId
```

 Valid reset points per the Event encyclopedia are "`WorkflowTaskStarted`, `WorkflowTaskCompleted`, `WorkflowTaskTimedOut`, and `WorkflowTaskFailed`." Choose a `WorkflowTaskCompleted` immediately before the first failing WFT as the reset target: replay from that point against the fixed code avoids the divergence.

For batch resets, the `--type` values permitted are `FirstWorkflowTask`, `LastWorkflowTask`, and `BuildId`. The single-run reset example in the docs uses `LastContinuedAsNew`.

```bash
temporal workflow reset \
    --workflow-id YourWorkflowId \
    --type LastContinuedAsNew
```

 `--reapply-type` controls which Events are reapplied after the reset point; accepted values are `Signal, None`.

Confirm with the business owner before resetting: the Events after the reset point are re-executed, which means any activity that was run post-reset-point will be re-scheduled on replay — fine for idempotent operations, hazardous for irreversible external side effects.

## Quick routing

| Evidence | Go to |
|---|---|
| `WorkflowTaskFailed` Events with `cause` = Nondeterminism in the Event History | This file |
| `pendingWorkflowTask.attempt` climbing, but `WorkflowTaskFailed` Events show a different `cause` | [workflow-stuck.md §Pending Workflow Task and WorkflowTaskFailed loops](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops) |
| Worker logs show a class like `DeterminismViolationError` (TypeScript) or a nondeterminism error (other SDKs) | [Per-SDK error shape](#per-sdk-error-shape), [Reproducing ND locally](#reproducing-nd-locally-via-replay) |
| Need to reproduce the ND locally with breakpoints | [replay.md](replay.md) |
| Need a CI regression test around a fixed ND bug | [Reproducing ND locally via replay](#reproducing-nd-locally-via-replay) — use the SDK's bulk replayer |
| Planning a future-proof deploy strategy | [Remediation: Worker Versioning (preferred)](#remediation-worker-versioning-preferred) |
| Live incident, pre-existing Workflows are stuck, deploy-the-fix is not enough | [Remediation: fix and redeploy, or reset past the divergence](#remediation-fix-and-redeploy-or-reset-past-the-divergence) |
| The describe call itself fails (cannot reach/auth/authorize) | [connectivity.md](connectivity.md), [certificates.md](certificates.md), [authentication.md](authentication.md), [rate-limits.md](rate-limits.md) |

For the whole-stack picture and where this file sits in the diagnostic order, see [diagnostic-ladder.md](diagnostic-ladder.md).
