# SDK Snippet Review

A Layer-0 config check that runs **before** the [diagnostic ladder](diagnostic-ladder.md). When a user pastes SDK connection code (or just the address / namespace / auth fields), the snippet itself is frequently the whole bug — wrong endpoint family, short namespace, auth method mismatched to the Namespace. Running DNS / TCP / TLS probes at that point "fixes" nothing, because nothing lower is broken.

This file is a **cross-SDK** checklist for **Temporal Cloud** client/worker connection config. SDK-specific field names (`tls.Config{}` in Go, `Connection.connect({ tls })` in TypeScript, `TLSConfig` in Python) belong to `skill-temporal-developer`. Stay at the level of: endpoint, namespace, auth method, TLS expectations, env vars.

Out of scope here:
- Network-layer probes (DNS / TCP / TLS / auth) → [diagnostic-ladder.md](diagnostic-ladder.md)
- Endpoint-family rationale and DNS failure shapes → [connectivity.md → Endpoint formats](connectivity.md#endpoint-formats)
- API-key lifecycle and address guidance → [authentication.md → Address form for API-key connections](authentication.md#address-form-for-api-key-connections)
- mTLS certificate validation → [certificates.md](certificates.md)

## Table of Contents

- [When to use this check](#when-to-use-this-check)
- [Review order](#review-order)
- [Endpoint form](#endpoint-form)
- [Namespace format](#namespace-format)
- [Auth method](#auth-method)
- [TLS expectations](#tls-expectations)
- [Environment variables](#environment-variables)
- [Common misconfigurations](#common-misconfigurations)
- [Quick routing](#quick-routing)

## When to use this check

Run snippet review when the user pastes SDK connection code **and** reports any of:

- Cannot connect to Cloud, `UNAVAILABLE` on first attempt
- `UNAUTHENTICATED` / `PERMISSION_DENIED` on first attempt
- `context deadline exceeded` with no prior-success baseline
- `namespace not found` / `INVALID_ARGUMENT`
- "This worked yesterday" **after** a config change

Skip snippet review (go straight to the ladder) when the user has an established, previously-working config and the symptom is new — the snippet is not the culprit, something in the environment changed.

## Review order

Check in this order. Each step is cheaper than the one below it, and a failure at a higher step makes the lower ones moot.

1. **Auth method** — API key vs mTLS. This determines everything else.
2. **Endpoint form** — must be a plausible Cloud data-plane address for that auth method (see below).
3. **Namespace** — full `<namespace>.<account>` form.
4. **TLS expectations** — principle-level, per auth method.
5. **Env-var propagation** — are the `TEMPORAL_*` / `TEMPORAL_CLOUD_*` values actually reaching the client?

If any of steps 1–3 is wrong, fix that first. Do not start the diagnostic ladder until endpoint, namespace, and auth method are plausible — the ladder will produce misleading results.

## Endpoint form

Cloud data-plane endpoints (port `7233`) plus the control-plane endpoint:

| Purpose | Form | Typical use |
|---|---|---|
| Namespace Endpoint (recommended default) | `<namespace>.<account>.tmprl.cloud:7233` | mTLS and API-key-only Namespaces; follows HA failovers  |
| API Regional Endpoint | `<region>.<cloud_provider>.api.temporal.io:7233` | Explicit region pin; private connectivity without private DNS; dual-auth pre-release (API key cannot use Namespace Endpoint) |
| HA Regional Endpoint | `<cloud>-<region>.region.tmprl.cloud:7233` | Pin to a specific HA replica region |
| Control plane (`tcld`, Cloud Ops API, Terraform) | `saas-api.tmprl.cloud:443` | **Not** a workflow / worker endpoint |

The Namespace Endpoint follows HA failovers transparently. When a client pins to an API Regional or HA Regional Endpoint (or a PrivateLink/PSC DNS name) with **mTLS**, the client **must** override the TLS `server_name` to the Namespace Endpoint value — see [certificates.md → Server name override](certificates.md#server-name-override).

**Snippet smells:**

- Short hostname without `.<account>` or `.tmprl.cloud` / `.api.temporal.io` — stale docs / wrong form.
- `saas-api.tmprl.cloud` as the data-plane address — that's the control plane on port 443, not a workflow endpoint. Pointing a worker or `temporal` CLI data-plane command at it will not connect.
- Dual-auth (`api_key_or_mtls`) Namespace + API key + Namespace Endpoint — pre-release dual-auth does not support API key auth to the Namespace Endpoint; use the API Regional Endpoint.
- mTLS + Regional / VPCE address **without** SNI override — the TLS handshake will fail with `x509: certificate is valid for <SANs>, not <requested host>`. See [certificates.md → Hostname mismatch](certificates.md#hostname-mismatch).
- Empty `HostPort` / address with a Cloud namespace set — no explicit Cloud endpoint; the client will attempt a local-dev default that won't reach Cloud.
- URL form (`https://…`) in `--address` / `TEMPORAL_ADDRESS` — the flag takes `host:port`, not a URL.

## Namespace format

Cloud namespace format is `<namespace_name>.<account_id>`. The account suffix is visible in the Cloud UI and in `tcld namespace list`.

**Snippet smells:**

- Short name (`payments`) without the account suffix — fails resolution, or produces `INVALID_ARGUMENT: namespace not found`.
- Namespace set in the address but not in the namespace field (or vice versa) — both values are required.
- Case mismatch — namespace strings are case-sensitive. Match the Cloud UI exactly.
- Namespace from the wrong account — looks correct but the user isn't logged into that account. Verify with `tcld account get` (see [authentication.md → Cloud role and permission model](authentication.md#cloud-role-and-permission-model)).

## Auth method

One auth method per client connection. A snippet that sets both mTLS cert flags **and** an API key is a configuration smell — some SDKs apply both (API key credentials plus client certs), which is ambiguous and hard to debug. Prefer exactly one.

**Snippet smells:**

- Both `tls-cert-path` / `tls-key-path` **and** `api-key` set — pick one.
- API key in the snippet but the Namespace auth method is `mtls` only (or vice versa). Check with `tcld namespace auth-method get --namespace <ns>`. Migrate via Support or `tcld namespace auth-method set` (`mtls`, `api_key`, or pre-release `api_key_or_mtls`) — recreate is not the only path.
- Auth method mismatched against endpoint constraints (especially dual-auth + Namespace Endpoint for API keys — see [Endpoint form](#endpoint-form)).

## TLS expectations

Principle-level only. Do not diagnose SDK-specific struct fields here — that belongs to `skill-temporal-developer`.

- **API key auth.** TLS is **required**. The client opens a TLS connection (server TLS only, no client cert) and presents the API key as a bearer credential at the gRPC layer. An API-key snippet with TLS explicitly disabled will not connect.
- **mTLS auth.** Client certificate and private key are **required**. The certificate must chain to a CA that the namespace accepts — verify with `tcld namespace accepted-client-ca list --namespace <ns>` (see [certificates.md → Accepted client CA set (mTLS Cloud)](certificates.md#accepted-client-ca-set-mtls-cloud)). The key file must match the cert; see [certificates.md → Key does not match cert](certificates.md#key-does-not-match-cert).

**Snippet smells:**

- API key connection with TLS disabled or with an `insecure` flag set — the server will close the connection.
- mTLS snippet without a key file, or key and cert from different generations.
- `--tls-disable-host-verification` / `TEMPORAL_TLS_DISABLE_HOST_VERIFICATION=true` in a snippet the user expects to work in production — this masks hostname-mismatch bugs rather than fixes them.

## Environment variables

Two families. Do not mix them up.

### `temporal` CLI (and common SDK / envconfig names)

| Variable | Purpose | CLI flag |
|---|---|---|
| `TEMPORAL_ADDRESS` | `host:port` (not a URL) | `--address` |
| `TEMPORAL_NAMESPACE` | `<namespace>.<account>` | `--namespace` |
| `TEMPORAL_API_KEY` | API-key secret for `temporal` CLI / SDKs | `--api-key` |
| `TEMPORAL_TLS_CA` | Server CA certificate path | `--tls-ca-path` |
| `TEMPORAL_TLS_CERT` | Client x509 certificate path (CLI legacy name) | `--tls-cert-path` |
| `TEMPORAL_TLS_KEY` | Client private key path (CLI legacy name) | `--tls-key-path` |
| `TEMPORAL_TLS_SERVER_NAME` | SNI override (regional / VPCE + mTLS) | `--tls-server-name` |
| `TEMPORAL_TLS_DISABLE_HOST_VERIFICATION` | Default `false` | `--tls-disable-host-verification` |

SDK envconfig also accepts `TEMPORAL_TLS_CLIENT_CERT_PATH` / `TEMPORAL_TLS_CLIENT_KEY_PATH` (and `*_DATA` variants). Those are real for SDKs — not typos. The CLI's legacy names are `TEMPORAL_TLS_CERT` / `TEMPORAL_TLS_KEY`.

### `tcld` / Terraform (control plane)

| Variable | Purpose |
|---|---|
| `TEMPORAL_CLOUD_API_KEY` | API key for `tcld` and the Terraform provider |

`TEMPORAL_API_KEY` is **not** what `tcld` reads. Public Cloud docs that say otherwise are wrong vs current `tcld` source.

**Snippet smells:**

- Snippet hardcodes a value that an env var also sets. Precedence is SDK-specific; the effective value may not be what the snippet shows. Ask the user to echo the env var from the exact shell / container the client runs in.
- Env vars set in the user's interactive shell but the worker runs in a different shell / container / pod where they are absent.
- Wrong tool's API-key env var — `TEMPORAL_CLOUD_API_KEY` for an SDK/`temporal` CLI client, or `TEMPORAL_API_KEY` for `tcld`. Symptom: "my config doesn't take effect."
- Typo that truly does not exist — e.g. `TEMPORAL_TLS_CERT_FILE`. Unknown variables are ignored.
- Mixing env vars and explicit flags across auth methods — e.g. `TEMPORAL_API_KEY` set in the environment, but the snippet also passes `--tls-cert-path`. See [Auth method](#auth-method) above.

## Common misconfigurations

| Snippet shape | Likely root cause | First fix |
|---|---|---|
| API key + short / wrong hostname | Missing Namespace Endpoint or wrong family | Use `<ns>.<acct>.tmprl.cloud:7233` (default) or the API Regional form when pinning / dual-auth requires it |
| Dual-auth Namespace + API key + `*.tmprl.cloud` | Dual-auth pre-release blocks API key on Namespace Endpoint | Switch to `<region>.<provider>.api.temporal.io:7233` |
| mTLS + `*.api.temporal.io` / `*.region.tmprl.cloud` / VPCE without SNI | Regional / private address needs `server_name = <ns>.<acct>.tmprl.cloud` | Add SNI override, or switch to Namespace Endpoint |
| Short namespace (`payments`) | Missing account suffix | Use `<ns>.<account>` from `tcld namespace list` |
| Empty HostPort / address, Cloud namespace set | No explicit Cloud endpoint | Add Namespace Endpoint (or Regional when required) |
| API key **and** mTLS cert both configured | Ambiguous; may present both | Remove whichever you are not using |
| `saas-api.tmprl.cloud` as address | Control plane mistaken for data plane | Switch to Namespace or Regional Endpoint |
| `https://…` in `--address` | Flag takes `host:port`, not a URL | Strip the scheme |
| SDK/`temporal` CLI with only `TEMPORAL_CLOUD_API_KEY` | Wrong env var for that client | Set `TEMPORAL_API_KEY` |
| `tcld` with only `TEMPORAL_API_KEY` | Wrong env var for tcld | Set `TEMPORAL_CLOUD_API_KEY` |
| CLI expected, but only `TEMPORAL_TLS_CLIENT_CERT_PATH` set | CLI reads `TEMPORAL_TLS_CERT` | Rename for CLI, or keep `_CLIENT_` names for SDK envconfig |

## Quick routing

- Snippet looks plausible on all five review points → proceed to [diagnostic-ladder.md](diagnostic-ladder.md).
- Snippet has an obvious wrong endpoint, namespace, or auth method → fix that first; do not run network-layer probes until it's corrected.
- Snippet fix applied and symptom persists → descend the ladder from layer 1 (DNS). The environment may have a second, independent problem.
- Snippet references SDK-specific struct fields, connection-builder objects, or runtime-specific TLS APIs that aren't covered here → hand off to `skill-temporal-developer`.
