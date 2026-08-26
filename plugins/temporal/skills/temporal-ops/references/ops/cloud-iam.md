# Cloud IAM Reference

Quick-reference for Temporal Cloud identity and access management via `tcld`.
Covers API keys, users, user groups, service accounts, account operations, roles, and namespace permissions.

> For authentication failures during workflow execution, see the triage ladder in `../triage/authentication.md`.

---

## API Key Lifecycle (`tcld apikey`)

Alias: `ak`

### Create

```bash
tcld apikey create --name <name> \
    --description "<description>" \
    --duration <duration>        # e.g. 24h; ignored if --expiry set; required unless --expiry
    # --expiry <RFC3339>         # e.g. '2023-11-28T09:23:24-08:00'
    # --request-id <request_id>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--name` | `-n` | Yes | Display name of the API key |
| `--description` | `-desc` | No | |
| `--duration` | `-d` | Conditional | Duration from now until expiry. Ignored if `--expiry` is set. Required when `--expiry` is omitted; must be positive (no `0s` default) |
| `--expiry` | `-e` | Conditional | Absolute expiry timestamp (RFC3339). Required when `--duration` is omitted |
| `--request-id` | `-r` | No | Server assigns one if not set |

To create an API key for a **Service Account**, add `--service-account-id <id>`:

```bash
tcld apikey create \
    --name <name> \
    --description "<description>" \
    --duration <duration> \
    --service-account-id <service-account-id>
```

### Get

```bash
tcld apikey get --id <apikey_id>
```

| Flag | Alias | Required |
|------|-------|----------|
| `--id` | `-i` | Yes |

### List

```bash
tcld apikey list
```

Alias: `l`

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--owner-id` | `-oid` | No | Filter API keys by owner ID |
| `--owner-type` | `-ot` | No | Filter by owner type: `user` \| `service-account` |

### Delete

```bash
tcld apikey delete --id <apikey_id>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--id` | `-i` | Yes | |
| `--resource-version` | `-v` | No | ETag; uses latest if not set |
| `--request-id` | `-r` | No | Server assigns if not set |

Deleting a key immediately breaks every Worker, script, and CI job still
presenting it, and the key cannot be restored. Identify what is using the key
before proposing the delete, and confirm with the user rather than deleting
autonomously. During a rotation, prefer `disable` — it produces the same
`UNAUTHENTICATED` failure for callers but can be reversed with `enable` if you
disabled the wrong key. Delete only once the replacement is verified in use.

### Disable

```bash
tcld apikey disable --id <apikey_id>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--id` | `-i` | Yes | |
| `--resource-version` | `-v` | No | ETag; uses latest if not set |
| `--request-id` | `-r` | No | Server assigns if not set |

### Enable

```bash
tcld apikey enable --id <apikey_id>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--id` | `-i` | Yes | |
| `--resource-version` | `-v` | No | ETag; uses latest if not set |
| `--request-id` | `-r` | No | Server assigns if not set |

### Key Rotation Procedure

1. Create a new key (you may reuse key names).
2. Verify both original and new key function properly.
3. Switch clients to load the new key.
4. Delete the old key after it is no longer in use.

### API Key Limits

- Up to **10** non-expired keys per user.
- Up to **20** non-expired keys per Service Account.
- Maximum expiration time: **2 years**.

---

## API Key Connectivity Setup

To authenticate SDK or CLI connections to Temporal Cloud using an API key:

### Environment variable approach (recommended)

```bash
export TEMPORAL_API_KEY=<key-secret>
temporal workflow list \
    --address <namespace>.<account_id>.tmprl.cloud:7233 \
    --namespace <namespace>.<account_id>
```

### tcld authentication

Pass the key with `--api-key` or set `TEMPORAL_CLOUD_API_KEY` (tcld source/README).
Public docs sometimes say `TEMPORAL_API_KEY` for tcld; that env var is for Temporal CLI/SDKs, not tcld.

```bash
tcld --api-key <key-secret> apikey list
# or
export TEMPORAL_CLOUD_API_KEY=<key-secret>
tcld apikey list
```

### Namespace gRPC endpoint format

Recommended Namespace Endpoint (Temporal CLI, SDKs, Workers):

```
<namespace>.<account_id>.tmprl.cloud:7233
```

Regional endpoint (`<region>.<cloud_provider>.api.temporal.io:7233`) is an alternate for advanced HA routing, not the default API-key CLI address.

---

## User Management (`tcld user`)

Alias: `u`

### Invite

```bash
tcld user invite \
    --user-email <email> \
    --account-role <role> \
    --namespace-permission <namespace>=<permission>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--user-email` | `-e` | Yes | Can be supplied multiple times |
| `--account-role` | `--ar` | Yes | Case-insensitive: `Admin` \| `Developer` \| `Read` \| `Owner` \| `FinanceAdmin` \| `MetricsRead` |
| `--namespace-permission` | `-p` | No | Format: `namespace=permission-type`. Can be repeated. Permissions: `Admin` \| `Write` \| `Read` |
| `--request-id` | `-r` | No | |

Example with multiple namespace permissions:
```bash
tcld user invite \
    --user-email <test@example.com> \
    --account-role developer \
    --namespace-permission ns1=Admin \
    --namespace-permission ns2=Write \
    --request-id <123456>
