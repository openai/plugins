# Runway Video Generation in Web Apps

Use this reference when Runway is the chosen provider for a web app's video-generation feature. If the user only needs a video asset for a page, save the generated file with the app's assets; add a runtime API integration only when the app must generate videos for its users.

## Provider Setup

- Use Runway Dev's installed skills and documentation tools for current integration guidance when available. Otherwise use the official API documentation below. Plugin sign-in does not configure credentials for the deployed app.
- Keep `RUNWAYML_API_SECRET` in server-side environment configuration or a secret manager. Use the official `@runwayml/sdk` on the server; never put the secret in browser code, public environment variables, logs, or committed files.
- Check current models and their supported inputs, duration, aspect ratios, and cost before choosing parameters. Honor the user's provider choice and generation budget.

## Minimal Integration

1. **Create a task on the server.** Authenticate the app user, validate the prompt and any uploaded media, and call the supported text-to-video or image-to-video endpoint. Save the returned task ID against that user and return promptly. Prevent duplicate submissions while generation is pending.
2. **Track the existing task.** Expose an app status endpoint that checks task ownership before calling `client.tasks.retrieve(taskId)`. Poll no more often than once every five seconds, with bounded retries/backoff. For a background worker, the SDK's `waitForTaskOutput` helper supports a timeout and abort signal; do not hold a short-lived HTTP request open for the entire generation.
3. **Handle real states.** Show queued/generating UI for `PENDING`, `THROTTLED`, and `RUNNING`; stop polling on `SUCCEEDED`, `FAILED`, or `CANCELLED`. Explain failures in user-facing language and offer an explicit retry. A polling timeout or closed tab does not cancel the generation: keep its task ID so the app can resume tracking it instead of creating another paid task.
4. **Persist the output.** On success, download the returned video into the app's own durable storage and save that URL. Runway output URLs expire; do not use them as permanent playback URLs. If saving fails, retry retrieval/storage for the existing task instead of regenerating the video.
5. **Verify playback.** Use video controls, inline playback, and a poster or loading state. Check mobile sizing, loading failures, and actual play/pause/seek behavior; do not substitute an animated placeholder for a generated result.

## Verification

Exercise pending, success, failure, cancellation, timeout/resume, and storage-failure paths with mocks before a live smoke test. Verify that one user cannot retrieve another user's task and that no API secret enters the client bundle. State whether live generation was tested or only mocked.

## Official References

- [Runway API documentation](https://docs.dev.runwayml.com/)
- [Server-side TypeScript SDK](https://github.com/runwayml/sdk-node)
- [Task statuses and output retention](https://github.com/runwayml/sdk-node/blob/main/src/resources/tasks.ts)
- [SDK polling helpers](https://github.com/runwayml/sdk-node/blob/main/src/lib/polling.ts)
