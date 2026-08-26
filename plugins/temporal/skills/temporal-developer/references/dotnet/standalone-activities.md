> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

## Overview

Standalone Activities are Activities run independently of any Workflow, started directly from a Temporal Client — useful when you need a single durable, retryable task (job-queue style) and not multi-step orchestration. The same Activity method can be executed both as a Standalone Activity and as a Workflow Activity with no code changes.

Standalone Activities are conceptually the same across all SDKs. Read the [cross-SDK concept file](references/core/standalone-activities.md) if you have not already, and then see below for the .NET SDK specific APIs for calling Standalone Activities.

## Prerequisites

- Temporal .NET SDK v1.12.0 or higher.
- Temporal CLI v1.7.0 or higher — see [Temporal CLI install instructions](references/core/install_cli.md) if needed. Dev server includes Standalone Activities support.
- For production, Temporal Server v1.31.0 or higher (or Temporal Cloud).

## Hosting Activities on a Worker

The Activity is defined just as activities normally are in Temporal. Worker registration is also the same.

```csharp
using Microsoft.Extensions.Logging;
using Temporalio.Client;
using Temporalio.Common.EnvConfig;
using Temporalio.Worker;
using TemporalioSamples.StandaloneActivity;

var connectOptions = ClientEnvConfig.LoadClientConnectOptions();
connectOptions.TargetHost ??= "localhost:7233";
connectOptions.LoggerFactory = LoggerFactory.Create(builder =>
    builder.
        AddSimpleConsole(options => options.TimestampFormat = "[HH:mm:ss] ").
        SetMinimumLevel(LogLevel.Information));
var client = await TemporalClient.ConnectAsync(connectOptions);

const string taskQueue = "standalone-activity-sample";

using var tokenSource = new CancellationTokenSource();
Console.CancelKeyPress += (_, eventArgs) =>
{
    tokenSource.Cancel();
    eventArgs.Cancel = true;
};

using var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions(taskQueue).
        AddActivity(MyActivities.ComposeGreetingAsync)); // register whatever your activity(ies) is/are

await worker.ExecuteAsync(tokenSource.Token);
```

## Calling and managing Standalone Activities

Start and manage Standalone Activities from your application code using the Temporal Client.

### Do not call from inside a Workflow

Don't call `client.ExecuteActivityAsync` / `client.StartActivityAsync` or any other Standalone Activity APIs from inside a Workflow Definition — use Workflow-side activity invocation (`Workflow.ExecuteActivityAsync`) instead.

### Connect a Client

The Standalone Activity operations are methods on a connected `TemporalClient`. The examples below assume this `client`.

```csharp
using Temporalio.Client;
using Temporalio.Common.EnvConfig;

var connectOptions = ClientEnvConfig.LoadClientConnectOptions();
connectOptions.TargetHost ??= "localhost:7233";
var client = await TemporalClient.ConnectAsync(connectOptions);
```

### Execute (wait for result)

Use `client.ExecuteActivityAsync(...)` to durably enqueue the Activity, wait for it to run on a Worker, and return the result. The activity options require `Id`, `TaskQueue`, and at least one of `ScheduleToCloseTimeout` or `StartToCloseTimeout`.

#### With type checking

Use when activity definitions are available in this language. Pass a lambda invoking the activity method:

```csharp
// In practice, use a meaningful business identifier, like customer or transaction identifier
var activityId = Guid.NewGuid().ToString();

var result = await client.ExecuteActivityAsync(
    () => MyActivities.ComposeGreetingAsync(new ComposeGreetingInput("Hello", "World")),
    new(activityId, "standalone-activity-sample")
    {
        ScheduleToCloseTimeout = TimeSpan.FromSeconds(10),
    });
```

#### Without type checking

Use when activity definitions are unavailable in this language (i.e. you can't import them). Pass the activity type name as a string and an argument array:

```csharp
var result = await client.ExecuteActivityAsync<string>(
    "ComposeGreeting",
    new object?[] { new ComposeGreetingInput("Hello", "World") },
    new(activityId, "standalone-activity-sample")
    {
        ScheduleToCloseTimeout = TimeSpan.FromSeconds(10),
    });
```

### Start (do not wait for result)

Use `client.StartActivityAsync(...)` to durably enqueue the Activity and get back a handle without waiting for completion. This takes the **exact same arguments as `ExecuteActivityAsync`**.

```csharp
var handle = await client.StartActivityAsync(...);
```

### Get a handle to an existing Activity execution

Use `client.GetActivityHandle(...)` to attach a handle to a previously started Standalone Activity. Passing `null` as the run ID (the default) targets the latest run of that Activity ID.

```csharp
// Without a known result type
var handle = client.GetActivityHandle("my-activity-id", runId: "the-run-id");

// With a known result type
var typedHandle = client.GetActivityHandle<string>("my-activity-id", runId: "the-run-id");
```

### Wait for the result of a handle

```csharp
var result = await handle.GetResultAsync();
```

Calling `ExecuteActivityAsync` is equivalent to `StartActivityAsync` followed by `await handle.GetResultAsync()`.

### List Standalone Activities

```csharp
await foreach (var info in client.ListActivitiesAsync(
    "TaskQueue = 'standalone-activity-sample'")) // returns an IAsyncEnumerable<ActivityExecution>
{
    Console.WriteLine(
        $"ActivityID: {info.ActivityId}, Type: {info.ActivityType}, Status: {info.Status}");
}
```

Only Standalone Activity Executions are returned; Activities running inside Workflows are not included.

### Count Standalone Activities

Use `client.CountActivitiesAsync(query)` to count matching executions; this takes the **exact same arguments as `ListActivitiesAsync`**.

```csharp
var resp = await client.CountActivitiesAsync(
    "TaskQueue = 'standalone-activity-sample'");
Console.WriteLine($"Total activities: {resp.Count}");
```
