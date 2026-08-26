---
name: vercel-functions
description: Vercel Functions expert guidance — Serverless Functions, Edge Functions, Fluid Compute, streaming, Cron Jobs, and runtime configuration. Use when configuring, debugging, or optimizing server-side code running on Vercel.
metadata:
  priority: 8
  docs:
    - "https://vercel.com/docs/functions"
    - "https://vercel.com/docs/functions/runtimes"
    - "https://vercel.com/docs/functions/websockets"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'api/**/*.*'
    - 'pages/api/**'
    - 'src/pages/api/**'
    - 'app/**/route.*'
    - 'src/app/**/route.*'
    - 'apps/*/api/**/*.*'
    - 'apps/*/app/**/route.*'
    - 'apps/*/src/app/**/route.*'
    - 'apps/*/pages/api/**'
    - 'vercel.json'
    - 'apps/*/vercel.json'
  bashPatterns:
    - '\bvercel\s+dev\b'
    - '\bvercel\s+logs\b'
  importPatterns:
    - 'ws'
    - 'socket.io'
    - 'socket.io-client'
  promptSignals:
    phrases:
      - "websocket"
      - "websockets"
      - "web socket"
      - "socket.io"
      # Polling is the classic technique people reach for when they think Vercel
      # lacks websockets. We intentionally do NOT trigger on named third-party
      # services (Pusher, PubNub, Ably) — those are deliberate choices, not a
      # signal that someone is working around a missing feature.
      - "long polling"
      - "long-polling"
    allOf: []
    anyOf:
      - "realtime"
      - "bidirectional"
      - "ws server"
      - "polling"
      - "server-sent events"
    noneOf: []
    minScore: 6
---

# Vercel Functions

You are an expert in Vercel Functions — the compute layer of the Vercel platform.

## Function Types

### Serverless Functions (Node.js)
- Full Node.js runtime, all npm packages available
- Default for Next.js API routes, Server Actions, Server Components
- Cold starts: 800ms–2.5s (with DB connections)
- Max duration: 10s (Hobby), 300s (Pro default), 800s (Fluid Compute Pro/Enterprise)

```ts
// app/api/hello/route.ts
export async function GET() {
  return Response.json({ message: 'Hello from Node.js' })
}
```

### Edge Functions (V8 Isolates)
- Lightweight V8 runtime, Web Standard APIs only
- Ultra-low cold starts (<1ms globally)
- Limited API surface (no full Node.js)
- Best for: auth checks, redirects, A/B testing, simple transformations

```ts
// app/api/hello/route.ts
export const runtime = 'edge'

export async function GET() {
  return new Response('Hello from the Edge')
}
```

### Bun Runtime (Public Beta)

Add `"bunVersion": "1.x"` to `vercel.json` to run Node.js functions on Bun instead. ~28% lower latency for CPU-bound workloads. Supports Next.js, Express, Hono, Nitro.

### Rust Runtime (Public Beta)

Rust functions run on Fluid Compute with HTTP streaming and Active CPU pricing. Built on the community Rust runtime. Supports environment variables up to 64 KB.

### Node.js 24 LTS

Node.js 24 LTS is now GA on Vercel for both builds and functions. Features V8 13.6, global `URLPattern`, Undici v7 for faster `fetch()`, and npm v11.

### Choosing Runtime

| Need | Runtime | Why |
|------|---------|-----|
| Full Node.js APIs, npm packages | `nodejs` | Full compatibility |
| Lower latency, CPU-bound work | `nodejs` + Bun | ~28% latency reduction |
| Ultra-low latency, simple logic | `edge` | <1ms cold start, global |
| Database connections, heavy deps | `nodejs` | Edge lacks full Node.js |
| Auth/redirect at the edge | `edge` | Fastest response |
| AI streaming | Either | Both support streaming |
| Systems-level performance | `rust` (beta) | Native speed, Fluid Compute |

## Fluid Compute

Fluid Compute is the unified execution model for all Vercel Functions (both Node.js and Edge).

Key benefits:
- **Optimized concurrency**: Multiple invocations on a single instance — up to 85% cost reduction for high-concurrency workloads
- **Extended durations**: Default 300s for all plans; up to 800s on Pro/Enterprise
- **Active CPU pricing**: Charges only while CPU is actively working, not during idle/await time. Enabled by default for all plans. Memory-only periods billed at a significantly lower rate.
- **Background processing**: `waitUntil` / `after` for post-response tasks
- **Dynamic scaling**: Automatic during traffic spikes
- **Bytecode caching**: Reduces cold starts via Rust-based runtime with pre-compiled function code
- **Multi-region failover**: Default for Enterprise when Fluid is activated

### Instance Sizes

