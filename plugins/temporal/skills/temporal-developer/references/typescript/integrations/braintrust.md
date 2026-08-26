# Temporal Braintrust Integration (TypeScript)

## Overview

[Braintrust](https://braintrust.dev) is an LLM observability and prompt-management platform. The Temporal TypeScript integration is delivered as the `@braintrust/temporal` package, which exposes a `BraintrustTemporalPlugin` that registers on both the Temporal Client and the Worker. Once registered, the plugin produces Braintrust spans for Workflow and Activity executions and propagates trace context across the Worker boundary.

The Temporal TypeScript documentation lists Braintrust as a supported integration and points to the Braintrust-hosted guide as the canonical reference.

> Canonical TypeScript guide: <https://www.braintrust.dev/docs/integrations/sdk-integrations/temporal#typescript>. Treat the Braintrust-hosted page as authoritative for TypeScript-specific API surface; this reference file captures only what is independently verifiable from Temporal's documentation and the canonical guide.

For conceptual LLM patterns shared across SDKs read `references/core/ai-patterns.md`.

## Prerequisites

- An existing Temporal TypeScript development environment as described in `references/typescript/typescript.md`.
- Temporal TypeScript SDK 2.1.0 or later.
- A Braintrust account.

## Install

```bash
npm install @braintrust/temporal braintrust @temporalio/client @temporalio/worker @temporalio/workflow @temporalio/activity @temporalio/common
```

The integration package is `@braintrust/temporal`; it sits alongside the standard `braintrust` SDK and the relevant `@temporalio/*` packages.

## Initialize the Braintrust logger

Initialize the Braintrust logger before constructing the Temporal Client and Worker so spans connect to the active project.

```typescript
import * as braintrust from "braintrust";

braintrust.initLogger({ projectName: "my-project" });
```

## Register `BraintrustTemporalPlugin` on the Client and the Worker

Create one `BraintrustTemporalPlugin` instance and pass it to **both** the Client and the Worker via `plugins`.

```typescript
import { Client, Connection } from "@temporalio/client";
import { Worker } from "@temporalio/worker";
import { BraintrustTemporalPlugin } from "@braintrust/temporal";
import * as activities from "./activities";

const plugin = new BraintrustTemporalPlugin();

const client = new Client({
  connection: await Connection.connect(),
  plugins: [plugin],
});

const worker = await Worker.create({
  taskQueue: "my-task-queue",
  workflowsPath: require.resolve("./workflows"),
  activities,
  plugins: [plugin],
});
```

The Client registration links client-initiated spans to the Workflow Executions they start. The Worker registration produces the Workflow and Activity spans inside Braintrust.

## What Braintrust traces

The plugin captures:

- Workflow execution spans named `temporal.workflow.<workflow_type>`, including Workflow type, ID, run ID, and errors.
- Activity execution spans named `temporal.activity.<activity_type>`, including Activity type, ID, result, errors, and parent Workflow metadata.
- Trace context propagated through Temporal headers to Activities, Local Activities, and Child Workflows.
- Parent-child relationships across Client calls, Workflows, and Activities.

## Common mistakes

- **Initializing the Braintrust logger after constructing the Client or Worker.** Call `braintrust.initLogger({ projectName: ... })` first so the Worker process attaches spans to the correct project.
- **Registering `BraintrustTemporalPlugin` on only one side.** Register on both the Client and the Worker so client-side spans link to the Workflows they start.

## Additional Resources

- Canonical TypeScript guide: <https://www.braintrust.dev/docs/integrations/sdk-integrations/temporal#typescript>.
- `references/core/ai-patterns.md` — conceptual LLM patterns shared across SDKs.
