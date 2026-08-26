# Ruby SDK Versioning

For conceptual overview, see `references/core/versioning.md`.

## Patching API

### The patched() Method

`Temporalio::Workflow.patched('my-patch')` returns `true`/`false` to branch between new and old code paths:

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    if Temporalio::Workflow.patched('my-patch')
      # New code path
      Temporalio::Workflow.execute_activity(
        PostPatchActivity,
        start_to_close_timeout: 100
      )
    else
      # Old code path (for replay of existing workflows)
      Temporalio::Workflow.execute_activity(
        PrePatchActivity,
        start_to_close_timeout: 100
      )
    end
  end
end
```

**How it works:**
- For new executions: `patched()` returns `true` and records a marker in the Workflow history
- For replay with the marker: `patched()` returns `true` (history includes this patch)
- For replay without the marker: `patched()` returns `false` (history predates this patch)

**Note:** The `patched()` return value is memoized per patch ID. This means you cannot reliably use `patched()` in loops—it will return the same value every iteration. Workaround: append a sequence number to the patch ID for each iteration (e.g., `"my-change-#{i}"`).

### Three-Step Patching Process

**Warning:** Failing to follow this process correctly will result in non-determinism errors for in-flight workflows.

**Step 1: Patch in New Code**

Add the patch with both old and new code paths:

```ruby
class OrderWorkflow < Temporalio::Workflow::Definition
  def execute(order)
    if Temporalio::Workflow.patched('add-fraud-check')
      # New: Run fraud check before payment
      Temporalio::Workflow.execute_activity(
        CheckFraudActivity,
        order,
        start_to_close_timeout: 120
      )
    end

    # Original payment logic runs for both paths
    Temporalio::Workflow.execute_activity(
      ProcessPaymentActivity,
      order,
      start_to_close_timeout: 300
    )
  end
end
```

**Step 2: Deprecate the Patch**

Once all pre-patch Workflow Executions have completed, remove the old code and use `deprecate_patch()`:

```ruby
class OrderWorkflow < Temporalio::Workflow::Definition
  def execute(order)
    Temporalio::Workflow.deprecate_patch('add-fraud-check')

    # Only new code remains
    Temporalio::Workflow.execute_activity(
      CheckFraudActivity,
      order,
      start_to_close_timeout: 120
    )

    Temporalio::Workflow.execute_activity(
      ProcessPaymentActivity,
      order,
      start_to_close_timeout: 300
    )
  end
end
```

**Step 3: Remove the Patch**

After all workflows with the deprecated patch marker have completed, remove the `deprecate_patch()` call entirely:

```ruby
class OrderWorkflow < Temporalio::Workflow::Definition
  def execute(order)
    Temporalio::Workflow.execute_activity(
      CheckFraudActivity,
      order,
      start_to_close_timeout: 120
    )

    Temporalio::Workflow.execute_activity(
      ProcessPaymentActivity,
      order,
      start_to_close_timeout: 300
    )
  end
end
```

### Query Filters for Finding Workflows by Version

```bash
# Find running workflows with a specific patch
temporal workflow list --query \
  'WorkflowType = "OrderWorkflow" AND ExecutionStatus = "Running" AND TemporalChangeVersion = "add-fraud-check"'

# Find running workflows without any patch (pre-patch versions)
temporal workflow list --query \
  'WorkflowType = "OrderWorkflow" AND ExecutionStatus = "Running" AND TemporalChangeVersion IS NULL'
```

## Workflow Type Versioning

For incompatible changes, create a new Workflow Type by duplicating the class:

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    # Original implementation
    Temporalio::Workflow.execute_activity(
      OriginalActivity,
      start_to_close_timeout: 100
    )
  end
end

class MyWorkflowV2 < Temporalio::Workflow::Definition
  def execute
    # New implementation with incompatible changes
    Temporalio::Workflow.execute_activity(
      NewActivity,
      start_to_close_timeout: 100
    )
  end
end
```

Register both with the Worker:

```ruby
worker = Temporalio::Worker.new(
  client: client,
  task_queue: 'my-task-queue',
  workflows: [MyWorkflow, MyWorkflowV2],
  activities: [OriginalActivity, NewActivity]
)
```

