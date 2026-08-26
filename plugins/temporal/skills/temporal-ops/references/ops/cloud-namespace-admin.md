# Cloud Namespace Administration via tcld

Quick-reference for Cloud namespace lifecycle operations using `tcld namespace`.

Alias: `n`

---

## Identity formats

| Concept | Format | Example |
|---|---|---|
| Namespace Name | `<namespace_name>` (2-39 chars, lowercase, letters/numbers/hyphens, must start with letter, end with letter or number) | `accounting-production` |
| Account ID | `<account_suffix>` (5+ chars) | `123de` |
| Namespace ID | `<namespace_name>.<account_suffix>` | `accounting-production.123de` |
| Namespace endpoint | `<ns>.<acct>.tmprl.cloud:7233` | `accounting-production.123de.tmprl.cloud:7233` |
| Regional endpoint | `<region>.<cloud_provider>.api.temporal.io:7233` | `us-east-1.aws.api.temporal.io:7233` |

All `--namespace` / `-n` flags accept the **Namespace ID** (full form), not the short Namespace Name.

If `--namespace` is omitted, the environment variable `$TEMPORAL_CLOUD_NAMESPACE` is used.

---

## Limits

- Default account namespace limit: 10 (auto-increases as you create namespaces; for large-scale needs open a support ticket)
- Retention range: 1-90 days
- Max tags per namespace: 10
- Tag key/value length: 1-63 characters
- Soft limit of 1000 unique tag keys per account
- Max caller Namespaces per Nexus Endpoint Access Policy: 1,000 (support ticket to raise)
- Max Nexus Endpoints per account: 100 (support ticket to raise)

---

## tcld namespace create

Alias: `c`

```bash
tcld namespace create \
    --namespace <namespace_id> \
    --region <region> \
    --auth-method api_key
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | Becomes part of the Namespace ID |
| `--region` | `--re` | Yes | One for standard, two for HA. See Regions docs |
| `--auth-method` | | No | `mtls` (default), `api_key`, `restricted`, or `api_key_or_mtls` |
| `--ca-certificate` | `-c` | Conditional | Required if `--auth-method mtls` and no `--ca-certificate-file` |
| `--ca-certificate-file` | `--cf` | Conditional | Path to PEM file |
| `--certificate-filter-file` | `--cff` | No | JSON file defining cert filters |
| `--certificate-filter-input` | `--cfi` | No | JSON string defining cert filters |
| `--cloud-provider` | `--cp` | No | `aws` (default) or `gcp` |
| `--connectivity-rule-ids` | `--ids` | No | Can be specified multiple times |
| `--enable-delete-protection` | `--edp` | No | Default `false` |
| `--endpoint` | `-e` | No | Codec server endpoint (must be HTTPS) |
| `--include-credentials` | `--ic` | No | Include cross-origin credentials for codec server. Default `false` |
| `--pass-access-token` | `--pat` | No | Pass user access token to codec server. Default `false` |
| `--request-id` | `-r` | No | Async operation request ID |
| `--retention-days` | `--rd` | No | Default `30` |
| `--search-attribute` | `--sa` | No | `name=type` format; can repeat. Types: `Bool`, `Datetime`, `Double`, `Int`, `Keyword`, `Text` |
| `--tag` | `--t` | No | `key=value` format; can repeat |
| `--user-namespace-permission` | `-p` | No | `email=permission` format; `Admin`, `Write`, `Read` |

Example with HA (two regions), tags, and search attributes:

```bash
tcld namespace create \
    --namespace my-namespace.a1b2c \
    --region us-east-1 \
    --region us-west-2 \
    --auth-method api_key \
    --retention-days 30 \
    --search-attribute "customer_id=Int" \
    --tag "env=production" \
    --user-namespace-permission "user@example.com=Admin"
```

---

## tcld namespace get

Alias: `g`

```bash
tcld namespace get \
    --namespace <namespace_id>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | No | Falls back to `$TEMPORAL_CLOUD_NAMESPACE` |

