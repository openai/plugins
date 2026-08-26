# Workflow Streams (Python)

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

## Overview

`temporalio.contrib.workflow_streams` is a Python SDK `contrib` library that gives a Workflow a durable, offset-addressed event channel built on Temporal's basic message primitives: Signals, Updates, and Queries.  It batch-publishes events, deduplicates batches for exactly-once delivery to the log, supports topic filtering, and carries state across Continue-As-New.

Use it for modest fan-out progress streaming: AI-agent runs, order pipelines, multi-step workflow status updates, etc.  It targets "tens of publishers and subscribers per Workflow, not thousands"; it is not suited to ultra-low-latency cases like real-time voice.

Only available in the Python SDK today; cross-language is on the roadmap.

## When to use / not to use

- Use it for: updating a UI as an AI agent works; surfacing status from a payment or order pipeline; reporting intermediate results from a data job.
- Skip it for: ultra-low-latency cases like real-time voice.
- Skip it for: high fan-out — thousands of subscribers per Workflow.

## Where to host the stream

A `WorkflowStream` is hosted inside a Workflow. The Workflow Id is the address subscribers attach to.

- **Same-Workflow hosting (common shape):** the Workflow that does the work also hosts the stream. Its lifecycle aligns with the run. Use this for AI agents and most progress-streaming cases.
- **Dedicated Workflow:** when the stream should outlive any single producer, accept fan-in from multiple unrelated sources, or be subscribable before any work has started. Producers publish from outside. Trade-off: explicit lifecycle management — the dedicated Workflow does not terminate on its own, so wire a signal-driven shutdown or a Continue-As-New strategy.
- Multiple subscribers can attach to the same Workflow Id concurrently (e.g. a UI with multiple browser tabs).

## Enable streaming on a Workflow

Import: `from temporalio.contrib.workflow_streams import WorkflowStream`

Construct `WorkflowStream()` from `@workflow.init`, **not** `@workflow.run`.  The stream's handlers must be registered before the first publish Signal arrives; doing it from `@workflow.run` raises `RuntimeError`.

Constructing more than one `WorkflowStream` on the same Workflow also raises `RuntimeError`.

```python
from dataclasses import dataclass

from temporalio import workflow
from temporalio.contrib.workflow_streams import WorkflowStream


@dataclass
class OrderInput:
    order_id: str


@workflow.defn
class OrderWorkflow:
    @workflow.init
    def __init__(self, input: OrderInput) -> None:
        self.stream = WorkflowStream()
```

Construction creates the in-memory event log and dynamically registers the publish Signal, subscribe Update, and offset Query handlers.

## Publish from a Workflow

Bind a topic name to its event type once via `self.stream.topic("name", type=Type)`, then call `publish()` on the returned handle.

`type=` is optional and defaults to `Any`.  The codec chain (encryption, compression) runs once on the Signal/Update envelope, never per item.

```python
from dataclasses import dataclass


@dataclass
class StatusEvent:
    state: str
    progress: int = 0
    detail: str = ""


@workflow.defn
class OrderWorkflow:
    @workflow.init
    def __init__(self, input: OrderInput) -> None:
        self.stream = WorkflowStream()
        self.status = self.stream.topic("status", type=StatusEvent)

    @workflow.run
    async def run(self, input: OrderInput) -> None:
        self.status.publish(StatusEvent(state="validating", detail="checking inventory"))
        await validate_order(input.order_id)
        self.status.publish(StatusEvent(state="charging", progress=33, detail="authorizing payment"))
        await charge_payment(input.order_id)
        self.status.publish(StatusEvent(state="shipping", progress=66, detail="dispatching to warehouse"))
        await dispatch_order(input.order_id)
        self.status.publish(StatusEvent(state="completed", progress=100))
```

Note: `publish()` is **not** awaited. Inside a Workflow it appends synchronously to the in-memory log.

## Publish from a client (external process or Activity)

