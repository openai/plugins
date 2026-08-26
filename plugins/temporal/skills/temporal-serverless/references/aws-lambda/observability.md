# Observability for Serverless Workers

<!-- Sources:
  docs/develop/go/workers/serverless-workers/aws-lambda.mdx
  docs/develop/python/workers/serverless-workers/aws-lambda.mdx
  docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx
-->

## Overview

Each SDK provides an OpenTelemetry integration package with defaults configured for the AWS Distro for OpenTelemetry (ADOT) Lambda layer. When enabled, the Worker emits SDK metrics and distributed traces for Workflow and Activity executions. The ADOT Lambda layer collects this telemetry and can forward traces to AWS X-Ray and metrics to Amazon CloudWatch. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:129-131 -->

## Go SDK

### OTel package

Import: `otel "go.temporal.io/sdk/contrib/aws/lambdaworker/otel"` <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:145 -->

### OTel functions

- `otel.ApplyDefaults` — configures both metrics and tracing. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:157,172 -->
- `otel.ApplyMetrics` — configures metrics only. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:240 -->
- `otel.ApplyTracing` — configures tracing only. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:240 -->

Usage in the configure callback: <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:154-159 -->

```go
if err := otel.ApplyDefaults(opts, &opts.ClientOptions, otel.Options{}); err != nil {
    return err
}
```

By default, telemetry is sent to `localhost:4317`, which is the ADOT Lambda layer's default collector endpoint. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:173 -->

### ADOT layer setup (Go)

Attach the ADOT Collector layer to your Lambda function. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:175 -->
Go does not need a language-specific ADOT layer because the OTel SDK is compiled into the binary. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:177 -->

### Collector config env var (Go)

`OPENTELEMETRY_COLLECTOR_CONFIG_URI=/var/task/otel-collector-config.yaml` <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:226 -->

---

## Python SDK

### OTel package

Import: `from temporalio.contrib.aws.lambda_worker.otel import apply_defaults` <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:147 -->

To install with OTel support: `pip install temporalio[lambda-worker-otel]` <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:214 -->

### OTel functions

- `apply_defaults` — configures both metrics and tracing. <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:155,165 -->
- `build_metrics_telemetry_config` — configures metrics only. <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:232 -->
- `apply_tracing` — configures tracing only. <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:232 -->

Usage in the configure callback: <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:151-155 -->

```python
def configure(config: LambdaWorkerConfig) -> None:
    config.worker_config["task_queue"] = TASK_QUEUE
    config.worker_config["workflows"] = [SampleWorkflow]
    config.worker_config["activities"] = [hello_activity]
    apply_defaults(config)
```

By default, telemetry is sent to `localhost:4317`, which is the ADOT Lambda layer's default collector endpoint. <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:166 -->

### ADOT layer setup (Python)

Attach the ADOT Python Lambda layer to your Lambda function. The layer includes both auto-instrumentation and an OpenTelemetry Collector that receives telemetry on `localhost:4317` and forwards traces to AWS X-Ray and metrics to Amazon CloudWatch. <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:168-169 -->

### Collector config env var (Python)

`OPENTELEMETRY_COLLECTOR_CONFIG_FILE=/var/task/otel-collector-config.yaml` <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:218 -->

Note: Python uses `_FILE` while Go and TypeScript use `_URI`.

---

## TypeScript SDK

### OTel package

Import: `import { applyDefaults } from '@temporalio/lambda-worker/otel'` <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:138 -->

### OTel functions

- `applyDefaults` — registers Temporal SDK interceptors for tracing and configures the Core SDK to export metrics via OTLP. <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:148,153 -->
- `makeOtelPlugin` — returns a plugin for pre-bundling Workflow code that includes Workflow interceptor modules. <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:222,226 -->

Usage in the configure callback: <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:142-149 -->

```typescript
export const handler = runWorker({ deploymentName: 'sdk-demo', buildId: 'v1' }, (config) => {
  config.workerOptions.taskQueue = TASK_QUEUE;
  config.workerOptions.workflowBundle = {
    codePath: require.resolve('./workflow-bundle.js'),
  };
  config.workerOptions.activities = activities;
  applyDefaults(config);
});
```

By default, telemetry is sent to `localhost:4317`, which is the ADOT Lambda layer's default collector endpoint. <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:154 -->

