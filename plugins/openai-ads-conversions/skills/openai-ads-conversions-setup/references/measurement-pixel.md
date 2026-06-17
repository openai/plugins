# Measurement Pixel Reference

## Purpose

The Measurement Pixel captures browser-side conversion events for OpenAI Ads. Use it when the repository has a client-rendered flow or a browser-visible success page that can emit a conversion after user consent and after the conversion has actually happened.

The Pixel is a browser JavaScript integration. If the customer-facing surface is mobile/native, backend-only, or otherwise lacks a safe browser JavaScript/TypeScript insertion point, skip Pixel setup and prefer CAPI-only when a server conversion boundary exists.

## Inputs

- Pixel ID or repository config key that resolves to the Pixel ID.
- Event list and event boundaries.
- Consent/privacy gating requirements.
- Current OpenAI Ads Pixel docs or SDK reference for exact syntax. Prefer the docs when available; use this reference as a fallback when browsing is unavailable.

## Implementation Checklist

1. Find the existing analytics layer.
   - Prefer wrappers such as `analytics.track`, `trackEvent`, `useAnalytics`, `gtag`, `fbq`, Segment, RudderStack, or custom/first-party event dispatchers.
   - If a wrapper exists, add OpenAI Ads as another sink rather than scattering calls throughout the app.
   - On reruns, inventory existing OpenAI Ads browser helpers and event call sites before adding new ones. Extend the existing helper or analytics sink instead of adding a second Pixel initialization or parallel wrapper.
   - Use other ad platform browser events as clues for local boundaries and consent gates, but map event names and payloads to OpenAI Ads docs.

2. Initialize once in browser code.
   - Good candidates include app/root layout client providers, analytics providers, main browser entrypoints, or tag manager modules.
   - The current SDK pattern is: insert the loader script near the top of `<head>`, load `https://bzrcdn.openai.com/sdk/oaiq.min.js`, initialize with `oaiq("init", { pixelId: "<YOUR-PIXEL-ID>" })`, and emit events with `oaiq("measure", ...)`.
   - Use the exact current docs snippet when possible. If framework conventions require a component/module wrapper, preserve the same loader URL, global queue name, init command, and measure command semantics.
   - `pixelId` is required. `debug` is optional and should be enabled only for local/test troubleshooting unless the user explicitly asks otherwise.
   - Avoid server components, SSR-only files, route handlers, tests, stories, and build scripts.
   - Guard against repeated initialization during client-side navigation.
   - If user data is already available through an approved browser analytics path, pass documented user fields during Pixel initialization. Do not attach user data to each `measure` call unless current docs explicitly require it.
   - Pixel user fields are `email_sha256`, `external_id_sha256`, `country`, `city`, and `zip_code`. Hash raw email or external IDs before sending, or omit them if the repository has no approved browser hashing/normalization pattern.
   - If user data becomes available after the first init, such as during login, checkout, lead submission, or signup, call `oaiq("init", { user })` again with the complete documented `user` object before or near the relevant conversion event. After a successful first init, the follow-up init does not need to include `pixelId`.
   - Follow the repository's existing consent gates for whether Pixel measurement and Pixel user-data updates are allowed. If measurement is allowed but the event should be opted out of future user-level personalization, send the conversion event with Pixel options `{ opt_out: true }`.

3. Emit events at confirmed conversion boundaries.
   - Use only supported event names from current docs.
   - Commerce funnel examples: `page_viewed`, `contents_viewed`, `items_added`, `checkout_started`, `order_created`.
   - Lead/signup examples: `lead_created`, `registration_completed`, `appointment_scheduled`.
   - Subscription examples: `subscription_created`, `trial_started`.
   - Purchase: after payment/order confirmation, not on checkout click.
   - Add-to-cart: after the cart mutation succeeds. Cover each confirmed add path, including product-card add buttons, product-detail add buttons, and cart quantity-increment controls when they create or increase a cart line. If only some paths are safe to instrument, report the uncovered paths as optional follow-ups.
   - Lead: after lead submission succeeds, not when a form opens.
   - Signup: after account creation succeeds, not when signup starts.
   - Subscription/trial: after plan/trial activation succeeds.
   - Custom events: only if current docs support them, no standard event fits, and the event has a valid `custom_event_name`.
   - If you install Pixel but intentionally omit `page_viewed`, include the reason in the report: too noisy, SPA route semantics unclear, no meaningful landing pages, already covered elsewhere, or deferred for a smaller first patch.

