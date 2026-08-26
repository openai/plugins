# Temporal Rust SDK Reference

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

## Overview

The Temporal Rust SDK (`temporalio-sdk`) provides native Rust APIs for Workflows, Activities, Workers, and Clients. The SDK is in Public Preview and under active development, so verify exact crate versions and method names against the official docs before giving precise implementation guidance.

Rust Workflows are structs with macro-decorated methods. Activities are async methods on an `impl` block. Workers register Workflow and Activity types, then poll a Task Queue.

## Official References

- [Rust SDK developer guide](https://docs.temporal.io/develop/rust) - Rust documentation hub.
- [Rust SDK Quickstart](https://docs.temporal.io/develop/rust/quickstart) - setup, dependencies, local dev server, and a complete hello-world example.
- [Workflow basics](https://docs.temporal.io/develop/rust/workflows/basics) - Workflow structs, `#[run]`, optional `#[init]`, and message handlers.
- [Activity basics](https://docs.temporal.io/develop/rust/activities/basics) - Activity macros, parameters, and Activity boundaries.
- [Worker processes](https://docs.temporal.io/develop/rust/workers/worker-process) - Worker setup, registration, and Task Queue polling.
- [Temporal Client](https://docs.temporal.io/develop/rust/client/temporal-client) - connecting to Temporal Service, starting Workflows, and fetching results.
- [docs.rs temporalio-sdk](https://docs.rs/temporalio-sdk/latest/temporalio_sdk/) - generated Rust API documentation.
- [sdk-rust examples](https://github.com/temporalio/sdk-rust/tree/main/crates/sdk/examples) - current example programs from the SDK repository.

## Quick Demo of Temporal

**Add dependencies:** Follow the [official Rust SDK Quickstart](https://docs.temporal.io/develop/rust/quickstart) for the current `Cargo.toml` dependencies.

**src/activities.rs** - Activity definition:

```rust
use temporalio_macros::activities;
use temporalio_sdk::activities::{ActivityContext, ActivityError};

pub struct MyActivities;

#[activities]
impl MyActivities {
    #[activity]
    pub async fn greet(_ctx: ActivityContext, name: String) -> Result<String, ActivityError> {
        Ok(format!("Hello, {}!", name))
    }
}
```

**src/workflows.rs** - Workflow definition:

```rust
use temporalio_macros::{workflow, workflow_methods};
use temporalio_sdk::{ActivityOptions, WorkflowContext, WorkflowContextView, WorkflowResult};
use std::time::Duration;

use crate::activities::MyActivities;

#[workflow]
pub struct GreetingWorkflow {
    name: String,
}

#[workflow_methods]
impl GreetingWorkflow {
    #[init]
    fn new(_ctx: &WorkflowContextView, name: String) -> Self {
        Self { name }
    }

    #[run]
    pub async fn run(ctx: &mut WorkflowContext<Self>) -> WorkflowResult<String> {
        let name = ctx.state(|s| s.name.clone());

        // Execute an activity
        let greeting = ctx.start_activity(
            MyActivities::greet,
            name,
            ActivityOptions::start_to_close_timeout(Duration::from_secs(30)),
        ).await?;

        println!("{}", greeting);
        Ok(greeting)
    }
}
```

**src/main.rs** - Worker setup:

```rust
use temporalio_client::{Client, ClientOptions, Connection};
use temporalio_common::envconfig::LoadClientConfigProfileOptions;
use temporalio_sdk::{Worker, WorkerOptions};
use temporalio_sdk_core::{CoreRuntime, RuntimeOptions};

mod workflows;
mod activities;

use crate::workflows::GreetingWorkflow;
use crate::activities::MyActivities;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let runtime = CoreRuntime::new_assume_tokio(RuntimeOptions::builder().build()?)?;

    // Set up client connection options, loading from config if available
    let (connection_options, client_options) = ClientOptions::load_from_config(
        LoadClientConfigProfileOptions::default(),
    )?;

    let connection = Connection::connect(connection_options).await?;
    let client = Client::new(connection, client_options)?;

    let worker_options = WorkerOptions::new("my-task-queue")
        .register_activities(MyActivities)
        .register_workflow::<GreetingWorkflow>()
        .build();

    Worker::new(&runtime, client, worker_options)?.run().await?;

    Ok(())
}
```

**Run locally:**

1. Start the dev server with `temporal server start-dev`.
2. Run the Worker with `cargo run`.
3. Start a Workflow Execution with the CLI:

```sh
temporal workflow start \
  --type GreetingWorkflow \
  --task-queue my-task-queue \
  --input '"Ziggy"'
```

## Key Concepts

### Workflow Definition

- Define a struct and annotate it with `#[workflow]`.
- Put Workflow methods in a `#[workflow_methods]` impl block.
- Use `#[run]` for the main Workflow logic, and optionally use `#[init]`, `#[signal]`, `#[query]`, and `#[update]`.

### Activity Definition

- Put Activity methods in a `#[activities]` impl block.
- Annotate each Activity method with `#[activity]`.
- Activities can perform I/O, call services, use system time, and do other non-deterministic work.

### Worker Setup

- A Worker registers Workflow and Activity types, then polls one Task Queue.
- Workers polling the same Task Queue should register the same Workflow and Activity types.
- Keep Worker runtime, client, config, secrets, and logging setup outside Workflow code.

### Temporal Client

- Use the Rust client outside Workflow code to start Workflows and send Signals, Queries, and Updates.
- Do not create or use a Temporal Client inside Workflow code.
- A Client can be used inside an Activity when the Activity needs to interact with Temporal Service.

## File Organization Best Practice

Keep Workflow definitions, Activity implementations, Worker setup, and starter/client code separate. This makes the determinism boundary easy to inspect.

```text
my_temporal_app/
|-- src/
|   |-- activities.rs   # Activity implementations and side effects
|   |-- workflows.rs    # Workflow definitions and orchestration
|   `-- main.rs         # Worker process in the Quickstart
`-- Cargo.toml
```

## Common Pitfalls

1. **Calling I/O from a Workflow** - Put network, database, filesystem, process calls, and other side effects in Activities.
2. **Mixing Worker and Workflow concerns** - Runtime setup, clients, secrets, environment config, and external logging sinks belong outside Workflow code.
3. **Assuming APIs are stable** - The Rust SDK is Public Preview, so check official docs, docs.rs, and SDK examples before naming exact APIs.

## Rust-Specific References Status

Rust-specific local reference files do not exist yet. For deeper Rust SDK details, use the official Rust SDK docs, docs.rs, and [`sdk-rust` examples](https://github.com/temporalio/sdk-rust/tree/main/crates/sdk/examples). For SDK-neutral Temporal concepts, use the core references under `references/core/`.
