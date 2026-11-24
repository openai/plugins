# R2 Patterns & Best Practices

Choose the access and delivery model, then fetch the implementation guide.

| Task | Current documentation |
|------|-----------------------|
| Stream object downloads or accept uploads through a Worker | [Use R2 from Workers](https://developers.cloudflare.com/r2/api/workers/workers-api-usage/index.md) |
| Add conditional reads/writes, range handling, checksums, or batch deletion | [Workers API reference](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/index.md) |
| Upload large files with multipart state tracked by the client | [Multipart Worker and client example](https://developers.cloudflare.com/r2/api/workers/workers-multipart-usage/index.md) |
| Upload directly from a browser or share a temporary download | [Presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/index.md) and [CORS](https://developers.cloudflare.com/r2/buckets/cors/index.md) |
| Cache responses served by a Worker | [Cache API example](https://developers.cloudflare.com/r2/examples/cache-api/index.md) |
| Deliver public objects through a custom domain or evaluate r2.dev | [Public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/index.md) |
| Process object changes asynchronously | [Event notifications](https://developers.cloudflare.com/r2/buckets/event-notifications/index.md) and [Queues](../queues/) |
| Expire objects or transition storage classes | [Object lifecycles](https://developers.cloudflare.com/r2/buckets/object-lifecycles/index.md) and [storage classes](https://developers.cloudflare.com/r2/buckets/storage-classes/index.md) |

Authorize the caller for the selected object key and operation before exposing a Worker endpoint or issuing a presigned URL. A key-format check alone does not establish access rights. Set the intended expiry and signed request constraints for temporary access; configure browser CORS separately.

Keep private responses out of shared public caches. Choose cache keys and invalidation around the application's access model, and check [R2 consistency and caching behavior](https://developers.cloudflare.com/r2/reference/consistency/index.md) when objects can change. For multipart uploads, plan for failed parts, completion, and cleanup using the linked guide.
