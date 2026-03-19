---
name: observability
description: Vercel Observability expert guidance — Drains (logs, traces, speed insights, web analytics), Web Analytics, Speed Insights, runtime logs, custom events, OpenTelemetry integration, and monitoring dashboards. Use when instrumenting, debugging, or optimizing application performance and user experience on Vercel.
metadata:
  priority: 6
  docs:
    - "https://vercel.com/docs/observability"
    - "https://vercel.com/docs/observability/otel-overview"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'instrumentation.ts'
    - 'instrumentation.js'
    - 'src/instrumentation.ts'
    - 'src/instrumentation.js'
    - 'app/layout.*'
    - 'src/app/layout.*'
    - 'pages/_app.*'
    - 'src/pages/_app.*'
    - 'apps/*/instrumentation.ts'
    - 'apps/*/instrumentation.js'
    - 'apps/*/app/layout.*'
    - 'apps/*/src/app/layout.*'
    - 'apps/*/pages/_app.*'
    - 'apps/*/src/pages/_app.*'
    - 'sentry.client.config.*'
    - 'sentry.server.config.*'
    - 'sentry.edge.config.*'
  bashPatterns:
    - '\bvercel\s+logs?\b'
    - '\bvercel\s+logs?\s+.*--follow\b'
    - '\bvercel\s+logs?\s+.*--level\b'
    - '\bvercel\s+logs?\s+.*--since\b'
    - '\bcurl\s+.*deployments.*events\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/analytics\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/analytics\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/analytics\b'
    - '\byarn\s+add\s+[^\n]*@vercel/analytics\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/speed-insights\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/speed-insights\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/speed-insights\b'
    - '\byarn\s+add\s+[^\n]*@vercel/speed-insights\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@sentry/nextjs\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@sentry/nextjs\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@sentry/nextjs\b'
    - '\byarn\s+add\s+[^\n]*@sentry/nextjs\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@sentry/node\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@sentry/node\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@sentry/node\b'
    - '\byarn\s+add\s+[^\n]*@sentry/node\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@datadog/browser-rum\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@datadog/browser-rum\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@datadog/browser-rum\b'
    - '\byarn\s+add\s+[^\n]*@datadog/browser-rum\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bcheckly\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bcheckly\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bcheckly\b'
    - '\byarn\s+add\s+[^\n]*\bcheckly\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bnewrelic\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bnewrelic\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bnewrelic\b'
    - '\byarn\s+add\s+[^\n]*\bnewrelic\b'
  promptSignals:
    phrases:
      - "add logging"
      - "add logs"
      - "set up logging"
      - "setup logging"
      - "configure logging"
      - "structured logging"
      - "log drain"
      - "log drains"
      - "vercel analytics"
      - "speed insights"
      - "web analytics"
      - "opentelemetry"
      - "otel"
      - "instrumentation"
      - "monitoring"
      - "set up monitoring"
      - "add observability"
      - "track errors"
      - "error tracking"
      - "sentry"
      - "datadog"
      - "check the logs"
      - "show me the error"
      - "what went wrong"
      - "where did it fail"
      - "show me the logs"
      - "find the error"
      - "why did it fail"
      - "debug the error"
    allOf:
      - [add, logging]
      - [add, monitoring]
      - [set up, logs]
      - [configure, analytics]
      - [vercel, logs]
      - [vercel, analytics]
      - [track, performance]
      - [track, errors]
    anyOf:
      - "logging"
      - "monitoring"
      - "analytics"
      - "observability"
      - "telemetry"
      - "traces"
      - "metrics"
      - "debug"
      - "debugging"
      - "stuck"
      - "hanging"
      - "hung"
      - "waiting"
      - "stalled"
      - "spinning"
      - "timeout"
      - "slow"
      - "pending"
      - "unresponsive"
    minScore: 6
validate:
  -
    pattern: "export (async )?function (GET|POST|PUT|PATCH|DELETE)"
    message: "API route handlers should include error logging — wrap in try/catch with console.error for production debugging"
    severity: warn
    skipIfFileContains: "console\\.error|logger\\.|captureException|Sentry"
retrieval:
  aliases:
    - monitoring
    - logging
    - analytics
    - performance tracking
  intents:
    - add monitoring
    - set up logging
    - track performance
    - configure analytics
  entities:
    - Web Analytics
    - Speed Insights
    - OpenTelemetry
    - Drains
    - runtime logs