Any process holding a Temporal `Client` and the target Workflow Id can publish by constructing a `WorkflowStreamClient`.  This is the general pattern; it covers HTTP backends, starters, one-off scripts, other Workflows' Activities, and standalone Activities.

General pattern: `WorkflowStreamClient.create(client, workflow_id, batch_interval=...)`.  Use it as an `async with` context manager so the buffer flushes on exit.

```python
from datetime import timedelta

from temporalio.client import Client
from temporalio.contrib.workflow_streams import WorkflowStreamClient


async def publish_status(workflow_id: str) -> None:
    temporal_client = await Client.connect("localhost:7233")
    stream_client = WorkflowStreamClient.create(
        temporal_client,
        workflow_id=workflow_id,
        batch_interval=timedelta(milliseconds=200),
    )
    async with stream_client:
        status = stream_client.topic("status", type=StatusEvent)
        status.publish(StatusEvent(state="started"))
        # Buffer is flushed on context manager exit.
```

Inside an Activity scheduled by a Workflow, `WorkflowStreamClient.from_within_activity()` is a convenience that infers the Temporal `Client` and the parent Workflow Id from the Activity context.

```python
from temporalio import activity
from temporalio.contrib.workflow_streams import WorkflowStreamClient


@activity.defn
async def stream_deltas(order_id: str) -> None:
    client = WorkflowStreamClient.from_within_activity()
    async with client:
        deltas = client.topic("delta", type=Delta)
        for delta in generate_deltas(order_id):
            deltas.publish(delta)
            activity.heartbeat()
```

For a **standalone Activity** (started directly via `Client.start_activity`), there is no parent Workflow context to infer, so `from_within_activity()` raises.  Fall back to `WorkflowStreamClient.create(activity.client(), workflow_id=...)` with the Workflow Id threaded through the Activity input.

Publish from the Activity directly rather than returning events for the Workflow to forward; the Workflow hosts the stream but does not read its own stream.

## `force_flush=True` vs. `await client.flush()`

These are two separate operations.

- **`publish(..., force_flush=True)`** — wakes the background flusher so the current buffer ships without waiting for the next `batch_interval`.  The call returns immediately after appending and signaling; it does **not** wait for delivery.  The flusher only runs while the client is entered (`async with client`); outside that, `force_flush=True` queues the wake event but nothing ships until you enter the context or call `await client.flush()`.  Use it for latency-sensitive events: first delta, punctuated events like `RETRY` or `STATUS_CHANGE`.

  ```python
  deltas.publish(delta, force_flush=True)
  ```

- **`await client.flush()`** — mid-stream barrier. Successful completion proves the Temporal server has received all prior publications.  The client stays open afterward. Exiting `async with client` already flushes on its way out; the explicit call is only for barriers in the middle.

  ```python
  async with client:
      deltas = client.topic("delta", type=Delta)
      for delta in first_phase():
          deltas.publish(delta)
      await client.flush()
      checkpoint_id = await record_phase_one_complete()
      for delta in second_phase(checkpoint_id):
          deltas.publish(delta)
  ```

## Non-blocking publish, no backpressure

`publish()` is non-blocking and applies no backpressure.  A slow subscriber does not slow publishers; if a publisher emits faster than batches can ship, the buffer grows.

If you need to bound this, apply a policy upstream of `publish()`.  The library does not pick block/drop/error/sample for you.

## Subscribe

Construct a client with `WorkflowStreamClient.create(client, workflow_id)`, then iterate a topic handle's `subscribe()`.  The bound type drives decoding; each `item.data` arrives as `T`.

```python
from temporalio.client import Client
from temporalio.contrib.workflow_streams import WorkflowStreamClient


async def watch_order(order_id: str) -> None:
    temporal_client = await Client.connect("localhost:7233")
    stream = WorkflowStreamClient.create(temporal_client, workflow_id=order_id)

    status = stream.topic("status", type=StatusEvent)
    async for item in status.subscribe():
        evt = item.data
        print(f"[{evt.progress:3d}%] {evt.state}: {evt.detail}")
        if evt.state == "completed":
            break
```

