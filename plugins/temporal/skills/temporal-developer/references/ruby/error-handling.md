# Ruby SDK Error Handling

## Overview

Application errors use `Temporalio::Error::ApplicationError`. Retry behavior is configured via `Temporalio::RetryPolicy`.

## Application Errors

```ruby
raise Temporalio::Error::ApplicationError.new('message', type: 'ErrorType')
```

In activities, any Ruby exception is automatically converted to an `ApplicationError`.

## Non-Retryable Errors

```ruby
raise Temporalio::Error::ApplicationError.new(
  'message',
  non_retryable: true
)
```

Override the retry interval with `next_retry_delay:`:

```ruby
raise Temporalio::Error::ApplicationError.new(
  'message',
  next_retry_delay: 30
)
```

## Handling Activity Errors

```ruby
begin
  Temporalio::Workflow.execute_activity(MyActivity, 'arg', start_to_close_timeout: 10)
rescue Temporalio::Error::ActivityError => e
  # Let cancellation propagate so the workflow is canceled, not failed.
  # Temporalio::Error.canceled? is true for a CanceledError, or an
  # ActivityError/ChildWorkflowError whose cause is a CanceledError.
  raise if Temporalio::Error.canceled?(e)

  Temporalio::Workflow.logger.error("Activity failed: #{e.message}")
  # Deliberately fail the workflow. Only raising an ApplicationError fails a
  # workflow; other exceptions only fail/retry the workflow task.
  raise Temporalio::Error::ApplicationError.new('Workflow failed due to activity error')
end
```

## Retry Policy Configuration

```ruby
retry_policy: Temporalio::RetryPolicy.new(
  max_interval: 60,
  max_attempts: 5,
  non_retryable_error_types: ['ValidationError']
)
```

Only set retry policies when you have a domain-specific reason. Prefer the defaults otherwise.

## Timeout Configuration

```ruby
Temporalio::Workflow.execute_activity(
  MyActivity,
  'arg',
  start_to_close_timeout: 30,
  schedule_to_close_timeout: 300,
  heartbeat_timeout: 10
)
```

All timeout values are in seconds (numeric).

## Workflow Failure

Only `Temporalio::Error::ApplicationError` causes a workflow failure. Other exceptions cause a workflow task failure, which Temporal retries automatically.

```ruby
class MyWorkflow < Temporalio::Workflow::Definition
  def execute
    if some_condition
      raise Temporalio::Error::ApplicationError.new(
        'Cannot process order',
        type: 'BusinessError'
      )
    end
    'success'
  end
end
```

**Note:** Do not use `non_retryable:` with `ApplicationError` inside a workflow (as opposed to an activity).

## Best Practices

- Use specific error types (`type:` parameter) for differentiation.
- Mark permanent failures as `non_retryable: true`.
- Set retry policies only when defaults are insufficient.
- Log errors before re-raising.
- Design activities for idempotency so retries are safe.
