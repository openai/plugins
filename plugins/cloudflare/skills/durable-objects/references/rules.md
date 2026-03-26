# Durable Objects Rules & Best Practices

## Design & Sharding

### Model Around Coordination Atoms

Create one DO per logical unit needing coordination: chat room, game session, document, user, tenant.

```typescript
// ✅ Good: One DO per chat room
const stub = env.CHAT_ROOM.getByName(roomId);

// ❌ Bad: Single global DO
const stub = env.CHAT_ROOM.getByName("global"); // Bottleneck!
```

### Parent-Child Relationships

For hierarchical data, create separate child DOs. Parent tracks references, children handle own state.

```typescript
// Parent: GameServer tracks match references
// Children: GameMatch handles individual match state
async createMatch(name: string): Promise<string> {
  const matchId = crypto.randomUUID();
  this.ctx.storage.sql.exec(
    "INSERT INTO matches (id, name) VALUES (?, ?)",
    matchId, name
  );
  const child = this.env.GAME_MATCH.getByName(matchId);
  await child.init(matchId, name);
  return matchId;
}
```

### Location Hints

Influence DO creation location for latency-sensitive apps:

```typescript
const id = env.GAME.idFromName(gameId, { locationHint: "wnam" });
```

Available hints: `wnam`, `enam`, `sam`, `weur`, `eeur`, `apac`, `oc`, `afr`, `me`.

## Storage

### SQLite (Recommended)

Configure in wrangler:
```jsonc
{ "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyDO"] }] }
```

SQL API is synchronous:
```typescript
// Write
this.ctx.storage.sql.exec(
  "INSERT INTO items (name, value) VALUES (?, ?)",
  name, value
);

// Read
const rows = this.ctx.storage.sql.exec<{ id: number; name: string }>(
  "SELECT * FROM items WHERE name = ?", name
).toArray();

// Single row
const row = this.ctx.storage.sql.exec<{ count: number }>(
  "SELECT COUNT(*) as count FROM items"
).one();
```

### Migrations

**Note:** `PRAGMA user_version` is **not supported** in Durable Objects SQLite storage. Use a `_sql_schema_migrations` table instead:

```typescript
constructor(ctx: DurableObjectState, env: Env) {
  super(ctx, env);
  ctx.blockConcurrencyWhile(async () => this.migrate());
}

private migrate() {
  this.ctx.storage.sql.exec(`
    CREATE TABLE IF NOT EXISTS _sql_schema_migrations (
      id INTEGER PRIMARY KEY,
      applied_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
  `);

  const currentVersion = this.ctx.storage.sql
    .exec<{ version: number }>("SELECT COALESCE(MAX(id), 0) as version FROM _sql_schema_migrations")
    .one().version;

  if (currentVersion < 1) {
    this.ctx.storage.sql.exec(`
      CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, data TEXT);
      CREATE INDEX IF NOT EXISTS idx_items_data ON items(data);
      INSERT INTO _sql_schema_migrations (id) VALUES (1);
    `);
  }
  if (currentVersion < 2) {
    this.ctx.storage.sql.exec(`
      ALTER TABLE items ADD COLUMN created_at INTEGER;
      INSERT INTO _sql_schema_migrations (id) VALUES (2);
    `);
  }
}
```

