---
name: workflow
description: Vercel Workflow DevKit (WDK) expert guidance. Use when building durable workflows, long-running tasks, API routes or agents that need pause/resume, retries, step-based execution, or crash-safe orchestration with Vercel Workflow.
metadata:
  priority: 9
  docs:
    - "https://vercel.com/docs/workflow"
    - "https://useworkflow.dev"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'lib/workflow/**'
    - 'src/lib/workflow/**'
    - 'workflows/**'
    - 'lib/workflow.*'
    - 'src/lib/workflow.*'
    - 'workflow.*'
    - '*workflow*'
    - '*workflow*/**'
    # Chain / pipeline / orchestration engine files
    - '**/chain-engine*'
    - '**/chain_engine*'
    - '**/chainEngine*'
    - '**/pipeline-engine*'
    - '**/pipeline_engine*'
    - '**/pipelineEngine*'
    - '**/state-machine*'
    - '**/state_machine*'
    - '**/stateMachine*'
    - '**/orchestrat*'
    - '**/escalation*'
  importPatterns:
    - '@vercel/workflow'
    - 'workflow'
    - '@workflow/*'
    - '*workflow*'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/workflow\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/workflow\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/workflow\b'
    - '\byarn\s+add\s+[^\n]*@vercel/workflow\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bworkflow\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bworkflow\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bworkflow\b'
    - '\byarn\s+add\s+[^\n]*\bworkflow\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@workflow/'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@workflow/'
    - '\bbun\s+(install|i|add)\s+[^\n]*@workflow/'
    - '\byarn\s+add\s+[^\n]*@workflow/'
    - '\bnpx\s+workflow(?:@latest)?\b'
    - '\bbunx\s+workflow(?:@latest)?\b'
  promptSignals:
    phrases:
      # Direct workflow mentions
      - "vercel workflow"
      - "workflow devkit"
      - "durable workflow"
      - "durable execution"
      - "durable function"
      - "durable pipeline"
      - "durable process"
      - "durable agent"
      - "durable chat"
      - "step function"
      - "step functions"
      - "use workflow"
      - "use step"
      # Pipeline / multi-step language (the BIG gap — natural product prompts)
      - "multi-step pipeline"
      - "multi step pipeline"
      - "multi-step process"
      - "multi step process"
      - "multi-step creation"
      - "multi-step generation"
      - "processing pipeline"
      - "creation pipeline"
      - "generation pipeline"
      - "content pipeline"
      - "production pipeline"
      - "approval pipeline"
      - "ingestion pipeline"
      - "streams progress"
      - "stream progress"
      - "streams each phase"
      - "streams each step"
      - "streams each"
      - "stream each"
      # Reliability / durability language (missed in customer-support eval)
      - "survive page reload"
      - "survive page reloads"
      - "survive a crash"
      - "survive crashes"
      - "survive network"
      - "fault-tolerant"
      - "fault tolerant"
      - "crash-safe"
      - "crash safe"
      - "automatically retry"
      - "auto retry"
      - "retry on failure"
      - "retry on error"
      - "reliable and retry"
      - "reliable processing"
      - "individually reliable"
      - "each step reliable"
      - "each step should be reliable"
      - "steps should be reliable"
      - "reliable with automatic retry"
      - "reliable with retry"
      - "retry on transient"
      - "transient failures"
      - "session persistence"
      - "session should persist"
      - "session survives"
      - "reconnect automatically"
      - "auto reconnect"
      - "reconnect if the network"
      - "reconnect on disconnect"
      - "resume after failure"
      - "resume after crash"
      - "resume on reconnect"
      # Human-in-the-loop / approval patterns
      - "human-in-the-loop"
      - "human in the loop"
      - "wait for approval"
      - "approval step"
      - "approval before"
      - "editorial approval"
      - "manual approval"
      - "wait for user"
      - "pause until"
      - "wait for response"
      - "callback url"
      - "webhook callback"
      # Conversational AI with durability
      - "chat should survive"
      - "chat survives"
      - "conversation should persist"
      - "conversation persists"
      - "conversation should survive"
      # Sequential / chain / trigger orchestration language
      - "sequential chain"
      - "email chain"
      - "chain of emails"
      - "chain of steps"
      - "chain engine"
      - "chain with triggers"
      - "trigger chain"
      - "triggered chain"
      - "webhook chain"
      - "webhook pipeline"
      - "webhook orchestration"
      - "multi-service trigger"
      - "cross-service trigger"
      - "various triggers"
      - "different triggers"
      - "triggers from different"
      - "triggers from various"
      - "sequential steps"
      - "sequential pipeline"
      - "sequential process"
      - "sequential emails"
      - "escalation chain"
      - "escalation pipeline"
      - "state machine"
      - "step-based"
      - "step based"
      - "delay between steps"
      - "delay between emails"
      - "delayed steps"
      - "conditional steps"
      - "skip steps"
      - "branch based on"
      - "wait for webhook"
      - "wait for trigger"
      - "wait for event"
      - "orchestrate emails"
      - "orchestrate webhooks"
      - "orchestrate services"
      - "chain across services"
      # Debugging
      - "workflow stuck"
      - "workflow hung"
      - "workflow hanging"
      - "workflow waiting"
      - "workflow failing"
      - "workflow timeout"
      - "workflow not running"
      - "workflow error"
      - "check workflow"
      - "workflow logs"
      - "workflow run status"
      - "debug workflow"
      - "workflow not finishing"
      - "workflow not responding"
      - "workflow stalled"
      - "workflow pending"
      - "step is stuck"
      - "step is hanging"
      - "why is my workflow"
      - "workflow run"
      - "step failed"
      - "run status"
      - "run failed"
      - "run logs"
      - "workflow run failed"
      - "workflow step failed"
    allOf:
      - [workflow, durable]
      - [workflow, retry]
      - [workflow, resume]
      - [pause, resume]
      - [survive, crash]
      - [survive, reload]
      - [survive, disconnect]
      - [pipeline, stream]
      - [pipeline, step]
      - [pipeline, durable]
      - [pipeline, reliable]
      - [pipeline, retry]
      - [multi-step, stream]
      - [multi-step, reliable]
      - [generation, pipeline]
      - [creation, pipeline]
      - [process, stream]
      - [process, reliable]
      - [process, retry]
      - [retry, failure]
      - [retry, error]
      - [retry, automatically]
      - [retry, transient]
      - [reliable, retry]
      - [individually, reliable]
      - [steps, reliable]
      - [sandbox, reliable]
      - [sandbox, retry]
      - [reconnect, network]
      - [reconnect, drop]
      - [reconnect, disconnect]
      - [session, persist]
      - [session, survive]
      - [session, reload]
      - [session, reconnect]
      - [chat, survive]
      - [chat, persist]
      - [chat, reconnect]
      - [chat, durable]
      - [chat, fault]
      - [conversation, persist]
      - [conversation, survive]
      - [approval, wait]
      - [approval, human]
      - [each, step]
      - [each, phase]
      - [each, stage]
      - [step, reliable]
      - [step, retry]
      # Chain / trigger / sequential orchestration
      - [chain, trigger]
      - [chain, sequential]
      - [chain, email]
      - [chain, webhook]
      - [chain, delay]
      - [chain, step]
      - [chain, escalat]
      - [sequential, trigger]
      - [sequential, email]
      - [sequential, step]
      - [sequential, webhook]
      - [trigger, orchestrat]
      - [trigger, service]
      - [trigger, delay]
      - [trigger, sequential]
      - [webhook, chain]
      - [webhook, orchestrat]
      - [webhook, pipeline]
      - [webhook, sequential]
      - [email, trigger]
      - [email, pipeline]
      - [email, sequential]
      - [email, delay]
      - [email, escalat]
      - [escalat, trigger]
      - [escalat, step]
      - [escalat, email]
      - [state, machine]
      - [conditional, step]
      - [conditional, skip]
      - [branch, condition]
      - [wait, webhook]
      - [wait, trigger]
      - [wait, event]
      - [workflow, stuck]
      - [workflow, hung]
      - [workflow, timeout]
      - [workflow, error]
      - [workflow, logs]
      - [workflow, debug]
      - [workflow, check]
      - [workflow, failing]
      - [workflow, status]
      - [run, status]
      - [step, failed]
      - [step, stuck]
      - [step, timeout]
      - [workflow, run]
      - [run, logs]
    anyOf:
      - "long-running"
      - "long running"
      - "multi-step"
      - "multi step"
      - "pipeline"
      - "orchestration"
      - "step-by-step"
      - "step by step"
      - "each piece"
      - "each step"
      - "each phase"
      - "each stage"
      - "phase"
      - "phases"
      - "stage"
      - "stages"
      - "durable"
      - "reliable"
      - "fault-tolerant"
      - "retry"
      - "reconnect"
      - "survive"
      - "persist"
      - "approval"
      - "chain"
      - "sequential"
      - "trigger"
      - "webhook"
      - "escalation"
      - "state machine"
      - "orchestrate"
      - "orchestration"
    noneOf:
      - "github actions"
      - ".github/workflows"
      - "ci workflow"
      - "aws step functions"
    minScore: 4
