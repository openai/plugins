# Ops Recipes

End-to-end operational playbooks that chain commands from the ops reference files.
For triage-focused walkthroughs, see `../triage/recipes.md`.

---

## (a) Set up a new Cloud namespace with API key auth (end-to-end)

**When to use:** Provisioning a new Temporal Cloud namespace from scratch, using API key authentication.

### Step 1: Create the namespace

```bash
tcld namespace create \
    --namespace <namespace_name>.<account_suffix> \
    --region <region> \
    --auth-method api_key \
    --retention-days 30 \
    --enable-delete-protection=true
```

Requires Developer, Account Owner, or Global Admin account-level role.
The creator is automatically granted Namespace Admin permission.

Optional flags:
- `--search-attribute "name=type"` (types: `Bool`, `Datetime`, `Double`, `Int`, `Keyword`, `Text`).
- `--tag "key=value"` (up to 10 tags per namespace).
- `--user-namespace-permission "email=permission"` (permissions: `Admin`, `Write`, `Read`).
- Omit `--enable-delete-protection` (or pass `--enable-delete-protection=false`) to skip delete protection; it is disabled by default.

### Step 2: Create a service account for Workers

```bash
tcld service-account create -n "<name>" -d "<description>" --ar "developer" \
    --np "<namespace_name>.<account_suffix>=Write"
```

Note the returned `ServiceAccountId`.

### Step 3: Create an API key for the service account

```bash
tcld apikey create \
    --name <key_name> \
    --description "<description>" \
    --duration <duration> \
    --service-account-id <service-account-id>
```

Save the returned key secret.

### Step 4: Verify connectivity

Set the API key and test with the Temporal CLI:

```bash
export TEMPORAL_API_KEY=<key-secret>
temporal workflow list \
    --address <namespace_name>.<account_suffix>.tmprl.cloud:7233 \
    --namespace <namespace_name>.<account_suffix>
```

### Step 5: (Optional) Grant additional user access

```bash
tcld user set-namespace-permissions \
    --user-email <email> \
    --namespace-permission <namespace_name>.<account_suffix>=<permission>
```

Permissions: `Admin`, `Write`, `Read`.

---

## (b) Check current APS and capacity mode for a Cloud namespace

**When to use:** You need to know whether a namespace is On-Demand or Provisioned and what its current APS limit is.

1. Get the namespace details:

   ```bash
   tcld namespace get \
       --namespace <namespace_name>.<account_suffix>
   ```

   Output is JSON by default (no `--format` flag exists).

2. In the JSON output, look for the capacity configuration section. Key fields:

   - **Capacity mode**: `on_demand` or `provisioned`.
   - **TRU count** (if provisioned): the number of Temporal Resource Units allocated. Valid values: 2, 3, 4, 6, 8, 10, 12.
   - **APS limit**: On-Demand default is 500; each TRU provides 500 APS.

3. To check whether throttling is occurring, look for `temporal_cloud_v0_resource_exhausted_errors` in your metrics.

---

## (c) Switch capacity mode from On-Demand to Provisioned

**When to use:** You are preparing for a planned spike (load test, promotion, migration) and need to pre-provision capacity beyond the On-Demand auto-scaling limit.

1. Confirm current capacity mode (see playbook (b)):

   ```bash
   tcld namespace get \
       --namespace <namespace_name>.<account_suffix>
   ```

2. Switch to Provisioned mode with the desired TRU count:

   ```bash
   tcld namespace capacity update \
       --namespace <namespace_name>.<account_suffix> \
       --capacity-mode provisioned \
       --capacity-value <tru_count>
   ```

   Valid `--capacity-value` values: 2, 3, 4, 6, 8, 10, 12.

   Temporal aims to provision the additional capacity within two minutes.

   For requests in excess of 4 TRUs in regions outside of the US, submit a support ticket to ensure capacity availability.

   Requires **Global Admin** or **Namespace Admin** role.

3. Verify the change took effect:

   ```bash
   tcld namespace get \
       --namespace <namespace_name>.<account_suffix>
   ```

   Confirm the capacity mode is `provisioned` and the TRU count matches your request.

4. When the spike is over, switch back to On-Demand:

   ```bash
   tcld namespace capacity update \
       --namespace <namespace_name>.<account_suffix> \
       --capacity-mode on_demand
   ```

   When switching back to On-Demand mode, your APS limit resets to the running average from the last 7 days. Plan for this if your workload is sensitive to the transition.

---

## (d) Find and triage all hung workflows in a namespace

**When to use:** You suspect workflows are stuck and need to locate them and understand why they are not making progress.

### Step 1: Count potentially stuck workflows

```bash
temporal workflow count \
    --query "ExecutionStatus = 'Running' AND StartTime < '2024-01-15T09:00:00Z'"
```

