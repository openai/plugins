---
description: Implement or correct a Zoom WebSocket event stream with connection lifecycle, auth handling, and reconnect behavior.
---

# Setup Zoom WebSockets

Use this command when the integration needs persistent Zoom event delivery instead of standard webhook callbacks.

## Preflight

1. Inspect the repository for existing WebSocket clients, event consumers, connection-state handling, and auth configuration.
2. Confirm WebSockets are justified by latency, delivery model, firewall constraints, or connection semantics.
3. Identify the event types and app configuration required for the stream.
4. Confirm the owning backend or service that will manage connect, heartbeat, reconnect, and shutdown behavior.

## Plan

Before making changes:

- state the WebSocket event stream being implemented
- list the files that will be changed
- state the auth path and connection lifecycle responsibilities
- state how the connection path will be verified

## Commands

1. Add or correct the WebSocket connection setup at the appropriate service layer.
2. Implement authentication, heartbeat, reconnect, backoff, and shutdown handling explicitly.
3. Normalize streamed events into the repo’s existing internal event contract where possible.
4. Add observability for connection state, reconnects, and dropped or delayed events.
5. Keep the first pass focused on one working event stream before layering in broader orchestration.
6. Avoid claiming the stream works until the connection lifecycle and event handling path are both checked.

## Verification

1. Re-read the connection manager, auth code, and event handler logic after changes.
2. Run local build or tests where available.
3. Verify the connect path, reconnect strategy, and event normalization path.
4. State any remaining blocker such as app subscription setup, token path, or network constraints.

## Summary

```text
## Result
- Action: implemented or updated a Zoom WebSocket event stream
- Status: success | partial | failed
- Details: connection path, auth model, event handling, verification run
```

## Next Steps

- Test the stream against real events in a controlled environment.
- If the connection path is healthy but event handling fails, narrow the downstream layer next.
- If HTTP callbacks would be simpler and sufficient, switch to `/setup-zoom-webhooks`.
