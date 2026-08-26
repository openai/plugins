# Ruby SDK Patterns

## Signals

```ruby
class OrderWorkflow < Temporalio::Workflow::Definition
  def initialize
    @approved = false
    @items = []
  end

  workflow_signal
  def approve
    @approved = true
  end

  workflow_signal
  def add_item(item)
    @items << item
  end

  def execute
    Temporalio::Workflow.wait_condition { @approved }
    "Processed #{@items.length} items"
  end
end
```

### Dynamic Signal Handlers

For handling signals with names not known at compile time. Use cases for this pattern are rare — most workflows should use statically defined signal handlers.

```ruby
class DynamicSignalWorkflow < Temporalio::Workflow::Definition
  def initialize
    @signals = {}
  end

  workflow_signal dynamic: true, raw_args: true
  def dynamic_signal(signal_name, *args)
    @signals[signal_name] ||= []
    @signals[signal_name] << Temporalio::Workflow.payload_converter.from_payload(args.first)
  end
end
```

## Queries

**Important:** Queries must NOT modify workflow state or have side effects.

```ruby
class StatusWorkflow < Temporalio::Workflow::Definition
  def initialize
    @status = 'pending'
    @progress = 0
  end

  # Shorthand for simple attribute readers
  workflow_query_attr_reader :status, :progress

  def execute
    @status = 'running'
    100.times do |i|
      @progress = i
      Temporalio::Workflow.execute_activity(
        ProcessItem, i,
        start_to_close_timeout: 60
      )
    end
    @status = 'completed'
    'done'
  end
end
```

### Dynamic Query Handlers

For handling queries with names not known at compile time. Use cases for this pattern are rare — most workflows should use statically defined query handlers.

```ruby
workflow_query dynamic: true, raw_args: true
def dynamic_query(query_name, *args)
  if query_name == 'get_field'
    field_name = Temporalio::Workflow.payload_converter.from_payload(args.first)
    instance_variable_get(:"@#{field_name}")
  end
end
```

## Updates

```ruby
class OrderWorkflow < Temporalio::Workflow::Definition
  def initialize
    @items = []
  end

  workflow_update
  def add_item(item)
    @items << item
    @items.length # Returns new count to caller
  end

  workflow_update_validator(:add_item)
  def validate_add_item(item)
    raise 'Item cannot be empty' if item.nil? || item.empty?
    raise 'Order is full' if @items.length >= 100
  end
end
```

**Important:** Validators must NOT mutate workflow state or do anything blocking (no activities, sleeps, or other commands). They are read-only, similar to query handlers. Raise an exception to reject the update; return `nil` to accept.

## Child Workflows

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute(orders)
    results = []
    orders.each do |order|
      result = Temporalio::Workflow.execute_child_workflow(
        ProcessOrderWorkflow, order,
        id: "order-#{order.id}",
        parent_close_policy: Temporalio::Workflow::ParentClosePolicy::ABANDON
      )
      results << result
    end
    results
  end
end
```

### Child Workflow Options

```ruby
Temporalio::Workflow.execute_child_workflow(
  ChildWorkflow, arg,
  id: 'child-1',
  parent_close_policy: Temporalio::Workflow::ParentClosePolicy::ABANDON,
  cancellation_type: Temporalio::Workflow::ChildWorkflowCancellationType::WAIT_CANCELLATION_COMPLETED,
  execution_timeout: 3600,
  run_timeout: 1800
)
```

## Handles to External Workflows

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute(target_workflow_id)
    handle = Temporalio::Workflow.external_workflow_handle(target_workflow_id)

    # Signal the external workflow
    handle.signal(TargetWorkflow.data_ready, data_payload)

    # Or cancel it
    handle.cancel
  end
end
```

## Parallel Execution

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute(items)
    futures = items.map do |item|
      Temporalio::Workflow::Future.new do
        Temporalio::Workflow.execute_activity(
          ProcessItem, item,
          start_to_close_timeout: 300
        )
      end
    end
    Temporalio::Workflow::Future.all_of(*futures).wait
    results = futures.map(&:result)
    results
  end
end
```

## Continue-as-New

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute(state)
    loop do
      state = process_batch(state)

      return 'done' if state.complete?

      # Continue with fresh history before hitting limits
      if Temporalio::Workflow.continue_as_new_suggested
        raise Temporalio::Workflow::ContinueAsNewError.new(state)
      end
    end
  end
end
```

## Saga Pattern (Compensations)

