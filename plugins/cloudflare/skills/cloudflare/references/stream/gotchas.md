# Stream Gotchas

Identify whether the failure occurs during upload, encoding, authorization, playback, or live ingestion before changing configuration. Read the linked requirements and error guidance for that stage.

| Symptom or check | Read |
|---|---|
| Unsupported file or upload constraint failure | [Supported formats and upload requirements](https://developers.cloudflare.com/stream/uploading-videos/index.md) |
| Large upload fails or restarts after interruption | [Resumable upload requirements](https://developers.cloudflare.com/stream/uploading-videos/resumable-uploads/index.md#requirements) |
| Stream cannot fetch an imported video | [Upload via link requirements](https://developers.cloudflare.com/stream/uploading-videos/upload-via-link/index.md) |
| Upload finished but video is not playable | [Upload progress tracking](https://developers.cloudflare.com/stream/uploading-videos/direct-creator-uploads/index.md#track-upload-progress) and [processing error codes](https://developers.cloudflare.com/stream/manage-video-library/using-webhooks/index.md#error-codes) |
| Private playback or embedding fails | [Signed tokens, restrictions, and allowed origins](https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/index.md) |
| Webhook signature verification fails | [Verify the raw body and signature](https://developers.cloudflare.com/stream/manage-video-library/using-webhooks/index.md#verify-webhook-authenticity) |
| A custom HLS/DASH player behaves incorrectly | [Own-player integration and manifest handling](https://developers.cloudflare.com/stream/viewing-videos/using-own-player/index.md) |
| Live stream will not connect or playback buffers | [Live troubleshooting](https://developers.cloudflare.com/stream/stream-live/troubleshooting/index.md) |
| Simulcast output does not behave as expected | [Output configuration and limits](https://developers.cloudflare.com/stream/stream-live/simulcasting/index.md) |
| Estimate storage or delivery costs | [Stream pricing](https://developers.cloudflare.com/stream/pricing/index.md) |

Check the actual response and current docs before adopting a retry policy or treating a video as ready. Keep credentials out of browser code and logs; use [configuration.md](./configuration.md) for access setup and [patterns.md](./patterns.md) for state decisions.
