---
name: micro
description: Expert guidance for micro — asynchronous HTTP microservices framework by Vercel. Use when building lightweight HTTP servers, API endpoints, or microservices using the micro library.
metadata:
  priority: 4
  docs:
    - "https://github.com/vercel/micro"
  pathPatterns: []
  importPatterns:
    - 'micro'
    - 'micro-dev'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bmicro\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bmicro\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bmicro\b'
    - '\byarn\s+add\s+[^\n]*\bmicro\b'
    - '\bnpx\s+micro\b'
    - '\bnpx\s+micro-dev\b'
---

# micro — Asynchronous HTTP Microservices

You are an expert in micro, Vercel's lightweight framework for building asynchronous HTTP microservices in Node.js. micro makes it easy to write single-purpose HTTP endpoints with minimal boilerplate.

## Installation

```bash
npm install micro
```

## Basic Usage

Create a module that exports a request handler:

```ts
// index.ts
import { serve } from 'micro'

const handler = (req: Request) => {
  return new Response('Hello, World!')
}

serve(handler)
```

Or use the classic API:

```ts
import { IncomingMessage, ServerResponse } from 'http'

export default (req: IncomingMessage, res: ServerResponse) => {
  res.end('Hello, World!')
}
```

Run with:

```bash
npx micro
```

## Core API

### `json(req)` — Parse JSON Body

```ts
import { json } from 'micro'

export default async (req: IncomingMessage, res: ServerResponse) => {
  const body = await json(req)
  return { received: body }
}
```

### `text(req)` — Parse Text Body

```ts
import { text } from 'micro'

export default async (req: IncomingMessage, res: ServerResponse) => {
  const body = await text(req)
  return `You said: ${body}`
}
```

### `buffer(req)` — Parse Raw Body

```ts
import { buffer } from 'micro'

export default async (req: IncomingMessage, res: ServerResponse) => {
  const raw = await buffer(req)
  return `Received ${raw.length} bytes`
}
```

### `send(res, statusCode, data)` — Send Response

```ts
import { send } from 'micro'

export default (req: IncomingMessage, res: ServerResponse) => {
  send(res, 200, { status: 'ok' })
}
```

### `createError(statusCode, message)` — HTTP Errors

```ts
import { createError } from 'micro'

export default (req: IncomingMessage, res: ServerResponse) => {
  if (!req.headers.authorization) {
    throw createError(401, 'Unauthorized')
  }
  return { authorized: true }
}
```

## Development with micro-dev

`micro-dev` provides hot-reloading for development:

```bash
npm install --save-dev micro-dev

# Run in dev mode
npx micro-dev index.js
```

## Composition

Chain multiple handlers with function composition:

```ts
import { IncomingMessage, ServerResponse } from 'http'

const cors = (fn: Function) => async (req: IncomingMessage, res: ServerResponse) => {
  res.setHeader('Access-Control-Allow-Origin', '*')
  return fn(req, res)
}

const handler = async (req: IncomingMessage, res: ServerResponse) => {
  return { hello: 'world' }
}

export default cors(handler)
```

## package.json Setup

```json
{
  "main": "index.js",
  "scripts": {
    "start": "micro",
    "dev": "micro-dev"
  },
  "dependencies": {
    "micro": "^10.0.0"
  },
  "devDependencies": {
    "micro-dev": "^3.0.0"
  }
}
```

## Key Points

1. **Return values are sent as responses** — return strings, objects (auto-serialized to JSON), or Buffers
2. **Async by default** — handlers can be async functions, errors are caught automatically
3. **Thrown errors become HTTP errors** — use `createError()` for proper status codes
4. **No routing built-in** — micro is a single-endpoint server; use a router like `micro-router` for multi-route services
5. **Body parsing is explicit** — use `json()`, `text()`, or `buffer()` to parse request bodies
6. **Composable** — wrap handlers with higher-order functions for middleware-like behavior

## Official Resources

- [micro GitHub](https://github.com/vercel/micro)
