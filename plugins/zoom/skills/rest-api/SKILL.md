---
name: build-zoom-rest-api-app
description: Use when calling REST APIs.
---

# Build Zoom REST API App

Use this skill when the task needs deterministic Zoom API calls or resource management from application code.

## Workflow

1. Define the resource and actor: user, meeting, webinar, recording, docs, chat, phone, account, or admin-level workflow.
2. Select the endpoint and required scopes from the reference files before coding.
3. Confirm auth fit: user-level OAuth for user-owned resources, account-level OAuth for admin workflows, and only use server-to-server OAuth where the target API documents support for it.
4. Implement narrow API wrappers with explicit pagination, retry, idempotency, and rate-limit handling.
5. Treat webhook processing as a separate event-ingestion path with signature verification and replay protection.
6. Debug by checking token audience, missing scopes, resource ownership, account settings, API enablement, and rate-limit headers.

## References

- Full preserved guide: [references/full-guide.md](references/full-guide.md)
- API architecture: [concepts/api-architecture.md](concepts/api-architecture.md)
- Authentication flows: [concepts/authentication-flows.md](concepts/authentication-flows.md)
- Rate limits: [references/rate-limits.md](references/rate-limits.md)
- Meetings: [references/meetings.md](references/meetings.md)
- Recordings: [references/recordings.md](references/recordings.md)
- Users: [references/users.md](references/users.md)
- Token and scope playbook: [troubleshooting/token-scope-playbook.md](troubleshooting/token-scope-playbook.md)
