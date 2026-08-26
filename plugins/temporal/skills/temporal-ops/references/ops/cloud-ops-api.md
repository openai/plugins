# Cloud Ops API

The Cloud Ops API provides programmatic management of Temporal Cloud control plane resources, including Namespaces, Users, Service Accounts, API Keys, and others. The Temporal Cloud Terraform Provider, `tcld` CLI, and Web UI all use the Cloud Ops API.

**Stage:** Public Preview.

---

## Endpoints

| Interface | URL | Notes |
|---|---|---|
| HTTP | `https://saas-api.tmprl.cloud` | Control-plane HTTP API |
| gRPC | `saas-api.tmprl.cloud:443` | Port 443 for gRPC connections |

PrivateLink / Private Service Connect: configure private DNS for `saas-api.tmprl.cloud` (and `web.saas-api.tmprl.cloud` for the Web UI).

- HTTP API docs: [saas-api.tmprl.cloud/docs/httpapi.html](https://saas-api.tmprl.cloud/docs/httpapi.html#description/introduction)
- gRPC API source: [github.com/temporalio/cloud-api](https://github.com/temporalio/cloud-api/tree/main)
- gRPC docs on Buf: [buf.build/temporalio/cloud-api](https://buf.build/temporalio/cloud-api/docs/main:temporal.api.cloud.cloudservice.v1#temporal.api.cloud.cloudservice.v1.CloudService)

The HTTP API supports the same operations as the gRPC API, but is usable via standard HTTP methods. It does **not** allow interaction with individual Workflows or Activities via HTTP.

---

## Prerequisites

- A Temporal Cloud User or Service Account
- API Key for authentication (owned by that User or Service Account)

Required roles/permissions vary by RPC (Account Owner, Global Admin, Developer, Finance Admin, Namespace roles, or Custom Roles). Do not assume Account Admin for every operation.

---

## API version header

Use the `temporal-cloud-api-version` header to select an API version. The backend uses this version to safely mutate resources. Current version: [github.com/temporalio/cloud-api/blob/main/VERSION](https://github.com/temporalio/cloud-api/blob/main/VERSION).

### gRPC

gRPC clients must send a `temporal-cloud-api-version` header on every request.

### HTTP

For HTTP clients, the version header is optional. If omitted, the HTTP gateway defaults it to the latest API version. This supports simple `curl` usage without looking up a version first.

For production HTTP automation, still pin an explicit version so behavior does not change when the gateway’s latest version advances.

---

## Go SDK

For Go developers, use the [Go SDK](https://github.com/temporalio/cloud-sdk-go). Module path is `go.temporal.io/cloud-sdk`. SDK is under active development; pin a version.

Install:

```go
go get go.temporal.io/cloud-sdk@latest
```

Import:

```go
import (
    "go.temporal.io/cloud-sdk/cloudclient"
)
```

Go samples: [github.com/temporalio/cloud-samples-go](https://github.com/temporalio/cloud-samples-go)
Cloud Ops API client setup: [client/api/client.go](https://github.com/temporalio/cloud-samples-go/blob/main/client/api/client.go)

---

## Compiling protobuf (non-Go languages)

For languages other than Go, download the gRPC protobufs from the [Cloud Ops API repository](https://github.com/temporalio/cloud-api/tree/main/temporal/api/cloud) and compile them manually. Prefer [Buf](https://buf.build/temporalio/cloud-api) when possible.

Example using Python (from the `cloud-api` repository root; protos live under `temporal/`):

```bash
git clone https://github.com/temporalio/cloud-api.git
cd cloud-api
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  $(find temporal -name '*.proto')
```

For operation specifics, refer to `cloudservice/v1/request_response.proto` for gRPC messages and `cloudservice/v1/service.proto` for gRPC services.

---

## Use cases

Common reasons to use the Cloud Ops API:

- Provision Namespaces per environment or tenant via pipelines.
- Bootstrap new projects by creating users, assigning roles, and creating Namespaces via custom scripts.
- Rotate service account keys on a schedule with a job.
- Audit and report access across orgs with scheduled HTTP requests.

---

## Rate limits

| Scope | Limit |
|---|---|
| Account-level total | 160 RPS |
| Per user | 40 RPS |
| Per service account | 80 RPS |
| Concurrent long-running mutating ops | 10 (default; subset of create/update/delete RPCs) |

Rate limits are enforced across all Temporal Cloud control plane operations (tcld, UI, Cloud Ops API).

Multiple clients used by the same identity (user or service account) share the same rate limit.

Authentication method (SSO, API keys) does not affect rate limiting.

### Requesting limit increases

If your use case requires higher rate limits, submit a support ticket. Provide your current usage patterns, the specific limits you need increased, and a description of your use case.

---

## Connection setup

- gRPC: `saas-api.tmprl.cloud:443`.
- HTTP: `https://saas-api.tmprl.cloud`.
- Establish a secure connection. See the [Cloud Ops API client setup in Go](https://github.com/temporalio/cloud-samples-go/blob/main/client/api/client.go).
