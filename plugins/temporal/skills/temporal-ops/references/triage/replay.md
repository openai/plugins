# Replay a Workflow Execution locally

This file is about the *tooling* that reproduces a recorded Workflow Execution in a debugger. For what replay divergence *means* as a concept — why the Worker Task fails, how the server classifies the cause, and how to remediate — see [non-determinism.md](non-determinism.md).

A Replay is "the method by which a Workflow Execution resumes making progress. During a Replay the Commands that are generated are checked against an existing Event History." Running a recorded history through a local replayer against your Worker source tree replays the Workflow Execution "to replicate errors" — how you reproduce a non-determinism error under a debugger and, via the bulk replayer, pin a CI regression test.

The **SDK replayer** is the general-purpose tool — documented for every supported SDK, it runs headless, attaches to any debugger, and drops into CI as a regression guard. The **VS Code extension** is a TypeScript-only convenience wrapper around the same replayer.

Out of scope:

- What non-determinism means, how to identify it in an Event History, and remediation options → [non-determinism.md](non-determinism.md)
- Worker not polling the Task Queue at all — nothing to replay, fix the Worker first → [worker-health.md](worker-health.md)
- Can't reach the server to fetch the history → [connectivity.md](connectivity.md), [authentication.md](authentication.md)
- The bottom-up layer model for routing between files → [diagnostic-ladder.md](diagnostic-ladder.md)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1 — Get the Event History](#step-1--get-the-event-history)
- [Step 2 — Run the SDK replayer (all supported SDKs)](#step-2--run-the-sdk-replayer-all-supported-sdks)
- [TEMPORAL_DEBUG: suppress the deadlock detector while stepping](#temporal_debug-suppress-the-deadlock-detector-while-stepping)
- [Interpreting a replay that diverges](#interpreting-a-replay-that-diverges)
- [Interpreting a replay that succeeds](#interpreting-a-replay-that-succeeds)
- [The VS Code extension (TypeScript only, interactive)](#the-vs-code-extension-typescript-only-interactive)

## Prerequisites

- The Workflow source tree at the commit that was deployed when the recorded Workflow Execution ran. Replaying current `main` against an older recording can produce divergence *for a different reason than the bug you're triaging*.
- The SDK installed and importable in that workspace (the replayer is part of the SDK, not a standalone binary).
- A client connection from that workspace to the Namespace holding the run, with read access to its history (see [authentication.md](authentication.md)) — or, failing that, a history file exported by someone who has it.

## Step 1 — Get the Event History

The replayer takes an Event History object, and every SDK client can fetch one. Fetch it in the same test that replays it.

| SDK | Fetch from the server |
|---|---|
| Go | `c.GetWorkflowHistory(ctx, id, runID, false, enums.HISTORY_EVENT_FILTER_TYPE_ALL_EVENT)` returns an iterator; accumulate `iter.Next()` into a `history.History` |
| Python | `client.list_workflows(<query>).map_histories()` |
| TypeScript | `client.workflow.getHandle(<workflow-id>).fetchHistory()`; `client.workflow.list({ query }).intoHistories()` for many |
| Java | `service.blockingStub().getWorkflowExecutionHistory(<request>)`, wrapped as `new WorkflowExecutionHistory(response.getHistory(), <workflow-id>)` |
| .NET | `client.ListWorkflowHistoriesAsync(<query>)` |
| Ruby | `client.list_workflows(<query>)` |
| PHP | `$replayer->replayFromServer(workflowType: ..., execution: ...)` fetches and replays in one call |

The list-based fetches require Advanced Visibility on the server.

Export a JSON file instead when the workspace has no client access to the Namespace, the history is being committed as a CI fixture, or the run has aged out of retention:

```bash
temporal workflow show \
    --workflow-id YourWorkflowId \
    --run-id YourRunId \
    --output json > history.json
```

`--output` accepts `text, json, jsonl, none` (default `text`); replay requires `json`. `--run-id` is not required.

If the run id is unknown, find it via `temporal workflow describe --workflow-id YourWorkflowId` (see [workflow-stuck.md](workflow-stuck.md)) or the Web UI.

For Cloud or any non-default target, add the usual connection flags (`--address`, `--namespace`, and either `--api-key` or the mTLS `--tls-*` flags). See [authentication.md](authentication.md).

## Step 2 — Run the SDK replayer (all supported SDKs)

Each SDK's testing-suite page documents a replayer. Names and signatures below are transcribed from those pages; they are what the docs state, not what the runtime type system exports at any given version. The history argument is whatever step 1 produced — a fetched object or a parsed file.

All of these run headless and the failure surfaces as a thrown error, which is enough to identify the divergence. A debugger is only needed to step through Workflow code; recommend that to the user rather than treating it as the default path.

### Go

```go
replayer := worker.NewWorkflowReplayer()
replayer.RegisterWorkflow(YourWorkflow)
err := replayer.ReplayWorkflowHistory(nil, hist)
```

 Use `worker.WorkflowReplayer` to "replay an existing Workflow Execution from its Event History to replicate errors." "If a noticeably different code path was followed or some code caused a deadlock, it will be returned in the error code."

To step through the Workflow function, attach Delve or an IDE debugger to the test process that calls `ReplayWorkflowHistory`, with `TEMPORAL_DEBUG=true` (see below).

### Python

```python
replayer = Replayer(workflows=[YourWorkflow])
await replayer.replay_workflows(histories)
```

 `replay_workflows` takes the iterator from step 1; if any replay fails, it raises. Set `fail_fast` to `false` to replay every history before reporting. From a file, the single-history form is `replayer.replay_workflow(WorkflowHistory.from_json(history_json_str))`. Histories fetched from the server or exported can be protobuf-encoded (`bytes`) while the `Replayer` works with decoded histories (like a `dict`); a `dict`-vs-`bytes` `TypeError` during replay means the history needs decoding first.

### TypeScript

```ts
const history = JSON.parse(await fs.promises.readFile('./history.json', 'utf8'));
await Worker.runReplayHistory(
  { workflowsPath: require.resolve('./your/workflows') },
  history,
);
```

 For bulk replay, use `Worker.runReplayHistories`.

Two error classes are documented: "When an Event History is replayed and non-determinism is detected (that is, the Workflow code is incompatible with the History), `DeterminismViolationError` is thrown. If replay fails for any other reason, `ReplayError` is thrown."

### Java

```java
File file = new File("history.json");
WorkflowReplayer.replayWorkflowExecution(file, MyWorkflow.class);
```

 Use `WorkflowReplayer` from the `temporal-testing` package. For bulk replay, `WorkflowReplayer.replayWorkflowExecutions`. "In both examples, if Event History is non-deterministic, an error is thrown. You can choose to wait until all histories have been replayed with `replayWorkflowExecutions` by setting the `failFast` argument to `false`."

### .NET

```csharp
var replayer = new WorkflowReplayer(
    new WorkflowReplayerOptions().AddWorkflow<MyWorkflow>());
await replayer.ReplayWorkflowAsync(
    WorkflowHistory.FromJson("my-workflow-id", historyJson));
```

 For bulk replay, iterate `replayer.ReplayWorkflowsAsync(...)` and check each `result.ReplayFailure`.

### Ruby

```ruby
replayer = Temporalio::Worker::WorkflowReplayer.new(workflows: [MyWorkflow])
replayer.replay_workflow(history)
```

 For bulk replay, pass `client.list_workflows(...)` to `replayer.replay_workflows(...)`; set `raise_on_replay_failure: true`, or inspect each `result.replay_failure`.

### PHP

The replayer is `\Temporal\Testing\Replay\WorkflowReplayer`. Replay from a running server with `replayFromServer(...)`, from an exported JSON file with `replayFromJSON(...)`, or from an in-memory history with `replayHistory($history)`. A non-deterministic replay throws `\Temporal\Testing\Replay\Exception\ReplayerException`.

## TEMPORAL_DEBUG: suppress the deadlock detector while stepping

Two SDKs explicitly document a debug-mode env var. Without it, pausing on a breakpoint for more than a second can cause the Worker's deadlock detector to fail the Workflow Task *during your debugging session*:

- **Go.** "The Temporal Go SDK includes deadlock detection which fails a Workflow Task in case the code blocks over a second without relinquishing execution control. Because of this you can often encounter a `PanicError: Potential deadlock detected` while stepping through Workflow Definitions during debugging. To alleviate this issue, you can set the `TEMPORAL_DEBUG` environment variable to `true` before debugging your Workflow Definition."
- **Java.** "The Temporal Java SDK includes deadlock detection which fails a Workflow Task in case the code blocks over a second without relinquishing execution control. Because of this you can often encounter the `PotentialDeadlockException` Exception while stepping through Workflow code during debugging. To alleviate this issue, you can set the `TEMPORAL_DEBUG` environment variable to true before debugging your Workflow code."

Both pages add the same warning: "Make sure to set `TEMPORAL_DEBUG` to true only during debugging."

Python and TypeScript debugging pages do not document a `TEMPORAL_DEBUG` env var in the sources consulted.

## Interpreting a replay that diverges

The documented behavior when replay detects non-determinism:

- **TypeScript**: throws `DeterminismViolationError`; any other replay failure throws `ReplayError`.
- **Go**: the replayer returns an error from `ReplayWorkflowHistory`; the docs describe the condition as "cause the Workflow to fail with a nondeterminism error" without pinning a public type name.
- **Java**: `WorkflowReplayer.replayWorkflowExecution` throws; the versioning doc describes the condition as "This would cause the Workflow to fail with a nondeterminism error."
- **Python**: `Replayer.replay_workflow` raises; if any replay fails, the code raises an exception.

The error is raised where the SDK detected the mismatch — typically inside *the Worker machinery*, not on the Workflow line that emitted the bad Command. A debugger halts at the same place. To locate the offending Workflow line, compare:

- The last Command the code was about to emit (the frame just below the SDK entry in the stack), and
- The next non-bookkeeping Event in the recorded history (see [non-determinism.md §Identifying ND from the Event History](non-determinism.md#identifying-nd-from-the-event-history)).

The divergence is the mismatch between those two. The encyclopedia frames this as: "If a generated Command doesn't match what it needs to in the existing Event History, then the Workflow Execution returns a non-deterministic error."

For remediation paths (Worker Versioning, per-SDK patching, reset past the divergence), return to [non-determinism.md §Remediation](non-determinism.md#remediation-worker-versioning-preferred).

## Interpreting a replay that succeeds

If replay succeeds locally against the checked-out source, but production Workers keep failing with the same Workflow Execution, the deployed Worker code almost certainly differs from the local checkout. Find the deployed build (via Worker Versioning metadata if used, or your deploy system) and reproduce from that commit. See [non-determinism.md §Reproducing ND locally via replay](non-determinism.md#reproducing-nd-locally-via-replay).

A local-replay success on the *current* source with production still failing is also the classic case Worker Versioning is meant to prevent. See [non-determinism.md §Remediation: Worker Versioning (preferred)](non-determinism.md#remediation-worker-versioning-preferred).

## The VS Code extension (TypeScript only, interactive)

Temporal publishes a VS Code extension that wraps the TypeScript SDK's replayer in the VS Code debugger UI — one-click "open history → set breakpoints → step through." For Workflows authored in any other SDK, skip it and use the SDK replayer above under your IDE's native debugger; the observability is the same (a stack trace at the point the SDK detected divergence) and the replayer APIs are first-party and doc-backed.

Claims in this section come from the extension's marketplace listing; the Temporal docs themselves do not document the extension.

- **Install:** search the VS Code Marketplace for "Temporal" and install the extension published by **Temporal Technologies Inc.** (`temporal-technologies.temporalio`). As of the listing consulted, it debugs **TypeScript workflows only**.
- **Configure:** the replayer is driven by a TypeScript entrypoint that calls `startDebugReplayer` with a `workflowsPath`; the extension reads the path from the `temporal.replayerEntrypoint` setting (default `src/debug-replayer.ts`).
- **Run:** **Temporal: Open Panel** from the Command Palette → enter a Workflow ID (fetched from the configured server, default `localhost:7233`) or pick a history JSON file → **Start** → set breakpoints in Workflow source or on history events, then step through. For Cloud, supply the Cloud gRPC endpoint plus the credentials in [authentication.md](authentication.md) and [certificates.md](certificates.md).

For anything the marketplace page does not spell out (a supported-SDK matrix beyond TypeScript, the full command list, `launch.json` recipes, OS requirements, mTLS-vs-API-key support), consult the extension's README for the version you installed — the citations here are a point-in-time snapshot.
