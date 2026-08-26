# .NET SDK Error Handling

## Overview

The .NET SDK uses `ApplicationFailureException` for application-specific errors and provides comprehensive retry policy configuration. Generally, the following information about errors and retryability applies across activities, child workflows and Nexus operations.

## Application Failures

```csharp
using Temporalio.Activities;
using Temporalio.Exceptions;

[Activity]
public async Task ValidateOrderAsync(Order order)
{
    if (!order.IsValid())
    {
        throw new ApplicationFailureException(
            "Invalid order",
            errorType: "ValidationError");
    }
}
```

## Non-Retryable Errors

```csharp
using Temporalio.Activities;
using Temporalio.Exceptions;

[Activity]
public async Task<string> ChargeCardAsync(ChargeCardInput input)
{
    if (!IsValidCard(input.CardNumber))
    {
        throw new ApplicationFailureException(
            "Permanent failure - invalid credit card",
            errorType: "PaymentError",
            nonRetryable: true); // Will not retry activity
    }
    return await ProcessPaymentAsync(input.CardNumber, input.Amount);
}
```

## Handling Activity Errors in Workflows

```csharp
using Temporalio.Workflows;
using Temporalio.Exceptions;

[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        try
        {
            return await Workflow.ExecuteActivityAsync(
                (MyActivities a) => a.RiskyActivityAsync(),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        }
        catch (ActivityFailureException ex) when (!TemporalException.IsCanceledException(ex))
        {
            Workflow.Logger.LogError(ex, "Activity failed");
            throw new ApplicationFailureException(
                "Workflow failed due to activity error");
        }
    }
}
```

## Retry Configuration

```csharp
using Temporalio.Common;
using Temporalio.Workflows;

[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        return await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.MyActivityAsync(),
            new()
            {
                StartToCloseTimeout = TimeSpan.FromMinutes(10),
                RetryPolicy = new()
                {
                    MaximumInterval = TimeSpan.FromMinutes(1),
                    MaximumAttempts = 5,
                    NonRetryableErrorTypes = new[] { "ValidationError", "PaymentError" },
                },
            });
    }
}
```

Only set options such as MaximumInterval, MaximumAttempts etc. if you have a domain-specific reason to.
If not, prefer to leave them at their defaults.

## Timeout Configuration

```csharp
[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        return await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.MyActivityAsync(),
            new()
            {
                StartToCloseTimeout = TimeSpan.FromMinutes(5),      // Single attempt
                ScheduleToCloseTimeout = TimeSpan.FromMinutes(30),  // Including retries
                HeartbeatTimeout = TimeSpan.FromMinutes(2),         // Between heartbeats
            });
    }
}
```

## Workflow Failure

**Critical .NET behavior:** Only `ApplicationFailureException` will fail a workflow. All other exceptions (including standard .NET exceptions like `NullReferenceException`, `KeyNotFoundException`, etc.) will **retry the workflow task** indefinitely. This is by design — those are treated as bugs to be fixed with a code deployment, not reasons for the workflow to fail.

```csharp
[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        if (someCondition)
        {
            throw new ApplicationFailureException(
                "Cannot process order",
                errorType: "BusinessError");
        }
        return "success";
    }
}
```

**Note:** Do not use `nonRetryable:` with `ApplicationFailureException` inside a workflow (as opposed to an activity).

## Best Practices

1. Use specific error types for different failure modes
2. Mark permanent failures as non-retryable in activities
3. Configure appropriate retry policies
4. Log errors before re-raising
5. Use `ActivityFailureException` to catch activity failures in workflows
6. Design code to be idempotent for safe retries (see more at `references/core/patterns.md`)
7. Only throw `ApplicationFailureException` from workflows to fail them — other exceptions will retry the workflow task
