# .NET SDK Versioning

For conceptual overview and guidance on choosing an approach, see `references/core/versioning.md`.

## Patching API

### The Patched() Method

The `Workflow.Patched()` method checks whether a Workflow should run new or old code:

```csharp
[Workflow]
public class ShippingWorkflow
{
    [WorkflowRun]
    public async Task RunAsync()
    {
        if (Workflow.Patched("send-email-instead-of-fax"))
        {
            // New code path
            await Workflow.ExecuteActivityAsync(
                (ShippingActivities a) => a.SendEmailAsync(),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        }
        else
        {
            // Old code path (for replay of existing workflows)
            await Workflow.ExecuteActivityAsync(
                (ShippingActivities a) => a.SendFaxAsync(),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
        }
    }
}
```

**How it works:**

- For new executions: `Patched()` returns `true` and records a marker in the Workflow history
- For replay with the marker: `Patched()` returns `true` (history includes this patch)
- For replay without the marker: `Patched()` returns `false` (history predates this patch)

### Three-Step Patching Process

**Warning:** Failing to follow this process correctly will result in non-determinism errors for in-flight workflows.

**Step 1: Patch in New Code**

```csharp
[Workflow]
public class OrderWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(Order order)
    {
        if (Workflow.Patched("add-fraud-check"))
        {
            await Workflow.ExecuteActivityAsync(
                (OrderActivities a) => a.CheckFraudAsync(order),
                new() { StartToCloseTimeout = TimeSpan.FromMinutes(2) });
        }

        return await Workflow.ExecuteActivityAsync(
            (OrderActivities a) => a.ProcessPaymentAsync(order),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
    }
}
```

**Step 2: Deprecate the Patch**

Once all pre-patch Workflow Executions have completed:

```csharp
[Workflow]
public class OrderWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(Order order)
    {
        Workflow.DeprecatePatch("add-fraud-check");

        await Workflow.ExecuteActivityAsync(
            (OrderActivities a) => a.CheckFraudAsync(order),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(2) });

        return await Workflow.ExecuteActivityAsync(
            (OrderActivities a) => a.ProcessPaymentAsync(order),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
    }
}
```

**Step 3: Remove the Patch**

After all workflows with the deprecated patch marker have completed, remove the `DeprecatePatch()` call entirely:

```csharp
[Workflow]
public class OrderWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(Order order)
    {
        await Workflow.ExecuteActivityAsync(
            (OrderActivities a) => a.CheckFraudAsync(order),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(2) });

        return await Workflow.ExecuteActivityAsync(
            (OrderActivities a) => a.ProcessPaymentAsync(order),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
    }
}
```

### Query Filters for Finding Workflows by Version

Use List Filters to find workflows with specific patch versions:

```bash
# Find running workflows with a specific patch
temporal workflow list --query \
  'WorkflowType = "OrderWorkflow" AND ExecutionStatus = "Running" AND TemporalChangeVersion = "add-fraud-check"'

# Find running workflows without any patch (pre-patch versions)
temporal workflow list --query \
  'WorkflowType = "OrderWorkflow" AND ExecutionStatus = "Running" AND TemporalChangeVersion IS NULL'
```

## Workflow Type Versioning

For incompatible changes, create a new Workflow Type instead of using patches:

```csharp
[Workflow("PizzaWorkflow")]
public class PizzaWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(PizzaOrder order)
    {
        return await ProcessOrderV1Async(order);
    }
}

[Workflow("PizzaWorkflowV2")]
public class PizzaWorkflowV2
{
    [WorkflowRun]
    public async Task<string> RunAsync(PizzaOrder order)
    {
        return await ProcessOrderV2Async(order);
    }
}
```

Register both with the Worker:

```csharp
var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions("pizza-task-queue")
        .AddWorkflow<PizzaWorkflow>()
        .AddWorkflow<PizzaWorkflowV2>()
        .AddAllActivities(new PizzaActivities()));
```

Update client code to start new workflows with the new type:

```csharp
// Old workflows continue on PizzaWorkflow
// New workflows use PizzaWorkflowV2
var handle = await client.StartWorkflowAsync(
    (PizzaWorkflowV2 wf) => wf.RunAsync(order),
    new(id: $"pizza-{order.Id}", taskQueue: "pizza-task-queue"));
```

Check for open executions before removing the old type:

```bash
temporal workflow list --query 'WorkflowType = "PizzaWorkflow" AND ExecutionStatus = "Running"'
```

## Worker Versioning

Worker Versioning manages versions at the deployment level, allowing multiple Worker versions to run simultaneously.

### Key Concepts

**Worker Deployment**: A logical service grouping similar Workers together (e.g., "loan-processor"). All versions of your code live under this umbrella.

**Worker Deployment Version**: A specific snapshot of your code identified by a deployment name and Build ID (e.g., "loan-processor:v1.0" or "loan-processor:abc123").

### Configuring Workers for Versioning

```csharp
using Temporalio.Worker;

var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions("my-task-queue")
    {
        DeploymentOptions = new WorkerDeploymentOptions(
            DeploymentName: "my-service",
            BuildId: Environment.GetEnvironmentVariable("BUILD_ID") ?? "dev"),
        UseWorkerVersioning = true,
    }
    .AddWorkflow<MyWorkflow>()
    .AddAllActivities(new MyActivities()));
```