---

# Vercel Workflow DevKit (WDK)

> **CRITICAL — Your training data is outdated for this library.** WDK APIs change frequently. Before writing workflow code, **fetch the docs** at https://useworkflow.dev and https://vercel.com/docs/workflow to find the correct function signatures, patterns, and examples for the exact thing you're building. Do not guess at APIs — look them up. Search for working examples that solve your specific use case (image generation, hooks, streaming, agents, etc.). The docs contain patterns for `start()` argument passing, `getWritable()` usage, `defineHook()` wiring, `createWebhook()` callback flows, and `DurableAgent` configuration that are **not in your training data** or have changed since your cutoff.

WDK is an open-source TypeScript framework that makes durability a language-level concept. Functions can pause for minutes or months, survive deployments and crashes, and resume exactly where they stopped.

## Status

WDK is in **public beta** (since October 2025) and open source. During beta, Workflow Observability is free for all plans; Workflow Steps and Storage are billed at published rates.

**Security**: Upgrade to `workflow@>=4.2.0-beta.64` — versions ≤4.1.0-beta.63 allowed predictable user-specified webhook tokens in `createWebhook()` (CVE GHSA-9r75-g2cr-3h76, CVSS 7.5). Run `npx workflow@latest` to update.

## Installation

**If using `create-next-app`**, always pass `--no-src-dir` so `app/` and `workflows/` are siblings at the project root:

