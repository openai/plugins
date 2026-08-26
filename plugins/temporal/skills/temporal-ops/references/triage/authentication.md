# Authentication

Diagnose failures that happen *after* TLS has completed — the TCP connection is up, the handshake finished, and the peer returned a gRPC error about who you are or what you can do. This file covers layer 4 of the [diagnostic ladder](diagnostic-ladder.md).

Prerequisite: rule out layers 1–3 first. If `openssl s_client` (see [certificates.md → openssl recipes](certificates.md#openssl-recipes)) does not print `Verify return code: 0 (ok)`, the problem is not in this file.

Out of scope here:
- DNS / TCP / endpoint family → [connectivity.md](connectivity.md) (layers 1–2)
- TLS handshake / x509 / SNI override → [certificates.md](certificates.md) (layer 3)
- gRPC `RESOURCE_EXHAUSTED` → [rate-limits.md](rate-limits.md)
- `context deadline exceeded` (ambiguous) → [runtime-errors.md](runtime-errors.md)

## Table of Contents

- [Authentication vs authorization](#authentication-vs-authorization)
- [UNAUTHENTICATED vs PERMISSION_DENIED](#unauthenticated-vs-permission_denied)
- [API-key authentication](#api-key-authentication)
- [mTLS authentication after TLS completes](#mtls-authentication-after-tls-completes)
- [Cloud role and permission model](#cloud-role-and-permission-model)
- [Quick routing](#quick-routing)

## Authentication vs authorization

Temporal Cloud distinguishes authentication from authorization, but **API keys and mTLS do not share the same authorization model**.

### API keys

- **Authentication** — *who you are*. The API key is valid and active. Failure → `UNAUTHENTICATED`.
- **Authorization** — *what you can do*. Key → User or Service Account → Cloud RBAC. Failure → `PERMISSION_DENIED`.

The authorization pathway for API keys is documented as "API key (authentication) → Identity (user or Service Account) → RBAC (authorization)".

### mTLS

- **Authentication (connection)** — client cert chains to an accepted Namespace CA. Failure is usually a **TLS-layer** error (`tls:` / `x509:`), not gRPC `UNAUTHENTICATED`. See [certificates.md](certificates.md).
- **Authorization (Namespace access)** — after a clean handshake: no certificate filters → full Namespace data-plane access; with filters → leaf must match or the connection is rejected (exact wire signal is release-dependent — see [certificates.md](certificates.md)).

**mTLS is not tied to Cloud RBAC identities** (User / Service Account / Namespace Read|Write|Admin). Access is CA trust + optional filters. Do not triage mTLS `PERMISSION_DENIED` via `tcld user get`. Check CA, filters, Namespace name (`<ns>.<account>`), and Namespace auth method.

## UNAUTHENTICATED vs PERMISSION_DENIED

The two gRPC codes in this file, per the gRPC spec:

| Code | Meaning in the spec | What it tells you on Temporal Cloud |
|---|---|---|
| `UNAUTHENTICATED` | The request does not have valid authentication credentials for the operation. | Almost always an **API key** problem: missing, typo, disabled, deleted, expired, or wrong auth method for the Namespace. Untrusted mTLS certs usually fail at TLS (`UNAVAILABLE` / `x509:`), not here. |
| `PERMISSION_DENIED` | The caller does not have permission to execute the specified operation. Distinct from `UNAUTHENTICATED`. | **API key:** identity known but lacks the Namespace-level permission (`Read` / `Write` / `Admin`) or the account-level role required for the action (including Owner/Admin inheritance). **mTLS:** often cert-filter mismatch, wrong Namespace, or auth-method mismatch — not missing Cloud RBAC. |

Two traps this distinction prevents:

- **`UNAVAILABLE` is not an auth code.** If your error is gRPC `UNAVAILABLE`, TLS may have failed before any auth happened. Peel the wrapped cause; if it starts with `tls:`, `x509:`, or `remote error: tls:`, jump to [certificates.md](certificates.md). The troubleshooting guide names an expired TLS certificate as a common root cause of "looks like auth but isn't."
- **`RESOURCE_EXHAUSTED` is not `PERMISSION_DENIED`.** A rate-limited caller is *allowed* to make the call but is being throttled. See [rate-limits.md](rate-limits.md).

Do not use `FORBIDDEN` or `FAILED_PRECONDITION` as auth codes. `FORBIDDEN` is not a gRPC code; `FAILED_PRECONDITION` is a gRPC code but is unrelated to Cloud auth decisions.

## API-key authentication

### How the Temporal CLI and SDKs pick up the key

The Temporal CLI reads the API key either from the `--api-key` flag or from the `TEMPORAL_API_KEY` environment variable. The Cloud docs: "The CLI automatically picks up the `TEMPORAL_API_KEY` environment variable from your shell."

`tcld` and the Terraform provider use a **different** env var: `--api-key` or `TEMPORAL_CLOUD_API_KEY` (confirmed in `tcld` source `app/flags.go`). Do not tell a `tcld` user to set `TEMPORAL_API_KEY` — and do not tell an SDK / `temporal` CLI user that `TEMPORAL_CLOUD_API_KEY` is enough. Public api-keys docs that claim `tcld` reads `TEMPORAL_API_KEY` are stale vs current `tcld`.

This section covers data-plane API-key auth (`TEMPORAL_API_KEY` / `--api-key` on `temporal` CLI and SDKs).

### Address form for API-key connections

For **API-key-only** Namespaces, the Cloud API-keys guide and SDK develop docs recommend the **Namespace Endpoint**: `<namespace>.<account_id>.tmprl.cloud:7233`.

Use the **API Regional Endpoint** (`<region>.<cloud_provider>.api.temporal.io:7233`) when:

- The client needs an explicit region pin
- Private connectivity without private DNS (SNI / server name may need the regional API hostname — see [connectivity.md](connectivity.md#endpoint-formats))
- The Namespace uses **dual auth** (`api_key_or_mtls`, pre-release): API keys cannot use the Namespace Endpoint on these Namespaces — enable via Support; HA is not supported in this mode

If an API key fails on the Namespace Endpoint, try Regional before assuming the key is bad (especially if the Namespace allows both auth methods). See the endpoint table in [connectivity.md → endpoint formats](connectivity.md#endpoint-formats) for the full comparison.

### Things to check when `UNAUTHENTICATED` is returned with an API key

Per the Cloud troubleshooting note: "Invalid API key errors: Check that you copied the key correctly and that it hasn't been revoked or expired."

- **Key not delivered to the process.** Inside the failing environment (pod/container/host), confirm `TEMPORAL_API_KEY` is set: `env | grep -i TEMPORAL_API_KEY`. A shell-level export on the developer's laptop is not inherited by a container.
- **Key typo or truncation.** Leading/trailing whitespace, a trailing newline from a copy-paste, or a shell that split the key on whitespace will all produce `UNAUTHENTICATED`.
- **Key disabled.** A disabled key cannot authenticate — per the Cloud docs: "When disabled, an API key cannot authenticate with Temporal Cloud." Check with `tcld apikey list` or `tcld apikey get --id <apikey_id>`.
- **Key deleted.** Per the Cloud docs: "Deleting an API key stops it from authenticating with Temporal Cloud."
- **Key expired.** API keys expire based on the `--duration` or `--expiry` set at creation time. The FAQ caps expiry at 2 years.
- **Wrong address / auth combo.** See above — default to Namespace Endpoint for API-key-only; use API Regional when pinning, private connectivity, or a dual-auth (`api_key_or_mtls`) Namespace requires it.
- **API keys disabled at the account level.** A Global Administrator or Account Owner can disable the *creation* of new API keys with the **Disable Create API Keys** control; existing keys continue to work until disabled, deleted, or expired. This does not on its own turn a working key into `UNAUTHENTICATED`.

### API-key lifecycle commands

Every command here is grounded in `docs/cloud/tcld/apikey.mdx`. The `tcld apikey` group alias is `ak`.

```bash
# Create
tcld apikey create --name <name>
# Command and required flag:
# Optional: --description, --duration, --expiry, --request-id
#   --description:
#   --duration:
#   --expiry:
#   --request-id:

# List (to find the ID for disable/enable/delete)
tcld apikey list
# Command:

# Inspect a specific key
tcld apikey get --id <apikey_id>
# Command:

# Disable / enable
tcld apikey disable --id <apikey_id>
tcld apikey enable  --id <apikey_id>
# disable:
# enable:

# Delete
tcld apikey delete --id <apikey_id>
# Command:
```

### Rotating without downtime

The Cloud docs prescribe this sequence: create a new key; verify both keys work; switch clients to the new key; delete the old key.

Key behavioral note: "Deleting or disabling a key removes its ability to authenticate into Temporal Cloud. If you delete or disable an API key being used by Workers to run a Workflow, those Workers will be unable to connect to Temporal until a new API key secret is created and configured." That is why the rotation order is "deploy new, verify, then delete old" and not the reverse.

### Discriminating with a CLI smoke test

Prefer Namespace Endpoint for API-key-only Namespaces. Use Regional for dual-auth Namespaces or when Namespace Endpoint fails:

```bash
# Preferred for API-key-only Namespaces
temporal workflow list --limit 1 \
  --address <namespace>.<account_id>.tmprl.cloud:7233 \
  --namespace <namespace>.<account_id> \
  --api-key "$TEMPORAL_API_KEY"

# Fallback: Regional Endpoint (dual-auth API-key clients, region pin, private connectivity)
temporal workflow list --limit 1 \
  --address <region>.<cloud_provider>.api.temporal.io:7233 \
  --namespace <namespace>.<account_id> \
  --api-key "$TEMPORAL_API_KEY"
# --address / --namespace / --api-key flags: docs/cli/setup-cli.mdx
```

Interpret the result:

| CLI result | Where the chain broke | Where to go |
|---|---|---|
| Returns a list (possibly empty) | Auth and authorization both succeeded | Issue is elsewhere — look at the SDK / worker config |
| `UNAUTHENTICATED` | Key itself is rejected (disabled, deleted, expired, typo, wrong env var, wrong endpoint / auth combo) | Re-run the [things-to-check list above](#things-to-check-when-unauthenticated-is-returned-with-an-api-key) |
| `PERMISSION_DENIED` | Key is authenticated but the identity lacks Namespace permission | [Cloud role and permission model](#cloud-role-and-permission-model) |
| API key rejected on the Namespace Endpoint (mTLS-only or dual-auth Namespace) | Wrong endpoint for the auth combo | Try the API Regional Endpoint |
| An `x509:` or `tls:` error | Not an auth issue | [certificates.md](certificates.md) |

A lighter probe is `temporal operator cluster health --address <addr>` — if it returns `SERVING`, the client can reach the frontend service.

## mTLS authentication after TLS completes

If the TLS handshake succeeded (the peer did not send a `tls:` alert and the client did not emit an `x509:` error — see [certificates.md](certificates.md) for those), remaining mTLS failures are usually:

1. **Certificate filter mismatch** — leaf does not match any filter. See [Certificate filters](#certificate-filters) below.
2. **Wrong Namespace** (missing `.<account>` suffix, or CA not configured on the target Namespace) or **wrong auth method** (API-key-only Namespace).

Case (1) is an authorization rejection *after* a clean TLS handshake. The exact wire signal is release-dependent — you may see a TLS-layer alert (`remote error: tls: bad certificate`) or a post-handshake gRPC `PERMISSION_DENIED`; read the observed error rather than pinning a string. An untrusted CA fails earlier, at the handshake (`remote error: tls: unknown certificate authority`) → [certificates.md → Accepted client CA set](certificates.md#accepted-client-ca-set-mtls-cloud).

### Certificate filters

Cloud Namespace certificate filters are configured at the Namespace level and restrict which end-entity (leaf) certificates may authenticate, even when the issuing CA is in the accepted-client-ca set. Per the Cloud docs: "To limit access to specific end-entity certificates, create certificate filters. Each filter contains values for one or more of the following fields: commonName (CN), organization (O), organizationalUnit (OU), subjectAlternativeName (SAN)." "Corresponding fields in the client certificate must match every specified value in the filter."

Matching rules worth knowing when diagnosing a filter mismatch:

- Values are case-insensitive.
- Without wildcards, each value must match exactly.
- A single `*` wildcard may appear at the beginning or end of a value (but not both, and not alone).
- Maximum 25 filters per Namespace.

Inspect the DN fields on the client cert:

```bash
openssl x509 -in client.pem -noout -subject
# -subject prints the cert's Subject (CN, O, OU, etc.) — see certificates.md openssl recipes
```

Inspect / change filters with `tcld`:

```bash
# View current filters
tcld namespace certificate-filters export \
  --namespace <namespace_id> \
  --certificate-filter-file <path>
# Command:

# Clear all filters (allows any cert that chains to an accepted CA)
tcld namespace certificate-filters clear \
  --namespace <namespace_id>
# Command:

# Replace filters with a JSON file
tcld namespace certificate-filters import \
  --namespace <namespace_id> \
  --certificate-filter-file <path>
# Command:

# Add additional filters
tcld namespace certificate-filters add \
  --namespace <namespace_id> \
  --certificate-filter-file <path>
# Command:
```

Cloud UI path is documented alongside these commands.

Caution on clearing: "Using this command allows _any_ client certificate that chains up to a configured CA certificate to connect to the Namespace."

### mTLS does not use Cloud roles

After CA (+ optional filter) acceptance, the data plane grants full Namespace access for WorkflowService APIs. There is no User/Service Account principal with Read/Write/Admin RBAC for the cert.

Clean `openssl s_client` (`Verify return code: 0 (ok)`) + a `PERMISSION_DENIED` (or TLS-layer rejection) on the first data-plane call → check filters, Namespace name, or auth method — not `tcld user get`. Cloud RBAC applies to **API keys** (next section), not mTLS data-plane callers.

## Cloud role and permission model

Applies to **API keys** (and UI/SSO users / Service Accounts), not to mTLS data-plane callers.

Cloud access is governed on two axes — account-level roles (who can do account operations) and Namespace-level permissions (who can do data-plane operations in a given Namespace) — with important coupling via inheritance. Reference: `docs/cloud/manage-access/roles-and-permissions.mdx`.

### Account-level roles

The CLI `--account-role` flag on `tcld user invite` and `tcld user set-account-role` accepts:

> `[Admin Developer FinanceAdmin MetricsRead Owner Read]`

Concept docs use display names (Account Owner, Global Admin, Developer, Finance Admin, Read-Only, Metrics Read). Map CLI `Admin` ↔ Global Admin.

**Inheritance:** Account Owner and Global Admin automatically have Namespace Admin on every Namespace in the account. Developers get Namespace Admin on Namespaces they create (revocable).

### Namespace-level permissions

Namespace permissions are set via `--namespace-permission <ns>=<permission-type>` on `tcld user invite` and `tcld user set-namespace-permissions`. The enum is:

> Available namespace permissions: `Admin` | `Write` | `Read`.

The values are case-sensitive (the docs write them capitalized; the invite example uses `ns1=Admin --namespace-permission ns2=Write`).

What each permission grants is summarized in the concept table: Read observes activity; Write starts / signals / cancels / terminates / resets Workflows and polls Task Queues; Namespace Admin does all of that plus Namespace administration.

Also check **Service Account** ownership of the API key (`tcld service-account get`, Cloud UI). Keys inherit the owner's roles.

### Inviting and adjusting users with tcld

```bash
# Invite a user with account role + per-namespace permissions
tcld user invite \
  --user-email <user@example.com> \
  --account-role Developer \
  --namespace-permission <ns1>=Admin \
  --namespace-permission <ns2>=Write
# Command:
# --user-email (required, NOT --email):
# --account-role (required), enum Admin|Developer|FinanceAdmin|MetricsRead|Owner|Read:
# --namespace-permission (repeatable), format <ns>=<Admin|Write|Read>:

# Change a user's account role after the fact
tcld user set-account-role \
  --user-email <user@example.com> \
  --account-role Developer
# Command:

# Change a user's Namespace permissions
tcld user set-namespace-permissions \
  --user-email <user@example.com> \
  --namespace-permission <ns>=Write
# Command:

# Look up what a user has
tcld user get --user-email <user@example.com>
# Command:

# List users scoped to a Namespace
tcld user list --namespace <namespace_id>
# Command:
```

User groups follow a parallel shape but a different namespace-role syntax — `<namespaceid>-<role>` with `<role>` in `admin | read | write`, instead of the `<ns>=<Admin|Write|Read>` used on `tcld user`.  The user-group account-role enum is also broader than the `tcld user` one. If a triage turns up `PERMISSION_DENIED` for a principal that inherits its access from a group, reach for `tcld user-group get --group-id <id>` rather than `tcld user get`.

### Discriminating with a read-vs-write smoke test

If a user can do one operation but not another in the same session, the question is almost always which Namespace permission they hold (API keys / users / Service Accounts only):

- `temporal workflow list --limit 1 ...` — requires `Read` or higher (or Owner/Admin inheritance). Success implies the identity is authenticated and has at least `Read` on the Namespace.
- `temporal workflow start ...` or `temporal workflow signal ...` — requires `Write` or higher.
- `tcld namespace get --namespace <ns>` is control plane and needs Namespace **Read** (or Owner/Admin inheritance) — not Admin-only. A control-plane-only failure with data-plane access intact still points at account role / missing Namespace grant, not broken data-plane auth.

If the read smoke test returns data and the write smoke test returns `PERMISSION_DENIED`, the diagnosis is "identity authenticated, permission insufficient" rather than "broken auth."

## Quick routing

| Error text shape | Layer | Go to |
|---|---|---|
| gRPC `UNAUTHENTICATED` with API key | 4 | [API-key authentication](#api-key-authentication) |
| API key rejected on Namespace Endpoint (mTLS-only / dual-auth Namespace) | 4 | Try the API Regional Endpoint |
| gRPC `UNAUTHENTICATED` with mTLS | 3–4 boundary | First confirm TLS with `openssl s_client` per [certificates.md](certificates.md); if TLS is clean, this is a post-TLS rejection — see [mTLS authentication after TLS completes](#mtls-authentication-after-tls-completes) |
| gRPC `PERMISSION_DENIED` on data-plane (API key) | 4 | [Cloud role and permission model](#cloud-role-and-permission-model) |
| gRPC `PERMISSION_DENIED` on data-plane (mTLS, TLS clean) | 4 | [Certificate filters](#certificate-filters) / wrong Namespace / auth method — **not** Cloud RBAC |
| gRPC `PERMISSION_DENIED` on `tcld` control-plane call | 4 (control plane) | Account-level role — see [Account-level roles](#account-level-roles) |
| `remote error: tls: bad certificate` | 3–4 | [certificates.md → Accepted client CA set](certificates.md#accepted-client-ca-set-mtls-cloud) — rejected cert (untrusted CA or filter mismatch) |
| `remote error: tls: unknown certificate authority` | 3 | [certificates.md → Accepted client CA set](certificates.md#accepted-client-ca-set-mtls-cloud) |
| gRPC `UNAVAILABLE` | 2–3 | Not an auth code — peel the wrapped cause; see [connectivity.md](connectivity.md) and [certificates.md](certificates.md) |
| gRPC `RESOURCE_EXHAUSTED` | 4+ | Not an auth code — see [rate-limits.md](rate-limits.md) |
