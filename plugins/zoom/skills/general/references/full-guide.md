# Zoom General Cross-Product Guide

Background reference for cross-product Zoom developer questions. Prefer the workflow skills first, then use this file for shared platform guidance and routing detail.

## Choose Your Path

| I want to... | Use this skill |
|---|---|
| Build deterministic automation, account management, reporting, or scheduled jobs | [rest-api](../../rest-api/SKILL.md) |
| Receive event notifications over HTTP | [webhooks](../../webhooks/SKILL.md) |
| Receive event notifications over WebSocket | [websockets](../../websockets/SKILL.md) |
| Embed Zoom meetings into an app | [meeting-sdk](../../meeting-sdk/SKILL.md) |
| Build custom video experiences | [video-sdk](../../video-sdk/SKILL.md) |
| Build an app that runs inside the Zoom client | [zoom-apps-sdk](../../zoom-apps-sdk/SKILL.md) |
| Access live meeting media or transcripts | [rtms](../../rtms/SKILL.md) |
| Transcribe uploaded or stored media | [scribe](../../scribe/SKILL.md) |
| Enable collaborative browsing for support | [cobrowse-sdk](../../cobrowse-sdk/SKILL.md) |
| Build Contact Center apps and channel integrations | [contact-center](../../contact-center/SKILL.md) |
| Build Virtual Agent web or mobile chatbot experiences | [virtual-agent](../../virtual-agent/SKILL.md) |
| Build Zoom Phone integrations | [phone](../../phone/SKILL.md) |
| Build Team Chat apps and integrations | [team-chat](../../team-chat/SKILL.md) |
| Build server-side integrations with Rivet | [rivet-sdk](../../rivet-sdk/SKILL.md) |
| Run browser, device, or network preflight diagnostics | [probe-sdk](../../probe-sdk/SKILL.md) |
| Add prebuilt UI components for Video SDK | [ui-toolkit](../../ui-toolkit/SKILL.md) |
| Implement OAuth authentication | [oauth](../../oauth/SKILL.md) |

## Routing Rules

- If the user asks for meeting embed or join behavior, route to Meeting SDK before REST.
- If the user asks for a fully custom session product, route to Video SDK.
- If the user asks for account, user, meeting, recording, reporting, or scheduled automation, route to REST API.
- If the user asks for event ingestion, choose Webhooks for HTTP delivery and WebSockets for lower-latency persistent connections.
- If the user asks for live media, raw streams, or live transcripts, route to RTMS and pair it with Meeting SDK or REST only when needed.
- If the user asks for an app inside the Zoom client, route to Zoom Apps SDK.
- If auth, scopes, redirect handling, or token refresh are involved, chain OAuth guidance.

## Webhooks vs WebSockets

| Aspect | Webhooks | WebSockets |
|---|---|---|
| Connection | HTTP POST to your endpoint | Persistent WebSocket |
| Latency | Higher | Lower |
| Public endpoint | Required | Not required in the same way |
| Setup | Simpler | More operationally complex |
| Best for | Most event ingestion | Low-latency or private-network event streams |

## Common Use Cases

| Use Case | Description | Skills Needed |
|---|---|---|
| [Meeting + Webhooks + OAuth Refresh](../references/meeting-webhooks-oauth-refresh-orchestration.md) | Create a meeting, process real-time updates, and refresh OAuth tokens safely | [rest-api](../../rest-api/SKILL.md) + [oauth](../../oauth/SKILL.md) + [webhooks](../../webhooks/SKILL.md) |
| [Scribe Transcription Pipeline](../use-cases/scribe-transcription-pipeline.md) | Transcribe uploaded files or S3 archives | [scribe](../../scribe/SKILL.md) |
| [Custom Meeting UI (Web)](../use-cases/custom-meeting-ui-web.md) | Build a custom video UI for a real Zoom meeting | [meeting-sdk](../../meeting-sdk/SKILL.md) |
| [Meeting Automation](../use-cases/meeting-automation.md) | Schedule, update, and delete meetings programmatically | [rest-api](../../rest-api/SKILL.md) |
| [Meeting Bots](../use-cases/meeting-bots.md) | Build bots that join meetings for AI, transcription, or recording | [meeting-sdk/linux](../../meeting-sdk/linux/SKILL.md) + [rest-api](../../rest-api/SKILL.md) |
| [Recording & Transcription](../use-cases/recording-transcription.md) | Download recordings and get transcripts | [webhooks](../../webhooks/SKILL.md) + [rest-api](../../rest-api/SKILL.md) |
| [Real-Time Media Streams](../use-cases/real-time-media-streams.md) | Access live audio, video, and transcript streams | [rtms](../../rtms/SKILL.md) |
| [In-Meeting Apps](../use-cases/in-meeting-apps.md) | Build apps that run inside Zoom meetings | [zoom-apps-sdk](../../zoom-apps-sdk/SKILL.md) |
| [Zoom Phone Smart Embed CRM Integration](../use-cases/zoom-phone-smart-embed-crm.md) | Build CRM dialer and call logging flows | [phone](../../phone/SKILL.md) + [oauth](../../oauth/SKILL.md) |
| [Rivet Event-Driven API Orchestrator](../use-cases/rivet-event-driven-api-orchestrator.md) | Combine webhooks and API actions through Rivet | [rivet-sdk](../../rivet-sdk/SKILL.md) + [oauth](../../oauth/SKILL.md) + [rest-api](../../rest-api/SKILL.md) |

## Detailed References

- [Authentication](authentication.md)
- [App types](app-types.md)
- [Scopes](scopes.md)
- [Marketplace](marketplace.md)
- [Query routing playbook](query-routing-playbook.md)
- [Automatic REST and webhook chaining](automatic-skill-chaining-rest-webhooks.md)
- [Meeting webhook and OAuth refresh orchestration](meeting-webhooks-oauth-refresh-orchestration.md)
- [Distributed meeting fallback architecture](distributed-meeting-fallback-architecture.md)
- [Community repositories](community-repos.md)
- [SDK upgrade guide](sdk-upgrade-guide.md)
- [SDK logs troubleshooting](sdk-logs-troubleshooting.md)
