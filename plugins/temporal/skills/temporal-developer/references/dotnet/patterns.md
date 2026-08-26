# .NET SDK Patterns

## Signals

```csharp
[Workflow]
public class OrderWorkflow
{
    private bool _approved;
    private readonly List<string> _items = new();

    [WorkflowSignal]
    public async Task ApproveAsync()
    {
        _approved = true;
    }

    [WorkflowSignal]
    public async Task AddItemAsync(string item)
    {
        _items.Add(item);
    }

    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        await Workflow.WaitConditionAsync(() => _approved);
        return $"Processed {_items.Count} items";
    }
}
```

## Dynamic Signal Handlers

For handling signals with names not known at compile time. Use cases for this pattern are rare — most workflows should use statically defined signal handlers.

```csharp
[Workflow]
public class DynamicSignalWorkflow
{
    private readonly Dictionary<string, List<string>> _signals = new();

    [WorkflowSignal(Dynamic = true)]
    public async Task HandleSignalAsync(string signalName, IRawValue[] args)
    {
        if (!_signals.ContainsKey(signalName))
            _signals[signalName] = new List<string>();
        var value = Workflow.PayloadConverter.ToValue<string>(args.Single());
        _signals[signalName].Add(value);
    }

    [WorkflowRun]
    public async Task<Dictionary<string, List<string>>> RunAsync()
    {
        await Workflow.WaitConditionAsync(() => _signals.ContainsKey("done"));
        return _signals;
    }
}
```

## Queries

**Important:** Queries must NOT modify workflow state or have side effects.

```csharp
[Workflow]
public class StatusWorkflow
{
    private string _status = "pending";
    private int _progress;

    [WorkflowQuery]
    public string GetStatus() => _status;

    [WorkflowQuery]
    public int Progress => _progress;

    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        _status = "running";
        for (var i = 0; i < 100; i++)
        {
            _progress = i;
            await Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.ProcessItem(i),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(1) });
        }
        _status = "completed";
        return "done";
    }
}
```

## Dynamic Query Handlers

For handling queries with names not known at compile time. Use cases for this pattern are rare — most workflows should use statically defined query handlers.

```csharp
[Workflow]
public class DynamicQueryWorkflow
{
    private readonly SortedDictionary<string, string> _state = new()
    {
        ["status"] = "running",
        ["progress"] = "0",
    };

    [WorkflowQuery(Dynamic = true)]
    public string HandleQuery(string queryName, IRawValue[] args)
    {
        return _state.GetValueOrDefault(queryName, "unknown");
    }

    [WorkflowRun]
    public async Task RunAsync() { /* ... */ }
}
```

## Updates

```csharp
[Workflow]
public class OrderWorkflow
{
    private readonly List<string> _items = new();

    [WorkflowUpdate]
    public async Task<int> AddItemAsync(string item)
    {
        _items.Add(item);
        return _items.Count;
    }

    [WorkflowUpdateValidator(nameof(AddItemAsync))]
    public void ValidateAddItem(string item)
    {
        if (string.IsNullOrEmpty(item))
            throw new ArgumentException("Item cannot be empty");
        if (_items.Count >= 100)
            throw new InvalidOperationException("Order is full");
    }

    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        await Workflow.WaitConditionAsync(() => _items.Count > 0);
        return $"Order with {_items.Count} items";
    }
}
```

**Important:** Validators must NOT mutate workflow state or do anything blocking (no activities, sleeps, or other commands). They are read-only, similar to query handlers. Throw an exception to reject the update; return void to accept.

## Child Workflows

```csharp
[Workflow]
public class ParentWorkflow
{
    [WorkflowRun]
    public async Task<List<string>> RunAsync(List<Order> orders)
    {
        var results = new List<string>();
        foreach (var order in orders)
        {
            var result = await Workflow.ExecuteChildWorkflowAsync(
                (ProcessOrderWorkflow wf) => wf.RunAsync(order),
                new()
                {
                    Id = $"order-{order.Id}",
                    // Control what happens to child when parent completes
                    // Terminate (default), Abandon, RequestCancel
                    ParentClosePolicy = ParentClosePolicy.Abandon,
                });
            results.Add(result);
        }
        return results;
    }
}
```