Output is JSON by default (no `--format` flag exists).

---

## tcld namespace list

Alias: `l`

```bash
tcld namespace list
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--page-size` | | No | Namespaces per page; must be >0 and ≤ max page size |
| `--page-token` | | No | Page token from a previous response |

Returns JSON with a `namespaces` array and `nextPageToken`.

---

## tcld namespace delete

Alias: `d`

```bash
tcld namespace delete \
    --namespace <namespace_id>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | ETag; if omitted uses latest |

Deletion is permanent. All Workflow Executions and Task Queues are removed immediately. Closed Workflow Histories remain until their retention period expires.

There is no undo. Never run it autonomously. Before proposing it, report what is
in the Namespace —
`temporal workflow count --query 'ExecutionStatus="Running"'` against that
Namespace — and quote the full Namespace ID (`<namespace_name>.<account_suffix>`)
back to the user for confirmation, since a bare name can match a Namespace in a
different account than the one they mean. If the intent is to stop work rather
than discard the Namespace, that is a Workflow-level or capacity-level change,
not a delete.

If the delete is refused, the Namespace has delete protection enabled (below).
Treat that as a deliberate decision by whoever provisioned it: report the block
and stop. Do not disable protection and retry unless the user explicitly asks for
that, as a separate step.

### Delete protection

Enable via `--enable-delete-protection` / `--edp` at create time.

Toggle on an existing namespace (`lifecycle`, alias `lc`):

```bash
tcld namespace lifecycle set \
    --namespace <namespace_id> \
    --enable-delete-protection <Boolean>
```

Read the current delete-protection state:

```bash
tcld namespace lifecycle get \
    --namespace <namespace_id>
```

---

## tcld namespace add-region

Upgrades a namespace to support High Availability by adding a replica region.

```bash
tcld namespace add-region \
    --namespace <namespace_id> \
    --region <replica_region_name>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--region` | `--re` | Yes | Region name, e.g. `us-east-1` |
| `--cloud-provider` | | No | `aws` (default) or `gcp` |
| `--request-id` | `-r` | No | |

Temporal Cloud sends an email alert once the Namespace is ready.

---

## tcld namespace delete-region

Removes a replica region, disabling HA. Imposes a mandatory 7-day waiting period before re-enabling HA in the same location.

```bash
tcld namespace delete-region \
    --namespace <namespace_id> \
    --region <region_name>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--region` | `--re` | Yes | Region to remove |
| `--cloud-provider` | | No | `aws` (default) or `gcp` |
| `--request-id` | `-r` | No | |

The 7-day wait is what makes this hard to walk back: the Namespace runs
single-region for a week with no failover target, so a removal done to "clean up"
a replica cannot be reversed if the primary degrades in the meantime. Confirm
with the user that they intend to give up HA for at least that long, and check
which region is currently active first — removing the replica is a different
operation from failing back to it.

---

## tcld namespace failover

Switches a namespace from its primary region to a replica region (requires HA).

```bash
tcld namespace failover \
    --namespace <namespace_id> \
    --region <target_region>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--region` | `--re` | Yes | Region to fail over TO |
| `--cloud-provider` | | No | `aws` (default) or `gcp` |
| `--request-id` | `-r` | No | |

This moves production traffic and is not a diagnostic step — never trigger one to
test whether failover works, and never trigger one while diagnosing a symptom that
has not been traced to the active region. Confirm the target with the user, and
note that `--region` names the region being failed over **to**, not away from.
Once the request returns an operation ID the failover is guaranteed to proceed and
cannot be called back; clients may see a brief window of retryable errors during
handover. After a user-triggered failover Temporal does **not** fail back
automatically. See [../triage/ha-failover.md](../triage/ha-failover.md).

---

## tcld namespace retention

Alias: `r`

### retention get

Alias: `g`

```bash
tcld namespace retention get \
    --namespace <namespace_id>