For production apps, consider [`durable-utils`](https://github.com/lambrospetrou/durable-utils#sqlite-schema-migrations) — provides a `SQLSchemaMigrations` class that tracks executed migrations both in memory and in storage. Also see [`@cloudflare/actors` storage utilities](https://github.com/cloudflare/actors/blob/main/packages/storage/src/sql-schema-migrations.ts) — a reference implementation of the same pattern used by the Cloudflare Actors framework.

### State Types

| Type | Speed | Persistence | Use Case |
|------|-------|-------------|----------|
| Class properties | Fastest | Lost on eviction | Caching, active connections |
| SQLite storage | Fast | Durable | Primary data |
| External (R2, D1) | Variable | Durable, cross-DO | Large files, shared data |

**Rule**: Always persist critical state to SQLite first, then update in-memory cache.

## Concurrency

### Input/Output Gates

Storage operations automatically block other requests (input gates). Responses wait for writes (output gates).

```typescript
async increment(): Promise<number> {
  // Safe: input gates block interleaving during storage ops
  const val = (await this.ctx.storage.get<number>("count")) ?? 0;
  await this.ctx.storage.put("count", val + 1);
  return val + 1;
}
```

### Write Coalescing

Multiple writes without `await` between them are batched atomically:

```typescript
// ✅ Good: All three writes commit atomically
this.ctx.storage.sql.exec("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromId);
this.ctx.storage.sql.exec("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toId);
this.ctx.storage.sql.exec("INSERT INTO transfers (from_id, to_id, amount) VALUES (?, ?, ?)", fromId, toId, amount);

// ❌ Bad: await breaks coalescing
await this.ctx.storage.put("key1", val1);
await this.ctx.storage.put("key2", val2); // Separate transaction!
```

### Race Conditions with External I/O

`fetch()` and other non-storage I/O allows interleaving:

```typescript
// ⚠️ Race condition possible
async processItem(id: string) {
  const item = await this.ctx.storage.get<Item>(`item:${id}`);
  if (item?.status === "pending") {
    await fetch("https://api.example.com/process"); // Other requests can run here!
    await this.ctx.storage.put(`item:${id}`, { status: "completed" });
  }
}
```

**Solution**: Use optimistic locking (version numbers) or `transaction()`.

### blockConcurrencyWhile()

Blocks ALL concurrency. Use sparingly - only for initialization:

```typescript
// ✅ Good: One-time init
constructor(ctx: DurableObjectState, env: Env) {
  super(ctx, env);
  ctx.blockConcurrencyWhile(async () => this.migrate());
}

// ❌ Bad: On every request (kills throughput)
async handleRequest() {
  await this.ctx.blockConcurrencyWhile(async () => {
    // ~5ms = max 200 req/sec
  });
}
```

**Never** hold across external I/O (fetch, R2, KV).

## RPC Methods

Use RPC (compatibility date >= 2024-04-03) instead of fetch() handler:

```typescript
export class ChatRoom extends DurableObject<Env> {
  async sendMessage(userId: string, content: string): Promise<Message> {
    // Public methods are RPC endpoints
    const result = this.ctx.storage.sql.exec<{ id: number }>(
      "INSERT INTO messages (user_id, content) VALUES (?, ?) RETURNING id",
      userId, content
    );
    return { id: result.one().id, userId, content };
  }
}

// Caller
const stub = env.CHAT_ROOM.getByName(roomId);
const msg = await stub.sendMessage("user-123", "Hello!"); // Typed!
```

### Explicit init() Method

DOs don't know their own ID. Pass identity explicitly:

```typescript
async init(entityId: string, metadata: Metadata): Promise<void> {
  await this.ctx.storage.put("entityId", entityId);
  await this.ctx.storage.put("metadata", metadata);
}
```

## Alarms

One alarm per DO. `setAlarm()` replaces existing.

```typescript
// Schedule
await this.ctx.storage.setAlarm(Date.now() + 60_000);

// Handler
async alarm(): Promise<void> {
  const tasks = this.ctx.storage.sql.exec<Task>(
    "SELECT * FROM tasks WHERE due_at <= ?", Date.now()
  ).toArray();
  
  for (const task of tasks) {
    await this.processTask(task);
  }
  
  // Reschedule if more work
  const next = this.ctx.storage.sql.exec<{ due_at: number }>(
    "SELECT MIN(due_at) as due_at FROM tasks WHERE due_at > ?", Date.now()
  ).one();
  if (next?.due_at) {
    await this.ctx.storage.setAlarm(next.due_at);
  }
}

// Get/Delete
const alarm = await this.ctx.storage.getAlarm();
await this.ctx.storage.deleteAlarm();
```

**Retry**: Alarms auto-retry on failure. Use idempotent handlers.

## WebSockets (Hibernation API)

```typescript
async fetch(request: Request): Promise<Response> {
  const pair = new WebSocketPair();
  this.ctx.acceptWebSocket(pair[1]);
  return new Response(null, { status: 101, webSocket: pair[0] });
}

async webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
  const data = JSON.parse(message as string);
  // Handle message
  ws.send(JSON.stringify({ type: "ack" }));
}

async webSocketClose(ws: WebSocket, code: number, reason: string) {
  // Cleanup
}

// Broadcast
getWebSockets().forEach(ws => ws.send(JSON.stringify(payload)));
```

## Error Handling

```typescript
async safeOperation(): Promise<Result> {
  try {
    return await this.riskyOperation();
  } catch (error) {
    console.error("Operation failed:", error);
    // Log to external service if needed
    throw error; // Re-throw to signal failure to caller
  }
}
```

**Note**: Uncaught exceptions may terminate the DO instance. In-memory state is lost, but SQLite storage persists.