| Size | CPU | Memory |
|------|-----|--------|
| Standard (default) | 1 vCPU | 2 GB |
| Performance | 2 vCPU | 4 GB |

Hobby projects use Standard CPU. The Basic CPU instance has been removed.

### Background Processing with `waitUntil`

```ts
// Continue work after sending response
import { waitUntil } from '@vercel/functions'

export async function POST(req: Request) {
  const data = await req.json()

  // Send response immediately
  const response = Response.json({ received: true })

  // Continue processing in background
  waitUntil(async () => {
    await processAnalytics(data)
    await sendNotification(data)
  })

  return response
}
```

### Next.js `after` (equivalent)

```ts
import { after } from 'next/server'

export async function POST(req: Request) {
  const data = await req.json()

  after(async () => {
    await logToAnalytics(data)
  })

  return Response.json({ ok: true })
}
```

## Streaming

Zero-config streaming on **both runtimes**, including Server-Sent Events (SSE). Essential for AI applications.

> **You do NOT need `runtime = 'edge'` for streaming or SSE.** Streaming responses (`ReadableStream`, `text/event-stream`) work on the default Node.js runtime — this is a common misconception. Stay on Node.js (Fluid Compute) so you keep full Node.js APIs, npm packages, and longer durations; Edge offers no streaming advantage here.

```ts
export async function POST(req: Request) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of data) {
        controller.enqueue(encoder.encode(chunk))
        await new Promise(r => setTimeout(r, 100))
      }
      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
```

For AI streaming, use the AI SDK's `toUIMessageStreamResponse()` (for chat UIs with `useChat`) which handles SSE formatting automatically.

## WebSockets

Vercel Functions can hold open bidirectional WebSocket connections — use them for realtime features like interactive AI streaming, chat, and collaborative apps. There is **no separate WebSocket-server product and no third-party service (Pusher, Ably, etc.) required** — it runs on Vercel Functions directly. Requires **Fluid Compute**, which is the default for new projects.

**How it works**: a WebSocket starts as an HTTP `GET` with an `Upgrade` header, so it passes through the same Routing Middleware, rewrites, Firewall rules, and rate limits as any other request. After the upgrade, the connection is pinned to a single function instance for its lifetime; Fluid Compute lets one instance serve many concurrent connections. Active CPU pricing means you're billed while processing messages, not for idle open connections — the same limits and pricing as other Function invocations apply.

### `ws` (no extra config)

WebSockets work like any distributed WebSocket server — export an `http.Server` and use a library such as `ws`:

```ts
// api/ws.ts
import http from 'http'
import { WebSocketServer } from 'ws'

const server = http.createServer()
const wss = new WebSocketServer({ server })

wss.on('connection', (ws) => {
  ws.on('message', (data) => ws.send(data)) // echo
})

export default server
```

### Socket.IO

Higher-level realtime libraries like Socket.IO work too. Configure the **client** to use the WebSocket transport directly — Socket.IO defaults to HTTP long-polling, which won't work:

```ts
// api/socket-io.ts
import http from 'http'
import { Server } from 'socket.io'

const server = http.createServer()
const io = new Server(server)

io.on('connection', (socket) => {
  socket.on('message', (data) => socket.send(data))
})

export default server
```

```ts
// client.ts
import { io } from 'socket.io-client'

const socket = io('https://your-domain.com', {
  // Socket.IO appends /socket.io, so the full path becomes /api/socket-io/socket.io
  path: '/api/socket-io/socket.io',
  transports: ['websocket'], // required — Socket.IO defaults to HTTP long-polling
})
```

Express, Hono, and Nitro (including Nuxt, via native WebSocket support) serve WebSockets the same way — export the HTTP server. Python frameworks work too: FastAPI handles the upgrade natively, and `python-socketio` is protocol-compatible with the JS Socket.IO client.

### Next.js

Next.js doesn't expose an API for handling WebSocket upgrades. Use `experimental_upgradeWebSocket()` from `@vercel/functions` inside a route handler:

```ts
// app/api/ws/route.ts
import { experimental_upgradeWebSocket, type WebSocketData } from '@vercel/functions'

export async function GET() {
  return experimental_upgradeWebSocket((ws) => {
    ws.on('message', (data: WebSocketData) => ws.send(data))
  })
}
```

### Reconnects and persistent state