## Handles to External Workflows

```csharp
[Workflow]
public class CoordinatorWorkflow
{
    [WorkflowRun]
    public async Task RunAsync(string targetWorkflowId)
    {
        var handle = Workflow.GetExternalWorkflowHandle<TargetWorkflow>(targetWorkflowId);

        // Signal the external workflow
        await handle.SignalAsync(wf => wf.DataReadyAsync(new DataPayload()));

        // Or cancel it
        await handle.CancelAsync();
    }
}
```

## Parallel Execution

```csharp
[Workflow]
public class ParallelWorkflow
{
    [WorkflowRun]
    public async Task<string[]> RunAsync(string[] items)
    {
        var tasks = items.Select(item =>
            Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.ProcessItem(item),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) }));

        return await Workflow.WhenAllAsync(tasks);
    }
}
```

## Deterministic Task Alternatives

.NET `Task` APIs often use `TaskScheduler.Default` implicitly. Use Temporal's deterministic alternatives:

```csharp
// Instead of Task.WhenAll:
await Workflow.WhenAllAsync(task1, task2, task3);

// Instead of Task.WhenAny:
await Workflow.WhenAnyAsync(task1, task2);

// Instead of Task.Run:
await Workflow.RunTaskAsync(() => SomeWork());

// Instead of Task.Delay:
await Workflow.DelayAsync(TimeSpan.FromMinutes(5));

// Instead of System.Threading.Mutex:
var mutex = new Temporalio.Workflows.Mutex();
await mutex.WaitOneAsync();
try { /* critical section */ }
finally { mutex.ReleaseMutex(); }

// Instead of System.Threading.Semaphore:
var semaphore = new Temporalio.Workflows.Semaphore(3);
await semaphore.WaitAsync();
try { /* limited concurrency section */ }
finally { semaphore.Release(); }
```

## Continue-as-New

```csharp
[Workflow]
public class LongRunningWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(WorkflowState state)
    {
        while (true)
        {
            state = await ProcessNextBatch(state);

            if (state.IsComplete)
                return "done";

            if (Workflow.ContinueAsNewSuggested)
                throw Workflow.CreateContinueAsNewException(
                    (LongRunningWorkflow wf) => wf.RunAsync(state));
        }
    }
}
```

## Saga Pattern (Compensations)

**Important:** Compensation activities should be idempotent — they may be retried (as with ALL activities).

```csharp
[Workflow]
public class OrderSagaWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(Order order)
    {
        var compensations = new List<Func<Task>>();

        try
        {
            // IMPORTANT: Save compensation BEFORE calling the activity.
            // If activity fails after completing but before returning,
            // compensation must still be registered.
            compensations.Add(() => Workflow.ExecuteActivityAsync(
                (OrderActivities a) => a.ReleaseInventoryIfReservedAsync(order),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) }));
            await Workflow.ExecuteActivityAsync(
                (OrderActivities a) => a.ReserveInventoryAsync(order),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });

            compensations.Add(() => Workflow.ExecuteActivityAsync(
                (OrderActivities a) => a.RefundPaymentIfChargedAsync(order),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) }));
            await Workflow.ExecuteActivityAsync(
                (OrderActivities a) => a.ChargePaymentAsync(order),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });

            await Workflow.ExecuteActivityAsync(
                (OrderActivities a) => a.ShipOrderAsync(order),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });

            return "Order completed";
        }
        catch (Exception ex)
        {
            Workflow.Logger.LogError(ex, "Order failed, running compensations");
            compensations.Reverse();
            foreach (var compensate in compensations)
            {
                try { await compensate(); }
                catch (Exception compErr)
                {
                    Workflow.Logger.LogError(compErr, "Compensation failed");
                }
            }
            throw;
        }
    }
}
```

## Cancellation Handling (CancellationToken)

.NET uses standard `CancellationToken` for workflow cancellation.