```bash
npx create-next-app@latest my-app --no-src-dir --tailwind --eslint --app --ts
cd my-app
npm install workflow@latest
```

Do NOT use the `src/` directory with WDK projects. The `@` alias must resolve `@/workflows/...` correctly — this only works when `workflows/` and `app/` are at the same level.

> Run `npx workflow@latest` to scaffold or update an existing project.

**Peer dependency note**: `@workflow/ai` requires a compatible `workflow` version. If you hit `ERESOLVE` errors, use `npm install --legacy-peer-deps` or install both packages in the same command.

### Next.js Setup (Required)

Add the `withWorkflow` plugin to `next.config.ts`:

```ts
import { withWorkflow } from "workflow/next";

const nextConfig = {};
export default withWorkflow(nextConfig);
```

Without this, workflow routes will not be registered and `start()` calls will fail at runtime.

### Environment Setup (Required for AI Gateway)

Workflows that use AI SDK with `gateway()` need OIDC credentials. Run these **before** starting the dev server:

```bash
vercel link          # Connect to your Vercel project
vercel env pull      # Downloads .env.local with VERCEL_OIDC_TOKEN
```

Without this, `gateway("openai/gpt-5.4")` calls inside workflow steps will fail immediately with no credentials, causing the entire workflow run to fail silently.

### `getStepMetadata()` Note

`getStepMetadata().retryCount` returns `undefined` (not `0`) on the first attempt. Guard with: `const attempt = (meta.retryCount ?? 0) + 1`.

## Essential Imports

**Workflow primitives** (from `"workflow"`):