chainTo:
  -
    pattern: 'console\.log\s*\(\s*[''"]error|catch\s*\(\w+\)\s*\{\s*\n\s*console\.log'
    targetSkill: vercel-functions
    message: 'Console.log-only error handling detected in route handler — loading Vercel Functions guidance for structured error handling, proper logging, and function runtime configuration.'
    skipIfFileContains: 'captureException|@sentry/|@opentelemetry/|logger\.\w+|Sentry\.|reportError'
  -
    pattern: 'from\s+[''"]@sentry/(nextjs|node)[''""]'
    targetSkill: nextjs
    message: 'Sentry SDK import detected — loading Next.js guidance for instrumentation.ts setup and Sentry config integration.'
    skipIfFileContains: 'instrumentation\.register|withSentryConfig'
  -
    pattern: "winston|pino|bunyan"
    targetSkill: observability
    message: 'Third-party logger detected (winston/pino/bunyan) — Vercel provides native structured logging, runtime logs, and Drains for log export. Loading Observability guidance for Vercel-native logging.'
    skipIfFileContains: "@vercel/otel|@opentelemetry/|Sentry\\."

---

# Vercel Observability

You are an expert in Vercel's observability stack — runtime logs, structured logging, Drains, Web Analytics, Speed Insights, and monitoring integrations. **Always start with logging.** When something is stuck, slow, or broken, the first step is always to check or add logs.

## Structured Logging Baseline

Add this to every API route and server action as a minimum. If the user reports something stuck, hanging, or slow, verify this baseline exists first:

```ts
const start = Date.now();
console.log(JSON.stringify({ level: "info", msg: "start", route: "/api/example", requestId: req.headers.get("x-vercel-id") }));
// ... your logic ...
console.log(JSON.stringify({ level: "info", msg: "done", route: "/api/example", ms: Date.now() - start }));
// On error:
console.error(JSON.stringify({ level: "error", msg: "failed", route: "/api/example", error: err.message, ms: Date.now() - start }));
```

## Runtime Logs

Vercel provides real-time logs for all function invocations.

### Structured Logging

```ts
// app/api/process/route.ts
export async function POST(req: Request) {
  const start = Date.now()
  const data = await req.json()

  // Structured logs appear in Vercel's log viewer
  console.log(JSON.stringify({
    level: 'info',
    message: 'Processing request',
    requestId: req.headers.get('x-vercel-id'),
    payload_size: JSON.stringify(data).length,
  }))

  try {
    const result = await processData(data)
    console.log(JSON.stringify({
      level: 'info',
      message: 'Request completed',
      duration_ms: Date.now() - start,
    }))
    return Response.json(result)
  } catch (error) {
    console.error(JSON.stringify({
      level: 'error',
      message: 'Processing failed',
      error: error instanceof Error ? error.message : String(error),
      duration_ms: Date.now() - start,
    }))
    return Response.json({ error: 'Internal error' }, { status: 500 })
  }
}
```

### Next.js Instrumentation

```ts
// instrumentation.ts (Next.js 16)
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    // Initialize monitoring on server startup
    const { initMonitoring } = await import('./lib/monitoring')
    initMonitoring()
  }
}
```

### Runtime Logs via REST API

Query deployment runtime logs programmatically. The endpoint returns `application/stream+json` — a streaming response where each line is a separate JSON object.

```bash
# Stream runtime logs for a deployment (returns application/stream+json)
curl -N -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v3/deployments/<deployment-id>/events" \
  --max-time 120
```

> **Streaming guidance:** The response is unbounded — always set a timeout (`--max-time` in curl, `AbortController` with `setTimeout` in fetch). Parse line-by-line as NDJSON. Each line contains `{ timestamp, text, level, source }`.

```ts
// Programmatic streaming with timeout
const controller = new AbortController()
const timeout = setTimeout(() => controller.abort(), 60_000) // 60s max

const res = await fetch(
  `https://api.vercel.com/v3/deployments/${deploymentId}/events`,
  {
    headers: { Authorization: `Bearer ${process.env.VERCEL_TOKEN}` },
    signal: controller.signal,
  }
)

const reader = res.body!.getReader()
const decoder = new TextDecoder()
let buffer = ''

