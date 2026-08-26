# Temporal LangSmith Tracing Integration (Python)

## Overview

`temporalio.contrib.langsmith` is a Temporal [Plugin](https://docs.temporal.io/develop/plugins-guide) for the Python SDK that makes [LangSmith](https://smith.langchain.com/) traces work across Temporal Workflows and Activities. It propagates trace context across Worker boundaries so `@traceable` calls, LLM invocations, and Temporal operations show up as a single connected trace, and it suppresses duplicate traces during Workflow replays.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For Python AI patterns (Pydantic data converter, disabling client-side LLM retries, generic LLM Activity shape) read `references/python/ai-patterns.md`. For conceptual LLM patterns shared across SDKs read `references/core/ai-patterns.md`. Python sandbox theory lives in `references/python/determinism-protection.md` — this integration handles the sandbox restrictions for `@traceable` for you, so do not restate sandbox rules here.

## Install

```bash
uv add temporalio[langsmith]
```

## Register the Plugin

Register `LangSmithPlugin` on both the Client (starter side) and every Worker. Strictly only the sides that produce traces need it, but registering everywhere avoids surprises with context propagation. The Client and Worker can use different configurations (e.g. different `add_temporal_runs` settings).

```python
from temporalio.client import Client
from temporalio.contrib.langsmith import LangSmithPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[LangSmithPlugin(project_name="my-project")],
)
```

```python
from temporalio.worker import Worker
from temporalio.contrib.langsmith import LangSmithPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[LangSmithPlugin(project_name="chatbot")],
)

worker = Worker(
    client,
    task_queue="chatbot",
    workflows=[ChatbotWorkflow],
    activities=[call_openai],
)
await worker.run()
```

## `LangSmithPlugin` parameters

Constructor is keyword-only.

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `client` | `langsmith.Client \| None` | `None` (auto-created) | LangSmith client; auto-created if not supplied. |
| `project_name` | `str \| None` | `None` | LangSmith project name traces are written to. |
| `add_temporal_runs` | `bool` | `False` | When `True`, adds Temporal operation nodes (StartWorkflow, RunWorkflow, StartActivity, RunActivity) to the trace tree. |
| `default_metadata` | `dict[str, Any] \| None` | `None` | Custom metadata attached to all LangSmith traces. |
| `default_tags` | `list[str] \| None` | `None` | Custom tags attached to all LangSmith traces. |

`LangSmithInterceptor` is also exported alongside `LangSmithPlugin`; the plugin is the registration entry point and is what user code should use.

## Where `@traceable` works

| Location | Works? | Notes |
|---|---|---|
| Inside Workflow methods | Yes | Traces called from inside `@workflow.run`, `@workflow.signal`, etc.; sync and async methods. |
| Inside Activity methods | Yes | Traces called from inside `@activity.defn`; sync and async methods. |
| On `@activity.defn` functions | Yes | Stack `@traceable` on top of `@activity.defn` (decorator order matters). Fires on every retry. |
| On Workflow methods | No | Do not wrap `@traceable` around `@workflow.defn`, `workflow.run`, `workflow.signal`; Use inside `@workflow.run` instead. |

Decorator-order example for an Activity — `@traceable` on top:

```python
from langsmith import traceable
from temporalio import activity

@traceable(name="Call OpenAI", run_type="llm")
@activity.defn
async def call_openai(...):
    ...
```

## `add_temporal_runs` — Temporal operation visibility

By default (`add_temporal_runs=False`), only application `@traceable` runs appear in LangSmith. With `add_temporal_runs=True`, Temporal operation nodes are added so the orchestration layer is visible alongside application logic.

```python
plugins=[LangSmithPlugin(project_name="my-project", add_temporal_runs=True)]
```

With `add_temporal_runs=True`, `StartFoo` and `RunFoo` appear as siblings: the start is the short-lived outbound RPC that enqueues work, the run is the actual execution.

## Replay safety — handled by the plugin

The plugin makes `@traceable` replay-safe in the Workflow sandbox. You do not need to write extra code for this.

- Replay correctness and non-duplication is correctly handled by the plugin, no matter the cause of replay (happy paths, errors, crashes, etc.). Replayed Activities create no new trace data; new work after that produces fresh traces
- The plugin injects metadata using `workflow.now()` for timestamps and `workflow.random()` for UUIDs instead of `datetime.now()` and `uuid4()`.
- LangSmith HTTP calls run on a background thread pool that does not interfere with deterministic Workflow execution.

## Context propagation

Trace context flows automatically across Client → Workflow → Activity → Child Workflow → Nexus via Temporal headers. Do not pass context manually.

## Worked example — chatbot Workflow with `@traceable`

A Workflow stays alive waiting for user messages and dispatches each message to an Activity that calls the LLM. `@traceable` can be used both inside `@workflow.run` and stacked on top of `@activity.defn`.

Activity (wraps the LLM call):

```python
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import AsyncOpenAI
from temporalio import activity

@traceable(name="Call OpenAI", run_type="chain")
@activity.defn
async def call_openai(request: OpenAIRequest) -> Response:
    client = wrap_openai(AsyncOpenAI())  # traced LangSmith wrapper
    return await client.responses.create(
        model=request.model,
        input=request.input,
        instructions=request.instructions,
    )
```

Workflow (orchestrates the conversation; `@traceable` used **inside** `@workflow.run`, not on the class):

```python
from datetime import timedelta
from langsmith import traceable
from temporalio import workflow

@workflow.defn
class ChatbotWorkflow:
    @workflow.run
    async def run(self) -> str:
        # @traceable works inside Workflows — fully replay-safe
        now = workflow.now().strftime("%b %d %H:%M")
        return await traceable(
            name=f"Session {now}", run_type="chain",
        )(self._run_with_trace)()

    async def _run_with_trace(self) -> str:
        while not self._done:
            await workflow.wait_condition(
                lambda: self._pending_message is not None or self._done
            )
            if self._done:
                break

            message = self._pending_message
            self._pending_message = None

            @traceable(name=f"Query: {message[:60]}", run_type="chain")
            async def _query(msg: str) -> str:
                response = await workflow.execute_activity(
                    call_openai,
                    OpenAIRequest(model="gpt-4o-mini", input=msg),
                    start_to_close_timeout=timedelta(seconds=60),
                )
                return response.output_text

            self._last_response = await _query(message)

        return "Session ended."
```

With `add_temporal_runs=False`, the trace contains only application logic:

```
Session Apr 03 14:30
  Query: "What's the weather in NYC?"
    Call OpenAI
      openai.responses.create  (auto-traced by wrap_openai)
```

With `add_temporal_runs=True` and the caller wrapping `start_workflow` in `@traceable`:

```
Ask Chatbot                      # @traceable wrapper around client.start_workflow
  StartWorkflow:ChatbotWorkflow
  RunWorkflow:ChatbotWorkflow
    Session Apr 03 14:30
      Query: "What's the weather in NYC?"
        StartActivity:call_openai
        RunActivity:call_openai
          Call OpenAI
            openai.responses.create
```

## Grouping Activity retries under one trace

Because Temporal retries failed Activities and `@traceable` on `@activity.defn` fires per attempt, wrap the Activity call in an outer `@traceable` to group the attempts together:

```python
@traceable(name="Call OpenAI", run_type="llm")
@activity.defn
async def call_openai(...):
    ...

@traceable(name="my_step", run_type="chain")
async def my_step(message: str) -> str:
    return await workflow.execute_activity(
        call_openai,
        ...
    )
```

Result:

```
my_step
  Call OpenAI           # first attempt
    openai.responses.create
  Call OpenAI           # retry
    openai.responses.create
```

## Common mistakes

- **`@traceable` on a `@workflow.defn` class.** Not supported — use `@traceable` inside `@workflow.run` instead.
- **`@activity.defn` on top of `@traceable`.** Wrong order — `@traceable` must be the outer decorator on Activities.
- **Registering the plugin only on the Client.** Register on both Client and every Worker.
- **Positional argument to `LangSmithPlugin`.** The constructor is keyword-only — use `LangSmithPlugin(project_name="...")`.
- **Combining with `temporalio.contrib.opentelemetry` and expecting unified traces.** They are independent integrations; this reference covers LangSmith only.

## Additional Resources

- `references/python/integrations/langgraph.md` - LangGraph + Temporal plugin - enables running LangGraph agents as durable Temporal workflows.
