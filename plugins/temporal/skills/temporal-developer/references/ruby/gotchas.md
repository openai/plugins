# Ruby Gotchas

Ruby-specific mistakes and anti-patterns. See also [Common Gotchas](references/core/gotchas.md) for language-agnostic concepts.

## File Organization

Unlike Python, Ruby doesn't reload workflow files (no sandbox). Still best practice to separate workflows and activities for clarity and maintainability.

```ruby
# BAD - Everything in one file
# app.rb
class MyWorkflow < Temporalio::Workflow::Definition
  def execute(name)
    Temporalio::Workflow.execute_activity(
      MyActivity,
      name,
      start_to_close_timeout: 30
    )
  end
end

class MyActivity < Temporalio::Activity::Definition
  def execute(name)
    # Heavy I/O, external calls, etc.
  end
end
```

```ruby
# GOOD - Separate files
# workflows/my_workflow.rb
require 'temporalio/workflow'

class MyWorkflow < Temporalio::Workflow::Definition
  def execute(name)
    Temporalio::Workflow.execute_activity(
      MyActivity,
      name,
      start_to_close_timeout: 30
    )
  end
end

# activities/my_activity.rb
require 'temporalio/activity'

class MyActivity < Temporalio::Activity::Definition
  def execute(name)
    # Heavy I/O, external calls, etc.
  end
end

# worker.rb
require_relative 'workflows/my_workflow'
require_relative 'activities/my_activity'
```

## Wrong Retry Classification

Transient network errors should be retried. Authentication errors should not be. See `references/ruby/error-handling.md` to understand how to classify errors with `non_retryable: true` and `non_retryable_error_types`.

## Heartbeating

### Forgetting to Heartbeat Long Activities

```ruby
# BAD - No heartbeat, can't detect stuck activities
class ProcessLargeFile < Temporalio::Activity::Definition
  def execute(path)
    File.foreach(path).each_slice(1000) do |chunk|
      process(chunk)  # Takes hours, no heartbeat
    end
  end
end
```

```ruby
# GOOD - Regular heartbeats with progress
class ProcessLargeFile < Temporalio::Activity::Definition
  def execute(path)
    File.foreach(path).each_slice(1000).with_index do |chunk, i|
      Temporalio::Activity::Context.current.heartbeat("Processing chunk #{i}")
      process(chunk)
    end
  end
end
```

### Heartbeat Timeout Too Short

```ruby
# BAD - Heartbeat timeout shorter than processing time between heartbeats
Temporalio::Workflow.execute_activity(
  ProcessChunk,
  start_to_close_timeout: 1800,
  heartbeat_timeout: 10  # Too short!
)

# GOOD - Heartbeat timeout allows for processing variance
Temporalio::Workflow.execute_activity(
  ProcessChunk,
  start_to_close_timeout: 1800,
  heartbeat_timeout: 120
)
```

Set heartbeat timeout as high as acceptable for your use case -- each heartbeat counts as an action.

## Cancellation

### Not Handling Workflow Cancellation

```ruby
# BAD - Cleanup doesn't run on cancellation
class BadWorkflow < Temporalio::Workflow::Definition
  def execute
    Temporalio::Workflow.execute_activity(AcquireResource, start_to_close_timeout: 300)
    Temporalio::Workflow.execute_activity(DoWork, start_to_close_timeout: 300)
    Temporalio::Workflow.execute_activity(ReleaseResource, start_to_close_timeout: 300)  # Never runs if cancelled!
  end
end
```

```ruby
# GOOD - Use ensure with detached cancellation for cleanup
class GoodWorkflow < Temporalio::Workflow::Definition
  def execute
    Temporalio::Workflow.execute_activity(AcquireResource, start_to_close_timeout: 300)
    Temporalio::Workflow.execute_activity(DoWork, start_to_close_timeout: 300)
  ensure
    # Create a detached cancellation (not tied to workflow cancellation)
    # so cleanup activity runs even after workflow is cancelled
    detached_cancel, _cancel_proc = Temporalio::Cancellation.new
    Temporalio::Workflow.execute_activity(
      ReleaseResource,
      start_to_close_timeout: 300,
      cancellation: detached_cancel
    )
  end
end
```

### Not Handling Activity Cancellation

Activities must **opt in** to receive cancellation. This requires:

1. **Heartbeating** -- cancellation is delivered via the heartbeat response
2. **Catching the cancellation exception** -- `Temporalio::Error::CancelledError` is raised when a heartbeat detects cancellation

```ruby
# BAD - Activity ignores cancellation
class LongActivity < Temporalio::Activity::Definition
  def execute
    do_expensive_work  # Runs to completion even if cancelled
  end
end
```

```ruby
# GOOD - Heartbeat and handle cancellation
class LongActivity < Temporalio::Activity::Definition
  def execute
    items.each do |item|
      Temporalio::Activity::Context.current.heartbeat
      process(item)
    end
  rescue Temporalio::Error::CancelledError
    cleanup
    raise
  end
end
```

## Testing

### Not Testing Failures

Make sure workflows work as expected under failure paths, not just happy paths. See `references/ruby/testing.md` for more info.

### Not Testing Replay

Replay tests help you detect hidden sources of non-determinism in your workflow code and should be considered in addition to standard testing. See `references/ruby/testing.md` for more info.

## Timers and Sleep

### Using Kernel.sleep

```ruby
# BAD - Kernel.sleep raises NondeterminismError
class BadWorkflow < Temporalio::Workflow::Definition
  def execute
    sleep(60)          # NondeterminismError!
    Kernel.sleep(60)   # NondeterminismError!
  end
end
```

```ruby
# GOOD - Use Temporalio::Workflow.sleep for durable timers
class GoodWorkflow < Temporalio::Workflow::Definition
  def execute
    Temporalio::Workflow.sleep(60)  # Deterministic, durable timer
  end
end
```

**Why this matters:** `Kernel.sleep` uses the system clock, which differs between original execution and replay. `Temporalio::Workflow.sleep` creates a durable timer in the event history, ensuring consistent behavior during replay.

## Illegal Call Tracing Gotchas

### Third-Party Gems Triggering NondeterminismError

The Ruby SDK uses `TracePoint`-based illegal call tracing on the workflow fiber. Any gem that internally uses `Thread`, `IO`, `Socket`, `Net::HTTP`, or other forbidden operations will trigger `NondeterminismError` -- even if the call is deep in the gem's internals.

```ruby
# BAD - Logging gem that uses Thread internally
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    SomeFancyLogger.info("Starting workflow")  # NondeterminismError if gem uses Thread.new!
  end
end
```

### Fix: Disable Illegal Call Tracing for Specific Code

```ruby
# Wrap non-deterministic but safe code
Temporalio::Workflow::Unsafe.illegal_call_tracing_disabled do
  # Code here won't trigger NondeterminismError
  SomeFancyLogger.info("Starting workflow")
end
```

For code that performs IO that you know is safe and want to allow:

```ruby
# Disable the durable scheduler for IO operations
Temporalio::Workflow::Unsafe.durable_scheduler_disabled do
  # IO operations allowed here
end
```

### Side Effects and Replay Safety

Always check replaying status before performing side effects in workflows:

```ruby
unless Temporalio::Workflow::Unsafe.replaying?
  # Only runs during original execution, not replay
  Temporalio::Workflow.logger.info("Processing started")
end
```