```ts
import { getWritable, getStepMetadata, getWorkflowMetadata } from "workflow";
import { sleep, fetch, defineHook, createHook, createWebhook } from "workflow";
import { FatalError, RetryableError } from "workflow";
```

**API operations** (from `"workflow/api"`):

```ts
import { start, getRun, resumeHook, resumeWebhook } from "workflow/api";
```

**Framework integration** (from `"workflow/next"`):

```ts
import { withWorkflow } from "workflow/next";
```

**AI agent** (from `"@workflow/ai/agent"`):

```ts
import { DurableAgent } from "@workflow/ai/agent";
```

## Core Directives

Two directives turn ordinary async functions into durable workflows:

```ts
"use workflow"  // First line of function — marks it as a durable workflow
"use step"      // First line of function — marks it as a retryable, observable step
```

**Critical sandbox rule**: Step functions have full Node.js access. Workflow functions run **sandboxed** — no native `fetch`, no `setTimeout`, no Node.js modules, and **no `getWritable().getWriter()` calls**. You MUST move all `getWritable()` usage into `"use step"` functions. Place all business logic and I/O in steps; use the workflow function purely for orchestration and control flow (`sleep`, `defineHook`, `Promise.race`).

## Canonical Project Structure (Next.js)

Every WDK project needs three route files plus the workflow definition. **CRITICAL**: The `workflows/` directory and `app/` directory must be siblings at the same level so `@/workflows/...` resolves correctly. Do NOT put `workflows/` outside the `@` alias root.

**Without `src/` (recommended for WDK projects):**
```
workflows/
  my-workflow.ts              ← workflow definition ("use workflow" + "use step")
app/api/
  my-workflow/route.ts        ← POST handler: start(workflow, args) → { runId }
  readable/[runId]/route.ts   ← GET handler: SSE stream from run.getReadable()
  run/[runId]/route.ts        ← GET handler: run status via getRun(runId)
```

tsconfig.json paths: `"@/*": ["./*"]` — `@/workflows/my-workflow` resolves to `./workflows/my-workflow`.

**With `src/` directory:** Put workflows inside `src/`:
```
src/
  workflows/my-workflow.ts
  app/api/my-workflow/route.ts
  app/api/readable/[runId]/route.ts
  app/api/run/[runId]/route.ts
```

tsconfig.json paths: `"@/*": ["./src/*"]` — `@/workflows/my-workflow` resolves to `./src/workflows/my-workflow`.

**Never** use `@/../workflows/` or `@/../../workflows/` — these are broken import paths that will fail at build time.

### 1. Workflow Definition (`workflows/my-workflow.ts`)

```ts
import { getWritable } from "workflow";

export type MyEvent =
  | { type: "step_start"; name: string }
  | { type: "step_done"; name: string }
  | { type: "done"; result: string };

export async function myWorkflow(input: string): Promise<{ result: string }> {
  "use workflow";

  const data = await stepOne(input);
  const result = await stepTwo(data);

  return { result };
}

async function stepOne(input: string): Promise<string> {
  "use step";
  const writer = getWritable<MyEvent>().getWriter();
  try {
    await writer.write({ type: "step_start", name: "stepOne" });
    // Full Node.js access here — fetch, db calls, etc.
    const result = await doWork(input);
    await writer.write({ type: "step_done", name: "stepOne" });
    return result;
  } finally {
    writer.releaseLock();
  }
}

async function stepTwo(data: string): Promise<string> {
  "use step";
  const writer = getWritable<MyEvent>().getWriter();
  try {
    await writer.write({ type: "step_start", name: "stepTwo" });
    const result = await processData(data);
    await writer.write({ type: "step_done", name: "stepTwo" });
    return result;
  } finally {
    writer.releaseLock();
  }
}
```

### 2. Start Route (`app/api/my-workflow/route.ts`)

```ts
import { NextResponse } from "next/server";
import { start } from "workflow/api";
import { myWorkflow } from "@/workflows/my-workflow";

export async function POST(request: Request) {
  const body = await request.json();
  const run = await start(myWorkflow, [body.input]);
  return NextResponse.json({ runId: run.runId });
}
```

