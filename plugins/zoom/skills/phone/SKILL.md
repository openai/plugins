---
name: build-zoom-phone-integration
description: Use when building Phone.
---

# Build Zoom Phone Integration

Use this skill when the target workflow is Zoom Phone, CTI, CRM calling, call events, or Smart Embed behavior.

## Workflow

1. Classify the integration: REST API automation, webhook event processing, Smart Embed, URI launch, CRM dialer, or call-handling workflow.
2. Confirm the actor, account settings, phone entitlements, and OAuth scopes before implementation.
3. Keep call control, call records, number management, and webhook processing as separate modules.
4. For Smart Embed, validate postMessage event contracts, embedding constraints, and CRM state mapping.
5. Debug by checking scopes, phone license, role permissions, number ownership, webhook subscriptions, and event payload shape.

## References

- Full preserved guide: [references/full-guide.md](references/full-guide.md)
- Architecture and lifecycle: [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
- Phone API service pattern: [examples/phone-api-service-pattern.md](examples/phone-api-service-pattern.md)
- Smart Embed bridge: [examples/smart-embed-postmessage-bridge.md](examples/smart-embed-postmessage-bridge.md)
- Event contract: [references/smart-embed-event-contract.md](references/smart-embed-event-contract.md)
- Common issues: [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
