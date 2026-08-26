# Temporal Mastra Integration (TypeScript)

## Overview

[Mastra](https://mastra.ai/docs) is a TypeScript agent / workflow framework. The `@mastra/temporal` package transforms Mastra workflow and step definitions into Temporal Workflows and Activities at build time, then auto-registers them on a Temporal Worker via the `MastraPlugin`. Each `createStep` becomes a Temporal Activity and each `createWorkflow` becomes a Temporal Workflow.

Mastra appears on the Temporal TypeScript integrations page as the "Mastra | Agent framework" row, which links out to the upstream Mastra deployment guide.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview. The upstream `@mastra/temporal` package is also flagged as "experimental and not ready for production use"; the API may change between releases.

For Temporal TypeScript SDK fundamentals (Worker, Workflow, Activity, Task Queue, replay), see `references/typescript/typescript.md` and `references/typescript/determinism.md`.

## Install

```bash
npm install @mastra/temporal@latest @temporalio/client @temporalio/worker @temporalio/envconfig
```

`pnpm`, `yarn`, and `bun` equivalents are all supported.

## Initialize the integration

Wire up a Temporal `Client` once at module scope and pass it to `init()` from `@mastra/temporal`. `init()` returns Mastra's `createWorkflow` and `createStep` factories bound to that client and task queue.

```ts
// src/temporal.ts
import { init } from '@mastra/temporal'
import { Client, Connection } from '@temporalio/client'
import { loadClientConnectConfig } from '@temporalio/envconfig'

const config = loadClientConnectConfig()
const connection = await Connection.connect(config.connectionOptions)
const client = new Client({ connection })

export const { createWorkflow, createStep } = init({
  client,
  taskQueue: 'mastra',
})
```

`init()` parameters:

- `client` — a `@temporalio/client` `Client` instance.
- `taskQueue` — the Task Queue name Mastra-derived Workflows and Activities run on. The same value must be passed to the Worker (below).
- `startToCloseTimeout` — optional. Maximum activity runtime. **Default: 1 minute.** Accepts string values like `'5 minutes'`.

`loadClientConnectConfig()` from `@temporalio/envconfig` reads `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, and `TEMPORAL_API_KEY` from the environment.

## Define a step and a workflow

Use the bound `createStep` and `createWorkflow` from `src/temporal.ts`. Each `createStep` becomes a Temporal Activity; each `createWorkflow` becomes a Temporal Workflow.

```ts
// src/mastra/workflows.ts
import { z } from 'zod'
import { createWorkflow, createStep } from '../temporal'

const incrementStep = createStep({
  id: 'increment',
  inputSchema: z.object({
    value: z.number(),
  }),
  outputSchema: z.object({
    value: z.number(),
  }),
  execute: async ({ inputData }) => {
    return { value: inputData.value + 1 }
  },
})

const workflow = createWorkflow({
  id: 'increment-workflow',
  steps: [incrementStep],
  inputSchema: z.object({
    value: z.number(),
  }),
  outputSchema: z.object({
    value: z.number(),
  }),
}).then(incrementStep)

workflow.commit()

export { workflow as incrementWorkflow }
```

- **Workflow `id` must be a static string literal.** The build-time transformer derives each Workflow's Temporal export name from this `id`, so it cannot be a variable, template, or computed value.
- **Call `workflow.commit()` before exporting.** Workflows without `.commit()` are not picked up by the build-time transformer.

## Register workflows with Mastra

```ts
// src/mastra/index.ts
import { Mastra } from '@mastra/core'
import { PinoLogger } from '@mastra/loggers'
import { incrementWorkflow } from './workflows'

export const mastra = new Mastra({
  workflows: { incrementWorkflow },
  logger: new PinoLogger({ name: 'Mastra', level: 'info' }),
})
```

## Worker

Construct a `MastraPlugin` from `@mastra/temporal/worker`, run its build-time `prebuild` step pointing at the Mastra entry file, then pass the plugin into `Worker.create({ plugins: [...] })`.

```ts
// src/mastra/worker.ts
import { MastraPlugin } from '@mastra/temporal/worker'
import { NativeConnection, Worker } from '@temporalio/worker'

const connection = await NativeConnection.connect({
  address: 'localhost:7233',
})

const mastraPlugin = new MastraPlugin()

await mastraPlugin.prebuild({
  entryFile: import.meta.resolve('./index.ts'),
})

const worker = await Worker.create({
  connection,
  namespace: 'default',
  taskQueue: 'mastra',
  plugins: [mastraPlugin],
})

await worker.run()
```

- **Don't pass `activities` to `Worker.create`.** `MastraPlugin` auto-registers every Activity derived from `createStep` after `prebuild` runs.
- **`taskQueue` on the Worker must match the `taskQueue` passed to `init()`.** Both sides target the same queue.
- **`prebuild({ entryFile })` is a build-time transform.** It must complete before `Worker.create`; pass the path to the Mastra entry file (`src/mastra/index.ts` above).

## Run a workflow

Resolve the workflow off the configured `mastra` instance and start a run. The bound client routes execution through Temporal.

```ts
// scripts/run.ts
import { mastra } from '../src/mastra'

const run = await mastra.getWorkflow('incrementWorkflow').createRun()
const result = await run.start({ inputData: { value: 5 } })

console.log(result)
```

## Local development

```bash
docker run --rm -p 7233:7233 -p 8080:8080 temporalio/auto-setup:latest
```

Run the worker in another terminal:

```bash
npx tsx src/mastra/worker.ts
```

The Temporal UI is available at `http://localhost:8080`.

## Environment variables

`@temporalio/envconfig`'s `loadClientConnectConfig()` consumes these variables when wiring the Client connection:

- `TEMPORAL_ADDRESS`
- `TEMPORAL_NAMESPACE`
- `TEMPORAL_API_KEY`

## Hard constraints

- **Workflow `id` must be a static string literal.** Pass a literal to `createWorkflow({ id: 'my-workflow', ... })`; the build-time transformer derives the Temporal export name from it.
- **Don't pass `activities` to `Worker.create`.** `MastraPlugin` auto-registers Activities; manual registration conflicts with the plugin.
- **`mastraPlugin.prebuild({ entryFile })` must run before `Worker.create`.** The transform produces the Workflow and Activity definitions the Worker hosts.
- **Temporal Workers require a long-lived process.** Don't deploy the worker to serverless platforms that hibernate between requests.

## Common mistakes

- Importing `MastraPlugin` from `@mastra/temporal` instead of `@mastra/temporal/worker`.
- Passing `activities` to `Worker.create` alongside `MastraPlugin`.
- Forgetting `workflow.commit()` after `.then(step)` — the transformer skips uncommitted workflows.
- Using a computed `id` on `createWorkflow` — breaks the build-time transformer's Temporal export naming.
- Mismatching `taskQueue` between `init()` and `Worker.create`.
- Calling `MastraPlugin` without first running `prebuild({ entryFile })`.

## Out of scope

The upstream Mastra Temporal guide covers `createWorkflow` and `createStep` only. Mastra Agents, Tools, Memory, RAG, evals, and Mastra Studio are **not** documented as participating in this Temporal integration.

For language-agnostic AI/LLM orchestration patterns (centralized retries, tool placement, multi-agent), see `references/core/ai-patterns.md`.

## Resources

- Temporal TypeScript integrations index: <https://docs.temporal.io/develop/typescript/integrations>
- Upstream Mastra deployment guide: <https://mastra.ai/guides/deployment/temporal>
