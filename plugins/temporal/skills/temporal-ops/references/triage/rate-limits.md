# Rate Limits

Diagnose gRPC `RESOURCE_EXHAUSTED` against Temporal — what budget was exceeded, which party enforced it, and how to tell from the error text and Cloud signals. This file covers one specific gRPC status code; it does not cover every "things feel slow" symptom.

Prerequisite: `RESOURCE_EXHAUSTED` is returned *after* the connection, TLS, and auth layers have succeeded. If you do not yet know that the caller is reaching the frontend, rule out layers 1–3 first via [connectivity.md](connectivity.md), [certificates.md](certificates.md), and [authentication.md](authentication.md).

Out of scope here:
- DNS / TCP / endpoint → [connectivity.md](connectivity.md)
- TLS / x509 → [certificates.md](certificates.md)
- `UNAUTHENTICATED` / `PERMISSION_DENIED` → [authentication.md](authentication.md)
- Task-queue backlog, poller count, worker health → [worker-health.md](worker-health.md)
- Workflow stuck in a pending state (pending activity / pending child / pending signal) → [workflow-stuck.md](workflow-stuck.md)
- Ambiguous `context deadline exceeded` that callers sometimes confuse with throttling → [runtime-errors.md](runtime-errors.md)

## Table of Contents

