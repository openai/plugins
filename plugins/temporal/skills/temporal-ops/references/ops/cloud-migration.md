# Cloud Migration

Three migration paths exist for Temporal workflows:

| Path | From | To | Downtime |
|---|---|---|---|
| Automated | Self-hosted | Temporal Cloud | Zero |
| Manual | Self-hosted | Temporal Cloud | Varies |
| Within Cloud | Cloud region A | Cloud region B | Zero |

---

## Automated Migration (Self-Hosted to Cloud)

Pre-release feature. Contact your Temporal account executive before planning.

Migrate in order of least-critical to most-critical namespace. Start with testing namespaces where downtime is acceptable.

### Limitations

- Self-hosted server version 1.22+ required
- History shard counts must be a power of two (e.g. 512, 1024)
- Multiple self-hosted servers with the same cluster name (default `active`) cannot connect to one migration server simultaneously; either migrate one at a time or use separate migration servers
- Cross-namespace commands (`system.enableCrossNamespaceCommands`) must be disabled and related code removed before migration
- Target cloud namespace must be empty (no workflows); cannot combine manual and auto migration
- If Global Namespace was previously enabled: Initial Failover Version must be <= 1,000,000 and Failover Version Increment must be a divisor of 1,000,000

### Phase 1: Prepare

Collect data and submit to Temporal via support ticket:

**Cluster configuration** (run per cluster):
```
temporal operator cluster describe --address <frontend:7233> --output json   # server > 1.28.1
tctl --address <frontend:7233> admin cluster describe                        # server <= 1.28.1
```

**Custom search attributes** (must be Cloud-compatible):
```
temporal operator search-attribute list                          # Elasticsearch/OpenSearch
temporal operator search-attribute list --namespace="your_ns"    # SQL
```

**Namespace metrics**: total open/closed workflows, total storage, current retention policy, peak APS

**mTLS certificates** for S2S Proxy: `openssl verify -CAfile ca.pem client-cert.pem`

**Cloud namespaces**: create empty target namespaces, apply custom search attributes, adjust rate limits

**Submit CSV mapping** to Temporal:
```
cluster_name, cloud_region, source_namespace, cloud_namespace
cluster1,     us-east-1,    default,          use1.nnnnn
```

### Phase 2: Setup

Proceed only after Temporal approves the migration request.

**S2S Proxy deployment**:
1. Pull latest image from `temporalio/s2s-proxy` Docker Hub
2. Deploy 3 replicas (min 4 CPU, 512 MB memory per replica). Replica count must match cloud side.
3. Proxy initiates outbound TCP 8233 to cloud-side proxy. Ensure firewalls permit this.
4. Verify connectivity:
```
temporal operator cluster describe --address {proxy-external-address}
```

Monitor proxy health via Prometheus endpoint (`proxy-pod-ip:9090/metrics`), in particular `temporal_s2s_proxy_mux_connection_active`.

**Dynamic configuration changes**:

```yaml
frontend.keepAliveMaxConnectionAge:
  - value: '2h'
```

If Global Namespace was never enabled, enable it: set `clusterMetadata.enableGlobalNamespace: true`, `failoverVersionIncrement: 1000000` (coordinate with Temporal), `initialFailoverVersion: <2-99>` (unique per cluster), and `dcRedirectionPolicy.policy: 'all-apis-forwarding'`.

Restart all services (frontend first, then history, matching, worker) and verify with `temporal operator cluster describe`.

For server versions 1.22.x-1.23.x, also enable stream-based replication:
```yaml
history.enableReplicationStream:
  - value: true
```

Verify your persistence/database layer has sufficient CPU and I/O capacity.

### Phase 3: Test

Use a non-production namespace that can tolerate data loss. Run a mix of completed, active, and new workflows. Perform a full end-to-end migration. Testing succeeds if all data migrates to Cloud.

### Phase 4: Initiate

**Start migration** (Temporal generates the endpoint-id):
```
tcld migration start --endpoint-id <endpoint-id> --source-namespace <source-namespace> --target-namespace <target-namespace>
```

Self-hosted namespace is active, cloud namespace is passive. Workflows replicate self-hosted to cloud.

Billing for the cloud namespace does not begin until migration is confirmed.

**Monitor progress**:
```
tcld migration get --id <migration-id>
```
Also monitor `replication_stream_stuck` metric from self-hosted side.

**Handover to Cloud**:
```
tcld migration handover --id <migration-id> --to-replica-id cloud
```
Cloud becomes active, self-hosted becomes passive. To hand back to self-hosted:
```
tcld migration handover --id <migration-id> --to-replica-id on-prem
```

### Phase 5: Finalize

Complete client transfer, then validate: confirm worker access to cloud namespaces, verify metrics access, monitor schedule-to-start latency / start vs. completion rate / sync match rate, and plan a worker tuning session (performance may differ).

**Confirm migration** (final, cannot be undone; halts replication):
```
tcld migration confirm --id <migration-id>
```

**Abort migration** (rolls back without impacting workflows):
```
tcld migration abort --id <migration-id>
```

### Transfer Clients to Cloud

