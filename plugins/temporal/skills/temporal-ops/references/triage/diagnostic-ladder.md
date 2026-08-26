# Diagnostic Ladder

The bottom-up seven-layer model every other file in this skill hangs off. A failure at a lower layer breaks every layer above it, so a signature you think you recognize at layer 5 may really be layer 3 with a misleading wrapper.

This file is a table of contents, not a recipe book: each layer gives one check and one minimal healthy signal, then links to the sibling file that owns the failure diagnosis. If you want the full OpenSSL recipe, it's in [certificates.md](certificates.md); if you want the full worker-polling discrimination, it's in [worker-health.md](worker-health.md). Come here to choose *which* layer to investigate.

## Table of Contents

- [How to use the ladder](#how-to-use-the-ladder)
- [Layer 1: DNS / network path](#layer-1-dns--network-path)
- [Layer 2: TCP / port reachability](#layer-2-tcp--port-reachability)
- [Layer 3: TLS handshake](#layer-3-tls-handshake)
- [Layer 4: Authentication and authorization](#layer-4-authentication-and-authorization)
- [Layer 5: gRPC / Temporal frontend health](#layer-5-grpc--temporal-frontend-health)
- [Layer 6: Namespace, task queues, and workers](#layer-6-namespace-task-queues-and-workers)
- [Layer 7: Workflow code](#layer-7-workflow-code)
- [Quick per-layer commands](#quick-per-layer-commands)

## How to use the ladder

1. **Run diagnostics from the failing environment.** A pod in a production VPC and a laptop on a home network do not share DNS, egress paths, or CA bundles. Always reproduce from where the problem occurs. (Skill convention.)
2. **Start at the lowest layer that could plausibly be broken.** For a fresh cert-rotation incident, start at layer 3. For a "workflow stuck" report where the client still works, start at layer 6.
3. **Move up only after the current layer is proven healthy.** "Healthy" means the check in that layer returned the signal described — not that the command didn't crash.
4. **If a layer fails, layers above it are unknown.** An `UNAUTHENTICATED` reported by a client whose TLS handshake is actually failing will not be fixed by rotating API keys — see the wrapped-cause trap in [authentication.md → UNAUTHENTICATED vs PERMISSION_DENIED](authentication.md#unauthenticated-vs-permission_denied).
5. **Do not skip layers.** Skill convention, not a Temporal contract — but every bug-report-chased-at-the-wrong-layer in this skill's scope would have been caught by it.

## Layer 1: DNS / network path

**Question:** Can this host resolve the Temporal endpoint to an address it can route?

**Minimal check:**

```bash
nslookup <namespace>.<account>.tmprl.cloud
dig +short <namespace>.<account>.tmprl.cloud
```

**Healthy signal:** an A record (self-hosted) or a CNAME chain through `<region>.region.tmprl.cloud` ending in A records (Cloud). See [connectivity.md → DNS](connectivity.md#dns) for the exact shapes per namespace type.

**Failure signatures** (each routes to [connectivity.md](connectivity.md) for remediation):

- `no such host` wrapped in a gRPC `UNAVAILABLE` — resolver returned NXDOMAIN or the resolver is unreachable. See [connectivity.md → DNS](connectivity.md#dns).
- Namespace hostname format wrong (missing `.<account>` suffix, typo) — the endpoint table in [connectivity.md → Endpoint formats](connectivity.md#endpoint-formats) shows the valid patterns.
- Returns a private IP unexpectedly, or a public IP when PrivateLink is supposed to be in use — split-horizon / missing private hosted zone. See [connectivity.md → PrivateLink and PSC](connectivity.md#privatelink-and-psc).

**What failure here means above:** every higher layer fails. Do not attempt TLS or auth diagnosis until DNS works.

## Layer 2: TCP / port reachability

**Question:** Can this host open a TCP connection on the Temporal frontend port to the resolved IP?

**Minimal check:**

```bash
nc -zvw10 <host> 7233
```

The Cloud Namespace gRPC endpoint is on TCP/7233 (see [connectivity.md → Connection refused](connectivity.md#connection-refused), which cites the Namespace Endpoint port). On BSD `nc`, `-z` scans without sending data, `-v` is verbose, `-w` sets the idle timeout.

**Healthy signal:** `succeeded!` (or the BSD `nc` equivalent line). Anything beyond a successful connect is out of scope for layer 2.

**Failure signatures:**

- `Connection refused` — TCP reached the host but nothing is listening. See [connectivity.md → Connection refused](connectivity.md#connection-refused) for the top causes (dev server not running; wrong port — e.g. pointing at `saas-api.tmprl.cloud:7233` when that endpoint is port 443; self-hosted frontend not accepting connections).
- Hangs for the full `-w` timeout — firewall silently dropping packets. See [connectivity.md → Firewall and proxy](connectivity.md#firewall-and-proxy).
- TCP succeeds but no bytes returned at TLS time — often a TLS-inspecting middlebox. Same section: [connectivity.md → Firewall and proxy](connectivity.md#firewall-and-proxy).
- PrivateLink / PSC: DNS resolves to the private endpoint but port unreachable — VPC-endpoint security group not permitting TCP/7233. See [connectivity.md → PrivateLink and PSC](connectivity.md#privatelink-and-psc).

**What failure here means above:** TLS and everything above cannot complete.

## Layer 3: TLS handshake

**Question:** Does the TLS handshake complete and (for mTLS) does the server accept the client cert?

**Minimal check** (API-key or server TLS only):

```bash
openssl s_client -connect <host>:7233 -servername <host> </dev/null
```

For the mTLS variant with `-cert`/`-key`, see [certificates.md → OpenSSL recipes](certificates.md#openssl-recipes).

**Healthy signal:** `Verify return code: 0 (ok)` and the server certificate block shows the expected subject. See [certificates.md → Handshake failure](certificates.md#handshake-failure) for the full interpretation table.

**Failure signatures** (each routes to [certificates.md](certificates.md); the sibling file owns the Go/x509 and TLS alert strings):

- `Verify return code: 10 (certificate has expired)` or client-side `x509: certificate has expired or is not yet valid` — [certificates.md → Expired or not-yet-valid](certificates.md#expired-or-not-yet-valid).
- `Verify return code: 19/20/21` or client-side `x509: certificate signed by unknown authority` — [certificates.md → Unknown authority](certificates.md#unknown-authority).
- `tlsv1 alert unknown ca` / `remote error: tls: unknown certificate authority` — Cloud mTLS server rejected the client CA. [certificates.md → Accepted client CA set (mTLS Cloud)](certificates.md#accepted-client-ca-set-mtls-cloud).
- `x509: certificate is valid for <SAN list>, not <requested host>` — [certificates.md → Hostname mismatch](certificates.md#hostname-mismatch). Common on PrivateLink / Regional-Endpoint clients that didn't override SNI — fix per [certificates.md → Server name override](certificates.md#server-name-override).
- TCP opens, closes without a TLS alert — typically a middlebox. Back off to layer 2, [connectivity.md → Firewall and proxy](connectivity.md#firewall-and-proxy).

See also [certificates.md → TLS / cert error reference](certificates.md#tls--cert-error-reference) for the full error-string table.

**What failure here means above:** depending on the SDK / client, the gRPC client will surface this as `UNAVAILABLE` with a wrapped `tls:` / `x509:` cause, or — confusingly — as `UNAUTHENTICATED`. Do not debug layer 4 until TLS is clean. The wrapped-cause trap is documented in [authentication.md → UNAUTHENTICATED vs PERMISSION_DENIED](authentication.md#unauthenticated-vs-permission_denied).

## Layer 4: Authentication and authorization

**Question:** Does Temporal accept the presented credentials, and does the resulting identity permit this operation on this namespace?

**Minimal check** (API-key variant; mTLS variant is in the sibling):

```bash
temporal workflow list --limit 1 \
  --address <namespace>.<account>.tmprl.cloud:7233 \
  --namespace <namespace>.<account> \
  --api-key "$TEMPORAL_API_KEY"
# Command form: authentication.md → Discriminating with a CLI smoke test
# Use API Regional Endpoint when dual-auth / region pin requires it
```

The full form, including flag citations and the mTLS variant, is in [authentication.md → Discriminating with a CLI smoke test](authentication.md#discriminating-with-a-cli-smoke-test). API-key-only Namespaces default to the Namespace Endpoint; API Regional is for pin / dual-auth / some private-connectivity cases — see [authentication.md → Address form for API-key connections](authentication.md#address-form-for-api-key-connections).

**Healthy signal:** the command returns a list (possibly empty) without error.

**Failure signatures:**

- `UNAUTHENTICATED` — credentials rejected (missing, typo, disabled, deleted, expired key; untrusted mTLS cert; wrong endpoint family). [authentication.md → API-key authentication](authentication.md#api-key-authentication) and [authentication.md → mTLS authentication after TLS completes](authentication.md#mtls-authentication-after-tls-completes).
- `PERMISSION_DENIED` — credentials valid but the identity lacks account-role / namespace-permission / cert-filter-derived identity for the action. [authentication.md → Cloud role and permission model](authentication.md#cloud-role-and-permission-model).
- `INVALID_ARGUMENT` with a "namespace not found" suffix — namespace string does not exist in this account, or the Namespace Endpoint form is wrong. See [runtime-errors.md → `INVALID_ARGUMENT`](runtime-errors.md#invalid_argument) and verify against the endpoint table in [connectivity.md → Endpoint formats](connectivity.md#endpoint-formats).

**What failure here means above:** every gRPC call from this principal fails the same way. No point inspecting task queues or workflows.

## Layer 5: gRPC / Temporal frontend health

**Question:** Is the Temporal frontend reachable and reporting itself healthy over gRPC?

**Minimal check:**

```bash
temporal operator cluster health
```

Supply whatever `--address`, `--namespace`, and auth flags you established at layer 4. The command calls `grpc.health.v1.Health/Check`.

**Self-hosted:** use `temporal operator cluster health` directly. **Cloud:** use `temporal workflow list --limit 1` as the frontend-reachability smoke test instead — `cluster health` is scoped to self-hosted in the docs.

**Healthy signal:** `SERVING` (self-hosted) or a successful list response (Cloud). The Temporal troubleshooting guide uses `cluster health` as the first "is the frontend up?" probe on self-hosted.

**Failure signatures:**

- `NOT_SERVING` or an unhealthy status — the frontend is up but reports itself unhealthy. On self-hosted, the troubleshooting guide points at `grpc-health-probe` to test Frontend, Matching, and History individually; on Cloud, open a ticket. See [runtime-errors.md → Deadline exceeded](runtime-errors.md#deadline-exceeded) for the self-hosted vs. Cloud routing.
- Long timeouts or `DEADLINE_EXCEEDED` with no specific cause — overload or upstream saturation. A `resource_exhausted` condition can surface as a deadline — see [runtime-errors.md → Deadline exceeded](runtime-errors.md#deadline-exceeded) and [rate-limits.md → Identifying which limit was hit](rate-limits.md#identifying-which-limit-was-hit).
- `RESOURCE_EXHAUSTED` at the frontend — rate limit or capacity. [rate-limits.md → What RESOURCE_EXHAUSTED means and what it does not](rate-limits.md#what-resource_exhausted-means-and-what-it-does-not).

**What failure here means above:** task-queue and workflow operations will succeed intermittently or not at all. Check this layer before blaming workers or workflow code.

## Layer 6: Namespace, task queues, and workers

**Question:** Are workers polling the expected task queue in the expected namespace on a recent timescale?

**Minimal check:**

```bash
temporal task-queue describe --task-queue <queue>
# Command form and statistics: worker-health.md → Inspecting a Task Queue
```

The full invocation, including `--task-queue-type` filtering and the statistics the call returns, is in [worker-health.md → Inspecting a Task Queue with `temporal task-queue describe`](worker-health.md#inspecting-a-task-queue-with-temporal-task-queue-describe).

**Healthy signal:** a non-empty pollers list whose `LastAccessTime` values are recent. Per the CLI docs, "A `LastAccessTime` over one minute may indicate the Worker is at capacity or has shut down. Temporal Workers are removed if 5 minutes have passed since the last poll request" (quoted and cited in [worker-health.md → Reading the pollers field](worker-health.md#reading-the-pollers-field)).

**Failure signatures:**

- Empty poller list — no worker reached the frontend for this queue+type within the 5-minute window. [worker-health.md → What "no pollers" looks like](worker-health.md#what-no-pollers-looks-like).
- Pollers present but stale `LastAccessTime` (> ~1 min, no tasks moving) — worker at capacity or shut down. [worker-health.md → Reading the pollers field](worker-health.md#reading-the-pollers-field).
- Pollers present but the Build IDs / versions don't match the worker fleet you expect — versioning routing issue. [worker-health.md → Reachability and versioning](worker-health.md#reachability-and-versioning).
- Backlog growing despite fresh pollers — slot exhaustion or schedule-to-start saturation. [worker-health.md → Schedule-to-start latency](worker-health.md#schedule-to-start-latency) and [worker-health.md → Worker task slots](worker-health.md#worker-task-slots).

**What failure here means above:** workflows enqueue tasks that never get picked up, so a workflow will appear stuck at the first `ActivityTaskScheduled` or `WorkflowTaskScheduled` event. Do not start diagnosing layer 7 until pollers are healthy.

## Layer 7: Workflow code

**Question:** When a worker picks up a Workflow Task, does the workflow code execute successfully against the recorded Event History?

**Minimal check:**

```bash
temporal workflow describe --workflow-id <id>
# Command form and output schema: workflow-stuck.md → The primary inspection command
```

For the full inspection flow — describe output shape, status interpretation, pending-sections routing, and the companion `temporal workflow show` for Event History — see [workflow-stuck.md → The primary inspection command: `temporal workflow describe`](workflow-stuck.md#the-primary-inspection-command-temporal-workflow-describe) and [workflow-stuck.md → Inspecting the Event History: `temporal workflow show`](workflow-stuck.md#inspecting-the-event-history-temporal-workflow-show).

**Healthy signal:** `workflowExecutionInfo.status` is `Running` and the last meaningful event is one that legitimately blocks progress (an intentional `TimerStarted`, an awaited signal, an in-flight activity with a running retry state), or the workflow has progressed since the previous check. The full status table (Running / Completed / Failed / Canceled / Terminated / ContinuedAsNew / TimedOut) is in [workflow-stuck.md → Workflow Execution Status values](workflow-stuck.md#workflow-execution-status-values).

**Failure signatures:**

- `WorkflowTaskFailed` events recurring with `cause` = Nondeterminism — [non-determinism.md → The WFT-failure signature of non-determinism](non-determinism.md#the-wft-failure-signature-of-non-determinism). Reproduce locally via [replay.md](replay.md).
- `WorkflowTaskFailed` loops with a non-Nondeterminism cause (e.g. Workflow Worker Unhandled Failure) — [workflow-stuck.md → Pending Workflow Task and WorkflowTaskFailed loops](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops).
- `ActivityTaskScheduled` with no matching retry / terminal event after describe — loop back to layer 6; the task was never picked up. [workflow-stuck.md → Pending activities](workflow-stuck.md#pending-activities).
- Pending Activity with climbing attempts and `last_failure` populated — the Activity is running and failing; fix the Activity or its retry policy. Same section.
- Workflow `Running` with `historyLength` flat and no pending sections — a timer-based wait, covered in [workflow-stuck.md → Timer-based waits](workflow-stuck.md#timer-based-waits).
- Ambiguous `DEADLINE_EXCEEDED` or `Workflow is busy` lock contention on signals/updates/queries — [runtime-errors.md → Deadline exceeded](runtime-errors.md#deadline-exceeded) and [runtime-errors.md → Workflow lock contention (BusyWorkflow)](runtime-errors.md#workflow-lock-contention-busyworkflow).

## Quick per-layer commands

Each command below is the minimal check for its layer. Full invocations with all flags and citations live in the sibling file linked on the right.

| Layer | Command | Healthy signal | Owner |
|---|---|---|---|
| 1. DNS | `nslookup <host>` | A record or CNAME chain returned | [connectivity.md → DNS](connectivity.md#dns) |
| 2. TCP | `nc -zvw10 <host> 7233` | `succeeded!` | [connectivity.md → Connection refused](connectivity.md#connection-refused) |
| 3. TLS | `openssl s_client -connect <host>:7233 -servername <host>` | `Verify return code: 0 (ok)` | [certificates.md → Handshake failure](certificates.md#handshake-failure) |
| 4. Auth | `temporal workflow list --limit 1 …` | list returns (possibly empty) | [authentication.md → Discriminating with a CLI smoke test](authentication.md#discriminating-with-a-cli-smoke-test) |
| 5. Frontend | Self-hosted: `temporal operator cluster health`; Cloud: `temporal workflow list --limit 1` | `SERVING` (self-hosted) or successful response (Cloud) | [runtime-errors.md → Deadline exceeded](runtime-errors.md#deadline-exceeded) |
| 6. Workers | `temporal task-queue describe --task-queue <q>` | pollers listed with recent `LastAccessTime` | [worker-health.md → Inspecting a Task Queue with `temporal task-queue describe`](worker-health.md#inspecting-a-task-queue-with-temporal-task-queue-describe) |
| 7. Workflow | `temporal workflow describe --workflow-id <id>` | status `Running` with a legitimate pending reason | [workflow-stuck.md → The primary inspection command: `temporal workflow describe`](workflow-stuck.md#the-primary-inspection-command-temporal-workflow-describe) |

If every layer is healthy and the user still reports a problem, the diagnosis narrows to workflow code, SDK configuration, or workload pressure — handed off to [workflow-stuck.md](workflow-stuck.md), [non-determinism.md](non-determinism.md), [runtime-errors.md](runtime-errors.md), or [rate-limits.md](rate-limits.md) depending on the shape of the symptom. HA-failover-specific symptoms (CNAME didn't update, PrivateLink breaks after failover) are in [ha-failover.md](ha-failover.md); the worker-placement triage pointer is at [ha-failover.md → Worker placement — triage-layer pointer](ha-failover.md#worker-placement--triage-layer-pointer).
