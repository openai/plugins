# Ruby SDK Observability

## Overview

Temporal Ruby SDK provides logging, metrics, tracing, and visibility for monitoring workflows and activities.

## Logging

### Workflow Logging (Replay-Safe)

```ruby
Temporalio::Workflow.logger.info("Processing order")
Temporalio::Workflow.logger.warn("Retrying with fallback")
Temporalio::Workflow.logger.error("Order failed: #{reason}")
```

### Activity Logging

```ruby
Temporalio::Activity::Context.current.logger.info("Sending email")
Temporalio::Activity::Context.current.logger.warn("Slow response: #{elapsed}s")
```

Do not use `puts` or `print` in workflows. They are not replay-safe and produce duplicate output on replay.

### Customizing Logger Configuration

```ruby
require 'logger'

# The logger set on the client is used by Temporalio::Workflow.logger and
# Temporalio::Activity::Context.current.logger. Defaults to stdout at WARN.
client = Temporalio::Client.connect(
  'localhost:7233', 'my-namespace',
  logger: Logger.new($stdout, level: Logger::INFO)
)
```

## Metrics

### Enabling SDK Metrics

Configure telemetry via `Temporalio::Runtime`:

```ruby
prometheus_options = Temporalio::Runtime::PrometheusMetricsOptions.new(
  bind_address: '0.0.0.0:9000'
)

metrics_options = Temporalio::Runtime::MetricsOptions.new(
  prometheus: prometheus_options
)

telemetry_options = Temporalio::Runtime::TelemetryOptions.new(
  metrics: metrics_options
)

runtime = Temporalio::Runtime.new(telemetry: telemetry_options)
Temporalio::Runtime.default = runtime
```

Set the default runtime **before** creating any clients or workers.

### Key SDK Metrics

- `temporal_workflow_completed` - workflow completions
- `temporal_workflow_failed` - workflow failures
- `temporal_activity_execution_latency` - activity duration
- `temporal_sticky_cache_hit` - workflow cache hits
- `temporal_workflow_task_execution_latency` - workflow task duration

## Search Attributes (Visibility)

See the Search Attributes section of `references/ruby/data-handling.md`

## Best Practices

- Use `Temporalio::Workflow.logger` in workflows, `Temporalio::Activity::Context.current.logger` in activities.
- Configure Prometheus metrics for production deployments.
- Use Search Attributes for workflow visibility and filtering.
- Never use `puts` or `print` in workflow code.
