# Ruby SDK Determinism

## Overview

The Ruby SDK enforces workflow determinism through **Illegal Call Tracing** (via `TracePoint`) and a **Durable Fiber Scheduler**. This is not a sandbox like Python's `SandboxedWorkflowRunner`; instead, it intercepts illegal calls at runtime on the workflow fiber.

## Why Determinism Matters: History Replay

Temporal re-executes workflow code from the beginning on recovery (worker restart, continue-as-new, etc.). Commands already recorded in history are matched against replayed commands. If the code produces different commands on replay, the workflow fails with a non-determinism error.

All workflow code must therefore be deterministic: same input and history must produce the same sequence of commands every time.

## SDK Protection: Illegal Call Tracing

The Ruby SDK installs a `TracePoint` on the workflow fiber thread. Every method call is checked against a configurable set of illegal calls. If a forbidden method is invoked, the SDK raises `Temporalio::Workflow::NondeterminismError`.

Configuration is via the `illegal_workflow_calls` parameter on `Temporalio::Worker.new`. The default set is available at:

```ruby
Temporalio::Worker.default_illegal_workflow_calls
```

## Forbidden Operations in Workflows

The following are forbidden inside workflow code by default:

- `Kernel.sleep` -- blocks the fiber non-deterministically
- `Time.now` (without args) -- returns wall-clock time
- `Thread.new` -- spawns non-deterministic OS threads
- `IO` operations (`IO.read`, `IO.write`, `File.open`, etc.)
- `Random.rand` / `SecureRandom` -- non-deterministic randomness
- `Process` calls (`Process.spawn`, `Process.exec`, etc.)
- Network calls (`Net::HTTP`, `Socket`, etc.)
- `Mutex` / `synchronize`

## Safe Builtin Alternatives to Common Non Deterministic Things

| Forbidden | Safe Alternative |
|-----------|------------------|
| `Kernel.sleep(n)` | `Temporalio::Workflow.sleep(n)` |
| `Time.now` | `Temporalio::Workflow.now` |
| `Random.rand` / `SecureRandom` | `Temporalio::Workflow.random.rand(100)` |
| `SecureRandom.uuid` | `Temporalio::Workflow.uuid` |
| `Logger.new` / `puts` | `Temporalio::Workflow.logger.info(...)` |
| `Mutex` / `synchronize` | explicit `Temporalio::Workflow::Mutex` |

## Testing Replay Compatibility

Use `Temporalio::Worker::WorkflowReplayer` to verify that workflow code is replay-compatible against recorded histories. See `testing.md` for details.

```ruby
replayer = Temporalio::Worker::WorkflowReplayer.new(
  workflows: [MyWorkflow]
)
replayer.replay_workflow(workflow_history)
```

## Best Practices

- Use `Temporalio::Workflow.sleep`, `.now`, `.random`, `.uuid`, `.logger` instead of stdlib equivalents.
- Delegate all I/O, network calls, and side effects to activities.
- Test with `WorkflowReplayer` against saved histories before deploying workflow changes.
- Use `Temporalio::Workflow.logger` for all logging inside workflows -- it is replay-aware and suppresses duplicate logs during replay.
