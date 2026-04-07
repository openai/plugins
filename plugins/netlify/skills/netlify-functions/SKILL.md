---
name: netlify-functions
description: Guide for writing Netlify serverless functions. Use when creating API endpoints, background processing, scheduled tasks, or any server-side logic using Netlify Functions. Covers modern syntax (default export + Config), TypeScript, path routing, background functions, scheduled functions, streaming, and method routing.
---

# Netlify Functions

## Modern Syntax

Always use the modern default export + Config pattern. Never use the legacy `exports.handler` or named `handler` export.

```typescript
import type { Context, Config } from "@netlify/functions";

export default async (req: Request, context: Context) => {
  return new Response("Hello, world!");
};

export const config: Config = {
  path: "/api/hello",
};
```

The handler receives a standard Web API `Request` and returns a `Response`. The second argument is a Netlify `Context` object.

## File Structure

Place functions in `netlify/functions/`:

```
netlify/functions/
  _shared/           # Non-function shared code (underscore prefix)
    auth.ts
    db.ts
  items.ts           # -> /.netlify/functions/items (or custom path via config)
  users/index.ts     # -> /.netlify/functions/users
```

Use `.ts` or `.mts` extensions. If both `.ts` and `.js` exist with the same name, the `.js` file takes precedence.

## Path Routing

Define custom paths via the `config` export:

```typescript
export const config: Config = {
  path: "/api/items",                    // Static path
  // path: "/api/items/:id",            // Path parameter
  // path: ["/api/items", "/api/items/:id"], // Multiple paths
  // excludedPath: "/api/items/special", // Excluded paths
  // preferStatic: true,                // Don't override static files
};
```

Without a `path` config, functions are available at `/.netlify/functions/{name}`. Setting a `path` makes the function available **only** at that path.

Access path parameters via `context.params`:

```typescript
// config: { path: "/api/items/:id" }
export default async (req: Request, context: Context) => {
  const { id } = context.params;
  // ...
};
```

## Method Routing

```typescript
export default async (req: Request, context: Context) => {
  switch (req.method) {
    case "GET":    return handleGet(context.params.id);
    case "POST":   return handlePost(await req.json());
    case "DELETE": return handleDelete(context.params.id);
    default:       return new Response("Method not allowed", { status: 405 });
  }
};

export const config: Config = {
  path: "/api/items/:id",
  method: ["GET", "POST", "DELETE"],
};
```

## Background Functions

For long-running tasks (up to 15 minutes). The client receives an immediate `202` response; return values are ignored.

Name the file with a `-background` suffix:

```
netlify/functions/process-background.ts
```

Store results externally (Netlify Blobs, database) for later retrieval.

## Scheduled Functions

Run on a cron schedule (UTC timezone):

```typescript
export default async (req: Request) => {
  const { next_run } = await req.json();
  console.log("Next invocation at:", next_run);
};

export const config: Config = {
  schedule: "@hourly", // or cron: "0 * * * *"
};
```

Shortcuts: `@yearly`, `@monthly`, `@weekly`, `@daily`, `@hourly`. Scheduled functions have a **30-second timeout** and only run on published deploys.

## Streaming Responses

Return a `ReadableStream` body for streamed responses (up to 20 MB):

```typescript
export default async (req: Request) => {
  const stream = new ReadableStream({ /* ... */ });
  return new Response(stream, {
    headers: { "Content-Type": "text/event-stream" },
  });
};
```

## Context Object

| Property | Description |
|---|---|
| `context.params` | Path parameters from config |
| `context.geo` | `{ city, country: {code, name}, latitude, longitude, subdivision, timezone, postalCode }` |
| `context.ip` | Client IP address |
| `context.cookies` | `.get()`, `.set()`, `.delete()` |
| `context.deploy` | `{ context, id, published }` |
| `context.site` | `{ id, name, url }` |
| `context.account.id` | Team account ID |
| `context.requestId` | Unique request ID |
| `context.waitUntil(promise)` | Extend execution after response is sent |

## Environment Variables

Use `Netlify.env` (not `process.env`) inside functions:

```typescript
const apiKey = Netlify.env.get("API_KEY");
```

## Resource Limits

| Resource | Limit |
|---|---|
| Synchronous timeout | 60 seconds |
| Background timeout | 15 minutes |
| Scheduled timeout | 30 seconds |
| Memory | 1024 MB |
| Buffered payload | 6 MB |
| Streamed payload | 20 MB |

## Framework Considerations

Frameworks with server-side capabilities (Astro, Next.js, Nuxt, SvelteKit, TanStack Start) typically generate their own serverless functions via adapters. You usually do not write raw Netlify Functions in these projects — the framework adapter handles server-side rendering and API routes. Write Netlify Functions directly when:

- Using a client-side-only framework (Vite + React SPA, vanilla JS)
- Adding background or scheduled tasks to any project
- Building standalone API endpoints outside the framework's routing

See the **netlify-frameworks** skill for adapter setup.