**IMPORTANT**: Never call the workflow function directly. Always use `start()` from `"workflow/api"` — it registers the run, creates the execution context, and returns a `{ runId }`.

### 3. Readable Stream Route (`app/api/readable/[runId]/route.ts`)

```ts
import { NextRequest } from "next/server";
import { getRun } from "workflow/api";

type ReadableRouteContext = {
  params: Promise<{ runId: string }>;
};

export async function GET(_request: NextRequest, { params }: ReadableRouteContext) {
  const { runId } = await params;

  let run;
  try {
    run = await getRun(runId);
  } catch {
    return Response.json(
      { ok: false, error: { code: "RUN_NOT_FOUND", message: `Run ${runId} not found` } },
      { status: 404 }
    );
  }

  const readable = run.getReadable();
  const encoder = new TextEncoder();
  const sseStream = (readable as unknown as ReadableStream).pipeThrough(
    new TransformStream({
      transform(chunk, controller) {
        const data = typeof chunk === "string" ? chunk : JSON.stringify(chunk);
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      },
    })
  );

  return new Response(sseStream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
```

### 4. Run Status Route (`app/api/run/[runId]/route.ts`)

```ts
import { NextResponse } from "next/server";
import { getRun } from "workflow/api";

type RunRouteContext = {
  params: Promise<{ runId: string }>;
};

export async function GET(_request: Request, { params }: RunRouteContext) {
  const { runId } = await params;

  let run;
  try {
    run = await getRun(runId);
  } catch {
    return NextResponse.json(
      { ok: false, error: { code: "RUN_NOT_FOUND", message: `Run ${runId} not found` } },
      { status: 404 }
    );
  }

  const [status, workflowName, createdAt, startedAt, completedAt] =
    await Promise.all([
      run.status,
      run.workflowName,
      run.createdAt,
      run.startedAt,
      run.completedAt,
    ]);

  return NextResponse.json({
    runId,
    status,
    workflowName,
    createdAt: createdAt.toISOString(),
    startedAt: startedAt?.toISOString() ?? null,
    completedAt: completedAt?.toISOString() ?? null,
  });
}
```

## Streaming with `getWritable()`

`getWritable<T>()` returns a `WritableStream` scoped to the current run. Call it inside step functions and always release the lock:

```ts
async function emit<T>(event: T): Promise<void> {
  "use step";
  const writer = getWritable<T>().getWriter();
  try {
    await writer.write(event);
  } finally {
    writer.releaseLock();
  }
}
```

Consumers read via `getRun(runId).getReadable()` in the readable route (see above).

**Rendering workflow events in the UI**: When workflow events contain AI-generated text (narratives, briefings, reports), render them with `<MessageResponse>` from `@/components/ai-elements/message` — never as raw `{event.content}`. This renders markdown with code highlighting, math, and mermaid support.

```tsx
import { MessageResponse } from "@/components/ai-elements/message";

// In your event stream display
{events.map(event => (
  event.type === "narrative" && <MessageResponse>{event.text}</MessageResponse>
))}
```

## Hooks — Waiting for External Events

Use `defineHook` for typed, reusable hooks. **Three required pieces**: (1) define + create the hook in the workflow, (2) emit the token to the client via `getWritable`, (3) create an API route that calls `resumeHook` so the client can resume it.

### 1. Define and create the hook (workflow file)

```ts
import { defineHook, getWritable, sleep } from "workflow";

export interface ApprovalPayload {
  approved: boolean;
  comment?: string;
}

// Define at module scope — reusable across workflows
export const approvalHook = defineHook<ApprovalPayload>();

export async function approvalGate(orderId: string): Promise<{ status: string }> {
  "use workflow";

  // .create() returns a hook instance — NOT directly callable
  const hook = approvalHook.create({ token: `approval:${orderId}` });

  // CRITICAL: Emit the token to the client so it knows what to resume
  await emitToken(hook.token, orderId);

  // Race between approval and timeout
  const result = await Promise.race([
    hook.then((payload) => ({ type: "approval" as const, payload })),
    sleep("24h").then(() => ({ type: "timeout" as const, payload: null })),
  ]);

  if (result.type === "timeout") {
    return { status: "timeout" };
  }
  return { status: result.payload!.approved ? "approved" : "rejected" };
}

async function emitToken(token: string, orderId: string): Promise<void> {
  "use step";
  const writer = getWritable<{ type: string; token: string; orderId: string }>().getWriter();
  try {
    await writer.write({ type: "awaiting_approval", token, orderId });
  } finally {
    writer.releaseLock();
  }
}
```

