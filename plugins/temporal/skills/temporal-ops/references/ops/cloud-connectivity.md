# Cloud Connectivity

Quick-reference for private connectivity (AWS PrivateLink / GCP PSC) and Connectivity Rules in Temporal Cloud.

Citations use stable doc anchors (slug + heading), e.g. `/cloud/connectivity#connectivity-rules` — public URL fragments, not line numbers.

---

## Private Connectivity

Temporal Cloud supports private connectivity via **AWS PrivateLink** or **GCP Private Service Connect (PSC)** in addition to public internet endpoints.

Namespace access is always authenticated via API keys or mTLS regardless of connectivity method.

### Three-step setup process

1. **Set up the private connection** from your VPC to the region where the Namespace is located.
2. **Update private DNS and/or client configuration** to use the private connection. Activating private connectivity does not change Namespace or Regional Endpoints automatically — clients keep resolving public addresses until you do this.
3. **Create a Connectivity Rule** (required for GCP PSC, optional for AWS PrivateLink) and attach it to the target Namespace(s).

### AWS PrivateLink key facts

- The PrivateLink endpoint **must be in the same region** as the Namespace (or, for HA, the same region as one of the replicas). Cross-region endpoints are not supported.
- PrivateLink endpoint services are **regional** -- individual Namespaces do not use separate services.
- Security group must accept **TCP ingress on port 7233**.
- The VPC endpoint can take up to 10 minutes to reach `Available`; configure private DNS or direct VPCE targeting only after that.
- **Direct VPCE targeting** (without per-Namespace DNS): point clients at the VPC Endpoint DNS name and set `ServerName` / SNI override to the Namespace Endpoint. Works with HA too — each Worker targets its own region's VPC Endpoint (different VPCE address per region), while `ServerName` stays the Namespace Endpoint. It does not follow the CNAME, so Temporal Cloud's cross-region forwarding is what keeps passive-region Workers productive and preserves the path across a failover.

### GCP Private Service Connect key facts

- PSC endpoint must be in the **same region** as the Namespace (or, for HA, the same region as one of the replicas).
- PSC endpoint stays in **`Pending`** until a matching Connectivity Rule is created -- the Connectivity Rule is the approval step (no separate producer-side approval).
- Automatic Failover via Temporal Cloud DNS is **not currently supported** with GCP PSC; manual worker updates are required on failover.

### Client configuration without private DNS

If you cannot set up private DNS, update two settings in your Temporal clients:

1. Set endpoint server address to the PrivateLink DNS name or PSC IP address, port `7233`.
2. Set the TLS server name override (depends on auth method):

| Auth method | TLS server name |
|---|---|
| mTLS (single-region) | Namespace Endpoint, e.g. `my-namespace.my-account.tmprl.cloud` |
| API key (single-region) | Regional API endpoint, e.g. `us-east-1.aws.api.temporal.io` (or `us-central1.gcp.api.temporal.io`) |
| Multi-region (mTLS or API key) | Active region endpoint, e.g. `aws-us-east-1.region.tmprl.cloud` |

Using the wrong TLS server name with API-key auth over PrivateLink/PSC fails the handshake with `connection reset by peer` even though `nc` shows the port open.

### Control plane connectivity