**Important:** Compensation activities should be idempotent - they may be retried (as with ALL activities).

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute(order)
    compensations = []

    begin
      # Save compensation before running the activity, because:
      # 1. reserve_inventory starts running
      # 2. it successfully reserves inventory
      # 3. but then fails for some other reason (timeout, reporting metrics, etc.)
      # 4. the activity failed, but the effect (reserved inventory) already happened
      # So the compensation must handle both reserved and unreserved states.
      compensations << lambda { |cancellation|
        Temporalio::Workflow.execute_activity(
          ReleaseInventoryIfReserved, order,
          start_to_close_timeout: 300,
          cancellation: cancellation
        )
      }
      Temporalio::Workflow.execute_activity(
        ReserveInventory, order,
        start_to_close_timeout: 300
      )

      compensations << lambda { |cancellation|
        Temporalio::Workflow.execute_activity(
          RefundPaymentIfCharged, order,
          start_to_close_timeout: 300,
          cancellation: cancellation
        )
      }
      Temporalio::Workflow.execute_activity(
        ChargePayment, order,
        start_to_close_timeout: 300
      )

      Temporalio::Workflow.execute_activity(
        ShipOrder, order,
        start_to_close_timeout: 300
      )

      'Order completed'

    rescue => e
      Temporalio::Workflow.logger.error("Order failed: #{e}, running compensations")
      # Use a detached cancellation so compensations still run even if the workflow
      # was canceled (the workflow's own cancellation is already canceled by then).
      detached_cancel, = Temporalio::Cancellation.new
      compensations.reverse.each do |compensate|
        begin
          compensate.call(detached_cancel)
        rescue => comp_err
          Temporalio::Workflow.logger.error("Compensation failed: #{comp_err}")
        end
      end
      raise
    end
  end
end
```

## Cancellation (Token-based)

Ruby uses `Temporalio::Cancellation` tokens.

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    # The workflow's cancellation token
    workflow_cancel = Temporalio::Workflow.cancellation

    begin
      Temporalio::Workflow.execute_activity(
        LongRunningActivity,
        start_to_close_timeout: 3600,
        cancellation: workflow_cancel
      )
      'completed'
    ensure
      # Create a detached cancellation for cleanup
      # (not tied to workflow cancellation)
      cancel, _cancel_proc = Temporalio::Cancellation.new
      Temporalio::Workflow.execute_activity(
        CleanupActivity,
        start_to_close_timeout: 300,
        cancellation: cancel
      )
    end
  end
end
```

## Wait Condition with Timeout

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    @approved = false

    # Wait for approval with 24-hour timeout
    # Returns false on timeout (no exception raised)
    if Temporalio::Workflow.wait_condition(timeout: 86400) { @approved }
      'approved'
    else
      'auto-rejected due to timeout'
    end
  end
end
```

## Waiting for All Handlers to Finish

Signal and update handlers should generally be non-async (avoid running activities from them). Otherwise, the workflow may complete before handlers finish their execution. However, making handlers non-async sometimes requires workarounds that add complexity.

When async handlers are necessary, use `wait_condition { all_handlers_finished }` at the end of your workflow (or before continue-as-new) to prevent completion until all pending handlers complete.

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    # ... main workflow logic ...

    # Before exiting, wait for all handlers to finish
    Temporalio::Workflow.wait_condition { Temporalio::Workflow.all_handlers_finished? }
    'done'
  end
end
```

## Activity Heartbeat Details

### WHY:
- **Support activity cancellation** - Cancellations are delivered via heartbeat; activities that don't heartbeat won't know they've been cancelled
- **Resume progress after worker failure** - Heartbeat details persist across retries

### WHEN:
- **Cancellable activities** - Any activity that should respond to cancellation
- **Long-running activities** - Track progress for resumability
- **Checkpointing** - Save progress periodically

```ruby
class ProcessLargeFile < Temporalio::Activity::Definition
  def execute(file_path)
    context = Temporalio::Activity::Context.current

    # Get heartbeat details from previous attempt (if any)
    heartbeat_details = context.info.heartbeat_details
    start_line = heartbeat_details&.first || 0

    begin
      File.foreach(file_path).with_index do |line, i|
        next if i < start_line

        process_line(line)

        # Heartbeat with progress
        # If cancelled, heartbeat raises Temporalio::Error::CanceledError
        context.heartbeat(i + 1)
      end

      'completed'
    rescue Temporalio::Error::CanceledError
      cleanup
      raise
    end
  end
end
```

## Timers

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    Temporalio::Workflow.sleep(3600)

    'Timer fired'
  end
end
```

## Local Activities

**Purpose**: Reduce latency for short, lightweight operations by skipping the task queue. ONLY use these when necessary for performance. Do NOT use these by default, as they are not durable and distributed.

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    result = Temporalio::Workflow.execute_local_activity(
      QuickLookup, 'key',
      start_to_close_timeout: 5
    )
    result
  end
end
```

## Using ActiveModel

See `references/ruby/data-handling.md`.