```csharp
[Workflow]
public class CancellableWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        try
        {
            await Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.LongRunningAsync(),
                new() { StartToCloseTimeout = TimeSpan.FromHours(1) });
            return "completed";
        }
        catch (Exception e) when (TemporalException.IsCanceledException(e))
        {
            // The "when" clause above is because we only want to apply the logic to cancellation, but
            // this kind of cleanup could be done on any/all exceptions too.
            Workflow.Logger.LogError(e, "Cancellation occurred, performing cleanup");

            // Call cleanup activity. If this throws, it will swallow the original exception which we
            // are ok with here. This could be changed to just log a failure and let the original
            // cancellation continue.
            // The default token on Workflow.CancellationToken is now marked
            // cancelled, so we pass a different one. We use CancellationToken.None here because the
            // cleanup activity itself doesn't need to be cancellable; if it did (e.g. you want to
            // cancel cleanup from a timeout or another signal), create a new detached
            // CancellationTokenSource and pass its Token instead.
            await Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.MyCancellationCleanupActivity(),
                new()
                {
                    ScheduleToCloseTimeout = TimeSpan.FromMinutes(5),
                    CancellationToken = CancellationToken.None,
                });

            // Rethrow the cancellation
            throw;
        }
    }
}
```

## Wait Condition with Timeout

```csharp
[Workflow]
public class ApprovalWorkflow
{
    private bool _approved;

    [WorkflowSignal]
    public async Task ApproveAsync() => _approved = true;

    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        // Wait for approval with 24-hour timeout
        var gotApproval = await Workflow.WaitConditionAsync(
            () => _approved,
            TimeSpan.FromHours(24));

        return gotApproval ? "approved" : "auto-rejected due to timeout";
    }
}
```

## Waiting for All Handlers to Finish

Signal and update handlers should generally be non-async (avoid running activities from them). Otherwise, the workflow may complete before handlers finish their execution. However, making handlers non-async sometimes requires workarounds that add complexity.

When async handlers are necessary, use `WaitConditionAsync(AllHandlersFinished)` at the end of your workflow (or before continue-as-new) to prevent completion until all pending handlers complete.

```csharp
[Workflow]
public class HandlerAwareWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        // ... main workflow logic ...

        // Before exiting, wait for all handlers to finish
        await Workflow.WaitConditionAsync(() => Workflow.AllHandlersFinished);
        return "done";
    }
}
```

## Activity Heartbeat Details

### WHY:

- **Support activity cancellation** — Cancellations are delivered via heartbeat; activities that don't heartbeat won't know they've been cancelled
- **Resume progress after worker failure** — Heartbeat details persist across retries

### WHEN:

- **Cancellable activities** — Any activity that should respond to cancellation
- **Long-running activities** — Track progress for resumability
- **Checkpointing** — Save progress periodically

```csharp
[Activity]
public async Task<string> ProcessLargeFileAsync(string filePath)
{
    var info = ActivityExecutionContext.Current.Info;
    // Get heartbeat details from previous attempt (if any)
    var startLine = info.HeartbeatDetails.Count > 0
        ? await info.HeartbeatDetailAtAsync<int>(0)
        : 0;

    var lines = await File.ReadAllLinesAsync(filePath);
    for (var i = startLine; i < lines.Length; i++)
    {
        await ProcessLineAsync(lines[i]);

        // Heartbeat with progress
        // If cancelled, CancellationToken will be triggered
        ActivityExecutionContext.Current.Heartbeat(i + 1);
        ActivityExecutionContext.Current.CancellationToken.ThrowIfCancellationRequested();
    }

    return "completed";
}
```

## Timers

```csharp
[Workflow]
public class TimerWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        await Workflow.DelayAsync(TimeSpan.FromHours(1));
        return "Timer fired";
    }
}
```

## Local Activities

**Purpose**: Reduce latency for short, lightweight operations by skipping the task queue. ONLY use these when necessary for performance. Do NOT use these by default, as they are not durable and distributed.

```csharp
[Workflow]
public class LocalActivityWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        var result = await Workflow.ExecuteLocalActivityAsync(
            (MyActivities a) => a.QuickLookup("key"),
            new() { StartToCloseTimeout = TimeSpan.FromSeconds(5) });
        return result;
    }
}
```