Replace the timestamp with your threshold for "too long". A count greater than zero indicates workflows that have been running longer than expected.

### Step 2: List the stuck workflows

```bash
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND StartTime < '2024-01-15T09:00:00Z'" \
    --limit 20
```

You can narrow further by Task Queue or Workflow Type:

```bash
temporal workflow list \
    --query "ExecutionStatus = 'Running' AND TaskQueue = 'my-task-queue' AND StartTime < '2024-01-15T09:00:00Z'"
```

### Step 3: Check worker health on the relevant Task Queue

```bash
temporal task-queue describe \
    --task-queue my-task-queue
```

Look for: active pollers present, `LastAccessTime` within the last minute, no growing `ApproximateBacklogCount`.

If there are no pollers, no Workers are running for this Task Queue and workflows on this queue cannot make progress.

### Step 4: Inspect individual stuck workflows

```bash
temporal workflow describe --workflow-id <id>
```

```bash
temporal workflow show --workflow-id <id> --reverse
```

```bash
temporal workflow stack --workflow-id <id>
```

### Step 5: Diagnose root cause

For diagnosing *why* a specific workflow is stuck (pending activities, pending child workflows, non-determinism, etc.), follow the triage procedures in `../triage/workflow-stuck.md`.

---

## (e) Rotate an API key without downtime

**When to use:** An API key is approaching expiration or needs to be rotated for security hygiene.

1. Create a new API key (for a user):

   ```bash
   tcld apikey create --name <name> \
       --description "<description>" \
       --duration <duration>
   ```

   Or for a Service Account:

   ```bash
   tcld apikey create \
       --name <name> \
       --description "<description>" \
       --duration <duration> \
       --service-account-id <service-account-id>
   ```

   You may reuse key names.

   Save the returned key secret -- it is only shown once.

2. Verify both the original and new key function properly:

   ```bash
   temporal workflow list \
       --address <namespace>.<account>.tmprl.cloud:7233 \
       --namespace <namespace_id>.<account_id>
   ```

   Set `TEMPORAL_API_KEY` to each key in turn and confirm the command succeeds.

3. Update clients and workers to load the new key.

4. Once no traffic uses the old key, delete it:

   ```bash
   tcld apikey delete --id <old_apikey_id>
   ```

   Alternatively, disable before deleting to validate nothing breaks:

   ```bash
   tcld apikey disable --id <old_apikey_id>
   ```

**Limits:** Up to 10 non-expired keys per user; up to 20 non-expired keys per Service Account. Maximum expiration: 2 years.

---

## (f) Audit namespace access (users + keys + service accounts)

**When to use:** You need a complete picture of who and what can access a namespace -- humans, API keys, and service accounts.

### Step 1: List all users with access to the namespace

```bash
tcld user list --namespace <namespace_name>.<account_suffix>
```

This filters to users with direct permissions on the specified namespace. Users with account-level roles (e.g., Account Owner, Global Admin) have implicit access to all namespaces but may not appear in this filtered list — check `tcld user list` (without `--namespace`) and inspect account roles to get the full picture.

### Step 2: Inspect individual user permissions

```bash
tcld user get --user-email <email>
```

Check the account role (`admin`, `developer`, `read`) and namespace-level permissions (`Admin`, `Write`, `Read`).

### Step 3: List all user groups

```bash
tcld user-group list
```

For each group with namespace access, list its members:

```bash
tcld user-group list-members --group-id <id>
```

### Step 4: List all service accounts

```bash
tcld service-account list
```

Review the output for service accounts that have permissions on the target namespace. Namespace-scoped Service Accounts always have a `Read` Account Role and are restricted to a single namespace.

### Step 5: List all API keys

```bash
tcld apikey list
```

Cross-reference the API key owners (user IDs or service account IDs) against the users and service accounts identified above.

---
## (g) Rotate mTLS certificates

**When to use:** A CA certificate is approaching expiration, or you need to switch to a new CA without disrupting running Workers.

Temporal Cloud sends email notifications 15 days before certificate expiration.

### Step 1: Generate a new CA certificate

```bash
tcld generate-certificates certificate-authority-certificate \
    --organization <value> \
    --validity-period <duration> \
    --ca-certificate-file <new_ca>.pem \
    --ca-key-file <new_ca>.key
```

Default key algorithm is ECDSA P-384. Maximum duration: 1 year.

### Step 2: Generate new end-entity (leaf) certificates

```bash
tcld generate-certificates end-entity-certificate \
    --organization <value> \
    --validity-period <duration> \
    --ca-certificate-file <new_ca>.pem \
    --ca-key-file <new_ca>.key \
    --certificate-file <new_client>.pem \
    --key-file <new_client>.key
```

