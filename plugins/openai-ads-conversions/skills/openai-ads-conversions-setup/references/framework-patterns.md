# Framework Patterns

Use these as starting points while inspecting a repository. Existing local conventions should override these hints.

## Next.js

- App Router Pixel candidates: client providers imported by `app/layout.tsx`, analytics provider components, or client-only tag modules.
- Pages Router Pixel candidates: `_app.tsx`, analytics providers, or browser entry modules.
- CAPI candidates: route handlers, API routes, server actions, checkout webhooks, order services, or backend package code.
- `NEXT_PUBLIC_*` values are browser-visible. Pixel IDs may be public if docs require it; CAPI keys must not use this prefix.
- Watch for server components. Pixel code must be inside a client component or browser-only module.
- For CAPI web attribution, prefer reading `__oppref` from request cookies in route handlers/server actions. If the conversion is submitted from a client component and cookies are not available server-side, pass a minimal optional context object through the existing request body.

## React/Vite/SPA

- Pixel candidates: `src/main.tsx`, `src/App.tsx`, analytics providers, or router-level providers.
- CAPI usually requires a backend package or API service. If the repo is frontend-only, add Pixel and report that CAPI needs server ownership.
- Avoid embedding CAPI calls in frontend API clients.
- If the SPA posts conversion data to a backend, pass only optional attribution context such as `oppref` and sanitized `sourceUrl`; never pass the CAPI key or let the browser choose arbitrary event names.

## Mobile / Native Apps

- Do not add the browser Measurement Pixel to iOS, Android, React Native, Flutter, or other native-only surfaces unless current docs explicitly provide a supported SDK for that platform.
- Prefer CAPI-only from a trusted backend conversion boundary when available.
- If the repo has both web and mobile apps, instrument only the supported web surface with Pixel and report mobile as CAPI-only or deferred.

## Remix

- Pixel candidates: root document scripts, client analytics modules, or route success pages.
- CAPI candidates: actions/loaders that confirm conversion, server utilities, or webhook handlers.
- Keep server-only code out of files imported by browser bundles.

## Express/Fastify/Nest

- Pixel is usually in a separate frontend package.
- CAPI candidates: controllers/routes for checkout, lead submission, signup, or webhook processing.
- Use existing config providers and HTTP client abstractions.
- Read `__oppref` from request cookies when same-site; otherwise accept optional attribution context only on existing trusted conversion routes.

## Rails

- Pixel candidates: layout templates, Stimulus controllers, frontend packs, or tag manager partials.
- CAPI candidates: controllers after successful persistence, service objects, ActiveJob jobs, or webhook handlers.
- Use credentials/env patterns already present.
- Prefer controller/request cookie access for `__oppref` before adding browser payload plumbing.

## Django/Flask

- Pixel candidates: base templates, frontend bundles, or success-page templates.
- CAPI candidates: views after successful persistence, service modules, Celery tasks, or webhook handlers.
- Use existing settings/secrets patterns.
- Prefer request cookie access for `__oppref` before adding browser payload plumbing.

## Monorepos

- Identify the deployed web app and backend package before editing.
- Avoid adding dependencies at the repo root unless the repository already centralizes analytics there.
- Run the package-specific checks rather than broad repo-wide checks when the monorepo is large.

## Existing Analytics Abstractions

If an analytics abstraction already exists, prefer adding an OpenAI Ads adapter/sink. This usually gives better consent handling, fewer call sites, and easier testing.

Avoid bypassing a mature analytics layer unless it cannot represent the required OpenAI Ads event fields.

## Existing Advertising Platform Integrations

Search for Meta Pixel/CAPI, Google Ads/gtag, TikTok Events API, Pinterest, Snap, Segment, RudderStack, or custom/first-party ad conversion publishers before adding new OpenAI Ads code.

Use those integrations to infer:

- Confirmed conversion boundaries such as checkout success, lead accepted, signup completed, trial started, or subscription activated.
- Existing analytics adapters or event dispatchers to extend.
- Consent/privacy gates.
- Server-side secret/config retrieval patterns.
- Non-blocking dispatch, queue, background-task, or fire-and-log patterns.
- Dedupe or idempotency IDs such as order ID, payment intent ID, lead ID, or signup transaction ID.
- Local tests and fixtures for conversion behavior.

Do not copy platform-specific event names, request schemas, user matching fields, retry semantics, or credential exposure patterns. Map each event back to current OpenAI Ads docs.
