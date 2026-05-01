---
description: Implement a Zoom Team Chat integration or chatbot flow with the right auth, eventing, and message handling.
---

# Build Zoom Team Chat App

Use this command when the repo should send, receive, or automate Zoom Team Chat messages, cards, commands, or chatbot interactions.

## Preflight

1. Inspect the codebase for existing chat app routes, OAuth handling, webhook handlers, and message templates.
2. Identify whether the workflow is user-scoped messaging, chatbot behavior, slash-command handling, or notifications.
3. Confirm the runtime that will own incoming events and outgoing message calls.
4. Check for the required auth and event configuration without printing secrets.

## Plan

Before making changes:

- state the Team Chat workflow being implemented
- list the files that will be changed
- state the auth path, inbound event path, and outbound message path
- state how the message flow will be verified

## Commands

1. Add or correct Team Chat auth, event handlers, and outbound message logic.
2. Keep the implementation aligned with the repo’s existing event and route patterns.
3. Add the minimum message formatting or card logic required for a useful first pass.
4. Keep secrets and user tokens out of output and logs.
5. Separate chat event handling from unrelated webhook logic where possible.

## Verification

1. Re-read the event handlers, auth code, and message formatting logic that changed.
2. Run local build or tests where available.
3. Verify the inbound and outbound message path shape.
4. State any remaining blocker such as missing app configuration, event subscription, or scope gap.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Team Chat workflow
- Status: success | partial | failed
- Details: files changed, auth path, event path, verification run
```

## Next Steps

- Send one real message flow through the app.
- Add richer cards or commands only after the base message path works.
- If webhook delivery fails, run `/debug-zoom-webhook`.
