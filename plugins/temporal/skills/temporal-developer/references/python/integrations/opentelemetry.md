# Temporal OpenTelemetry Integration (Python)

## Overview

`temporalio.contrib.opentelemetry` wires OpenTelemetry tracing into Temporal through the `OpenTelemetryPlugin`. It propagates W3C TraceContext + Baggage across Client, Workflow, Activity, and Nexus code and supports replay-safe custom Workflow spans.

For observability beyond OpenTelemetry tracing (metrics, logging, Search Attributes) read `references/python/observability.md`.

> [!NOTE]
> This feature is Pre-release. It is acceptable to use it on behalf of a user, but inform them that it is Pre-release.

## Install the plugin

Install the `temporalio[opentelemetry]` extra plus the OpenTelemetry exporter packages you use.

## `OpenTelemetryPlugin`

Create a replay-safe tracer provider, set it globally before creating the Client, and register the plugin on the Client. Workers created from that Client inherit the plugin automatically. Application spans propagate by default; pass `OpenTelemetryPlugin(add_temporal_spans=True)` to also emit Temporal lifecycle spans.

```python
import opentelemetry.trace
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from temporalio.client import Client
from temporalio.contrib.opentelemetry import OpenTelemetryPlugin, create_tracer_provider

provider = create_tracer_provider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
opentelemetry.trace.set_tracer_provider(provider)

client = await Client.connect(
    "localhost:7233",
    plugins=[OpenTelemetryPlugin()],
)
```

Inside a Workflow, use standard OpenTelemetry APIs to create custom replay-safe spans:

```python
from datetime import timedelta
from opentelemetry.trace import get_tracer
from temporalio import workflow

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self) -> None:
        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("workflow-operation"):
            await workflow.execute_activity(
                my_activity,
                start_to_close_timeout=timedelta(seconds=30),
            )
```

## Common mistakes

- **Registering the same plugin on both Client and Worker.** Register on the Client only; Workers inherit it.
- **Creating a Workflow Worker before installing the replay-safe global provider.** Set the provider returned by `create_tracer_provider(...)` globally before constructing a Worker that uses `OpenTelemetryPlugin`.
- **Building a plain `opentelemetry.sdk.trace.TracerProvider` and passing it to `set_tracer_provider`.** `OpenTelemetryPlugin` requires a `ReplaySafeTracerProvider`; build it with `create_tracer_provider(...)`.

## Resources

- SDK metrics and observability reference: `references/python/observability.md`