- The control plane (`saas-api.tmprl.cloud`) is accessible via public internet and optionally via AWS PrivateLink. Private connectivity does **not** block public internet access — the control plane is always reachable publicly.
- Control plane PrivateLink is in `us-west-2`, service name `com.amazonaws.vpce.us-west-2.vpce-svc-0c57a5930b6f6be0e`. The endpoint ships its own private DNS name, so clients can use it without configuring private DNS (enable the VPC's `Enable DNS hostnames` and `Enable DNS support`).
- Hostnames by surface: `saas-api.tmprl.cloud` for Terraform / `tcld` / Cloud Ops API; `web.onboarding.tmprl.cloud` and `web.saas-api.tmprl.cloud` for the Web UI.
- The PrivateLink service is exposed only in `us-west-2`; reach it from another region via a `us-west-2` VPC Endpoint plus VPC Peering.

---

## Connectivity Rules

Connectivity Rules restrict the network paths that can reach a Namespace. They are enforced by Temporal Cloud and do not create or modify the underlying network connection.

### Default behavior

A Namespace with **zero** Connectivity Rules is reachable over the public internet and any private connections already configured to the region.

When one or more rules are attached, Temporal Cloud **immediately blocks** any traffic that does not match a rule.

The Web UI is **not** subject to connectivity rule enforcement — it stays reachable over the public internet even on a private-only Namespace.

### When you need a Connectivity Rule

| Provider | Required? | Why |
|---|---|---|
| AWS PrivateLink | Optional -- add only to enforce private-only access | PrivateLink becomes usable when VPC endpoint is `Available` without any rule |
| GCP PSC | **Required** | PSC endpoint stays `Pending` until a matching rule is created |

### Rule parameters

**Public rule**: Only **one public rule per account**.

**AWS PrivateLink private rule** requires:
- `--connection-id`: VPC endpoint identifier (`vpce-...` value), not the endpoint service or DNS name.
- `--region`: Region prefixed with `aws-` (e.g. `aws-us-east-1`). Must match Namespace region.

**GCP PSC private rule** requires:
- `--connection-id`: PSC connection identifier (numeric string, e.g. `1234567890123456789`).
- `--region`: Region prefixed with `gcp-` (e.g. `gcp-us-east1`). Must match Namespace region.
- `--gcp-project-id`: GCP project where the PSC connection was created.

> **Connectivity Rules cannot be updated in place.** To change a rule, delete it, create a new one with the desired parameters, and re-attach it to every Namespace that used it. Creating a second public rule alongside an existing one returns an error.

### Permissions and limits

- Only **Account Admins and Account Owners** can create/manage connectivity rules (visible to Account Developers and above).
- Default: 5 private rules per Namespace, 50 private rules per account. Contact support to raise limits.

### tcld connectivity-rule commands

Alias: `cr`.

Create a private rule (AWS):

```bash
tcld connectivity-rule create --connectivity-type private --connection-id "vpce-00939a7ed9EXAMPLE" --region "aws-us-east-1"
```

Create a private rule (GCP):

```bash
tcld connectivity-rule create --connectivity-type private --connection-id "1234567890" --region "gcp-us-central1" --gcp-project-id "my-project-123"
```

Create a public rule (once per account):

```bash
tcld connectivity-rule create --connectivity-type public
```

Other subcommands:

| Subcommand | Purpose |
|---|---|
| `tcld connectivity-rule get --connectivity-rule-id <id>` | Get a rule |
| `tcld connectivity-rule delete --connectivity-rule-id <id>` | Delete a rule |
| `tcld connectivity-rule list` | List all rules (optionally filter by `--namespace`) |

`--connectivity-type` values: `private`, `public`.

### Attaching rules to a Namespace

> ⚠️ **Attaching a rule is destructive to existing access.** Once any Connectivity Rule is set, the Namespace is reachable **only** via the connections named in its rules. Removing a rule that workers are using interrupts their traffic. To migrate without lockout: attach a public rule alongside the private rules, move all workers onto private connections, then remove the public rule.

```bash
tcld namespace set-connectivity-rules \
    --namespace "my-namespace.abc123" \
    --connectivity-rule-ids "rule-id-1" \
    --connectivity-rule-ids "rule-id-2"
```

Alias: `tcld n scrs`.

Rules are attached **as a set** -- to remove one rule while keeping others, re-specify only the rules to keep.

Remove all rules (makes Namespace public again):

```bash
tcld namespace set-connectivity-rules --namespace "my-namespace.abc123" --remove-all
```

Rules can also be set at Namespace creation time with `--connectivity-rule-ids`:

```bash
tcld namespace create \
    --namespace test-namespace.a1b2c \
    --region us-east-1 \
    --auth-method api_key \
    --connectivity-rule-ids <rule_id1> \
    --connectivity-rule-ids <rule_id2>
```

View rules for a Namespace:

```bash
tcld connectivity-rule list -n "my-namespace.abc123"
```

Or view them as part of `tcld namespace get`.

---

## Troubleshooting pointers

### PSC endpoint stuck in Pending

- Most common cause: no Connectivity Rule exists for the connection ID.
- Check that `--connection-id`, `--region`, and `--gcp-project-id` in the Connectivity Rule match the endpoint exactly.
- The endpoint's region must be a supported Temporal Cloud region.

### PrivateLink TLS handshake fails

- If using API key auth over PrivateLink/PSC with the wrong TLS server name, the handshake fails with `connection reset by peer` even though `nc` shows the port is open.
- Verify the TLS server name override matches the auth-method table above.

### Network connectivity check

```bash
nc -zv <endpoint_host> 7233
```

For full connectivity diagnosis, see the triage `../triage/connectivity.md` reference.
