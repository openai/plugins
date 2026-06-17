---
name: openai-ads-conversions-setup
description: Guide Codex through instrumenting or extending repositories with OpenAI Ads Measurement Pixel and optional Conversions API (CAPI). Use when adding Ads conversion tracking, browser pixel events, server-side conversion events, event_id deduplication, CAPI secret placeholders, incremental conversion coverage, or validating Ads conversion setup. Applies to local repositories and PR review contexts; prioritize safe, reviewable diffs and never place API keys or secrets in source code or client bundles.
---

# OpenAI Ads Conversions Setup

## Overview

Use this skill to add, extend, or review OpenAI Ads conversion instrumentation in an advertiser repository. It supports browser Pixel setup, server-side Conversions API setup, Pixel+CAPI deduplication, and incremental reruns after the app adds new pages or flows, while keeping diffs small and avoiding secret exposure.

Use only public OpenAI Ads documentation and repository-local patterns for implementation choices. If the docs are unavailable or unclear, ask for clarification or leave a documented follow-up instead of relying on undocumented behavior.

## Required Inputs

Before editing code, identify:

- Setup mode: `pixel`, `capi`, or `pixel+capi`.
- Frontend/runtime surface: browser JavaScript/TypeScript, server-rendered web, backend-only, mobile/native, or unknown.
- Pixel ID, if Pixel is in scope.
- CAPI authentication plan, if CAPI is in scope: existing secret/env var name, secret manager path, or placeholder-only.
- Conversion events to instrument and where they occur in the product flow.
- Whether this is a first-time setup or an incremental rerun extending existing OpenAI Ads instrumentation.
- Whether the desired behavior is `propose patch`, `apply local patch`, or `review existing integration`.

Treat the linked OpenAI Ads docs as the source of truth for exact SDK syntax, endpoint shape, supported events, request fields, and validation rules. When browsing is available, check the current docs before writing concrete calls; if the docs conflict with this skill, follow the docs and mention the conflict in the setup report. When browsing is unavailable, use this skill's references as a fallback. Do not invent SDK functions, event names, request schemas, or endpoint paths.

Primary docs to prefer when available:

- `https://developers.openai.com/ads/measurement-pixel`
- `https://developers.openai.com/ads/conversions-api`
- `https://developers.openai.com/ads/supported-events`

## Workflow

1. Inspect the repository shape.
   - Detect framework, package manager, router, server runtime, frontend surface, env convention, test commands, and existing analytics integrations.
   - Determine whether a browser JavaScript Pixel is supportable. If the customer-facing surface is mobile/native, backend-only, or otherwise lacks a safe browser JS insertion point, use CAPI-only and report that Pixel was skipped.
   - Search for existing OpenAI Ads instrumentation: Pixel initialization, CAPI clients, event helpers, config/env vars, dedupe IDs, attribution context, tests, and setup docs.
   - Search for existing pixels or server conversion APIs such as Meta Pixel/CAPI, Google Ads/gtag, TikTok Events API, Pinterest, Snap, Segment, RudderStack, or custom analytics wrappers.
   - Use other ad platform integrations as evidence for local conversion boundaries, consent gates, config/secret patterns, non-blocking dispatch, dedupe IDs, and tests. Do not copy their event names, payload schemas, user matching fields, credential exposure patterns, or retry behavior.
   - Prefer the repository's existing analytics abstraction over adding a parallel abstraction. If OpenAI Ads instrumentation already exists, treat its helper/client/config pattern as canonical.
   - Search for existing config and secret retrieval patterns before choosing env vars: framework settings, typed config objects, deployment env conventions, Vault, cloud secret managers, Kubernetes secrets, Doppler, 1Password, or similar.

