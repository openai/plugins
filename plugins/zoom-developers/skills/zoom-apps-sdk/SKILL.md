---
name: zoom-apps-sdk
description: Use when using Apps SDK.
---

# Zoom Apps SDK

Use this skill when the app runs inside the Zoom client. If the user only needs to embed a meeting in an external app, route to Meeting SDK instead.

## Workflow

1. Confirm the running context: meeting, webinar, main client, phone, collaborate mode, immersive mode, camera mode, or Layers API.
2. Configure Marketplace app settings, allowed domains, redirect URIs, and in-client OAuth before implementing SDK calls.
3. Initialize `zoomSdk` and gate features by capability and running context.
4. Design client communication and data flow: frontend SDK calls, backend REST calls, in-client OAuth tokens, and webhook handoff.
5. Implement advanced client features only after the base app loads reliably: Layers API, breakout rooms, guest mode, collaborate mode, or ZMail.
6. Debug blank panels, domain allowlist issues, CSP, missing capabilities, running-context mismatch, and OAuth redirect problems independently.

## References

- Full preserved guide: [references/full-guide.md](references/full-guide.md)
- Architecture: [concepts/architecture.md](concepts/architecture.md)
- Running contexts: [concepts/running-contexts.md](concepts/running-contexts.md)
- Meeting SDK versus Zoom Apps: [concepts/meeting-sdk-vs-zoom-apps.md](concepts/meeting-sdk-vs-zoom-apps.md)
- Layers API: [references/layers-api.md](references/layers-api.md)
- In-client OAuth: [examples/in-client-oauth.md](examples/in-client-oauth.md)
- Common issues: [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