### Pre-bundling with OTel

When pre-bundling Workflow code, pass the plugin from `makeOtelPlugin()` so that Workflow interceptor modules are included in the bundle: <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:222 -->

```typescript
import { bundleWorkflowCode } from '@temporalio/worker';
import { makeOtelPlugin } from '@temporalio/lambda-worker/otel';

const { plugin } = makeOtelPlugin();
const { code } = await bundleWorkflowCode({
  workflowsPath: require.resolve('./workflows'),
  plugins: [plugin],
});
```
<!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:224-233 -->

### ADOT layer setup (TypeScript)

Attach two ADOT Lambda layers: <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:156 -->

1. The ADOT JavaScript layer for Node.js-side auto-instrumentation and trace export. <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:158 -->
2. The ADOT Collector layer (`aws-otel-collector-amd64`) to run the OTel Collector as a Lambda extension, receiving telemetry via OTLP on `localhost:4317` and forwarding traces to X-Ray and metrics to CloudWatch. <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:159 -->

### Collector config env var (TypeScript)

`OPENTELEMETRY_COLLECTOR_CONFIG_URI=/var/task/otel-collector-config.yaml` <!-- docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:208 -->

---

## Common across all SDKs

### Custom Collector configuration required

The default ADOT Collector configuration does not route OpenTelemetry Protocol (OTLP) data to the traces pipeline. You must provide a custom Collector configuration that wires the OTLP receiver to both the traces and metrics pipelines. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:179-180 -->

Example `otel-collector-config.yaml` (bundle in your Lambda deployment package): <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:181 -->

```yaml
receivers:
    otlp:
        protocols:
            grpc:
                endpoint: "localhost:4317"
            http:
                endpoint: "localhost:4318"

exporters:
    debug:
    awsxray:
        region: us-west-2
    awsemf:
        namespace: TemporalWorkerMetrics
        log_group_name: /aws/lambda/<your-function-name>
        region: us-west-2
        dimension_rollup_option: NoDimensionRollup
        resource_to_telemetry_conversion:
            enabled: true

service:
    pipelines:
        traces:
            receivers: [otlp]
            exporters: [awsxray, debug]
        metrics:
            receivers: [otlp]
            exporters: [awsemf]
    telemetry:
        logs:
            level: debug
        metrics:
            address: localhost:8888
```
<!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:185-221 -->

### Enable X-Ray active tracing

```bash
aws lambda update-function-configuration \
  --function-name <your-function-name> \
  --tracing-config Mode=Active
```
<!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:230-234 -->

### Required IAM permissions

The Lambda execution role must have permissions to write to X-Ray and CloudWatch: <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:236 -->

- `xray:PutTraceSegments` <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:237 -->
- `xray:PutTelemetryRecords` <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:237 -->
- `cloudwatch:PutMetricData` <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:237 -->

Without these permissions, the Collector fails silently and no telemetry appears. <!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:238 -->

For Python, the `AWSXRayDaemonWriteAccess` managed policy can be attached instead. <!-- docs/develop/python/workers/serverless-workers/aws-lambda.mdx:229 -->

### Collector config env var summary

<!-- docs/develop/go/workers/serverless-workers/aws-lambda.mdx:226, docs/develop/python/workers/serverless-workers/aws-lambda.mdx:218, docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:208 -->

| SDK | Environment variable |
|---|---|
| Go | `OPENTELEMETRY_COLLECTOR_CONFIG_URI` |
| Python | `OPENTELEMETRY_COLLECTOR_CONFIG_FILE` |
| TypeScript | `OPENTELEMETRY_COLLECTOR_CONFIG_URI` |

### ADOT layer summary

| SDK | Layers needed |
|---|---|
| Go | ADOT Collector layer only (no language-specific layer; OTel SDK is compiled into the binary) |
| Python | ADOT Python Lambda layer (includes collector and auto-instrumentation) |
| TypeScript | ADOT JavaScript layer + ADOT Collector layer (`aws-otel-collector-amd64`) |

<!-- Go: docs/develop/go/workers/serverless-workers/aws-lambda.mdx:175-177 -->
<!-- Python: docs/develop/python/workers/serverless-workers/aws-lambda.mdx:168-169 -->
<!-- TypeScript: docs/develop/typescript/workers/serverless-workers/aws-lambda.mdx:156-159 -->
