# Temporal .NET SDK Reference

## Overview

The Temporal .NET SDK provides a high-performance, type-safe approach to building durable workflows using C# and .NET. Workflows use attributes (`[Workflow]`, `[WorkflowRun]`) and lambda expressions for type-safe invocations. Supports .NET Framework 4.6.2+ and .NET Core 3.1+ (including .NET 5+).

**CRITICAL**: The .NET SDK has **no sandbox**. Developers must be careful to avoid non-deterministic code in workflows. See the Determinism Rules section below and `references/dotnet/determinism.md`.

## Understanding Replay

Temporal workflows are durable through history replay. For details on how this works, see `references/core/determinism.md`.

## Quick Start

**Add Dependency:** Install the Temporal SDK NuGet package:

```bash
dotnet add package Temporalio
```

**Activities.cs** - Activity definitions (separate file for clarity):

```csharp
using Temporalio.Activities;

public class MyActivities
{
    [Activity]
    public string Greet(string name)
    {
        return $"Hello, {name}!";
    }
}
```

**GreetingWorkflow.workflow.cs** - Workflow definition:

```csharp
using Temporalio.Workflows;

[Workflow]
public class GreetingWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(string name)
    {
        return await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.Greet(name),
            new() { StartToCloseTimeout = TimeSpan.FromSeconds(30) });
    }
}
```

**Worker (Program.cs)** - Worker setup (registers activity and workflow, runs indefinitely and processes tasks):

```csharp
using Temporalio.Client;
using Temporalio.Common.EnvConfig;
using Temporalio.Worker;

var connectOptions = ClientEnvConfig.LoadClientConnectOptions();
connectOptions.TargetHost ??= "localhost:7233";
var client = await TemporalClient.ConnectAsync(connectOptions);

using var tokenSource = new CancellationTokenSource();
Console.CancelKeyPress += (_, eventArgs) =>
{
    tokenSource.Cancel();
    eventArgs.Cancel = true;
};

using var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions("my-task-queue")
        .AddWorkflow<GreetingWorkflow>()
        .AddAllActivities(new MyActivities()));

await worker.ExecuteAsync(tokenSource.Token);
```

**Start the dev server:** Start `temporal server start-dev` in the background.

**Start the worker:** Run `dotnet run` in the worker project.

**Starter (Program.cs)** - Start a workflow execution:

```csharp
using Temporalio.Client;
using Temporalio.Common.EnvConfig;

var connectOptions = ClientEnvConfig.LoadClientConnectOptions();
connectOptions.TargetHost ??= "localhost:7233";
var client = await TemporalClient.ConnectAsync(connectOptions);

var result = await client.ExecuteWorkflowAsync(
    (GreetingWorkflow wf) => wf.RunAsync("my name"),
    new(id: $"greeting-{Guid.NewGuid()}", taskQueue: "my-task-queue"));

Console.WriteLine($"Result: {result}");
```

**Run the workflow:** Run `dotnet run` in the starter project. Should output: `Result: Hello, my name!`.

## Key Concepts

### Workflow Definition

- Use `[Workflow]` attribute on class
- Put any state initialization logic in the constructor of your workflow class to guarantee that it happens before signals/updates arrive. If your state initialization logic requires the workflow parameters, then add the `[WorkflowInit]` attribute and parameters to your constructor.
- Use `[WorkflowRun]` on the async entry point method
- Must return `Task` or `Task<T>`
- Use `[WorkflowSignal]`, `[WorkflowQuery]`, `[WorkflowUpdate]` for handlers

### Activity Definition

- Use `[Activity]` attribute on methods
- Can be sync or async
- Instance methods support dependency injection
- Static methods are also supported

### Worker Setup

- Load connection settings with `ClientEnvConfig.LoadClientConnectOptions()`, connect the client, and create `TemporalWorker` with workflows and activities
- Use `AddWorkflow<T>()` and `AddAllActivities(instance)` or `AddActivity(method)`

### Determinism

**Workflow code must be deterministic!** The .NET SDK has no sandbox. See the Determinism Rules section below and `references/core/determinism.md` and `references/dotnet/determinism.md`.

## File Organization Best Practice

