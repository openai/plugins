# Certificates

Diagnose TLS and x509 failures against Temporal Cloud or a self-hosted frontend. This file covers layer 3 of the [diagnostic ladder](diagnostic-ladder.md).

Prerequisite: before reading this file, rule out layers 1 and 2 (DNS, TCP). TLS errors can masquerade as connectivity errors when a middlebox drops packets mid-handshake, so confirm TCP reachability first via [connectivity.md](connectivity.md#connection-refused). The reverse also happens: when a TLS handshake completes but the cert is invalid, the Go client emits cert-shaped errors that are firmly in layer 3.

**Ports referenced in this file:** SDK and CLI gRPC traffic to a Namespace (Cloud or self-hosted frontend) uses **7233**, for both mTLS and API-key Namespaces. The web UI uses **443**. All examples below assume 7233 unless stated.

**Flexible Auth (mTLS + API key on the same Namespace):** When a Namespace has both auth methods enabled concurrently, a TLS-layer failure on the mTLS leg can be masked by a successful API-key path (and vice versa). Before triaging, confirm which auth method the failing client is using. If the same client is configured for both, disable one at a time to isolate which leg is broken. The recipes in this file apply to the mTLS leg only; API-key auth failures live in [authentication.md](authentication.md).

Out of scope here:
- DNS / TCP / endpoint / firewall → [connectivity.md](connectivity.md) (layers 1-2)
- gRPC `UNAUTHENTICATED` after a successful TLS handshake → [authentication.md](authentication.md) (layer 4)
- API-key auth semantics (API-key connections still ride TLS, so TLS-level issues in this file apply — but the API-key authorization check itself is not a TLS issue) → [authentication.md](authentication.md)
- gRPC `RESOURCE_EXHAUSTED` → [rate-limits.md](rate-limits.md)

## Table of Contents

- [Error-string origin cheat sheet](#error-string-origin-cheat-sheet)
- [Handshake failure](#handshake-failure)
- [Expired or not-yet-valid](#expired-or-not-yet-valid)
- [Unknown authority](#unknown-authority)
- [Hostname mismatch](#hostname-mismatch)
- [Server name override](#server-name-override)
- [Key does not match cert](#key-does-not-match-cert)
- [Accepted client CA set (mTLS Cloud)](#accepted-client-ca-set-mtls-cloud)
  - [Certificate filters](#certificate-filters)
- [Certificate requirements (Cloud mTLS)](#certificate-requirements-cloud-mtls)
- [Rotation and expiry notifications](#rotation-and-expiry-notifications)
- [Private key handling](#private-key-handling)
- [openssl recipes](#openssl-recipes)
- [TLS / cert error reference](#tls--cert-error-reference)

## Error-string origin cheat sheet

Strings in this file come from the Go standard library (client side) or the TLS peer (alert descriptions). Every quoted string below is tagged with its source so you can tell a Go-local complaint from a peer-originated alert.

- **`x509: ...`** — emitted by Go's `crypto/x509` when the client rejects a peer cert locally. Source: `src/crypto/x509/verify.go`.
- **`tls: ...`** — emitted by Go's `crypto/tls` during the handshake (typically a local protocol-level error). Source: `src/crypto/tls/`.
- **`remote error: tls: <alert description>`** — a TLS alert received from the *peer*, formatted by Go. The alert description words (`handshake failure`, `bad certificate`, `unknown certificate authority`, `expired certificate`, `internal error`, etc.) come from `src/crypto/tls/alert.go`; the `remote error: tls: ` prefix is added by Go when it surfaces the peer's alert.
- **`Failed reaching server: last connection error`** — surfaced by the Temporal Cloud connection path; the troubleshooting guide identifies an expired TLS certificate as a common root cause.

If you have an error string that doesn't start with `x509:`, `tls:`, or `remote error: tls:`, it is probably not a TLS-layer error — re-check the layer above (connectivity.md) or below (authentication.md).

## Handshake failure

**Symptom shape:**
- Client side: `tls: handshake failure` or a gRPC `UNAVAILABLE` whose wrapped cause starts with `tls:` or `remote error: tls:`.
- Peer-alerted: `remote error: tls: handshake failure` (the word `handshake failure` is the TLS alert description emitted by the other side).

**What it means:** the two sides did not agree on protocol version, cipher, or client authentication. On its own, `handshake failure` is not specific — it is the generic TLS alert when the peer cannot continue. Use `openssl s_client` (see [openssl recipes](#openssl-recipes)) to get a more specific line such as `certificate has expired`, `unknown certificate authority`, or a hostname-mismatch error.

**First check:** reproduce the handshake from the same host that saw the failure:

```bash
openssl s_client -connect <host>:7233 -servername <host> </dev/null
# -connect host:port: who to connect to
# -servername name:  set the SNI server name
```

For mTLS, add `-cert` and `-key`:

```bash
openssl s_client -connect <host>:7233 \
  -servername <host> \
  -cert client.pem -key client.key \
  -showcerts </dev/null
# -cert file:       client cert, PEM assumed
# -key file:        client private key
# -showcerts:       show all server certs
```

(The same `openssl s_client -connect <endpoint> -showcerts -cert ... -key ...` form is used by the Temporal troubleshooting guide.)

Interpret by looking at the last few lines of output:

| Output line | Interpretation | Where to go |
|---|---|---|
| `Verify return code: 0 (ok)` and certificate info printed | TLS succeeded | Not a TLS problem. Move to [authentication.md](authentication.md). |
| `Verify return code: 10 (certificate has expired)` or `x509: certificate has expired or is not yet valid` on the client | Cert past validity on server or client chain | [Expired or not-yet-valid](#expired-or-not-yet-valid) |
| `Verify return code: 19 (self signed certificate in certificate chain)` or `Verify return code: 20/21` | Client doesn't trust the server chain | [Unknown authority](#unknown-authority) |
| `tlsv1 alert unknown ca` / `remote error: tls: unknown certificate authority` | Server rejected the client CA | [Accepted client CA set](#accepted-client-ca-set-mtls-cloud) |
| `tlsv1 alert bad certificate` / `remote error: tls: bad certificate` | Server rejected the client cert (cert-filter mismatch, malformed cert, or wrong cert presented) | [Accepted client CA set](#accepted-client-ca-set-mtls-cloud) and [certificate filters in `docs/cloud/certificates.mdx`](https://docs.temporal.io/cloud/certificates#manage-certificate-filters) |
| Handshake opens TCP but closes with no TLS alert bytes | Middlebox dropping / TLS-inspecting proxy | Back off to [connectivity.md → firewall and proxy](connectivity.md#firewall-and-proxy) |

## Expired or not-yet-valid

**Symptom shapes:**
- Go client: `x509: certificate has expired or is not yet valid: ` followed by detail
- Peer alert: `remote error: tls: expired certificate`
- Temporal Cloud: `Failed reaching server: last connection error` — the troubleshooting guide names an expired TLS certificate as a common root cause.
- Workers that were fine yesterday stopped connecting overnight with no deploy.

**What to check first — exact expiry times of each cert in play:**

```bash
# Local cert file
openssl x509 -enddate -noout -in client.pem
# -enddate: print notAfter field
# -noout:   no encoded output
# -in file: input file

# Both notBefore and notAfter
openssl x509 -dates -noout -in client.pem
# -dates: Both Before and After dates

# Server cert fetched from a live endpoint
openssl s_client -connect <host>:7233 -servername <host> </dev/null 2>/dev/null \
  | openssl x509 -enddate -noout
```

For the accepted-client-ca set on a Cloud Namespace, the troubleshooting guide lists expiry via `tcld namespace accepted-client-ca list` with `jq`:

```bash
tcld namespace accepted-client-ca list \
  --namespace <namespace_id>.<account_id> \
  | jq -r '.[0].notAfter'
# tcld namespace accepted-client-ca list:
# --namespace (-n) modifier:
# Recipe exactly as written in:
```

**Clock skew — the "not yet valid" variant:** the same Go error string covers both "expired" and "not yet valid" (`x509: certificate has expired or is not yet valid: `). If `date -u` on the client disagrees with a time authority by more than the cert's overlap window (common in containers with no NTP, on appliances with a dead RTC battery, or right after a host boot), a cert that is in fact valid will still fail verification. Verify with `date -u` before regenerating anything.

**Classification:**

- **End-entity (leaf) cert expired, CA still valid:** regenerate the leaf against the existing CA. See [openssl recipes → issue a new leaf with tcld](#issue-a-new-leaf-with-tcld).
- **CA cert expired (so all leaves under it fail):** regenerate CA + leaf, upload the new CA *alongside* the existing one before removing the old one, then distribute new leaves and restart clients. See [Rotation and expiry notifications](#rotation-and-expiry-notifications). The Cloud docs describe this as a "rollover process" that "enables your Namespace to serve both CA certificates for a period of time until traffic to your old CA certificate ceases."
- **Temporal Cloud server-side cert expired:** you don't manage the server side on Cloud. Open a support ticket per `docs/troubleshooting/last-connection-error.mdx`.
- **Self-hosted server cert expired:** rotate the frontend's server TLS cert on your deployment. No tcld involvement.

:::caution
An expired root CA certificate invalidates all downstream certificates, per `docs/cloud/get-started/certificates.mdx:31`.
:::

## Unknown authority

**Symptom shapes:**
- Go client: `x509: certificate signed by unknown authority`
- Go client (verify chain): `x509: no valid chains built` or `x509: failed to load system roots and no roots provided`
- Peer alert: `remote error: tls: unknown certificate authority`
- Peer alert: `remote error: tls: bad certificate`

**Two directions this error travels — check which side is complaining before you act:**

1. **Client does not trust server (client-side `x509: ...`).** The client cannot validate the server certificate against any root it knows about. One thing to check is whether the client's trust store is populated — minimal container images often ship without system CAs — and whether the client is being pointed at a non-Temporal endpoint (TLS-inspecting proxy). The Go client does not ship its own root bundle; it relies on the host's trust store or an explicit `--tls-ca-path` / `TEMPORAL_TLS_CA`.
2. **Server does not trust client (peer-alert `remote error: tls: unknown certificate authority`).** For mTLS, the Namespace's accepted-client-ca set does not contain the CA that signed the client cert. Fix in [Accepted client CA set](#accepted-client-ca-set-mtls-cloud).

**Verify locally that the client cert chains to the CA you think it chains to:**

```bash
openssl verify -CAfile ca.pem client.pem
# -CAfile file: Certificate Authority file
```

If intermediates exist, supply them via `-untrusted`:

```bash
openssl verify -CAfile root-ca.pem -untrusted intermediate.pem client.pem
# -untrusted file: untrusted certificates file
```

## Hostname mismatch

**Symptom shapes:**
- `x509: certificate is valid for <SAN list>, not <requested host>`
- `x509: certificate is not valid for any names, but wanted to match <host>`
- `x509: cannot validate certificate for <host>`
- Go client may also emit: `x509: certificate relies on legacy Common Name field, use SANs instead` when a server cert has no SAN and only a CN. Rare on modern clients: this string is from the deprecated `GODEBUG=x509ignoreCN=0` path, which Go 1.17 removed. Go 1.17+ rejects the cert with a hostname-mismatch error instead. Treat the legacy-CN string as a Go 1.15–1.16 era signal; if you see it on a current build, the client is pinned to an older Go runtime.

**What it means:** the hostname the client asked for does not match any Subject Alternative Name (or DNSName) on the server certificate the peer presented.

**First check:** which hostname is the client asking for?

```bash
# Inspect server cert SANs as actually served:
openssl s_client -connect <host>:7233 -servername <host> </dev/null 2>/dev/null \
  | openssl x509 -text -noout \
  | grep -A1 "Subject Alternative Name"
# -text: print certificate in text form
```

**Common cause on Temporal Cloud:** connecting by VPC-endpoint DNS name (PrivateLink) or GCP PSC IP, or by Regional Endpoint, without overriding the TLS server name. The TLS peer serves the Namespace's certificate, whose SAN is the Namespace Endpoint hostname — the VPC-endpoint hostname is not in it. Fix in the next section.

## Server name override

**Symptom:** TLS handshake fails with hostname-mismatch errors (see [Hostname mismatch](#hostname-mismatch) above) when connecting through a PrivateLink VPC endpoint, a GCP Private Service Connect IP, or a Cloud Regional Endpoint.

**What the Cloud docs say:**

- When a client uses a PrivateLink / PSC endpoint instead of the Namespace Endpoint DNS name, the docs instruct you to "Set TLS configuration to override the TLS server name (e.g., my-namespace.my-account.tmprl.cloud)."
- When a client uses a Regional Endpoint with mTLS, the docs say: "the Temporal Client must set the `server_name` property to `<namespace endpoint value>` in its request to the value of the Namespace endpoint. This tells the client to expect a different SNI header during the TLS handshake, since the request to the regional endpoint is redirected to the specific Namespace."
- Temporal recommends configuring private DNS instead, so the Namespace Endpoint hostname resolves to the VPC endpoint directly and no server-name override is needed.

**How to override on each client — verified forms only:**

`temporal` CLI flag (value: the Namespace Endpoint, e.g. `<namespace>.<account>.tmprl.cloud`):

```bash
temporal workflow list \
  --address vpce-0123456789abcdef-abc.us-east-1.vpce.amazonaws.com:7233 \
  --namespace <namespace>.<account> \
  --tls-cert-path client.pem --tls-key-path client.key \
  --tls-server-name <namespace>.<account>.tmprl.cloud
# --tls-server-name: Overrides the target TLS server name
# --tls-cert-path:   Path to x509 certificate
# --tls-key-path:    Path to private certificate key
```

`temporal` CLI env var equivalent:

```bash
export TEMPORAL_ADDRESS=vpce-0123456789abcdef-abc.us-east-1.vpce.amazonaws.com:7233
export TEMPORAL_TLS_CERT=/path/to/cert.pem
export TEMPORAL_TLS_KEY=/path/to/cert.key
export TEMPORAL_TLS_SERVER_NAME=<namespace>.<account>.tmprl.cloud
# TEMPORAL_TLS_SERVER_NAME: Override for target TLS server name
# TEMPORAL_TLS_CERT:        Path to x509 certificate
# TEMPORAL_TLS_KEY:         Path to private certificate key
# TEMPORAL_ADDRESS:         Host and port for the Temporal Frontend Service

temporal workflow list --namespace <namespace>.<account>
```

The exact form above — `TEMPORAL_ADDRESS=vpce-...:7233` paired with `TEMPORAL_TLS_SERVER_NAME=my-namespace.my-account.tmprl.cloud` — is written out in the Cloud connectivity guide.

`grpcurl` (useful as a SDK-independent probe) — exactly the form the Cloud docs give:

```bash
grpcurl \
  -servername <namespace>.<account>.tmprl.cloud \
  -cert path/to/cert.pem \
  -key path/to/cert.key \
  vpce-0123456789abcdef-abc.us-east-1.vpce.amazonaws.com:7233 \
  temporal.api.workflowservice.v1.WorkflowService/GetSystemInfo
# Recipe as written in:
```

**For SDK clients:** the SDK concept is the same — set the TLS `ServerName` (Go / Java / .NET / Python / TypeScript) to the Namespace Endpoint hostname. The exact property name varies by SDK; refer to each SDK's client-connection doc linked from `docs/cloud/certificates#configure-clients-to-use-client-certificates` and cross-check against `skill-temporal-developer`. This triage file deliberately does not spell SDK APIs out, to avoid drift.

## Key does not match cert

**Symptom shapes:**
- `tls: failed to find any PEM data in certificate input` (the file is empty, wrong format, or the wrong file)
- Go's `tls.LoadX509KeyPair` surfaces a keypair mismatch at client start. The precise string varies across Go versions, so don't pattern-match on it; the *shape* is an error at client dial saying the cert and key don't pair.

**Verify by comparing modulus hashes of the cert and the private key:**

```bash
# RSA
openssl x509 -modulus -noout -in client.pem | shasum -a 256
openssl rsa  -modulus -noout -in client.key | shasum -a 256
# -modulus: print the RSA key modulus
# The two digests must be identical.
```

If the modulus hashes disagree, the cert and key file are from different keypairs. Find the key that was generated alongside this cert — commonly in the same directory — or regenerate both together.

(For ECDSA keys, `-modulus` does not apply; compare public keys with `openssl pkey -in client.key -pubout` against `openssl x509 -in client.pem -pubkey -noout`.)

## Accepted client CA set (mTLS Cloud)

On Temporal Cloud, an mTLS Namespace authenticates a client by validating the client cert against the CA set configured on the Namespace. The server-side error when the CA is not trusted is `remote error: tls: unknown certificate authority`. When a CA *is* trusted but the end-entity cert fails other checks (certificate filter mismatch, malformed cert), the server sends `remote error: tls: bad certificate`.

### Certificate filters

Certificate filters are SAN/CN-based allow rules configured on the Namespace that further restrict which client certs are accepted, even when the signing CA is in the accepted set. A filter specifies allowed values for the leaf's Common Name, Subject Organization, Subject Organizational Unit, or SANs (DNS names, URIs, emails); a client cert that chains to a trusted CA but does not match any filter is rejected with `remote error: tls: bad certificate`.

Filters are the common cause of "the CA is trusted, the cert looks fine, but the handshake still fails." If you see `remote error: tls: bad certificate` and the local `openssl verify -CAfile ...` check passes, suspect a filter mismatch before regenerating certs.

```bash
# Inspect what filters (if any) are configured on the Namespace
tcld namespace certificate-filters export \
  --namespace <namespace_id>.<account_id>
# Reference:

# Inspect the SANs / CN / OU on the client cert that's failing
openssl x509 -in client.pem -noout -subject -ext subjectAltName
```

If the filter set is non-empty, the leaf cert's subject fields and SANs must match at least one filter entry. Either re-issue the leaf with subject/SAN values that match an existing filter, or update the filter set to allow the new cert.

**List what the Namespace currently accepts:**

```bash
tcld namespace accepted-client-ca list \
  --namespace <namespace_id>.<account_id>
# Command:
# --namespace:
```

**Add a new CA to the accepted set:**

`add` **appends** to the existing set without removing other CAs, so it is the safe verb for the upload-alongside step of a rollover.

```bash
tcld namespace accepted-client-ca add \
  --namespace <namespace_id>.<account_id> \
  --ca-certificate-file <path>
# Command:
# --ca-certificate-file:
```

**Remove a CA (by fingerprint, safer than by PEM):**

```bash
tcld namespace accepted-client-ca remove \
  --namespace <namespace_id>.<account_id> \
  --ca-certificate-fingerprint <fingerprint>
# Command:
# --ca-certificate-fingerprint (--fp):
```

**Set the whole bundle at once (zero-downtime rollover):**

The Cloud docs describe a concat-old-plus-new-then-set pattern for rolling over CA certs without dropping traffic:

```bash
# 1. Create a file with old + new CA PEM blocks concatenated.
# 2. Run:
tcld namespace accepted-client-ca set \
  --namespace <namespace_id>.<account_id> \
  --ca-certificate-file <path>
# Command and rollover procedure:
# Same procedure in:
# 3. Wait until all clients present leaves signed by the new CA (operator-confirmed; Cloud shows no drain signal).
# 4. Create a file with only the new CA and run the set command again.
```

:::caution
`set` **replaces the entire accepted-CA bundle** with exactly what you pass, and it does not prompt for confirmation. Passing only the new CA silently drops every other trusted CA and locks out any client still presenting a leaf under them. Use `add` to append a CA during a rollover; use `set` only with a deliberately concatenated old+new bundle. Trust-changing commands (`set`, `remove`, rotation) are high-consequence: run them with operator confirmation of the blast radius, not autonomously.
:::

**Verify locally before uploading** that the client cert chains to the CA you're about to upload:

```bash
openssl verify -CAfile new-ca.pem client.pem
# Expected: client.pem: OK
```

If this fails locally, it will fail at the peer too. Fix before touching the Namespace.

## Certificate requirements (Cloud mTLS)

The docs state hard requirements for any CA or leaf cert you upload to a Cloud Namespace. These are where subtle TLS rejections come from when a cert "looks fine" but the peer sends `remote error: tls: bad certificate` anyway. Quoting the requirements as listed at `docs/cloud/get-started/certificates.mdx:62-96`:

**CA certificates:**
- X.509v3.
- Each cert in a bundle is either a root or issued by another cert in the bundle.
- Each cert includes `CA: true`.
- Cannot be a well-known CA (DigiCert, Let's Encrypt, etc.) unless the user also specifies certificate filters.
- Signing algorithm must be RSA or ECDSA and must include SHA-256 or stronger. SHA-1 and MD5 cannot be used.
- Cannot be generated with a passphrase.
- Bundle ≤ 16 CA certs, ≤ 32 KB before base64 encoding.
- In a full end-entity → root chain, each certificate must have a unique Distinguished Name (DN comparison is case-insensitive).

**End-entity (leaf) certificates:**
- X.509v3.
- Basic constraints must include `CA: false`.
- Key usage must include Digital Signature.
- Signing algorithm: RSA or ECDSA with SHA-256 or stronger.

**Certificate Revocation Lists:** Temporal does not support or check CRLs (or OCSP); customers are expected to keep certificates up to date. Because there is no revocation list, plan for revocation by other means:

- **Short certificate lifetimes** are the primary control: a short-lived leaf bounds how long a stolen key is usable. Set leaves to expire before their issuing CA.
- **Removing a CA from the accepted set** (`tcld namespace accepted-client-ca remove`) is the hard kill switch. This rejects *all* leaves signed by that CA, so confirm the blast radius before running it.
- **Certificate filters** scope acceptance to specific leaf identities (CN/OU/Subject Organization/SAN); tightening or removing a filter cuts off specific certs without rotating the CA.
- There is **no per-leaf revocation**: to cut off a single leaf before it expires, you must rotate or remove its CA. Size leaf lifetimes accordingly.

**Algorithm choice when generating with tcld:** `tcld gen ca` defaults to ECDSA P-384; `--rsa-algorithm` (alias `--rsa`) switches to a 4096-bit RSA key pair.

The accepted set above (RSA or ECDSA, SHA-256+) is a floor, not a recommendation: Temporal does not mandate a specific key size or curve for customer CAs. Match key strength to certificate lifetime. RSA-2048 (~112-bit) is acceptable for short-lived certs today, but NIST (SP 800-131A Rev. 2) deprecates 112-bit strength after 2030, so a long-lived CA root that must stay trusted past then should use ECDSA (P-256/P-384) or RSA-3072 or larger (4096 preferred; the `--rsa` flag emits 4096). The tcld default, ECDSA P-384, is a good choice for most cases.

**Duration caps when generating with tcld:** `tcld gen ca` has a maximum duration of 1 year (`-d 1y`). You must set an end-entity cert to expire before its root CA.

## Rotation and expiry notifications

**Notifications.** Temporal Cloud sends email notifications before CA expiry. The notifications doc lists "Certificate Expiring in 15 days" as an admin notification sent to Global Administrators, Namespace Administrators, and Account Owners. The certificates guide states: "Temporal Cloud begins sending notifications 15 days before expiration."

**Rollover strategy.** The Cloud docs prescribe a zero-downtime rollover pattern: add the new CA alongside the existing one (`accepted-client-ca add`), wait until every client has rolled to leaves signed by the new CA, then remove the old CA. Cloud exposes no signal for when traffic has fully shifted, so treat this as operator-driven: confirm your worker fleet is on new-CA leaves before removing the old CA. The same shape applies whether you use the UI or `tcld`.

**Rotation command sequence (issue with tcld, upload with tcld):** the generated `*.key` files are secrets; see [Private key handling](#private-key-handling).

```bash
# Issue a new CA cert (if rotating CA). Default is ECDSA P-384.
tcld generate-certificates certificate-authority-certificate \
  --organization <org> \
  --validity-period 1y \
  --ca-certificate-file new-ca.pem \
  --ca-key-file new-ca.key
# Command (alias: tcld gen ca):
# --organization (--org):
# --validity-period (-d):
# --ca-certificate-file (--ca-cert):
# --ca-key-file (--ca-key):

# Issue a new end-entity (leaf) cert against a CA
tcld generate-certificates end-entity-certificate \
  --organization <org> \
  --validity-period 364d \
  --ca-certificate-file new-ca.pem \
  --ca-key-file new-ca.key \
  --certificate-file client.pem \
  --key-file client.key
# Command (alias: tcld gen leaf):
# --certificate-file (--cert):
# --key-file (--key):

# Upload concatenated old+new CA bundle to the Namespace, then (after drain) upload new-only bundle.
tcld namespace accepted-client-ca set \
  --namespace <namespace_id>.<account_id> \
  --ca-certificate-file <path-to-bundle>
# Procedure:
# --namespace:
```

**When the CA itself is already expired** (the rollover window was missed), a new CA must be uploaded before any client can reconnect. This is the "cert expired at 3 a.m." shape; see [recipes.md](recipes.md) for the full step-by-step.

## Private key handling

The recipes in this file generate private keys (`new-ca.key`, `client.key`). Treat them as secrets, and treat the CA private key as a root credential: it can mint client certificates the Namespace will accept, and there is no revocation backstop if it leaks (see [Certificate Revocation Lists](#certificate-requirements-cloud-mtls)).

- **Never print, echo, `cat`, or log private-key contents.** To check whether a key matches a cert, use the modulus/fingerprint comparisons in [Compare a keypair](#compare-a-keypair) and [Key does not match cert](#key-does-not-match-cert) — those expose no secret material.
- **The key is plaintext on disk.** Cloud requires CA keys to be generated without a passphrase, so the file itself is the secret. Restrict permissions (`chmod 600`), never commit it to source control (add `*.key` to `.gitignore`), and keep the long-term CA key in a secrets manager or offline storage.
- **Don't leave key material in working or shared directories.** Where a key should live long-term depends on the environment, so flag leftover key files to the operator to place in durable secret storage rather than guessing or deleting them.

:::caution
Generating or rotating keys locally is safe, but anything that changes a Namespace's trust (`accepted-client-ca set`/`remove`, rotation) or deletes key material is high-consequence: it can lock out every worker on the Namespace or destroy an unrecoverable CA key. Run those steps with operator confirmation, not autonomously.
:::

## openssl recipes

These are reference-card forms; each flag is cross-linked to the openssl usage output.

### Inspect a local cert

```bash
# Full text
openssl x509 -in cert.pem -noout -text
# -in / -noout / -text

# Subject and issuer
openssl x509 -in cert.pem -noout -subject -issuer
# -subject / -issuer

# Validity dates
openssl x509 -in cert.pem -noout -dates
# -dates: both Before and After

# Fingerprint (for tcld --ca-certificate-fingerprint)
openssl x509 -in cert.pem -noout -fingerprint
# -fingerprint
```

Note: LibreSSL (the `openssl` shipped with macOS as of LibreSSL 3.x) does not support the upstream OpenSSL `-ext <extname>` filter on `openssl x509`. To see SANs on LibreSSL, use `openssl x509 -text -noout` and read the `X509v3 Subject Alternative Name` section, or use grep as in [Hostname mismatch](#hostname-mismatch).

### Verify a chain

```bash
# Leaf + root
openssl verify -CAfile ca.pem client.pem

# Leaf + root + intermediate
openssl verify -CAfile root-ca.pem -untrusted intermediate.pem client.pem
# -CAfile / -untrusted
```

### Test a live endpoint

```bash
# Public-internet or mTLS Namespace, inspect the peer's cert chain
openssl s_client -connect <host>:7233 \
  -servername <host> \
  -showcerts </dev/null 2>/dev/null \
  | openssl x509 -text -noout

# Full mTLS handshake (what the Temporal troubleshooting guide uses)
openssl s_client -connect <namespace>.<account>.tmprl.cloud:7233 \
  -showcerts \
  -cert client.pem -key client.key \
  -tls1_2 </dev/null
# Recipe as written in the troubleshooting guide:
# -tls1_2: force TLSv1.2 (the troubleshooting guide uses this)
```

Reading the output:
- Server cert block(s) appear between `-----BEGIN CERTIFICATE-----` markers under `Certificate chain`.
- The last line normally prints `Verify return code: 0 (ok)` on success; a non-zero code is the OpenSSL verify error, e.g. `10 (certificate has expired)`.
- If the server sent a TLS alert rather than certs, you will see `tlsv1 alert <description>`; the alert description is one of the words listed in `src/crypto/tls/alert.go` (`handshake failure`, `bad certificate`, `unknown certificate authority`, `expired certificate`, etc.).

### Compare a keypair

```bash
openssl x509 -in cert.pem -modulus -noout | shasum -a 256
openssl rsa  -in key.pem  -modulus -noout | shasum -a 256
# Digests must match for the files to be from the same keypair.
```

### Self-signed cert workflow (self-hosted or temporary)

The troubleshooting guide suggests using `temporal namespace describe` with explicit TLS flags when working with self-signed certs:

```bash
temporal namespace describe \
  --namespace <namespace_id>.<account_id> \
  --address <namespace_grpc_endpoint> \
  --tls-cert-path <path-to-mTLS-pem-file> \
  --tls-key-path <path-to-mTLS-key-file>
# Recipe as written in:
```

### Issue a new leaf with tcld

```bash
tcld gen leaf \
  --org <org> \
  -d 364d \
  --ca-cert ca.pem --ca-key ca.key \
  --cert client.pem --key client.key
# tcld gen leaf = tcld generate-certificates end-entity-certificate
# Aliases listed in:
# Example as written in:
```

## TLS / cert error reference

Each row is tagged with the string's origin. When an error doesn't fit any row here, re-read [Error-string origin cheat sheet](#error-string-origin-cheat-sheet) to decide whether it is really a TLS-layer error at all.

| Error text (exact, as emitted) | Origin | One thing to check |
|---|---|---|
| `x509: certificate has expired or is not yet valid: <detail>` | Go x509 | [Expired or not-yet-valid](#expired-or-not-yet-valid); also check `date -u` for clock skew |
| `x509: certificate signed by unknown authority` | Go x509 | Client doesn't trust peer's root. [Unknown authority](#unknown-authority) |
| `x509: certificate is valid for <SAN>, not <host>` | Go x509 | [Server name override](#server-name-override) |
| `x509: cannot validate certificate for <host>` | Go x509 | [Hostname mismatch](#hostname-mismatch) |
| `x509: no valid chains built` | Go x509 | Chain does not reach a trusted root; verify with `openssl verify -CAfile ...` |
| `x509: a root or intermediate certificate is not authorized to sign for this name: <detail>` | Go x509 | Name-constraints extension rejects the leaf |
| `x509: certificate is not authorized to sign other certificates` | Go x509 | Cert with `CA: false` is being used as an issuer |
| `x509: failed to load system roots and no roots provided` | Go x509 | Minimal container missing `ca-certificates`; or `TEMPORAL_TLS_CA` / `--tls-ca-path` not set |
| `x509: certificate relies on legacy Common Name field, use SANs instead` | Go x509 (Go 1.15–1.16 era) | Peer cert has no SAN, only CN; re-issue with SANs. Go 1.17+ emits hostname-mismatch instead; if you see this on current Go, the client is pinned to an older runtime |
| `tls: handshake failure` | Go tls (local) | See [Handshake failure](#handshake-failure) and reproduce with `openssl s_client` |
| `remote error: tls: handshake failure` | peer alert | Peer rejected the handshake; reproduce with `openssl s_client` for the alert description |
| `remote error: tls: bad certificate` | peer alert | [Accepted client CA set](#accepted-client-ca-set-mtls-cloud); also check certificate filters |
| `remote error: tls: unknown certificate authority` | peer alert | [Accepted client CA set](#accepted-client-ca-set-mtls-cloud) |
| `remote error: tls: expired certificate` | peer alert | [Expired or not-yet-valid](#expired-or-not-yet-valid) |
| `remote error: tls: internal error` | peer alert | Peer-side failure, not a cert problem on this end; retry and, if persistent on Cloud, open a support ticket |
| `Failed reaching server: last connection error` | Temporal client diagnostic | Often an expired TLS cert per the troubleshooting guide; run the expiry checks in [Expired or not-yet-valid](#expired-or-not-yet-valid) |

For TLS errors that only appear after the handshake (gRPC `UNAUTHENTICATED`, `PERMISSION_DENIED`), jump to [authentication.md](authentication.md). For `UNAVAILABLE` without a TLS-layer cause, back off to [connectivity.md](connectivity.md).
