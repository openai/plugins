# Cloud Terraform Provider

The Terraform Temporal Cloud provider allows you to use Terraform to manage resources for Temporal Cloud. It uses the Cloud Ops API.

Once a resource is managed by Terraform, you should only use Terraform to manage that resource.

Source of truth for resource/data-source schemas: [Terraform Registry](https://registry.terraform.io/providers/temporalio/temporalcloud/latest/docs). Public docs at docs.temporal.io can lag the provider.

---

## Prerequisites

- Terraform CLI
- An API Key for authentication

---

## Setup

Set the `TEMPORAL_CLOUD_API_KEY` environment variable:

```bash
export TEMPORAL_CLOUD_API_KEY=<your-secret-key>
```

Or pass it directly in the provider block:

```hcl
provider "temporalcloud" { api_key = "my-temporalcloud-api-key" }
```

Required provider configuration:

```hcl
terraform {
  required_providers {
    temporalcloud = {
      source = "temporalio/temporalcloud"
    }
  }
}

provider "temporalcloud" {
  # Optional: TEMPORAL_CLOUD_ENDPOINT, TEMPORAL_CLOUD_ALLOWED_ACCOUNT_ID,
  # TEMPORAL_CLOUD_ALLOW_INSECURE
}
```

---

## Supported resources (provider inventory)

Prefer the [registry resources list](https://registry.terraform.io/providers/temporalio/temporalcloud/latest/docs) for the full set. Current resources include:

- `temporalcloud_namespace`
- `temporalcloud_nexus_endpoint`
- `temporalcloud_user`
- `temporalcloud_service_account`
- `temporalcloud_apikey`
- `temporalcloud_connectivity_rule`
- `temporalcloud_custom_role`
- `temporalcloud_group`
- `temporalcloud_group_access`
- `temporalcloud_group_members`
- `temporalcloud_metrics_endpoint`
- `temporalcloud_namespace_export_sink`
- `temporalcloud_namespace_search_attribute`
- `temporalcloud_namespace_tags`
- `temporalcloud_account_audit_log_sink`

Sections below cover the most common ops workflows.

---

## Namespace management

Resource: `temporalcloud_namespace`

Required identity: Account Owner, Global Admin, or Developer Account Role.

### Create

```hcl
resource "temporalcloud_namespace" "namespace" {
  name               = "terraform"
  regions            = ["aws-us-east-1"]
  accepted_client_ca = base64encode(file("ca.pem"))
  retention_days     = 14
}
```

Key fields: `name`, `regions`, `retention_days`. Auth: at least one of `accepted_client_ca` (mTLS) or `api_key_auth = true`. Both may be enabled.

```hcl
resource "temporalcloud_namespace" "api_key_ns" {
  name           = "terraform-api-key"
  regions        = ["aws-us-east-1"]
  api_key_auth   = true
  retention_days = 14
}
```

### Update

Terraform automatically recognizes changes in `.tf` files and applies them. For example, changing `retention_days` triggers an update.

### Delete

Remove the `temporalcloud_namespace` resource and all dependent resource configurations from your Terraform files and run `terraform apply`.

Deletion safeguards:

- Terraform meta-argument: `prevent_destroy`
- Cloud-side: `namespace_lifecycle.enable_delete_protection` (must set to `false` before destroy)

### Import

```bash
terraform import temporalcloud_namespace.terraform namespaceid.acctid
```

The Namespace ID is in the format `namespaceid.acctid`, available at the top of the Namespace page in the Cloud UI.

---

## Nexus Endpoint management

Resource: `temporalcloud_nexus_endpoint`

Required identity: Developer role (or higher) and Namespace Admin permission on the Endpoint's target Namespace.

### Create

```hcl
resource "temporalcloud_nexus_endpoint" "nexus_endpoint" {
  name        = "terraform-nexus-endpoint"
  description = "my-service"
  worker_target = {
    namespace_id = temporalcloud_namespace.target_namespace.id
    task_queue   = "terraform-task-queue"
  }
  allowed_caller_namespaces = [
    temporalcloud_namespace.caller_namespace.id,
  ]
}
```

Key fields: `name`, `description`, `worker_target` (namespace_id, task_queue), `allowed_caller_namespaces`.

### Import

Address must be `TYPE.NAME` matching your resource block:

```bash
terraform import temporalcloud_nexus_endpoint.nexus_endpoint <your-nexus-endpoint-ID>
```

---

## User management

Resource: `temporalcloud_user`

### Limitations

- Terraform cannot create, update, or delete the Account Owner role. You can import an Account Owner, but not manage the role itself.
- Namespace access must be managed from the User resource, not from the Namespace resource.
- Account Owners and Global Admins automatically gain access to all Namespaces; you cannot specify Namespace access for these roles.
- Manage a specific user in one and only one `.tf` file to avoid overwriting permissions.
- To import a user, you need the User ID (currently not available in the Cloud UI). Fetch it with `tcld user list` or `data.temporalcloud_users`.

### Create

```hcl
resource "temporalcloud_user" "global_admin" {
  email          = "admin@example.com"
  account_access = "Admin"
}

resource "temporalcloud_user" "namespace_admin" {
  email          = "developer@example.com"
  account_access = "Developer"

  namespace_accesses = [{
    namespace_id = temporalcloud_namespace.namespace.id
    permission   = "Write"
  }]
}
```

`account_access` is case-insensitive. Allowed values: `owner` (import only), `admin`, `developer`, `read`, `financeadmin`, `none` (SCIM-managed).

### Import

```bash
terraform import temporalcloud_user.user 72360058153949edb2f1d47019c1e85f
```

---

## Service Account management

Resource: `temporalcloud_service_account`

Service Accounts use a `name` instead of `email`.

### Limitations (not identical to users)

- No Account Owner role for Service Accounts. `account_access` values: `admin`, `developer`, `read`, `financeadmin`, `metricsread`.
- Namespace access is managed on the Service Account resource (not the Namespace resource), same as users.
- Global Admins (`account_access = "admin"`) automatically gain access to all Namespaces; do not set `namespace_accesses` for them.
- Optional `namespace_scoped_access`: binds the SA to a single namespace (namespace assignment immutable after create; permission is mutable). Cannot combine with `account_access` / `namespace_accesses`.
- Manage a specific Service Account in one and only one `.tf` file.

---

## API Key management

Resource: `temporalcloud_apikey`

### Create

```hcl
resource "temporalcloud_apikey" "global_apikey" {
  display_name = "admin"
  owner_type   = "service-account"
  owner_id     = temporalcloud_service_account.global_service_account.id
  expiry_time  = "2024-11-01T00:00:00Z"
  disabled     = false
}
```

To access the API Key token, create an output:

```hcl
output "apikey_token" {
  value     = temporalcloud_apikey.global_apikey.token
  sensitive = true
}
```

Retrieve the token:

```bash
terraform output -json apikey_token
```

### Update

You can update `display_name`, `description`, and `disabled` in place. Changing `owner_id`, `owner_type`, or `expiry_time` forces resource replacement. Updating does not rotate the token.

### Import

API keys **cannot** be imported into Terraform. Once created, the API Key secret is not stored and cannot be retrieved. Create a new API Key using Terraform directly instead.

---

## Data sources

The provider supports many data sources. Prefer the [registry data sources list](https://registry.terraform.io/providers/temporalio/temporalcloud/latest/docs). Current set includes:

- `temporalcloud_regions`
- `temporalcloud_namespaces` / `temporalcloud_namespace`
- `temporalcloud_users` / `temporalcloud_user`
- `temporalcloud_service_accounts` / `temporalcloud_service_account`
- `temporalcloud_nexus_endpoints` / `temporalcloud_nexus_endpoint`
- `temporalcloud_connectivity_rule`
- `temporalcloud_account_audit_log_sink`
- `temporalcloud_scim_group`

### Regions

```hcl
data "temporalcloud_regions" "regions" {}

output "regions" {
  value = data.temporalcloud_regions.regions.regions
}
```

### Namespaces

The `temporalcloud_namespaces` data source provides access to available Namespaces in the account.

### Users

`temporalcloud_users` returns each user's `id` (useful for import when the Cloud UI does not show User IDs).

---

## Resources

- Terraform Registry: [registry.terraform.io/providers/temporalio/temporalcloud/latest](https://registry.terraform.io/providers/temporalio/temporalcloud/latest)
- GitHub repository: [github.com/temporalio/terraform-provider-temporalcloud](https://github.com/temporalio/terraform-provider-temporalcloud/tree/main)
