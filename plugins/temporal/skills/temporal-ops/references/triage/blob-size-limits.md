# Blob Size Limits

Temporal enforces size limits on the data that passes between the Temporal Client, Workers, and the Temporal Service. There are two distinct limits, each producing different error messages and behaviors.

---

## Payload size limit (2 MB)

The Temporal Service enforces a size limit on individual payloads. This limit is **2 MB** on Temporal Cloud, and is configurable on self-hosted deployments with a default of 2 MB.

A payload represents the serialized binary data for the input and output of Workflows and Activities.

### Error messages

- `WORKFLOW_TASK_FAILED_CAUSE_PAYLOADS_TOO_LARGE`
- `[TMPRL1103] Attempted to upload payloads with size that exceeded the error limit.`
- `BadScheduleActivityAttributes: ScheduleActivityTaskCommandAttributes.Input exceeds size limit`
- `Complete result exceeds size limit`
- `CompleteWorkflowExecutionCommandAttributes.Result exceeds size limit`
- `WORKFLOW_TASK_FAILED_CAUSE_BAD_UPDATE_WORKFLOW_EXECUTION_MESSAGE`

### Error behavior by SDK

**Python SDK 1.23.0+:** The SDK fails the Workflow Task with cause `WORKFLOW_TASK_FAILED_CAUSE_PAYLOADS_TOO_LARGE`. The Workflow is not terminated and remains open, so you can deploy a fix and allow the Workflow to continue.

**All other SDK versions:** The behavior depends on whether the oversized payload is an input or a result:

- **Inputs (Workflow input, Activity input):** The Temporal Service rejects the command and terminates the Workflow. You need to resolve the issue and restart the Workflow.
- **Activity result:** The Temporal Service rejects the Activity completion and the Activity fails with an error.
- **Workflow result:** The Workflow gets stuck in a retry loop. The server rejects the `CompleteWorkflowExecution` command, and replay produces the same oversized result.

### How to resolve

1. **Claim check pattern** (recommended): Offload large payloads to an object store. Pass references to stored payloads within the Workflow instead of the actual data. Retrieve the payloads from the object store when needed.

   The claim check pattern is built into the SDKs as **External Storage**, currently in **Pre-release**. Or implement your own via a custom Payload Codec.

2. **Compression**: Use compression with a custom Payload Codec. This may address the immediate issue, but if payload sizes continue to grow, the problem can arise again.

---

## gRPC message size limit (4 MB)

All communication between the Temporal Client, Workers, and the Temporal Service uses gRPC, which enforces a **4 MB** limit on each request. This limit is **fixed at 4 MB on Temporal Cloud**. On self-hosted it is technically configurable, but raising it requires changes across multiple layers (gRPC server config, event history limits, and the underlying Postgres row-size limit), so the recommended path is to fix the workflow design rather than raise the limit.

A Workflow can hit this limit even when every individual payload is under 2 MB. Scheduling several Activities with moderate-sized inputs, or hundreds of Activities with tiny inputs in the same Workflow Task, can push the combined request past 4 MB. Activity results are also subject to this limit.

### Error messages

- `WORKFLOW_TASK_FAILED_CAUSE_GRPC_MESSAGE_TOO_LARGE`
- `ScheduleToCloseTimeout` (Activities only, see error behavior below)

### Error behavior by SDK

**Python SDK 1.23.0+:** The SDK fails the Workflow Task with cause `WORKFLOW_TASK_FAILED_CAUSE_PAYLOADS_TOO_LARGE`. The Workflow is not terminated and remains open. For Activities, the Activity fails with an explicit error instead of timing out silently.

**All other SDK versions:**

- **Workflow Tasks:** The Workflow gets stuck in a retry loop that is not visible in the Event History. The Worker sends all commands back to the Temporal Service; if the combined size exceeds 4 MB, the SDK catches the gRPC error and sends a failed Workflow Task response with cause `WORKFLOW_TASK_FAILED_CAUSE_GRPC_MESSAGE_TOO_LARGE`. Replay produces the same oversized request every time, so the Workflow never makes progress.
- **Activity Tasks:** The Activity gets stuck in a retry loop or exits with a `ScheduleToCloseTimeout`. The Activity executes successfully, but the Worker cannot deliver the oversized result over gRPC. The server never receives the completion, so it retries the Activity. Each retry completes but fails to deliver the result. The Activity retries until `ScheduleToCloseTimeout` expires. If no `ScheduleToCloseTimeout` is set, it retries indefinitely until the Workflow is manually terminated. The `ResourceExhausted` gRPC error only appears in Worker logs.

### How to resolve

1. **Break larger batches into smaller sizes:**
   - **Workflow-level batching:** Process Activities or Child Workflows in smaller batches. Iterate through each batch, waiting for completion before the next.
   - **Workflow Task-level batching:** Execute Activities in smaller batches within a single Workflow Task. Introduce brief pauses or sleeps between batches.

2. If the request is large because of payload sizes (not the number of commands), refer to the Payload size limit solutions above.

---

## Quick diagnostic table

| Symptom | Likely limit | Next step |
|---|---|---|
| `WORKFLOW_TASK_FAILED_CAUSE_PAYLOADS_TOO_LARGE` | Payload (2 MB) | Check individual payload sizes; implement claim check pattern |
| `WORKFLOW_TASK_FAILED_CAUSE_GRPC_MESSAGE_TOO_LARGE` | gRPC (4 MB) | Reduce batch size or number of concurrent commands per Workflow Task |
| Workflow stuck in invisible retry loop | gRPC (4 MB) on Workflow Task | Check Worker logs for `ResourceExhausted`; reduce batch size |
| Activity retries indefinitely with no visible error | gRPC (4 MB) on Activity result | Check Worker logs for `ResourceExhausted`; implement claim check for result |
| `ScheduleToCloseTimeout` on Activity that completes successfully | gRPC (4 MB) on Activity result | Check Worker logs for `ResourceExhausted`; reduce result size |
| `CompleteWorkflowExecutionCommandAttributes.Result exceeds size limit` | Payload (2 MB) on Workflow result | Reduce Workflow result size or use claim check pattern |

---

## Sibling skill pointers

- For implementing the claim check pattern or External Storage in SDK code, see the developer skill (`skill-temporal-developer`).
- For worker tuning to manage batch sizes and concurrency, see the worker tuning skill (`skill-temporal-workertuning`).