```

### retention set

Alias: `s`

```bash
tcld namespace retention set \
    --namespace <namespace_id> \
    --retention-days <days>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--retention-days` | `--rd` | Yes | Range: 1-90 days |

Lowering retention is a data deletion, not a settings change: closed Workflow
Histories that fall outside the new window stop being retained and cannot be
recovered by setting the value back. Read the current value with `retention get`
and confirm the new number with the user before proposing it; the deletion does not
appear anywhere in the command's own output. Raising retention is safe but does not
resurrect anything already aged out.

---

## tcld namespace auth-method

Alias: `am`

Gets or sets the authentication method for an existing namespace. Changing the method can break existing client connections; tcld prompts for confirmation on disruptive changes.

### auth-method get

```bash
tcld namespace auth-method get \
    --namespace <namespace_id>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |

### auth-method set

```bash
tcld namespace auth-method set \
    --namespace <namespace_id> \
    --auth-method <method>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--auth-method` | `--am` | Yes | One of `restricted`, `mtls`, `api_key`, `api_key_or_mtls` |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | ETag; latest if omitted |

---

## tcld namespace export (Workflow History Exports)

Workflow History Export sinks are managed with `tcld namespace export` (alias `es`), under two provider subgroups: `s3` (AWS) and `gcs` (GCP).

Both subgroups expose the same subcommands:

| Subcommand | Alias | Purpose |
|---|---|---|
| `create` | `c` | Create a sink (created enabled) |
| `validate` | `v` | Validate sink config without creating it |
| `update` | `u` | Update sink fields or toggle enabled |
| `get` | `g` | Get a sink by name |
| `delete` | `d` | Delete a sink by name |
| `list` | `l` | List sinks |

### S3 create/validate flags

| Flag | Alias | Required |
|---|---|---|
| `--sink-name` | | Yes |
| `--role-arn` | | Yes |
| `--s3-bucket-name` | | Yes |
| `--kms-arn` | | No |
| `--region` | `--re` | No |

### GCS create/validate flags

| Flag | Alias | Required |
|---|---|---|
| `--sink-name` | | Yes |
| `--service-account-email` | | Yes |
| `--gcs-bucket` | | Yes |

`update` additionally takes `--enabled` (toggle `true`/`false`) and `--resource-version` / `-v`; provider flags are optional on update.

`get`, `delete`, and `list` are shared across both subgroups. `get` and `delete` identify the sink with `--sink-name` (`delete` also accepts `--resource-version` / `-v`); `list` accepts `--page-size` and `--page-token`.

---

## tcld namespace update-codec-server

Alias: `ucs`

```bash
tcld namespace update-codec-server \
    --namespace <namespace_id> \
    --endpoint <https_url>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--endpoint` | `-e` | Yes | Must be HTTPS |
| `--pass-access-token` | `--pat` | No | Default `false` |
| `--include-credentials` | `--ic` | No | Default `false` |

---

## tcld namespace update-high-availability

Alias: `uha`

```bash
tcld namespace update-high-availability \
    --namespace <namespace_id> \
    --disable-auto-failover=true
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--disable-auto-failover` | | No | `true` or `false` (default). Use `--disable-auto-failover=false` to (re-)enable Temporal-managed failover. |

---

## tcld namespace tags

Alias: `t`

### tags upsert

Add new tags or update existing tag values. Alias: `u`

```bash
tcld namespace tags upsert \
    --namespace <namespace_id> \
    --tag "key1=value1" \
    --tag "key2=updated"
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--tag` | `--t` | Yes | `key=value` format; repeatable |
| `--request-id` | `-r` | No | |

### tags remove

Remove tags by key. Alias: `rm`

