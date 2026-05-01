---
description: Implement a Zoom meeting bot, recorder, or real-time media workflow in the current codebase.
---

# Build Zoom Bot

Use this command when the repo needs to join meetings programmatically, capture media, process transcripts, or automate meeting-time behavior.

## Preflight

1. Inspect the codebase for existing bot, worker, Meeting SDK, RTMS, or media-processing code.
2. Identify whether the bot is joining meetings, consuming live media, processing recordings, or combining multiple paths.
3. Confirm the execution environment and deployment model for the bot runtime.
4. Check for required credentials, meeting join inputs, and media dependencies without printing secrets.

## Plan

Before making changes:

- state the bot goal and the Zoom surfaces involved
- list the files that will be changed
- state the auth path, runtime responsibilities, and media or transcript outputs
- state how the first working bot path will be verified

## Commands

1. Add or correct the bot entry path, meeting join or attach flow, and downstream processing pipeline.
2. Keep the first pass narrow: one working automation path before optional orchestration or analytics layers.
3. Add the minimal server, worker, or scheduler wiring required for the workflow.
4. Reuse existing logging, queueing, and secrets patterns where possible.
5. Do not claim recording or transcript automation works until the path is checked end to end.

## Verification

1. Re-read the bot runtime, auth helpers, and processing code that changed.
2. Run local build, tests, or static validation where available.
3. Verify the join pipeline, media handling assumptions, or downstream artifact path.
4. State any remaining blocker such as runtime environment constraints, account requirements, or missing meeting inputs.

## Summary

```text
## Result
- Action: implemented or updated a Zoom bot workflow
- Status: success | partial | failed
- Details: runtime, files changed, auth path, verification run
```

## Next Steps

- Test with a real meeting in a controlled environment.
- Add storage, analytics, or downstream integrations only after the base bot loop works.
- If the requirement is post-meeting retrieval rather than live participation, consider REST APIs or recording workflows instead.
