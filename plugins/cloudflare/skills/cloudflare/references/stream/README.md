# Cloudflare Stream

Use Stream for on-demand video upload and playback or live broadcasting. Start with the application's upload source, player, and access requirements, then read the corresponding documentation before writing code.

## Choose a Workflow

| Task | Read |
|---|---|
| Let users upload without exposing an API token | [Direct creator uploads](https://developers.cloudflare.com/stream/uploading-videos/direct-creator-uploads/index.md) |
| Choose server upload, resumable upload, or import from a URL | [Upload methods and supported formats](https://developers.cloudflare.com/stream/uploading-videos/index.md) |
| Embed playback or integrate an existing player | [Stream Player](https://developers.cloudflare.com/stream/viewing-videos/using-the-stream-player/index.md) or [HLS/DASH players](https://developers.cloudflare.com/stream/viewing-videos/using-own-player/index.md) |
| Restrict viewing to authorized users or embedding origins | [Secure your Stream](https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/index.md) |
| Broadcast live, replay recordings, or simulcast | [Live workflow routing](./api-live.md) |
| Check usage, costs, or upload constraints | [Analytics](https://developers.cloudflare.com/stream/getting-analytics/index.md), [pricing](https://developers.cloudflare.com/stream/pricing/index.md), and [upload requirements](https://developers.cloudflare.com/stream/uploading-videos/index.md) |

## In This Reference

- [configuration.md](./configuration.md): project setup and access decisions.
- [api.md](./api.md): upload, playback, editing, and library operations.
- [api-live.md](./api-live.md): live inputs, outputs, recording, and WebRTC.
- [patterns.md](./patterns.md): application workflow decisions.
- [gotchas.md](./gotchas.md): troubleshooting routes.
