# Stream Configuration

Inspect the existing runtime, API client or binding, authentication layer, player, and secret storage before adding Stream. Choose upload and viewing permissions from the application's requirements.

| Task | Read |
|---|---|
| Configure Stream in a Worker and use its binding | [Stream binding setup](https://developers.cloudflare.com/stream/manage-video-library/bindings/index.md#setup) |
| Set creator upload constraints and metadata | [Direct creator uploads](https://developers.cloudflare.com/stream/uploading-videos/direct-creator-uploads/index.md) |
| Choose a token endpoint, Worker binding, or signing key | [Token-generation choices](https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/index.md#three-ways-to-generate-signed-tokens) |
| Require private playback or apply token restrictions | [Secure your Stream](https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/index.md) |
| Restrict embedding origins | [Allowed origins](https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/index.md#allowed-origins) |
| Configure processing notifications and their secret | [Video webhooks](https://developers.cloudflare.com/stream/manage-video-library/using-webhooks/index.md) |
| Configure live recording or external destinations | [Live inputs](https://developers.cloudflare.com/stream/stream-live/start-stream-live/index.md) and [simulcasting](https://developers.cloudflare.com/stream/stream-live/simulcasting/index.md) |
| Choose player configuration or framework integration | [Stream Player](https://developers.cloudflare.com/stream/viewing-videos/using-the-stream-player/index.md) |

Use the project's server-side secret handling for API tokens, signing keys, and webhook secrets. Identify the authorization check that permits issuing an upload URL or playback token; Stream configuration alone does not define the application's user entitlements.

See [api.md](./api.md), [api-live.md](./api-live.md), and [gotchas.md](./gotchas.md).