```

### Get

```bash
tcld user get --user-email <email>
# or
tcld user get --user-id <user-id>
```

Must set either `--user-email` or `--user-id`.

### List

```bash
tcld user list
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--namespace` | `-n` | No | Filter: users with permissions to this namespace |
| `--page-token` | `-p` | No | Pagination token |
| `--page-size` | `-s` | No | Defaults to 10 |

### Delete

```bash
tcld user delete --user-email <email>
# or
tcld user delete --user-id <user-id>
```

Must set either `--user-email` or `--user-id`.

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--user-email` | | Conditional | |
| `--user-id` | | Conditional | |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | ETag; uses latest if not set |

Removes the user's access to the account and every Namespace they held
permissions on. Confirm the identity with the user before running — `--user-email`
is easy to mistype into a valid address belonging to someone else, so prefer
`tcld user list` to resolve the exact `--user-id` first and propose the delete
against that. To reduce a user's access rather than remove them, update their
account role or Namespace permissions instead.

### Resend Invite

```bash
tcld user resend-invite --user-email <email>
# or
tcld user resend-invite --user-id <user-id>
```

Alias: `ri`

Must set either `--user-email` or `--user-id`.

### Set Account Role

```bash
tcld user set-account-role --user-email <email> --account-role <role>
# or
tcld user set-account-role --user-id <user-id> --account-role <role>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--account-role` | `-ar` | Yes | Case-insensitive: `Admin` \| `Developer` \| `Read` \| `Owner` \| `FinanceAdmin` \| `MetricsRead` |
| `--user-email` | `-e` | Conditional | |
| `--user-id` | `--id` | Conditional | |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | ETag |

### Set Namespace Permissions

```bash
tcld user set-namespace-permissions \
    --user-email <email> \
    --namespace-permission <namespace>=<permission>
```

Alias: `snp`

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--user-email` | | Conditional | |
| `--user-id` | | Conditional | |
| `--namespace-permission` | `-p` | No | Format: `namespace=permission-type`. Can be repeated. Permissions: `Admin` \| `Write` \| `Read`. Empty removes all namespace permissions |
| `--request-id` | `-r` | No | |
| `--resource-version` | `-v` | No | ETag |

---

## Roles and Permissions

### Account-Level Roles

| Role (tcld value) | Notes |
|--------------------|-------|
| `admin` | Global Administrator |
| `developer` | |
| `read` | Read-only |
| `owner` | Account Owner |
| `financeadmin` | Finance Admin |
| `metricsread` | Metrics read access |
| `none` | User-group only; removes account-level role |

Account-role values are case-insensitive in `tcld user` commands; canonical forms are
`Admin`, `Developer`, `Read`, `Owner`, `FinanceAdmin`, `MetricsRead`.
`tcld user invite` and `tcld user set-account-role` accept all six of these values at the CLI.
Assignment policy is enforced by the server / account permissions, not by tcld:
Global Admin cannot assign Account Owner; Finance Admin is assignable by Account Owner
(and to Service Accounts by Global Admin). Owner changes may also require Support depending
on account policy. `none` is accepted only by `tcld user-group` commands.

### Namespace-Level Permissions

| Permission (tcld value) | Notes |
|--------------------------|-------|
| `Admin` | Full namespace control |
| `Write` | |
| `Read` | Read-only |

Format for `--namespace-permission` flag: `<namespace_id>=<permission>`
where `<namespace_id>` is the full Cloud namespace ID (e.g. `mynamespace.abc123`).

---

## User Groups (`tcld user-group`)

Alias: `ug`

### Create

```bash
tcld user-group create \
    --display-name <name> \
    --account-role <role> \
    --namespace-role <namespaceid>-<role>
```

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--display-name` | | Yes | Display name of the group |
| `--account-role` | | Yes | `admin` \| `read` \| `developer` \| `owner` \| `financeadmin` \| `none` |
| `--namespace-role` | `-nr` | No | Repeatable. Format: `<namespaceid>-<role>` where role is `admin` \| `read` \| `write`. Example: `mynamespace.abc123-read` |

Alias: `c`

**Important**: the `--namespace-role` format uses a **hyphen** separator (`<namespaceid>-<role>`), not `=`.
This differs from `tcld user` commands which use `<namespace>=<permission>`. Auto-generated tcld docs currently omit the format string; behavior is defined in tcld `nsRoleToAccess`.

### Get

```bash
tcld user-group get --group-id <id>
```

Alias: `g`

### List

```bash
tcld user-group list
```

| Flag | Alias | Notes |
|------|-------|-------|
| `--page-size` | `-s` | Defaults to 10 |
| `--page-token` | `-p` | |

### Delete

```bash
tcld user-group delete --group-id <id>
```

Alias: `d`

