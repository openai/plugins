# .NET Determinism Protection

## Overview

The .NET SDK has no runtime sandbox. Determinism is enforced by **developer convention** and **runtime task detection**. Unlike the Python and TypeScript SDKs, the .NET SDK will not intercept or replace non-deterministic calls at compile time or import time. The SDK does provide a runtime `EventListener` that detects some invalid task scheduling, but catching all non-deterministic code requires following the rules below and testing, in particular replay tests (see `references/dotnet/testing.md`).

## Runtime Task Detection

By default, the .NET SDK enables an `EventListener` that monitors task events. When workflow code accidentally starts a task on the wrong scheduler (e.g., via `Task.Run`), an `InvalidWorkflowOperationException` is thrown. This causes the workflow task to fail, which will continuously retry until the code is fixed.

```csharp
// This will be detected at runtime and fail the workflow task
[Workflow]
public class BadWorkflow
{
    [WorkflowRun]
    public async Task RunAsync()
    {
        // BAD: Task.Run uses TaskScheduler.Default
        await Task.Run(() => DoSomething());
    }
}
```

## .NET Task Determinism Rules

Many .NET `Task` APIs implicitly use `TaskScheduler.Default`, which breaks determinism. Here are the key rules:

**Do NOT use:**

- `Task.Run` — uses default scheduler. Use `Workflow.RunTaskAsync`.
- `Task.ConfigureAwait(false)` — leaves current context. Use `ConfigureAwait(true)` or omit.
- `Task.Delay` / `Task.Wait` / timeout-based `CancellationTokenSource` — uses system timers. Use `Workflow.DelayAsync` / `Workflow.WaitConditionAsync`.
- `Task.WhenAny` — use `Workflow.WhenAnyAsync`.
- `Task.WhenAll` — use `Workflow.WhenAllAsync` (technically safe currently, but wrapper is recommended).
- `CancellationTokenSource.CancelAsync` — use `CancellationTokenSource.Cancel`.
- `System.Threading.Semaphore` / `SemaphoreSlim` / `Mutex` — use `Temporalio.Workflows.Semaphore` / `Mutex`.

**Be wary of:**

- Third-party libraries that implicitly use `TaskScheduler.Default`
- `Dataflow` blocks and similar concurrency libraries with hidden default scheduler usage

## Best Practices

1. **Always use `Workflow.*` alternatives** for Task operations in workflows
2. **Don't disable the `EventListener`** — it's on by default and catches mistakes at runtime
3. **Separate workflow and activity code** into different files/projects for clarity
4. **Use `SortedDictionary`** or sort collections before iterating — `Dictionary<TKey, TValue>` iteration order is not guaranteed
5. **Test with replay** to catch non-determinism early
6. **Review third-party library usage** in workflow code for hidden default scheduler usage