The iterator handles re-polling, pagination at the ~1 MB cap, and Workflow-side log truncation transparently.

**Subscribing from inside the host Workflow is intentionally unsupported.**  The Workflow only sees the successful return value of each Activity; the stream may carry partial output from retried attempts. Letting the Workflow read its own stream would mix those two views and break the conduit role.

A subscriber stores the last delivered `item.offset` and reconnects resume from that offset.

## Heterogeneous topics

To consume topics whose payload types differ, call `client.subscribe()` directly with a list of names and `result_type=RawValue`.  Passing an empty list (`subscribe([])`) subscribes to every topic.  Dispatch on `item.topic`; decode the wrapped payload with the client's payload converter.

```python
from temporalio.common import RawValue

converter = temporal_client.data_converter.payload_converter

async for item in stream.subscribe(["status", "progress"], result_type=RawValue):
    if item.topic == "status":
        evt = converter.from_payload(item.data.payload, StatusEvent)
        print(f"[status] {evt.state}: {evt.detail}")
    elif item.topic == "progress":
        evt = converter.from_payload(item.data.payload, ProgressEvent)
        print(f"[progress] {evt.message}")
```

A single iterator over multiple topics avoids the cancellation race that two concurrent subscribers would create.

## Closing the stream

End-of-stream is application-level; Workflow Streams does not impose a marker.  There is no `stream.close()` / `stream.end_of_stream()` API.

Without coordination, a subscriber keeps polling until the Workflow reaches a terminal state, and a Workflow that returns immediately after its last publish can lose that publish's poll round-trip in the gap.

A poll Update that is still in flight when the Workflow returns surfaces to the client as `AcceptedUpdateCompletedWorkflow`, and no new polls can complete after that.  That's why an overlap is required.

The pattern is an **in-band terminator** the subscriber recognizes plus a **brief overlap** before the Workflow returns.

### Pattern 1: fixed sleep (simplest)

```python
# at the end of @workflow.run
self.status.publish(StatusEvent(state="completed", progress=100))
await workflow.sleep(timedelta(seconds=30))
return result
```

Thirty seconds is a generous default.

### Pattern 2: acknowledgment handshake

```python
@workflow.signal
async def subscriber_acknowledged_terminator(self) -> None:
    self.subscriber_done = True

@workflow.run
async def run(self, input: ChatInput) -> str:
    ...
    try:
        await workflow.wait_condition(
            lambda: self.subscriber_done,
            timeout=timedelta(seconds=30),
        )
    except TimeoutError:
        pass  # No subscriber attached; the run still completes cleanly.
    return result
```

The timeout is still required because the subscriber may not be attached.  With the ack, the typical case exits as soon as the subscriber confirms.

### Inspecting terminal status

`subscribe()` exits cleanly when the Workflow reaches `COMPLETED`, `FAILED`, `CANCELED`, `TERMINATED`, or `TIMED_OUT`, but does not distinguish among them.  Call `await temporal_client.get_workflow_handle(workflow_id).describe()` after the loop to inspect the Workflow's status.

## Continue-As-New (CAN)

Skip this section for short-lived Workflows (single chat completion, order pipeline). CAN is for streams that run for hours or accumulate thousands of events

Subscribers automatically follow Continue-As-New chains — the Workflow ID is stable, so the iterator fetches a fresh handle and continues polling from the carried offset.

To roll a long-running streaming Workflow over without subscribers seeing a gap, carry both your application state and the stream state across the boundary:

- Add a `WorkflowStreamState | None` field to your Workflow input,
- pass it to the constructor as `WorkflowStream(prior_state=...)`,
- and call `WorkflowStream.continue_as_new(build_args)` to invoke the rollover. The helper drains waiting subscribers, waits for in-flight handlers to finish, then calls `workflow.continue_as_new` with the args produced by `build_args(post_drain_state)`.

