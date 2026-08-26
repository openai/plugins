# Cloud Audit Logs

Audit Logs provide forensic access information for operations in the Temporal Cloud control plane. They answer "who, when, and what" questions about Temporal Cloud resources.

Required role: Account Owner or Global Administrator to view Audit Logs via UI, use the API, or configure an Audit Log Integration.

**Audit Logs do NOT capture data plane events** (Workflow Start, Workflow Terminate, Schedule Create, etc.). For closed Workflow Histories, use the Export feature instead.

---

## Supported events

### Account
- `ChangeAccountPlanType`: Change Account Plan Type
- `UpdateAccountAPI`: Configure Audit Logs, Configure Observability Endpoint

### API Keys
- `CreateAPIKey`: Create API Key
- `DeleteAPIKey`: Delete API Key
- `UpdateAPIKey`: Update API Key

### Connectivity Rules
- `CreateConnectivityRule`: Create Connectivity Rule
- `DeleteConnectivityRule`: Delete Connectivity Rule

### Namespace
- `CreateNamespaceAPI`: Create Namespace
- `DeleteNamespaceAPI`: Delete Namespace
- `FailoverNamespacesAPI`: Failover (for High Availability Namespaces)
- `RenameCustomSearchAttributeAPI`: Rename Custom Search Attribute
- `UpdateNamespaceAPI`: Retention period changes, replica edits, authentication method updates, custom search attribute updates, connectivity rule bindings

### Namespace Export
- `CreateNamespaceExportSink`: Create Namespace Export Sink
- `DeleteNamespaceExportSink`: Delete Namespace Export Sink
- `UpdateNamespaceExportSink`: Update Namespace Export Sink
- `ValidateNamespaceExportSink`: Validate Namespace Export Sink

### Nexus Endpoint
- `CreateNexusEndpoint`: Create Nexus Endpoint
- `DeleteNexusEndpoint`: Delete Nexus Endpoint
- `UpdateNexusEndpoint`: Update Nexus Endpoint

### Service Accounts
- `CreateServiceAccount`: Create Service Account
- `CreateServiceAccountAPIKey`: Create Service Account API Key
- `DeleteServiceAccount`: Delete Service Account
- `UpdateServiceAccount`: Update Service Account

### User
- `CreateUserAPI`: Create Users
- `DeleteUserAPI`: Delete Users
- `InviteUsersAPI`: Invite Users
- `SetUserNamespaceAccessAPI`: Set User Namespace Access
- `UpdateIdentityNamespacePermissionsAPI`: Update Identity Namespace Permissions
- `UpdateUserAPI`: Update User Account-level Roles
- `UpdateUserNamespacePermissionsAPI`: Update User Namespace Permissions

### User Groups
- `CreateUserGroup`: Create User Group
- `DeleteUserGroup`: Delete User Group
- `SetUserGroupNamespaceAccess`: Set User Group Namespace Access
- `UpdateUserGroup`: Update User Group

---

## Audit Log format

```json
{
  "operation":          // Operation that was performed
  "principal":          // Information about who initiated the operation
  "raw_details":        // Details about the request
  "x_forwarded_for":    // The IP address(es) making the call
  "emit_time":          // Time the operation was recorded
  "log_id":             // Unique ID of the log entry
  "async_operation_id": // Optional async operation id set by the user when sending a request
  "request_id":         // DEPRECATED, use async_operation_id
  "status":             // Status, such as OK or ERROR
  "version":            // Version of the log entry
}
```

**Deprecation notice:** The `request_id` field is deprecated and is planned for removal on or after November 1 2026. Use `async_operation_id` instead.

The `x_forwarded_for` field uses the `X-Forwarded-For` format: a comma-separated list of IP addresses, evaluated from last to first until meeting the first untrusted IP address.

---

## Viewing Audit Logs

### Via the Cloud UI

1. Select **Settings**.
2. On the **Settings** page, select **Audit Logs**.

Up to 1000 events can be downloaded from the Audit Log UI to a local file.

### Via the API

Audit Logs can be accessed using the Cloud Ops API. Use the API to build dashboards for viewing Audit Logs outside of Temporal Cloud. If your goal is to export logs continuously, use an Audit Log sink instead.

