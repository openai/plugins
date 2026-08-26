> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

## Overview

Standalone Activities are Activities run independently of any Workflow, started directly from a Temporal Client — useful when you need a single durable, retryable task (job-queue style) and not multi-step orchestration. The same Activity method can be executed both as a Standalone Activity and as a Workflow Activity with no code changes.

Standalone Activities are conceptually the same across all SDKs. Read the [cross-SDK concept file](references/core/standalone-activities.md) if you have not already, and then see below for the Java SDK specific APIs for calling Standalone Activities.

## Prerequisites

- Temporal Java SDK v1.35.0 or higher.
- Temporal CLI v1.7.0 or higher — see [Temporal CLI install instructions](references/core/install_cli.md) if needed. Dev server includes Standalone Activities support.
- For production, Temporal Server v1.31.0 or higher (or Temporal Cloud).

## Hosting Activities on a Worker

The Activity is defined just as activities normally are in Temporal. Worker registration is also the same.

```java
ClientConfigProfile profile = ClientConfigProfile.load();
WorkflowServiceStubs service =
    WorkflowServiceStubs.newServiceStubs(profile.toWorkflowServiceStubsOptions());

WorkflowClient client = WorkflowClient.newInstance(service, profile.toWorkflowClientOptions());
WorkerFactory factory = WorkerFactory.newInstance(client);
Worker worker = factory.newWorker(TASK_QUEUE);
worker.registerActivitiesImplementations(new GreetingActivitiesImpl()); // register whatever your activity(ies) is/are
factory.start();
```

## Calling and managing Standalone Activities

Start and manage Standalone Activities from your application code using the Temporal Client.

### Do not call from inside a Workflow

Don't call `ActivityClient.execute` / `ActivityClient.start` or any other Standalone Activity APIs from inside a Workflow Definition — use Workflow-side activity invocation (`Workflow.newActivityStub(...)`) instead.

### Connect a Client

The Standalone Activity operations are methods on a connected `ActivityClient`. The examples below assume this `client`.

```java
ActivityClient client =
    ActivityClient.newInstance(
        service,
        ActivityClientOptions.newBuilder().setNamespace(profile.getNamespace()).build());
```

### Execute (wait for result)

Use `client.execute(...)` to durably enqueue the Activity, wait for it to run on a Worker, and return the result. `StartActivityOptions` must set `id`, `taskQueue`, and at least one of `startToCloseTimeout` or `scheduleToCloseTimeout`.

#### With type checking

Use when activity definitions are available in this language. The typed form takes the Activity interface class and an unbound method reference; the SDK infers the Activity type name and result type at runtime.

```java
// In practice, use a meaningful business identifier, like customer or transaction identifier
String activityId = UUID.randomUUID().toString();

StartActivityOptions options =
    StartActivityOptions.newBuilder()
        .setId(activityId)
        .setTaskQueue(TASK_QUEUE)
        .setStartToCloseTimeout(Duration.ofSeconds(10))
        .build();

String result =
    client.execute(
        GreetingActivities.class,
        GreetingActivities::composeGreeting,
        options,
        "Hello",
        "World");
```

#### Without type checking

Use when activity definitions are unavailable in this language (i.e. you can't import them). Call the Activity by its string type name and pass the result class.

```java
String result = client.execute("ComposeGreeting", String.class, options, "Hello", "World");
```

### Start (do not wait for result)

Use `client.start(...)` to durably enqueue the Activity and get back an `ActivityHandle` without waiting for completion. This takes the **exact same arguments as `execute`**.

```java
ActivityHandle<String> handle = client.start(...);
```

### Get a handle to an existing Activity execution

Use `client.getHandle(...)` to attach a typed handle to a previously started Standalone Activity. Passing `null` as the run ID targets the latest run of that Activity ID.

```java
ActivityHandle<String> handle = client.getHandle("standalone-activity-id", null, String.class);
```

### Wait for the result of a handle

```java
String result = handle.getResult();
// or, for a non-blocking wait...
CompletableFuture<String> future = handle.getResultAsync();
```

Calling `execute` is equivalent to `start` followed by `getResult()`.

### List Standalone Activities

```java
client
    .listExecutions("TaskQueue = '" + TASK_QUEUE + "'") // returns a Stream<ActivityExecutionMetadata>
    .forEach(
        info ->
            System.out.printf(
                "ActivityID: %s, Type: %s, Status: %s%n",
                info.getActivityId(), info.getActivityType(), info.getStatus()));
```

Only Standalone Activity Executions are returned; Activities running inside Workflows are not included.

### Count Standalone Activities

Use `client.countExecutions(query)` to count matching executions; this takes the **exact same arguments as `listExecutions`**.

```java
ActivityExecutionCount resp = client.countExecutions("TaskQueue = '" + TASK_QUEUE + "'");
System.out.println("Total activities: " + resp.getCount());
```
