# Verification Checklist

## Static Checks

- Pixel initialization appears once in the normal browser startup path.
- Pixel user data, if used, is sent through `oaiq("init", { user })`, not through `measure` calls.
- Late-arriving Pixel user data, such as checkout/login/signup fields, triggers a follow-up `init` without repeating `pixelId` after the first successful init.
- Existing OpenAI Ads instrumentation was inventoried before changes on reruns.
- Pixel code is not imported by server-only execution paths unless guarded correctly.
- CAPI code is server-only and never imported by browser bundles.
- CAPI auth config uses a server-only env/secret convention.
- New event coverage extends existing OpenAI Ads helpers/clients/adapters instead of creating duplicate initialization, duplicate CAPI clients, or new config conventions.
- Pixel+CAPI duplicate events use the same logical Pixel ID, same event name, and same stable `event_id`.
- New call sites are not already covered by a shared analytics wrapper, cart/checkout service, confirmation component, or server conversion helper.
- Existing Meta/Google/TikTok/other ad platform integrations were used only as local pattern evidence, not as the OpenAI Ads API contract.
- Event names and payload fields match current OpenAI Ads docs.
- Checked-in env templates and runtime defaults do not set CAPI `validate_only` to true unless the user explicitly requested validation-only behavior.
- CAPI request body uses current field names (`id`, `type`, `timestamp_ms`, `source_url`, `action_source`, `data`) and not removed legacy names.
- CAPI `timestamp_ms` is generated from the actual event time, not a stale backfill or future timestamp.
- CAPI event `type` matches the documented `data.type` family.
- CAPI custom events use event-level `custom_event_name`; Pixel custom events use the Pixel options object.
- Commerce CAPI totals use top-level `data.amount`; item-level `contents[].amount` is unit price or omitted when semantics are unclear.
- CAPI web events include `action_source: "web"` and a sanitized HTTP(S) `source_url` with origin plus pathname only.
- Non-web CAPI events use an appropriate documented `action_source` such as `mobile_app`, `offline`, `physical_store`, `phone_call`, `email`, or `other`.
- CAPI `source_url` sanitizer strips query/fragment and rejects or replaces non-HTTP(S) schemes.
- Browser-provided CAPI `sourceUrl` is accepted only when its origin matches the current request origin or a configured canonical site origin; otherwise the implementation falls back to a server-derived URL.
- If a configured canonical site origin exists, fallback `source_url` construction prefers it over request service/proxy origins.
- Available `oppref` context is passed as a raw opaque value to CAPI and not decoded, normalized, transformed, or logged; server cookie access is preferred over client-supplied context.
- CAPI user data is event-scoped, documented, and uses hashed identity fields rather than raw email or raw external IDs. If no user data is sent, the report explains why.
- Existing consent or personalization opt-out behavior is preserved and mapped to documented `opt_out` fields when applicable.
- Existing consent gates control whether Pixel measurement and Pixel user-data updates are allowed. When measurement is allowed but the event should be opted out of future user-level personalization, the Pixel event uses documented `opt_out`.
- Pixel implementation relies on SDK-managed `oppref`, `source_url`, timestamps, and batching; manual plumbing for those fields is only added for CAPI when needed.
- Plausible supported events that are not instrumented are listed with reasons and optional follow-up guidance; if Pixel is installed and `page_viewed` is omitted, the reason is explicit.
- `items_added` covers all confirmed add-to-cart and quantity-increment success paths, or the report explicitly calls out partial coverage.
- Consent/privacy gating matches existing analytics behavior.
- Unsupported frontend surfaces such as mobile/native are skipped or reported as CAPI-only.

## Suggested Commands

Run the narrowest relevant commands the repository supports:

- TypeScript: `npm run typecheck`, `pnpm typecheck`, `yarn typecheck`, or package-specific equivalents.
- Lint: `npm run lint`, `pnpm lint`, `yarn lint`, or package-specific equivalents.
- Tests: targeted unit tests for changed files, checkout/lead/signup handlers, or analytics adapters.
- Static helper: `python3 <installed-skill-path>/scripts/verify_capi_secret_not_exposed.py <repo>`.
- Static helper: `python3 <installed-skill-path>/scripts/verify_ads_setup.py <repo> --pixel-id <id> --require pixel --require capi`.
- If Pixel+CAPI dedupe is in scope, include `--require dedupe --require shared-pixel-id`.
- If CAPI web attribution is in scope, include `--require oppref --require source-url`.

`<installed-skill-path>` is the directory containing this installed skill.

The helper scripts run locally. By default, they report paths, line numbers, rules, and summaries without printing source-line context or transmitting repository contents.

## Manual Checks

- Confirm the Pixel script initializes only after consent when consent is required.
- Confirm docs-focused Pixel coverage when applicable: current loader/init syntax, late `user` init placement, Pixel options-level `opt_out`, and no user data on `measure`.
- Confirm docs-focused CAPI coverage when applicable: event-scoped `user`, `opt_out`, valid `timestamp_ms`, documented `action_source`, trusted/sanitized `source_url`, configured canonical origin fallback, raw opaque `oppref` pass-through, and batch failure behavior if batching exists.
- Confirm conversion event fires after a successful test conversion, not before.
- Confirm Pixel or CAPI failures do not fail, block, or materially slow the user flow unless explicitly intended.
- Confirm no secret value appears in browser devtools, source maps, build output, logs, or reports.
- Confirm CAPI uses `Content-Type: application/json` and bearer auth from a server-only secret.
- Confirm CAPI dry-run or test hooks can use `validate_only: true` where practical, but deployed/default config sends real events.
- Confirm any CAPI batching has a clear failure strategy, because one invalid event can fail the whole batch.
- Confirm route/controller tests cover success-only CAPI scheduling when practical.
- Confirm rerun reports separate existing events found, new events added, events already covered, and optional follow-ups.
- Confirm final diff is limited to conversion setup and nearby tests/config.

## Failure Handling

If a check fails, either fix the issue or leave the integration unapplied and report the exact blocker. Do not ship a known secret leak, duplicate conversion emission, or undocumented API call.