- [What RESOURCE_EXHAUSTED means and what it does not](#what-resource_exhausted-means-and-what-it-does-not)
- [Temporal Cloud: APS, RPS, OPS and capacity modes](#temporal-cloud-aps-rps-ops-and-capacity-modes)
- [Self-hosted: service-level RPS via dynamic configuration](#self-hosted-service-level-rps-via-dynamic-configuration)
- [Server throttled me vs. client throttled itself](#server-throttled-me-vs-client-throttled-itself)
- [Identifying which limit was hit](#identifying-which-limit-was-hit)
- [What RESOURCE_EXHAUSTED is not](#what-resource_exhausted-is-not)
- [Quick routing](#quick-routing)

## What RESOURCE_EXHAUSTED means and what it does not

`RESOURCE_EXHAUSTED` is one of the 17 canonical gRPC status codes. In the spec it means "Some resource has been exhausted, perhaps a per-user quota, or perhaps the entire file system is out of space." On Temporal, it is the code the frontend returns when a request is **throttled against a configured rate limit** rather than rejected for identity or input reasons.

Key scoping facts:

- It is not `UNAVAILABLE` (connectivity / transient peer failure), not `DEADLINE_EXCEEDED` (the caller's deadline fired), and not `PERMISSION_DENIED` (identity known, action forbidden). Mapping a rate-limit symptom onto one of those codes is a common triage mistake — see [authentication.md → UNAUTHENTICATED vs PERMISSION_DENIED](authentication.md#unauthenticated-vs-permission_denied) for the boundary.
- Temporal Cloud documents the server-returned value as `ResourceExhausted`: "When throttled, the server returns a `ResourceExhausted` gRPC error." The gRPC wire name is `RESOURCE_EXHAUSTED`; client SDKs surface it as an `ResourceExhausted`-named exception. Both refer to the same code.
- On self-hosted, the same code is emitted when the frontend's RPS budget is exceeded: "Exceeding these limits results in `ResourceExhaustedError`."

## Temporal Cloud: APS, RPS, OPS and capacity modes

Cloud enforces three **per-Namespace** throughput limits, each of which can independently produce `RESOURCE_EXHAUSTED`:

| Limit | Default | Scope | What it counts |
|---|---|---|---|
| **Actions per second (APS)** | 500 APS | Namespace | Billable [Actions](https://docs.temporal.io/cloud/actions) — starts, Signals, Updates, Activity starts / retries / heartbeats, Timers, etc.  |
| **Requests per second (RPS)** | 2000 RPS | Namespace | gRPC requests to the frontend. A lower-level measure of load at the service level. |
| **Operations per second (OPS)** | 4000 OPS | Namespace | Operations (user-driven or Temporal-internal) that hit the Temporal Server on the user's behalf. See the [operations list](https://docs.temporal.io/references/operation-list) for the set. |

All three have the same **automatic scaling** behavior under the default **On-Demand Capacity** mode: the limit "automatically increases (and decreases) based on the last 7 days of [APS/RPS/OPS] usage. Will never go below the default limit." The On-Demand formula is documented as "the lesser of 4 × APS Average or 2 × APS P90 over the past 7 days."

**Provisioned Capacity** replaces the automatic envelope with a fixed allocation, expressed in Temporal Resource Units (TRUs); each TRU supplies 500 APS / 1500 RPS / 4000 OPS. TRUs are set via UI, `tcld namespace capacity update`, or the `UpdateNamespace` API. Adjustments are hourly.

There are additional, narrower Namespace-scoped rate limits that also surface as `RESOURCE_EXHAUSTED`:

- **Schedules rate limit**: 10 schedule requests per second, per Namespace, not configurable via UI — raise via a support ticket. The Cloud metric `temporal_cloud_v1_schedule_rate_limited_count` tracks workflows delayed due to this limit.
- **Visibility API rate limit**: 30 Visibility API calls per second per Namespace; not configurable. "All read calls are subject to the Visibility API rate limit."
- **Concurrent Task pollers**: 20,000 Activity pollers and 20,000 Workflow Task pollers per Namespace concurrently. Per-Namespace poll saturation falls under poller health — see [worker-health.md](worker-health.md).

### Throttling behavior (Cloud)

From the Cloud limits reference:

- **Priority-based throttling.** "Low-priority operations are throttled first. Higher-priority operations like `StartWorkflowExecution`, `SignalWorkflowExecution`, and `UpdateWorkflowExecution` continue to go through when possible."
- **Throttling latency.** "Rate limiting is not instantaneous, so usage may briefly exceed your limit before throttling takes effect."
- **SDK retry by default.** "SDK clients automatically retry these based on the default gRPC retry policy."
- **Persistent throttling fails the call.** "If throttling persists beyond the SDK's retry limit, client calls fail."
- **Per the Cloud docs, Actions that are external to the core Temporal service do not contribute to APS** — e.g. [Export](https://docs.temporal.io/cloud/export) and Capacity-related Actions.

## Self-hosted: service-level RPS via dynamic configuration

On a self-hosted cluster, per-Namespace and per-host rate limits are dynamic-configuration keys. The docs name these explicitly as producers of `ResourceExhaustedError`: "Exceeding these limits results in `ResourceExhaustedError`."

Commonly referenced frontend keys (defaults from `docs/references/dynamic-configuration.mdx`, Temporal server v1.21; verify against the version you run):

| Key | Default | What it limits |
|---|---|---|
| `frontend.rps` | 2400 | Requests per second accepted by each Frontend Service host |
| `frontend.namespaceRPS` | 2400 | Requests per second per Namespace, per Frontend host |
| `frontend.globalNamespaceRPS` | 0 (disabled) | Cluster-wide per-Namespace RPS, distributed across Frontend hosts. When set, overrides `frontend.namespaceRPS`. |
| `history.rps` | 3000 | Per History Service host |
| `matching.rps` | 1200 | Per Matching Service host |

Defaults shift across server versions. Before quoting a number to a user, check their server version against `docs/references/dynamic-configuration.mdx` or the release notes.

Persistence-store QPS keys (`frontend.persistenceMaxQPS`, `history.persistenceMaxQPS`, etc.) are evaluated synchronously and produce latency / timeouts rather than `RESOURCE_EXHAUSTED` to the client: "If the number of queries made to the Persistence store exceeds the dynamic configuration value, you will see latencies and timeouts on your tasks." Persistence saturation therefore usually surfaces as `DEADLINE_EXCEEDED`, not `RESOURCE_EXHAUSTED` — see [runtime-errors.md](runtime-errors.md).

## Server throttled me vs. client throttled itself

`RESOURCE_EXHAUSTED` on the wire is always server-emitted. But "why is my caller falling behind?" can also be the caller throttling *itself* — those two look alike from a dashboard but need different fixes.

- **Server-enforced limit hit → `RESOURCE_EXHAUSTED` returned to the caller.** Cloud APS/RPS/OPS; self-hosted `frontend.rps`/`frontend.namespaceRPS`; Cloud Schedules limit; Visibility API limit. The SDK default retry policy retries the RPC with exponential backoff until its retry budget is exhausted, after which the call fails to the application.
- **Client-side throttling (no `RESOURCE_EXHAUSTED` on the wire).** A worker may be limiting its own rate via SDK settings — e.g. `TaskQueueActivitiesPerSecond` or `(Max)WorkerActivitiesPerSecond`. These produce Activity schedule-to-start latency, not `RESOURCE_EXHAUSTED`: "Setting `TaskQueueActivitiesPerSecond` too low can limit the rate at which Activities are started, leading to increased Schedule-to-start latency." If the reported error is high `temporal_activity_schedule_to_start_latency` without `RESOURCE_EXHAUSTED`, the problem is worker-side — go to [worker-health.md](worker-health.md).

A quick discriminator: inspect the failed RPC's gRPC status. If the code is literally `RESOURCE_EXHAUSTED`, the server throttled it. If the RPC never left the worker or returned some other status, the ceiling is client-side.

Rule of thumb: **retries themselves count against the budget**. A caller that retries `RESOURCE_EXHAUSTED` without backoff makes the situation worse. The default gRPC retry policy used by the SDKs already includes backoff; custom clients that reimplement retry need to do the same.

## Identifying which limit was hit

Two sources of signal: the gRPC error itself and the Cloud metrics endpoint.

### From the error

`RESOURCE_EXHAUSTED` carries a free-text message whose wording varies by server version and by which internal limiter fired, so rely on the gRPC code plus the metric label rather than pattern-matching the text. Which label depends on the metric family:

| Environment | Metric | Label to split by |
|---|---|---|
| Cloud, v1 metrics | `temporal_cloud_v1_resource_exhausted_error_count` | `operation` |
| Cloud, v0 metrics | `temporal_cloud_v0_resource_exhausted_error_count` | `resource_exhausted_cause`, "Cause for resource exhaustion"  |
| Self-hosted | `service_errors_resource_exhausted` | `resource_exhausted_cause` |

Self-hosted: the `deadline-exceeded` troubleshooting page recommends `sum(rate(service_errors_resource_exhausted{}[1m])) by (resource_exhausted_cause)` to check for `RpsLimit`, `ConcurrentLimit`, and `SystemOverloaded` causes.

One documented message string does exist: per-Workflow lock contention appears in Service logs as `Workflow is busy.` That is a *different condition* from account-limit throttling and is not fixed by raising limits — see [runtime-errors.md → Workflow lock contention (BusyWorkflow)](runtime-errors.md#workflow-lock-contention-busyworkflow).

### From Cloud metrics

Temporal Cloud exposes an OpenMetrics endpoint whose limit / count / throttle triples let you tell "which budget is saturating" without guessing.

| Budget | Limit metric | Count metric | Throttle metric |
|---|---|---|---|
| Actions | `temporal_cloud_v1_action_limit`  | `temporal_cloud_v1_total_action_count`  | `temporal_cloud_v1_total_action_throttled_count`  |
| Frontend gRPC requests | `temporal_cloud_v1_service_request_limit`  | `temporal_cloud_v1_service_request_count` | `temporal_cloud_v1_service_request_throttled_count`  |
| Operations | `temporal_cloud_v1_operations_limit`  | `temporal_cloud_v1_operations_count`  | `temporal_cloud_v1_operations_throttled_count`  |

The v1 metrics are pre-computed per-second rates aggregated over a 1-minute window, so a sustained non-zero value on a `*_throttled_count` metric is the definitive Cloud signal that a specific budget is being hit.

**Do not read `temporal_cloud_v1_resource_exhausted_error_count` as the throttling signal.** The throttle metrics in the table above are. "Tracking trends against your account limits is the most important throttling signal to monitor. Unlike Resource Exhaustion, which usually self-heals through retries, hitting a limit slows or stalls progress until the workload backs off or your capacity is increased." The v1 resource-exhausted metric explicitly "does not include throttling due to Namespace limits"; it counts bursts against a single resource — a Namespace, Task Queue, or Workflow ID — that the resource could not absorb in the moment, and persistent non-zero values indicate a hot resource. Route those to [runtime-errors.md → Workflow lock contention (BusyWorkflow)](runtime-errors.md#workflow-lock-contention-busyworkflow), which is the most common cause.

For the v0 metric family, the equivalent is `temporal_cloud_v0_resource_exhausted_error_count`, "gRPC requests received that were rate-limited by Temporal Cloud, aggregated by cause."

For Provisioned Capacity namespaces, the *envelope* metrics (`temporal_cloud_v1_action_on_demand_envelope_limit`, `temporal_cloud_v1_operations_on_demand_envelope_limit`, `temporal_cloud_v1_service_request_on_demand_envelope_limit`) show what the limit would be under On-Demand. Compare these against the currently provisioned limit metric to evaluate whether the provisioned allocation is too tight or too loose.

### Without metrics (UI-only)

When the caller has no metrics pipeline, the Cloud UI shows a recent APS usage summary on the Namespace's *Manage Capacity* panel, which can confirm whether the Namespace is actually running hot.

## What RESOURCE_EXHAUSTED is not

These are the common false positives — they look superficially similar but are **not** `RESOURCE_EXHAUSTED`:

- **Worker task-queue backlog.** If Activity Tasks or Workflow Tasks sit in the queue without being picked up, the symptom is high `temporal_workflow_task_schedule_to_start_latency` or `temporal_activity_schedule_to_start_latency`. These are caused by "insufficient Worker capacity" or "worker configuration issues (too few pollers or task slots)" , not by server rate limiting. Diagnosis: see [worker-health.md](worker-health.md).
- **Workflow stuck with pending activities / children / signals.** The workflow made a Command (`ScheduleActivityTask`, `StartChildWorkflowExecution`, etc.), but nothing moves forward. This is a worker / queue / dependency issue, not a RESOURCE_EXHAUSTED condition. See [workflow-stuck.md](workflow-stuck.md).
- **`context deadline exceeded`.** The caller's own deadline fired before the server responded. This can *coincide* with a saturated namespace (the server-side `temporal_cloud_v0_resource_exhausted_error_count` may be non-zero), but the wire code received by the client is `DEADLINE_EXCEEDED`, not `RESOURCE_EXHAUSTED`. See [runtime-errors.md](runtime-errors.md) and the dedicated Cloud-side guidance.
- **`temporal_long_request_failure` spikes on poll RPCs.** The performance-bottlenecks guide calls out that high `temporal_long_request_failure` may be caused by rate limiting ("often indicated by a `ResourceExhausted` status code"). But that metric is counted on the client side and aggregates all causes; confirm via the server-side throttle metric above before concluding the limiter is the root cause.
- **Per-Workflow concurrency caps.** A single Workflow Execution hitting the 2000 incomplete Activities / Signals / Child Workflows / external Workflow Cancellation requests limit fails the Command at the programming-model level; it is not a Namespace-level rate limit and not diagnosed via this file.

Per the managing-APS guide: "In Temporal Cloud, the effect of rate limiting is increased latency, not lost work. Workers might take longer to complete Workflows." Combined with the Cloud limits note about failures if throttling persists beyond the SDK's retry budget, the distinction matters: short bursts of `RESOURCE_EXHAUSTED` are normal and self-recovering; sustained throttling plus application-visible failures is what warrants capacity action.

## Quick routing

| Symptom | Go to |
|---|---|
| gRPC `RESOURCE_EXHAUSTED` on a client call to Cloud | [Temporal Cloud: APS, RPS, OPS and capacity modes](#temporal-cloud-aps-rps-ops-and-capacity-modes) and [Identifying which limit was hit](#identifying-which-limit-was-hit) |
| gRPC `RESOURCE_EXHAUSTED` from a self-hosted frontend | [Self-hosted: service-level RPS via dynamic configuration](#self-hosted-service-level-rps-via-dynamic-configuration) |
| `temporal_cloud_v0_resource_exhausted_error_count` / `temporal_cloud_v1_*_throttled_count` non-zero | Identify the specific budget via the metric triples in [Identifying which limit was hit](#identifying-which-limit-was-hit) |
| Activity / Workflow Task `schedule_to_start_latency` rising but no `RESOURCE_EXHAUSTED` | [worker-health.md](worker-health.md) |
| Workflow stuck with pending activities / children / signals | [workflow-stuck.md](workflow-stuck.md) |
| `context deadline exceeded` on caller | [runtime-errors.md](runtime-errors.md) |
| `UNAUTHENTICATED` / `PERMISSION_DENIED` | [authentication.md](authentication.md) |
| `UNAVAILABLE` with no rate-limit context | [connectivity.md](connectivity.md) and [certificates.md](certificates.md) |

See the whole-stack picture in [diagnostic-ladder.md](diagnostic-ladder.md). For concrete commands to pull these metrics and confirm a throttling hypothesis, see [recipes.md](recipes.md).
