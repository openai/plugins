# Temporal Cloud Capacity Modes

Quick-reference for Temporal Cloud capacity configuration: On-Demand vs Provisioned modes, APS/RPS/OPS definitions, TRUs, CLI commands, default limits, throttling, and APS management best practices.

---

## APS, RPS, and OPS

These three measures apply at different layers. Do not conflate them.

| Measure | Full Name | Scope | What It Measures |
|---------|-----------|-------|------------------|
| **APS** | Actions Per Second | Temporal Cloud Namespace | Rate of billable Actions (starting/signaling Workflows, scheduling Activities, etc.) |
| **RPS** | Requests Per Second | Temporal Service (Cloud and self-hosted) | Rate of gRPC requests to the Temporal Service |
| **OPS** | Operations Per Second | Temporal Cloud | Anything a user does directly, or Temporal does on behalf of the user, that produces load on Temporal Server |

APS is the higher-level, primary limit for Namespaces. RPS and OPS are lower-level measures to control and balance request rates at the service level.

---

## What Counts as an Action?

An Action is any billable operation within Temporal Cloud. Key categories:

- **Workflow**: Starting, resetting, Continue-As-New, Child Workflow start, Search Attribute upsert
- **Activity**: Starting, retrying, Heartbeating (only if the heartbeat reaches the Server)
- **Timer**: Timer started (including implicit SDK timers from timeouts)
- **Signal**: Every Signal sent (from Client or Workflow); one Action for Signal-With-Start regardless of whether the Workflow starts
- **Query**: Every Query received by a Worker (`__temporal_workflow_metadata` excluded)
- **Update**: Every accepted or rejected Update
- **Schedule**: Each Schedule execution accrues 3 Actions (2 for Schedule start + 1 for the target Workflow start)
- **Nexus**: Scheduling or canceling a Nexus Operation each counts as 1 Action on the caller Namespace

Actions during Workflow Replay do **not** count.

Actions excluded from APS calculations: Export, Capacity-related Actions.

---

## On-Demand Capacity

Default mode. Namespace capacity scales automatically based on trailing usage.

### Default limits

| Measure | Default Limit |
|---------|---------------|
| APS     | 500           |
| RPS     | 2,000         |
| OPS     | 4,000         |

The limit never falls below the default value.

### Auto-scaling formula

Limit = the **greater** of:

1. Default limit (500 APS)
2. The **lesser** of:
   - 4 x APS Mean (over the past 7 days)
   - 2 x APS P90 (over the past 7 days)

**Example**: If your average APS over 7 days is 200 and your P90 is 500:

- 4 x 200 = 800
- 2 x 500 = 1,000
- Lesser of those = 800
- Greater of 800 vs default 500 = **800 APS limit**

Under On-Demand you are only charged for the Actions you use.

---

## Provisioned Capacity

Lets you manually control Namespace limits by requesting Temporal Resource Units (TRUs).

### Per-TRU rates

| Measure | Per TRU |
|---------|---------|
| APS     | 500     |
| RPS     | 1,500   |
| OPS     | 4,000   |

### Valid TRU counts

**2, 3, 4, 6, 8, 10, 12** -- subject to regional availability.

TRUs can be adjusted hourly.

When TRUs are requested, Temporal aims to provision the additional capacity within two minutes.

For requests in excess of 4 TRUs in regions outside of the US, submit a support ticket to ensure capacity availability.

### When to use Provisioned Capacity

- Planned events (promotions, load testing, migrations)
- Unplanned events / usage spikes
- Known but sudden system spikes
- Load testing
- Migrating workloads

When switching back to On-Demand mode, your APS limit resets to the running average from the last 7 days. If Temporal Support has set a custom limit for your namespace, this limit is persisted across capacity mode changes.

---

## Setting Capacity Modes

Capacity modes can be set and adjusted by **Global Admin** and **Namespace Admin**.

### CLI

Update capacity:

```
tcld namespace capacity update \
  --namespace <namespace_name> \
  --capacity-mode <on_demand|provisioned> \
  [--capacity-value <tru value>] \
  [--request-id <request_id>] \
  [--resource-version <resource-version>]
```

- `--capacity-mode` (`--cm`): `on_demand` for automatic scaling, `provisioned` for fixed allocation.
- `--capacity-value` (`--cv`): throughput value in TRUs. Required and must be greater than 0 when `--capacity-mode` is `provisioned`; ignored for `on_demand`.
- `--request-id`: optional; server assigns one if not specified.
- `--resource-version`: optional; CLI uses the latest version if not set.

Get current capacity (alias `g`):

```
tcld namespace capacity get \
  --namespace <namespace_name>
```

- `--namespace` (`-n`): required.

If using API key authentication with `--api-key`, add it directly after `tcld` and before `capacity update`.