Every member loses the Namespace permissions the group conferred, which can
revoke access for many people at once. List the members first and confirm the
scope with the user before proposing the delete. To remove one person, use
`remove-users`; to change what the group grants, update its permissions. For a
SCIM-synced group the IdP owns group create/update/delete and membership, so
deleting it here does not change the IdP — offboard in the IdP instead. See
[cloud-saml-scim.md](cloud-saml-scim.md).

### Add Users

```bash
tcld user-group add-users --group-id <id> --user-email <email>
```

Alias: `au`

| Flag | Alias | Notes |
|------|-------|-------|
| `--group-id` | `-id` | Required |
| `--user-email` | `-e` | Can be specified multiple times |

### Remove Users

```bash
tcld user-group remove-users --group-id <id> --user-email <email>
```

Alias: `ru`

| Flag | Alias | Notes |
|------|-------|-------|
| `--group-id` | `-id` | Required |
| `--user-email` | `-e` | Can be specified multiple times |

### List Members

```bash
tcld user-group list-members --group-id <id>
```

Alias: `lm`

### Set Access

```bash
tcld user-group set-access --group-id <id> \
    --account-role <role> \
    --namespace-role <namespaceid>-<role>
```

Alias: `sa`

| Flag | Alias | Required | Notes |
|------|-------|----------|-------|
| `--group-id` | `-id` | Yes | |
| `--account-role` | | Conditional | Required for replace mode. Omit with `--append`/`--remove` (those modes reject setting account role). Values: `admin` \| `read` \| `developer` \| `owner` \| `financeadmin` \| `none` |
| `--namespace-role` | `-nr` | No | Repeatable. Same `<namespaceid>-<role>` format as create |
| `--append` | `-a` | No | Append namespace roles instead of replacing all existing roles |
| `--remove` | `-r` | No | Remove the given namespace roles instead of replacing |

Without `--append` or `--remove`, set-access **replaces** all existing roles and requires `--account-role`.

---

## Service Accounts (`tcld service-account`)

Service Accounts are non-human identities that use API keys to authenticate.
Use `tcld service-account --help` for a full list of subcommands.

### Create

```bash
tcld service-account create -n "<name>" -d "<description>" --ar "<account-role>"
# Optional: --np "<namespace>=<permission>"
```

Returns a `ServiceAccountId` used for subsequent operations.

### Create Scoped (Namespace-scoped)

```bash
tcld service-account create-scoped -n "<name>" --np "<namespace>=<permission>"
```

Namespace-scoped Service Accounts always have a `Read` Account Role and are restricted to a single namespace.
Cannot be reassigned to a different namespace after creation.

### List

```bash
tcld service-account list
```

### Get

```bash
tcld service-account get --service-account-id "<id>"
```

Alias: `g`. `--service-account-id` (alias `--id`) is required.

### Delete

```bash
tcld service-account delete --service-account-id "<id>"
```

Deleting a Service Account automatically deletes all associated API keys.

The blast radius is not one identity but every Worker and automation
authenticating with any key the Service Account owns, and none of it is
recoverable. Run `tcld apikey list --owner-type service-account --owner-id
<id>` first, report what would be revoked, and confirm with the user before
proposing the delete.

### Update

Three update commands exist:

```bash
# Update name or description
tcld service-account update --id "<id>" -d "<new description>"

# Update account role
tcld service-account set-account-role --id "<id>" --ar "<role>"

# Update namespace permissions
tcld service-account set-namespace-permissions --id "<id>" -p "<namespace>=<permission>"
```

### Namespace-Scoped Lifecycle

When a namespace is deleted, all associated Namespace-scoped Service Accounts and their API keys are automatically deleted.

---

## Account Operations (`tcld account`)

Alias: `a`

### Get

```bash
tcld account get
```

Returns information about the Temporal Cloud account you are logged into. No modifiers.

### List Regions

```bash
tcld account list-regions
```

Lists all regions where the account can provision namespaces. Alias: `l`

### Audit Log

Subcommands for configuring audit log sinks:

- `tcld account audit-log kinesis` (alias: `k`) -- Kinesis sinks: create, delete, get, list, update, validate
- `tcld account audit-log pubsub` (alias: `ps`) -- Pub/Sub sinks: create, delete, get, list, update, validate

### Metrics

```bash
tcld account metrics enable    # Enable metrics endpoint
tcld account metrics disable   # Disable metrics endpoint
```

End-entity certificates must be configured before enabling.
Managed via `tcld account metrics accepted-client-ca` subcommands: `add`, `list`, `set`, `remove`.

---

## Key Differences: `tcld user` vs `tcld user-group` Namespace Permission Format

| Context | Flag | Format | Example |
|---------|------|--------|---------|
| `tcld user` commands | `--namespace-permission` | `<namespace>=<permission>` | `ns1.abc123=Admin` |
| `tcld user-group` commands | `--namespace-role` | `<namespaceid>-<role>` | `mynamespace.abc123-read` |

The permission values also differ in case:
- `tcld user`: `Admin` | `Write` | `Read` (title case)
- `tcld user-group`: `admin` | `read` | `write` (lower case)
