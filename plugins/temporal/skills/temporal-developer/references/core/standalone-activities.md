> [!NOTE]
> Standalone Activities are in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

# Standalone Activities (Concepts)

This document provides core conceptual explanations of Standalone Activities in Temporal. For language-specific implementation details, see `references/{your_language}/standalone-activities.md` for the language you are working in (Python, TypeScript, Java, .NET, Go).

## What is a Standalone Activity?

A **Standalone Activity** is a top-level Activity Execution started directly by a Client, without using a Workflow. It is Temporal's job queue — the simplest way to run a single durable, retryable task.

The rule of thumb:

- **Need to orchestrate multiple Activities?** Use a Workflow.
- **Just need to execute a single Activity?** Use a Standalone Activity.

The same Activity Function code runs in both modes with no changes — the only difference is how it is invoked. An Activity defined for a Workflow can also be executed standalone, and the Worker that hosts it does not need to know how it will be invoked.

Compared to wrapping a single Activity in a Workflow, a Standalone Activity:

- Reduces billable actions in Temporal Cloud.
- Lowers latency for short-lived executions (fewer Worker round-trips).
- Lives in a separate ID space from Workflows.

### Use cases

Standalone Activities fit durable single-job processing where you don't need multi-step orchestration:

- Sending an email
- Processing a webhook
- Syncing data
- Any single-function task that benefits from built-in retries and timeouts

### Key features

- Execute Activities as a top-level primitive, without Workflow overhead.
- Native async job lifecycle: **schedule → dispatch → process → result**.
- Arbitrary-length jobs, with heartbeats for progress tracking.
- **At-least-once execution by default**, with native retry policy and timeouts.
- **At-most-once execution** when the retry policy's maximum attempts is 1.
- Addressable by Activity ID / Run ID for result retrieval, cancellation, and termination.
- Deduplication via configurable conflict policies.
- Priority and fairness support.
- Full visibility — list and count executions.

## Using Standalone Activities

### Defining activities

Defining standalone activities is IDENTICAL to defining activities callable from a workflow - there is no distinction AT ALL between the two at activity definition or worker configuration site. Follow language-specific guidance for how to normally define activities and configure workers to run them.

### Calling and Interacting with Standalone Activities

The CLI and every SDK exposes the same conceptual operations against a Standalone Activity (method names differ per language — see the language reference):

- **Execute** — durably enqueue the Activity, wait for a Worker to run it, and return the result.
- **Start** — durably enqueue the Activity and return a handle immediately, without waiting.
- **Get handle** — rebind a handle to a previously started Activity by ID (and optionally Run ID).
- **Get result** — wait on a handle for completion. `execute` is equivalent to `start` followed by awaiting the handle's result.
- **Cancel / Terminate** — via the handle or CLI.

**Choosing an Activity ID.** Every Standalone Activity call requires an **Activity ID**, which uniquely identifies that one call. It is the key you use later to get the result, describe, cancel, or terminate the Activity, and it is what conflict/reuse policies dedupe against. Use a **business-logic identifier** that uniquely identifies the call — for example `send-welcome-email:user-42`, `sync-invoice:INV-2026-001`, or `process-webhook:<event-id>`. This makes Activities addressable and naturally deduplicated by your domain. Only if you genuinely have no meaningful business-level identifier should you generate a **UUID** to use as the Activity ID.

Visibility operations are available as well:
- **List** — enumerate Standalone Activity Executions matching a query. Only Standalone Activities are returned; Activities running inside Workflows are not included.
- **Count** — return the total number of executions matching a query (running, completed, failed, etc. — not the number of queued tasks).
- **Describe** — via the handle or CLI.

See below for a quick reference how to call these operations from the CLI rather than SDKs.

> [!IMPORTANT]
> When using an SDK, these operations are owned by the Temporal Client, and belong **in your non-workflow application code**. It is INVALID to call an activity as a standalone activity from within a workflow: you instead should use standard within-workflow activity calls.

**Currently Supported SDKs: Python, TypeScript, Java, .NET, Go**

## Quick CLI Standalone Activity Man Page

Ultimately, any standalone activity invocation code should live in your application code and use the appropriate SDK, but the Temporal CLI is a quick and easy way to test invoking standalone activities during development. All subcommands live under `temporal activity`.

The key operations are:

**Execute (start and wait for the result).** Blocks until the Activity completes and prints the result to stdout. Requires `--activity-id`, `--type`, `--task-queue`, and at least one of `--start-to-close-timeout` / `--schedule-to-close-timeout`:

```bash
temporal activity execute \
  --activity-id my-activity-id \
  --type ComposeGreeting \
  --task-queue my-task-queue \
  --start-to-close-timeout 10s \
  --input '{"some-key": "some-value"}'
```

`--input` takes a JSON value; pass it multiple times for multiple positional arguments. `--input-file` is also a convenient option for larger inputs. The same required flags apply to `start` below.

Reminder: `--activity-id` must be unique across all activity calls, as discussed above.

**Start (do not wait).** Enqueues the Activity and prints the Activity ID and Run ID without blocking:

```bash
temporal activity start \
  --activity-id my-activity-id \
  --type ComposeGreeting \
  --task-queue my-task-queue \
  --start-to-close-timeout 10s \
  --input '{"some-key": "some-value"}'
```

Outputs this JSON shape:

```json
{
  "activityId": "my-activity-id",
  "runId": "019e84d3-949a-7a0e-ae78-63b8a0b172bd",
  "namespace": "default"
}
```

**Result (wait for a started Activity).** Waits for completion and prints the result. `--run-id` is optional and defaults to the latest run of that Activity ID:

```bash
temporal activity result --activity-id my-activity-id
```

**Describe (current state of one Activity).** Shows status, run state, task queue, timeouts, attempt count, etc.:

```bash
temporal activity describe --activity-id my-activity-id
```

**List / Count (visibility across many Activities).** Only Standalone Activity Executions are returned (Activities running inside Workflows are not):

```bash
temporal activity list
temporal activity count
```

**Cancel / Terminate (stop an Activity).** `cancel` requests cooperative cancellation (surfaced to the Activity on its next heartbeat response); `terminate` forcefully ends it (Activity code cannot see or respond to it). Both accept `--reason`:

```bash
temporal activity cancel    --activity-id my-activity-id --reason "no longer needed"
temporal activity terminate --activity-id my-activity-id --reason "no longer needed"
```

## Observability

All existing Activity metrics apply to Standalone Activities (scheduled, started, completed, failed, timed out, canceled).

## Public Preview limitations

- Pause, reset, and update options are not supported (scheduled for GA).
- The `TerminateExisting` conflict policy and `TerminateIfRunning` reuse policy are not yet supported.

## Temporal CLI support

- Requires **Temporal CLI v1.7.0+** and **Temporal Server v1.31.0+**. See `references/core/install_cli.md` if you need to update the CLI.
- The Temporal Dev Server (`temporal server start-dev`) has Standalone Activities enabled by default.

## Temporal Cloud support

Standalone Activities are available in Temporal Cloud as a Public Preview feature. Because the SDK client config loaders read environment variables and TOML profiles, the same code runs against a local server or Temporal Cloud with no code changes.
