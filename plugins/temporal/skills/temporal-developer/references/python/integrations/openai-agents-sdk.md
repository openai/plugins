# Temporal OpenAI Agents SDK Integration (Python)

## Overview

The Temporal Python SDK ships a contrib module that runs [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) agents as durable Temporal Workflows. Model calls execute as Temporal Activities; tools can be Activities, Nexus stubs, or workflow-resident `@function_tool`s; MCP servers, sandbox backends, and OpenTelemetry export are layered on top.

The integration is delivered as a Temporal plugin: `OpenAIAgentsPlugin` from `temporalio.contrib.openai_agents`, registered on both the client and the worker via `plugins=[...]`.

For language-agnostic AI/LLM patterns (centralized retries, multi-agent orchestration, when to put a tool in an Activity vs. the workflow) see `references/core/ai-patterns.md`. For Python-side LLM patterns that apply when **not** using this plugin (Pydantic data converter, generic LLM activity, `max_retries=0` on the raw OpenAI client) see `references/python/ai-patterns.md` — note that the plugin already configures Pydantic serialization for you.

## Install

The integration lives at `temporalio.contrib.openai_agents`; use it by installing `temporalio[openai-agents]` to get the extra OpenAI Agents SDK dep.

```python
from temporalio.contrib.openai_agents import OpenAIAgentsPlugin, ModelActivityParameters
```

## Register the plugin

Pass `OpenAIAgentsPlugin` to `Client.connect(..., plugins=[...])`. Register it on **both** the worker process and the client process — the worker uses it to host the model activity; the client uses it to keep payload serialization compatible.

```python
from datetime import timedelta
from temporalio.client import Client
from temporalio.contrib.openai_agents import OpenAIAgentsPlugin, ModelActivityParameters
from temporalio.worker import Worker

client = await Client.connect(
    "localhost:7233",
    plugins=[
        OpenAIAgentsPlugin(
            model_params=ModelActivityParameters(
                start_to_close_timeout=timedelta(seconds=30)
            )
        ),
    ],
)
```

The 30-second timeout above is the example from the README, not a documented default. Pick a value sized to your model and prompt.

With the plugin registered, four things happen automatically:

- Pydantic types serialize correctly across activity boundaries.
- OpenAI Agents tracing context propagates between workflow and activity.
- The model-invocation activity is registered with every Temporal worker.
- The OpenAI Agents SDK is reconfigured so its model calls run as Temporal activities.

## A durable agent

Inside a workflow, write standard OpenAI Agents SDK code — `Agent`, `Runner.run`. The plugin reroutes model calls through an Activity, so the agent loop is durable.

```python
from temporalio import workflow
from agents import Agent, Runner

@workflow.defn
class HelloWorldAgent:
    @workflow.run
    async def run(self, prompt: str) -> str:
        agent = Agent(
            name="Assistant",
            instructions="You only respond in haikus.",
        )
        result = await Runner.run(agent, input=prompt)
        return result.final_output
```

Register the workflow with a `Worker` exactly like any other Temporal workflow.

## Tools

Two ways to wire a tool into an agent. Choose based on whether the tool has side effects.

### Activities as tools — for I/O, retries, timeouts

Wrap a Temporal activity with `temporalio.contrib.openai_agents.workflow.activity_as_tool` to expose it to the agent. Each invocation runs as a Temporal Activity, with retries and timeouts governed by the `ActivityOptions` you pass.

```python
from dataclasses import dataclass
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.contrib import openai_agents
from agents import Agent, Runner

@dataclass
class Weather:
    city: str
    temperature_range: str
    conditions: str

@activity.defn
async def get_weather(city: str) -> Weather:
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")

@workflow.defn
class WeatherAgent:
    @workflow.run
    async def run(self, question: str) -> str:
        agent = Agent(
            name="Weather Assistant",
            instructions="You are a helpful weather agent.",
            tools=[
                openai_agents.workflow.activity_as_tool(
                    get_weather,
                    start_to_close_timeout=timedelta(seconds=10),
                ),
            ],
        )
        result = await Runner.run(starting_agent=agent, input=question)
        return result.final_output
```

