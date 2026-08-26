# CLI Workflow Commands for Developers

Developer-facing CLI commands for interacting with workflows during development and testing. These commands work identically against a dev server, a self-hosted cluster, or Temporal Cloud -- only the connection descriptor changes.

**IMPORTANT:** In order to make outputs of `temporal` CLI commands easier to read and parse, use the `--output json` flag.

## Table of contents

- [Workflow start](#workflow-start)
- [Workflow execute](#workflow-execute)
- [Workflow signal](#workflow-signal)
- [Workflow query](#workflow-query)
- [Workflow update](#workflow-update)
- [Workflow signal-with-start](#workflow-signal-with-start)
- [Workflow result](#workflow-result)
- [Workflow metadata](#workflow-metadata)

## Workflow start

Start a new Workflow Execution asynchronously. Returns the Workflow ID and Run ID.

```bash
temporal workflow start \
    --output json \
    --workflow-id YourWorkflowId \
    --type YourWorkflow \
    --task-queue YourTaskQueue \
    --input '{"some-key": "some-value"}'
```

Required flags: `--type`, `--task-queue`. Optional `--workflow-id` -- the Service generates a UUID if omitted.

| Flag | Required | Purpose |
|---|---|---|
| `--type` | Yes | Workflow Type name. |
| `--task-queue`, `-t` | Yes | Workflow Task queue. |
| `--workflow-id`, `-w` | No | Workflow ID. Service generates a UUID if omitted. |
| `--input`, `-i` | No | Input value (JSON). Repeatable. Mutually exclusive with `--input-file`. |
| `--input-file` | No | Read input from file(s). Repeatable. Mutually exclusive with `--input`. |
| `--input-base64` | No | Decode `--input` as base64 before sending. |
| `--input-meta` | No | Override payload metadata as `KEY=VALUE` (e.g., `encoding=json/protobuf`). Repeatable. |
| `--id-reuse-policy` | No | How to reuse a previously-seen Workflow ID. Values: `AllowDuplicate`, `AllowDuplicateFailedOnly`, `RejectDuplicate`, `TerminateIfRunning`. |
| `--id-conflict-policy` | No | How to resolve conflicts with a running execution sharing the same ID. Values: `Fail`, `UseExisting`, `TerminateExisting`. |
| `--execution-timeout` | No | Fail a Workflow Execution if it lasts longer than this (duration). Includes retries and ContinueAsNew. |
| `--run-timeout` | No | Fail a single Workflow Run if it lasts longer than this (duration). |
| `--task-timeout` | No | Start-to-close timeout for a Workflow Task (duration). |
| `--search-attribute` | No | Set a search attribute as `KEY=VALUE` (JSON values). Repeatable. |
| `--memo` | No | Attach unindexed metadata as `KEY="VALUE"` (JSON values). Repeatable. |
| `--start-delay` | No | Delay before starting (duration). Cannot combine with `--cron`. |
| `--cron` | No | Legacy cron schedule (prefer `temporal schedule create`). |
| `--priority-key` | No | Priority 1-5 (default 3). Lower = higher priority. |
| `--fairness-key` | No | Proportional task dispatch grouping key (string, max 64 bytes). |
| `--fairness-weight` | No | Weight for this fairness key (0.001-1000). Keys dispatched proportionally. |
| `--static-summary` | No | Human-readable summary for UIs. Single line. _(Experimental)_ |
| `--static-details` | No | Human-readable details for UIs. May be multi-line. _(Experimental)_ |
| `--fail-existing` | No | Fail if the Workflow already exists. |
| `--headers` | No | Temporal workflow headers as `KEY=VALUE` (JSON). Not gRPC headers. Repeatable. |

## Workflow execute

Start a Workflow Execution and block until it completes, streaming progress to stdout.

```bash
temporal workflow execute \
    --output json \
    --workflow-id YourWorkflowId \
    --type YourWorkflow \
    --task-queue YourTaskQueue \
    --input '{"some-key": "some-value"}'
```

Accepts the same start-time flags as `workflow start`. The only `workflow execute` specific flag is `--detailed` (display events as sections rather than a table; not applied to JSON output). With `--output json`, the emitted blob includes the full `history` key for the run.

A non-zero exit code means the Workflow failed, was cancelled, terminated, or timed out. Useful for one-shot scripts and smoke tests during development.

## Workflow signal

Send an asynchronous signal to a running Workflow Execution.

```bash
temporal workflow signal \
    --output json \
    --workflow-id YourWorkflowId \
    --name YourSignal \
    --input '{"YourInputKey": "YourInputValue"}'
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes (or `--query`) | Workflow ID. |
| `--name` | Yes | Signal name. |
| `--input`, `-i` | No | Input value (JSON). Repeatable. |
| `--run-id`, `-r` | No | Pin to a specific run. Only with `--workflow-id`. |

For bulk signaling with `--query` (runs as a batch job), see skill-temporal-ops.

## Workflow query

Invoke a read-only query handler. Queries do not mutate workflow state and can run on both running and completed workflows.

```bash
temporal workflow query \
    --output json \
    --workflow-id YourWorkflowId \
    --name YourQueryType \
    --input '{"YourInputKey": "YourInputValue"}'
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--name` | Yes | Query Type/Name. |
| `--input`, `-i` | No | Input value (JSON). Repeatable. |
| `--run-id`, `-r` | No | Run ID. |
| `--reject-condition` | No | Reject queries based on Workflow state. Accepted values: `not_open`, `not_completed_cleanly`. |

## Workflow update

Update is a command **group**, not a single command. It has four subcommands: `describe`, `execute`, `result`, `start`.

### `temporal workflow update start`

Initiate an update and wait for the validator to accept or reject it.

```bash
temporal workflow update start \
    --output json \
    --workflow-id YourWorkflowId \
    --name YourUpdate \
    --input '{"some-key": "some-value"}' \
    --wait-for-stage accepted
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--name` | Yes | Handler method name. |
| `--wait-for-stage` | Yes | Update stage to wait for. The **only** accepted value is `accepted`. Required to allow a future CLI version to choose a default. |
| `--input`, `-i` | No | Input value (JSON). Repeatable. |
| `--update-id` | No | Idempotency key. Defaults to a UUID. |
| `--run-id`, `-r` | No | Run ID. If unset, targets the currently-running execution. |
| `--first-execution-run-id` | No | Pin the update to the last execution in the chain started with this Run ID. |

### `temporal workflow update execute`

Start an update and wait for it to complete or fail. Can also wait on an existing in-flight update by reusing its Update ID.

```bash
temporal workflow update execute \
    --output json \
    --workflow-id YourWorkflowId \
    --name YourUpdate \
    --input '{"some-key": "some-value"}'
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--name` | Yes | Handler method name. |
| `--input`, `-i` | No | Input value (JSON). Repeatable. |
| `--update-id` | No | Idempotency key. Defaults to a UUID. |
| `--run-id`, `-r` | No | Run ID. If unset, targets the currently-running execution. |
| `--first-execution-run-id` | No | Pin the update to the last execution in the chain started with this Run ID. |

### `temporal workflow update result`

Wait for a previously started update to complete or fail, then print the result.

```bash
temporal workflow update result \
    --output json \
    --workflow-id YourWorkflowId \
    --update-id YourUpdateId
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--update-id` | Yes | Update ID. Must be unique per Workflow Execution. |
| `--run-id`, `-r` | No | Run ID. |

### `temporal workflow update describe`

Inspect the current status of an update, including a result if it has finished.

```bash
temporal workflow update describe \
    --output json \
    --workflow-id YourWorkflowId \
    --update-id YourUpdateId
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--update-id` | Yes | Update ID. Must be unique per Workflow Execution. |
| `--run-id`, `-r` | No | Run ID. |

## Workflow signal-with-start

Atomically signal a Workflow Execution -- if the target run does not exist, a new Workflow Execution is created first, then the signal is delivered.

```bash
temporal workflow signal-with-start \
    --output json \
    --signal-name YourSignal \
    --signal-input '{"some-key": "some-value"}' \
    --workflow-id YourWorkflowId \
    --type YourWorkflowType \
    --task-queue YourTaskQueue \
    --input '{"some-key": "some-value"}'
```

Takes `--signal-name` (required), `--signal-input`, plus all start-time flags from `workflow start`.

| Flag | Required | Purpose |
|---|---|---|
| `--signal-name` | Yes | Signal name. |
| `--signal-input` | No | Signal input value (JSON). Repeatable. |
| `--type` | Yes | Workflow Type name. |
| `--task-queue`, `-t` | Yes | Workflow Task queue. |
| `--workflow-id`, `-w` | No | Workflow ID. Service generates a UUID if omitted. |

All other start-time flags (`--input`, `--id-reuse-policy`, `--id-conflict-policy`, timeouts, `--search-attribute`, `--memo`, etc.) are accepted. See [Workflow start](#workflow-start) for the full flag table.

## Workflow result

Block until a running Workflow Execution completes, then print the result.

```bash
temporal workflow result \
    --output json \
    --workflow-id YourWorkflowId
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--run-id`, `-r` | No | Run ID. |

## Workflow metadata

Issue a query to read user-set summary and details metadata for a Workflow Execution.

```bash
temporal workflow metadata \
    --output json \
    --workflow-id YourWorkflowId
```

| Flag | Required | Purpose |
|---|---|---|
| `--workflow-id`, `-w` | Yes | Workflow ID. |
| `--run-id`, `-r` | No | Run ID. |
| `--reject-condition` | No | Reject queries based on Workflow state. Accepted values: `not_open`, `not_completed_cleanly`. |
