# Ruby SDK Advanced Features

## Schedules

Create recurring workflow executions with `Temporalio::Client::Schedule`.

```ruby
require 'temporalio/client'

# Create a schedule
schedule_id = 'daily-report'
client.create_schedule(
  schedule_id,
  Temporalio::Client::Schedule.new(
    action: Temporalio::Client::Schedule::Action::StartWorkflow.new(
      DailyReportWorkflow,
      id: 'daily-report',
      task_queue: 'reports'
    ),
    spec: Temporalio::Client::Schedule::Spec.new(
      intervals: [
        Temporalio::Client::Schedule::Spec::Interval.new(every: 86_400) # 1 day in seconds
      ]
    )
  )
)

# Manage schedules
handle = client.schedule_handle(schedule_id)
handle.pause(note: 'Maintenance window')
handle.unpause
handle.trigger
handle.delete
```

## Async Activity Completion

For activities that complete asynchronously (e.g., human tasks, external callbacks).

**Note:** If the external system that completes the asynchronous action can reliably be trusted to do the task and Signal back with the result, and it doesn't need to Heartbeat or receive Cancellation, then consider using **signals** instead.

```ruby
class RequestApproval < Temporalio::Activity::Definition
  def execute(request_id)
    # Get task token for async completion
    task_token = Temporalio::Activity::Context.current.info.task_token

    # Store task token for later completion (e.g., in database)
    store_task_token(request_id, task_token)

    # Signal that this activity completes asynchronously
    Temporalio::Activity::Context.current.raise_complete_async
  end
end

# Later, complete the activity from another process
client = Temporalio::Client.connect('localhost:7233')
task_token = get_task_token(request_id)
handle = client.async_activity_handle(task_token: task_token)

if approved
  handle.complete('approved')
else
  handle.fail(Temporalio::Error::ApplicationError.new('Rejected'))
end
```

If you configure a `heartbeat_timeout:` on the activity, the external completer is responsible for sending heartbeats via the async handle. If you do NOT set a `heartbeat_timeout`, no heartbeats are required.

## Worker Tuning

Configure worker performance settings.

```ruby
worker = Temporalio::Worker.new(
  client: client,
  task_queue: 'my-queue',
  workflows: [MyWorkflow],
  activities: [MyActivity],
  # Max concurrent execution slots (default 100 each): how many workflow tasks
  # and activities run at once on this worker.
  tuner: Temporalio::Worker::Tuner.create_fixed(
    workflow_slots: 100,
    activity_slots: 100
  ),
  # Grace period (seconds) after shutdown is requested before in-progress
  # activities are canceled. Defaults to 0 (cancel immediately on shutdown).
  graceful_shutdown_period: 30
)
worker.run
```

On shutdown the worker stops polling for new tasks and cancels the `worker_shutdown_cancellation` on each running activity's context. After `graceful_shutdown_period` seconds it then issues actual cancellation to any still-running activities. The worker will not finish shutting down until all in-progress activities complete, so activities that ignore cancellation can block shutdown indefinitely.

## Workflow Init Decorator

Always initialize workflow state before signals/updates arrive. Signal and Update handlers can run *before* the main `execute` method -- for example with Signal-with-Start, when the Task Queue is backlogged, or right after continue-as-new -- so a handler may otherwise read uninitialized instance variables.

Normally `initialize` must accept no required arguments. If you place the `workflow_init` class method directly above `initialize`, the constructor receives the same workflow arguments that `execute` receives (the same input the Client sent). It is guaranteed to run before any handler.

```ruby
class GreetingWorkflow < Temporalio::Workflow::Definition
  workflow_init
  def initialize(input)
    # Runs before any signal/update handler
    @name_with_title = "Sir #{input['name']}"
    @title_has_been_checked = false
  end

  def execute(input)
    Temporalio::Workflow.wait_condition { @title_has_been_checked }
    "Hello, #{@name_with_title}"
  end

  workflow_update
  def check_title_validity
    # Guaranteed to see workflow input, since initialize ran first
    valid = Temporalio::Workflow.execute_activity(
      CheckTitleValidityActivity,
      @name_with_title,
      start_to_close_timeout: 100
    )
    @title_has_been_checked = true
    valid
  end
end
```

`initialize` (with `workflow_init`) and `execute` must have the same parameters with the same types. You cannot make blocking calls (activities, sleeps, etc.) from `initialize`.

## Workflow Failure Exception Types

Control which exceptions cause workflow failure vs workflow task failure (which Temporal retries automatically).

### Per-Workflow Configuration

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  # Class method approach
  def self.workflow_failure_exception_type
    MyCustomError
  end

  def execute
    raise MyCustomError, 'This fails the workflow, not just the task'
  end
end
```

### Worker-Level Configuration

```ruby
Temporalio::Worker.new(
  client: client,
  task_queue: 'my-queue',
  workflows: [MyWorkflow],
  workflow_failure_exception_types: [MyCustomError]
)
```

**Tips:**
- Set to `[Exception]` in tests so any unhandled exception fails the workflow immediately rather than retrying the workflow task forever. Surfaces bugs faster.
- Include `Temporalio::Workflow::NondeterminismError` to fail the workflow instead of leaving it in a retrying state on non-determinism errors.

## Activity Concurrency and Executors

Ruby uses `Temporalio::Worker::ActivityExecutor::ThreadPool` by default. Activities run in a thread pool.

```ruby
# Default: activities run in thread pool
worker = Temporalio::Worker.new(
  client: client,
  task_queue: 'my-queue',
  workflows: [MyWorkflow],
  activities: [MyActivity],
  activity_executors: {
    default: Temporalio::Worker::ActivityExecutor::ThreadPool.new(max_threads: 20)
  }
)
```

Fiber-based execution is also possible for IO-bound activities using Ruby's fiber scheduler.

## Rails Integration

### ActiveRecord Considerations

Never pass ActiveRecord models directly to Temporal workflows or activities. Serialize to plain data structures.

```ruby
# BAD - Passing AR model
client.execute_workflow(
  ProcessOrderWorkflow,
  Order.find(42),  # Don't pass AR objects!
  id: 'order-42',
  task_queue: 'orders'
)

# GOOD - Pass serializable data
client.execute_workflow(
  ProcessOrderWorkflow,
  { id: 42, total: order.total, status: order.status },
  id: 'order-42',
  task_queue: 'orders'
)
```

### Zeitwerk and Autoloading

Rails autoloading can result in unexpected I/O during replay. `config.eager_load` must be enabled or Workflows must explicitly require code dependencies before they are executed. Usually the easiest place to do that is when starting the worker, and requiring all activities and workflows that the worker needs *before* starting the worker. For example:

```ruby
require "temporal_client"
require "temporalio/worker"
require "workflows/shopping_cart_activities.rb"
require "workflows/shopping_cart_workflow.rb"

worker = Temporalio::Worker.new(
  client: TemporalClient.instance,
  task_queue: TemporalClient.task_queue,
  activities: [
    Workflows::ShoppingCartActivities::FetchProducts,
    ...
  ],
  workflows: [ Workflows::ShoppingCartWorkflow ]
)
worker.run
```

### Forking Considerations

If using a forking server (Puma, Unicorn), workers must be created **after** the fork. Connections established before fork are not safe to share across processes.

```ruby
# In Puma config (puma.rb)
before_worker_boot do
  # Create Temporal client and worker AFTER fork
  client = Temporalio::Client.connect('localhost:7233')
  worker = Temporalio::Worker.new(
    client: client,
    task_queue: 'my-queue',
    workflows: [MyWorkflow],
    activities: [MyActivity]
  )
  Thread.new { worker.run }
end
```
