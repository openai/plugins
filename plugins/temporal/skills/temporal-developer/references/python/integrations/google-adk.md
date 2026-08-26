# Temporal Google ADK Integration

## Overview

`temporalio.contrib.google_adk_agents` makes [Google ADK](https://adk.dev/) agents durable on the Temporal Python SDK: ADK model calls run through Temporal Activities, tools dispatch through Activities or the workflow thread, and non-deterministic primitives (`time.time()`, `uuid.uuid4()`) are replaced with deterministic workflow equivalents inside the sandbox.

The integration is built on the Python SDK [Plugin system](https://docs.temporal.io/develop/plugins-guide) and ships as part of the `temporalio` package via the `google-adk` extra.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For general Temporal AI/LLM patterns (retries, rate limits, multi-agent orchestration) see `references/core/ai-patterns.md` and `references/python/ai-patterns.md`.

## Prerequisites

| Dependency           | Minimum version |
| -------------------- | --------------- |
| Temporal Python SDK  | 1.24.0          |
| Google ADK           | a working `google-adk` install (pulled in by the extra) |

You also need access to a supported model (e.g. a Gemini API key for `gemini-flash-latest` / `gemini-2.5-pro`) and a running Temporal server — `temporal server start-dev` for local development, self-hosted, or Temporal Cloud.

## Install

```bash
pip install "temporalio[google-adk]"
```

The extra name is `google-adk` (hyphen). The module path is `temporalio.contrib.google_adk_agents` (note the `_agents` suffix).

## Public API

| Symbol                       | Import                                                                  | Purpose                                                                  |
| ---------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `GoogleAdkPlugin`            | `from temporalio.contrib.google_adk_agents import GoogleAdkPlugin`      | Client/Worker plugin: determinism replacement + Pydantic/ADK passthrough |
| `TemporalModel`              | `from temporalio.contrib.google_adk_agents import TemporalModel`        | LLM model wrapper that routes model calls through a Temporal Activity   |
| `activity_tool`              | `from temporalio.contrib.google_adk_agents.workflow import activity_tool` | Wraps a plain `@activity.defn` function as an ADK tool                  |
| `TemporalMcpToolSet`         | `from temporalio.contrib.google_adk_agents import TemporalMcpToolSet`   | Executes MCP tools as Temporal Activities                                |
| `TemporalMcpToolSetProvider` | `from temporalio.contrib.google_adk_agents import TemporalMcpToolSetProvider` | Factory wired into `GoogleAdkPlugin(toolset_providers=[...])` so MCP activities register with the worker |

## Configure the plugin on Client and Worker

`GoogleAdkPlugin()` must be attached to the Temporal `Client` used to build the worker. It installs the determinism replacements, configures Pydantic/ADK serialization, and registers the model and MCP activities on the worker.

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.google_adk_agents import GoogleAdkPlugin

async def main():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin()],
    )

    worker = Worker(
        client,
        task_queue="my-agent-task-queue",
        workflows=[WeatherAgentWorkflow],
        activities=[get_weather],
    )
    await worker.run()

asyncio.run(main())
```

Attach the same plugin when starting workflows from a client process so that data converters and toolset providers line up across both sides:

```python
client = await Client.connect(
    "localhost:7233",
    plugins=[GoogleAdkPlugin()],
)
result = await client.execute_workflow(
    WeatherAgentWorkflow.run,
    "What's the weather in San Francisco?",
    id="weather-agent-1",
    task_queue="my-agent-task-queue",
)
```

## Define tools with `activity_tool`

Write the underlying function as a normal Temporal Activity, then wrap it with `activity_tool(...)` to produce a tool that ADK can attach to an Agent. The wrapper records timeouts and retry policy at construction time, so each invocation runs as a Temporal Activity with those settings.

```python
from datetime import timedelta
from temporalio import activity
from temporalio.common import RetryPolicy
from temporalio.contrib.google_adk_agents.workflow import activity_tool

@activity.defn
async def get_weather(city: str) -> str:
    return f"72°F and sunny in {city}"

weather_tool = activity_tool(
    get_weather,
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(maximum_attempts=3),
)
```

Register the underlying `@activity.defn` function on the worker's `activities=` list — `activity_tool` does **not** auto-register it.

## Use `TemporalModel` on the Agent

`TemporalModel(model_name, activity_config=ActivityConfig(...))` wraps any ADK-supported model so each call lands in a Temporal Activity. `ActivityConfig` comes from `temporalio.workflow` and accepts the usual per-Activity settings (timeouts, retry policy, task queue, summary, etc.).

```python
from google.adk.agents import Agent
from temporalio.contrib.google_adk_agents import TemporalModel
from temporalio.workflow import ActivityConfig

