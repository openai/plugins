# MCP Server Troubleshooting

Common errors and solutions for MCP servers on Cloudflare.

## Connection Issues

### "Failed to connect to MCP server"

**Symptoms:** Client cannot establish connection to deployed server.

**Causes & Solutions:**

1. **Wrong URL path**
   ```
   # Wrong
   https://my-server.workers.dev/

   # Correct
   https://my-server.workers.dev/mcp
   ```

2. **Worker not deployed**
   ```bash
   wrangler deployments list
   # If empty, deploy first:
   wrangler deploy
   ```

3. **Worker crashed on startup**
   ```bash
   wrangler tail
   # Check for initialization errors
   ```

### "WebSocket connection failed"

MCP uses SSE (Server-Sent Events), not WebSockets. Ensure your client is configured for SSE transport:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["mcp-remote", "https://my-server.workers.dev/mcp"]
    }
  }
}
```

### CORS Errors in Browser

If calling from browser-based client:

```typescript
// Add CORS headers to your worker
export default {
  async fetch(request: Request, env: Env) {
    // Handle preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    const response = await handleRequest(request, env);

    // Add CORS headers to response
    const headers = new Headers(response.headers);
    headers.set("Access-Control-Allow-Origin", "*");

    return new Response(response.body, {
      status: response.status,
      headers,
    });
  },
};
```

## Tool Errors

### "Tool not found: [tool_name]"

**Causes:**

1. Tool not registered in `init()`
2. Tool name mismatch (case-sensitive)
3. `init()` threw an error before registering tool

**Debug:**

```typescript
async init() {
  console.log("Registering tools...");

  this.server.tool("my_tool", { ... }, async () => { ... });

  console.log("Tools registered:", this.server.listTools());
}
```

Check logs: `wrangler tail`

### "Invalid parameters for tool"

Zod validation failed. Check parameter schema:

```typescript
// Schema expects number, client sent string
this.server.tool(
  "calculate",
  { value: z.number() },  // Client must send number, not "123"
  async ({ value }) => { ... }
);

// Fix: Coerce string to number
this.server.tool(
  "calculate",
  { value: z.coerce.number() },  // "123" → 123
  async ({ value }) => { ... }
);
```

### Tool Timeout

Workers have CPU time limits (10-30ms for free, longer for paid). For long operations:

```typescript
this.server.tool(
  "long_operation",
  { ... },
  async (params) => {
    // Break into smaller chunks
    // Or use Queues/Durable Objects for background work

    // Don't do this:
    // await sleep(5000);  // Will timeout

    return { content: [{ type: "text", text: "Queued for processing" }] };
  }
);
```

## Authentication Errors

### "401 Unauthorized"

OAuth token missing or expired.

1. **Check client is handling OAuth flow**
2. **Verify secrets are set:**
   ```bash
   wrangler secret list
   # Should show GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
   ```

3. **Check KV namespace exists:**
   ```bash
   wrangler kv namespace list
   # Should show OAUTH_KV
   ```

### "Invalid redirect_uri"

OAuth callback URL doesn't match app configuration.

**Local development:**
- OAuth app callback: `http://localhost:8788/callback`

**Production:**
- OAuth app callback: `https://[worker-name].[account].workers.dev/callback`

Must match EXACTLY (including trailing slash or lack thereof).

### "State mismatch" / CSRF Error

State parameter validation failed.

1. **Clear browser cookies and retry**
2. **Check KV is storing state:**
   ```typescript
   // In your auth handler
   console.log("Storing state:", state);
   await env.OAUTH_KV.put(`state:${state}`, "1", { expirationTtl: 600 });
   ```

3. **Verify same domain for all requests**

## Binding Errors

### "Binding not found: [BINDING_NAME]"

Binding not in `wrangler.toml` or not deployed.

```toml
# wrangler.toml
[[d1_databases]]
binding = "DB"           # Must match env.DB in code
database_name = "mydb"
database_id = "xxx-xxx"
```

After adding bindings: `wrangler deploy`

### "D1_ERROR: no such table"

Migrations not applied.

```bash
# Local
wrangler d1 migrations apply DB_NAME --local

# Production
wrangler d1 migrations apply DB_NAME
```

### Durable Object Not Found

```toml
# wrangler.toml must have:
[durable_objects]
bindings = [{ name = "MCP", class_name = "MyMCP" }]

[[migrations]]
tag = "v1"
new_classes = ["MyMCP"]
```

And class must be exported:

```typescript
export { MyMCP };  // Don't forget this!
```

## Deployment Errors

### "Class MyMCP is not exported"

```typescript
// src/index.ts - Must export the class
export { MyMCP } from "./mcp";

// OR in same file
export class MyMCP extends McpAgent { ... }
```

### "Migration required"

New Durable Object class needs migration:

```toml
# Add to wrangler.toml
[[migrations]]
tag = "v2"  # Increment version
new_classes = ["NewClassName"]
# Or for renames:
# renamed_classes = [{ from = "OldName", to = "NewName" }]
```

### Build Errors

```bash
# Clear cache and rebuild
rm -rf node_modules .wrangler
npm install
wrangler deploy
```

## Debugging Tips

### Enable Verbose Logging

```typescript
export class MyMCP extends McpAgent {
  async init() {
    console.log("MCP Server initializing...");
    console.log("Environment:", Object.keys(this.env));

    this.server.tool("test", {}, async () => {
      console.log("Test tool called");
      return { content: [{ type: "text", text: "OK" }] };
    });

    console.log("Tools registered");
  }
}
```

View logs:
```bash
wrangler tail --format pretty
```

### Test Locally First

```bash
npm start
npx @modelcontextprotocol/inspector@latest
```

Always verify tools work locally before deploying.

### Check Worker Health

```bash
# List deployments
wrangler deployments list

# View recent logs
wrangler tail

# Check worker status
curl -I https://your-worker.workers.dev/mcp
```
