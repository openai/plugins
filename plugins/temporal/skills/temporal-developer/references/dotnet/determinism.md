# .NET SDK Determinism

## Overview

The .NET SDK has NO runtime sandbox (unlike Python/TypeScript). Workflows must be deterministic for replay, and determinism is enforced by developer convention and runtime task detection via an `EventListener` (see `references/dotnet/determinism-protection.md`).

## Why Determinism Matters: History Replay

Temporal provides durable execution through **History Replay**. When a Worker restores workflow state, it re-executes workflow code from the beginning. This requires the code to be **deterministic**. See `references/core/determinism.md` for a deep explanation.

## Forbidden Operations in Workflows

The following are forbidden inside workflow code but are appropriate to use in activities.

```csharp
// DO NOT do these in workflows:
await Task.Run(() => { });              // Uses default scheduler
await Task.Delay(TimeSpan.FromSeconds(1)); // System timer
var now = DateTime.UtcNow;              // System clock
var r = new Random().Next();            // Non-deterministic
var id = Guid.NewGuid();               // Non-deterministic
File.ReadAllText("file.txt");           // I/O
await httpClient.GetAsync("...");       // Network I/O
```

Most non-determinism and side effects should be wrapped in Activities.

## Safe Builtin Alternatives

| Forbidden | Safe Alternative |
|-----------|------------------|
| `DateTime.Now` / `DateTime.UtcNow` | `Workflow.UtcNow` |
| `Random` | `Workflow.Random` |
| `Guid.NewGuid()` | `Workflow.NewGuid()` |
| `Task.Delay` | `Workflow.DelayAsync` |
| `Thread.Sleep` | `Workflow.DelayAsync` |
| `Task.Run` | `Workflow.RunTaskAsync` |
| `Task.WhenAll` | `Workflow.WhenAllAsync` |
| `Task.WhenAny` | `Workflow.WhenAnyAsync` |
| `System.Threading.Mutex` | `Temporalio.Workflows.Mutex` |
| `System.Threading.Semaphore` | `Temporalio.Workflows.Semaphore` |
| `CancellationTokenSource.CancelAsync` | `CancellationTokenSource.Cancel` |

## Testing Replay Compatibility

Use `WorkflowReplayer` to verify your code changes are compatible with existing histories. See the Workflow Replay Testing section of `references/dotnet/testing.md`.

## Best Practices

1. Always use `Workflow.*` APIs instead of standard .NET equivalents (see table above)
2. Never use `ConfigureAwait(false)` in workflows
3. Use `SortedDictionary` or sort before iterating collections
4. Move all I/O operations (network, filesystem, database) into activities
5. Use `Workflow.Logger` instead of `Console.WriteLine` for replay-safe logging
6. Keep workflow code focused on orchestration; delegate non-deterministic work to activities
7. Test with replay after making changes to workflow definitions
