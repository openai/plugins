# .NET SDK Advanced Features

## Schedules

Create recurring workflow executions.

```csharp
using Temporalio.Client.Schedules;

var scheduleId = "daily-report";
await client.CreateScheduleAsync(
    scheduleId,
    new Schedule(
        Action: ScheduleActionStartWorkflow.Create(
            (DailyReportWorkflow wf) => wf.RunAsync(),
            new(id: "daily-report", taskQueue: "reports")),
        Spec: new ScheduleSpec
        {
            Intervals = new List<ScheduleIntervalSpec>
            {
                new(Every: TimeSpan.FromDays(1)),
            },
        }));

// Manage schedules
var handle = client.GetScheduleHandle(scheduleId);
await handle.PauseAsync("Maintenance window");
await handle.UnpauseAsync();
await handle.TriggerAsync(); // Run immediately
await handle.DeleteAsync();
```

## Async Activity Completion

For activities that complete asynchronously (e.g., human tasks, external callbacks).
If you configure a `HeartbeatTimeout` on this activity, the external completer is responsible for sending heartbeats via the async handle.
If you do NOT set a `HeartbeatTimeout`, no heartbeats are required.

**Note:** If the external system that completes the asynchronous action can reliably be trusted to do the task and Signal back with the result, and it doesn't need to Heartbeat or receive Cancellation, then consider using **signals** instead.

```csharp
using Temporalio.Activities;
using Temporalio.Client;

[Activity]
public async Task RequestApprovalAsync(string requestId)
{
    var taskToken = ActivityExecutionContext.Current.Info.TaskToken;

    // Store task token for later completion (e.g., in database)
    await StoreTaskTokenAsync(requestId, taskToken);

    // Mark this activity as waiting for external completion
    throw new CompleteAsyncException();
}

// Later, complete the activity from another process
public async Task CompleteApprovalAsync(string requestId, bool approved)
{
    var client = await TemporalClient.ConnectAsync(new("localhost:7233"));
    // Retrieve the task token from external storage (e.g., database)
    var taskToken = await GetTaskTokenAsync(requestId);

    var handle = client.GetAsyncActivityHandle(taskToken);

    // Optional: if a HeartbeatTimeout was set, you can periodically:
    // await handle.HeartbeatAsync(progressDetails);

    if (approved)
        await handle.CompleteAsync("approved");
    else
        // You can also fail or report cancellation via the handle
        await handle.FailAsync(new ApplicationFailureException("Rejected"));
}
```

## Worker Tuning

Configure worker performance settings.

```csharp
var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions("my-task-queue")
    {
        // Workflow task concurrency
        MaxConcurrentWorkflowTasks = 100,
        // Activity task concurrency
        MaxConcurrentActivities = 100,
        // Graceful shutdown timeout
        GracefulShutdownTimeout = TimeSpan.FromSeconds(30),
    }
    .AddWorkflow<MyWorkflow>()
    .AddAllActivities(new MyActivities()));
```

## Workflow Init Attribute

You should always put state initialization logic in the constructor of your workflow class, so that it happens before signals/updates arrive.

Normally, your constructor must have no arguments. However, if you add the `[WorkflowInit]` attribute, then your constructor instead receives the same workflow arguments that `[WorkflowRun]` receives:

```csharp
[Workflow]
public class MyWorkflow
{
    private readonly string _initialValue;
    private readonly List<string> _items = new();

    [WorkflowInit]
    public MyWorkflow(string initialValue)
    {
        _initialValue = initialValue;
    }

    [WorkflowRun]
    public async Task<string> RunAsync(string initialValue)
    {
        // _initialValue and _items are already initialized
        return _initialValue;
    }
}
```

Constructor (with `[WorkflowInit]`) and `[WorkflowRun]` method must have the same parameters with the same types. You cannot make blocking calls (activities, sleeps, etc.) from the constructor.

## Workflow Failure Exception Types

Control which exceptions cause workflow failures vs workflow task retries.

**Default behavior:** Only `ApplicationFailureException` fails a workflow. All other exceptions retry the workflow task forever (treated as bugs to fix with a code deployment).

**Tip for testing:** Set `WorkflowFailureExceptionTypes` to include `Exception` so any unhandled exception fails the workflow immediately rather than retrying the workflow task forever. This surfaces bugs faster.

### Worker-Level Configuration

```csharp
var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions("my-task-queue")
    {
        // These exception types will fail the workflow execution (not just the task)
        WorkflowFailureExceptionTypes = new[] { typeof(ArgumentException), typeof(InvalidOperationException) },
    }
    .AddWorkflow<MyWorkflow>()
    .AddAllActivities(new MyActivities()));
```

## Dependency Injection

The .NET SDK supports dependency injection via the `Temporalio.Extensions.Hosting` package, which integrates with .NET's generic host.

### Worker as Generic Host

```csharp
using Temporalio.Extensions.Hosting;

public class Program
{
    public static async Task Main(string[] args)
    {
        var host = Host.CreateDefaultBuilder(args)
            .ConfigureServices(ctx =>
                ctx.
                    AddScoped<IOrderRepository, OrderRepository>().
                    AddHostedTemporalWorker(
                        clientTargetHost: "localhost:7233",
                        clientNamespace: "default",
                        taskQueue: "my-task-queue").
                    AddScopedActivities<MyActivities>().
                    AddWorkflow<MyWorkflow>())
            .Build();
        await host.RunAsync();
    }
}
```

### Activity Dependency Injection

As shown in the host setup above, activities can be registered with `AddScopedActivities<T>()`, `AddSingletonActivities<T>()`, or `AddTransientActivities<T>()`. Activities registered this way are created via DI, allowing constructor injection:

```csharp
public class MyActivities
{
    private readonly ILogger<MyActivities> _logger;
    private readonly IOrderRepository _repository;

    public MyActivities(ILogger<MyActivities> logger, IOrderRepository repository)
    {
        _logger = logger;
        _repository = repository;
    }

    [Activity]
    public async Task<Order> GetOrderAsync(string orderId)
    {
        _logger.LogInformation("Fetching order {OrderId}", orderId);
        return await _repository.GetAsync(orderId);
    }
}
```

**Note:** Dependency injection is NOT available in workflows — workflows must be self-contained for determinism.
