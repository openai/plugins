# Performance Bottlenecks

Diagnose performance bottlenecks in Temporal Workers and Clients using SDK metrics. This reference covers key latency metrics, root causes, and diagnostic steps.

---

## Task processing metrics

### `temporal_workflow_task_schedule_to_start_latency` spike

Time between when a Workflow Task is scheduled (enqueued) and when it is picked up by a Worker. P95 higher than one second is a concern.

Potential causes:

- **Insufficient Worker capacity:** Not enough Workers or overloaded Workers cannot pick up Tasks quickly enough.
- **Worker configuration issues:** Too few pollers or Task slots.
- **High Workflow lock latency:** Many updates to a single execution cause lock contention. Reduce the rate of Signals.
- **Network latency:** Workers in a different region from the Temporal cluster, or large payload sizes.

Diagnostic steps:

1. Check Worker CPU and memory usage.
2. Review Worker configuration (number of pollers, Task slots, etc.).
3. Look for spikes in Workflow or Activity starts.
4. Ensure Workers are in the same region as the Temporal cluster.

### `temporal_activity_schedule_to_start_latency` spike

Time between when an Activity Task is scheduled and when it is picked up by a Worker. P95 higher than one second is a concern.

Potential causes:

- **Insufficient Worker capacity.**
- **Worker configuration issues:** Too few pollers or Task slots.
- **Task Queue configuration:** `TaskQueueActivitiesPerSecond` set too low.
- **Network latency.**

Diagnostic steps:

1. Check Worker CPU and memory usage.
2. Review Worker configuration.
3. Look for spikes in Workflow or Activity starts.
4. Ensure Workers are in the same region.

### `temporal_workflow_endtoend_latency` spike

Total Workflow Execution time from Schedule to closure for a single Workflow Run. Normal ranges depend on the use case.

Potential causes:

- **Complex Workflows:** Many Activities or slow Activity execution.
- **Workflow and Activity retries:** Frequent failures with retry delays.
- **Worker capacity and configuration.**
- **External dependencies:** Slow databases, APIs, or services.
- **Network latency.**

Diagnostic steps:

1. Review Workflow and Activity designs for efficiency.
2. Monitor Worker capacity (CPU, memory).
3. Monitor external dependencies.
4. Ensure Workers are co-located with the Temporal cluster.

### High `temporal_workflow_task_execution_latency`

Time taken by a Worker to execute a Workflow Task. The SDK raises a "Deadlock detected during Workflow run" error or TMPRL1101 when a Workflow Task takes more than one or two seconds.

Potential causes:

- **CPU-intensive work in Workflow Task.**
- **Slow Local Activities** (execution time included in the Workflow Task).
- **Slow Workflow replay** (see `workflow_task_replay_latency`).
- **Worker resource constraints:** High CPU usage on Worker pods.
- **Infinite loops or blocking calls in Workflow code.**
- **Slow data conversion:** Custom Data Converter taking too long.

Diagnostic steps:

1. Monitor Worker CPU and memory utilization.
2. Ensure Workers have adequate resources and scaling.
3. Run Workflow code in a profiler using a replayer.
4. Review Workflow code for optimizations or blocking operations.
5. For Data Converter: disable deadlock detection (Go: `workflow.DataConverterWithoutDeadlockDetection`; Java: `WorkflowUnsafe.deadlockDetectorOff`). This removes the error but does not reduce latency.

### High `workflow_task_replay_latency`

Time to replay a Workflow Task by re-executing the Workflow code from the beginning using the recorded Event History. High if it exceeds a few milliseconds.

Potential causes:

- **Large Event Histories.**
- **Slow Data Converters** (especially encryption or external services).
- **Large payloads** in Activities or Signals.
- **Complex Workflow logic** (many concurrent child Workflows or Activities).
- **Frequent cache evictions** (memory constraints or frequent restarts).
- **Worker resource constraints.**

Diagnostic steps:

1. Monitor `temporal_workflow_task_replay_latency`.
2. Analyze Workflow History size; consider Continue-As-New for long-running Workflows.
3. Optimize Data Converters.
4. Review payload sizes.
5. Profile Workflow code.
6. Tune Worker cache size and eviction policies.

### `temporal_activity_execution_latency` spike

Time from when a Worker starts processing an Activity Task until it reports completion or failure.

Potential causes:

- **Activity implementation:** Time-consuming operations or slow external API calls.
- **External dependencies:** Shared external resources causing contention.
- **Worker resource constraints.**
- **Network latency** between Workers and external services.