```bash
tcld namespace tags remove \
    --namespace <namespace_id> \
    --tag-key "key1" \
    --tag-key "key2"
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | Yes | |
| `--tag-key` | `--tk` | Yes | Key string; repeatable |
| `--request-id` | `-r` | No | |

### Tag constraints

- Allowed characters: lowercase `a-z`, `0-9`, `.`, `_`, `-`, `@`
- Keys must be unique per namespace
- Only Account Admins and Account Owners can create/edit tags

---

## tcld namespace set-connectivity-rules

Alias: `scrs`

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `n` | Yes | |
| `--connectivity-rule-ids` | `ids` | No | Repeatable. `--ids id1 --ids id2` |
| `--remove-all` | | No | Acknowledges removal of all rules, enabling connectivity from any source |

---

## tcld namespace search-attributes

Alias: `sa`

### search-attributes add

Alias: `a`

```bash
tcld namespace search-attributes add \
    --namespace <namespace_id> \
    --search-attribute "YourSearchAttribute1=Text" \
    --search-attribute "YourSearchAttribute2=Double"
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | No | Falls back to `$TEMPORAL_CLOUD_NAMESPACE` |
| `--search-attribute` | `--sa` | Yes | `name=type` format; repeatable. Types: `Bool`, `Datetime`, `Double`, `Int`, `Keyword`, `Text` |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | |

To delete a search attribute, contact Support at support.temporal.io.

### search-attributes rename

```bash
tcld namespace search-attributes rename \
    --namespace <namespace_id> \
    --existing-name <old_name> \
    --new-name <new_name>
```

| Flag | Alias | Required | Notes |
|---|---|---|---|
| `--namespace` | `-n` | No | |
| `--existing-name` | `--en` | Yes | |
| `--new-name` | `--nn` | Yes | |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | |

---

## tcld namespace accepted-client-ca

Manages client CA certificates used to verify mTLS connections. Alias: `ca`

| Subcommand | Alias | Purpose |
|---|---|---|
| `add` | `a` | Add CA certs |
| `list` | `l` | List current CA certs |
| `set` | `s` | Replace all CA certs (used for rollover) |
| `remove` | `r` | Remove specific CA certs |

All subcommands accept `--namespace` / `-n`, `--request-id` / `-r`, `--resource-version` / `-v`.

Certificate can be supplied as:
- `--ca-certificate` / `-c` (base64-encoded string)
- `--ca-certificate-file` / `-f` (path to PEM file)

If both are specified, `--ca-certificate` takes precedence.

The `remove` subcommand additionally supports `--ca-certificate-fingerprint` / `--fp` for removal by fingerprint.

### CA certificate rollover procedure

1. Create a single PEM file with both old and new CA certificate blocks concatenated
2. Run `tcld namespace accepted-client-ca set --ca-certificate-file <path>`
3. Monitor traffic until old cert usage ceases
4. Run `set` again with only the new certificate

Do NOT use a CA certificate signed with SHA-1 -- such signatures are rejected.

`set` and `remove` both change who can connect, and the failure is fleet-wide
rather than gradual: every client presenting a leaf that chained only to a dropped
CA fails its next handshake, and Workers fail closed with a TLS error rather than
degrading. `set` is the sharper of the two because it replaces the entire bundle —
a PEM that omits a CA still in use silently revokes it. Run `list` first, confirm
which CAs are live, and prefer `add` when the goal is to introduce a new CA.
Reserve `set` for steps 2 and 4 of the rollover above, and do not run step 4 until
step 3 has actually shown old-cert traffic stop. Recovery means re-uploading the
dropped CA, so keep the PEM until the rollover is confirmed complete.

---

## tcld namespace certificate-filters

Manages certificate filters that authorize client certificates based on DN fields. Alias: `cf`

| Subcommand | Alias | Purpose |
|---|---|---|
| `add` | `a` | Add certificate filters |
| `import` | `imp` | Set (replace all) certificate filters |
| `export` | `exp` | Export current filters to file |
| `clear` | `c` | Clear all filters (allows any client cert that chains to a configured CA) |

Filter fields (at least one required): `commonName`, `organization`, `organizationalUnit`, `subjectAlternativeName`

Filter input via `--certificate-filter-file` / `-f` or `--certificate-filter-input` / `-i`. Cannot specify both.