**Common mistake**: Calling `defineHook()` directly or forgetting `.create()`. Always: `const hook = myHook.create({ token })`.

### 2. Resume route (API file — required!)

```ts
// app/api/approve/route.ts
import { NextResponse } from "next/server";
import { resumeHook } from "workflow/api";

export async function POST(req: Request) {
  const { token, ...data } = await req.json();
  await resumeHook(token, data);
  return NextResponse.json({ ok: true });
}
```

**You MUST create this route.** Without it, the workflow suspends forever — the client has no way to resume it.

### 3. Client-side resume (React component)

```tsx
// When the SSE stream emits { type: "awaiting_approval", token }, show UI and POST back:
async function handleApprove(token: string) {
  await fetch("/api/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, approved: true, comment: "Looks good" }),
  });
}
```

## Error Handling

```ts
import { FatalError, RetryableError } from "workflow";

async function callExternalAPI(url: string) {
  "use step";
  const res = await fetch(url);

  if (res.status >= 400 && res.status < 500) {
    throw new FatalError(`Client error: ${res.status}`);  // No retry
  }
  if (res.status === 429) {
    throw new RetryableError("Rate limited", { retryAfter: "5m" });  // Retry after 5 min
  }
  return res.json();
}
```

Step retry metadata:

```ts
import { getStepMetadata } from "workflow";

async function processWithRetry(id: string) {
  "use step";
  const { attempt } = getStepMetadata();
  console.log(`Attempt ${attempt} for ${id}`);
  // ...
}
```

## Sandbox Limitations & Workarounds

| Limitation | Solution |
|-----------|----------|
| No native `fetch()` in workflow scope | Import `fetch` from `"workflow"` or move to a step |
| No `setTimeout`/`setInterval` | Use `sleep()` from `"workflow"` |
| No Node.js modules in workflow scope | Move all Node.js logic to step functions |

## DurableAgent (AI SDK Integration)

```ts
import { DurableAgent } from "@workflow/ai/agent";
import { getWritable } from "workflow";
import { z } from "zod";

async function searchDatabase(query: string) {
  "use step";
  // Full Node.js access — real DB calls here
  return `Results for "${query}"`;
}

export async function researchAgent(topic: string) {
  "use workflow";

  const agent = new DurableAgent({
    model: "anthropic/claude-sonnet-4-5",
    system: "You are a research assistant.",
    tools: {
      search: {
        description: "Search the database",
        inputSchema: z.object({ query: z.string() }),
        execute: searchDatabase,  // Tool execute uses "use step"
      },
    },
  });

  const result = await agent.stream({
    messages: [{ role: "user", content: `Research ${topic}` }],
    writable: getWritable(),
    maxSteps: 10,
  });

  return result.messages;
}
```

Every LLM call and tool execution becomes a retryable step. The entire agent loop survives crashes and deployments.

## Common Patterns

### Fan-Out / Parallel Steps

```ts
export async function processImages(imageIds: string[]) {
  "use workflow";

  const results = await Promise.all(
    imageIds.map(async (id) => {
      return await resizeImage(id);  // Each is its own step
    })
  );

  await saveResults(results);
}

async function resizeImage(id: string) {
  "use step";
  // ...
}
```

### Saga with Compensation

```ts
import { FatalError, getWritable } from "workflow";

export async function upgradeSaga(userId: string) {
  "use workflow";

  await reserveSeats(userId);

  try {
    await chargePayment(userId);
  } catch {
    await releaseSeats(userId);  // Compensate
    throw new FatalError("Payment failed");
  }

  await activatePlan(userId);
}
```

