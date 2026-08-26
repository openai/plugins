# Temporal Pydantic AI Integration (Python)

## Overview

[Pydantic AI](https://ai.pydantic.dev/) ships first-party Temporal support in `pydantic_ai.durable_exec.temporal`. Add the `TemporalDurability` capability to a regular Pydantic AI `Agent`; inside a Temporal Workflow, it moves model requests, I/O tool calls, and MCP communication into Temporal Activities while the agent loop remains deterministic Workflow code.

The same agent remains usable outside a Workflow as a normal, non-durable agent. Attaching the capability does not make calls durable by itself: the call to `agent.run()` must execute inside a Temporal Workflow started through a Temporal Client.

This integration comes from Pydantic AI, not `temporalio.contrib`. For general design guidance, also read `references/core/ai-patterns.md` and `references/python/ai-patterns.md`.

## Install

Install the full package or the slim package with Temporal support:

```bash
pip install "pydantic-ai[temporal]"
# or
pip install "pydantic-ai-slim[temporal]"
```

## Attach `TemporalDurability`

Construct the agent at module scope and attach the capability through `capabilities=`:

```python
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalDurability

agent = Agent(
    "openai:gpt-5.6-sol",
    instructions="You answer geography questions.",
    name="geography",
    capabilities=[TemporalDurability()],
)
```

Module-scope construction lets the Worker discover and register every generated Activity before Workflow execution begins. Inside a Workflow, use the asynchronous agent API; `Agent.run_sync()` cannot drive Temporal's Workflow event loop, so call `await agent.run(...)` instead.

### `TemporalDurability` configuration

| Parameter | Purpose |
|---|---|
| `models` | Additional model instances keyed by stable IDs for runtime model switching. |
| `event_stream_handler` | Handles live model events inside model-request Activities and tool events in event-handler Activities. |
| `event_stream_topic` | Publishes events to a Temporal Workflow Stream topic for an external consumer. |
| `event_stream_events` | Filters which events are published to `event_stream_topic`. |
| `event_stream_batch_interval` | Controls Workflow Stream batching; defaults to 100 ms. |
| `name` | Overrides the agent name used in generated Activity names. |
| `deps_type` | Overrides the dependency type used for Temporal serialization. |
| `activity_config` | Base `ActivityConfig`; defaults to a 60-second `start_to_close_timeout`. |
| `model_activity_config` | Overrides the base config for model-request Activities. |
| `event_stream_handler_activity_config` | Overrides the base config for event-handler Activities. |
| `toolset_activity_config` | Per-toolset overrides keyed by stable toolset ID. |
| `run_context_type` | Custom `TemporalRunContext` subclass for the Activity boundary. |

## Stable agent and toolset identity

Generated Activity names depend on the agent `name` and toolset IDs. Set them explicitly, keep them unique, and do not rename them while Workflows using the old names may still replay.

Dynamic toolsets require an explicit stable ID. Set `id=` when constructing a `DynamicToolset`, on `@agent.toolset`, or on a `DynamicCapability`. A capability that contributes tools should also have a stable capability ID.

Factories for dynamic toolsets are re-resolved inside Activities and must produce the same result for the same dependencies.

## Register the plugin on the Client

Pass `PydanticAIPlugin()` to `Client.connect()`:

```python
from temporalio.client import Client
from pydantic_ai.durable_exec.temporal import PydanticAIPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[PydanticAIPlugin()],
)
```

The plugin supplies Pydantic-aware payload conversion, a compatible Workflow sandbox runner, Activity registration, and failure handling. Temporal propagates Client plugins that implement the Worker plugin protocol to Workers created from that Client. Do not pass the same `PydanticAIPlugin()` to `Worker`, because it would run twice.

Do not also set `data_converter=pydantic_data_converter`; the plugin owns the payload-converter wiring. It preserves other `DataConverter` settings such as a payload codec, failure converter, or external storage.

### Direct Activity registration

Normally, list agents on `PydanticAIWorkflow.__pydantic_ai_agents__`. If changing the Worker is easier than changing the Workflow class, pass `AgentPlugin(agent)` to the Worker instead. Keep `PydanticAIPlugin()` on the Client for conversion and sandbox configuration.

## Define and register the Workflow

List every durable agent used by a Workflow in `__pydantic_ai_agents__`. These are regular `Agent` instances carrying `TemporalDurability`, not wrapper agents.

```python
from temporalio import workflow
from pydantic_ai.durable_exec.temporal import PydanticAIWorkflow


@workflow.defn
class GeographyWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await agent.run(prompt)
        return result.output
```

`PydanticAIWorkflow` is optional but provides typing for `__pydantic_ai_agents__`. A Workflow using multiple agents should list each one.

## Serialization and payload limits

Values crossing between the Workflow and Activities must be Pydantic-serializable. This includes `deps`, model settings, run-context metadata, tool-call metadata, and tool metadata. Untyped dictionaries arrive in their JSON form, so tuples and sets become lists, models become dictionaries, and non-string dictionary keys become strings. Re-validate them when the receiving code needs a specific type.

The Activity-side `RunContext` contains only the fields Pydantic AI serializes. Accessing unavailable fields such as `model`, `prompt`, `messages`, `model_settings`, or `tracer` raises `UserError`. Supply a custom `TemporalRunContext` through `run_context_type=` when an Activity requires additional serializable context.

Treat dependency models and other persisted payload schemas as durable contracts. An incompatible type change can prevent a Worker from decoding existing Workflow history before user code runs.

Temporal limits individual payloads to 2 MB by default, and binary data grows when base64-encoded. Keep large media and dependencies out of Workflow history by returning durable references or configuring Temporal external storage. Stored payloads must remain available for as long as their Workflow histories can replay.

## Runtime models

Model-name strings can cross the Activity boundary directly. The agent must have a model when it is constructed; that model is registered automatically as the default.

Runtime `Model` instances cannot be reconstructed safely from only their model ID. Register each instance in `TemporalDurability(models={...})`, then select it by its stable key or pass that registered instance to `agent.run(model=...)`.

For custom providers or credentials derived from `deps`, add a `ResolveModelId` capability before `TemporalDurability`. Its resolver runs again on the Worker and must be deterministic for a given model ID and dependencies; it must not perform external I/O.

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ResolveModelId
from pydantic_ai.durable_exec.temporal import TemporalDurability

# Define `default_model`, `fast_model`, and `resolve_model` at module scope.
agent = Agent(
    default_model,
    name="multi-model",
    capabilities=[
        ResolveModelId(resolve_model),
        TemporalDurability(models={"fast": fast_model}),
    ],
)
```

Executing toolsets that require durable wrapping must be attached when the agent is constructed so their Activities can be registered before the Worker starts. Runtime toolsets are limited to non-executing toolsets or function toolsets whose tools all opt out of Activity wrapping.

## Activity configuration

`activity_config` is the base for all generated Activities. `model_activity_config`, `event_stream_handler_activity_config`, and entries in `toolset_activity_config` merge over it. Pydantic AI validates these configs when constructing `TemporalDurability`, preventing an invalid key from repeatedly failing a Workflow Task at runtime.

Per-tool configuration belongs in tool metadata:

```python
from datetime import timedelta
from temporalio.workflow import ActivityConfig
from pydantic_ai.toolsets import FunctionToolset

toolset = FunctionToolset(id="research")

@toolset.tool(
    metadata={
        "temporal": ActivityConfig(
            start_to_close_timeout=timedelta(minutes=5),
        )
    }
)
async def fetch_paper(arxiv_id: str) -> str:
    ...
```

Use `metadata={"temporal": False}` to keep a non-I/O async tool in Workflow code. Synchronous tools cannot opt out because thread execution is non-deterministic. For third-party tools or groups of tools, apply the same metadata through `SetToolMetadata`.

Generated Activities heartbeat in the background. Model Activities receive a 30-second heartbeat timeout by default; other Activity types receive one only when configured. Do not set a heartbeat timeout on code that can block the event loop long enough to prevent the heartbeat task from running.

Temporal already retries failed Activities. Disable overlapping Pydantic AI HTTP retries and provider-client retries when possible, then configure the Temporal retry policy through `ActivityConfig`.

## Logfire

Register `LogfirePlugin` alongside `PydanticAIPlugin` on the Client:

```python
from pydantic_ai.durable_exec.temporal import LogfirePlugin, PydanticAIPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[PydanticAIPlugin(), LogfirePlugin()],
)
```

## End-to-end example

```python
import asyncio
import uuid

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import (
    PydanticAIPlugin,
    PydanticAIWorkflow,
    TemporalDurability,
)

agent = Agent(
    "openai:gpt-5.6-sol",
    instructions="You answer geography questions.",
    name="geography",
    capabilities=[TemporalDurability()],
)


@workflow.defn
class GeographyWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await agent.run(prompt)
        return result.output


async def main() -> None:
    client = await Client.connect(
        "localhost:7233",
        plugins=[PydanticAIPlugin()],
    )

    async with Worker(
        client,
        task_queue="geography",
        workflows=[GeographyWorkflow],
    ):
        result = await client.execute_workflow(
            GeographyWorkflow.run,
            args=["What is the capital of Mexico?"],
            id=f"geography-{uuid.uuid4()}",
            task_queue="geography",
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

## Resources

- `references/python/ai-patterns.md` — Python AI/LLM patterns, payload conversion, and retry classification.
- `references/core/ai-patterns.md` — language-agnostic agent and tool-placement patterns.
- Upstream guide — [Pydantic AI durable execution with Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/).
- Upstream API reference — [`pydantic_ai.durable_exec.temporal`](https://pydantic.dev/docs/ai/api/pydantic-ai/durable_exec/).