2. Confirm the setup plan.
   - For Pixel, identify a single browser-only initialization point, event call sites, and any approved browser user-data path.
   - For CAPI, identify a server-only execution point, secret retrieval pattern, and outbound HTTP/client pattern.
   - For Pixel+CAPI, define one logical Pixel ID and a stable `event_id` strategy so browser and server events can deduplicate.
   - For CAPI web events, define an `oppref` strategy and a sanitized `source_url` strategy before editing. Prefer a server-readable raw `__oppref` cookie value; if unavailable, pass minimal optional conversion context from the browser to an existing server conversion request. For deduped Pixel+CAPI events, make CAPI `source_url` describe the same browser conversion context as the paired Pixel event when practical. If the browser fires the Pixel event before navigation and the server would otherwise derive a different URL, pass the browser's current `sourceUrl` to the server and validate it against a trusted request/configured origin before using it. If a configured canonical site origin exists, prefer it for fallback `source_url` construction while still allowing the request origin as trusted.
   - For CAPI-only web setup, explicitly plan how the server event will include matching and attribution context that the Pixel would otherwise help provide: `oppref`, `source_url`, client `user_agent`, trusted client IP, and documented hashed user identifiers when safely available.
   - If adding a CAPI validation toggle, keep checked-in defaults production-capable. `validate_only: true` is documented for local smoke tests, but committed env templates and runtime defaults should be blank or false unless the user explicitly asks for validation-only behavior.
   - Select supported event names from current docs. Evaluate the primary supported events (`page_viewed`, `contents_viewed`, `items_added`, `checkout_started`, `order_created`, `lead_created`, `registration_completed`, `appointment_scheduled`, `subscription_created`, and `trial_started`) and report high-confidence events you will instrument plus supported events you intentionally skip.
   - If Pixel is installed and `page_viewed` is not instrumented, explicitly say why: too noisy, SPA route semantics unclear, no meaningful landing pages, already covered by an existing helper, or intentionally deferred.
   - Do not silently skip plausible events. For each skipped supported event, state why: not applicable, no confirmed success boundary found, ambiguous product semantics, unsupported surface, or safe follow-up available if the advertiser wants broader coverage.
   - If the target flow is ambiguous, ask one concise question before editing.

3. Implement the smallest useful patch.
   - Add initialization once.
   - Instrument only clearly identified conversion events.
   - Favor a small high-confidence initial patch over speculative broad coverage. Put plausible but unconfirmed events in the setup report as optional follow-ups, not half-guessed instrumentation.
   - Keep config names explicit. Public framework aliases such as `NEXT_PUBLIC_OPENAI_ADS_PIXEL_ID` or `VITE_OPENAI_ADS_PIXEL_ID` are allowed for browser Pixel code, but document that they must contain the same Pixel ID as the server-side Pixel ID when CAPI sends the same event.
   - Never put CAPI keys in browser-visible env vars, frontend code, logs, comments, docs, test snapshots, or generated reports.
   - Use documented OpenAI Ads event names and request field names only. Do not use legacy CAPI field names such as `event_name`, `event_time_epoch_ms`, `event_source_url`, or `event_data`.
   - For commerce flows, ensure each instrumented event covers the actual success path. For `items_added`, cover all successful add-to-cart and quantity-increment paths you can confirm; if you only cover a subset, say that clearly in the setup report and offer the missing paths as follow-ups.
   - If Pixel is installed and documented user matching data, such as hashed email or location fields, becomes available client-side after the initial Pixel init, add a second `oaiq("init", { user })` call near that point. Do this for normal web checkout/signup flows unless consent, opt-out, or repository policy prevents it; if skipped, explain why in the setup report. Do not include `pixelId` again after a successful first init, and do not put Pixel user data in `measure` calls.
   - Conversion reporting must not fail, block, or materially slow the core business flow. Pixel helpers should catch/suppress their own errors. The whole CAPI path, including event construction, source URL derivation, user-data hashing, timeout setup, and dispatch, must be inside a non-blocking/catch boundary so checkout, signup, lead submission, and other success paths still complete if conversion reporting code throws.

4. Verify locally.
   - Run relevant typecheck, lint, unit tests, or framework-specific checks when available.
   - Resolve the directory containing this installed skill before using helper scripts.
   - Run this skill's static helpers when useful:
     - `python3 <installed-skill-path>/scripts/verify_capi_secret_not_exposed.py <repo>`
     - `python3 <installed-skill-path>/scripts/verify_ads_setup.py <repo> --pixel-id <id> --require pixel --require capi`
     - For Pixel+CAPI web dedupe, add `--require dedupe --require shared-pixel-id --require oppref --require source-url`.
   - These helpers run locally. By default, they report paths, line numbers, rules, and summaries without printing source-line context or transmitting repository contents.
   - If verification cannot run, report the blocker and the residual risk.

5. Produce a setup report.
   - Include changed files, detected stack, setup mode, existing OpenAI Ads instrumentation found, events added or changed in this run, events already covered, supported events skipped with reasons, optional follow-up events the advertiser can add if desired, skipped surfaces/platforms, Pixel ID/config reference, Pixel user-data strategy, Pixel opt-out behavior, CAPI secret reference, CAPI `oppref` strategy, CAPI `source_url` strategy, browser-provided `sourceUrl` trust boundary, CAPI user-data strategy, event deduplication strategy, checks run, manual follow-ups, and risks.
   - Do not include raw secrets or sensitive advertiser source snippets.
   - End with a clear deployment review warning: before deploying, the advertiser should review that the implementation satisfies their privacy, security, consent, and data handling requirements.

