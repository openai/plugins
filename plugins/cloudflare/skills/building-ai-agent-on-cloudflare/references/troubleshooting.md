# Agent Troubleshooting

Common issues and solutions for Cloudflare Agents.

## Connection Issues

### "WebSocket connection failed"

**Symptoms:** Client cannot connect to agent.

**Causes & Solutions:**

1. **Worker not deployed**
   ```bash
   wrangler deployments list
   wrangler deploy  # If not deployed
   ```

2. **Wrong URL path**
   ```javascript
   // Ensure your routing handles the agent path
   // Client:
   new WebSocket("wss://my-worker.workers.dev/agent/user123");

   // Worker must route to agent:
   if (url.pathname.startsWith("/agent/")) {
     const id = url.pathname.split("/")[2];
     return env.AGENT.get(env.AGENT.idFromName(id)).fetch(request);
   }
   ```

3. **CORS issues (browser clients)**
   Agents handle WebSocket upgrades automatically, but ensure your entry worker doesn't block the request.

### "Connection closed unexpectedly"

1. **Agent threw an error**
   ```bash
   wrangler tail  # Check for exceptions
   ```

2. **Message handler crashed**
   ```typescript
   async onMessage(connection: Connection, message: string) {
     try {
       // Your logic
     } catch (error) {
       console.error("Message handling error:", error);
       connection.send(JSON.stringify({ type: "error", message: error.message }));
     }
   }
   ```

3. **Hibernation woke agent with stale connection**
   Ensure you handle reconnection gracefully in client code.

## State Issues

### "State not persisting"

**Causes:**

1. **Didn't call `setState()`**
   ```typescript
   // Wrong - direct mutation doesn't persist
   this.state.messages.push(newMessage);

   // Correct - use setState
   this.setState({
     ...this.state,
     messages: [...this.state.messages, newMessage],
   });
   ```

2. **Agent crashed before state saved**
   `setState()` is durable, but if agent crashes during processing before `setState()`, changes are lost.

3. **Wrong agent instance**
   Each unique ID gets a separate agent. Ensure clients connect to the same ID.

### "State out of sync between clients"

`setState()` automatically syncs to all connected clients via `onStateUpdate()`. If sync isn't working:

1. **Check `onStateUpdate` is implemented**
   ```typescript
   onStateUpdate(state: State, source: string) {
     // This fires when state changes from any source
     console.log("State updated:", state, "from:", source);
   }
   ```

2. **Client not listening for state updates**
   ```typescript
   // React hook handles this automatically
   const { state } = useAgent({ agent: "my-agent", name: id });

   // Manual WebSocket - listen for state messages
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     if (data.type === "state_update") {
       updateLocalState(data.state);
     }
   };
   ```

### "State too large" / Performance issues

State is serialized as JSON. Keep it small:

```typescript
// Bad - storing everything in state
interface State {
  allMessages: Message[];  // Could be thousands
  allDocuments: Document[];
}

// Good - state for hot data, SQL for cold
interface State {
  recentMessages: Message[];  // Last 50 only
  currentDocument: Document | null;
}

// Store full history in SQL
await this.sql`INSERT INTO messages ...`;
```

## SQL Issues

### "no such table"

Table not created. Create in `onStart()`:

```typescript
async onStart() {
  await this.sql`
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      content TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `;
}
```

### "SQL logic error"

Check your query syntax. Use tagged templates correctly:

```typescript
// Wrong - string interpolation (SQL injection risk!)
await this.sql`SELECT * FROM users WHERE id = '${userId}'`;

// Correct - parameterized query
await this.sql`SELECT * FROM users WHERE id = ${userId}`;
```

### SQL query returns empty

1. **Wrong table name**
2. **Data in different agent instance** (each agent ID has isolated storage)
3. **Query conditions don't match**

Debug:
```typescript
const tables = await this.sql`
  SELECT name FROM sqlite_master WHERE type='table'
`;
console.log("Tables:", tables);

const count = await this.sql`SELECT COUNT(*) as count FROM messages`;
console.log("Message count:", count);
```

## Scheduled Task Issues

### "Task never fires"

1. **Method name mismatch**
   ```typescript
   // Schedule references method that must exist
   await this.schedule(60, "sendReminder", { ... });

   // Method must be defined on the class
   async sendReminder(data: any) {
     // This method MUST exist
   }
   ```

2. **Cron syntax error**
   ```typescript
   // Invalid cron
   await this.schedule("every 5 minutes", "task", {});  // Wrong

   // Valid cron
   await this.schedule("*/5 * * * *", "task", {});  // Every 5 minutes
   ```

3. **Task was cancelled**
   ```typescript
   const schedules = await this.getSchedules();
   console.log("Active schedules:", schedules);
   ```

### "Task fires multiple times"

If you schedule in `onStart()` without checking:

```typescript
async onStart() {
  // Bad - schedules new task every time agent wakes
  await this.schedule("0 9 * * *", "dailyTask", {});

  // Good - check first
  const schedules = await this.getSchedules();
  const hasDaily = schedules.some(s => s.callback === "dailyTask");
  if (!hasDaily) {
    await this.schedule("0 9 * * *", "dailyTask", {});
  }
}
```

## Deployment Issues

### "Class MyAgent is not exported"

```typescript
// src/index.ts - Must export the class
export { MyAgent } from "./agent";

// Or if defined in same file
export class MyAgent extends Agent { ... }
```

### "Durable Object not found"

Check `wrangler.toml`:

```toml
[durable_objects]
bindings = [{ name = "AGENT", class_name = "MyAgent" }]

[[migrations]]
tag = "v1"
new_classes = ["MyAgent"]
```

### "Migration required"

When adding new Durable Object classes:

```toml
[[migrations]]
tag = "v2"  # Increment from previous
new_classes = ["NewAgentClass"]

# Or for renames
# renamed_classes = [{ from = "OldName", to = "NewName" }]
```

## AI Integration Issues

### "AI binding not found"

Add to `wrangler.toml`:

```toml
[ai]
binding = "AI"
```

### "Model not found" / "Rate limited"

```typescript
// Check model name is correct
const response = await this.env.AI.run(
  "@cf/meta/llama-3-8b-instruct",  // Exact model name
  { messages: [...] }
);

// Handle rate limits
try {
  const response = await this.env.AI.run(...);
} catch (error) {
  if (error.message.includes("rate limit")) {
    // Retry with backoff or use queue
  }
}
```

### "Streaming not working"

```typescript
// Enable streaming
const stream = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
  messages: [...],
  stream: true,  // Must be true
});

// Iterate over stream
for await (const chunk of stream) {
  connection.send(JSON.stringify({ type: "chunk", content: chunk.response }));
}
```

## Debugging Tips

### Enable Verbose Logging

```typescript
export class MyAgent extends Agent<Env, State> {
  async onStart() {
    console.log("Agent starting, state:", JSON.stringify(this.state));
  }

  async onConnect(connection: Connection) {
    console.log("Client connected:", connection.id);
  }

  async onMessage(connection: Connection, message: string) {
    console.log("Received message:", message);
    // ... handle
    console.log("State after:", JSON.stringify(this.state));
  }

  async onClose(connection: Connection) {
    console.log("Client disconnected:", connection.id);
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
# Connect with test client or use browser console:
# new WebSocket("ws://localhost:8787/agent/test")
```

### Inspect State

Add a debug endpoint:

```typescript
async onRequest(request: Request) {
  const url = new URL(request.url);

  if (url.pathname === "/debug") {
    return Response.json({
      state: this.state,
      schedules: await this.getSchedules(),
    });
  }

  return new Response("Not found", { status: 404 });
}
```
