# .NET SDK Testing

## Overview

You test Temporal .NET Workflows using the `Temporalio.Testing` namespace plus a normal .NET test framework. The .NET SDK is compatible with any testing framework; most samples use xUnit. The SDK provides `WorkflowEnvironment` for testing workflows in a local environment and `ActivityEnvironment` for isolated activity testing.

## Test Environment Setup

The core pattern is:

1. Start a `WorkflowEnvironment` (`WorkflowEnvironment.StartLocalAsync()`).
2. Create a `TemporalWorker` in that environment with your Workflow and Activities registered.
3. Use the environment's client to execute the Workflow, using a fresh GUID for the task queue name and workflow ID.
4. Assert on the result or status.

```csharp
using Temporalio.Testing;
using Temporalio.Worker;

[Fact]
public async Task TestWorkflow()
{
    await using var env = await WorkflowEnvironment.StartLocalAsync();

    using var worker = new TemporalWorker(
        env.Client,
        new TemporalWorkerOptions($"task-queue-{Guid.NewGuid()}")
            .AddWorkflow<MyWorkflow>()
            .AddAllActivities(new MyActivities()));

    await worker.ExecuteAsync(async () =>
    {
        var result = await env.Client.ExecuteWorkflowAsync(
            (MyWorkflow wf) => wf.RunAsync("input"),
            new(id: $"wf-{Guid.NewGuid()}", taskQueue: worker.Options.TaskQueue!));
        Assert.Equal("expected", result);
    });
}
```

Conveniently, the local `env` can be shared among tests, e.g. via a fixture class.

If your workflows / tests involve long durations (such as using Temporal timers / sleeps), then you can use the time-skipping environment, via `WorkflowEnvironment.StartTimeSkippingAsync()`. Only use time-skipping if you must. It is not thread safe and cannot be shared among tests.

## Activity Mocking

The .NET SDK provides a straightforward way to mock Activities. Create a mock function with the `[Activity]` attribute and specify the name of the original Activity you want to mock:

```csharp
[Fact]
public async Task TestWithMockActivity()
{
    await using var env = await WorkflowEnvironment.StartLocalAsync();

    [Activity("MyActivity")]
    static Task<string> MockMyActivity(string input) =>
        Task.FromResult($"mocked: {input}");

    using var worker = new TemporalWorker(
        env.Client,
        new TemporalWorkerOptions($"task-queue-{Guid.NewGuid()}")
            .AddWorkflow<MyWorkflow>()
            .AddActivity(MockMyActivity));

    await worker.ExecuteAsync(async () =>
    {
        var result = await env.Client.ExecuteWorkflowAsync(
            (MyWorkflow wf) => wf.RunAsync("test"),
            new(id: $"wf-{Guid.NewGuid()}", taskQueue: worker.Options.TaskQueue!));
        Assert.Equal("mocked: test", result);
    });
}
```

**Note:** If the original activity method name ends with `Async` and returns a `Task`, the default activity name has `Async` trimmed off. For example, `MyActivityAsync` has default name `MyActivity`.

## Testing Signals and Queries

```csharp
[Fact]
public async Task TestSignalsAndQueries()
{
    await using var env = await WorkflowEnvironment.StartLocalAsync();

    using var worker = new TemporalWorker(/* ... */);

    await worker.ExecuteAsync(async () =>
    {
        var handle = await env.Client.StartWorkflowAsync(
            (MyWorkflow wf) => wf.RunAsync(),
            new(id: $"wf-{Guid.NewGuid()}", taskQueue: worker.Options.TaskQueue!));

        // Send signal
        await handle.SignalAsync(wf => wf.MySignalAsync("data"));

        // Query state
        var status = await handle.QueryAsync(wf => wf.GetStatus());
        Assert.Equal("expected", status);

        // Wait for completion
        var result = await handle.GetResultAsync();
    });
}
```

## Testing Failure Cases

```csharp
[Fact]
public async Task TestActivityFailureHandling()
{
    await using var env = await WorkflowEnvironment.StartLocalAsync();

    [Activity("RiskyActivity")]
    static Task<string> MockFailingActivity() =>
        throw new ApplicationFailureException("Simulated failure", nonRetryable: true);

    using var worker = new TemporalWorker(/* ... with mock activity */);

    await worker.ExecuteAsync(async () =>
    {
        var ex = await Assert.ThrowsAsync<WorkflowFailedException>(() =>
            env.Client.ExecuteWorkflowAsync(
                (MyWorkflow wf) => wf.RunAsync(),
                new(id: $"wf-{Guid.NewGuid()}", taskQueue: worker.Options.TaskQueue!)));
    });
}
```

## Replay Testing

```csharp
using Temporalio.Worker;

[Fact]
public async Task TestReplay()
{
    var historyJson = await File.ReadAllTextAsync("example-history.json");
    var replayer = new WorkflowReplayer(
        new WorkflowReplayerOptions()
            .AddWorkflow<MyWorkflow>());

    await replayer.ReplayWorkflowAsync(
        WorkflowHistory.FromJson("my-workflow-id", historyJson));
}
```

## Activity Testing

```csharp
using Temporalio.Testing;

[Fact]
public async Task TestActivity()
{
    var env = new ActivityEnvironment();
    var activities = new MyActivities();
    var result = await env.RunAsync(() => activities.MyActivity("arg1"));
    Assert.Equal("expected", result);
}
```

The `ActivityEnvironment` provides:

- `Info` — Activity info, defaulted to basic values
- `CancellationTokenSource` — Token source for issuing cancellation
- `Heartbeater` — Callback invoked each heartbeat
- `Logger` — Activity logger

## Best Practices

1. Use the `WorkflowEnvironment.StartLocalAsync` environment for most testing
2. Use time-skipping environment for workflows with durable timers / durable sleeps
3. Mock external dependencies in activities
4. Test replay compatibility, especially when changing workflow code
5. Test signal/query handlers explicitly
6. Use unique workflow IDs and task queues per test to avoid conflicts — `Guid.NewGuid()` is easiest