Audit Logs are accessible for the past 30 days using the API.

API filter parameters:

| Parameter | Description |
|---|---|
| `StartTimeInclusive` | Filter for UTC time >= (defaults to 30 days ago) - optional |
| `EndTimeExclusive` | Filter for UTC time < (defaults to current time) - optional |
| `PageSize` | Cannot exceed 1000. Defaults to 100. - optional |
| `PageToken` | Page token for continuing from another response - optional |

---

## Audit Log sink configuration

Audit Logs can be sent to AWS Kinesis or GCP Pub/Sub.

### AWS Kinesis

Prerequisites: an AWS account and Kinesis Data Streams.

An [AWS CloudFormation template](https://temporal-auditlogs-config.s3.us-west-2.amazonaws.com/cloudformation/iam-role-for-temporal-audit-logs.yaml) is available to create an IAM role with access to a Kinesis stream.

Kinesis has a rate limit of 1,000 messages per second.

Setup via Cloud UI:

1. Select **Settings** > **Audit Logs** > **Setup**.
2. Choose your **Access method**: **Auto** (configure CloudFormation from the Cloud UI) or **Manual** (download a template).
3. Enter the **Kinesis ARN**, **Role name**, and **AWS region**.
4. Follow the Auto or Manual steps to complete CloudFormation stack creation.

Use the **Verify** button to confirm Temporal can write to the stream.

First logs appear within 10 minutes after configuring the sink.

### GCP Pub/Sub

For manual setup: create a Pub/Sub topic and a service account in the same GCP project.

Setup via Cloud UI:

1. Select **Settings** > **Audit Logs** > **Setup**.
2. Select **Pub/Sub**.
3. Enter the **service account email** and **Topic name**.
4. Choose **Manual** or **Deploy with Terraform** to configure permissions.
5. Use the **Verify** button to confirm Temporal can write to the topic.
6. Click **Create**.

Audit Logs appear in Pub/Sub within 10 minutes.

If using Terraform for deployment, the manual prerequisites (topic and service account creation) can be skipped.

---

## Managing sinks via tcld

Sinks can also be managed with `tcld account audit-log` (alias `al`), under two provider subgroups: `kinesis` (alias `k`) and `pubsub` (alias `ps`).

Both subgroups expose the same subcommands:

| Subcommand | Alias | Purpose |
|---|---|---|
| `create` | `c` | Create a sink (created enabled) |
| `validate` | `v` | Validate sink config without creating it |
| `update` | `u` | Update sink fields or toggle enabled |
| `get` | `g` | Get a sink by name |
| `delete` | `d` | Delete a sink by name |
| `list` | `l` | List sinks |

### Kinesis create/validate flags

| Flag | Alias | Required |
|---|---|---|
| `--sink-name` | | Yes |
| `--role-name` | `--rn` | Yes |
| `--destination-uri` | `--du` | Yes |
| `--region` | `--re` | Yes |

### Pub/Sub create/validate flags

| Flag | Alias | Required |
|---|---|---|
| `--sink-name` | | Yes |
| `--service-account-email` | `--sae` | Yes |
| `--topic-name` | `--tn` | Yes |

`update` additionally takes `--enabled` (toggle `true`/`false`) and `--resource-version` / `-v`; provider flags are optional on update.

`get`, `delete`, and `list` are shared across both subgroups. `get` and `delete` identify the sink with `--sink-name` (`delete` also accepts `--resource-version` / `-v`); `list` accepts `--page-size` and `--page-token`.

---

## Troubleshooting

### Sink status

The Audit Logs page of the Cloud UI shows the current status:

- If an error is detected, a summary appears below the page title.
- If functioning normally, an **On** badge appears next to the page heading.

Temporal retains Audit Log information for up to 30 days. To retrieve logs up to the past 30 days, file a request.

If you experience an issue with a sink, Temporal can provide missing audit information via a support ticket.

### Deleting a sink

In the Cloud UI: **Settings** > **Audit Logs** > **Edit** > **Delete** at the bottom of the page. After confirmation, the sink is removed and logs stop flowing to the stream.
