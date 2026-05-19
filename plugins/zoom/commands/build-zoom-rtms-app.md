---
description: Implement a Zoom RTMS workflow for live media, transcript, or event-stream processing with the right stream lifecycle and backend handling.
---

# Build Zoom RTMS App

Use this command when the repo needs Zoom RTMS for live meeting or contact-center media streams, transcript processing, or backend event-stream consumption.

## Preflight

1. Inspect the codebase for existing RTMS, WebSocket, bot, worker, or stream-processing code.
2. Confirm the use case actually belongs on RTMS rather than a visible Meeting SDK bot or a post-meeting retrieval workflow.
3. Identify the stream source: meeting media, transcript stream, contact-center voice stream, or another documented RTMS surface.
4. Confirm the owning backend runtime, downstream pipeline, and required credentials without printing secrets.

## Plan

Before making changes:

- state the RTMS source surface and the downstream processing goal
- list the files that will be created or edited
- state the auth path, stream lifecycle responsibilities, and output artifacts
- state how the first working RTMS path will be verified

## Commands

1. Add or correct the RTMS connection lifecycle: connect, validate, subscribe, heartbeat, reconnect, and shutdown.
2. Keep the implementation in the backend or worker layer that owns stream processing, not in an unrelated UI surface.
3. Add the minimum parsing and buffering needed for the requested media or transcript type.
4. Wire the stream output into the existing processing pipeline, queue, or storage layer using repo-native patterns.
5. Keep RTMS-specific concerns separate from visible participant-bot logic unless the workflow explicitly needs both.
6. Avoid claiming live stream support works until the connection lifecycle and payload handling path are both checked.

## Verification

1. Re-read the stream connection code, auth handling, and downstream processing code that changed.
2. Run local build or tests where available.
3. Verify the connection lifecycle and payload handling path are coherent for the intended media type.
4. State any remaining blocker such as missing account prerequisites, stream authorization, network reachability, or downstream decoder work.

## Summary

```text
## Result
- Action: implemented or updated a Zoom RTMS workflow
- Status: success | partial | failed
- Details: source surface, files changed, auth path, verification run
```

## Next Steps

- Test the RTMS path against a real stream source in a controlled environment.
- Add richer downstream AI, analytics, or storage steps only after the base stream loop works.
- If the workflow actually needs a visible participant or meeting controls, compare against `/build-zoom-bot` or Meeting SDK before expanding scope.
