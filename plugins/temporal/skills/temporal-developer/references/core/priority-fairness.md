# Task Queue Priority and Fairness

## Overview

Priority and Fairness control how Tasks are distributed within a Task Queue. Priority determines execution order. Fairness prevents one group of Tasks from starving others. They can be used independently or together.

Both features are in Public Preview. Priority is free. Fairness is a paid feature in Temporal Cloud.

## Priority

Priority lets you control execution order within a single Task Queue by assigning a priority key (integer 1-5, lower = higher priority). Each priority level acts as a sub-queue. All priority-1 Tasks dispatch before priority-2, and so on. Tasks at the same priority level dispatch in FIFO order.

Default priority is 3. Activities inherit their parent workflow's priority unless explicitly overridden.

### When to use Priority

Use Priority to differentiate execution order between types of work sharing a single Task Queue and Worker pool. For example, process payment-related Tasks before less time-sensitive inventory management Tasks, or ensure real-time Tasks run ahead of batch Tasks. You can also use it to run urgent Tasks immediately by assigning them priority 1.

### CLI

```
temporal workflow start \
  --type ChargeCustomer \
  --task-queue my-task-queue \
  --workflow-id my-workflow-id \
  --input '{"customerId":"12345"}' \
  --priority-key 1
```

### Go

```go
workflowOptions := client.StartWorkflowOptions{
  ID:        "my-workflow-id",
  TaskQueue: "my-task-queue",
  Priority:  temporal.Priority{PriorityKey: 1},
}
we, err := c.ExecuteWorkflow(context.Background(), workflowOptions, MyWorkflow)
```

### Java

```java
WorkflowOptions options = WorkflowOptions.newBuilder()
  .setTaskQueue("my-task-queue")
  .setPriority(Priority.newBuilder().setPriorityKey(1).build())
  .build();
```

### Python

```python
await client.start_workflow(
  MyWorkflow.run,
  args="hello",
  id="my-workflow-id",
  task_queue="my-task-queue",
  priority=Priority(priority_key=1),
)
```

### TypeScript

```ts
const handle = await startWorkflow(workflows.myWorkflow, {
  args: [false, 1],
  priority: { priorityKey: 1 },
});
```

### .NET

```csharp
var handle = await Client.StartWorkflowAsync(
  (MyWorkflow wf) => wf.RunAsync("hello"),
  new StartWorkflowOptions(id: "my-workflow-id", taskQueue: "my-task-queue")
  {
    Priority = new Priority(1),
  }
);
```

## Fairness

Fairness prevents one group of Tasks from monopolizing Worker capacity. Each fairness key creates a "virtual queue" within the Task Queue. The server uses round-robin dispatch across virtual queues so no single key can block others, even with a much larger backlog.

### When to use Fairness

Fairness solves the multi-tenant starvation problem. Without it, Tasks dispatch FIFO: if tenant-big enqueues 100k Tasks, tenant-small's 10 Tasks sit behind the entire backlog. With Fairness, each tenant gets its own virtual queue and Tasks are interleaved.

Common scenarios:

- **Multi-tenant applications** where large tenants should not block small ones.
- **Tiered capacity bands** where you want weighted distribution (e.g., 80% premium, 20% free) without limiting overall throughput when one band is empty.
- **Batch jobs** where some jobs run far more frequently than others.
- **Multi-vendor processing** where a few vendors generate the majority of work.

If all your Tasks can be dispatched immediately (no backlog), you don't need Fairness.

Fairness applies at Task dispatch time and considers each Task as having equal cost until dispatch. It does not account for Tasks currently being processed by Workers. So if you look at Tasks being processed by Workers, you might not see "fairness" across tenants — for example, if tenant-big already has Tasks being processed when tenant-small's Tasks are dispatched, it may still appear that tenant-big is using the most resources.

### Fairness keys and weights

A fairness key is a string, typically a tenant ID or workload category. Each unique key creates a virtual queue.

A fairness weight (float, default 1.0) controls how often a key's Tasks are dispatched relative to others. A key with weight 2.0 dispatches twice as often as keys with weight 1.0.

Example with three tiers:

| Fairness Key   | Weight | Share of Dispatches |
|----------------|--------|---------------------|
| premium-tier   | 5.0    | 50%                 |
| basic-tier     | 3.0    | 30%                 |
| free-tier      | 2.0    | 20%                 |

Tasks without a fairness key are grouped under an implicit empty-string key with weight 1.0. Adoption is incremental: unkeyed Tasks participate in round-robin alongside keyed Tasks.

### Using Fairness with Priority

When combined, Priority determines which sub-queue Tasks go into (priority 1 before 2, etc.), and Fairness applies within each priority level.

### SDK examples

#### CLI

```
temporal workflow start \
  --type ChargeCustomer \
  --task-queue my-task-queue \
  --workflow-id my-workflow-id \
  --input '{"customerId":"12345"}' \
  --priority-key 1 \
  --fairness-key tenant-123 \
  --fairness-weight 2.0
```

#### Go

```go
workflowOptions := client.StartWorkflowOptions{
  ID:        "my-workflow-id",
  TaskQueue: "my-task-queue",
  Priority: temporal.Priority{
    PriorityKey:    1,
    FairnessKey:    "tenant-123",
    FairnessWeight: 2.0,
  },
}
we, err := c.ExecuteWorkflow(context.Background(), workflowOptions, MyWorkflow)
```

Activities:

```go
ao := workflow.ActivityOptions{
  StartToCloseTimeout: time.Minute,
  Priority: temporal.Priority{
    PriorityKey:    1,
    FairnessKey:    "tenant-123",
    FairnessWeight: 2.0,
  },
}
ctx := workflow.WithActivityOptions(ctx, ao)
err := workflow.ExecuteActivity(ctx, MyActivity).Get(ctx, nil)
```

#### Java

```java
WorkflowOptions options = WorkflowOptions.newBuilder()
  .setTaskQueue("my-task-queue")
  .setPriority(Priority.newBuilder()
    .setPriorityKey(1)
    .setFairnessKey("tenant-123")
    .setFairnessWeight(2.0)
    .build())
  .build();
```

#### Python

```python
await client.start_workflow(
  MyWorkflow.run,
  args="hello",
  id="my-workflow-id",
  task_queue="my-task-queue",
  priority=Priority(priority_key=1, fairness_key="tenant-123", fairness_weight=2.0),
)
```

Activities:

```python
await workflow.execute_activity(
  say_hello,
  "hi",
  priority=Priority(priority_key=1, fairness_key="tenant-123", fairness_weight=2.0),
  start_to_close_timeout=timedelta(seconds=5),
)
```

#### TypeScript

```ts
const handle = await startWorkflow(workflows.myWorkflow, {
  args: [false, 1],
  priority: { priorityKey: 1, fairnessKey: 'tenant-123', fairnessWeight: 2.0 },
});
```

#### .NET

```csharp
var handle = await Client.StartWorkflowAsync(
  (MyWorkflow wf) => wf.RunAsync("hello"),
  new StartWorkflowOptions(id: "my-workflow-id", taskQueue: "my-task-queue")
  {
    Priority = new Priority(
      priorityKey: 1,
      fairnessKey: "tenant-123",
      fairnessWeight: 2.0
    )
  }
);
```

#### Child Workflows

Child workflows can set their own priority and fairness, overriding the parent.

Go:

```go
cwo := workflow.ChildWorkflowOptions{
  WorkflowID: "child-workflow-id",
  TaskQueue:  "child-task-queue",
  Priority: temporal.Priority{
    PriorityKey:    1,
    FairnessKey:    "tenant-123",
    FairnessWeight: 2.0,
  },
}
ctx := workflow.WithChildOptions(ctx, cwo)
err := workflow.ExecuteChildWorkflow(ctx, MyChildWorkflow).Get(ctx, nil)
```

Java:

```java
ChildWorkflowOptions childOptions = ChildWorkflowOptions.newBuilder()
  .setTaskQueue("child-task-queue")
  .setWorkflowId("child-workflow-id")
  .setPriority(Priority.newBuilder()
    .setPriorityKey(1)
    .setFairnessKey("tenant-123")
    .setFairnessWeight(2.0)
    .build())
  .build();
MyChildWorkflow child = Workflow.newChildWorkflowStub(MyChildWorkflow.class, childOptions);
child.run();
```

Python:

```python
await workflow.execute_child_workflow(
  MyChildWorkflow.run,
  args="hello child",
  priority=Priority(priority_key=1, fairness_key="tenant-123", fairness_weight=2.0),
)
```

TypeScript:

```ts
const handle = await startChildWorkflow(workflows.myChildWorkflow, {
  args: [false, 1],
  priority: { priorityKey: 1, fairnessKey: 'tenant-123', fairnessWeight: 2.0 },
});
```

.NET:

```csharp
await Workflow.ExecuteChildWorkflowAsync(
  (MyChildWorkflow wf) => wf.RunAsync("hello child"),
  new() {
    Priority = new(
      priorityKey: 1,
      fairnessKey: "tenant-123",
      fairnessWeight: 2.0
    )
  }
);
```

### Rate limiting

Two rate-limiting controls work alongside Fairness:

- **`queue-rps-limit`** — overall dispatch rate for the entire Task Queue.
- **`fairness-key-rps-limit-default`** — per-key rate limit, scaled by weight. If the default is 10 rps and a key has weight 2.5, that key's effective limit is 25 rps.

```
temporal task-queue config set \
    --task-queue my-task-queue \
    --task-queue-type activity \
    --namespace my-namespace \
    --queue-rps-limit 500 \
    --queue-rps-limit-reason "overall limit" \
    --fairness-key-rps-limit-default 33.3 \
    --fairness-key-rps-limit-reason "per-key limit"
```

If both limits are set, the more restrictive one applies.

### Fairness weight overrides

You can override the weights of up to 1000 keys through the config API. When an override is set for a key, the SDK-supplied weight is ignored. Overrides are per Task Queue and type (workflow vs. activity), so set them for both if needed.

### Enabling Fairness

When you start using fairness keys, it switches your active Task Queues to fairness mode. Existing queued Tasks are processed before any new fairness-mode ones.

**Temporal Cloud**: automatically enabled when you start using fairness keys.

**Self-hosted**: set these dynamic config flags to `true`:

- `matching.useNewMatcher`
- `matching.enableFairness`
- `matching.enableMigration` (to drain existing backlogs after enabling)

### Limitations

- Accuracy can degrade with a very large number of distinct fairness keys.
- Task Queue partitioning can interfere with fairness distribution. Contact Temporal Support to set a Task Queue to a single partition if needed.
- Weights apply at schedule time, not dispatch time. Changing a weight does not reorder already-backlogged Tasks.
- Fairness is not guaranteed across different Worker versions when using Worker Versioning.
- After server restarts, less-active keys may briefly dispatch new Tasks ahead of their existing backlog until ordering normalizes.