End-entity certificate must expire before its root CA certificate.

### Step 3: Create a combined PEM bundle with old and new CA certificates

Concatenate both CA certificates into a single PEM file:

```
-----BEGIN CERTIFICATE-----
... old CA cert ...
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
... new CA cert ...
-----END CERTIFICATE-----
```

### Step 4: Upload the combined bundle (replaces all existing CAs)

```bash
tcld namespace accepted-client-ca set \
    --namespace <namespace_name>.<account_suffix> \
    --ca-certificate-file <combined>.pem
```

Both old and new end-entity certificates will now be accepted.

### Step 5: Roll out new end-entity certificates to Workers and Clients

Deploy the new leaf certificates to all Workers and Clients. Monitor traffic to the old certificate until it ceases.

### Step 6: Remove the old CA certificate

Create a file containing only the new CA certificate and run `set` again:

```bash
tcld namespace accepted-client-ca set \
    --namespace <namespace_name>.<account_suffix> \
    --ca-certificate-file <new_ca_only>.pem
```

### Step 7: Verify the namespace only has the new CA

```bash
tcld namespace accepted-client-ca list \
    --namespace <namespace_name>.<account_suffix>
```

Do NOT use a CA certificate signed with SHA-1 -- such signatures are rejected.

---

## (h) Check self-hosted cluster health

**When to use:** You want to verify that a self-hosted Temporal cluster is operational and inspect its configuration.

The full command reference for self-hosted cluster operations lives in [self-hosted-admin.md](self-hosted-admin.md). This recipe chains the key commands into a quick health check.

1. **Cluster health:** `temporal operator cluster health` — returns `SERVING` if healthy.
2. **Cluster details:** `temporal operator cluster describe --detail` — Cluster Name, persistence, visibility, shard count.
3. **Namespaces:** `temporal operator namespace list` — all Namespaces on the Service.
4. **Worker health on key Task Queues:** `temporal task-queue describe --task-queue <task_queue_name>` — look for active pollers and no growing `ApproximateBacklogCount`.
5. **Spot-check stuck workflows:** `temporal workflow count --query "ExecutionStatus = 'Running' AND StartTime < '<threshold>'"` — if high, follow playbook (d) above.

