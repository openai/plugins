# Temporal Vercel AI SDK Integration (TypeScript)

## Overview

`@temporalio/ai-sdk` is the Temporal TypeScript SDK integration for [Vercel's AI SDK](https://ai-sdk.dev/) v7. It registers an `AiSdkPlugin` on the Worker so that LLM calls made by functions like `generateText()`, along with MCP tool invocations, run as Temporal Activities under Temporal's retry, timeout, and Durable Execution semantics. AI SDK tool functions execute inside the Workflow and must delegate any non-deterministic work to Activities, while the Workflow author otherwise writes normal AI SDK code.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For cross-SDK AI/LLM patterns (Activities wrapping LLM calls, centralized retries, multi-agent orchestration) see `references/core/ai-patterns.md`. For TypeScript SDK fundamentals (Worker setup, `proxyActivities`, the V8 workflow sandbox) see `references/typescript/typescript.md` and `references/typescript/determinism.md` — this file does not restate them.

## Prerequisites

- The standard TypeScript SDK setup from `references/typescript/typescript.md` (Temporal CLI installed, `@temporalio/client`, `@temporalio/worker`, `@temporalio/workflow`, `@temporalio/activity`).
- Familiarity with the Vercel AI SDK itself — for AI SDK API details refer to the [Vercel AI SDK documentation](https://ai-sdk.dev/).
- Provider credentials available to the Worker process. Most AI SDK providers read credentials from environment variables; the client process does **not** need provider credentials.

## Install

```bash
npm install @temporalio/ai-sdk
```

## Configure the Worker

Register `AiSdkPlugin` on `Worker.create` and pass a `modelProvider` (any AI SDK provider, e.g. `openai` from `@ai-sdk/openai`). The provider is what creates models when the workflow calls `temporalProvider.languageModel('<model-id>')`.

```ts
import { openai } from '@ai-sdk/openai';
import { AiSdkPlugin } from '@temporalio/ai-sdk';
import { Worker } from '@temporalio/worker';
import * as activities from './activities';

const worker = await Worker.create({
  plugins: [
    new AiSdkPlugin({
      modelProvider: openai,
    }),
  ],
  namespace: 'default',
  taskQueue: 'ai-sdk',
  workflowsPath: require.resolve('./workflows'),
  activities,
});
```

Make sure the Client and Worker share the same Task Queue and Namespace.

## Use the AI SDK inside a Workflow

In Workflow code, call AI SDK functions exactly as you would outside Temporal, but pass `temporalProvider.languageModel('<model-id>')` as `model`. The string is forwarded to the configured `modelProvider` to construct the model; the call itself runs as a Temporal Activity.

```ts
import { generateText } from 'ai';
import { temporalProvider } from '@temporalio/ai-sdk/workflow';

export async function haikuAgent(prompt: string): Promise<string> {
  const result = await generateText({
    model: temporalProvider.languageModel('gpt-4o-mini'),
    prompt,
    system: 'You only respond in haikus.',
  });
  return result.text;
}
```

The workflow now inherits Durable Execution: automatic retries on the LLM Activity, configurable timeouts, and recovery across Worker crashes.

## Tools

The AI SDK lets the model call tools; with this plugin, tool functions execute inside the Workflow. Because Workflow code must stay deterministic, any tool that performs I/O must delegate to an Activity. Obtain the Activity through `proxyActivities` and use it as the tool's `execute`.

Activity (regular Temporal Activity in `activities.ts`):

```ts
export async function getWeather(input: {
  location: string;
}): Promise<{ city: string; temperatureRange: string; conditions: string }> {
  return {
    city: input.location,
    temperatureRange: '14-20C',
    conditions: 'Sunny with wind.',
  };
}
```

Workflow that exposes the Activity as a tool:

```ts
import { proxyActivities } from '@temporalio/workflow';
import { generateText, tool } from 'ai';
import { temporalProvider } from '@temporalio/ai-sdk/workflow';
import { z } from 'zod';
import type * as activities from './activities';

const { getWeather } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function toolsAgent(question: string): Promise<string> {
  const result = await generateText({
    model: temporalProvider.languageModel('gpt-4o-mini'),
    prompt: question,
    system: 'You are a helpful agent.',
    tools: {
      getWeather: tool({
        description: 'Get the weather for a given city',
        inputSchema: z.object({
          location: z.string().describe('The location to get the weather for'),
        }),
        execute: getWeather,
      }),
    },
    stopWhen: stepCountIs(5),
  });
  return result.text;
}
```

## Model Context Protocol (MCP) servers

The plugin ships a stateless MCP client that runs inside a Workflow. Calls to MCP servers (listing tools, invoking them) run as Activities behind the scenes, so retries, timeouts, and observability come from Temporal.

### 1. Register MCP client factories on the Worker

Build a `mcpClientFactories` map keyed by server name. Each factory returns an MCP client built with `experimental_createMCPClient` from `@ai-sdk/mcp` (aliased as `createMCPClient` in the example) and a transport from the upstream MCP SDK — e.g. `StdioClientTransport` from `@modelcontextprotocol/sdk/client/stdio.js`. Pass the map to `AiSdkPlugin` via `mcpClientFactories`. Multiple servers can be registered by adding more factory entries.

```ts
import { experimental_createMCPClient as createMCPClient } from '@ai-sdk/mcp';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const mcpClientFactories = {
  testServer: () =>
    createMCPClient({
      transport: new StdioClientTransport({
        command: 'node',
        args: ['lib/mcp-server.js'],
      }),
    }),
};

const worker = await Worker.create({
  plugins: [
    new AiSdkPlugin({
      modelProvider: openai,
      mcpClientFactories,
    }),
  ],
  // ...
});
```

With `StdioClientTransport`, the Worker starts the MCP server process and connects to it on demand whenever a Task needs it.

### 2. Use the MCP client inside a Workflow

Inside the workflow, construct `new TemporalMCPClient({ name: '<server-name>' })` using the same name as the factory key, then call `await mcpClient.tools()` to get the tools to pass to `generateText`.

```ts
import { TemporalMCPClient, temporalProvider } from '@temporalio/ai-sdk/workflow';
import { generateText } from 'ai';

export async function mcpAgent(prompt: string): Promise<string> {
  const mcpClient = new TemporalMCPClient({ name: 'testServer' });
  const tools = await mcpClient.tools();
  const result = await generateText({
    model: temporalProvider.languageModel('gpt-4o-mini'),
    prompt,
    tools,
    system: 'You are a helpful agent, You always use your tools when needed.',
    stopWhen: stepCountIs(5),
  });
  return result.text;
}
```

## Common mistakes

- **Importing from the wrong package.** `AiSdkPlugin` comes from `@temporalio/ai-sdk`, while Workflow-side helpers such as `temporalProvider` and `TemporalMCPClient` come from `@temporalio/ai-sdk/workflow`. `generateText` and `tool` come from `ai`; `experimental_createMCPClient` comes from `@ai-sdk/mcp`.
- **Calling `fetch` (or any I/O) directly inside a tool's `execute`.** Tool functions run in the Workflow sandbox and must delegate to an Activity obtained through `proxyActivities`.
- **Passing an option other than `modelProvider`/`mcpClientFactories` to `AiSdkPlugin`.** Only those two options are documented.
- **Constructing `TemporalMCPClient` positionally.** Use the object form `new TemporalMCPClient({ name: '<server-name>' })`.
- **Mismatched Task Queue or Namespace between Client and Worker.** Both sides must agree, or the Worker will not pick up the workflow.
- **Putting provider credentials on the Client.** Only the Worker process needs provider API keys.

## Additional Resources

- [AI SDK by Vercel integration guide](https://docs.temporal.io/develop/typescript/integrations/ai-sdk) — the canonical Temporal doc this reference is grounded in.
- [Vercel AI SDK documentation](https://ai-sdk.dev/) — upstream AI SDK reference, including the provider list at [`ai-sdk.dev/providers/ai-sdk-providers`](https://ai-sdk.dev/providers/ai-sdk-providers).
- `references/core/ai-patterns.md` — cross-SDK AI/LLM patterns.
- `references/typescript/typescript.md` — TypeScript SDK fundamentals.