**Option 1 (recommended)**: Deploy two sets of clients, one pointing to self-hosted and one to Cloud.
1. Cloud clients connect and poll but receive no tasks initially
2. Start migration: self-hosted active, cloud passive. Cloud client requests forward to self-hosted automatically
3. Handover: cloud active, self-hosted passive. Self-hosted client requests forward to cloud automatically
4. Confirm migration: self-hosted clients stop receiving tasks; shut them down

**Option 2**: Single set of clients, switch endpoint during migration. Risk: if workers are misconfigured during switch, workflows stop making progress.

### Key Facts

All workflows migrate by default; for closed workflows you may specify a date range (top speed optimization). Schedules are supported. Cannot split one source namespace into multiple cloud namespaces. Encrypted payloads remain encrypted through migration.

---

## Manual Migration (Self-Hosted to Cloud)

Use when automated migration requirements are not met or when migration scope is smaller.

### Client Code Changes

Update Worker and Starter connection code:
- Add SSL certificate and private key associated with the namespace
- Set gRPC endpoint to `<namespace_id>.<account_id>.tmprl.cloud:port`
- Configure `tcld` with the same address, namespace, and certificate

### Workflow Execution Strategies

**New workflows**: Once updated client code is deployed, new executions automatically go to Cloud. Maintain the self-hosted client as long as you need to send Signals or Queries to old executions.

**Running workflows**:
- Short-running: drain (let them complete), then restart on Cloud
- Long-running / continuous: cancel and pass current state to a new workflow on Cloud. Example implementation: `github.com/temporalio/temporal-migration` (Java)

During live migration, a Signal and Query execute per workflow. The Query API loads the full history into Workers. Ensure self-hosted Worker capacity supports this memory load.

**Completed workflows**: Execution history cannot be automatically migrated to Cloud via manual migration. Maintain self-hosted access or export JSON for analytics.

### Considerations When Resuming Workflows

- **Idempotency**: Determine whether to skip non-idempotent steps when resuming
- **Elapsed time**: Calculate sleep deltas for resumed executions
- **Child workflows**: Pass child state into parent to resume children correctly; parent/child relationship does not carry over
- **Heartbeat state**: Long-running activities relying on heartbeat details will not receive latest details in target namespace
- **Signal handling**: Handle `NotFound` when signaling between workflows; they may resume out of order
- **Duration between awaitables**: Factor elapsed time accuracy for sleeps between awaitables

### Other Considerations

- Add mTLS certificate to Cloud namespace
- Metrics differ between self-hosted and Cloud; review Cloud metrics documentation
- Review security and access implications
- Review current APS load with your AE/SA to set appropriate namespace limits

---

## Migrate Within Cloud (Region to Region)

Uses Temporal Cloud High Availability features. Zero downtime.

HA features affect pricing.

### Prerequisites

- Namespaces using Export must stop Export and reconfigure for the new region before migration
- If workers use API key authentication, update all client code to use the regional endpoint of the new replica

### Migration Steps

1. **Add replica** in target region (see available regions and supported multi-region/multi-cloud configurations)
2. **Wait** for the replica to become active. Cloud UI shows a time estimate; namespace admins receive an email on completion.
3. **Update workers** (API key auth only) to use the new region's regional endpoint
4. **Failover** to the new region via Cloud UI
5. **Remove** the original region's replica

If using API keys for worker authentication, removing the replica requires a support ticket.

All replica changes are subject to a cooldown period before further changes can be made.

---

## tcld Migration Command Reference

| Command | Purpose |
|---|---|
| `tcld migration start --endpoint-id <id> --source-namespace <ns> --target-namespace <ns>` | Begin migration |
| `tcld migration get --id <migration-id>` | Check migration status |
| `tcld migration list` (alias `l`) | List all migrations (no flags) |
| `tcld migration handover --id <migration-id> --to-replica-id cloud` | Hand over to Cloud |
| `tcld migration handover --id <migration-id> --to-replica-id on-prem` | Hand back to self-hosted |
| `tcld migration confirm --id <migration-id>` | Finalize (irreversible) |
| `tcld migration abort --id <migration-id>` | Abort and roll back |

`start`, `handover`, `confirm`, and `abort` accept an optional `--request-id`/`-r`; the server assigns one if unset.

---

## Troubleshooting

**S2S Proxy not connecting**
- Verify outbound TCP 8233 is open through firewalls
- Check `temporal_s2s_proxy_mux_connection_active` metric on `proxy-pod-ip:9090/metrics`
- Confirm replica count matches between self-hosted and cloud-side proxy

**Replication appears stuck**
- Monitor `replication_stream_stuck` metric from self-hosted side
- For server 1.22.x-1.23.x, ensure `history.enableReplicationStream` is set to `true` and history pods are restarted

**Cluster name collision**
- Multiple self-hosted servers with the same cluster name (default `active`) cannot use the same migration server. Migrate one at a time or use separate migration servers.

**Workflows not progressing after handover**
- Option 2 (single client set) risk: if workers are misconfigured during endpoint switch, workflows stop. Verify all workers connect to Cloud before handover.
- Option 1 (dual client set) is recommended to avoid this scenario

**Manual migration: Query overloading Workers**
- Query API loads full workflow history into Worker memory. Ensure capacity before migrating large numbers of workflows via `ListFilter`.

**Within-Cloud: Cannot remove replica**
- If using API keys for worker auth, a support ticket is required to remove the replica
- Replica changes are subject to a cooldown period
