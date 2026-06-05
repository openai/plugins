# Build-output noise — known false positives

Read this only if `npx @wix/cli@latest build` surfaces warnings or errors and you're trying to decide whether they're real. A clean build emits a few warnings that are NOT real failures:

- **`Astro.request.headers used on prerendered page`** — emitted by the `@wix/astro` integration's middleware on every prerendered route. Internal to the integration, not from skill-emitted code. Ignore.
- **`Failed to resolve dependency: @wix/stores, present in client 'optimizeDeps.include'`** — Vite warning. The integration speculatively lists `@wix/stores` in `optimizeDeps` regardless of whether the project depends on it. Harmless.

Do NOT add filters, edit config, or attempt to silence these — they're upstream and stable. Surface to the user only if a real build failure needs context.