## Incremental Reruns

When rerunning this skill on a repository that may already have OpenAI Ads instrumentation:

- Build an inventory first: Pixel init locations, CAPI clients, event helpers, analytics sinks, event call sites, Pixel ID/config sources, `event_id` generation, `oppref` and `source_url` handling, user-data handling, tests, and docs.
- Treat existing OpenAI Ads integration surfaces as canonical. Extend the existing helper/client/adapter instead of creating a second Pixel initializer, second CAPI client, second config convention, or scattered one-off call sites.
- Compare current app flows against the existing event inventory. Add only missing coverage at confirmed success boundaries.
- Check duplicate-risk before editing: a new page or flow may already publish through a shared cart service, checkout service, confirmation component, analytics wrapper, or server conversion helper.
- Preserve existing dedupe, Pixel ID, attribution, user-data, failure-handling, test, and reporting patterns unless they are unsafe or incompatible with current docs.
- If another ad platform already publishes from a new flow but OpenAI Ads does not, treat that as a strong signal of missing OpenAI Ads coverage. Still map it to documented OpenAI Ads event names and payload fields.
- Keep rerun diffs focused. Do not churn env templates, setup docs, or shared helpers unless the extension requires it or they are stale.
- In the final report, separate existing events found, new events added, events skipped because they are already covered, and optional follow-ups.

## Pixel Rules

Use `references/measurement-pixel.md` for browser Pixel details.

- Initialize in a client-only location that runs once per page/app load.
- Use the documented browser SDK pattern: load `https://bzrcdn.openai.com/sdk/oaiq.min.js`, initialize with `oaiq("init", { pixelId })`, and emit events with `oaiq("measure", ...)`.
- Use Pixel only for browser JavaScript/TypeScript surfaces supported by current docs. For mobile/native or unsupported frontends, skip Pixel and prefer CAPI-only when a server conversion boundary exists.
- Avoid duplicate initialization across route transitions, hydration, tests, or nested layouts.
- Instrument conversion events close to the confirmed success boundary, not merely on button click unless the click itself is the conversion.
- Respect consent and privacy gating patterns already present in the repository.
- Do not manually send Pixel `oppref`, `source_url`, timestamps, or batching metadata; the browser SDK handles those transport details. Add `debug: true` only for local/test debugging, not as a committed production default.
- If documented Pixel user data becomes available after initial page-load initialization, call `oaiq("init", { user })` again with only documented, normalized fields. For checkout, signup, lead, subscription, or registration flows where the browser has email or location data before or after the confirmed conversion, add this second init unless consent, opt-out, or repository policy prevents it, and report any skip. Preserve the repository's existing consent gates for whether measurement and user-data collection are allowed. Put `opt_out` on the Pixel event options when measurement is allowed but the event should be opted out of future user-level personalization.
- Use supported standard event names from current docs, such as `page_viewed`, `contents_viewed`, `items_added`, `checkout_started`, `order_created`, `lead_created`, `registration_completed`, `appointment_scheduled`, `subscription_created`, or `trial_started`. If uncertain, use the closest documented event or leave an explicit follow-up instead of inventing a name.
- Custom events are a fallback when no standard event fits. Use `custom` only with a valid, documented `custom_event_name`.

## CAPI Rules

Use `references/conversions-api.md` for server-side setup details.

