# R2 Configuration

Fetch the task's documentation before editing Wrangler configuration or bucket settings.

| Task | Current documentation |
|------|-----------------------|
| Create a bucket and bind it to a Worker | [Workers API setup](https://developers.cloudflare.com/r2/get-started/workers-api/index.md) |
| Choose local simulation or a remote bucket during development | [Supported bindings per development mode](https://developers.cloudflare.com/workers/local-development/bindings-per-env/index.md) and [local development](https://developers.cloudflare.com/workers/local-development/index.md) |
| Create S3 credentials and scope permissions | [R2 authentication](https://developers.cloudflare.com/r2/api/tokens/index.md) |
| Set the S3 endpoint and SDK region | [AWS SDK for JavaScript v3](https://developers.cloudflare.com/r2/examples/aws/aws-sdk-js-v3/index.md) |
| Choose placement hints or a jurisdiction | [Data location](https://developers.cloudflare.com/r2/reference/data-location/index.md) |
| Configure browser origins, methods, and headers | [CORS](https://developers.cloudflare.com/r2/buckets/cors/index.md) |
| Set expiration, storage transitions, or incomplete-upload cleanup | [Object lifecycles](https://developers.cloudflare.com/r2/buckets/object-lifecycles/index.md) |
| Choose or change storage classes | [Storage classes](https://developers.cloudflare.com/r2/buckets/storage-classes/index.md) and [pricing](https://developers.cloudflare.com/r2/pricing/index.md) |
| Send object events to a queue | [Event notifications](https://developers.cloudflare.com/r2/buckets/event-notifications/index.md) |
| Configure public access or a custom domain | [Public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/index.md) |
| Manage bucket settings with Wrangler | [R2 commands](https://developers.cloudflare.com/r2/reference/wrangler-commands/index.md) |

Choose the development bucket deliberately: a remote binding accesses real data. Scope S3 credentials to the required buckets and operations; Workers bindings use their own access mechanism. Review lifecycle prefixes and retention needs before applying deletion rules, and evaluate retrieval and minimum-storage charges before choosing a storage class.