try {
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()! // keep incomplete line in buffer
    for (const line of lines) {
      if (!line.trim()) continue
      const event = JSON.parse(line)
      console.log(`[${event.level}] ${event.text}`)
    }
  }
} finally {
  clearTimeout(timeout)
}
```

> **MCP alternative:** Use `get_runtime_logs` via the Vercel MCP server for agent-friendly log queries without managing streams directly. See `⤳ skill: vercel-api`.

## Web Analytics

Privacy-friendly, first-party analytics with no cookie banners required.

### Installation

```bash
npm install @vercel/analytics
```

### Setup (Next.js App Router)

```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/next'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

### Custom Events (Pro/Enterprise)

Track business-specific events beyond pageviews.

```ts
import { track } from '@vercel/analytics'

// Track a conversion
track('purchase', {
  product: 'pro-plan',
  value: 20,
  currency: 'USD',
})

// Track a feature usage
track('feature_used', {
  name: 'ai-chat',
  duration_ms: 3200,
})
```

### Server-Side Tracking

```ts
import { track } from '@vercel/analytics/server'

export async function POST(req: Request) {
  const data = await req.json()
  await processOrder(data)

  track('order_completed', {
    order_id: data.id,
    total: data.total,
  })

  return Response.json({ success: true })
}
```

## Speed Insights

Real-user performance monitoring built on Core Web Vitals.

### Installation

```bash
npm install @vercel/speed-insights
```

### Setup (Next.js App Router)

```tsx
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  )
}
```

### Metrics Tracked

| Metric | What It Measures | Good Threshold |
|--------|-----------------|----------------|
| LCP | Largest Contentful Paint | < 2.5s |
| INP | Interaction to Next Paint | < 200ms |
| CLS | Cumulative Layout Shift | < 0.1 |
| FCP | First Contentful Paint | < 1.8s |
| TTFB | Time to First Byte | < 800ms |

### Performance Attribution

Speed Insights attributes metrics to specific routes and pages, letting you identify which pages are slow and why.

## Drains

Drains forward observability data from Vercel to external endpoints. They are the primary mechanism for exporting logs, traces, Speed Insights, and Web Analytics data to third-party platforms.

