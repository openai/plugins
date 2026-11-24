# Workflow APIs

Fetch the documentation for the operation before writing code; use its current signatures and serialization rules.

| Task | Documentation |
| --- | --- |
| Implement steps; create, batch, inspect, pause, resume, restart, or terminate instances; check parameter and return types | [Workers API](https://developers.cloudflare.com/workflows/build/workers-api/index.md) |
| Access a step's name, occurrence, retry attempt, and resolved configuration | [Step context](https://developers.cloudflare.com/workflows/build/step-context/index.md) |
| Configure retries, backoff, timeouts, non-retryable failures, or relative/absolute sleeps | [Sleeping and retrying](https://developers.cloudflare.com/workflows/build/sleeping-and-retrying/index.md) |
| Pass initial parameters, wait for an external event, or send an event to an instance | [Events and parameters](https://developers.cloudflare.com/workflows/build/events-and-parameters/index.md) |
| Start instances from a Worker or another Workflow, or schedule execution | [Trigger Workflows](https://developers.cloudflare.com/workflows/build/trigger-workflows/index.md) |
| Trigger and manage instances from the command line | [Wrangler commands](https://developers.cloudflare.com/workflows/reference/wrangler-commands/index.md) |
| Manage Workflows over HTTP, including authentication and request bodies | [Workflows REST API](https://developers.cloudflare.com/api/resources/workflows/methods/list/index.md) |

Decide whether input is available at creation or must arrive later as an event. Starting a child instance does not establish that it has completed; choose how the parent will observe completion. Check current instance ID retention and creation semantics before designing duplicate-trigger handling.

See [configuration.md](./configuration.md) and [patterns.md](./patterns.md).