- **Connections close when the function reaches its max duration.** Clients must reconnect with backoff, then resubscribe to channels and reload any state they need.
- **No instance affinity across connections.** A reconnect — or a new deployment — may land on a different instance, so never keep durable state, presence, rooms, or pub/sub coordination in memory. Use an external store such as [Redis from the Marketplace](https://vercel.com/marketplace/redis).

```ts
// client.ts — reconnect with exponential backoff
let socket: WebSocket
let delay = 1000

function connect() {
  socket = new WebSocket('wss://your-domain.com/api/ws')
  socket.addEventListener('open', () => { delay = 1000 })
  socket.addEventListener('message', (e) => console.log(e.data))
  socket.addEventListener('close', () => {
    setTimeout(connect, delay)
    delay = Math.min(delay * 2, 30000)
  })
}

connect()
```

## Cron Jobs

Schedule function invocations via `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/daily-report",
      "schedule": "0 8 * * *"
    },
    {
      "path": "/api/cleanup",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

The cron endpoint receives a normal HTTP request. Verify it's from Vercel:

```ts
export async function GET(req: Request) {
  const authHeader = req.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 })
  }
  // Do scheduled work
  return Response.json({ ok: true })
}
```

## Configuration via vercel.json

**Deprecation notice**: Support for the legacy `now.json` config file will be removed on **March 31, 2026**. Rename `now.json` to `vercel.json` (no content changes required).

```json
{
  "functions": {
    "app/api/heavy/**": {
      "maxDuration": 300,
      "memory": 1024
    },
    "app/api/edge/**": {
      "runtime": "edge"
    }
  }
}
```

## Timeout Limits

All plans now default to 300s execution time with Fluid Compute.

| Plan | Default | Max |
|------|---------|-----|
| Hobby | 300s | 300s |
| Pro | 300s | 800s |
| Enterprise | 300s | 800s |

## Common Pitfalls

1. **Cold starts with DB connections**: Use connection pooling (e.g., Neon's `@neondatabase/serverless`)
2. **Edge limitations**: No `fs`, no native modules, limited `crypto` — use Node.js runtime if needed
3. **Timeout exceeded**: Use Fluid Compute for long-running tasks, or Workflow DevKit for very long processes
4. **Bundle size**: Functions support up to 5 GB package size on Fluid Compute (up from 250 MB); request bodies up to 100 MB (up from 4.5 MB)
5. **Environment variables**: Available in all functions automatically; use `vercel env pull` for local dev

## Function Runtime Diagnostics

### Timeout Diagnostics

```
504 Gateway Timeout?
├─ All plans default to 300s with Fluid Compute
├─ Pro/Enterprise: configurable up to 800s
├─ Long-running task?
│  ├─ Under 5 min → Use Fluid Compute with streaming
│  ├─ Up to 15 min → Use Vercel Functions with `maxDuration` in vercel.json
│  └─ Hours/days → Use Workflow DevKit (DurableAgent or workflow steps)
└─ DB query slow? → Add connection pooling, check cold start, use Edge Config
```

### 500 Error Diagnostics

```
500 Internal Server Error?
├─ Check Vercel Runtime Logs (Dashboard → Deployments → Functions tab)
├─ Missing env vars? → Compare `.env.local` against Vercel dashboard settings
├─ Import error? → Verify package is in `dependencies`, not `devDependencies`
└─ Uncaught exception? → Wrap handler in try/catch, use `after()` for error reporting
```

### Invocation Failure Diagnostics

```
"FUNCTION_INVOCATION_FAILED"?
├─ Memory exceeded? → Increase `memory` in vercel.json (up to 3008 MB on Pro)
├─ Crashed during init? → Check top-level await or heavy imports at module scope
└─ Edge Function crash? → Check for Node.js APIs not available in Edge runtime
```

### Cold Start Diagnostics

```
Cold start latency > 1s?
├─ Using Node.js runtime? → Consider Edge Functions for latency-sensitive routes
├─ Large function bundle? → Audit imports, use dynamic imports, tree-shake
├─ DB connection in cold start? → Use connection pooling (Neon serverless driver)
└─ Enable Fluid Compute to reuse warm instances across requests
```

### Edge Function Timeout Diagnostics

```
"EDGE_FUNCTION_INVOCATION_TIMEOUT"?
├─ Edge Functions have 25s hard limit (not configurable)
├─ Move heavy computation to Node.js Serverless Functions
└─ Use streaming to start response early, process in background with `waitUntil`
```

## Official Documentation

- [Vercel Functions](https://vercel.com/docs/functions)
- [Serverless Functions](https://vercel.com/docs/functions)
- [Edge Functions](https://vercel.com/docs/functions)
- [Fluid Compute](https://vercel.com/docs/fluid-compute)
- [Streaming](https://vercel.com/docs/functions/streaming)
- [WebSockets](https://vercel.com/docs/functions/websockets)
- [Cron Jobs](https://vercel.com/docs/cron-jobs)
- [GitHub: Vercel](https://github.com/vercel/vercel)
