# Production Sharp Edges

Use this reference when a Wix Headless run touches production release, SEO-controlled root files, favicon behavior, or multi-site orchestration.

## Release Retries

`wix release` can hit transient backend/network errors after upload or during publish. Known retryable signals include:

- `ECONNRESET`
- `ETIMEDOUT`
- `EAI_AGAIN`
- `STATE_MISMATCH`
- `temporary system error`
- `try again shortly`

The bundled `scripts/release.sh` retries these known transient release failures. Do not retry build failures; TypeScript, Astro, missing import, and missing module failures are code issues that must be fixed before another release attempt.

For batch releases across many projects, prefer releasing failed sites one by one after the current deployment state settles. Parallel release is useful for throughput, but retry serially when Wix reports state-machine errors.

## Reserved Root Paths

Wix can intercept root paths before the Astro app serves them. Do not assume files in `public/` or root Astro routes will win for these URLs:

- `/robots.txt`
- `/llms.txt`
- `/favicon.svg`

### `robots.txt`

Use the Wix SEO robots REST endpoint instead of `public/robots.txt`:

```http
PUT https://www.wixapis.com/promote-seo-robots-server/v2/robots
```

```json
{
  "robotsTxt": {
    "content": "...",
    "default": false,
    "subdomain": "www"
  }
}
```

`default: true` resets to Wix's built-in robots file.

### `llms.txt`

Use the sibling Wix SEO endpoint instead of `public/llms.txt` or `src/pages/llms.txt.ts`:

```http
PUT https://www.wixapis.com/promote-seo-robots-server/v2/llms
```

```json
{
  "llmsTxt": {
    "content": "...",
    "default": false,
    "subdomain": "www"
  }
}
```

Do not use `default: true` for custom `llms.txt`; in observed runs it caused `/llms.txt` to return `404`.

Wix may mutate `llms.txt` content by:

- prepending an H1 from the site/business title
- wrapping the first submitted line as a tagline blockquote
- appending AI Agent Access and available MCP tools sections

Start custom content with the intended tagline, not another H1.

### Favicon

Wix may intercept `/favicon.svg`, even if the project has `public/favicon.svg` or `src/pages/favicon.svg.ts`.

When a run needs a custom favicon and no site-favicon API/CLI is available, embed the SVG directly in the document head:

```html
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,..." />
```

Keep the source SVG in `public/favicon.svg` for repository readability, but do not use `/favicon.svg` as the browser-facing href unless a live fetch proves Wix is serving the project asset.

## Verification

For production checks, verify the final rendered HTML and edge-controlled files separately:

- For favicon: fetch the live page HTML and confirm the `<link rel="icon">` points to the expected data URI or supported favicon URL.
- For `robots.txt`: fetch `/robots.txt` after the REST update.
- For `llms.txt`: fetch `/llms.txt` after the REST update and account for Wix-injected sections.
- For custom domains: check both the Wix-hosted URL and custom domain when available, because domain propagation and redirects can differ.

Do not construct URLs by editing the release URL from memory. Use the exact release URL printed by the CLI or the configured custom domain.