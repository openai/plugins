# Runtime Errors

Disambiguate Temporal errors whose text does not by itself identify the layer at fault. Primary focus: `context deadline exceeded` (`DEADLINE_EXCEEDED`) and Workflow lock contention (`BusyWorkflow`). Secondary: where to route `no pollers`, `INVALID_ARGUMENT`, and unspecified `UNAVAILABLE` when the layer isn't obvious from the message alone.

Unambiguous errors are covered in the layer-specific files — link, don't duplicate:
- DNS / TCP / endpoint / PrivateLink → [connectivity.md](connectivity.md)
- TLS / x509 / mTLS alerts → [certificates.md](certificates.md)
- `UNAUTHENTICATED` / `PERMISSION_DENIED` → [authentication.md](authentication.md)
- `RESOURCE_EXHAUSTED` rate-limit anatomy → [rate-limits.md](rate-limits.md)
- Pollers / schedule-to-start / sticky cache → [worker-health.md](worker-health.md)
- Pending activities / children / signals / Workflow Task failures → [workflow-stuck.md](workflow-stuck.md)
- Blob-size / history-size limits → `docs/troubleshooting/blob-size-limit-error.mdx` (not ambiguous; the error names itself)
- Performance-bottlenecks deep dive → `docs/troubleshooting/performance-bottlenecks.mdx`

## Table of Contents