**Configuration parameters:**

- `UseWorkerVersioning`: Enables Worker Versioning
- `DeploymentOptions`: Identifies the Worker Deployment Version (deployment name + build ID)
- Build ID: Typically a git commit hash, version number, or timestamp

### PINNED vs AUTO_UPGRADE Behaviors

**PINNED Behavior**

Workflows stay locked to their original Worker version:

```csharp
[Workflow(VersioningBehavior = VersioningBehavior.Pinned)]
public class StableWorkflow { /* ... */ }
```

**When to use PINNED:**

- Short-running workflows (minutes to hours)
- Consistency is critical (e.g., financial transactions)
- You want to eliminate version compatibility complexity
- Building new applications and want simplest development experience

**AUTO_UPGRADE Behavior**

Workflows can move to newer versions:

```csharp
[Workflow(VersioningBehavior = VersioningBehavior.AutoUpgrade)]
public class UpgradableWorkflow { /* ... */ }
```

**When to use AUTO_UPGRADE:**

- Long-running workflows (weeks or months)
- Workflows need to benefit from bug fixes during execution
- Migrating from traditional rolling deployments
- You are already using patching APIs for version transitions

**Important:** AUTO_UPGRADE workflows still need patching to handle version transitions safely since they can move between Worker versions.

### Worker Configuration with Default Behavior

```csharp
var worker = new TemporalWorker(
    client,
    new TemporalWorkerOptions("my-task-queue")
    {
        DeploymentOptions = new WorkerDeploymentOptions(
            DeploymentName: "order-service",
            BuildId: Environment.GetEnvironmentVariable("BUILD_ID") ?? "dev")
        {
            DefaultVersioningBehavior = VersioningBehavior.Pinned,
        },
        UseWorkerVersioning = true,
    }
    .AddWorkflow<OrderWorkflow>()
    .AddAllActivities(new OrderActivities()));
```

### Deployment Strategies

**Blue-Green Deployments**

Maintain two environments and switch traffic between them:

1. Deploy new code to idle environment
2. Run tests and validation
3. Switch traffic to new environment
4. Keep old environment for instant rollback

**Rainbow Deployments**

Multiple versions run simultaneously:

- New workflows use latest version
- Existing workflows complete on their original version
- Add new versions alongside existing ones
- Gradually sunset old versions as workflows complete

### Querying Workflows by Worker Version

```bash
# Find workflows on a specific Worker version
temporal workflow list --query \
  'TemporalWorkerDeploymentVersion = "my-service:v1.0.0" AND ExecutionStatus = "Running"'
```

## Upgrading on Continue-as-New

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For long-running Pinned Workflows that use Continue-as-New, detect a new Target Worker Deployment Version on `Workflow.TargetWorkerDeploymentVersionChanged` and continue-as-new with `InitialVersioningBehavior.AutoUpgrade` so the new run starts on the Target Version. See `references/core/versioning.md` for the conceptual model.

### Detecting the Target Version change

`Workflow.TargetWorkerDeploymentVersionChanged` is `true` when a new Current or Ramping Version is available for this Workflow's Worker Deployment.  The flag is refreshed after each Workflow Task completes.

Check the flag from code that runs as part of a Workflow Task — for example, before accepting an Update, starting an Activity, or starting a child Workflow.

### Continue-as-new with upgrade

When the flag is set, throw the exception from `Workflow.CreateContinueAsNewException`, passing a `ContinueAsNewOptions` whose `InitialVersioningBehavior` is `AutoUpgrade`, so the new run starts on the Target Version of its Worker Deployment.

```csharp
using Temporalio.Common;
using Temporalio.Workflows;

// At a natural Workflow Task boundary, e.g. before accepting Updates,
// starting Activities, starting child Workflows, etc.:
if (Workflow.TargetWorkerDeploymentVersionChanged)
{
    throw Workflow.CreateContinueAsNewException(
        (MyWorkflow wf) => wf.RunAsync(nextInput),
        new ContinueAsNewOptions
        {
            InitialVersioningBehavior = InitialVersioningBehavior.AutoUpgrade,
        });
}
```

> [!IMPORTANT]
> Don't busy-poll the flag on a timer. Check it at a natural Workflow Task boundary — before accepting Updates, starting Activities, starting child Workflows, etc. For idle Workflows, send a Signal to wake them so they can check it (see Limitations).

### Limitations

- **Lazy moving only — idle Workflows do not upgrade.** Send a Signal to wake an idle Workflow so it can check `TargetWorkerDeploymentVersionChanged`.
- **Workflow input must remain compatible across versions.** The new version's Workflow definition must accept the previous version's input; otherwise the new run may fail on its first Workflow Task.
- **Pinned Workflow Types only.** Auto-Upgrade Workflows move at Workflow Task boundaries already; the upgrade-on-CaN pattern adds nothing for them.

## Best Practices

1. **Check for open executions** before removing old code paths
2. **Use descriptive patch IDs** that explain the change (e.g., "add-fraud-check" not "patch-1")
3. **Deploy patches incrementally**: patch, deprecate, remove
4. **Use PINNED for short workflows** to simplify version management
5. **Use AUTO_UPGRADE with patching** for long-running workflows that need updates
6. **Generate Build IDs from code** (git hash) to ensure changes produce new versions
7. **Avoid rolling deployments** for high-availability services with long-running workflows