```python
from dataclasses import dataclass, field

from temporalio import workflow
from temporalio.contrib.workflow_streams import WorkflowStream, WorkflowStreamState


@dataclass
class AppState:
    items_processed: int = 0


@dataclass
class WorkflowInput:
    app_state: AppState = field(default_factory=AppState)
    stream_state: WorkflowStreamState | None = None


@workflow.defn
class LongRunningWorkflow:
    @workflow.init
    def __init__(self, input: WorkflowInput) -> None:
        self.app_state = input.app_state
        self.stream = WorkflowStream(prior_state=input.stream_state)

    @workflow.run
    async def run(self, input: WorkflowInput) -> None:
        while True:
            await do_one_iteration(self)
            if workflow.info().is_continue_as_new_suggested():
                await self.stream.continue_as_new(
                    lambda stream_state: [
                        WorkflowInput(
                            app_state=self.app_state,
                            stream_state=stream_state,
                        )
                    ]
                )
```

**Hard constraint:** the field type must be `WorkflowStreamState | None`, **not** `Any`.  With `Any`, the data converter rebuilds the field as a plain `dict` and `WorkflowStream(prior_state=...)` raises `AttributeError` accessing `.log` / `.base_offset` / `.publishers` on the dict.

To pass other CAN parameters (`task_queue`, `retry_policy`, `run_timeout`), use the explicit recipe:

```python
self.stream.detach_pollers()
await workflow.wait_condition(workflow.all_handlers_finished)
workflow.continue_as_new(
    args=[WorkflowInput(app_state=self.app_state, stream_state=self.stream.get_state())],
    task_queue="other-tq",
)
```