JSON format: `{ "filters": [ { "commonName": "test1" } ] }`

Two of these subcommands change access, in opposite directions, and both are worth
proposing rather than running. `import` replaces the whole filter set rather than
appending to it, so it locks out every identity whose cert matched only a filter
the new file omits — the same fleet-wide shape as `accepted-client-ca set`, and the
reason to `export` to a file first and edit that. `clear` fails the other way: with
no filters, **any** client cert that chains to a configured CA is accepted
, so it silently widens access
instead of removing it. Neither direction is what "clear the filters" sounds like;
state which one you mean when you propose it.

---

## tcld nexus endpoint allowed-namespace

Manages a Nexus Endpoint's Access Policy — the allowlist of caller Namespaces
permitted to use the Endpoint at runtime. Cloud-only: self-hosted authorization
goes through a custom Authorizer plugin instead. For Endpoint CRUD itself, see
[self-hosted-admin.md § Nexus Endpoint Commands](self-hosted-admin.md#nexus-endpoint-commands),
which maps each `temporal operator nexus` verb to its `tcld nexus` equivalent.

| Subcommand | Purpose |
|---|---|
| `list` | Show the current allowlist |
| `add` | Add caller Namespaces; entries already present are ignored |
| `remove` | Remove caller Namespaces; entries not present are ignored |
| `set` | Replace the entire allowlist |

All subcommands take `--name` / `-n` (the Endpoint) and, except `list`,
`--namespace` / `-ns`, which is repeatable:

```bash
tcld nexus endpoint allowed-namespace add \
    --name <endpoint-name> \
    --namespace <caller-ns-1> \
    --namespace <caller-ns-2>
```

**No callers are allowed by default**, not even from the Endpoint's own target
Namespace. The allowlist is empty at create time unless seeded with
`--allow-namespace` (singular, a repeatable flag on `tcld nexus endpoint create`,
not a subcommand).

`set` replaces the full list, so any entry you don't pass is dropped — revoking
those callers at their next Nexus Operation. Never run it on your own initiative.
Run `list` first, name the exact entries it would drop, and ask the user directly;
run it only once they have approved, and only against that Endpoint. Prefer `add`
when the goal is to grant. Terraform manages the
same field as `allowed_caller_namespaces`, so a `set` against a
Terraform-provisioned Endpoint will be reverted on the next apply — see
[cloud-terraform.md](cloud-terraform.md).

---

## Endpoint and authentication summary

| Auth method | Endpoint type | Format |
|---|---|---|
| API key or mTLS | Namespace endpoint (recommended) | `<ns>.<acct>.tmprl.cloud:7233` |
| API key or mTLS | Regional endpoint | `<region>.<cloud_provider>.api.temporal.io:7233` |

- Namespace endpoints auto-route during HA failover -- Workers and Clients do not need endpoint changes
- When using mTLS with a regional endpoint, set `server_name` to the Namespace endpoint value
- Web UI URL: `https://cloud.temporal.io/namespaces/<namespace_id>`

---

## Access and permissions

- Creating a namespace requires Developer, Account Owner, or Global Admin account-level role
- The creator is automatically granted Namespace Admin permission
- Deleting a namespace requires Namespace Admin permission
- Tags: only Account Admins and Account Owners can create/edit

---

## Common anti-patterns

| Wrong | Right | Why |
|---|---|---|
| `--namespace my-ns` | `--namespace my-ns.a1b2c` | Namespace ID requires account suffix |
| `tcld namespace get --format json` | `tcld namespace get` | No `--format` flag; output is JSON by default |
| `tcld namespace search-attributes create` | `tcld namespace search-attributes add` | Subcommand is `add`, not `create` |
| `tcld namespace update --retention-days 30` | `tcld namespace retention set --retention-days 30` | Retention is its own subcommand tree |
| Short-name endpoint `my-ns:7233` | `my-ns.a1b2c.tmprl.cloud:7233` | Cloud requires full Namespace ID in endpoint |
