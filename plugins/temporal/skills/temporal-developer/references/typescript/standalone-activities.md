> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

## Overview

Standalone Activities are Activities run independently of any Workflow, started directly from a Temporal Client — useful when you need a single durable, retryable task (job-queue style) and not multi-step orchestration. The same Activity method can be executed both as a Standalone Activity and as a Workflow Activity with no code changes.

Standalone Activities are conceptually the same across all SDKs. Read the [cross-SDK concept file](references/core/standalone-activities.md) if you have not already, and then see below for the TypeScript SDK specific APIs for calling Standalone Activities.

## Prerequisites

- Temporal TypeScript SDK v1.17.0 or higher.
- All `@temporalio/*` packages must be pinned to the same version (heads-up — install/upgrade them together).
- Temporal CLI v1.7.0 or higher — see [Temporal CLI install instructions](references/core/install_cli.md) if needed. Dev server includes Standalone Activities support.
- For production, Temporal Server v1.31.0 or higher (or Temporal Cloud).

## Hosting Activities on a Worker

The Activity is defined just as activities normally are in Temporal. Worker registration is also the same.

```typescript
import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';
import { loadClientConnectConfig } from '@temporalio/envconfig';

async function run() {
  const config = loadClientConnectConfig();
  const connection = await NativeConnection.connect(config.connectionOptions);
  const worker = await Worker.create({
    connection,
    namespace: config.namespace,
    taskQueue: 'hello-standalone-activities',
    activities, // register whatever your activity(ies) is/are
  });
  await worker.run();
}

run().catch(console.error);
```

## Calling and managing Standalone Activities

Start and manage Standalone Activities from your application code using the Temporal Client.

### Do not call from inside a Workflow

Don't call `client.activity.execute` / `client.activity.start` or any other Standalone Activity APIs from inside a Workflow Definition — use Workflow-side activity invocation (`proxyActivities`) instead.

### Connect a Client

The Standalone Activity operations are methods on `client.activity`, where `client` is a connected `Client`. The examples below assume this `client`.

```typescript
import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';

const config = loadClientConnectConfig();
const connection = await Connection.connect(config.connectionOptions);
const client = new Client({ connection, namespace: config.namespace });
```

### Execute (wait for result)

Use `execute` to durably enqueue the Activity, wait for it to run on a Worker, and return the result. The options require `id`, `taskQueue`, and at least one of `startToCloseTimeout` or `scheduleToCloseTimeout`.

#### With type checking

Use when activity definitions are available in this language. Call `client.activity.typed<typeof activities>()` to obtain a typed Activity Client interface. Calling `typed` does not create a new Client object — it only adjusts the type annotation of the existing Client.

```typescript
import * as activities from './activities';
import { nanoid } from 'nanoid';

const activitiesClient = client.activity.typed<typeof activities>();

const activityOptions = {
  taskQueue: 'hello-standalone-activities',
  startToCloseTimeout: '10s',
};

// In practice, use a meaningful business identifier, like customer or transaction identifier
const activityId = nanoid();

const result = await activitiesClient.execute('greet', {
  ...activityOptions,
  id: activityId,
  args: ['World'],
});
```

#### Without type checking

Use when activity definitions are unavailable in this language (i.e. you can't import them). Call `execute` directly on `client.activity`.

```typescript
const result = await client.activity.execute<string>('greet', {
  ...activityOptions,
  id: activityId,
  args: [1],
});
```

### Start (do not wait for result)

Use `activitiesClient.start(...)` (or `client.activity.start<R>(...)` on the untyped interface) to durably enqueue the Activity and get back a handle without waiting for completion. This takes the **exact same arguments as `execute`**.

```typescript
const handle = await activitiesClient.start(...);
```

### Get a handle to an existing Activity execution

Use `client.activity.getHandle<R>(activityId, runId?)` to attach a handle to a previously started Standalone Activity. Omitting `runId` targets the latest run of that Activity ID. `getHandle` is not available on the typed interface, and the optional type argument constrains the result type but isn't verified.

```typescript
const newHandle = client.activity.getHandle<string>(activityId);
```

### Wait for the result of a handle

```typescript
const result = await handle.result();
```

Calling `execute` is equivalent to `start` followed by `await handle.result()`.

### List Standalone Activities

```typescript
const query = 'TaskQueue="hello-standalone-activities"';

for await (const a of client.activity.list(query)) { // returns an AsyncIterable<ActivityExecutionInfo>
  console.log(
    `${a.activityId} | ${a.activityRunId} | ${a.activityType} | ${a.status} | ${a.closeTime?.toISOString()}`,
  );
}
```

Only Standalone Activity Executions are returned; Activities running inside Workflows are not included.

### Count Standalone Activities

Use `client.activity.count(query)` to count matching executions; this takes the **exact same arguments as `list`**.

```typescript
const { count } = await client.activity.count(query);
console.log(`Total activities: ${count}`);
```
