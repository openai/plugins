# Conversions API Reference

## Purpose

Conversions API (CAPI) sends conversion events from trusted server-side code. Use it for conversions that are confirmed on the server, for improved reliability, or to pair with Pixel events through deduplication.

## Non-Negotiable Safety Rules

- CAPI authentication material must never be written to source code, frontend code, browser-visible env vars, logs, generated reports, snapshots, or comments.
- Do not mint or store secrets. Add only a config reference or placeholder unless the user explicitly asks for secret provisioning through an approved system.
- Do not expose server conversion endpoints that allow arbitrary client event injection.
- Do not log full request payloads if they contain identifiers, customer data, or auth metadata.
- Treat `oppref` as opaque attribution context, not a user identifier. Pass the raw value unchanged when available, but do not parse, URL-decode, cookie-decode, generate, transform, store broadly, or log it with raw identifiers.

## Implementation Checklist

1. Find server runtime and outbound API conventions.
   - Look for route handlers, API controllers, background jobs, webhook handlers, service objects, typed HTTP clients, retries, and logging standards.
   - Prefer existing conversion/event service patterns when present.
   - On reruns, inventory existing OpenAI Ads CAPI clients, payload builders, event boundaries, tests, and config before adding new code. Extend the existing CAPI path instead of creating a second client or config convention.
   - Use server-side conversion publishers for other ad platforms as evidence for boundaries, secret retrieval, non-blocking dispatch, dedupe IDs, and tests. Do not copy their request schema, user matching fields, retry policy, or credential handling.
   - Search for existing config and secret retrieval patterns before defaulting to env vars: typed settings, framework config, deployment env conventions, Vault, cloud secret managers, Kubernetes secrets, Doppler, 1Password, or similar.

2. Choose the event boundary.
   - Purchase: order/payment success persisted on the server.
   - Lead: server accepts and stores the lead, or the upstream CRM request succeeds.
   - Signup: user/account creation succeeds.
   - Subscription/trial: entitlement or plan activation succeeds.

3. Add safe configuration.
   - Use an existing config/env abstraction.
   - Use a clear placeholder such as `OPENAI_ADS_CONVERSIONS_API_KEY` for server-only auth.
   - If the framework distinguishes public env vars, never use a public prefix for CAPI keys.
   - Use one logical Pixel ID for Pixel and CAPI when both emit the same event. A browser public env alias may exist, but it should resolve to the same Pixel ID used by server-side CAPI.
   - If adding a `validate_only` toggle, make checked-in env templates and runtime defaults blank or false. `validate_only: true` is for local smoke tests and should not be the default deployed behavior unless the user explicitly asks for validation-only instrumentation.

4. Build the request using documented schema only.
   - Send `POST https://bzr.openai.com/v1/events?pid=<PIXEL-ID>` with `Content-Type: application/json` and `Authorization: Bearer <server-only CAPI key>`.
   - Use current field names: top-level `validate_only` and `events`, and per-event `id`, `type`, `timestamp_ms`, `oppref`, `source_url`, `action_source`, `user`, and `data`.
   - Include `custom_event_name` as a CAPI event field when `type` is `custom`. Do not put it inside `data` for CAPI.
   - Include `opt_out` when the repository has an existing opt-out or consent concept that should opt the event out of future user-level personalization.
   - Do not use legacy field names such as `event_name`, `event_time_epoch_ms`, `event_id`, `event_source_url`, or `event_data` in the CAPI request body. `event_id` is valid for Pixel options, but CAPI uses `id`.
   - Verify endpoint path, auth header, event names, field names, and required identifiers from current docs.
   - Reuse existing HTTP client and timeout/retry conventions.
   - Keep payload construction small and testable.

5. Add deduplication for Pixel+CAPI.
   - Include the same Pixel ID, event name, and `event_id` in Pixel and CAPI events for the same conversion.
   - Prefer existing order/payment/lead IDs when stable and non-sensitive.

6. Add failure behavior consistent with product semantics.
   - Conversion reporting failure must not fail, block, or materially slow checkout, signup, lead submission, or other core success flows unless the user explicitly asks for fail-closed behavior.
   - Prefer existing background-task, queue, or after-commit patterns. If none exist and adding one would be too broad, use a bounded fire-and-log implementation and report any remaining latency risk.
   - Log a redacted warning/metric if the repository has a standard observability pattern.
   - Avoid retry loops that can duplicate conversions unless the API supports idempotency/deduplication.

7. Add web attribution context for CAPI when available.
   - If the conversion request is same-site and the server can read cookies, read the raw `__oppref` cookie value and pass it as `events[].oppref` without decoding or normalizing it.
   - If the server cannot read the cookie but an existing browser-to-server conversion request exists, add a minimal optional context object such as `openaiAds: { oppref, sourceUrl }`. Treat this as a fallback attribution path, not as trusted business state.
   - On the browser, source `oppref` from the `oppref` URL parameter or existing `__oppref` cookie when available. Pass it unchanged and omit it when absent.
   - For `action_source: "web"`, send `source_url` as HTTP(S) origin plus pathname only. Strip query strings and fragments before sending, and reject or replace non-HTTP(S) schemes with a trusted configured app URL.
   - If using browser-provided `sourceUrl`, validate its origin against the current request origin or a configured canonical site origin before using it. If it is missing, malformed, non-HTTP(S), or from an untrusted origin, fall back to a server-derived URL such as the current route, checkout/confirmation route, or configured canonical site URL.
   - If the repository has a configured canonical site origin, such as `OPENAI_ADS_SITE_ORIGIN` or an existing public app URL setting, prefer that origin when constructing fallback `source_url`. The request origin can still be trusted for validation, but it should not override the configured canonical origin for fallback URLs.
   - For non-web conversions, choose the documented `action_source` that matches the source: `mobile_app`, `offline`, `physical_store`, `phone_call`, `email`, or `other`. Do not force `web` unless a browser/webpage source URL is available and meaningful.
   - Do not build a new public endpoint solely to accept arbitrary conversion events from the browser.