Update client code to start new workflows with the new type:

```ruby
# Old workflows continue on MyWorkflow
# New workflows use MyWorkflowV2
handle = client.start_workflow(
  MyWorkflowV2,
  input,
  id: SecureRandom.uuid,
  task_queue: 'my-task-queue'
)
```

Check for open executions before removing the old type:

```bash
temporal workflow list --query 'WorkflowType = "MyWorkflow" AND ExecutionStatus = "Running"'
```

## Worker Versioning

Worker Versioning manages versions at the deployment level, allowing multiple Worker versions to run simultaneously. Requires Ruby SDK v0.5.0+.

### Key Concepts

**Worker Deployment**: A logical service grouping similar Workers together (e.g., "order-processor"). All versions of your code live under this umbrella.

**Worker Deployment Version**: A specific snapshot of your code identified by a deployment name and Build ID (e.g., "order-processor:v1.0" or "order-processor:abc123").

### Configuring Workers for Versioning

```ruby
worker = Temporalio::Worker.new(
  client: client,
  task_queue: 'my-task-queue',
  workflows: [MyWorkflow],
  activities: [MyActivity],
  deployment_options: Temporalio::Worker::DeploymentOptions.new(
    version: Temporalio::WorkerDeploymentVersion.new(
      deployment_name: 'my-service',
      build_id: 'v1.0.0' # or git commit hash
    ),
    use_worker_versioning: true
  )
)
```

### PINNED vs AUTO_UPGRADE Behaviors

**PINNED Behavior**

Workflows stay locked to their original Worker version. Set on the workflow definition:

```ruby
class StableWorkflow < Temporalio::Workflow::Definition
  workflow_versioning_behavior :pinned

  def execute
    Temporalio::Workflow.execute_activity(
      ProcessOrderActivity,
      start_to_close_timeout: 300
    )
  end
end
```

**When to use PINNED:**
- Short-running workflows (minutes to hours)
- Consistency is critical (e.g., financial transactions)
- You want to eliminate version compatibility complexity
- Building new applications and want simplest development experience

**AUTO_UPGRADE Behavior**

Workflows can move to newer versions:

```ruby
class LongRunningWorkflow < Temporalio::Workflow::Definition
  workflow_versioning_behavior :auto_upgrade

  def execute
    # This workflow may be picked up by a newer Worker version
    Temporalio::Workflow.execute_activity(
      ProcessActivity,
      start_to_close_timeout: 300
    )
  end
end
```

**When to use AUTO_UPGRADE:**
- Long-running workflows (weeks or months)
- Workflows need to benefit from bug fixes during execution
- Migrating from traditional rolling deployments
- You are already using patching APIs for version transitions

**Important:** AUTO_UPGRADE workflows still need patching to handle version transitions safely since they can move between Worker versions.

### Worker Configuration with Default Behavior

```ruby
worker = Temporalio::Worker.new(
  client: client,
  task_queue: 'orders-task-queue',
  workflows: [OrderWorkflow],
  activities: [ProcessOrderActivity],
  deployment_options: Temporalio::Worker::DeploymentOptions.new(
    version: Temporalio::WorkerDeploymentVersion.new(
      deployment_name: 'order-service',
      build_id: ENV.fetch('BUILD_ID')
    ),
    use_worker_versioning: true,
    default_versioning_behavior: Temporalio::VersioningBehavior::PINNED
  )
)
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

This works well with Kubernetes where you manage multiple ReplicaSets running different Worker versions.

### Querying Workflows by Worker Version

```bash
# Find workflows on a specific Worker version
temporal workflow list --query \
  'TemporalWorkerDeploymentVersion = "my-service:v1.0.0" AND ExecutionStatus = "Running"'
```

## Best Practices

1. **Check for open executions** before removing old code paths
2. **Use descriptive patch IDs** that explain the change (e.g., "add-fraud-check" not "patch-1")
3. **Deploy patches incrementally**: patch, deprecate, remove
4. **Use PINNED for short workflows** to simplify version management
5. **Use AUTO_UPGRADE with patching** for long-running workflows that need updates
6. **Generate Build IDs from code** (git hash) to ensure changes produce new versions
7. **Avoid rolling deployments** for high-availability services with long-running workflows
