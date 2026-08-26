# Serverless Workers — Concepts

<!-- Sources: docs/encyclopedia/workers/serverless-workers.mdx, docs/evaluate/development-production-features/serverless-workers/index.mdx -->

## Release status

**AWS Lambda — Public Preview since July 30, 2026.** Open to all Temporal Cloud customers. There is no access request, no support ticket, and no manual toggle to enable: a customer selects "AWS Lambda (Public Preview)" as the compute provider in the UI and sets up their Worker Deployment directly. Never route a user to support to "get access" for Lambda.

AWS Lambda is the only compute provider this skill supports. Do not adapt the Lambda material to any other provider.

Public Preview is not General Availability. APIs are still evolving and may be subject to backwards-incompatible changes between versions — pin SDK and CLI versions for anything long-lived, and read the installed package's real API surface rather than writing from memory.

## What is a Serverless Worker?

A Serverless Worker is a Temporal Worker that runs on serverless compute instead of a long-lived process. <!-- docs/encyclopedia/workers/serverless-workers.mdx:43 -->
There is no always-on infrastructure to provision or scale. Temporal invokes the Worker when Tasks arrive on a Task Queue, and the Worker shuts down when the work is done. <!-- docs/encyclopedia/workers/serverless-workers.mdx:43-45 -->

A Serverless Worker uses the same Temporal SDKs as a traditional long-lived Worker. It registers Workflows and Activities the same way. The difference is in the lifecycle: instead of the Worker starting and polling continuously, Temporal invokes the Serverless Worker on demand, the Worker starts, processes available Tasks, and then shuts down. <!-- docs/encyclopedia/workers/serverless-workers.mdx:47-49 -->

Serverless Workers require Worker Versioning. Each Serverless Worker must be associated with a Worker Deployment Version that has a compute provider configured. <!-- docs/encyclopedia/workers/serverless-workers.mdx:51-52 -->

Each Workflow must have an `AutoUpgrade` or `Pinned` versioning behavior, set per-Workflow or as a Worker-level default. <!-- docs/encyclopedia/workers/serverless-workers.mdx:245 -->

## How Serverless invocation works

With long-lived Workers, the Worker process starts, connects to Temporal, and polls a Task Queue for work. Temporal does not need to know anything about the Worker's infrastructure. <!-- docs/encyclopedia/workers/serverless-workers.mdx:59-60 -->

With Serverless Workers, Temporal starts the Worker. <!-- docs/encyclopedia/workers/serverless-workers.mdx:62 -->

### Worker Controller Instance (WCI)

The Worker Controller Instance (WCI) is a system Workflow that scales Serverless Workers based on Task Queue conditions. <!-- docs/encyclopedia/workers/serverless-workers.mdx:66 -->
One WCI Workflow runs per Worker Deployment Version that has a compute provider configured. The WCI runs in the same Namespace as your Worker Deployment. <!-- docs/encyclopedia/workers/serverless-workers.mdx:67-68 -->