Diagnostic steps:

1. Monitor `activity_execution_latency` (filter by Activity type and Task Queue).
2. Optimize Activity implementation.
3. Check Worker CPU and memory.
4. Check Worker configuration: `(Max)ConcurrentActivityExecutionSize` and `(Max)WorkerActivitiesPerSecond`.

---

## Task slot depletion

### `temporal_worker_task_slots_available{worker_type="WorkflowWorker"}` at zero

Available slots for executing Workflow Tasks on a Worker.

Potential causes:

- **High Workflow Task load** exceeding concurrent capacity.
- **Worker configuration:** `MaxConcurrentWorkflowTaskExecutionSize` set too low.
- **High `temporal_workflow_task_execution_latency`** and `workflow_task_replay_latency`.

Resolution:

1. Monitor Worker CPU and Memory while increasing `(Max)ConcurrentWorkflowTaskExecutionSize`.
2. Scale Workers vertically (CPU, Memory) and horizontally (more instances).

### `temporal_worker_task_slots_available{worker_type="ActivityWorker"}` at zero

Available slots for executing Activity Tasks on a Worker.

Potential causes:

- **Blocked Activities and Zombie Activities:** Activities blocked on downstream services or infinite loops. Zombie Activities occur when an Activity times out (`StartToClose` or `HeartbeatTimeout`) but continues running, occupying slots as retries occur.
- **Resource utilization:** High CPU or memory causing Activities to block.

Resolution:

1. Monitor Worker CPU and Memory while increasing `(Max)ConcurrentActivityExecutionSize`.
2. Add client-side timeout to downstream API clients.
3. Review Task code to ensure completion within reasonable time.

---

## Network request metrics

### High `temporal_long_request_failure`

Counts failed RPC long poll requests for `PollWorkflowTaskQueue`, `PollActivityTaskQueue`, and `GetWorkflowExecutionHistory`.

Potential causes:

- **Network issues** between Client and Server.
- **Rate limiting** (`ResourceExhausted` status code).
- **Server errors.**

Diagnostic steps:

1. Check the `operation` and `status`/`code` tag.
2. For `ResourceExhausted`, review rate limits.
3. Check the network connection.

### High `temporal_request_failure_total`

Counts total failed RPC requests.

Potential causes:

- **Network issues.**
- **Client errors** (misconfiguration, resource exhaustion).
- **Operation errors** (acting on a closed Workflow past retention time).
- **Rate limiting** (`ResourceExhausted` status code).
- **Request size limit** (blob size limit of 2 MB).
- **Server errors.**

Diagnostic steps:

1. Check the `status`/`code` tag.
2. Check the `operation` tag.
3. Monitor Server and Client logs.
4. Check the network connection.

### High `temporal_request_latency`

Latency of gRPC requests made by the Temporal Client.

Potential causes:

- **Network latency** (distance, conditions).
- **Network transfer time** (large payloads).
- **Resource exhaustion** (CPU, memory on client or server).
- **Client configuration** (thread pool sizes, memory constraints).
- **Server load.**

Diagnostic steps:

1. Monitor `temporal_request_latency` for spike timing and location.
2. Check the network connection.
3. Monitor resource usage on Client and Server.
4. Review Client configuration.
5. For Temporal Cloud, check `service-latency` metric and contact Support.

---

## Caching metrics

### `temporal_sticky_cache_size`

Number of Workflow executions cached in a Worker's memory. Sticky cache keeps Workflow state in memory, reducing the need to replay from Event History.

Monitor alongside Worker memory usage. A sudden increase correlates with increased memory consumption.

### `temporal_sticky_cache_hit_total` and `temporal_sticky_cache_miss_total`

A "hit" means the Worker found the Workflow in its cache; a "miss" means the Worker must fetch the Event History and replay. High hit rate with low miss rate indicates efficient scheduling.

### `temporal_sticky_cache_total_forced_eviction_total`

Counts Workflow Executions forcibly evicted from the sticky cache (cache was full). A high eviction rate may indicate the cache size is too small; increase `WorkflowCacheSize` if resources allow.

---

## Sibling skill pointers

- For detailed Worker tuning recommendations (slot counts, poller counts, cache sizes), see the worker tuning skill (`skill-temporal-workertuning`).
- For metrics collection and dashboard setup, see the observability skill (planned: `skill-temporal-observability`).
