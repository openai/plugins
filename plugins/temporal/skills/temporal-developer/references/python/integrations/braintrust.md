# Temporal Braintrust Integration (Python)

## Overview

[Braintrust](https://braintrust.dev) is an LLM observability and prompt-management platform. The Temporal Python SDK integrates with it through `braintrust.contrib.temporal.BraintrustPlugin`, which traces every Workflow and Activity as a span in Braintrust and links client-initiated spans to the Workflows they start.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For Python AI patterns (Pydantic data converter, disabling client-side LLM retries, generic LLM Activity shape) read `references/python/ai-patterns.md`. For conceptual LLM patterns shared across SDKs read `references/core/ai-patterns.md`.

## Prerequisites

- An existing Temporal Python development environment as described in `references/python/python.md`.

## Install

```bash
uv add "braintrust[temporal]"
```

## Initialize the logger before the Client or Worker

The Braintrust logger must be initialized **before** the Temporal Client and Worker are constructed so that spans connect correctly.

```python
import os
from braintrust import init_logger

init_logger(project=os.environ.get("BRAINTRUST_PROJECT", "my-project"))
```

`init_logger` takes a `project` argument that names the Braintrust project traces are written to.

## Register `BraintrustPlugin` on the Client and the Worker

Register `BraintrustPlugin` on **both** the Client and every Worker. The Worker registration produces Workflow/Activity spans; the Client registration propagates span context so client-side spans link to the Workflow they start.

Client:

```python
from temporalio.client import Client
from braintrust.contrib.temporal import BraintrustPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[BraintrustPlugin()],
)
```

Worker:

```python
from braintrust.contrib.temporal import BraintrustPlugin
from temporalio.worker import Worker

worker = Worker(
    client,
    task_queue="my-task-queue",
    workflows=[MyWorkflow],
    activities=[my_activity],
    plugins=[BraintrustPlugin()],
)
```

## API credentials

The Worker process needs `BRAINTRUST_API_KEY` in its environment. The Client process that starts Workflow Executions does **not** need the Braintrust API key.

```bash
export BRAINTRUST_API_KEY="your-api-key"
python worker.py
```

## Trace LLM calls with `wrap_openai`

Wrap the OpenAI client with `braintrust.wrap_openai` so every chat/completion call is captured as a span with inputs, outputs, token counts, and latency. Pass `max_retries=0` so Temporal — not the OpenAI client — owns retries.

```python
from braintrust import wrap_openai
from openai import AsyncOpenAI
from temporalio import activity

@activity.defn
async def invoke_model(prompt: str) -> str:
    client = wrap_openai(AsyncOpenAI(max_retries=0))

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
```

The resulting trace nests the OpenAI span under the Activity span, which sits under the Workflow span, which sits under the client-side span:

```
my-workflow-request (client span)
└── temporal.workflow.MyWorkflow
    └── temporal.activity.invoke_model
        └── Chat Completion (gpt-4o)
```

## Add custom spans with `start_span`

Use `braintrust.start_span` from client code to capture application-level context (the user query, the final result) alongside the Workflow/Activity spans the plugin produces.

```python
import uuid
from braintrust import start_span

async def run_research(query: str):
    with start_span(name="research-request", type="task") as span:
        span.log(input={"query": query})

        result = await client.execute_workflow(
            ResearchWorkflow.run,
            query,
            id=f"research-{uuid.uuid4()}",
            task_queue="research-task-queue",
        )

        span.log(output={"result": result})
        return result
```

## Manage prompts with `load_prompt`

`braintrust.load_prompt(project=..., slug=...)` fetches a prompt managed in the Braintrust UI, so prompt edits go live without redeploying Workflow or Activity code. Call it from an Activity (model calls live in Activities), then call `prompt.build()` to get the prompt configuration; extract the message you need before invoking the LLM.

```python
import os
import braintrust
from braintrust import wrap_openai
from openai import AsyncOpenAI
from temporalio import activity

@activity.defn
async def invoke_model(prompt_slug: str, user_input: str) -> str:
    prompt = braintrust.load_prompt(
        project=os.environ.get("BRAINTRUST_PROJECT", "my-project"),
        slug=prompt_slug,
    )

    built = prompt.build()

    system_content = "You are a helpful assistant."
    for msg in built.get("messages", []):
        if msg.get("role") == "system" and msg.get("content"):
            system_content = msg["content"]
            break

    client = wrap_openai(AsyncOpenAI(max_retries=0))

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input},
        ],
    )

    return response.choices[0].message.content
```

### Fallback prompt for resilience

Wrap `load_prompt` in a `try`/`except` and fall back to a hardcoded prompt so the Activity still runs if Braintrust is unreachable.

```python
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

try:
    prompt = braintrust.load_prompt(project="my-project", slug="my-prompt")
    system_content = extract_system_message(prompt.build())
except Exception as e:
    activity.logger.warning(f"Failed to load prompt: {e}. Using fallback.")
    system_content = DEFAULT_SYSTEM_PROMPT
```

## Common mistakes

- **Initializing the Braintrust logger after constructing the Client or Worker.** Call `init_logger(...)` first; otherwise spans don't connect to the Worker process.
- **Registering `BraintrustPlugin` on only the Worker (or only the Client).** Register on both — the Client registration is what links client-side spans to Workflow executions.
- **Forgetting `max_retries=0` on the wrapped OpenAI client.** Temporal owns retries; leaving the OpenAI client's built-in retries on duplicates work and obscures retry counts in traces.
- **Calling `load_prompt` from inside a Workflow.** Prompt loading is an external I/O call; keep it in an Activity.
- **Setting `BRAINTRUST_API_KEY` only on the Client process.** The Worker is what calls Braintrust; the Client doesn't need the key.

## Additional Resources

- `references/python/ai-patterns.md` — Python LLM patterns (Pydantic, retry discipline, generic LLM Activity shape).
- `references/core/ai-patterns.md` — Conceptual LLM patterns shared across SDKs.
- [Deep research sample](https://github.com/braintrustdata/braintrust-cookbook/blob/main/examples/TemporalDeepResearch/TemporalDeepResearch.mdx) — end-to-end agent showing `BraintrustPlugin`, `wrap_openai`, `start_span`, and `load_prompt`.