4. Preserve existing privacy behavior.
   - Follow existing consent, cookie, and data minimization gates.
   - Do not add user identifiers or hashed PII unless current docs require/allow it and the repository already has an approved normalization path.
   - For Pixel-only events, do not manually pass `oppref`, `source_url`, timestamps, or batching metadata. The SDK captures `oppref` from the landing page URL, stores it in the first-party `__oppref` cookie, adds `source_url`, timestamps events, and batches `measure` calls.
   - If Pixel and CAPI are both in scope, preserve attribution context for CAPI by passing `oppref` from the URL or `__oppref` cookie to the server only through an existing conversion request path when the server cannot read the cookie itself.

5. Keep config explicit.
   - Browser-visible Pixel ID may use the repository's public env convention, such as `NEXT_PUBLIC_OPENAI_ADS_PIXEL_ID` in Next.js.
   - If CAPI sends the same event, the browser-visible Pixel ID must be the same logical Pixel ID used by server-side CAPI. Separate env variable names are fine only as framework aliases for the same value.
   - Do not use browser-visible config for CAPI credentials.

## Event Deduplication

When Pixel and CAPI both emit the same conversion, use the same Pixel ID, same event name, and same `event_id` in both the browser and server paths. Prefer an existing order ID, payment intent ID, lead ID, or signup transaction ID when it is stable and non-sensitive. If no stable ID exists, generate one at conversion start and persist it through the successful completion path.

For Pixel, pass `event_id` in the optional fourth `oaiq("measure", ...)` options object. For CAPI, the same value is the event's `id`. For custom events, keep the same `custom_event_name` on both Pixel and CAPI.

## Standard Event Selection

Evaluate all primary supported event types before choosing the smallest safe set. Instrument high-confidence events now; put plausible but unconfirmed events in the report as optional follow-ups the advertiser can add if desired.

- `page_viewed`: page load or important landing page view; usually rely on Pixel if browser support exists.
- `contents_viewed`: specific product, listing, article, plan, or content unit view, including interactions that happen after a page has loaded.
- `items_added`: add-to-cart or quantity increment succeeds; cover all confirmed successful add paths or report partial coverage.
- `checkout_started`: checkout session starts.
- `order_created`: order or payment is confirmed.
- `lead_created`: lead submission is accepted.
- `registration_completed`: account creation completes.
- `appointment_scheduled`: booking completes.
- `subscription_created`: subscription activates.
- `trial_started`: trial starts.
- `custom`: use only when no standard event maps cleanly.

For Pixel custom events, call `oaiq("measure", "custom", { type: "custom" }, { custom_event_name: "<name>" })`. Custom event names must be 1-64 characters, contain only letters, numbers, underscores, or dashes, start and end with a letter or number, and not match a standard event name. Use lowercase names for consistency.

## Common Risks

- Initializing the Pixel in both a root layout and a nested page.
- Rerunning the setup and adding duplicate event calls to a page that already publishes through a shared analytics helper.
- Emitting a conversion on attempted action instead of success.
- Putting Pixel user data on `measure` calls instead of `init`, or sending raw email/raw external IDs as Pixel user fields.
- Bypassing the repository's existing consent gates for Pixel measurement or Pixel user-data updates.
- Using a standard event name that is not supported by current docs.
- Duplicating a Pixel and CAPI event without a shared `event_id`.
- Adding browser plumbing for `oppref` when the server already has the `__oppref` cookie.
- Silently skipping obvious funnel events such as product views, add-to-cart, or checkout start without explaining whether they were inapplicable, ambiguous, or simply left as optional follow-ups.
- Adding Pixel logic before consent checks that other analytics obey.
- Coupling Pixel setup to checkout implementation details more than necessary.
