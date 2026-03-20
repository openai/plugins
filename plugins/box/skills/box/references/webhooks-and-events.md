# Webhooks and Events

## Table of Contents

- Choose webhooks vs events
- Minimal implementation path
- Verification checklist
- Primary docs

## Choose webhooks vs events

- Use Box webhooks when the app needs push-based notifications for new or changed content.
- Use the events APIs for catch-up syncs, polling-based integrations, or backfills after downtime.
- Start with the smallest event consumer that can receive the signal, fetch the affected object metadata, and log or enqueue work.

## Minimal implementation path

1. Confirm which Box actor owns the webhook or event subscription.
2. Store webhook signing secrets outside the codebase.
3. Verify signatures before mutating request bodies.
4. Persist enough event data to deduplicate duplicate deliveries and retries.
5. Fetch the file or folder metadata after receiving the event rather than trusting the event payload alone.
6. Hand off to downstream processing only after the idempotency key is recorded.

## Verification checklist

- Happy path: receive the event, verify the signature, fetch the file or folder metadata, and log the Box ID.
- Duplicate delivery: send the same payload twice and confirm only one downstream action happens.
- Signature failure: reject a payload with a bad signature and confirm no side effects occur.
- Catch-up behavior: if the workflow also uses the events APIs, confirm the checkpoint or cursor is persisted.

## Primary docs

- Webhook guides:
  - https://developer.box.com/guides/webhooks/
- Webhook use cases:
  - https://developer.box.com/guides/webhooks/use-cases/
- Events API reference:
  - https://developer.box.com/reference/resources/event/