agent = Agent(
    name="weather_agent",
    model=TemporalModel(
        "gemini-flash-latest",
        activity_config=ActivityConfig(summary="Weather Agent"),
    ),
    tools=[weather_tool],
)
```

Streaming responses are not currently supported through `TemporalModel`.

## Wrap the agent in a Workflow

Workflows drive ADK in the same way as a non-Temporal program: build an `InMemoryRunner`, create a session, and iterate `run_async`. Use `contextlib.aclosing` so the async generator is closed deterministically, and consume the events to collect the final assistant text.

```python
from contextlib import aclosing
from google.adk.runners import InMemoryRunner
from google.genai import types
from temporalio import workflow

@workflow.defn
class WeatherAgentWorkflow:
    @workflow.run
    async def run(self, user_message: str) -> str:
        runner = InMemoryRunner(agent=agent, app_name="weather_app")
        session = await runner.session_service.create_session(
            user_id="user", app_name="weather_app",
        )
        result = ""
        async with aclosing(
            runner.run_async(
                user_id="user",
                session_id=session.id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)],
                ),
            )
        ) as events:
            async for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            result = part.text
        return result
```

Determinism rules still apply to the workflow body itself: don't read the wall clock, generate random IDs, or perform I/O outside Activities or the ADK-managed model/tool calls. The plugin redirects `time.time()` and `uuid.uuid4()` to `workflow.now()` and `workflow.uuid4()` when running inside a workflow, but new non-deterministic call sites you add (e.g. `random`, `datetime.now()`, network I/O) are not covered.

## MCP tools

To expose [MCP](https://modelcontextprotocol.io/) tools to an ADK agent through Temporal, register a `TemporalMcpToolSetProvider` on the plugin and attach a matching `TemporalMcpToolSet` to the agent. The provider factory builds the underlying ADK `McpToolset`; the same factory is also passed as `not_in_workflow_toolset=` on the workflow-side `TemporalMcpToolSet` so local runs (e.g. `adk run` / `adk web`) execute the toolset directly.

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from temporalio.contrib.google_adk_agents import (
    GoogleAdkPlugin,
    TemporalMcpToolSet,
    TemporalMcpToolSetProvider,
    TemporalModel,
)

def toolset_factory(_):
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path"],
            ),
        ),
    )

toolset_provider = TemporalMcpToolSetProvider("my-tools", toolset_factory)

client = await Client.connect(
    "localhost:7233",
    plugins=[GoogleAdkPlugin(toolset_providers=[toolset_provider])],
)

agent = Agent(
    name="tool_agent",
    model=TemporalModel("gemini-flash-latest"),
    tools=[TemporalMcpToolSet("my-tools", not_in_workflow_toolset=toolset_factory)],
)
```

The provider name (`"my-tools"` above) must match between `TemporalMcpToolSetProvider` and `TemporalMcpToolSet`. Always pass `not_in_workflow_toolset=` — without it, local execution outside a workflow has no fallback path.

## Local fallback for `adk run` / `adk web`

`TemporalModel`, `activity_tool`, and `TemporalMcpToolSet` detect when they are invoked outside a workflow and execute directly against the underlying model, function, or MCP toolset. The same agent definition therefore works both under `adk run` / `adk web` for local development and under a Temporal worker in production — no separate code paths.

## Common mistakes

- **Mixing up `ActivityConfig` and `ActivityOptions`.** `TemporalModel` takes `activity_config=ActivityConfig(...)` from `temporalio.workflow`.
- **Forgetting `not_in_workflow_toolset` on `TemporalMcpToolSet`.** Required for local fallback.
- **Skipping `GoogleAdkPlugin()` on the client used by `execute_workflow`.** Data-converter and toolset wiring lives on the plugin; using only the worker-side plugin leads to serialization errors.
- **Registering `activity_tool(...)` wrappers in `activities=`.** Register the underlying `@activity.defn` function instead.
- **Forgetting non-determinism rules.** As with Temporal broadly, workflow code must be deterministic. This plugin makes it a bit easier by auto-replacing common sources of non-determinism with Temporal durable variants, but you are strongly encouraged to just use those explicitly. In workflow code: use `workflow.now()`, etc. In activity code: use `time.time()` or whatever standard non-deterministic things, NOT `workflow.*` calls.
- **Expecting streaming responses.** Not currently supported via `TemporalModel`.
