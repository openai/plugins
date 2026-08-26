# Worker Health

Diagnose worker-side failures that surface as tasks not being picked up, picked up slowly, or dropped because no worker is actually connected to the right task queue. This file scopes to the worker-polling surface — the gap between "a task is enqueued on a Task Queue" and "a Worker Process dequeues it" — and to the direct symptoms of worker saturation (task slots, sticky cache, heartbeat).

Prerequisite: layers 1–4 already succeed. If the worker cannot connect or cannot authenticate, its pollers will never register and every symptom here is secondary — rule those out via [connectivity.md](connectivity.md), [certificates.md](certificates.md), [authentication.md](authentication.md) first.

Out of scope here:
- Pending activity / pending child / pending signal inside a specific Workflow Execution → [workflow-stuck.md](workflow-stuck.md)
- Non-determinism / replay errors / `WorkflowTaskFailed` loops → [non-determinism.md](non-determinism.md)
- gRPC `RESOURCE_EXHAUSTED` / server-side throttling → [rate-limits.md](rate-limits.md)
- DNS / TCP / endpoint / TLS / auth → earlier layers
- SDK-specific worker knob names and tuning targets — described here as concepts only; ground-truth for the API names lives in each SDK's worker docs, not in this skill

## Table of Contents

- [What "no pollers" looks like](#what-no-pollers-looks-like)
- [Inspecting a Task Queue with `temporal task-queue describe`](#inspecting-a-task-queue-with-temporal-task-queue-describe)
- [Schedule-to-start latency](#schedule-to-start-latency)
- [Worker task slots](#worker-task-slots)
- [Sticky Execution and sticky cache](#sticky-execution-and-sticky-cache)
- [Worker heartbeating, restarts, and disconnects](#worker-heartbeating-restarts-and-disconnects)
- [Cloud Namespace-level poller limits](#cloud-namespace-level-poller-limits)
- [Worker log signatures](#worker-log-signatures)
- [Quick routing](#quick-routing)

## What "no pollers" looks like

**Symptom shape:** a workflow or activity has been enqueued on a Task Queue, but no Worker picks it up. The classic server-side confirmation is that `temporal task-queue describe` returns no recent pollers for that queue and type.

The server's view of liveness for a Worker polling a Task Queue is time-based: "The Temporal Server records each poll request time. A `LastAccessTime` over one minute may indicate the Worker is at capacity or has shut down. Temporal Workers are removed if 5 minutes have passed since the last poll request." So "no pollers" can mean any of:

- No worker process is reaching the frontend on this Task Queue at all.
- Workers reached the frontend historically but have been silent > 5 minutes, so their poller entries have aged out.
- Workers are polling a *different* queue (name mismatch: `foo` vs `foo-prod` vs `foo ` with trailing whitespace) or a different Namespace.
- Workers connect and authenticate, then fail before the poll loop — crash on startup, deadlock, or TLS/auth rejection silently producing a reconnect loop.

This is a discrimination problem: the triage task is to separate "no worker was ever started" from "the worker is running but pointed somewhere else" from "the worker is running but blocked." The tools below address each.

## Inspecting a Task Queue with `temporal task-queue describe`

The authoritative worker-side view from outside the worker process is `temporal task-queue describe`, which reports "a list of active Workers that have recently polled a Task Queue."

### Minimal invocation

```bash
temporal task-queue describe \
    --task-queue YourTaskQueue
```

Workflow and Activity polling happen on separate queues internally; filter with `--task-queue-type` (`workflow`, `activity`, or `nexus`):

```bash
temporal task-queue describe \
    --task-queue YourTaskQueue \
    --task-queue-type "activity"
```

 Flag: `--task-queue-type` accepts `workflow`, `activity`, `nexus`, and defaults to reporting all types.

### Statistics the describe call returns

Per the CLI docs, a describe call without `--disable-stats` returns the following Task Queue statistics:

- `ApproximateBacklogCount` — approximate number of tasks backlogged. "May count expired tasks but eventually converges to the right value."
- `ApproximateBacklogAge` — approximate age of the oldest backlog task in seconds.
- `TasksAddRate` — approximate rate at which tasks are being added, averaged over the last 30 seconds.
- `TasksDispatchRate` — approximate rate at which tasks are being dispatched, averaged over the last 30 seconds.
- `BacklogIncreaseRate` — roughly `TasksAddRate − TasksDispatchRate`; docs note this is "accurate for backlogs older than a few seconds" even though the component rates can be off because of sync-matched and sticky dispatch.

These statistics are the server's view of matching-service throughput; combine them with the poller list (below) to answer "is there a worker attached, and is it keeping up?"

### Reading the pollers field

The textual output includes a list of Worker identities that have recently polled the queue. The identifier Temporal reports is a Worker Identity, and by default "Temporal SDKs set a Worker Identity to `${process.pid}@${os.hostname()}`". A "recent" poller is one whose `LastAccessTime` is within 5 minutes.

Interpretation matrix:

| Observation | What it suggests |
|---|---|
| No pollers at all | No Worker reached the frontend for this queue+type within the last 5 minutes. |
| Pollers present, `LastAccessTime` > ~1 minute, no tasks moving | Docs note this "may indicate the Worker is at capacity or has shut down." |
| Pollers present, recent, backlog still growing | Sizing or per-task-failure issue — see [Schedule-to-start latency](#schedule-to-start-latency) and [Worker task slots](#worker-task-slots) below. |
| Pollers present but identities don't match the worker fleet the user expects | Worker versioning / Build ID routing — re-run with versioning-aware flags (below). |

### Reachability and versioning

On the same `describe` call you can request reachability information, which reports whether a given Build ID can be reached by new Workflows, only by closed Workflows, or is unreachable:

```bash
temporal task-queue describe \
    --task-queue YourTaskQueue \
    --select-build-id "YourBuildId" \
    --report-reachability
```

 Relevant flags for versioning discrimination:

| Flag | Purpose |
|---|---|
| `--select-build-id` | Filter the Task Queue describe results to one or more Build IDs. |
| `--select-unversioned` | Include the unversioned queue. |
| `--select-all-active` | Include all "active" versions (recent polls or new tasks). |
| `--report-reachability` | Display task reachability. Docs note "task reachability status is deprecated in favor of Drainage Status (ie. of a Drained or Draining Worker Deployment Version) and will be removed in a future release." |
| `--report-config` | Include Task Queue rate-limit configuration. |
| `--legacy-mode` | Fallback for servers that do not support rules-based worker versioning; "only provides pollers info." |
| `--disable-stats` | Suppress the statistics listed above. |

If the user is running Worker Deployments, the per-version worker view is `temporal worker deployment describe-version`, which reports "the task queues polled by workers in this Deployment Version, or drainage information required to safely decommission workers". Adding `--report-task-queue-stats` reports per-task-queue stats for that version.

### Worker-level describe and list

Separate from Task Queue introspection, two worker-centric CLI commands surface individual Worker instances connected to the server:

```bash
temporal worker list --namespace YourNamespace --query 'TaskQueue="YourTaskQueue"'
temporal worker describe --namespace YourNamespace --worker-instance-key YourKey
```

 These depend on Worker heartbeating being enabled (see [Worker heartbeating](#worker-heartbeating-restarts-and-disconnects) below); if heartbeating is disabled, "features that provide the list of active Workers and information about those Workers to show missing or inaccurate information."

## Schedule-to-start latency

The primary *latency* signal for "tasks are being enqueued but not picked up promptly" is the SDK's schedule-to-start metric, split by task kind:

- `temporal_workflow_task_schedule_to_start_latency` — "the time between when a [Workflow Task](https://docs.temporal.io/tasks#workflow-task) is scheduled (enqueued) and when it is picked up by a Worker for processing."
- `temporal_activity_schedule_to_start_latency` — "the time between when an [Activity Task](https://docs.temporal.io/tasks#activity-task) is scheduled (enqueued) and when it is picked up by a Worker for processing."

Both are Worker-reported SDK metrics, available as histograms (`_bucket`, `_sum`, `_count`). Per the Cloud worker-health guide, "This latency should be very low, close to zero. Any higher value indicates a bottleneck", with example alert thresholds of ">200ms for your p99 value" and ">100ms for your p95 value."

### Causes documented for high schedule-to-start latency

The performance-bottlenecks troubleshooting page lists, for both the Workflow-Task and Activity-Task variants:

- **Insufficient Worker capacity.** "If there aren't enough Workers or if the Workers are overloaded, they may not be able to pick up Tasks quickly enough."
- **Worker configuration issues.** "Improperly configured Workers, such as having too few pollers or Task slots, can lead to increased latency."
- **Network latency.** "Workers in a different region from the Temporal cluster, or large payload size, can introduce additional latency."
- Activity-specific: **Task Queue configuration.** "Setting `TaskQueueActivitiesPerSecond` too low can limit the rate at which Activities are started, leading to increased Schedule-to-start latency." This is client/worker-imposed throttling, not server throttling — the symptom is latency, not `RESOURCE_EXHAUSTED`. The discrimination against server-side throttling is covered in [rate-limits.md → Server throttled me vs. client throttled itself](rate-limits.md#server-throttled-me-vs-client-throttled-itself).
- Workflow-specific: **High Workflow lock latency.** "If many updates are made to a single execution, this can cause Workflow lock latency, which in turn affects the Schedule-to-start latency. Reduce the rate of Signals."

### Cloud-side counterparts

On Cloud, two server-visible metric families let you cross-check without pulling SDK metrics:

- `temporal_cloud_v1_approximate_backlog_count` — "Approximate number of tasks pending in a task queue. Started Activities are not included in the count as they have been dequeued from the task queue."
- No direct Cloud-side "no poller" metric exists. Use `temporal_cloud_v1_approximate_backlog_count` rising while poll success rate is zero as the proxy signal for the "no poller" case in [What "no pollers" looks like](#what-no-pollers-looks-like). The self-hosted equivalent is `no_poller_tasks`.
- Sync-match ratio: `temporal_cloud_v1_poll_success_sync_count / temporal_cloud_v1_poll_success_count`. The Cloud worker-health page targets ">95%, but preferably >99%"; a drop indicates workers are not on hand to sync-match new tasks.

See [Cloud Namespace-level poller limits](#cloud-namespace-level-poller-limits) for the related *greedy-worker* signal (poll timeouts).

## Worker task slots

A Worker Entity has a bounded number of concurrent Task execution slots per task kind. When those slots saturate, even a well-connected Worker stops picking up new Tasks, and the symptom is identical to "too few Workers": rising schedule-to-start latency.

The worker-side gauge is `temporal_worker_task_slots_available`: "The total number of Workflow, Activity, Local Activity, or Nexus Task execution slots that are currently available. Use the `worker_type` key to differentiate execution slots." Cloud worker-health documents the monitoring target: "The `temporal_worker_task_slots_available` metric should always be >0."

Docs call out two common depletion patterns:

- **Workflow-Worker slot depletion** — usually driven by inbound Workflow Task load exceeding the configured cap, or by elevated `temporal_workflow_task_execution_latency` / `workflow_task_replay_latency` holding slots longer.
- **Activity-Worker slot depletion** — docs' first-listed cause is "Blocked Activities and Zombie Activities ... when an Activity times out (hits its `StartToClose` or `HeartbeatTimeout` timeout) and has stopped Heartbeating but continues to run, occupying some or all the slots as more retries occur." A companion gauge, `temporal_worker_task_slots_used`, surfaces how many slots are in use.

The *configuration* knobs that set these slot caps differ by SDK; the Cloud worker-health page refers to `maxConcurrentWorkflowTaskExecutionSize` and `maxConcurrentActivityExecutionSize` as the generic names, and the Worker tuning reference documents the per-SDK defaults (e.g., Go 1,000; Java 200; TypeScript 40 / 100; Python 100; .NET 100). For SDK-specific API names and tuning, follow `/develop/worker-performance` and `/develop/worker-tuning-reference` rather than guessing.

The triage-layer conclusion is: confirm slot availability is non-zero over the period the task was stuck; if it is chronically zero, the ceiling is the Worker, not the server.

## Sticky Execution and sticky cache

**Concept:** "Workers cache the state of the Workflow they execute. ... Temporal employs a performance optimization known as 'Sticky Execution', which directs Workflow Tasks to the same Worker that previously processed tasks for a specific Workflow Execution." Each Worker gets an "automatically-generated" Sticky Queue name exclusive to that Worker.

**Failure mode relevant to triage:** if the Worker fails to start a queued Workflow Task in its Sticky Queue "shortly after it's scheduled (within five seconds by default), the Temporal Service disables stickiness for that Workflow Execution" and reschedules on the original Task Queue. A related trigger: if a Workflow Task fails, "the Worker removes that Workflow Execution from its cache ... which invalidates the Sticky Execution."

Key metrics for cache-pressure diagnosis:

- `temporal_sticky_cache_size` — "Current cache size, expressed in number of Workflow Executions."
- `temporal_sticky_cache_total_forced_eviction` / `_total` — counter for forced evictions. "A 'forced eviction' ... means that a Workflow Execution was removed from the cache before it completed, typically because the cache was full and needed to make room for other Workflow Executions." Available in the Go SDK and the Java SDK.
- `temporal_sticky_cache_hit_total` / `temporal_sticky_cache_miss_total` — sticky match versus Event-History-replay.

The Cloud worker-health guidance: "The `sticky_cache_size` should report less than or equal to your `WorkflowCacheSize` value. Also, `sticky_cache_total_forced_eviction` should not be reporting high numbers (relative)." The `WorkflowCacheSize` / `StickyWorkflowCacheSize` per-SDK defaults are in the Worker tuning reference (Go 10,000; Java 600; TypeScript dynamic; Python 1,000; .NET 10,000).

Triage-layer conclusions:

- A workflow that keeps moving but with elevated schedule-to-start latency and a high sync-match-miss or a high forced-eviction rate is starving the cache, not a pollers-missing problem.
- A workflow that was Sticky to a Worker that later died or restarted will wait up to five seconds before the Sticky-queue scheduler gives up and the Task returns to the shared queue.

## Worker heartbeating, restarts, and disconnects

Temporal Workers send a heartbeat to the Server on an interval. Per the Cloud worker-health guide (the feature is "in Public Preview" as documented): "Workers send a heartbeat to Temporal Server every 60 seconds by default. This heartbeat serves to provide liveness and configuration data from the Worker to the Server." Heartbeats feed the `temporal worker list` / `temporal worker describe` views; "Disabling the Worker heartbeat will cause features that provide the list of active Workers and information about those Workers to show missing or inaccurate information."

Heartbeating is distinct from Task Queue polling. A Worker process can stop polling (or start failing polls) for reasons that do not appear in its heartbeat. Consequently:

- If `temporal task-queue describe` shows no pollers but `temporal worker list --query 'TaskQueue="..."'` shows recent Workers, the Workers are alive and heartbeating but not polling this queue (name mismatch, task-queue-type mismatch, or they've exhausted slots).
- If `temporal worker list` is empty for a Namespace where the user insists workers are running, the likeliest triage question is "is heartbeating disabled?" or "do the workers predate an SDK version with heartbeating available?" Per the Cloud worker-health page, heartbeating is available in specific SDK versions: Go SDK v1.41.0+, Java SDK v1.35.0+, Python SDK v1.20.0+, TypeScript SDK v1.14.0+, .NET SDK v1.10.0+, Ruby SDK v1.1.0+.

Restart-loop / container-kill failure shapes are operating-system and orchestrator concerns, not Temporal-specific errors — the triage-layer observation is that a Worker in a restart loop will never sustain the 5-minute `LastAccessTime` window the server needs to keep it in the poller list. If the Worker container is crash-looping, the symptom will alternate between "pollers present briefly" and "pollers absent" at the restart cadence.

## Cloud Namespace-level poller limits

Cloud caps the *total* pollers a Namespace can hold concurrently: "Temporal Cloud limits each Namespace to 20,000 Activity pollers and 20,000 Workflow Task pollers concurrently." Per the same section, "Each SDK offers a way to configure Workers for per-Worker maximum Activity and Workflow Task pollers. Those values do not affect the global Namespace limit." Saturating this cap is a Namespace-level policy limit — it falls under [rate-limits.md](rate-limits.md) in terms of gRPC surface behavior.

A related symptom is *too many* pollers for the load: the Poll Success Rate, computed as `temporal_cloud_v1_poll_success_count / (temporal_cloud_v1_poll_success_count + temporal_cloud_v1_poll_timeout_count)`, falling well below the documented target of ">90% in most cases of systems with a steady load. For high volume and low latency, try to target >95%." The Cloud guide's interpretation: low poll success + low schedule-to-start latency + low Worker host utilization together suggest "you might have too many Workers."

Self-hosted has no equivalent documented Namespace-wide poller cap in this skill's primary sources; see `docs/references/dynamic-configuration.mdx` for per-service RPS and capacity keys and [rate-limits.md → Self-hosted: service-level RPS via dynamic configuration](rate-limits.md#self-hosted-service-level-rps-via-dynamic-configuration).

## Worker log signatures

Patterns to watch for in the Worker's own process logs when correlating with `task-queue describe` output. Each row points to the file that actually owns the diagnostic.

| Log pattern (shape — exact wording is SDK/version-specific) | Interpretation | Route |
|---|---|---|
| gRPC `UNAUTHENTICATED` / `PERMISSION_DENIED` at worker startup or on poll RPCs | Identity or authorization rejected after TLS; Worker never registers as a poller | [authentication.md](authentication.md) |
| `x509: ...` / `tls: ...` | TLS handshake or cert validation failed before gRPC | [certificates.md](certificates.md) |
| `no such host` / `connection refused` / `i/o timeout` | DNS / TCP problem; poll loop never engages | [connectivity.md](connectivity.md) |
| gRPC `RESOURCE_EXHAUSTED` | Server throttling the Worker's RPCs (polls or other) | [rate-limits.md](rate-limits.md) |
| `temporal_long_request_failure` elevated on `PollWorkflowTaskQueue` / `PollActivityTaskQueue` | Long-poll RPCs failing; docs note this "is often indicated by a `ResourceExhausted` status code" when caused by rate limiting, but also covers network issues and server errors | [rate-limits.md](rate-limits.md) / [connectivity.md](connectivity.md) depending on the `status` / `code` tag on the metric |
| "Deadlock detected during Workflow run" / `TMPRL1101` | Workflow Task ran longer than the SDK's deadlock-detection threshold | [non-determinism.md](non-determinism.md) and the relevant SDK docs |
| Replay-divergence messages from the SDK (non-determinism) | Re-execution of recorded history no longer matches the compiled Workflow | [non-determinism.md](non-determinism.md) |
| Unhandled exception / panic / OOM kill at process level, no Temporal-specific error | Runtime-level failure, not a Temporal error string; the Worker will drop out of the poller list until restarted | OS / runtime tooling; not covered in this skill |

Correlate these with `task-queue describe` output. Agreement (log says "polling" and describe shows a fresh poller) confirms the Worker is healthy at the server's view. Disagreement is itself a diagnostic signal — e.g., log says "connected" but `task-queue describe` is empty → likely a Namespace or Task Queue name mismatch, or heartbeating is disabled so `worker list` is silent while polling still works.

## Quick routing

| Symptom | Go to |
|---|---|
| `temporal task-queue describe` returns no pollers | [What "no pollers" looks like](#what-no-pollers-looks-like) |
| `temporal_cloud_v1_approximate_backlog_count` rising with zero poll success on Cloud | [Schedule-to-start latency](#schedule-to-start-latency) (proxy for no-poller on Cloud; no direct no-poller metric exists) |
| Pollers are present but `LastAccessTime` stale | [What "no pollers" looks like](#what-no-pollers-looks-like) and [Worker heartbeating](#worker-heartbeating-restarts-and-disconnects) |
| `temporal_workflow_task_schedule_to_start_latency` or `temporal_activity_schedule_to_start_latency` spike | [Schedule-to-start latency](#schedule-to-start-latency) |
| `temporal_worker_task_slots_available` hits 0 | [Worker task slots](#worker-task-slots) |
| Elevated `temporal_sticky_cache_total_forced_eviction` | [Sticky Execution and sticky cache](#sticky-execution-and-sticky-cache) |
| `temporal worker list` is empty but workers are running | [Worker heartbeating](#worker-heartbeating-restarts-and-disconnects) |
| Low Poll Success Rate with low schedule-to-start latency and low host utilization | [Cloud Namespace-level poller limits](#cloud-namespace-level-poller-limits) — likely too many Workers |
| `RESOURCE_EXHAUSTED` on poll RPCs | [rate-limits.md](rate-limits.md) |
| Workflow Execution is stuck with a pending activity / child / signal | [workflow-stuck.md](workflow-stuck.md) |
| Replay errors / non-determinism in Worker logs | [non-determinism.md](non-determinism.md) |

See the whole-stack picture in [diagnostic-ladder.md](diagnostic-ladder.md).