> **Plan requirement:** Drains require a **Pro or Enterprise** plan. For Hobby plans, see the [Fallback Guidance](#fallback-guidance-no-drains) section below.

### Data Types

Drains can forward multiple categories of telemetry:

| Data Type | What It Contains | Use Case |
|-----------|-----------------|----------|
| **Logs** | Runtime function logs, build logs, static access logs | Centralized log aggregation |
| **Traces** | OpenTelemetry-compatible distributed traces | End-to-end request tracing |
| **Speed Insights** | Core Web Vitals and performance metrics | Performance monitoring pipelines |
| **Web Analytics** | Pageviews, custom events, visitor data | Analytics data warehousing |

### Supported Formats

| Format | Protocol | Best For |
|--------|----------|----------|
| JSON | HTTPS POST | Custom backends, generic log collectors |
| NDJSON | HTTPS POST | Streaming-friendly consumers, high-volume pipelines |
| Syslog | TLS syslog | Traditional log management (rsyslog, syslog-ng) |

### Setting Up Drains

Drains are configured via the **Vercel Dashboard** at `https://vercel.com/dashboard/{team}/~/settings/log-drains` or the **REST API**.

#### Via Dashboard

1. Open `https://vercel.com/dashboard/{team}/~/settings/log-drains` (replace `{team}` with your team slug)
2. Click **Add Log Drain**
3. Select the drain type (JSON, NDJSON, or syslog) and enter the endpoint URL
4. Choose which environments and sources to include
5. Click **Create** to activate the drain

#### Via REST API (`/v1/drains`)

```bash
# List all drains
curl -s -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v1/drains?teamId=$TEAM_ID" | jq

# Create a JSON drain
curl -X POST -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.vercel.com/v1/drains?teamId=$TEAM_ID" \
  -d '{
    "url": "https://your-endpoint.example.com/logs",
    "type": "json",
    "sources": ["lambda", "edge", "static"],
    "environments": ["production"]
  }'

# Test a drain (sends a test payload to your endpoint)
curl -X POST -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v1/drains/<drain-id>/test?teamId=$TEAM_ID"

# Update a drain (change URL, sources, or environments)
curl -X PATCH -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.vercel.com/v1/drains/<drain-id>?teamId=$TEAM_ID" \
  -d '{
    "url": "https://new-endpoint.example.com/logs",
    "environments": ["production", "preview"]
  }'

# Delete a drain
curl -X DELETE -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v1/drains/<drain-id>?teamId=$TEAM_ID"
```

### Web Analytics Drains Reference

When a drain is configured to receive Web Analytics data, payloads arrive as batched events. The format depends on your drain type.

#### JSON Payload Schema

```json
[
  {
    "type": "pageview",
    "url": "https://example.com/blog/post-1",
    "referrer": "https://google.com",
    "timestamp": 1709568000000,
    "geo": { "country": "US", "region": "CA", "city": "San Francisco" },
    "device": { "os": "macOS", "browser": "Chrome", "isBot": false },
    "projectId": "prj_xxxxx",
    "environment": "production"
  },
  {
    "type": "custom_event",
    "name": "purchase",
    "url": "https://example.com/checkout",
    "properties": { "product": "pro-plan", "value": 20 },
    "timestamp": 1709568100000,
    "geo": { "country": "US" },
    "device": { "os": "macOS", "browser": "Chrome", "isBot": false },
    "projectId": "prj_xxxxx",
    "environment": "production"
  }
]
```

#### NDJSON Payload Format

Each line is a separate JSON object (one event per line):

```
{"type":"pageview","url":"https://example.com/","timestamp":1709568000000,"geo":{"country":"US"},"device":{"browser":"Chrome"},...}
{"type":"pageview","url":"https://example.com/about","timestamp":1709568001000,"geo":{"country":"DE"},"device":{"browser":"Firefox"},...}
{"type":"custom_event","name":"signup","url":"https://example.com/register","timestamp":1709568002000,...}
```

> **Ingestion tip:** For NDJSON, process line-by-line as events arrive. This format is preferred for high-volume pipelines where batch parsing overhead matters.

### Security: Signature Verification

Vercel signs every drain payload with an HMAC-SHA1 signature in the `x-vercel-signature` header. **Always verify signatures in production** to prevent spoofed data.

> **Critical:** You must verify against the **raw request body** (not a parsed/re-serialized version). JSON parsing and re-stringifying can change key order or whitespace, breaking the signature match.

```ts
import { createHmac, timingSafeEqual } from 'crypto'

function verifyDrainSignature(rawBody: string, signature: string, secret: string): boolean {
  const expected = createHmac('sha1', secret).update(rawBody).digest('hex')
  // Use timing-safe comparison to prevent timing attacks
  if (expected.length !== signature.length) return false
  return timingSafeEqual(Buffer.from(expected), Buffer.from(signature))
}
```

Usage in a drain endpoint:

```ts
// app/api/drain/route.ts
export async function POST(req: Request) {
  const rawBody = await req.text()
  const signature = req.headers.get('x-vercel-signature')
  const secret = process.env.DRAIN_SECRET!

  if (!signature || !verifyDrainSignature(rawBody, signature, secret)) {
    return new Response('Unauthorized', { status: 401 })
  }

  const events = JSON.parse(rawBody)
  // Process verified events...
  return new Response('OK', { status: 200 })
}
```

> **Secret management:** The drain signing secret is shown once when you create the drain. Store it in an environment variable (e.g., `DRAIN_SECRET`). If lost, delete and recreate the drain.

### OpenTelemetry Integration

Vercel exports traces in OpenTelemetry-compatible format via Drains. Configure an OTel-compatible drain endpoint at `https://vercel.com/dashboard/{team}/~/settings/log-drains` → **Add Log Drain** → select **OTLP** format, or via the REST API.

### Vendor Integrations

```bash
# Install via Marketplace (recommended — auto-configures drain)
vercel integration add datadog
```

Or manually create a drain at `https://vercel.com/dashboard/{team}/~/settings/log-drains` → **Add Log Drain**, or via REST API, pointing to:

| Vendor | Endpoint | Auth Header |
|--------|----------|-------------|
| **Datadog** | `https://http-intake.logs.datadoghq.com/api/v2/logs` | `DD-API-KEY` |
| **Honeycomb** | `https://api.honeycomb.io/1/batch/<dataset>` | `X-Honeycomb-Team` |

### Fallback Guidance (No Drains)

If drains are unavailable (Hobby plan or not yet configured), use these alternatives:

| Need | Alternative | How |
|------|-------------|-----|
| View runtime logs | **Vercel Dashboard** | `https://vercel.com/{team}/{project}/deployments` → select deployment → Logs tab |
| Stream logs from terminal | **Vercel CLI** | `vercel logs <deployment-url> --follow` (see `⤳ skill: vercel-cli`) |
| Query logs programmatically | **MCP / REST API** | `get_runtime_logs` tool or `/v3/deployments/:id/events` (see `⤳ skill: vercel-api`) |
| Monitor errors post-deploy | **CLI** | `vercel logs <url> --level error --since 1h` |
| Web Analytics data | **Dashboard only** | `https://vercel.com/{team}/{project}/analytics` |
| Performance metrics | **Dashboard only** | `https://vercel.com/{team}/{project}/speed-insights` |

> **Upgrade path:** When ready for centralized observability, upgrade to Pro and configure drains at `https://vercel.com/dashboard/{team}/~/settings/log-drains` or via REST API. The drain setup is typically < 5 minutes.

### Deploy Preflight Observability

Before promoting to production, verify observability readiness:

- **Drains check**: Query configured drains via MCP `list_drains` or REST API. If no drains are configured on a Pro/Enterprise plan, warn:
  > ⚠️ No drains configured. Production errors won't be forwarded to external monitoring.
  > Configure drains via Dashboard or REST API before promoting. See `⤳ skill: observability`.
- **Errored drains**: If any drain is in error state, warn and suggest remediation before deploying:
  > ⚠️ Drain "<url>" is errored. Fix or recreate before production deploy to avoid monitoring gaps.
- **Error monitoring**: Check that at least one of these is in place: configured drains, an error tracking integration (e.g., Sentry, Datadog via `vercel integration ls`), or `@vercel/analytics` in the project.
- These are warnings, not blockers — the user may proceed after acknowledgment.

### Post-Deploy Error Scan

For production deployments, wait 60 seconds after READY state, then scan for early runtime errors:

```bash
vercel logs <deployment-url> --level error --since 1h
```

Or via MCP if available: use `get_runtime_logs` with level filter `error`.

**Interpret results:**

| Finding | Action |
|---------|--------|
| No errors | ✓ Clean deploy — no runtime errors in first hour |
| Errors detected | List error count and first 5 unique error messages. Suggest: check drain payloads for correlated traces, review function logs in Dashboard |
| 500 status codes in logs | Correlate timestamps with drain data (if configured) or `vercel logs <url> --json` for structured output. Flag for immediate investigation |
| Timeout errors | Check function duration limits in `vercel.json` or project settings. Consider increasing `maxDuration` |

**Fallback (no drains):**

If no drains are configured, the error scan relies on CLI and Dashboard:

```bash
# Stream live errors
vercel logs <deployment-url> --level error --follow

# JSON output for parsing
vercel logs <deployment-url> --level error --since 1h --json
```

> For richer post-deploy monitoring, configure drains to forward logs/traces to an external platform. See `⤳ skill: observability`.

### Performance Audit Checklist

Run through this when asked to optimize a Vercel application:

1. **Measure first**: Check Speed Insights dashboard for real-user CWV data
2. **Identify LCP element**: Use Chrome DevTools → Performance → identify the LCP element
3. **Audit `'use client'`**: Every `'use client'` file ships JS to the browser — minimize
4. **Check images**: All above-fold images use `next/image` with `priority`
5. **Check fonts**: All fonts loaded via `next/font` (zero CLS)
6. **Check third-party scripts**: All use `next/script` with correct strategy
7. **Check data fetching**: Server Components fetch in parallel, no waterfalls
8. **Check caching**: Cache Components used for expensive operations
9. **Check bundle**: Run analyzer, look for low-hanging fruit
10. **Check infrastructure**: Functions in correct region, Fluid Compute enabled

## Monitoring Dashboard Patterns

### Full-Stack Observability Setup

Combine all Vercel observability tools for comprehensive coverage.

```tsx
// app/layout.tsx — complete observability setup
import { Analytics } from '@vercel/analytics/next'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
```

### Custom Monitoring with `waitUntil`

Fire-and-forget telemetry that doesn't block responses.

```ts
import { waitUntil } from '@vercel/functions'

export async function GET(req: Request) {
  const start = Date.now()
  const result = await fetchData()

  // Send response immediately
  const response = Response.json(result)

  // Report metrics in background
  waitUntil(async () => {
    await reportMetric('api_latency', Date.now() - start, {
      route: '/api/data',
      status: 200,
    })
  })

  return response
}
```

### Error Tracking Pattern

```ts
// lib/error-reporting.ts
export async function reportError(error: unknown, context: Record<string, unknown>) {
  const payload = {
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : undefined,
    timestamp: new Date().toISOString(),
    ...context,
  }

  // Log for Vercel's runtime logs
  console.error(JSON.stringify(payload))

  // Also send to external service if configured
  if (process.env.ERROR_WEBHOOK_URL) {
    await fetch(process.env.ERROR_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  }
}
```

## Marketplace Observability Integrations

### Sentry — Error & Performance Monitoring

Native Vercel Marketplace integration. Auto-configures source maps and release tracking.

```bash
npx @sentry/wizard@latest -i nextjs
# Or install manually:
npm install @sentry/nextjs
```

Sentry wizard creates `sentry.client.config.ts`, `sentry.server.config.ts`, and `sentry.edge.config.ts`. It also wraps `next.config.js` with `withSentryConfig`.

Install via Marketplace: `vercel integration add sentry`

### Datadog — Full-Stack Monitoring

APM, logs, and Real User Monitoring (RUM). Auto-configures log drain on Marketplace install.

```bash
npm install @datadog/browser-rum
```

```ts
import { datadogRum } from '@datadog/browser-rum'

datadogRum.init({
  applicationId: process.env.NEXT_PUBLIC_DD_APPLICATION_ID!,
  clientToken: process.env.NEXT_PUBLIC_DD_CLIENT_TOKEN!,
  site: 'datadoghq.com',
  service: 'my-app',
  sessionSampleRate: 100,
  trackResources: true,
  trackLongTasks: true,
})
```

Install via Marketplace: `vercel integration add datadog`

### Checkly — Synthetic Monitoring & Testing

API and browser checks that run continuously against your deployments.

```bash
npm install -D checkly
npx checkly init
```

Checkly integrates with Vercel deployment events to trigger checks on every deploy.

Install via Marketplace: `vercel integration add checkly`

### New Relic — Application Performance Monitoring

Full-stack observability with distributed tracing and alerting.

```bash
npm install newrelic
```

Requires a `newrelic.js` config file at the project root. Install via Marketplace: `vercel integration add newrelic`

## Decision Matrix

| Need | Use | Why |
|------|-----|-----|
| Page views, traffic sources | Web Analytics | First-party, privacy-friendly |
| Business event tracking | Web Analytics custom events | Track conversions, feature usage |
| Core Web Vitals monitoring | Speed Insights | Real user data per route |
| Function debugging | Runtime Logs (CLI `vercel logs` / Dashboard (`https://vercel.com/{team}/{project}/logs`) / REST) | Real-time, per-invocation logs |
| Export logs to external platform | Drains (JSON/NDJSON/Syslog) | Centralize observability (Pro+) |
| Export analytics data | Drains (Web Analytics type) | Warehouse pageviews + custom events (Pro+) |
| OpenTelemetry traces | Drains (OTel-compatible endpoint) | Standards-based distributed tracing (Pro+) |
| Post-response telemetry | `waitUntil` + custom reporting | Non-blocking metrics |
| Server-side event tracking | `@vercel/analytics/server` | Track API-triggered events |
| Hobby plan log access | CLI `vercel logs` + Dashboard (`https://vercel.com/{team}/{project}/logs`) | No drains needed |

## Cross-References

- **Drains REST API & runtime logs endpoint** → `⤳ skill: vercel-api` (Observability APIs section)
- **CLI log streaming (`--follow`, `--since`, `--level`)** → `⤳ skill: vercel-cli` (Logs & Inspection section)
- **Marketplace vendor integrations** → `⤳ skill: marketplace`

## Official Documentation

- [Vercel Analytics](https://vercel.com/docs/analytics)
- [Speed Insights](https://vercel.com/docs/speed-insights)
- [Runtime Logs](https://vercel.com/docs/logs/runtime)
- [Drains Overview](https://vercel.com/docs/drains)
- [Drains REST API](https://vercel.com/docs/rest-api/reference/endpoints/drains/retrieve-a-list-of-all-drains)
- [Drains Security](https://vercel.com/docs/drains/security)
- [Web Analytics Drains Reference](https://vercel.com/docs/drains/reference/analytics)
- [Monitoring](https://vercel.com/docs/query/monitoring)
- [@vercel/analytics npm](https://www.npmjs.com/package/@vercel/analytics)
- [@vercel/speed-insights npm](https://www.npmjs.com/package/@vercel/speed-insights)
