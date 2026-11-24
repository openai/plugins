# Cloudflare Containers

Use this reference for containerized applications on the Workers platform, including container-enabled Durable Objects, lifecycle management, and request routing.

## Choose the runtime

Use [Containers](https://developers.cloudflare.com/containers/index.md) for existing container images, custom runtimes, system dependencies, full filesystem access, or workloads needing additional CPU and memory. Use [Workers](https://developers.cloudflare.com/workers/index.md) when the application fits the Workers runtime without those requirements.

Containers are controlled through [Durable Objects](https://developers.cloudflare.com/durable-objects/index.md). An instance's identity does not make its filesystem persistent: design for restarts and store durable data outside the container disk. Read [Container lifecycle](https://developers.cloudflare.com/containers/concepts/architecture/index.md) and [Container interface](https://developers.cloudflare.com/containers/api/container-class/index.md) for the relationship between the process, its Durable Object, and persistent storage.

## Find the documentation for the task

Read the linked page before writing code or configuration; use its current API, examples, and constraints rather than reconstructing them from memory.

| Task | Start here |
| --- | --- |
| Create a project and deploy the first container | [Get started](https://developers.cloudflare.com/containers/get-started/index.md) |
| Configure images, bindings, instance sizes, and deployments | [Configuration](configuration.md) |
| Control startup, requests, lifecycle, and scheduling | [API](api.md) |
| Choose routing or connect other services | [Patterns](patterns.md) |
| Diagnose startup, persistence, capacity, or rollout issues | [Gotchas](gotchas.md) |

For additional topics, consult the [Containers documentation index](https://developers.cloudflare.com/containers/llms.txt).