`capacity update` changes both the bill and the throughput ceiling, so propose it
rather than running it: read the current setting with `capacity get` first, and put
the before-and-after mode and TRU count in front of the user. The direction that
causes an incident is downward — lowering TRUs, or switching `provisioned` →
`on_demand` on a Namespace that was provisioned precisely because auto-scaling
could not keep up, throttles production traffic with `RESOURCE_EXHAUSTED` rather
than failing the command. See [Throttling Behavior](#throttling-behavior) and
[../triage/rate-limits.md](../triage/rate-limits.md).

### UI

Navigate to the Namespace page in Temporal Cloud UI (`https://cloud.temporal.io/namespaces/<Namespace ID>`), click **Manage Capacity**, then select On-Demand or Provisioned and configure TRUs via the slider.

### API

Call the `UpdateNamespace` API after Namespace creation and define the desired capacity state as part of the capacity spec.

---

## Throttling Behavior

When your Action rate exceeds your APS (or RPS/OPS) limit, Temporal Cloud throttles requests.

1. **Priority-based**: Low-priority operations throttled first; higher-priority operations (`StartWorkflowExecution`, `SignalWorkflowExecution`, `UpdateWorkflowExecution`) continue when possible.
2. **Not instantaneous**: Usage may briefly exceed your limit before throttling takes effect.
3. **`ResourceExhausted` errors**: Server returns a `ResourceExhausted` gRPC error; SDK clients automatically retry based on the default gRPC retry policy.
4. **Potential failure**: If throttling persists beyond the SDK's retry limit, client calls fail -- work **can** be lost if you do not handle these failures.

> For diagnosis of `RESOURCE_EXHAUSTED` errors in triage context, see `../triage/rate-limits.md`.

**Best practices for handling throttling**:

- Log any failed `StartWorkflowExecution`, `SignalWorkflowExecution`, or `UpdateWorkflowExecution` calls (including payloads) so you can retry or backfill later.
- Set up Cloud metrics (`temporal_cloud_v0_resource_exhausted_errors`) to alert when throttling occurs.
- Alert at 70-80% utilization to give time to react.

---

## Other Namespace-Level Limits

| Limit | Default | Notes |
|-------|---------|-------|
| Namespaces per account | 10 (auto-increases) | |
| Schedules RPS | 10 per second | Use jitter to avoid thundering herd |
| Visibility API | 30 calls per second | Not configurable |
| Certificates | 32 KB or 16 certificates (whichever first) | |
| Concurrent Task pollers | 20,000 Activity + 20,000 Workflow Task | Per Namespace |
| Retention period | 30 days default, configurable 1-90 days | |
| Batch jobs | 1 concurrent per Namespace, max 50 Executions/sec | |

---

## APS Management Best Practices

### Common reasons for hitting APS limits

1. **Bursty traffic**: Calendar-driven spikes, event-driven surges, recovery thundering herds, timer storms, retry storms.
2. **Cascading Workflows and fan-out**: Parent Workflows spawning many Child Workflows; each child's full action lifecycle counts against the Namespace APS.
3. **Human-in-the-loop at scale**: Long-running Workflows with frequent Queries from UIs for state polling.
4. **Many small Activities**: 1,000 single-record Activities vs 10 batched Activities -- each Activity adds Action overhead.
5. **Multiple use cases in one Namespace**: APS limit is per Namespace, so multiple workloads compound.

### Mitigation strategies

- **Stagger and jitter**: Use Schedule jitter and Start Delay to smooth batch starts.
- **Batch Activities**: Combine multiple external calls in a single Activity; process data in chunks.
- **Reduce fan-out depth**: Evaluate whether Child Workflows are necessary; limit fan-out size; flatten deeply nested hierarchies.
- **Push state, don't poll**: Avoid polling patterns where UIs constantly Query Workflow state; push state changes to a database that UIs read.
- **Use longer monitoring intervals**: Check SLAs every 30 minutes instead of every 1 minute; consolidate Timers.
- **Separate Namespaces per use case**: Plan for one set of Namespaces (per environment) per use case.
- **Provision TRUs for known spikes**: Pre-provision before planned events, deprovision after.

### Automation for TRU scaling

- Use the Cloud Ops API, Terraform Provider, or `tcld` CLI to programmatically scale capacity.
- Set utilization thresholds (e.g., scale up at 70-80% of limit).
- Schedule capacity changes with Temporal Schedules or Workflows.
- React to upstream leading indicators (queue depth, campaign start) to trigger capacity changes proactively.

### Monitoring

- Track `temporal_cloud_v0_resource_exhausted_errors` to detect throttling events.
- Alert at 70-80% utilization.
- Analyze historical patterns to decide between reactive TRU provisioning and proactive automation.
- For Provisioned Namespaces, on-demand envelope metrics show what limits would be under On-Demand mode.

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Default APS (On-Demand) | 500 |
| Default RPS (On-Demand) | 2,000 |
| Default OPS (On-Demand) | 4,000 |
| APS per TRU | 500 |
| RPS per TRU | 1,500 |
| OPS per TRU | 4,000 |
| Valid TRU counts | 2, 3, 4, 6, 8, 10, 12 |
| TRU provisioning time | Within 2 minutes |
| On-Demand scaling window | Past 7 days |
| On-Demand formula | lesser of 4 x APS Mean or 2 x APS P90 |
| Who can change capacity | Global Admin, Namespace Admin |
| CLI commands | `tcld namespace capacity get`, `tcld namespace capacity update` |
| Throttling error | `ResourceExhausted` gRPC error |