For remote clusters, pass `--address <host>:<port>` (and TLS flags if enabled). See [self-hosted-admin.md → Global flags](self-hosted-admin.md#global-flags-summary) for the full flag set.

---

## (i) View billing and generate a billing report

**When to use:** You need to understand your Temporal Cloud costs at the namespace level, or generate a CSV billing report for FinOps tooling.

### Step 1: Review billing in the Cloud UI

Navigate to the **Billing** page in the Temporal Cloud UI. Account Owners and Finance Admins can view:

- Current balance and recent bill
- Invoices table (with downloadable invoices for prior months)
- Credits table
- Cost by Namespace (per-namespace proportional cost breakdown)

### Step 2: Generate a billing report via the Billing API

The Billing API provides namespace-level cost attribution in CSV format.

Report generation is asynchronous:

1. Call `CreateBillingReport` with the desired date range (billing-month boundaries) and granularity. The response includes a `billing_report_id` and `async_operation_id`.
2. Poll `GetBillingReport` using the `billing_report_id` with exponential backoff.
3. When the state is `BILLING_REPORT_STATE_GENERATED`, retrieve the download URL.
4. Download the CSV before the URL expires.

Date range limits by granularity:

| Granularity | Available range |
|---|---|
| Hourly | Current + previous billing month |
| Daily | Current + previous two billing months |
| Monthly | Current + previous eleven billing months |

### Step 3: Interpret the report

Key columns to understand:

- `ContractedCost`: The actual cost (not `Cost` or `TotalCost`).
- `ResourceID`: `namespace_name.account_id` (e.g., `production.a2dd6`), not just the namespace name.
- `BillingCurrency`: Values are in cents (e.g., `USD (cents)`).

Only one billing report per account is generated at a time; additional requests are queued.

---

## (j) Configure an Audit Log sink

**When to use:** You need to stream Temporal Cloud control plane Audit Logs to your infrastructure for compliance or monitoring.

Audit Logs capture control plane events only -- they do NOT capture data plane events (Workflow Start, etc.).

Required role: Account Owner or Global Administrator.

### Option A: AWS Kinesis

1. Ensure you have a Kinesis Data Stream in your AWS account. An [AWS CloudFormation template](https://temporal-auditlogs-config.s3.us-west-2.amazonaws.com/cloudformation/iam-role-for-temporal-audit-logs.yaml) is available to create the required IAM role.

2. In the Cloud UI: **Settings** > **Audit Logs** > **Setup**.

3. Choose **Auto** (configure CloudFormation from the UI) or **Manual** (download a template).

4. Enter the **Kinesis ARN**, **Role name**, and **AWS region**.

5. Complete the CloudFormation stack creation.

6. Use the **Verify** button to confirm Temporal can write to the stream.

First logs appear within 10 minutes.

### Option B: GCP Pub/Sub

1. Create a Pub/Sub topic and set up a service account in the same GCP project (or skip if using Terraform).

2. In the Cloud UI: **Settings** > **Audit Logs** > **Setup** > **Pub/Sub**.

3. Enter the **service account email** and **Topic name**.

4. Choose **Manual** or **Deploy with Terraform** to configure permissions.

5. Use the **Verify** button, then click **Create**.

Audit Logs appear in Pub/Sub within 10 minutes.

### Verify the sink is working

The Audit Logs page of the Cloud UI shows the current status: an **On** badge if functioning normally, or an error summary if an issue is detected.

### Accessing logs via API

Audit Logs are accessible for the past 30 days without a sink.

**[Cloud Ops API](https://docs.temporal.io/ops) (retrieving log records):** Use `StartTimeInclusive`, `EndTimeExclusive`, `PageSize` (max 1000, default 100), and `PageToken` for pagination.

tcld does not retrieve log records; it only manages export sinks. List the configured sinks with:

```bash
tcld account audit-log kinesis list
tcld account audit-log pubsub list
```

---

## (k) Provision resources with Terraform

**When to use:** You want to automate Temporal Cloud resource management (Namespaces, Users, Service Accounts, API Keys, Nexus Endpoints) using infrastructure as code.

Provider source: [github.com/temporalio/terraform-provider-temporalcloud](https://github.com/temporalio/terraform-provider-temporalcloud).

### Step 1: Set up the Terraform provider

```bash
export TEMPORAL_CLOUD_API_KEY=<your-secret-key>
```

```hcl
terraform {
  required_providers {
    temporalcloud = {
      source = "temporalio/temporalcloud"
    }
  }
}

provider "temporalcloud" {

}
```

### Step 2: Define resources

Example Namespace:

```hcl
resource "temporalcloud_namespace" "namespace" {
  name               = "terraform"
  regions            = ["aws-us-east-1"]
  accepted_client_ca = base64encode(file("ca.pem"))
  retention_days     = 14
}
```

Example User with namespace access:

```hcl
resource "temporalcloud_user" "developer" {
  email          = "developer@example.com"
  account_access = "Developer"

  namespace_accesses = [{
    namespace_id = temporalcloud_namespace.namespace.id
    permission   = "Write"
  }]
}
```

### Step 3: Apply

```bash
terraform init
terraform apply
```

### Key limitations

- Once a resource is managed by Terraform, manage it only through Terraform.
- Terraform cannot create, update, or delete the Account Owner role.
- Namespace access must be managed from the User resource, not the Namespace resource.
- API keys cannot be imported into Terraform -- create new keys instead.
- The Terraform resource for API keys is `temporalcloud_apikey` (no underscore between `api` and `key`).

---

## (l) Set up SAML SSO

**When to use:** You want to enable single sign-on for your organization's Temporal Cloud account using your corporate identity provider.

SAML is available as an add-on for any Temporal Cloud plan.

### Step 1: Locate your Account Id

Find your Account Id (5-6 characters after the period in your Namespace Id, e.g., `f45a2`). Available from the Cloud UI profile dropdown or from any Namespace Id.

### Step 2: Construct the SAML URLs

Entity identifier:

```
urn:auth0:prod-tmprl:ACCOUNT_ID-saml
```

Callback URL:

```
https://login.tmprl.cloud/login/callback?connection=ACCOUNT_ID-saml
```

Replace `ACCOUNT_ID` with your actual Account Id.

### Step 3: Configure your IdP

**Microsoft Entra ID:** Create an Enterprise application, configure SAML with the entity identifier, callback URL, and sign on URL (`https://cloud.temporal.io/login/saml?connection=ACCOUNT_ID-saml`). Set NameID to `user.userprincipalname` with format `emailAddress`. Collect the Certificate (Base64) and Login URL.

**Okta:** Create a SAML 2.0 app integration. Set Single sign on URL to the callback URL. Set Audience URI to the entity identifier. Set Name ID format to `EmailAddress` with `email` and `name` attribute statements. Collect IdP settings and download the active certificate.

### Step 4: Submit a support ticket

Include:

- The sign-in URL from your application
- The X.509 SAML sign-in certificate in PEM format
- One or more IdP domains to map to the SAML connection

### Step 5: Verify

After Temporal confirms configuration, log in with your email and click **Continue** to be redirected to your IdP.