## Event Contract

Every CAPI event needs a stable non-empty `id`, supported `type`, integer `timestamp_ms`, and `data` object. `timestamp_ms`, `amount`, and `quantity` values should be integers. `timestamp_ms` must represent the event time in milliseconds, be within the last 7 days, and not be more than 10 minutes in the future. If a `data.amount` is present, include a valid ISO 4217 `data.currency`.

For `action_source: "web"`, `source_url` is required. For other action sources, include `source_url` only when it is documented and meaningful for the source. Use one of the documented action sources: `web`, `mobile_app`, `offline`, `physical_store`, `phone_call`, `email`, or `other`.

Use this event-to-data mapping:

| Event type | `data.type` | Typical boundary |
| --- | --- | --- |
| `page_viewed` | `contents` | meaningful page view, usually Pixel-first |
| `contents_viewed` | `contents` | product/content detail shown |
| `items_added` | `contents` | item added to cart after success |
| `checkout_started` | `contents` | checkout session started |
| `order_created` | `contents` | order/payment success persisted |
| `lead_created` | `customer_action` | lead accepted/stored |
| `registration_completed` | `customer_action` | account creation succeeds |
| `appointment_scheduled` | `customer_action` | appointment booking succeeds |
| `subscription_created` | `plan_enrollment` | paid subscription activates |
| `trial_started` | `plan_enrollment` | trial entitlement activates |
| `custom` | `custom` | no standard event fits |

For `contents` payloads, use documented content item fields such as `id`, `name`, `content_type`, `quantity`, `amount`, and `currency`. Do not use removed object shapes such as `checkout_session`, `line_items`, or `order`. For commerce totals, use top-level `data.amount` and `data.currency` for the order, checkout, or cart total. If item-level `contents[].amount` is included, prefer unit price. Omit item-level amount when only line totals are available or the repository does not make unit price semantics clear.

For custom events, set event-level `type: "custom"` and event-level `custom_event_name`, with `data.type: "custom"`. Use lowercase names where possible. Names must be 1-64 ASCII letters, numbers, underscores, or dashes, start and end with an alphanumeric character, and not overlap with standard event names.

## User Data

CAPI user data belongs on each event as `events[].user`. Pixel user data belongs in Pixel initialization, not in each Pixel `measure` call.

Only include documented user fields that the repository already has an approved pattern to collect or derive:

- `email_sha256`
- `external_id_sha256`
- `country`
- `city`
- `zip_code`
- `ip_address`
- `user_agent`

Hash `email_sha256` and `external_id_sha256` before sending; values must be lowercase 64-character SHA-256 hex strings. Do not send raw email, raw external IDs, phone numbers, or phone hashes. For `ip_address` and `user_agent`, only pass values already available on the server request path and consistent with the repository's privacy/consent model.

## Validation And Smoke Testing

When the repository supports it, add a dry-run or test path that sends `validate_only: true` to CAPI. `validate_only` validates the request but should not be used for Pixel/SDK traffic, and it should not be the default in committed env templates or production runtime config. Keep conversion reporting failures non-blocking for core business logic even when validation or network calls fail.

If batching events, cap batches at 1000 events. One invalid event fails the full batch, so prefer one event per conversion unless the repository already has a safe batching abstraction, validation path, and retry behavior.

Add focused tests when practical:

- Payload builder test for documented field names, event/data type pairing, integer amount/quantity values, and shared dedupe `id`.
- Rerun/extension test or review note showing the new flow uses the existing OpenAI Ads helper/client rather than duplicating CAPI setup.
- `source_url` sanitizer tests that strip query/fragment and reject or replace non-HTTP(S) schemes.
- Browser-provided `sourceUrl` tests that reject untrusted origins, prefer a configured canonical origin for fallback when present, and otherwise fall back to a server-derived URL.
- `oppref` tests or review notes showing cookie/URL values are passed through as raw opaque values without decoding or normalization.
- Conversion boundary test showing reporting is attempted only after the core action succeeds, and skipped when the core action fails.
- Failure-path test or review note showing CAPI network/API failures do not fail checkout, signup, lead submission, or the relevant core flow.

## When To Defer CAPI

Defer to a manual follow-up if:

- There is no server-side conversion boundary in the repository.
- There is no safe secret/config pattern.
- The exact CAPI schema/auth behavior cannot be verified.
- The implementation cannot safely capture `oppref` or `source_url`; omit/report those fields rather than creating a brittle or privacy-risky path.
- Implementing CAPI would require new infrastructure such as queues, cron, secret provisioning, database migrations, or webhook contracts beyond the user's request.

## Suggested Output

Report the server files changed, event boundaries, secret reference name, `oppref` strategy, `source_url` strategy, user-data strategy, dedupe strategy, tests/checks run, and manual secret provisioning steps. If no user data is sent, say so and explain why, such as no approved email/customer identifier path. Never include a raw key, token, raw user data, or sensitive source snippets.