- [Why these errors are hard](#why-these-errors-are-hard)
- [Deadline exceeded](#deadline-exceeded)
- [Workflow lock contention (BusyWorkflow)](#workflow-lock-contention-busyworkflow)
- [Other frequently ambiguous errors](#other-frequently-ambiguous-errors)
- [Triage protocol](#triage-protocol)

## Why these errors are hard

`context deadline exceeded` is emitted by the Go `context` package and propagates through gRPC as `DEADLINE_EXCEEDED`. It tells you only that the caller gave up waiting — not why the response did not arrive. The Temporal troubleshooting guide lists "network interruptions, timeouts, server overload, and Query errors" as causes in the same breath, and the fix catalog spans clock skew, Frontend Service reachability, rate-limit saturation, client/worker configuration, and connection-age tuning.

`ResourceExhausted` (`RESOURCE_EXHAUSTED`) is ambiguous for a different reason: one gRPC code covers both throttling against your account limits and per-Workflow lock contention, and these are different problems with different fixes. The Cloud docs are explicit that lock contention "is contention on a single Execution, not an account limit. Increasing your Actions, Requests, or Operations per second limits does not resolve it." The discriminator is the metric breakdown, not the error text.

Treating either error as a single-layer failure is the most common triage mistake in this category. Identify the operation and the layer before prescribing a fix. Give the proposed root cause an explicit confidence label — "low confidence, next discriminating check is X" beats a guess dressed up as a diagnosis. (Confidence framing is a skill convention, not a Temporal contract.)

## Deadline exceeded

**Verbatim error shapes seen in the wild:**
- `Context: deadline exceeded` — surfaced by the Temporal troubleshooting guide.
- `rpc error: code = DeadlineExceeded desc = context deadline exceeded` — Go gRPC client.
- `Error: 4 DEADLINE_EXCEEDED: context deadline exceeded` — the `@grpc/grpc-js` TypeScript client form documented in the Temporal TS debugging guide.

**What it means:** the caller's deadline fired before a response arrived. The code is `DEADLINE_EXCEEDED` regardless of which layer failed to respond.

**Causes documented in the Temporal troubleshooting guide for `deadline-exceeded`:**

- **Clock skew** between a Worker and the Temporal Service exceeding an Activity's Start-To-Close Timeout — produces `Activity complete after timeout` alongside `Context: deadline exceeded`. Resolution: sync to NTP.
- **Frontend Service not reachable.** OSS users can check with `temporal operator cluster health --address 127.0.0.1:7233`; `grpc-health-probe` lets you probe Frontend, Matching, and History individually. Cloud users cannot access these logs directly — the guide directs them to open a support ticket with Namespace Name and sample Workflow IDs.
- **Resource-exhausted backpressure masquerading as deadline.** "A `resource exhausted` error can cause your client request to fail, which prompts the `deadline exceeded` error." Discriminator query (self-hosted metrics): `sum(rate(service_errors_resource_exhausted{}[1m])) by (resource_exhausted_cause)`, watching for `RpsLimit`, `ConcurrentLimit`, `SystemOverloaded`. For the Cloud equivalent and the `RESOURCE_EXHAUSTED` anatomy see [rate-limits.md](rate-limits.md#identifying-which-limit-was-hit).
- **Invalid client/worker configuration** (wrong server name, address, or certificate). These produce `connection refused` alongside `deadline exceeded`; the guide explicitly pairs the two. Re-run the [connectivity ladder](connectivity.md) before anything else.
- **Service just restarted / roles not yet initialized.** Wait and retry; review Workflow Execution history and server logs if it persists.
- **Self-hosted: `frontend.keepAliveMaxConnectionAge` too short** for in-flight requests — increase it and monitor server load.

**TypeScript SDK guide adds two concrete triggers for a `context deadline exceeded` at call time:**

- Network hiccup, timeout that's too short, or overloaded server.
- "Querying a Workflow Execution whose query handler causes an error can result in the query call timing out."

**Nexus-specific:** "If a Nexus handler doesn't process a start or cancel request within 10 seconds, it will receive a context deadline exceeded error, and the caller will retry, with an exponential backoff, for the ScheduleToClose duration for the overall Nexus Operation."

### Discriminating by where the call was made

**First question to ask the reporter:** which operation emitted this — workflow start, signal/update, query, a worker poll, a Nexus start/cancel, or an un-attributed log line? The answer narrows the layer.

| Operation | Likely-first check |
|---|---|
| Workflow start / signal / update / describe (RPC from a client) | Confirm DNS / TCP / TLS / auth succeed for the same endpoint from the failing environment. Start at [connectivity.md → Quick diagnostic scripts](connectivity.md#quick-diagnostic-scripts). If layers 1–4 pass, move to Frontend health and the `resource_exhausted_cause` metric. |
| Workflow start with a large input | Rule out `BlobSizeLimitError` (2 MB per individual payload, 4 MB per gRPC request).  That error is self-naming, not a bare `deadline exceeded`, but large payloads also inflate request latency (`temporal_request_latency`) per the bottlenecks guide. |
| Query | The Workflow's Query handler may itself be erroring out. Queries run in the Worker and the call is synchronous. Check Worker logs for an exception raised inside the handler; fix and redeploy. |
| Worker long-poll (`PollWorkflowTaskQueue`, `PollActivityTaskQueue`) | `temporal_long_request_failure` is counted against these poll RPCs; the bottlenecks guide lists network issues, rate limiting (often indicated by `ResourceExhausted`), and server errors as the three cause classes. Jump to [worker-health.md → Worker log signatures](worker-health.md#worker-log-signatures). |
| Nexus handler call | 10-second handler cap; see `docs/evaluate/temporal-cloud/limits.mdx` for Nexus timeout semantics. |

### PrivateLink-specific deadline exceeded

`context deadline exceeded` from a Worker or CLI going through AWS PrivateLink or GCP Private Service Connect has a common set of layer-1–3 causes. The commands below are the ones already grounded in the sibling files — reuse them rather than re-deriving.

1. **VPC-endpoint path unreachable from the client subnet.**
   ```bash
   nc -zvw10 vpce-0123456789abcdef-abc.us-east-1.vpce.amazonaws.com 7233
   ```
   If this times out, the VPC-endpoint security group is not permitting TCP/7233 from the client subnet. The exact probe command form is the one used in the Cloud connectivity guide. See [connectivity.md → PrivateLink and PSC](connectivity.md#privatelink-and-psc).
2. **TLS handshake fails because SNI is not overridden.** When connecting by the VPC-endpoint DNS name (i.e. not via private DNS), the client must set the TLS server name to the Namespace Endpoint — `<namespace>.<account>.tmprl.cloud`. The Cloud connectivity guide gives the exact env-var form: `TEMPORAL_ADDRESS=vpce-...:7233` paired with `TEMPORAL_TLS_SERVER_NAME=my-namespace.my-account.tmprl.cloud`. Full details: [certificates.md → Server name override](certificates.md#server-name-override).
3. **Private DNS missing for the region the Namespace is currently in (HA Namespaces).** After a failover, the `region.tmprl.cloud` private hosted zone must cover every region the Namespace can fail over to. Details: [ha-failover.md → PrivateLink stopped working after failover](ha-failover.md#symptom-privatelink--psc-stopped-working-after-failover).
4. **PrivateLink not enabled on the Namespace.** Verify connectivity configuration on the Namespace; if the Namespace is not configured for PrivateLink, public DNS will route the caller somewhere the VPC cannot reach.

## Workflow lock contention (BusyWorkflow)

**Error shape:** every operation that mutates a single Workflow Execution — starting it, sending a Signal, and so on — is serialized under a per-Workflow lock. When operations reach one Execution faster than that lock can be acquired, the Service rejects the excess with a `ResourceExhausted` error (`RESOURCE_EXHAUSTED`). In Service logs it appears as `Workflow is busy.` The Cloud docs name the condition **Workflow lock contention (BusyWorkflow)**; use that term when explaining it, and treat a caller's "workflow is busy" report as pointing at it.

The Cloud metric is `temporal_cloud_v1_resource_exhausted_error_count`, which increments when "a single resource (a Namespace, Task Queue, or Workflow ID) receives a burst of operations larger than that resource can absorb in the moment." Lock contention is the most common cause of resource exhaustion.

**What this is not:**
- **Not an account limit.** "This is contention on a single Execution, not an account limit. Increasing your Actions, Requests, or Operations per second limits does not resolve it." Account-limit throttling is APS / RPS / OPS on Cloud or `frontend.rps` / `frontend.namespaceRPS` self-hosted — see [rate-limits.md](rate-limits.md). The two are distinct conditions that share a gRPC code.
- **Not a Workflow failure.** A `ResourceExhausted` on a signal/update does not fail the Workflow Execution; the SDK's default gRPC retry policy retries the RPC with backoff.
- **Not "the Workflow is blocked in a useful sense."** The Workflow may be perfectly healthy; the pressure is on the lock, from the caller's side.
- **Not always worth chasing.** "At low, brief rates this error is benign because clients retry it and no progress is lost." Investigate when the rate is sustained or correlates with rising latency on the affected operations.

### Confirming lock contention

The Cloud service-health guide's protocol:

1. **Rule out account-limit throttling first.** If the throttle metrics are elevated, address that throttling before looking at lock contention — limits-driven throttling slows or stalls a workload, so it is the more important signal.  See [rate-limits.md → Identifying which limit was hit](rate-limits.md#identifying-which-limit-was-hit).
2. **If you are within limits but `temporal_cloud_v1_resource_exhausted_error_count` is still non-zero, break it down by the `operation` label.** "Lock contention concentrates on operations that target individual executions."
3. **Match the operation to the guidance below.**

**Mind the label, it differs by metric family.** The v1 Cloud metric carries only `operation`. The v0 metric carries `resource_exhausted_cause`.  Self-hosted uses `resource_exhausted_cause` on `service_errors_resource_exhausted`. Whichever family the user is on, classify from the label, not the free-text message. See [rate-limits.md → From the error](rate-limits.md#from-the-error).

### Per-operation guidance

Mapped from the Cloud service-health table.

| `operation` | What it indicates | What to do |
|---|---|---|
| `StartWorkflowExecution`, `SignalWithStartWorkflowExecution` | The same Workflow ID was started again inside the de-duplication window (about one second). The first start succeeded; the duplicate was rejected. | Usually safe to ignore. Don't retry aggressively. Look for a client path firing the duplicate start. |
| `SignalWorkflowExecution` | Signal rate to one Execution is too high. | Batch or coalesce Signals (one per N events), shard work across more Executions, or buffer Signals and drain them in the main Workflow loop. |
| `UpdateWorkflowExecution` | More than the per-execution in-flight Update limit (10) are outstanding. | Cap concurrent in-flight Updates client-side, then back off and retry. |
| `RecordActivityTaskHeartbeat` | Too many Activities heartbeating into the same Execution. | Raise the heartbeat timeout and interval; reduce how many Activities heartbeat into one Execution concurrently. |
| `RespondWorkflowTaskCompleted` | One Workflow schedules a large batch of Activities or Child Workflows in parallel, each taking the lock. | Keep concurrent operations at 500 or fewer per Execution. Process the batch in smaller groups (sliding-window or plain batching) instead of scheduling everything at once. |
| `QueryWorkflow` | Too many concurrent Queries against one Execution, or fallout from repeated Workflow Task retries. | Reduce concurrent Queries to that Execution. If it correlates with Workflow Task failures or timeouts, resolve those first. |

The per-execution ceilings referenced above are in the Cloud limits page: 10 in-flight Updates per Execution, and 2,000 incomplete Activities / Signals / Child Workflows / external-cancellation requests, with 500 or fewer recommended for optimal performance.

### Related signals

- **Schedule-to-start latency rising alongside it.** "High Workflow lock latency. If many updates are made to a single execution, this can cause Workflow lock latency, which in turn affects the Schedule-to-start latency. Reduce the rate of Signals." This is the same hot-execution pressure seen from the latency side; see [performance-bottlenecks.md](performance-bottlenecks.md).
- **Is the caller retrying without backoff?** Retries count against the budget. A raw gRPC client reimplementing retry must use exponential backoff.
- **Pending state on the Execution.** `pendingWorkflowTask` in `temporal workflow describe` output shows in-flight Workflow Task state for the Execution.

## Other frequently ambiguous errors

### `no pollers`

This phrase is a clue, not a diagnosis. Common shapes: no Worker reached the frontend for the queue+type within the last 5 minutes, Workers are polling a different queue or Namespace, or Workers connect but fail before the poll loop. Verify from `temporal task-queue describe`, not from cached metrics. Full protocol: [worker-health.md → What "no pollers" looks like](worker-health.md#what-no-pollers-looks-like).

### `INVALID_ARGUMENT`

`INVALID_ARGUMENT` is a catch-all. The suffix is the useful part:

- `namespace not found` — the namespace string does not exist in this account. Confirm via `tcld namespace list` (see [connectivity.md → Endpoint formats](connectivity.md#endpoint-formats) for the correct Namespace Endpoint form, which is a common source of this shape).
- Field-specific validation errors — fix the input; the suffix names the bad field.

### Unspecified `UNAVAILABLE`

`UNAVAILABLE` on its own does not pin a layer. Peel the wrapped cause: `tls:` / `x509:` / `remote error: tls:` → [certificates.md](certificates.md); `connection refused` / `no such host` / `i/o timeout` → [connectivity.md](connectivity.md). If the wrapped cause is absent, run the [diagnostic ladder](diagnostic-ladder.md) from layer 1.

## Triage protocol

For any ambiguous runtime error:

1. **Demand the exact text.** Copy-paste, not paraphrase. An `UNAVAILABLE` with `x509:` wrapped inside is a TLS problem, not a network one.
2. **Identify which operation produced it** — start / signal / update / query / poll / Nexus handler / internal. The operation narrows the candidate layers.
3. **Identify which environment produced it** — local dev, self-hosted, Cloud. Different error catalogs (e.g. Cloud's `resource_exhausted_cause` labels versus self-hosted `service_errors_resource_exhausted`).
4. **Walk the diagnostic ladder** up to the layer the evidence implicates. See [diagnostic-ladder.md](diagnostic-ladder.md).
5. **Attach confidence.** Below 6, the next action is a discriminating check (DNS lookup, `openssl s_client`, `temporal operator cluster health`), not a fix. Confidence framing is a skill-level triage norm, not a documented Temporal property — but it's how this skill avoids prescribing fixes on the strength of ambiguous evidence.
