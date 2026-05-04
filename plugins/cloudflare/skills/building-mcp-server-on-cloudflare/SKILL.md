---
name: building-mcp-server-on-cloudflare
description: |
  Builds remote MCP (Model Context Protocol) servers on Cloudflare Workers
  with tools, OAuth authentication, and production deployment. Generates
  server code, configures auth providers, and deploys to Workers.

  Use when: user wants to "build MCP server", "create MCP tools", "remote
  MCP", "deploy MCP", add "OAuth to MCP", or mentions Model Context Protocol
  on Cloudflare. Also triggers on "MCP authentication" or "MCP deployment".
  Biases towards retrieval from Cloudflare docs over pre-trained knowledge.
---

# Building MCP Servers on Cloudflare

Your knowledge of the MCP SDK and Cloudflare Workers integration may be outdated. **Prefer retrieval over pre-training** for any MCP server task.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| MCP docs | `https://developers.cloudflare.com/agents/mcp/` | Server setup, auth, deployment |
| MCP spec | `https://modelcontextprotocol.io/` | Protocol spec, tool/resource definitions |
| Workers docs | Search tool or `https://developers.cloudflare.com/workers/` | Runtime APIs, bindings, config |

## When to Use

- User wants to build a remote MCP server
- User needs to expose tools via MCP
- User asks about MCP authentication or OAuth
- User wants to deploy MCP to Cloudflare Workers

## Prerequisites

- Cloudflare account with Workers enabled
- Node.js 18+ and npm/pnpm/yarn
- Wrangler CLI (`npm install -g wrangler`)

## Quick Start

### Option 1: Public Server (No Auth)

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-authless
cd my-mcp-server
npm start
```

Server runs at `http://localhost:8788/mcp`

### Option 2: Authenticated Server (OAuth)

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-github-oauth
cd my-mcp-server
```

Requires OAuth app setup. See [references/oauth-setup.md](references/oauth-setup.md).

## Core Workflow

### Step 1: Define Tools

Tools are functions MCP clients can call. Define them using `server.tool()`:

```typescript
import { McpAgent } from "agents/mcp";
import { z } from "zod";

export class MyMCP extends McpAgent {
  server = new Server({ name: "my-mcp", version: "1.0.0" });

  async init() {
    // Simple tool with parameters
    this.server.tool(
      "add",
      { a: z.number(), b: z.number() },
      async ({ a, b }) => ({
        content: [{ type: "text", text: String(a + b) }],
      })
    );

    // Tool that calls external API
    this.server.tool(
      "get_weather",
      { city: z.string() },
      async ({ city }) => {
        const response = await fetch(`https://api.weather.com/${city}`);
        const data = await response.json();
        return {
          content: [{ type: "text", text: JSON.stringify(data) }],
        };
      }
    );
  }
}
```

### Step 2: Configure Entry Point

**Public server** (`src/index.ts`):

```typescript
import { MyMCP } from "./mcp";

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url);
    if (url.pathname === "/mcp") {
      return MyMCP.serveSSE("/mcp").fetch(request, env, ctx);
    }
    return new Response("MCP Server", { status: 200 });
  },
};

export { MyMCP };
```

**Authenticated server** — See [references/oauth-setup.md](references/oauth-setup.md).

### Step 3: Test Locally

```bash
# Start server
npm start

# In another terminal, test with MCP Inspector
npx @modelcontextprotocol/inspector@latest
# Open http://localhost:5173, enter http://localhost:8788/mcp
```

### Step 4: Deploy

```bash
npx wrangler deploy
```

Server accessible at `https://[worker-name].[account].workers.dev/mcp`

### Step 5: Connect Clients

**Codex MCP client setup:**

```bash
codex mcp add my-server -- npx mcp-remote https://my-mcp.workers.dev/mcp
```

Restart Codex after updating the MCP configuration.

## Tool Patterns

### Return Types

```typescript
// Text response
return { content: [{ type: "text", text: "result" }] };

// Multiple content items
return {
  content: [
    { type: "text", text: "Here's the data:" },
    { type: "text", text: JSON.stringify(data, null, 2) },
  ],
};
```

### Input Validation with Zod

```typescript
this.server.tool(
  "create_user",
  {
    email: z.string().email(),
    name: z.string().min(1).max(100),
    role: z.enum(["admin", "user", "guest"]),
    age: z.number().int().min(0).optional(),
  },
  async (params) => {
    // params are fully typed and validated
  }
);
```

### Accessing Environment/Bindings

```typescript
export class MyMCP extends McpAgent<Env> {
  async init() {
    this.server.tool("query_db", { sql: z.string() }, async ({ sql }) => {
      // Access D1 binding
      const result = await this.env.DB.prepare(sql).all();
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    });
  }
}
```

## Authentication

For OAuth-protected servers, see [references/oauth-setup.md](references/oauth-setup.md).

Supported providers:
- GitHub
- Google
- Auth0
- Stytch
- WorkOS
- Any OAuth 2.0 compliant provider

## Wrangler Configuration

Minimal `wrangler.toml`:

```toml
name = "my-mcp-server"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[durable_objects]
bindings = [{ name = "MCP", class_name = "MyMCP" }]

[[migrations]]
tag = "v1"
new_classes = ["MyMCP"]
```

With bindings (D1, KV, etc.):

```toml
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxx"

[[kv_namespaces]]
binding = "KV"
id = "xxx"
```

## Common Issues

### "Tool not found" in Client

1. Verify tool name matches exactly (case-sensitive)
2. Ensure `init()` registers tools before connections
3. Check server logs: `wrangler tail`

### Connection Fails

1. Confirm endpoint path is `/mcp`
2. Check CORS if browser-based client
3. Verify Worker is deployed: `wrangler deployments list`

### OAuth Redirect Errors

1. Callback URL must match OAuth app config exactly
2. Check `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set
3. For local dev, use `http://localhost:8788/callback`

## References

- [references/examples.md](references/examples.md) — Official templates and production examples
- [references/oauth-setup.md](references/oauth-setup.md) — OAuth provider configuration
- [references/troubleshooting.md](references/troubleshooting.md) — Error codes and fixes