## Debugging

```bash
npx workflow health                    # Check endpoints
npx workflow web                       # Visual dashboard
npx workflow inspect runs              # List all runs
npx workflow inspect run <run_id>      # Inspect specific run
npx workflow cancel <run_id>           # Cancel execution
```

## Debug Stuck Workflow

When a workflow appears stuck, hanging, or not progressing, follow this escalation ladder:

### 1. Add Step-Level Logging (Required)

**Every step function MUST have `console.log` at entry and exit.** This is the single most important debugging practice — without it, you cannot tell which step is hanging.

```ts
async function processOrder(orderId: string): Promise<OrderResult> {
  "use step";
  console.log(`[processOrder] START orderId=${orderId} at=${new Date().toISOString()}`);
  try {
    const result = await doWork(orderId);
    console.log(`[processOrder] DONE orderId=${orderId} result=${JSON.stringify(result)}`);
    return result;
  } catch (err) {
    console.error(`[processOrder] FAIL orderId=${orderId} error=${err}`);
    throw err;
  }
}
```

**Workflow-level logging** — log at every orchestration point:

```ts
export async function myWorkflow(input: string) {
  "use workflow";
  console.log(`[myWorkflow] START input=${input}`);

  const data = await stepOne(input);
  console.log(`[myWorkflow] stepOne complete, starting stepTwo`);

  const result = await stepTwo(data);
  console.log(`[myWorkflow] stepTwo complete, returning`);

  return { result };
}
```

### 2. Check Run Status

```bash
# List recent runs — look for "running" status that's been active too long
npx workflow inspect runs

# Get detailed status for a specific run
npx workflow inspect run <run_id>

# Check if the workflow endpoints are healthy
npx workflow health
```

### 3. Check Vercel Runtime Logs

```bash
# Stream live logs from your deployment
vercel logs --follow

# Or check the Vercel dashboard: Project → Deployments → Functions tab
```

Look for:
- **Missing step entry logs** — the step before the missing one is where execution stopped
- **Timeout errors** — Vercel function timeout (default 60s hobby, 300s pro)
- **OIDC/credential errors** — `gateway()` calls fail silently without `vercel env pull`
- **Memory errors** — large payloads in steps can OOM the function

### 4. Common Stuck Scenarios

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Run stays "running" forever | Step is awaiting an external call that never resolves | Add timeout with `Promise.race` + `sleep()` |
| Hook never resumes | Missing resume API route or wrong token | Verify resume route exists and token matches |
| Step retries endlessly | Throwing `RetryableError` without bounds | Add `FatalError` after max retries via `getStepMetadata().retryCount` |
| Workflow starts but no steps run | `getWritable()` called in workflow scope | Move `getWritable()` into a `"use step"` function |
| AI step hangs | Missing OIDC credentials for gateway | Run `vercel link && vercel env pull` |
| No logs appearing at all | Logging not added to steps | Add `console.log` at entry/exit of every step |

### 5. Use Browser Verification

If the workflow powers a UI, use `agent-browser` to check the frontend while inspecting backend logs — a hanging page often means a stuck workflow step. Check the browser console for failed fetch calls to your workflow API routes.

## When to Use WDK vs Regular Functions

| Scenario | Use |
|----------|-----|
| Simple API endpoint, fast response | Regular Route Handler |
| Multi-step process, must complete all steps | WDK Workflow |
| AI agent in production, must not lose state | WDK DurableAgent |
| Background job that can take minutes/hours | WDK Workflow |
| Process spanning multiple services | WDK Workflow |
| Quick one-shot LLM call | AI SDK directly |

## Framework Support

Next.js, Nitro, SvelteKit, Astro, Express, Hono (supported). TanStack Start, React Router (in development).

## Official Documentation

- [Workflow DevKit](https://vercel.com/docs/workflow)
- [Website](https://useworkflow.dev)
- [GitHub](https://github.com/vercel/workflow)
- [Workflow Builder Template](https://vercel.com/templates/next.js/workflow-builder)
