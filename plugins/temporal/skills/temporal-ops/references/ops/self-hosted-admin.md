# Self-Hosted Admin — `temporal operator`

Control-plane operations for self-hosted Temporal Services.
All commands use the `temporal operator` CLI prefix and connect to `--address` (default `localhost:7233`).

> **Cloud vs Self-Hosted**: `temporal operator` manages self-hosted clusters.
> Cloud equivalents use `tcld` — see [comparison table](#cloud-equivalent-comparison) at the end.

---

## Cluster Commands

### Health check

```bash
temporal operator cluster health
```

Returns health status of the Temporal Service. No subcommand-specific flags; uses [global flags](#global-flags-summary) only.

### Describe cluster

```bash
temporal operator cluster describe [--detail]
```

Shows Cluster Name, persistence store, and visibility store.

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--detail` | No | **bool** | Show history shard count and Cluster/Service version information. |

### System info

```bash
temporal operator cluster system
```

Shows Server version, scheduling support, and more. Defaults to local Service; use `--frontend-address` to target a remote endpoint.

### List clusters

```bash
temporal operator cluster list [--limit max-count]
```

Lists remote Temporal Clusters registered to the local Service. Reports: name, ID, address, History Shard count, Failover version, availability.

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--limit` | No | **int** | Maximum number of Clusters to display. |

### Remove cluster

Removes a registered remote Cluster from the local Service. De-registering it
affects everything relying on replication to that Cluster, across every Namespace
configured against it — the blast radius is Service-wide, not per-Namespace.
Confirm the Cluster name and what still depends on it with the user before
proposing this.

```bash
temporal operator cluster remove --name YourClusterName
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--name` | Yes | **string** | Cluster/Service name. |

### Upsert cluster

```bash
temporal operator cluster upsert \
    --frontend-address "YourRemoteEndpoint:YourRemotePort" \
    --enable-connection false
```

Add, remove, or update a registered remote Cluster.

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--enable-connection` | No | **bool** | Set the connection to "enabled". |
| `--enable-replication` | No | **bool** | Set the replication to "enabled". |
| `--frontend-address` | Yes | **string** | Remote endpoint. |

---

## Namespace Commands

### Create namespace

```bash
temporal operator namespace create \
    --namespace YourNewNamespaceName \
    [options]
```

Create a Namespace with multi-region replication:

```bash
temporal operator namespace create \
    --global \
    --namespace YourNewNamespaceName
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--active-cluster` | No | **string** | Active Cluster (Service) name. |
| `--cluster` | No | **string[]** | Cluster names. Can be passed multiple times. |
| `--data` | No | **string[]** | Namespace data as `KEY=VALUE` pairs. Keys must be identifiers, values must be JSON. |
| `--description` | No | **string** | Namespace description. |
| `--email` | No | **string** | Owner email. |
| `--global` | No | **bool** | Enable multi-region data replication. |
| `--history-archival-state` | No | **string-enum** | Accepted values: `disabled`, `enabled`. Default `disabled`. |
| `--history-uri` | No | **string** | Archive history to this URI. Once enabled, can't be changed. |
| `--retention` | No | **duration** | Time to preserve closed Workflows before deletion. Default `72h`. |
| `--visibility-archival-state` | No | **string-enum** | Accepted values: `disabled`, `enabled`. Default `disabled`. |
| `--visibility-uri` | No | **string** | Archive visibility to this URI. Once enabled, can't be changed. |

Note: URI values for archival states can't be changed once enabled.

### Delete namespace

Deletion is permanent, and it takes the Namespace's Workflow Executions and Task
Queues with it. Never run it autonomously. Before proposing it, report what the
Namespace holds — `temporal workflow count --query 'ExecutionStatus="Running"'`
against that Namespace — and confirm the Namespace name with the user.

```bash
temporal operator namespace delete --namespace YourNamespaceName
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--yes`, `-y` | No | **bool** | Don't prompt to confirm deletion. |

The confirmation is stronger than the usual `y/N`: the CLI asks for the Namespace
name to be typed back. Without `--yes`, and with no terminal to answer the prompt,
the command exits non-zero with `user denied confirmation or mistyped the
namespace name` and deletes nothing. So `--yes` belongs only in a command the user
has already approved — never in a retry of one that failed its prompt.

### Describe namespace

```bash
temporal operator namespace describe --namespace YourNamespaceName
```

Can also identify by `--namespace-id`:

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--namespace-id` | No | **string** | Namespace ID. |

### List namespaces

```bash
temporal operator namespace list
```

Displays a detailed listing for all Namespaces on the Service. No subcommand-specific flags.

### Update namespace

```bash
temporal operator namespace update --namespace YourNamespaceName [options]
```

Examples:

```bash
# Assign active cluster
temporal operator namespace update \
    --namespace YourNamespaceName \
    --active-cluster NewActiveCluster

# Promote for multi-region replication
temporal operator namespace update \
    --namespace YourNamespaceName \
    --promote-global
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--active-cluster` | No | **string** | Active Cluster (Service) name. |
| `--cluster` | No | **string[]** | Cluster (Service) names. |
| `--data` | No | **string[]** | Namespace data as `KEY=VALUE` pairs. |
| `--description` | No | **string** | Namespace description. |
| `--email` | No | **string** | Owner email. |
| `--history-archival-state` | No | **string-enum** | Accepted values: `disabled`, `enabled`. |
| `--history-uri` | No | **string** | Archive history URI. Once enabled, can't be changed. |
| `--promote-global` | No | **bool** | Enable multi-region data replication. |
| `--replication-state` | No | **string-enum** | Accepted values: `normal`, `handover`. |
| `--retention` | No | **duration** | Time to preserve closed Workflows before deletion. |
| `--visibility-archival-state` | No | **string-enum** | Accepted values: `disabled`, `enabled`. |
| `--visibility-uri` | No | **string** | Archive visibility URI. Once enabled, can't be changed. |

---

## Search Attribute Commands

Supported types: `Text`, `Keyword`, `Int`, `Double`, `Bool`, `Datetime`, `KeywordList`.

### Create search attribute

```bash
temporal operator search-attribute create \
    --name YourAttributeName \
    --type Keyword
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--name` | Yes | **string[]** | Search Attribute name. |
| `--type` | Yes | **string-enum[]** | Accepted values: `Text`, `Keyword`, `Int`, `Double`, `Bool`, `Datetime`, `KeywordList`. |

### List search attributes

```bash
temporal operator search-attribute list
```

Displays active Search Attributes that can be assigned or used in Workflow Queries. No subcommand-specific flags.

### Remove search attribute

Confirm with the user before proposing a removal: every List Filter, saved query,
and Workflow Query referencing the attribute stops resolving, and the effect is
Namespace-wide rather than scoped to one Workflow.

```bash
temporal operator search-attribute remove --name YourAttributeName
```

Once the user has approved the removal, `--yes` skips the confirmation prompt:

```bash
temporal operator search-attribute remove --name YourAttributeName --yes
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--name` | Yes | **string[]** | Search Attribute name. |
| `--yes`, `-y` | No | **bool** | Don't prompt to confirm removal. |

> **Self-hosted deletion note**: `remove` de-registers custom attributes from the queryable set ("Remove custom Search Attributes from the options that can be assigned or used with Workflow Queries"). Permanent deletion from the backing store may require additional steps. The Cloud docs note: "If you wish to delete a Search Attribute, please contact Support."

---

## Nexus Endpoint Commands

### Create endpoint

```bash
temporal operator nexus endpoint create \
    --name your-endpoint \
    --target-namespace your-namespace \
    --target-task-queue your-task-queue \
    --description-file DESCRIPTION.md
```

Target is either a Worker (`--target-namespace` + `--target-task-queue`) or an external URL (`--target-url`).

Fails if an Endpoint with the same name already exists.

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--description` | No | **string** | Endpoint description. May use Markdown. |
| `--description-file` | No | **string** | Path to description file. May use Markdown. |
| `--name` | Yes | **string** | Endpoint name. |
| `--target-namespace` | No | **string** | Namespace where handler Worker polls for Nexus tasks. |
| `--target-task-queue` | No | **string** | Task Queue that handler Worker polls for Nexus tasks. |
| `--target-url` | No | **string** | External endpoint URL. _(Experimental)_ |

### Delete endpoint

```bash
temporal operator nexus endpoint delete --name your-endpoint
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--name` | Yes | **string** | Endpoint name. |

### Get endpoint (EXPERIMENTAL)

```bash
temporal operator nexus endpoint get --name your-endpoint
```

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--name` | Yes | **string** | Endpoint name. |

### List endpoints

```bash
temporal operator nexus endpoint list
```

No subcommand-specific flags.

### Update endpoint

```bash
temporal operator nexus endpoint update \
    --name your-endpoint \
    --target-task-queue your-other-queue
```

Patches the endpoint; existing fields for which flags are not provided are left unchanged.

| Flag | Required | Type | Description |
|------|----------|------|-------------|
| `--description` | No | **string** | Endpoint description. May use Markdown. |
| `--description-file` | No | **string** | Path to description file. May use Markdown. |
| `--name` | Yes | **string** | Endpoint name. |
| `--target-namespace` | No | **string** | Namespace where handler Worker polls for Nexus tasks. |
| `--target-task-queue` | No | **string** | Task Queue that handler Worker polls for Nexus tasks. |
| `--target-url` | No | **string** | External endpoint URL. _(Experimental)_ |
| `--unset-description` | No | **bool** | Unset the description. |

---

## Global Flags Summary

Key global flags applicable to all `temporal operator` commands:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--address` | **string** | `localhost:7233` | Temporal Service gRPC endpoint. |
| `--namespace`, `-n` | **string** | `default` | Temporal Service Namespace. |
| `--api-key` | **string** | | API key for request. |
| `--tls` | **bool** | | Enable base TLS encryption. Defaulted to true if api-key or other TLS options are present. |
| `--tls-ca-path` | **string** | | Path to server CA certificate. |
| `--tls-cert-path` | **string** | | Path to x509 certificate. |
| `--tls-key-path` | **string** | | Path to x509 private key. |
| `--tls-server-name` | **string** | | Override target TLS server name. |
| `--output`, `-o` | **string-enum** | `text` | Non-logging data output format. Accepted values: `text`, `json`, `jsonl`, `none`. |
| `--log-level` | **string-enum** | `never` | Log level. Accepted values: `debug`, `info`, `warn`, `error`, `never`. |
| `--env` | **string** | `default` | Active environment name. |
| `--config-file` | **string** | | TOML config file path. |

See `docs/cli/operator.mdx` lines 520-558 for the full list.

---

## Cloud-Equivalent Comparison

| Operation | Self-Hosted (`temporal operator`) | Cloud (`tcld`) |
|-----------|-----------------------------------|----------------|
| Check cluster health | `temporal operator cluster health` | N/A (Cloud-managed) |
| Describe cluster | `temporal operator cluster describe` | N/A (Cloud-managed) |
| Server system info | `temporal operator cluster system` | N/A (Cloud-managed) |
| List clusters | `temporal operator cluster list` | N/A (Cloud-managed) |
| Create namespace | `temporal operator namespace create` | `tcld namespace create` |
| Delete namespace | `temporal operator namespace delete` | `tcld namespace delete` |
| Describe namespace | `temporal operator namespace describe` | `tcld namespace get` |
| List namespaces | `temporal operator namespace list` | `tcld namespace list` |
| Update namespace | `temporal operator namespace update` | No single equivalent; use per-attribute subcommands (`retention set`, `capacity update`, `auth-method set`, `tags`, …) |
| Create search attribute | `temporal operator search-attribute create` | `tcld namespace search-attributes add` |
| List search attributes | `temporal operator search-attribute list` | No tcld subcommand; use Cloud UI or Cloud Ops API |
| Remove search attribute | `temporal operator search-attribute remove` | `tcld namespace search-attributes rename` |
| Create Nexus endpoint | `temporal operator nexus endpoint create` | `tcld nexus endpoint create` |
| Delete Nexus endpoint | `temporal operator nexus endpoint delete` | `tcld nexus endpoint delete` |
| Get Nexus endpoint | `temporal operator nexus endpoint get` | `tcld nexus endpoint get` |
| List Nexus endpoints | `temporal operator nexus endpoint list` | `tcld nexus endpoint list` |
| Update Nexus endpoint | `temporal operator nexus endpoint update` | `tcld nexus endpoint update` |
