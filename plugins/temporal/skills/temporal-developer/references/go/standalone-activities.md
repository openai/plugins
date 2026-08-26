> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

## Overview

Standalone Activities are Activities run independently of any Workflow, started directly from a Temporal Client — useful when you need a single durable, retryable task (job-queue style) and not multi-step orchestration. The same Activity method can be executed both as a Standalone Activity and as a Workflow Activity with no code changes.

Standalone Activities are conceptually the same across all SDKs. Read the [cross-SDK concept file](references/core/standalone-activities.md) if you have not already, and then see below for the Go SDK specific APIs for calling Standalone Activities.

## Prerequisites

- Temporal Go SDK v1.41.0 or higher.
- Temporal CLI v1.7.0 or higher — see [Temporal CLI install instructions](references/core/install_cli.md) if needed. The Temporal Dev Server has Standalone Activities enabled by default.
- For production, Temporal Server v1.31.0 or higher (or Temporal Cloud).

## Hosting Activities on a Worker

The Activity is defined just as activities normally are in Temporal. Worker registration is also the same.

```go
package main

import (
	"github.com/temporalio/samples-go/standalone-activity/helloworld"
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/contrib/envconfig"
	"go.temporal.io/sdk/worker"
	"log"
)

func main() {
	c, err := client.Dial(envconfig.MustLoadDefaultClientOptions())
	if err != nil {
		log.Fatalln("Unable to create client", err)
	}
	defer c.Close()

	w := worker.New(c, "standalone-activity-helloworld", worker.Options{})

	w.RegisterActivity(helloworld.Activity)

	err = w.Run(worker.InterruptCh())
	if err != nil {
		log.Fatalln("Unable to start worker", err)
	}
}
```

## Calling and managing Standalone Activities

Start and manage Standalone Activities from your application code using the Temporal `Client`.

### Do not call from inside a Workflow

Don't call `client.ExecuteActivity` or any other Standalone Activity APIs from inside a Workflow Definition — use Workflow-side activity invocation (`workflow.ExecuteActivity(ctx, ...)`) instead.

### Connect a Client

The Standalone Activity operations are methods on a connected `Client`. The examples below assume this client `c`.

```go
import (
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/contrib/envconfig"
	"context"
)

c, err := client.Dial(envconfig.MustLoadDefaultClientOptions())
if err != nil {
	log.Fatalln("Unable to create client", err)
}
defer c.Close()
```

### Execute a Standalone Activity

Use `client.ExecuteActivity(...)` to durably enqueue the Activity. It then returns an `ActivityHandle` immediately — it does not wait for completion. After that, call `handle.Get(ctx, &out)` to wait for the result. There is no separate `Start` function in the Go SDK; `ExecuteActivity` is the only entry point.

`client.StartActivityOptions` requires `ID`, `TaskQueue`, and at least one of `ScheduleToCloseTimeout` or `StartToCloseTimeout`.

#### With type checking

Use when activity definitions are available in this language. Pass the activity function reference.

Pass the Activity as a function reference:

```go
activityOptions := client.StartActivityOptions{
	ID:                     "send-welcome-email:user-42",
	TaskQueue:              "standalone-activity-helloworld",
	ScheduleToCloseTimeout: 10 * time.Second,
}

handle, err := c.ExecuteActivity(context.Background(), activityOptions, helloworld.Activity, "Temporal")
if err != nil {
	log.Fatalln("Unable to execute activity", err)
}

log.Println("Started", "ActivityID", handle.GetID(), "RunID", handle.GetRunID())

var result string
err := handle.Get(context.Background(), &result)
if err != nil {
	log.Fatalln("Activity failed", err)
}
log.Println("Activity result:", result)
```

#### Without type checking

Use when activity definitions are unavailable in this language (i.e. you can't import them). Pass the activity type name as a string.

```go
activityOptions := client.StartActivityOptions{
	ID:                     "send-welcome-email:user-42",
	TaskQueue:              "standalone-activity-helloworld",
	ScheduleToCloseTimeout: 10 * time.Second,
}

handle, err := c.ExecuteActivity(context.Background(), activityOptions, "Activity", "Temporal")
if err != nil {
	log.Fatalln("Unable to execute activity", err)
}

log.Println("Started", "ActivityID", handle.GetID(), "RunID", handle.GetRunID())

var result string
err := handle.Get(context.Background(), &result)
if err != nil {
	log.Fatalln("Activity failed", err)
}
log.Println("Activity result:", result)
```

### Get a handle to an existing Activity execution

Use `client.GetActivityHandle()` to attach a handle to a previously started Standalone Activity. Both `ActivityID` and `RunID` are required.

```go
handle := c.GetActivityHandle(client.GetActivityHandleOptions{
	ActivityID: "send-welcome-email:user-42",
	RunID:      "the-run-id",
})
```

### Wait for the result of a handle

Call `handle.Get(ctx, &out)` to block until the Activity completes and deserialize its result into the provided pointer. If the Activity failed, the failure is returned as an error.

```go
var result string
err := handle.Get(context.Background(), &result)
if err != nil {
	log.Fatalln("Activity failed", err)
}
log.Println("Activity result:", result)
```

Calling `ExecuteActivity` and then `handle.Get(ctx, &out)` is the Go equivalent of the synchronous "Execute and wait" pattern that other SDKs offer as a single call.

### List Standalone Activities

```go
resp, err := c.ListActivities(context.Background(), client.ListActivitiesOptions{
	Query: "TaskQueue = 'standalone-activity-helloworld'",
})
if err != nil {
	log.Fatalln("Unable to list activities", err)
}

for info, err := range resp.Results { // a range-over-func iterator that yields `(ActivityExecutionInfo, error)` pairs.
	if err != nil {
		log.Fatalln("Error iterating activities", err)
	}
	log.Printf("ActivityID: %s, Type: %s, Status: %v\n",
		info.ActivityID, info.ActivityType, info.Status)
}
```

Only Standalone Activity Executions are returned; Activities running inside Workflows are not included.

### Count Standalone Activities

Use `client.CountActivities()` to count matching executions; this takes the **exact same arguments as `ListActivities`**.

```go
resp, err := c.CountActivities(context.Background(), client.CountActivitiesOptions{
	Query: "TaskQueue = 'standalone-activity-helloworld'",
})
if err != nil {
	log.Fatalln("Unable to count activities", err)
}

log.Println("Total activities:", resp.Count)
```