- CAPI code must run server-side only.
- Do not create, request, store, or print CAPI keys.
- Prefer an existing secret manager/env retrieval pattern; otherwise add a placeholder config reference and report that the user must provision the secret.
- Use existing HTTP clients, retry conventions, telemetry, and privacy filters.
- Do not add new queues, databases, background jobs, or broad infra unless the user explicitly asks.
- If Pixel and CAPI both emit the same conversion, use the same Pixel ID, event name, and `event_id` in both paths.
- For web CAPI events, include `action_source: "web"` and a sanitized HTTP(S) `source_url` containing only origin plus pathname. Strip query strings and fragments before sending; reject or replace non-HTTP(S) URL schemes with a trusted configured web app URL. For deduped Pixel+CAPI events, prefer a `source_url` from the same browser conversion context as the paired Pixel event. If accepting a browser-provided `sourceUrl`, require its origin to match the current request origin or a configured canonical site origin before using it; otherwise fall back to a server-derived URL. When a configured canonical site origin exists, use it as the preferred fallback origin and do not let request service/proxy origins override it. If the final CAPI `source_url` intentionally differs from the Pixel event's browser page, call that out in the setup report. For non-web server conversions, choose the documented `action_source` that matches the source (`mobile_app`, `offline`, `physical_store`, `phone_call`, `email`, or `other`) instead of forcing `web`.
- Treat `oppref` as opaque attribution context. Prefer a server-readable `__oppref` cookie over client-supplied request context; pass the raw value unchanged and do not parse, URL-decode, cookie-decode, generate, transform, or log it.
- Use CAPI `events[].user` only for documented fields already available through an approved repository pattern. Never send raw email or raw external IDs. For CAPI-only web conversions, make a best effort to include client `user_agent`, trusted client IP, and hashed email or external ID when available; these fields are especially important when there is no paired Pixel event.
- Use current event timestamps in `timestamp_ms`; do not send stale backfills older than the documented window or future-dated events.
- Preserve existing opt-out/consent semantics and map them to documented `opt_out` fields when the repository has a relevant user-level personalization opt-out.
- CAPI failure handling must not throw into checkout, signup, lead submission, or other core success paths. Wrap event construction, source URL derivation, user-data hashing, timeout setup, and dispatch in the same non-blocking failure boundary. Prefer existing background-task or queue patterns; if none exist, use a bounded fire-and-log implementation and document remaining latency risk.
- For `contents` payloads, use top-level `data.amount` for the event total. For item-level `contents[].amount`, use the unit price when the repository exposes it; omit item-level amount if only line totals are available or the semantics are unclear.

## Framework Hints

Use `references/framework-patterns.md` for common locations and pitfalls in Next.js, React/Vite, Remix, Express, Rails, Django, Flask, and monorepos.

Treat these as hints, not rules. The repository's existing conventions win.

## Verification And Reporting

Use `references/verification-checklist.md` for validation steps and `references/report-schema.md` for the final setup report format.

High-priority failure cases:

- CAPI secret or API key appears in client code, browser-visible env vars, logs, comments, generated docs, snapshots, or reports.
- Pixel initialization can run multiple times in normal navigation.
- CAPI code can run from a browser bundle.
- Pixel and CAPI duplicate the same event without the same logical Pixel ID and shared dedupe key.
- OpenAI Ads event names are invented or unsupported by current docs.
- CAPI payload uses undocumented or legacy field names, mismatched event/data types, or web events without a sanitized `source_url`.
- Pixel user data is attached to `measure` instead of `init`, includes undocumented/raw identity fields, or bypasses the repository's existing consent gates.
- CAPI `timestamp_ms` is stale, future-dated beyond the documented allowance, or not tied to the actual conversion time.
- CAPI action source is forced to `web` for non-web/mobile/offline events instead of using an appropriate documented `action_source`.
- CAPI custom event names are placed in the wrong field, or Pixel custom events omit the options-level `custom_event_name`.
- CAPI web events ignore available `oppref` context or log `oppref` alongside raw identifiers.
- CAPI `source_url` accepts non-HTTP(S) schemes or preserves query strings/fragments.
- CAPI decodes or transforms `oppref` instead of passing the raw opaque value through unchanged.
- CAPI uses a browser-provided `sourceUrl` with an untrusted origin instead of falling back to a server-derived URL.
- CAPI lets request service/proxy origins override a configured canonical site origin when constructing fallback `source_url`.
- Existing consent or user-level personalization opt-out behavior is bypassed or lost.
- Pixel is installed but available checkout/signup/lead user matching data is neither sent through a second `init({ user })` call nor explicitly skipped with a consent/policy reason.
- Deduped Pixel+CAPI events derive materially different browser context or `source_url` without explanation.
- The setup report does not explain why plausible supported events were skipped.
- The patch instruments likely pre-conversion intent instead of confirmed conversion success.
- Any CAPI setup step, including event construction before dispatch, can fail or materially delay the core business flow.

## When To Stop And Ask

Ask before proceeding when:

- The conversion event boundary is unclear.
- CAPI is requested but no server runtime or secret pattern exists.
- Exact OpenAI Ads SDK/API syntax cannot be verified from docs or provided context.
- Pixel is requested but the repository has no browser JavaScript/TypeScript surface and no safe browser insertion point.
- The only viable implementation would require new infrastructure, a deploy step, or changing authentication/checkout behavior.
- The user provides or asks you to embed a raw CAPI key in the repository.
