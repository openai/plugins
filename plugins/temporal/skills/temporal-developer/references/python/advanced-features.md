# Python SDK Advanced Features

## Schedules

Create recurring workflow executions.

```python
from temporalio.client import (
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
    ScheduleIntervalSpec,
)

# Create a schedule
schedule_id = "daily-report"
await client.create_schedule(
    schedule_id,
    Schedule(
        action=ScheduleActionStartWorkflow(
            DailyReportWorkflow.run,
            id="daily-report",
            task_queue="reports",
        ),
        spec=ScheduleSpec(
            intervals=[ScheduleIntervalSpec(every=timedelta(days=1))],
        ),
    ),
)

# Manage schedules
schedule = client.get_schedule_handle(schedule_id)
await schedule.pause("Maintenance window")
await schedule.unpause()
await schedule.trigger()  # Run immediately
await schedule.delete()
```

## Async Activity Completion

For activities that complete asynchronously (e.g., human tasks, external callbacks).
If you configure a heartbeat_timeout on this activity, the external completer is responsible for sending heartbeats via the async handle.
If you do NOT set a heartbeat_timeout, no heartbeats are required.

**Note:** If the external system that completes the asynchronous action can reliably be trusted to do the task and Signal back with the result, and it doesn't need to Heartbeat or receive Cancellation, then consider using **signals** instead.

```python
from temporalio import activity
from temporalio.client import Client

@activity.defn
async def request_approval(request_id: str) -> None:
    # Get task token for async completion
    task_token = activity.info().task_token

    # Store task token for later completion (e.g., in database)
    await store_task_token(request_id, task_token)

    # Mark this activity as waiting for external completion
    activity.raise_complete_async()

# Later, complete the activity from another process
async def complete_approval(request_id: str, approved: bool):
    client = await Client.connect("localhost:7233", namespace="default")
    # Retrieve the task token from external storage (e.g., database)
    task_token = await get_task_token(request_id)

    handle = client.get_async_activity_handle(task_token=task_token)

    # Optional: if a heartbeat_timeout was set, you can periodically:
    # await handle.heartbeat(progress_details)

    if approved:
        await handle.complete("approved")
    else:
        # You can also fail or report cancellation via the handle
        await handle.fail(ApplicationError("Rejected"))
```

## Sandbox Customization

The Python SDK runs workflows in a sandbox to help you ensure determinism. You can customize sandbox restrictions when needed. See `references/python/determinism-protection.md`

## Gevent Compatibility Warning

**The Python SDK is NOT compatible with gevent.** Gevent's monkey patching modifies Python's asyncio event loop in ways that break the SDK's deterministic execution model.

If your application uses gevent:

- You cannot run Temporal workers in the same process
- Consider running workers in a separate process without gevent
- Use a message queue or HTTP API to communicate between gevent and Temporal processes

## Worker Tuning

Configure worker performance settings.

```python
from concurrent.futures import ThreadPoolExecutor

worker = Worker(
    client,
    task_queue="my-queue",
    workflows=[MyWorkflow],
    activities=[my_activity],
    # Workflow task concurrency
    max_concurrent_workflow_tasks=100,
    # Activity task concurrency
    max_concurrent_activities=100,
    # Executor for sync activities
    activity_executor=ThreadPoolExecutor(max_workers=50),
    # Graceful shutdown timeout
    graceful_shutdown_timeout=timedelta(seconds=30),
)
```

## DNS Resolver Configuration

`DnsLoadBalancingConfig`  makes Core periodically re-resolve the client's target host and round-robin requests across the resolved addresses . Use it when `target_host` resolves to multiple A/AAAA records (e.g., a load-balanced gRPC frontend, multi-address private endpoints) and you want the client to spread RPCs across them.

### Configuration

```python
from temporalio.client import Client
from temporalio.service import DnsLoadBalancingConfig

client = await Client.connect(
    "frontend.example.internal:7233",
    dns_load_balancing_config=DnsLoadBalancingConfig(
        resolution_interval_millis=5000,  # re-resolve every 5 seconds
    ),
)
```

- The only field is `resolution_interval_millis: int = 30000`  — how often to re-resolve DNS, in milliseconds.
- `DnsLoadBalancingConfig.default`  is a pre-built instance with the default 30-second interval.
- `dns_load_balancing_config` defaults to 30 seconds if you don't pass anything explicitly.
- Pass `dns_load_balancing_config=None` to disable DNS load balancing entirely.

### Mutual exclusion with HTTP CONNECT proxy

DNS load balancing and `HttpConnectProxyConfig` cannot be used together. When `http_connect_proxy_config` is set on the same client, DNS load balancing is **silently disabled**  — there is no error and no precedence flag. If you need both, you cannot have both; choose the one your network requires.

## Workflow Init Decorator

You should always put state initialization logic in the `__init__` of your workflow class, so that it happens before signals/updates arrive.

Normally, your `__init__` must have no arguments. However, if you add the `@workflow.init` decorator, then your `__init__` instead receives the same workflow arguments that `@workflow.run` receives:

```python
@workflow.defn
class MyWorkflow:
    @workflow.init
    def __init__(self, initial_value: str) -> None:
        # This runs when the Workflow is instantiated, including during replay
        self._value = initial_value
        self._items: list[str] = []

    @workflow.run
    async def run(self, initial_value: str) -> str:
        # self._value and self._items are already initialized
        return self._value
```

`__init__` (with `@workflow.init`) and `@workflow.run` must have the same parameters with the same types. You cannot make blocking calls (activities, sleeps, etc.) from the `__init__`.

## Workflow Failure Exception Types

Control which exceptions cause workflow task failures vs workflow failures.

- Special case: if you include temporalio.workflow.NondeterminismError (or a superclass), non-determinism errors will fail the workflow instead of leaving it in a retrying state
- **Tip for testing:** Set to `[Exception]` in tests so any unhandled exception fails the workflow immediately rather than retrying the workflow task forever. This surfaces bugs faster.

### Per-Workflow Configuration

```python
@workflow.defn(
    # These exception types will fail the workflow execution (not just the task)
    failure_exception_types=[ValueError, CustomBusinessError]
)
class MyWorkflow:
    @workflow.run
    async def run(self) -> str:
        raise ValueError("This fails the workflow, not just the task")
```

### Worker-Level Configuration

```python
worker = Worker(
    client,
    task_queue="my-queue",
    workflows=[MyWorkflow],
    workflow_failure_exception_types=[ValueError, CustomBusinessError],
)
```