The WCI responds to two triggers: sync match failures and Task Queue backlog. When either trigger fires, the WCI produces a scaling action, such as invoking the configured compute provider (for example, calling AWS Lambda's `InvokeFunction` API) to start new Workers. <!-- docs/encyclopedia/workers/serverless-workers.mdx:70-72 -->

You can list WCI Workflows in your Namespace: <!-- docs/encyclopedia/workers/serverless-workers.mdx:75 -->

```bash
temporal workflow list \
  --namespace <NAMESPACE> \
  --query 'TemporalNamespaceDivision = "TemporalWorkerControllerInstance"'
```
<!-- docs/encyclopedia/workers/serverless-workers.mdx:77-81 -->

WCI Workflow IDs follow the pattern `temporal-sys-worker-controller-instance:<deployment-name>:<build-id>`. <!-- docs/encyclopedia/workers/serverless-workers.mdx:83 -->

You can inspect a WCI Workflow's history to see its recent Activity results: <!-- docs/encyclopedia/workers/serverless-workers.mdx:83-84 -->

```bash
temporal workflow show \
  --namespace <NAMESPACE> \
  --workflow-id 'temporal-sys-worker-controller-instance:<DEPLOYMENT_NAME>:<BUILD_ID>'
```
<!-- docs/encyclopedia/workers/serverless-workers.mdx:86-90 -->

### Invocation flow

The invocation flow works as follows: <!-- docs/encyclopedia/workers/serverless-workers.mdx:101 -->

1. A Task is submitted (for example, `StartWorkflow` or `ScheduleActivity`). <!-- docs/encyclopedia/workers/serverless-workers.mdx:103 -->
2. The Matching Service attempts to route the Task directly to an available Worker (a sync match). <!-- docs/encyclopedia/workers/serverless-workers.mdx:104-105 -->
3. If a Worker is available, the Task is routed to that Worker. <!-- docs/encyclopedia/workers/serverless-workers.mdx:106 -->
4. If no Worker is available (sync match fails), the Matching Service pushes a signal to the WCI, and the WCI invokes the configured compute provider. <!-- docs/encyclopedia/workers/serverless-workers.mdx:107-108 -->
5. The Serverless Worker starts, creates a Temporal Client, and begins polling the Task Queue. <!-- docs/encyclopedia/workers/serverless-workers.mdx:109 -->
6. The Worker processes available Tasks until it exits (see Worker lifecycle). <!-- docs/encyclopedia/workers/serverless-workers.mdx:110 -->

Each invocation is independent. The Worker creates a fresh client connection on every invocation. There is no connection reuse or shared state across invocations. <!-- docs/encyclopedia/workers/serverless-workers.mdx:112-113 -->

## Autoscaling

The WCI automatically scales Serverless Workers based on Task Queue signals. When Tasks arrive and no Worker is available, the WCI invokes new Workers. When the Tasks are done, Workers exit and scale to zero. <!-- docs/encyclopedia/workers/serverless-workers.mdx:117-118 -->

The WCI uses two signals to decide when to invoke new Workers: <!-- docs/encyclopedia/workers/serverless-workers.mdx:120 -->

### Sync match failure

When a Task is submitted, the Matching Service attempts to route it directly to an available Worker. If no Worker is available, the sync match fails, and the Matching Service pushes a signal to the WCI. The WCI then invokes a new Worker. This is the primary scaling path. <!-- docs/encyclopedia/workers/serverless-workers.mdx:124-126 -->

Because the Matching Service pushes match failures to the WCI as they happen rather than the WCI polling on a timer, latency stays low and scaling is responsive. <!-- docs/encyclopedia/workers/serverless-workers.mdx:126-128 -->

### Task Queue backlog

The WCI monitors Task Queue metadata to determine whether pending Tasks exist without enough Workers to process them. If there are Tasks on the queue and not enough Workers, the WCI invokes additional Workers. <!-- docs/encyclopedia/workers/serverless-workers.mdx:132-133 -->

## Scaling with long-lived Workers

Serverless Workers can share a Task Queue with long-lived Workers. Because Serverless Workers are only invoked on sync match failure, Serverless Workers only pick up Tasks that no long-lived Worker was available to handle. In practice, the Serverless Workers act as spillover capacity for the long-lived fleet. <!-- docs/encyclopedia/workers/serverless-workers.mdx:137-139 -->

**Warning:** If you configure Serverless and long-lived Workers on the same Task Queue, do not enable dynamic scaling on the long-lived Workers. The two groups cannot coordinate their scaling behavior. If both scale dynamically, the long-lived Workers may scale up to handle the same Tasks that Temporal is simultaneously invoking Serverless Workers for, leading to unnecessary invocations and unpredictable scaling. <!-- docs/encyclopedia/workers/serverless-workers.mdx:143-146 -->

## Worker lifecycle

A single Serverless Worker invocation has three phases: init, work, and shutdown. <!-- docs/encyclopedia/workers/serverless-workers.mdx:152 -->

### Init phase

The Worker initializes and establishes a client connection to Temporal. <!-- docs/encyclopedia/workers/serverless-workers.mdx:161 -->

### Work phase

The Worker polls the Task Queue and processes Tasks. <!-- docs/encyclopedia/workers/serverless-workers.mdx:163 -->

### Shutdown phase

The Worker stops polling, waits for in-flight Tasks to finish, and runs any shutdown hooks (for example, OpenTelemetry telemetry flushes). Shutdown begins before the invocation deadline so the Worker can exit cleanly before the compute provider forcibly terminates the execution environment. <!-- docs/encyclopedia/workers/serverless-workers.mdx:165-167 -->

### Tuning for long-running Activities

If your Worker handles long-running Activities, set these three values together: <!-- docs/encyclopedia/workers/serverless-workers.mdx:171 -->

- **Worker stop timeout > longest Activity runtime.** Gives in-flight Activities enough time to finish after polling stops. <!-- docs/encyclopedia/workers/serverless-workers.mdx:173-174 -->
- **Shutdown deadline buffer > Worker stop timeout + shutdown hook time.** Ensures the drain and any shutdown hooks complete before the compute provider terminates the environment. <!-- docs/encyclopedia/workers/serverless-workers.mdx:175-176 -->
- **Invocation deadline > longest Activity runtime + shutdown deadline buffer.** Set on the compute provider to give each invocation enough total runtime. <!-- docs/encyclopedia/workers/serverless-workers.mdx:177-178 -->

If your longest-running Activity runs longer than half the maximum invocation deadline, use Activity Heartbeats to record the state of the Activity execution so that the next retry can pick up where it left off. <!-- docs/encyclopedia/workers/serverless-workers.mdx:182-185 -->

Example: if your longest Activity runtime is 5 minutes, and your shutdown hooks take 3 seconds, set the Worker stop timeout to more than 5 minutes, and the shutdown deadline buffer to more than 303 seconds (5 minutes + 3 seconds). Set your invocation deadline to at least 10 minutes and 3 seconds. <!-- docs/encyclopedia/workers/serverless-workers.mdx:189-191 -->

The Worker stop timeout controls how long the Worker waits for in-flight Tasks to finish after it stops polling. The shutdown deadline buffer controls how much time before the invocation deadline the Worker stops polling for Tasks. <!-- docs/encyclopedia/workers/serverless-workers.mdx:193-194 -->

Raising only the shutdown deadline buffer makes the Worker stop polling earlier, but does not give in-flight Tasks any more time to complete. <!-- docs/encyclopedia/workers/serverless-workers.mdx:196-197 -->

Raising only the Worker stop timeout does not make the Worker stop polling earlier, which means the compute provider might terminate the Worker before the full stop timeout completes. <!-- docs/encyclopedia/workers/serverless-workers.mdx:199-201 -->

## Failure handling

Serverless Workers rely on Temporal's standard retry and timeout semantics to recover from failures. <!-- docs/encyclopedia/workers/serverless-workers.mdx:205-206 -->

### Worker crash

If a Worker invocation crashes (out of memory, unhandled exception, etc.): <!-- docs/encyclopedia/workers/serverless-workers.mdx:210-211 -->

- The Activity Timeout fires after the configured duration. <!-- docs/encyclopedia/workers/serverless-workers.mdx:213 -->
- Temporal retries the Activity on a different Worker invocation. <!-- docs/encyclopedia/workers/serverless-workers.mdx:214 -->
- No manual intervention is required. <!-- docs/encyclopedia/workers/serverless-workers.mdx:215 -->

### Provider concurrency limit

If the compute provider's concurrency limit is reached (for example, AWS Lambda account concurrency): <!-- docs/encyclopedia/workers/serverless-workers.mdx:219 -->

- Further invocations from the WCI fail. <!-- docs/encyclopedia/workers/serverless-workers.mdx:221 -->
- Tasks remain in the Task Queue backlog. No data loss occurs. <!-- docs/encyclopedia/workers/serverless-workers.mdx:222 -->
- Processing slows until concurrency frees up. <!-- docs/encyclopedia/workers/serverless-workers.mdx:223 -->

### Resource exhaustion across Activity slots

By default, a single Worker invocation may run multiple Activity slots. A crash or resource exhaustion in one Activity can affect other Activities running in the same invocation. <!-- docs/encyclopedia/workers/serverless-workers.mdx:227-229 -->

To isolate Activities from each other: <!-- docs/encyclopedia/workers/serverless-workers.mdx:231 -->

- Split Workflow and Activity Workers into separate compute functions. <!-- docs/encyclopedia/workers/serverless-workers.mdx:233 -->
- Set Activity slots to 1 per invocation. <!-- docs/encyclopedia/workers/serverless-workers.mdx:234 -->

With single-slot configuration, each Activity gets a dedicated execution environment. <!-- docs/encyclopedia/workers/serverless-workers.mdx:236 -->

## Constraints

<!-- docs/encyclopedia/workers/serverless-workers.mdx:240-245 -->

| Constraint | Detail |
|---|---|
| Activity duration | Must complete within the compute provider's invocation limit (minus shutdown deadline buffer). For AWS Lambda, the maximum is 15 minutes. |
| Workflow duration | No limit. Workflows of any duration work, regardless of the invocation timeout. A Workflow runs across as many invocations as needed. |
| Worker code | Same Temporal SDK Worker code, using the serverless Worker package for your SDK. |
| Versioning | Worker Versioning is required. Each Workflow must have an `AutoUpgrade` or `Pinned` behavior, set per-Workflow or as a Worker-level default. |

## Worker Versioning with Serverless Workers

Serverless Workers require Worker Versioning, and the compute provider must invoke a stable, immutable build for each Worker Deployment Version. With AWS Lambda, this means aligning two versioning systems: <!-- docs/encyclopedia/workers/serverless-workers.mdx:249-250 -->

- **Temporal Worker Deployment Versions** — identified by deployment name and Build ID. Each Workflow runs against a specific Worker Deployment Version (Pinned) or moves between them on routing changes (Auto-Upgrade). <!-- docs/encyclopedia/workers/serverless-workers.mdx:252-253 -->
- **AWS Lambda function versions** — immutable numbered snapshots of your Lambda function code (`1`, `2`, `3`, ...). <!-- docs/encyclopedia/workers/serverless-workers.mdx:254 -->

For production workloads, map each Worker Deployment Version to exactly one Lambda function version, and configure the compute provider with the qualified versioned ARN for that Lambda version (for example, `arn:aws:lambda:us-east-1:123:function:my-worker:5`). <!-- docs/encyclopedia/workers/serverless-workers.mdx:256-260 -->

For development or non-critical workloads, you can use an unqualified ARN to iterate without publishing a new Lambda function version each time. <!-- docs/encyclopedia/workers/serverless-workers.mdx:281-282 -->

**Caution:** An unqualified ARN (no version suffix) points at `$LATEST`, which changes on every redeploy. Without a versioned ARN, deploying replay-unsafe code causes non-determinism errors for in-flight Workflows, even for Workflows annotated as Pinned. <!-- docs/encyclopedia/workers/serverless-workers.mdx:284-290 -->

The choice of Pinned or Auto-Upgrade controls how Workflows move between Worker Deployment Versions in Temporal. It does not change how a Worker Deployment Version targets Lambda. Both behaviors expect a versioned ARN that points at one immutable Lambda function version. <!-- docs/encyclopedia/workers/serverless-workers.mdx:294-296 -->

| Versioning Behavior | With versioned Lambda ARN | Without versioned Lambda ARN |
|---|---|---|
| **Pinned** | Existing Workflows stay on their original Lambda function version until they complete. | Existing Workflows stay on their original Worker Deployment Version, but the underlying Lambda code has already changed since `$LATEST` updated at redeploy. The new code must be replay-compatible. |
| **Auto-Upgrade** | Existing Workflows move to the new Worker Deployment Version and its new Lambda function version at the next Workflow Task after you move the Current Version. | The Lambda redeploy already changed the code for all versions. Setting the Current Version only changes routing, not which code runs. |
<!-- docs/encyclopedia/workers/serverless-workers.mdx:299-302 -->

See `aws-lambda/versioning.md` for the step-by-step `aws lambda publish-version` workflow and `aws-lambda/setup.md` (Step 4) for how to configure the compute provider with a versioned ARN.

## Compute providers

A compute provider is the configuration that tells Temporal how to invoke a Serverless Worker. The compute provider is set on a Worker Deployment Version and specifies the provider type, the invocation target, and the credentials Temporal needs to trigger the invocation. <!-- docs/encyclopedia/workers/serverless-workers.mdx:310-312 -->

For example, an AWS Lambda compute provider includes the Lambda function ARN and the IAM role that Temporal assumes to invoke the function. <!-- docs/encyclopedia/workers/serverless-workers.mdx:314-315 -->

Compute providers are only needed for Serverless Workers. Traditional long-lived Workers do not require a compute provider because the Worker process lifecycle is not managed by the Temporal server. <!-- docs/encyclopedia/workers/serverless-workers.mdx:317-318 -->

### Supported providers

<!-- docs/encyclopedia/workers/serverless-workers.mdx:322-324 -->

| Provider | Description |
|---|---|
| AWS Lambda | Temporal assumes an IAM role in your AWS account to invoke a Lambda function. |

## Why use Serverless Workers?

<!-- docs/evaluate/development-production-features/serverless-workers/index.mdx:34-71 -->

- **Reduce operational overhead.** No always-on infrastructure to manage and no autoscaling policies to tune. Temporal and the compute provider handle invocation and scaling.
- **Get started faster.** Deploying a Worker is as simple as deploying a function. No Kubernetes, container orchestration, or scaling strategy required.
- **Scale automatically.** The compute provider handles scaling natively. When traffic drops, instances scale down. When there is no work, there is no compute running.
- **Pay only for what you use.** Workers run only when Tasks are available. For low or intermittent volume workloads, this pay-per-invocation model can significantly reduce compute costs.

## When to use Serverless Workers

<!-- docs/evaluate/development-production-features/serverless-workers/index.mdx:75-86 -->

Good fit when:

- Workloads are bursty or event-driven (order processing, notifications, webhook handlers).
- Traffic is low or intermittent.
- You want a simpler getting-started path.
- Your organization has standardized on serverless.
- You serve multiple tenants with infrequent workloads.

May not be ideal when:

<!-- docs/evaluate/development-production-features/serverless-workers/index.mdx:88-97 -->

- Activities are long-running and cannot be interrupted. AWS Lambda has a 15-minute execution limit. Activities that run longer and cannot be broken into smaller steps need a different hosting strategy or a provider with longer limits.
- Workloads require sustained high throughput. Long-lived Workers on dedicated compute may be more cost-effective and performant.
- You need persistent connections. Some features require a persistent connection between the Worker and Temporal, which serverless invocations do not maintain.

## How Serverless Workers compare to long-lived Workers

<!-- docs/evaluate/development-production-features/serverless-workers/index.mdx:99-105 -->

|                | Long-lived Worker | Serverless Worker |
|---|---|---|
| **Lifecycle** | Long-lived process that runs continuously. | Invoked on demand. Starts and stops per invocation. |
| **Scaling** | You manage scaling (Kubernetes HPA, instance count, etc.). | Temporal invokes additional instances as needed, within the compute provider's concurrency limits. |
| **Connection** | Persistent connection to Temporal. | Fresh connection on each invocation. |