The carried `WorkflowStreamState` includes the entire in-memory log of the previous run.  Offload large items via [External Storage](https://docs.temporal.io/external-storage) so each item is a small reference, and combine with `truncate()` to keep the carried log itself small.

## Tuning

The driving question: how often should the UI update? That answer trades user-perceived latency against history events accumulated.  Each batched publish is one Signal; each subscriber poll is one Update; both accumulate against the Workflow's history.

| Setting | Default | Notes |
| --- | --- | --- |
| `batch_interval` | 2 seconds | Maximum time between automatic flushes. 200 ms is a good start for LLM token streams. Below 100 ms the per-Signal RPC overhead starts to dominate.  |
| `max_batch_size` | unbounded | Cap by item count to stay under Temporal's per-message gRPC payload limit.  |
| `poll_cooldown` | 100 ms | Subscriber sleeps this interval between polls. Skipped only when a poll response hit the ~1 MB cap with more items remaining (`more_ready`).  |
| `max_retry_duration` | 10 minutes | How long a `WorkflowStreamClient` retries a failed publish batch before raising `TimeoutError`.  |
| `publisher_ttl` | 15 minutes | How long the Workflow retains per-publisher dedup state; entries older than this drop at each CAN.  |

**Invariant:** `max_retry_duration < publisher_ttl`.  Defaults (10 min < 15 min) satisfy this.  If a publisher's retry window exceeds the dedup retention, a retry that arrives after its dedup record has been pruned is treated as a fresh publish, and if the original delivery had also succeeded the same logical batch lands twice.

`force_flush=True` is a per-publish latency knob. Use it for the first delta or punctuated events like `RETRY` and `STATUS_CHANGE`.  Don't use it per-token or per-character: per-character `force_flush=True` is not tractable.

Hold a single subscriber iterator and consume from it rather than opening and closing subscriptions in a loop.

## Delivery semantics

**Exactly-once at the execution layer.** Each `(publisher_id, sequence)` batch lands in the Workflow's event log at most once, even if the Signal is retried by the SDK or the network.  Dedup state is carried across Continue-As-New.

**Ordering.**
- The log imposes a single total order on all events, fixed once written: an event at offset N stays at offset N on every read.
- Within one publisher, events appear in publish order.
- Across concurrent publishers, the interleaving is whatever the Workflow saw when serializing inbound Signals; stable once recorded but not under application control.
- If event A must precede event B, publish them from the same publisher.

**Activity retries surface to subscribers.** Both attempts' events appear in the stream.  The Workflow itself only sees the successful attempt's return value; a UI subscribed to the stream will see partial output unless it dedupes.

**Conventional pattern:** an Activity on a retry attempt publishes a `RETRY` event with `force_flush=True`; the consumer clears or annotates prior-attempt output when it sees one.  Build an idempotent consumer reducer: overwrite on terminal events like `STATUS_CHANGE` or `TEXT_COMPLETE`; reset an accumulator on a sentinel like `AGENT_START` before deltas resume.

**Other failure modes.**
- Events still in a publisher's in-memory client buffer are lost if the process crashes before they ship.
- Subscribers that handle an item and crash before persisting their next offset will reprocess that item on resume.
- On `max_retry_duration` exhaustion, a `TimeoutError` raises from inside the background flusher task and terminates it; until you call `await client.flush()` or exit the `async with` block, subsequent publishes accumulate with no flusher to ship them.  The dropped batch is at-most-once: may or may not have reached the Workflow.

## Architecture

**Append-only in-memory log inside the Workflow.** Each entry is `(topic, data)` with a monotonically increasing global offset.  Subscribers maintain their own cursor; each long-poll receives the next range past it.  The log is replay-safe and carried across Continue-As-New via `WorkflowStreamState`.

**Two mechanisms bound log growth, and they do different jobs:**
- `truncate(up_to_offset)` drops entries from the in-memory log (and from the carried CAN payload). It does **not** remove publish Signals already recorded in history.
- **Continue-As-New** starts a fresh history. This is the only way to shrink history; truncate alone cannot.

A subscriber whose offset falls below the new base after `truncate()` is silently advanced; the iterator does not raise, but the subscriber may re-receive items already in the log past the new base.

**Wire-level handler names** (registered when you construct a `WorkflowStream`):
- `__temporal_workflow_stream_publish` — Signal that receives batched publishes.
- `__temporal_workflow_stream_poll` — long-poll Update that subscribers use.
- `__temporal_workflow_stream_offset` — Query that reports the current head offset.

**Poll responses are capped at roughly 1 MB**, by accumulating items until the next would exceed the budget.  A single item that exceeds 1 MB on its own is admitted unconditionally; offload via [External Storage](https://docs.temporal.io/external-storage).

**Batch dedup applies at the Signal layer, not the Activity layer.**  When Temporal retries the Activity, the retried execution constructs a new `WorkflowStreamClient` with its own client id, so every Activity attempt is a fresh publisher whose batches will not deduplicate against the prior attempt's.

## Gotchas

- **`WorkflowStreamClient` is asyncio-only.** The client buffer is mutated on the publish path and read from the flusher inside a single event loop. Don't call `publish()` from a worker thread.
- **First-activation handler race.** On the very first activation a publish Signal can be queued before class-level `@workflow.signal` or `@workflow.update` handlers have run.  The fix: make the handler `async def` and `await` once before reading state. Use `asyncio.sleep(0)` — a no-op yield that adds no history events.  **Do not** substitute `workflow.sleep(0)` — it records a timer event.
- **Type bindings are per-instance.** Each `WorkflowStream` and each `WorkflowStreamClient` records topic types only for its own instance. If two publishers bind the same topic name to different types, the mismatch is not caught at publish; the subscriber gets a decode error on events from the mismatched publisher.

## See also

- [Workflow Streams samples (samples-python)](https://github.com/temporalio/samples-python/tree/main/workflow_streams) — basic publish/subscribe, reconnecting subscribers, external publishers, bounded logs.
- [`temporalio.contrib.workflow_streams` API reference](https://python.temporal.io/temporalio.contrib.workflow_streams.html).
- `references/python/patterns.md` — Signals/Queries/Updates primitives this builds on.
- `references/python/ai-patterns.md` — LLM patterns.