Just like with standard `@function_tool` declarations, if your Activity-as-tool has a `RunContextWrapper[T]` as the first parameter, then it will receive the [OpenAI Agents context wrapper](https://openai.github.io/openai-agents-python/ref/run_context/#agents.run_context.RunContextWrapper). However, unlike with a `@function_tool`,
it will only be a **read-only copy** of the OpenAI Agents context — mutations from the tool body are not visible to other tools or to the agent!

```python
@activity.defn
async def get_weather(ctx: RunContextWrapper[MyState], city: str) -> Weather:
    state: MyState = ctx.context
    # Now we have **read-only** access to state which is shared across tool invocations.
    pass
```

Note that the initial run context comes from the `context=...` argument you pass to `Runner.run()`, and is `None` by default.

### `@function_tool` — for deterministic, in-process tools

For pure computations or tools that mutate agent state, use the upstream `@function_tool` decorator. The tool runs as part of the workflow, so it must obey workflow determinism rules.

```python
from temporalio import workflow
from agents import Agent, Runner, function_tool

@function_tool
def calculate_circle_area(radius: float) -> float:
    return 3.14 * radius ** 2

@workflow.defn
class MathAssistantAgent:
    @workflow.run
    async def run(self, message: str) -> str:
        agent = Agent(
            name="Math Assistant",
            instructions="You are a helpful math assistant.",
            tools=[calculate_circle_area],
        )
        result = await Runner.run(agent, input=message)
        return result.final_output
```

`@function_tool` bodies can read **and update** OpenAI Agents context:

```python
@activity.defn
async def calculate_circle_area(ctx: RunContextWrapper[MyState], radius: float) -> float:
    state: MyState = ctx.context
    # Now we have **read-write** access to state which is shared across tool invocations.
    pass
```

Note that the initial run context comes from the `context=...` argument you pass to `Runner.run()`, and is `None` by default.

In addition, since a `@function_tool` runs in the workflow, they can also call Temporal activities or other durable primitives themselves.

**Don't put I/O, system clock, or sources of randomness inside a `@function_tool` body.** Make it an `@activity.defn` and wrap with `activity_as_tool` instead.

### Picking between the two

| Tool body does… | Use |
|---|---|
| Network call, file I/O, DB access | Activity + `activity_as_tool` |
| Mutates agent state read by other tools | `@function_tool` |
| Pure computation, deterministic | Either; `@function_tool` is lighter |
| Calls `time.time()`, RNG, threads | Activity + `activity_as_tool` |

## MCP servers

MCP support comes in two flavors based on whether the server keeps session state between calls. Choose by examining the server's protocol, not by guessing.

- **Stateless MCP server** — each call is self-contained. Wrap with `StatelessMCPServerProvider(factory)` and register on the plugin.
- **Stateful MCP server** — session state persists between calls. Failure raises `ApplicationError`; **Temporal cannot auto-recover** the lost server state, so you implement application-level retry.

Both wrappers work with `MCPServerStdio`, `MCPServerSse`, and `MCPServerStreamableHttp` transports.

### Stateless MCP — worker setup

```python
from agents.mcp import MCPServerStdio
from temporalio.contrib.openai_agents import (
    ModelActivityParameters,
    OpenAIAgentsPlugin,
    StatelessMCPServerProvider,
)

filesystem_server = StatelessMCPServerProvider(
    lambda: MCPServerStdio(
        name="FileSystemServer",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"],
        },
    )
)

client = await Client.connect(
    "localhost:7233",
    plugins=[
        OpenAIAgentsPlugin(
            model_params=ModelActivityParameters(
                start_to_close_timeout=timedelta(seconds=60)
            ),
            mcp_server_providers=[filesystem_server],
        ),
    ],
)
```

### Stateless MCP — workflow usage

Reference the server inside a workflow with `openai_agents.workflow.stateless_mcp_server("Name")`. The string must match the `name=` argument on the MCP server instance the factory creates.

```python
from temporalio import workflow
from temporalio.contrib import openai_agents
from agents import Agent, Runner

@workflow.defn
class FileSystemWorkflow:
    @workflow.run
    async def run(self, query: str) -> str:
        server = openai_agents.workflow.stateless_mcp_server("FileSystemServer")
        agent = Agent(
            name="File Assistant",
            instructions="Use the filesystem tools to read files and answer questions.",
            mcp_servers=[server],
        )
        result = await Runner.run(agent, input=query)
        return result.final_output
```

### Hosted MCP

For network-accessible MCP servers, the upstream `HostedMCPTool` (OpenAI Responses API hosting an MCP client) is also supported and avoids the stateless/stateful wrapping choice.

## Sandbox support

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

The OpenAI Agents SDK's `SandboxAgent` runs commands inside a remote or local sandbox (e.g. Daytona, Docker, E2B, local Unix). With this integration, every sandbox operation — creating a session, exec, file I/O, PTY — dispatches as a Temporal activity, so sandbox work is durable like any other activity and sandbox session state survives worker restarts.

> Naming gotcha: this is the **Agents SDK** sandbox (remote command execution), **not** the Temporal Python SDK workflow sandbox (determinism protection). They are unrelated.

### Worker setup

Register one or more `SandboxClientProvider("name", BaseSandboxClient())` on the plugin via `sandbox_clients=[...]`. Each provider's name becomes the prefix for its activities, so names must be unique.

```python
from temporalio.contrib.openai_agents import (
    OpenAIAgentsPlugin,
    SandboxClientProvider,
    ModelActivityParameters,
)
from agents.extensions.sandbox.daytona import DaytonaSandboxClient
from agents.extensions.sandbox.unix_local import UnixLocalSandboxClient

client = await Client.connect(
    "localhost:7233",
    plugins=[
        OpenAIAgentsPlugin(
            model_params=ModelActivityParameters(
                start_to_close_timeout=timedelta(seconds=30)
            ),
            sandbox_clients=[
                SandboxClientProvider("daytona", DaytonaSandboxClient()),
                SandboxClientProvider("local", UnixLocalSandboxClient()),
            ],
        ),
    ],
)
```

### Workflow usage

Reference a registered backend in the workflow with `temporal_sandbox_client("name")`. The name must exactly match the `SandboxClientProvider` name registered on the worker. Pass it through `RunConfig(sandbox=SandboxRunConfig(client=...))`.

```python
from temporalio import workflow
from temporalio.contrib.openai_agents.workflow import temporal_sandbox_client
from agents import Runner
from agents.sandbox import SandboxAgent, SandboxRunConfig
from agents.run import RunConfig

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, prompt: str) -> str:
        agent = SandboxAgent(
            name="Coding Assistant",
            instructions="You are a helpful coding assistant with access to a sandbox.",
        )
        result = await Runner.run(
            agent,
            prompt,
            run_config=RunConfig(
                sandbox=SandboxRunConfig(
                    client=temporal_sandbox_client("daytona"),
                    options=DaytonaSandboxClientOptions(pause_on_exit=False),
                ),
            ),
        )
        return result.final_output
```

A single workflow can target multiple backends by name; register each on the worker and reference in the workflow.

## Streaming

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

Streaming uses the upstream `Runner.run_streamed` API. Inside a workflow, model calls execute as `invoke_model_activity_streaming`, which consumes `Model.stream_response` and returns the collected list of native OpenAI response events. The workflow surfaces those events via `RunResultStreaming.stream_events()`.

```python
from agents import Agent, Runner
from agents.stream_events import RawResponsesStreamEvent
from temporalio import workflow

@workflow.defn
class MyAgent:
    @workflow.run
    async def run(self, prompt: str) -> str:
        agent = Agent(name="Assistant", instructions="...")
        result = Runner.run_streamed(agent, prompt)
        async for event in result.stream_events():
            if isinstance(event, RawResponsesStreamEvent):
                raw_event = event.data
                ...
        return result.final_output
```

To publish events to external subscribers, set a topic on `ModelActivityParameters(streaming_topic="events")` and host a `WorkflowStream` in the workflow. The topic is required when calling `Runner.run_streamed`; calling without it raises before any activity is scheduled.

**Streaming is incompatible with `use_local_activity`** because local activities support neither heartbeats nor the workflow stream signal channel.

Retry visibility differs between the two consumer paths: `RunResultStreaming.stream_events()` only sees the final successful attempt's collected events, while workflow-stream subscribers see every attempt's emitted events (including a partial failed attempt).

## OpenTelemetry integration

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

Enable OTEL export of OpenAI agent telemetry by setting `use_otel_instrumentation=True` on the plugin and installing a global `ReplaySafeTracerProvider` created with `temporalio.contrib.opentelemetry.create_tracer_provider`. Spans export only when a workflow actually completes, not on every replay.

```python
from temporalio.contrib.openai_agents import OpenAIAgentsPlugin, ModelActivityParameters
from temporalio.contrib.opentelemetry import create_tracer_provider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

tracer_provider = create_tracer_provider()
tracer_provider.add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
)
trace.set_tracer_provider(tracer_provider)

client = await Client.connect(
    "localhost:7233",
    plugins=[
        OpenAIAgentsPlugin(
            use_otel_instrumentation=True,
            model_params=ModelActivityParameters(
                start_to_close_timeout=timedelta(seconds=30)
            ),
        ),
    ],
)
```

OTEL extras need to be installed separately:

```bash
pip install openinference-instrumentation-openai-agents opentelemetry-sdk
```

If `use_otel_instrumentation=True` is set without the deps installed, the plugin raises `ImportError` with the exact install line. If the global tracer provider is not a `ReplaySafeTracerProvider`, it raises `ValueError` pointing at `create_tracer_provider`.

### Direct `opentelemetry.trace` calls inside a workflow

To call the OpenTelemetry API directly inside a workflow (e.g. `opentelemetry.trace.get_tracer(__name__).start_as_current_span(...)`), allow OTel through the Python SDK's workflow sandbox using `with_passthrough_modules("opentelemetry")` on the runner:

```python
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

worker = Worker(
    client,
    task_queue="my-task-queue",
    workflows=[MyWorkflow],
    workflow_runner=SandboxedWorkflowRunner(
        SandboxRestrictions.default.with_passthrough_modules("opentelemetry"),
    ),
)
```

To get correct trace parenting, start an Agents SDK span with `agents.custom_span(...)` before opening any direct OTEL spans — the Agents-SDK span establishes the OTEL context that subsequent direct spans inherit from.

### Starting a trace from the client

`plugin.tracing_context()` lets the client side open an Agents-SDK trace before calling `execute_workflow`, so the whole workflow run is part of one larger trace:

```python
plugin = OpenAIAgentsPlugin(use_otel_instrumentation=True)
client = await Client.connect("localhost:7233", plugins=[plugin])

with plugin.tracing_context():
    with trace("Customer support workflow"):
        with custom_span("Workflow execution"):
            await client.execute_workflow(
                CustomerSupportAgent.run,
                "Help me with my order",
                id="customer-support-123",
                task_queue="my-task-queue",
            )
```

## Feature support

The README's compatibility matrix, condensed:

| Area | Supported | Not supported |
|---|---|---|
| Model providers | OpenAI, LiteLLM | — |
| Model response | `Runner.run`; `Runner.run_streamed` (experimental) | — |
| Tools | `FunctionTool`, `WebSearchTool`, `FileSearchTool`, `HostedMCPTool`, `ImageGenerationTool`, `CodeInterpreterTool` | `LocalShellTool`, `ComputerTool` |
| MCP transports | `MCPServerStdio`, `MCPServerSse`, `MCPServerStreamableHttp` | — |
| Guardrails | Code, Agent | — |
| Sessions | (in-workflow agent state) | `SQLiteSession` |
| Tracing | OpenAI platform; OpenTelemetry (Public Preview) | — |
| Voice | `VoicePipeline` (STT/TTS outside Temporal, agent loop durable) | Realtime agents |
| Utilities | — | REPL |

Tool context propagation:

| Path | Receives context | Can update context |
|---|---|---|
| Activity tool (`activity_as_tool`) | Yes (copy) | **No** |
| Function tool (`@function_tool`) | Yes | Yes |

## Common pitfalls

- **Register the plugin on both client and worker.** Skipping client-side registration breaks payload compatibility.
- **Don't put I/O or non-deterministic code in `@function_tool` bodies.** Move it to an `@activity.defn` and wrap with `activity_as_tool`.
- **Don't expect Temporal to auto-recover stateful MCP server sessions.** A failed session raises `ApplicationError`; implement your own application-level retry.
- **Don't enable streaming together with `use_local_activity`.** Local activities lack heartbeats and the workflow-stream signal channel. Use the standard activity path.
- **Don't call `Runner.run_streamed` without `ModelActivityParameters(streaming_topic="...")`.** It raises before any activity is scheduled.
- **MCP server names must match exactly** between `MCPServerStdio(name="X")` and `stateless_mcp_server("X")`. Same for `SandboxClientProvider("Y", ...)` and `temporal_sandbox_client("Y")`.
- **`use_otel_instrumentation=True` requires `ReplaySafeTracerProvider`.** Setting `trace.set_tracer_provider(...)` with anything else raises `ValueError`.
- **Activity-tool context is a read-only copy.** A tool that needs to mutate agent state must be a `@function_tool`.

## Resources

- `references/core/ai-patterns.md` — language-agnostic agent patterns (when to wrap a tool as an activity, centralized retry, multi-agent orchestration).
- `references/python/ai-patterns.md` — Python-side LLM patterns for when you are **not** using this plugin (Pydantic data converter, OpenAI client `max_retries=0`).
- `references/python/determinism.md` and `references/core/determinism.md` — determinism rules that apply to `@function_tool` bodies and any in-workflow agent code.
- Upstream samples — [`temporalio/samples-python/openai_agents`](https://github.com/temporalio/samples-python/tree/main/openai_agents).
