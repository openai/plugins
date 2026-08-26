# .NET Gotchas

.NET-specific mistakes and anti-patterns. See also [Common Gotchas](references/core/gotchas.md) for language-agnostic concepts.

## .NET Task Determinism

The biggest .NET gotcha. Many `Task` APIs implicitly use `TaskScheduler.Default`, which breaks determinism. The SDK detects some of these at runtime via an `EventListener`, but not all.

### Task.Run

```csharp
// BAD: Uses TaskScheduler.Default
await Task.Run(() => DoSomething());

// GOOD: Uses current (deterministic) scheduler
await Workflow.RunTaskAsync(() => DoSomething());
```

### Task.Delay / Thread.Sleep

```csharp
// BAD: Uses system timer
await Task.Delay(TimeSpan.FromMinutes(5));

// GOOD: Creates durable timer in event history
await Workflow.DelayAsync(TimeSpan.FromMinutes(5));
```

### ConfigureAwait(false)

```csharp
// BAD: Leaves the deterministic context
var result = await SomeCallAsync().ConfigureAwait(false);

// GOOD: Stays on deterministic scheduler (or just omit ConfigureAwait)
var result = await SomeCallAsync().ConfigureAwait(true);
var result = await SomeCallAsync(); // Also fine
```

### Task.WhenAll / Task.WhenAny

```csharp
// BAD: Potential non-determinism
await Task.WhenAll(task1, task2);
await Task.WhenAny(task1, task2);

// GOOD: Deterministic wrappers
await Workflow.WhenAllAsync(task1, task2);
await Workflow.WhenAnyAsync(task1, task2);
```

### Threading Primitives

```csharp
// BAD: System threading primitives
var mutex = new System.Threading.Mutex();
var semaphore = new SemaphoreSlim(1);

// GOOD: Temporal workflow-safe alternatives
var mutex = new Temporalio.Workflows.Mutex();
var semaphore = new Temporalio.Workflows.Semaphore(1);
```

See `references/dotnet/determinism-protection.md` for the complete list.

## Wrong Retry Classification

**Example:** Transient network errors should be retried. Authentication errors should not be.
See `references/dotnet/error-handling.md` to understand how to classify errors.

## Heartbeating

### Forgetting to Heartbeat Long Activities

```csharp
// BAD: No heartbeat, can't detect stuck activities
[Activity]
public async Task ProcessLargeFileAsync(string path)
{
    foreach (var chunk in ReadChunks(path))
        await ProcessAsync(chunk); // Takes hours, no heartbeat

// GOOD: Regular heartbeats with progress
[Activity]
public async Task ProcessLargeFileAsync(string path)
{
    var chunks = ReadChunks(path);
    for (var i = 0; i < chunks.Count; i++)
    {
        ActivityExecutionContext.Current.Heartbeat($"Processing chunk {i}");
        await ProcessAsync(chunks[i]);
    }
}
```

### Heartbeat Timeout Too Short

```csharp
// BAD: Heartbeat timeout shorter than processing time
await Workflow.ExecuteActivityAsync(
    (MyActivities a) => a.ProcessChunkAsync(),
    new()
    {
        StartToCloseTimeout = TimeSpan.FromMinutes(30),
        HeartbeatTimeout = TimeSpan.FromSeconds(10), // Too short!
    });

// GOOD: Heartbeat timeout allows for processing variance
await Workflow.ExecuteActivityAsync(
    (MyActivities a) => a.ProcessChunkAsync(),
    new()
    {
        StartToCloseTimeout = TimeSpan.FromMinutes(30),
        HeartbeatTimeout = TimeSpan.FromMinutes(2),
    });
```

Set heartbeat timeout as high as acceptable for your use case — each heartbeat counts as an action.

## Cancellation

### Not Handling Workflow Cancellation

```csharp
// BAD: Cleanup doesn't run on cancellation
[Workflow]
public class BadWorkflow
{
    [WorkflowRun]
    public async Task RunAsync()
    {
        await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.AcquireResourceAsync(),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.DoWorkAsync(),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.ReleaseResourceAsync(), // Never runs if cancelled!
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
    }
}

// GOOD: Use try/finally for cleanup
[Workflow]
public class GoodWorkflow
{
    [WorkflowRun]
    public async Task RunAsync()
    {
        await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.AcquireResourceAsync(),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        try
        {
            await Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.DoWorkAsync(),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        }
        finally
        {
            await Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.ReleaseResourceAsync(),
                new()
                {
                    StartToCloseTimeout = TimeSpan.FromMinutes(5),
                    CancellationToken = CancellationToken.None,
                });
        }
    }
}
```

### Not Handling Activity Cancellation

Activities must **opt in** to receive cancellation. This requires:

1. **Heartbeating** — Cancellation is delivered via heartbeat
2. **Checking the cancellation token** — Token is triggered when heartbeat detects cancellation

```csharp
// BAD: Activity ignores cancellation
[Activity]
public async Task LongActivityAsync()
{
    await DoExpensiveWorkAsync(); // Runs to completion even if cancelled
}

// GOOD: Heartbeat, check cancellation, and handle cleanup
[Activity]
public async Task LongActivityAsync()
{
    try
    {
        foreach (var item in items)
        {
            ActivityExecutionContext.Current.Heartbeat();
            ActivityExecutionContext.Current.CancellationToken.ThrowIfCancellationRequested();
            await ProcessAsync(item);
        }
    }
    catch (OperationCanceledException)
    {
        await CleanupAsync();
        throw;
    }
}
```

## Testing

### Not Testing Failures

It is important to make sure workflows work as expected under failure paths in addition to happy paths. Please see `references/dotnet/testing.md` for more info.

### Not Testing Replay

Replay tests help you test that you do not have hidden sources of non-determinism bugs in your workflow code. Please see `references/dotnet/testing.md` for more info.

## Timers and Sleep

### Using Task.Delay

```csharp
// BAD: Task.Delay uses system timer, not deterministic during replay
[Workflow]
public class BadWorkflow
{
    [WorkflowRun]
    public async Task RunAsync()
    {
        await Task.Delay(TimeSpan.FromMinutes(1)); // SDK will detect and fail the task
    }
}

// GOOD: Use Workflow.DelayAsync for deterministic timers
[Workflow]
public class GoodWorkflow
{
    [WorkflowRun]
    public async Task RunAsync()
    {
        await Workflow.DelayAsync(TimeSpan.FromMinutes(1)); // Deterministic
    }
}
```

**Why this matters:** `Task.Delay` uses the system clock, which differs between original execution and replay. `Workflow.DelayAsync` creates a durable timer in the event history, ensuring consistent behavior during replay.

## Dictionary Iteration Order

```csharp
// BAD: Dictionary iteration order is not guaranteed
var dict = new Dictionary<string, int> { ["b"] = 2, ["a"] = 1 };
foreach (var kvp in dict) // Order may differ between executions!
    await ProcessAsync(kvp.Key, kvp.Value);

// GOOD: Use SortedDictionary or sort before iterating
var dict = new SortedDictionary<string, int> { ["b"] = 2, ["a"] = 1 };
foreach (var kvp in dict) // Always iterates in key order
    await ProcessAsync(kvp.Key, kvp.Value);
```
