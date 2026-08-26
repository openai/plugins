# Connectivity

Diagnose failures to reach the Temporal frontend at the network layer — DNS resolution, TCP reachability, wrong endpoint, firewall/proxy drops, PrivateLink / Private Service Connect routing. This file covers layers 1 and 2 of the [diagnostic ladder](diagnostic-ladder.md).

Out of scope here:
- TLS handshake / x509 / server-name mismatch → [certificates.md](certificates.md) (layer 3)
- gRPC `UNAUTHENTICATED` / `PERMISSION_DENIED` → [authentication.md](authentication.md) (layer 4)
- gRPC `RESOURCE_EXHAUSTED` → [rate-limits.md](rate-limits.md)
- `context deadline exceeded` (ambiguous) → [runtime-errors.md](runtime-errors.md)

## Table of Contents

- [Connection refused](#connection-refused)
- [DNS](#dns)
- [Endpoint formats](#endpoint-formats)
- [Firewall and proxy](#firewall-and-proxy)
- [PrivateLink and PSC](#privatelink-and-psc)
- [Quick diagnostic scripts](#quick-diagnostic-scripts)
- [Connection error reference](#connection-error-reference)

## Connection refused

**Symptom shape:** OS-level `connection refused` reported inside a gRPC `UNAVAILABLE` status, or by tools like `nc` / `curl` before any gRPC is attempted. The string `connection refused` is emitted by the Go `net` package wrapping `ECONNREFUSED`.

**What it means:** a TCP SYN reached the host but nothing was listening on that port (RST response). This is layer 2 — the host is up and routable; the process you wanted is not.

**Things to check (not attributed causes — verify each one):**
- **Dev server not running.** The local dev server is `temporal server start-dev`, which listens on `localhost:7233` by default .
- **Wrong port.** Temporal Cloud's Namespace gRPC endpoint is on port `7233`. The Cloud Ops / control-plane endpoint `saas-api.tmprl.cloud` is on port `443`, not `7233` — pointing a worker or `temporal` CLI data-plane command at `saas-api.tmprl.cloud:7233` will not connect.
- **Self-hosted frontend not accepting connections.** Verify from the process/pod perspective that the frontend is listening on the configured port.

**First check:**

```bash
nc -zvw10 <host> 7233
```

On macOS/BSD `nc`, `-z` scans without sending data, `-v` is verbose, `-w <timeout>` sets the idle/connection timeout in seconds. If this fails with "Connection refused" no higher layer (TLS, gRPC, auth) can succeed.

## DNS

**Symptom shape:** errors containing `no such host` (Go's `net` package wrapping `EAI_NONAME` / NXDOMAIN), or resolver-specific messages from the libc resolver (`nodename nor servname provided`, `Temporary failure in name resolution`) bubbled up through Go.

**What it means:** the resolver could not produce an IP for the hostname. No TCP attempt happens.

**Things to check:**
- **Namespace endpoint format.** Temporal Cloud Namespace Endpoint is `<namespace>.<account>.tmprl.cloud:7233`. A short namespace name without the `.<account>` suffix will not resolve.
- **Typo in the namespace or account ID.** The hostname must match the Namespace page in the Cloud UI exactly.
- **Broken resolver in the client environment.** Container with missing/empty `/etc/resolv.conf`, CoreDNS not running in the cluster, split-tunnel VPN that isn't forwarding DNS for `*.tmprl.cloud`.
- **PrivateLink / PSC private DNS not set up.** When a namespace is served via a private connection, public DNS still returns a public IP; without a private hosted zone the client may resolve an address it cannot route. See [PrivateLink and PSC](#privatelink-and-psc) below and `/cloud/connectivity` for the required DNS configuration.

**First check:**

```bash
nslookup <namespace>.<account>.tmprl.cloud
dig <namespace>.<account>.tmprl.cloud
dig +short <namespace>.<account>.tmprl.cloud # short-form answer
```

Interpreting results:

- For a **public-internet Namespace**, the A record resolves to a public IP (CNAME chain through `<cloud>-<region>.region.tmprl.cloud`).
- For a **PrivateLink/PSC Namespace with private DNS configured**, the Namespace hostname should resolve to the VPC endpoint address (AWS VPCE DNS name) or the PSC internal IP (GCP) from inside the VPC.
- For an HA (multi-region) Namespace, the Namespace record is a CNAME to `<cloud>-<region>.region.tmprl.cloud` where `<region>` is the currently active region.

## Endpoint formats

Using the wrong endpoint family is one of the most common causes of "cannot connect" reports.

| Purpose | Endpoint pattern | Port | Source |
|---|---|---|---|
| Cloud Namespace Endpoint (recommended default for workers, SDKs, and `temporal` CLI data-plane — mTLS and API-key-only) | `<namespace>.<account>.tmprl.cloud` | 7233 |  |
| Cloud API Regional Endpoint (explicit region pin; dual-auth API-key path; some private-connectivity setups) | `<region>.<cloud_provider>.api.temporal.io` | 7233 | |
| Cloud HA Regional Endpoint (pin to a specific HA replica region) | `<cloud>-<region>.region.tmprl.cloud` | 7233 | |
| Cloud control-plane (Cloud Ops API, `tcld`, Terraform provider) | `saas-api.tmprl.cloud` | 443 | |
| Self-hosted frontend | `<your-frontend-host>` | `7233` default | deployment-specific |
| Local dev server | `localhost` | `7233` default | `temporal server start-dev` |

Notes:

- The **Namespace Endpoint** is the recommended default for Temporal Clients (SDK, workers, `temporal` CLI) for both mTLS and API-key-only Namespaces, because it transparently follows HA failovers without a client change .
- The **API Regional Endpoint** is for explicit region pinning, some private-connectivity setups, and **dual-auth pre-release** (which does not support API key auth to a Namespace Endpoint). When using **mTLS** against an API Regional, HA Regional, or VPCE address, the client must set the TLS server name to the Namespace Endpoint value (see [certificates.md → server name override](certificates.md#server-name-override)).
- Do not conflate the API Regional form (`*.api.temporal.io`) with the HA Regional form (`*.region.tmprl.cloud`) — both are “regional” in docs, but they are different hostnames.
- `saas-api.tmprl.cloud` is **not** a workflow data-plane endpoint — pointing a worker or `temporal workflow …` command at it will not work.
- The `--address` flag (env `TEMPORAL_ADDRESS`) takes `host:port`, not a URL.

**Private connectivity (PrivateLink / PSC):** When using private endpoints without private DNS, the TLS server name override varies by auth method:

| Auth method | TLS server name |
|---|---|
| mTLS (single-region) | Namespace Endpoint, e.g. `my-namespace.my-account.tmprl.cloud` |
| API key (single-region) | Regional API endpoint, e.g. `us-east-1.aws.api.temporal.io` (or `us-central1.gcp.api.temporal.io`) |
| Multi-region (mTLS or API key) | Active region endpoint, e.g. `aws-us-east-1.region.tmprl.cloud` |

For full private connectivity setup (PrivateLink, PSC, connectivity rules), see [cloud-connectivity.md](../ops/cloud-connectivity.md).

See also [cli-conventions.md → Connection and identity](../ops/cli-conventions.md#connection-and-identity) for the endpoint / env-var reference.

## Firewall and proxy

**Symptom shape:** `nc -zvw10` hangs and then reports failure; or the TCP connection completes but no bytes are returned during TLS handshake. Depending on the device, a middlebox may silently drop packets (timeout), send TCP RST (looks like `connection refused` late in the session), or terminate and re-originate TLS (breaks mTLS).

**Things to check:**
- **Egress allowlist.** Corporate proxy, AWS security group / NACL, or Kubernetes NetworkPolicy permitting TCP egress to the Temporal endpoint on the correct port. For AWS PrivateLink, the VPC-endpoint security group must accept TCP ingress to port 7233.
- **TLS-inspecting proxy in the path.** A device that terminates and re-originates TLS will break mTLS client-certificate authentication because the proxy presents its own certificate downstream and can't forward the client's private key. Detection heuristic: `nc -zvw10` succeeds (TCP works) but an `openssl s_client` against the same host returns an unexpected certificate chain or is closed without a TLS alert.

**First check:**
- Run `nc -zvw10 <host> 7233` from the failing environment. A connect with no data is enough to confirm TCP reachability; that isolates the problem above layer 2.
- For TLS-inspection hypotheses, compare the server certificate returned by `openssl s_client -connect <host>:7233 -servername <host>` (see [certificates.md → OpenSSL recipes](certificates.md#openssl-recipes)) against the expected Temporal Cloud CA/issuer.

**Fix direction:**
- Allow egress on TCP/7233 to the Temporal endpoint (or the VPCE / PSC IP when using private connectivity).
- Bypass TLS inspection for the Temporal endpoint. Re-signing TLS is incompatible with mTLS client-cert auth.

## PrivateLink and PSC

Temporal Cloud supports private connectivity via AWS PrivateLink and GCP Private Service Connect in addition to the default public internet endpoints. This section is layer 1–2 diagnosis only; the full setup reference is in `docs/cloud/connectivity/`.

Classification of common layer-1/2 failures after PrivateLink/PSC is supposed to be in use:

- **DNS resolves to a public IP, VPC cannot route it.** Private DNS (Route 53 PHZ in AWS, Cloud DNS private zone in GCP) is missing or not attached to the workers' VPC. Without it, the client gets the public A record, and the VPC has no egress to the internet. See the private-DNS setup in `/cloud/connectivity/aws-connectivity` or `/cloud/connectivity/gcp-connectivity`.
- **DNS resolves to the private endpoint, port unreachable.** Likely the VPC-endpoint security group is not permitting TCP/7233 from the client subnet.
- **Connection succeeds but TLS fails with a server-name mismatch.** This is layer 3, not layer 2. Clients connecting by VPC-endpoint DNS name must set the TLS server name (SNI override) to the Namespace Endpoint (`<namespace>.<account>.tmprl.cloud`). Details in [certificates.md → server name override](certificates.md#server-name-override).
- **Works before failover, breaks after failover (HA Namespaces).** For multi-region Namespaces, the Namespace record CNAMEs to `<cloud>-<region>.region.tmprl.cloud`, and on failover the CNAME is updated to point to the new active region. If private DNS only overrides the old region, workers lose the path on failover. The `region.tmprl.cloud` private zone must cover every region the Namespace can fail over to. Note: automatic DNS-based failover is not supported for GCP PSC — manual worker reconfiguration is required.

**Quick reachability check from inside the client's VPC:**

```bash
# AWS VPCE DNS name, or GCP PSC IP
nc -zvw10 vpce-0123456789abcdef-abc.us-east-1.vpce.amazonaws.com 7233
```

.

## Quick diagnostic scripts

Run from the failing environment (the pod, container, or host where the problem reproduces). These scripts chain the layer-1/2 checks with a final `temporal` call to confirm the whole stack end-to-end.

### mTLS variant

```bash
#!/bin/bash
NS="your-namespace.account-id"
CERT="client.pem"
KEY="client.key"
HOST="$NS.tmprl.cloud"
ADDRESS="$HOST:7233"

echo "=== DNS resolution ==="
nslookup "$HOST"

echo "=== TCP reachability ==="
nc -zvw10 "$HOST" 7233

echo "=== TLS handshake (see certificates.md for deeper TLS diagnosis) ==="
openssl s_client -connect "$ADDRESS" \
  -servername "$HOST" \
  -cert "$CERT" -key "$KEY" </dev/null 2>&1 | head -20

echo "=== Temporal CLI end-to-end ==="
temporal workflow list --limit 1 \
  --address "$ADDRESS" \
  --namespace "$NS" \
  --tls-cert-path "$CERT" \
  --tls-key-path "$KEY"
# --address: docs/cli/cmd-options.mdx:137
# --namespace: docs/cli/cmd-options.mdx:420
# --tls-cert-path: docs/cli/cmd-options.mdx:661
# --tls-key-path: docs/cli/cmd-options.mdx:673
# --limit: docs/cli/cmd-options.mdx:379
```

### API-key variant

For API-key-only Namespaces, default to the **Namespace Endpoint**. Use the API Regional form for region pin / dual-auth / some private-connectivity setups.

```bash
#!/bin/bash
NS="your-namespace.account-id"
ADDRESS="<namespace>.<account>.tmprl.cloud:7233"   # default for API-key-only
# ADDRESS="<region>.<cloud_provider>.api.temporal.io:7233"  # region pin / dual-auth
HOST="${ADDRESS%:*}"
export TEMPORAL_API_KEY="..."

echo "=== DNS resolution ==="
nslookup "$HOST"

echo "=== TCP reachability ==="
nc -zvw10 "$HOST" 7233

echo "=== TLS handshake ==="
openssl s_client -connect "$ADDRESS" \
  -servername "$HOST" </dev/null 2>&1 | head -20

echo "=== Temporal CLI end-to-end ==="
temporal workflow list --limit 1 \
  --address "$ADDRESS" \
  --namespace "$NS" \
  --api-key "$TEMPORAL_API_KEY"
```

A lighter end-to-end probe, with fewer moving parts, is `temporal operator cluster health --address <address>` — if it returns `SERVING`, the client reached a Temporal frontend through all of DNS, TCP, TLS, and gRPC.

## Connection error reference

Each row's error text comes from outside Temporal — either the Go `net` package (syscall wrapping) or the gRPC runtime. Tagged accordingly.

| Error text (shape) | Origin | Layer | One thing to check |
|---|---|---|---|
| `no such host` | Go net / libc resolver | 1 (DNS) | Endpoint hostname typo; missing `.<account>` suffix; resolver / VPN / private DNS configuration |
| `connection refused` | Go net (ECONNREFUSED) | 2 (TCP) | Wrong port, dev server not running, data-plane command pointed at `saas-api.tmprl.cloud` |
| `i/o timeout` | Go net | 2 (TCP) | Silent drop by firewall / NACL / NetworkPolicy |
| `network is unreachable` | Go net (ENETUNREACH) | 2 (routing) | No route from client subnet to target |
| `UNAVAILABLE` with a connection-layer cause | gRPC status | 2–3 | Peel back to the wrapped `net` error; `UNAVAILABLE` on its own can also come from TLS and gRPC layers |
| `context deadline exceeded` | Go context | ambiguous | Not diagnostic on its own; see [runtime-errors.md](runtime-errors.md) |
| `Failed reaching server: last connection error` | Temporal Cloud client diagnostics | usually 3 (TLS) | Most often an expired TLS cert per the troubleshooting guide — jump to [certificates.md](certificates.md) |

For TLS-layer errors that surface through `UNAVAILABLE` or masquerade as connectivity, jump to [certificates.md](certificates.md). For `UNAUTHENTICATED` / `PERMISSION_DENIED`, [authentication.md](authentication.md). For `RESOURCE_EXHAUSTED`, [rate-limits.md](rate-limits.md).
