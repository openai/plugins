# Temporal LangGraph Plugin (Python)

## Overview

The `LangGraphPlugin` runs [LangGraph](https://www.langchain.com/langgraph) nodes and tasks as Temporal Activities, giving LangGraph-orchestrated AI workflows durable execution, automatic retries, and timeouts.

Both LangGraph APIs are supported:

- **Graph API** (`StateGraph`).
- **Functional API** (`@entrypoint` / `@task`).

The plugin ships in the Temporal Python SDK at `temporalio.contrib.langgraph`.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For general Temporal Python AI/LLM patterns (Pydantic data converter, LLM Activity design, retry classification, multi-agent orchestration), read `references/python/ai-patterns.md` first; for language-agnostic patterns, read `references/core/ai-patterns.md`.

## Installation

```bash
uv add temporalio[langgraph]
```

This pulls in `langgraph` as well for you.

## Public API

`temporalio.contrib.langgraph` exports four symbols:

- `LangGraphPlugin` — the plugin class. Pass to both the `Client` and the `Worker`.
- `graph(name, cache=...)` — Workflow-side accessor that returns a registered `StateGraph` by name.
- `entrypoint(name, cache=...)` — Workflow-side accessor that returns a registered Functional-API `Pregel`.
- `cache()` — accessor for the per-workflow LangGraph cache.

## Build the plugin

Construct the plugin once at startup. The constructor signature is:

```python
LangGraphPlugin(
    graphs: dict[str, StateGraph] | None = None,
    entrypoints: dict[str, Pregel] | None = None,
    tasks: list | None = None,
    activity_options: dict[str, dict[str, Any]] | None = None,
    default_activity_options: dict[str, Any] | None = None,
)
```

### Graph API

Register your `StateGraph` instances in `graphs=`, keyed by a name your workflow code will look up with `graph(name)`:

```python
from langgraph.graph import StateGraph
from temporalio.contrib.langgraph import LangGraphPlugin

g = StateGraph(State)
g.add_node("my_node", my_node, metadata={"execute_in": "activity"})

plugin = LangGraphPlugin(graphs={"my-graph": g})
```

### Functional API

Pass entrypoints in `entrypoints=`, tasks in `tasks=`, and per-task activity options in `activity_options=` (keyed by task function name):

```python
from temporalio.contrib.langgraph import LangGraphPlugin

plugin = LangGraphPlugin(
    entrypoints={"my_entrypoint": my_entrypoint},
    tasks=[my_task],
    activity_options={"my_task": {"execute_in": "activity"}},
)
```

## Register the plugin on Client and Worker

Pass the same `LangGraphPlugin` instance to both the Temporal Client and the Worker via their `plugins=` parameter, like any other Temporal Python SDK plugin:

```python
from temporalio.client import Client
from temporalio.worker import Worker

client = await Client.connect("localhost:7233", plugins=[plugin])

worker = Worker(
    client,
    task_queue="my-task-queue",
    workflows=[MyWorkflow],
    plugins=[plugin],
)
await worker.run()
```

## Execution location — required per node and per task

Every node (Graph API) and every task (Functional API) must declare `execute_in`, set to either `"activity"` or `"workflow"`:

```python
# Graph API — set via node metadata
graph.add_node("my_node", my_node, metadata={"execute_in": "activity"})
graph.add_node("tool_node", tool_node, metadata={"execute_in": "workflow"})

# Functional API — set via activity_options on the plugin
plugin = LangGraphPlugin(
    tasks=[my_task, tool_task],
    activity_options={
        "my_task": {"execute_in": "activity"},
        "tool_task": {"execute_in": "workflow"},
    },
)
```

- Use `"activity"` for I/O, LLM calls, or anything that needs Temporal retries and timeouts.
- Use `"workflow"` for logic that should run on the workflow thread: purely deterministic logic, or logic which orchestrates Temporal durable primitives within the workflow thread (e.g. multiple activity calls, wait conditions, etc.)
- **`execute_in` cannot be defaulted in `default_activity_options`** — it must be specified individually per node or task.

## Activity options

For nodes or tasks with `execute_in: "activity"`, you can pass parameters that flow through to [`workflow.execute_activity()`](https://python.temporal.io/temporalio.workflow.html#execute_activity): `start_to_close_timeout`, `retry_policy`, `schedule_to_close_timeout`, `heartbeat_timeout`.

### Graph API — options in node metadata

```python
from datetime import timedelta
from temporalio.common import RetryPolicy

g = StateGraph(State)
g.add_node("my_node", my_node, metadata={
    "execute_in": "activity",
    "start_to_close_timeout": timedelta(seconds=30),
    "retry_policy": RetryPolicy(maximum_attempts=3),
})
```

### Functional API — options keyed by task name

```python
from datetime import timedelta
from temporalio.common import RetryPolicy
from temporalio.contrib.langgraph import LangGraphPlugin

plugin = LangGraphPlugin(
    entrypoints={"my_entrypoint": my_entrypoint},
    tasks=[my_task],
    activity_options={
        "my_task": {
            "execute_in": "activity",
            "start_to_close_timeout": timedelta(seconds=30),
            "retry_policy": RetryPolicy(maximum_attempts=3),
        },
    },
)
```

## Run a graph from a Workflow

Inside the Workflow, get the registered graph by name with `graph(name)`, compile it, then `ainvoke` (or `astream`) as usual. If the graph requires a checkpointer (for example, when using interrupts), use `InMemorySaver` — Temporal supplies durability, so third-party checkpointers like PostgreSQL or Redis are not needed:

```python
import typing
import langgraph.checkpoint.memory
from temporalio import workflow
from temporalio.contrib.langgraph import graph

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, input: str) -> typing.Any:
        g = graph("my-graph").compile(
            checkpointer=langgraph.checkpoint.memory.InMemorySaver(),
        )
        return await g.ainvoke({"input": input})
```

Use `entrypoint(name)` instead of `graph(name)` for Functional-API entrypoints.

## Runtime context

LangGraph's run-scoped context (`context_schema`) is reconstructed on the Activity side, so a node can read and write `runtime.context` even when the node runs as an Activity:

```python
from langgraph.runtime import Runtime
from typing_extensions import TypedDict
from temporalio.contrib.langgraph import graph

class Context(TypedDict):
    user_id: str

async def my_node(state: State, runtime: Runtime[Context]) -> dict:
    return {"user": runtime.context["user_id"]}

# In the Workflow:
g = graph("my-graph").compile()
await g.ainvoke({...}, context=Context(user_id="alice"))
```

The `context` object must be serializable by the configured Temporal payload converter, since it crosses the Activity boundary.  If your context uses Pydantic models, configure `pydantic_data_converter` — see `references/python/ai-patterns.md`.

## Tracing

For LangSmith tracing of LangGraph nodes and Temporal Activities together, use the Temporal LangSmith plugin (`references/python/integrations/langsmith.md`).

## Hard constraints

- **`execute_in` is mandatory on every node and task.** Set it to `"activity"` or `"workflow"` per node/task — it cannot be set in `default_activity_options`.
- **Use `InMemorySaver` as your checkpointer.** Temporal handles durability; do not configure PostgreSQL, Redis, or other third-party checkpointers.
- **LangGraph `Store` is not supported across the Activity boundary.** If you pass a `Store` (e.g. `InMemoryStore` via `graph.compile(store=...)` or `@entrypoint(store=...)`), the plugin logs a warning on first use and `runtime.store` is `None` inside nodes. Use Workflow state for per-run memory, or an external database (Postgres/Redis/etc.) configured on each worker for shared memory across runs.
- **Context objects must be serializable by the configured Temporal payload converter,** since they cross the Activity boundary.

## Resources

- `references/python/ai-patterns.md` — Python AI/LLM patterns (Pydantic data converter, LLM Activity design, retry/error classification).
- `references/core/ai-patterns.md` — language-agnostic AI/LLM patterns.
- `references/python/integrations/langsmith.md` - Companion LangSmith plugin.