**Keep Workflow definitions in separate files from Activity definitions.** While not as critical as Python (no sandbox reloading), separation improves clarity and testability. Use the `.workflow.cs` extension for workflow files so the `.editorconfig` overrides (see below) apply only to workflow code.

```
MyTemporalApp/
├── Workflows/
│   └── GreetingWorkflow.workflow.cs  # Only Workflow classes
├── Activities/
│   └── TranslateActivities.cs       # Only Activity classes
├── Models/
│   └── OrderInput.cs                # Shared data models
├── Worker/
│   └── Program.cs                   # Worker setup
└── Starter/
    └── Program.cs                   # Client code to start workflows
```

## Workflow .editorconfig

Workflow code violates some standard .NET analyzer rules. The recommended approach is to use the `.workflow.cs` file extension for workflow files and scope the overrides to that extension:

```ini
# Configuration specific for Temporal workflows
[*.workflow.cs]

# We use getters for queries, they cannot be properties
dotnet_diagnostic.CA1024.severity = none

# Don't force workflows to have static methods
dotnet_diagnostic.CA1822.severity = none

# Do not need ConfigureAwait for workflows
dotnet_diagnostic.CA2007.severity = none

# Do not need task scheduler for workflows
dotnet_diagnostic.CA2008.severity = none

# Workflow randomness is intentionally deterministic
dotnet_diagnostic.CA5394.severity = none

# Allow async methods to not have await in them
dotnet_diagnostic.CS1998.severity = none

# Don't force workflows to call async methods
dotnet_diagnostic.VSTHRD103.severity = none

# Don't avoid, but rather encourage things using TaskScheduler.Current in workflows
dotnet_diagnostic.VSTHRD105.severity = none
```

## Determinism Rules

The .NET SDK has **no sandbox** like Python or TypeScript. Developers must avoid non-deterministic operations manually. Many standard .NET `Task` APIs use `TaskScheduler.Default` implicitly, which breaks determinism.

See `references/dotnet/determinism.md` for the full list of forbidden operations, safe alternatives, and best practices. See `references/dotnet/determinism-protection.md` for details on the runtime detection mechanism.

## Common Pitfalls

1. **Using `Task.Run` in workflows** — Uses default scheduler, breaks determinism. Use `Workflow.RunTaskAsync`.
2. **Using `Task.Delay` in workflows** — Uses system timer. Use `Workflow.DelayAsync`.
3. **`ConfigureAwait(false)` in workflows** — Leaves the deterministic scheduler. Never use in workflows.
4. **Non-`ApplicationFailureException` in workflows** — Other exceptions retry the workflow task forever instead of failing the workflow.
5. **Dictionary iteration in workflows** — `Dictionary<TKey, TValue>` has no guaranteed order. Use `SortedDictionary`.
6. **Forgetting to heartbeat** — Long-running activities need `ActivityExecutionContext.Current.Heartbeat()` calls.
7. **Using `CancellationTokenSource.CancelAsync`** — Use `CancellationTokenSource.Cancel` instead.
8. **Logging with `Console.WriteLine` in workflows** — Use `Workflow.Logger` for replay-safe logging.

## Writing Tests

See `references/dotnet/testing.md` for info on writing tests.

## Additional Resources

### Reference Files

- **`references/dotnet/patterns.md`** — Signals, queries, child workflows, saga pattern, etc.
- **`references/dotnet/determinism.md`** — Essentials of determinism in .NET
- **`references/dotnet/gotchas.md`** — .NET-specific mistakes and anti-patterns
- **`references/dotnet/error-handling.md`** — ApplicationFailureException, retry policies, non-retryable errors
- **`references/dotnet/observability.md`** — Logging, metrics, tracing
- **`references/dotnet/testing.md`** — WorkflowEnvironment, time-skipping, activity mocking
- **`references/dotnet/advanced-features.md`** — Schedules, worker tuning, dependency injection
- **`references/dotnet/data-handling.md`** — Data converters, payload encryption, etc.
- **`references/dotnet/versioning.md`** — Patching API, workflow type versioning, Worker Versioning
- **`references/dotnet/standalone-activities.md`** — Standalone Activities: run an Activity directly from a Client without a Workflow (Public Preview). Concept overview at `references/core/standalone-activities.md`.
- **`references/dotnet/determinism-protection.md`** — Runtime task detection, .NET Task determinism rules
