---
description: Implement a Zoom Scribe transcription pipeline for uploaded or stored media with the right processing mode and callback flow.
---

# Build Zoom Scribe App

Use this command when the repo needs a Zoom Scribe transcription workflow for uploaded or stored media rather than live in-meeting media.

## Preflight

1. Inspect the codebase for existing ingestion, storage, queueing, webhook, or transcript-processing code.
2. Confirm the media source, expected latency, language requirements, and whether fast mode or batch mode fits the workflow.
3. Identify the runtime that will own Build-platform credentials, request submission, and callback or polling behavior.
4. Check for required credentials, storage paths, and callback endpoints without printing secrets.

## Plan

Before making changes:

- state the media source and chosen Scribe processing mode
- list the files that will be changed
- state the auth path, ingestion path, and transcript output destination
- state how the first transcription flow will be verified

## Commands

1. Add or correct the transcription request path in the backend or worker layer.
2. Keep Build-platform auth handling separate from transcript business logic.
3. Add the minimum ingest, submit, parse, and persist flow required for a working transcription pipeline.
4. If batch mode is used, wire the callback or job-status path explicitly.
5. Reuse existing queueing, storage, and observability patterns where possible.
6. Avoid presenting live meeting media workflows as Scribe if the use case really belongs on RTMS or a bot pipeline.

## Verification

1. Re-read the auth handling, submission path, and transcript parsing code after changes.
2. Run local build or tests where available.
3. Verify the chosen processing mode and transcript output path are coherent.
4. State any remaining blocker such as credential audience, media format, callback path, or size constraints.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Scribe transcription workflow
- Status: success | partial | failed
- Details: processing mode, files changed, auth path, verification run
```

## Next Steps

- Test the pipeline with one real media file in a controlled environment.
- Add retries, batching, or downstream AI processing only after the base path works.
- If the workflow needs live media instead of stored files, switch to `/build-zoom-rtms-app` or `/build-zoom-bot`.
