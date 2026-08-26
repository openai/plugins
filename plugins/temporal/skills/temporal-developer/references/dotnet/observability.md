# .NET SDK Observability

## Overview

The .NET SDK provides observability through logging, metrics, and tracing using standard .NET patterns.

## Logging

### Workflow Logging (Replay-Safe)

Use `Workflow.Logger` for replay-safe logging that avoids duplicate messages:

```csharp
[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(string name)
    {
        Workflow.Logger.LogInformation("Workflow started for {Name}", name);

        var result = await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.MyActivityAsync(),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });

        Workflow.Logger.LogInformation("Activity completed with {Result}", result);
        return result;
    }
}
```

The workflow logger automatically:

- Suppresses duplicate logs during replay
- Includes workflow context (workflow ID, run ID, etc.)

### Activity Logging

Use `ActivityExecutionContext.Current.Logger` for context-aware activity logging:

```csharp
[Activity]
public async Task<string> ProcessOrderAsync(string orderId)
{
    var logger = ActivityExecutionContext.Current.Logger;
    logger.LogInformation("Processing order {OrderId}", orderId);

    // Perform work...

    logger.LogInformation("Order processed successfully");
    return "completed";
}
```

### Customizing Logger Configuration

```csharp
using Microsoft.Extensions.Logging;

var client = await TemporalClient.ConnectAsync(new("localhost:7233")
{
    LoggerFactory = LoggerFactory.Create(builder =>
        builder
            .AddSimpleConsole(options => options.TimestampFormat = "[HH:mm:ss] ")
            .SetMinimumLevel(LogLevel.Information)),
});
```

## Metrics

### Enabling SDK Metrics

Metrics are configured on `TemporalRuntime`. Create the runtime globally before any client/worker and set a Prometheus endpoint or custom metric meter.

```csharp
using Temporalio.Client;
using Temporalio.Runtime;

// Create runtime with Prometheus endpoint
var runtime = new TemporalRuntime(new()
{
    Telemetry = new() { Metrics = new() { Prometheus = new("0.0.0.0:9000") } },
});

// Use this runtime for all clients
var client = await TemporalClient.ConnectAsync(
    new("localhost:7233") { Runtime = runtime });
```

Alternatively, use `Temporalio.Extensions.DiagnosticSource` to bridge metrics to a .NET `System.Diagnostics.Metrics.Meter` for integration with OpenTelemetry or other .NET metrics pipelines.

### Key SDK Metrics

- `temporal_request` — Client requests to server
- `temporal_workflow_task_execution_latency` — Workflow task processing time
- `temporal_activity_execution_latency` — Activity execution time
- `temporal_workflow_task_replay_latency` — Replay duration

## Search Attributes (Visibility)

See the Search Attributes section of `references/dotnet/data-handling.md`

## Best Practices

1. Use `Workflow.Logger` in workflows, `ActivityExecutionContext.Current.Logger` in activities
2. Don't use `Console.WriteLine` in workflows — it will produce duplicate output on replay
3. Configure metrics for production monitoring
4. Use Search Attributes for business-level visibility
