# State Management Patterns

Strategies for managing state in Cloudflare Agents.

## How State Works

State is automatically persisted to the `cf_agents_state` SQL table. The `this.state` getter lazily loads from storage, while `this.setState()` serializes and persists changes. State survives Durable Object evictions.

```typescript
class MyAgent extends Agent<Env, { count: number }> {
  initialState = { count: 0 };

  increment() {
    this.setState({ count: this.state.count + 1 });
  }

  onStateUpdate(state: State, source: string) {
    console.log("State updated by:", source);
  }
}
```

## State vs SQL: When to Use Which

### Use `this.state` + `setState()` When:

- Data is small (< 1MB recommended)
- Needs real-time sync to all connected clients
- Simple key-value or object structure
- Frequently read, occasionally updated

```typescript
interface State {
  currentUser: { id: string; name: string };
  preferences: Record<string, string>;
  recentMessages: Message[];  // Keep limited, e.g., last 50
  isTyping: boolean;
}
```

### Use `this.sql` When:

- Large datasets (many records)
- Complex queries (JOINs, aggregations, filtering)
- Historical data / audit logs
- Data that doesn't need real-time sync

```typescript
// Good for SQL
// - Full message history
// - User documents
// - Analytics events
// - Search indexes
```

## Hybrid Pattern

Combine both for optimal performance:

```typescript
interface State {
  recentMessages: Message[];
  onlineUsers: string[];
  currentDocument: Document | null;
}

export class HybridAgent extends Agent<Env, State> {
  initialState: State = {
    recentMessages: [],
    onlineUsers: [],
    currentDocument: null,
  };

  async onStart() {
    await this.sql`
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `;

    const recent = await this.sql`
      SELECT * FROM messages
      ORDER BY created_at DESC
      LIMIT 50
    `;

    this.setState({
      ...this.state,
      recentMessages: recent.reverse(),
    });
  }

  async addMessage(message: Message) {
    await this.sql`
      INSERT INTO messages (id, user_id, content)
      VALUES (${message.id}, ${message.userId}, ${message.content})
    `;

    const recentMessages = [...this.state.recentMessages, message].slice(-50);
    this.setState({ ...this.state, recentMessages });
  }
}
```

---

## Queue System

The SDK includes a built-in queue for background task processing. Tasks are stored in SQLite and processed in FIFO order.

### Queue Methods

| Method | Purpose |
|--------|---------|
| `queue(callback, payload)` | Add task, returns task ID |
| `dequeue(id)` | Remove specific task |
| `dequeueAll()` | Clear entire queue |
| `dequeueAllByCallback(name)` | Remove tasks by callback name |
| `getQueue(id)` | Get single task |
| `getQueues(key, value)` | Find tasks by payload field |

### Queue Example

```typescript
export class TaskAgent extends Agent<Env, State> {
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "process_later") {
      const taskId = await this.queue("processItem", {
        itemId: data.itemId,
        priority: data.priority,
      });

      connection.send(JSON.stringify({ queued: true, taskId }));
    }
  }

  // Callback receives payload and QueueItem metadata
  async processItem(payload: { itemId: string }, item: QueueItem) {
    console.log(`Processing ${payload.itemId}, queued at ${item.createdAt}`);
    // Successfully executed tasks are auto-removed
  }
}
```

**Queue characteristics:**
- Sequential processing (no parallelization)
- Persists across agent restarts
- No built-in retry mechanism
- Payloads must be JSON-serializable

---

## Context Management

Custom methods automatically have full agent context. Use `getCurrentAgent()` to access context from external functions.

```typescript
import { getCurrentAgent } from "agents";

// External utility function
async function logActivity(action: string) {
  const { agent } = getCurrentAgent<MyAgent>();
  await agent.sql`
    INSERT INTO activity_log (action, timestamp)
    VALUES (${action}, ${Date.now()})
  `;
}

export class MyAgent extends Agent<Env, State> {
  async performAction() {
    // Context automatically available
    await logActivity("action_performed");
  }
}
```

`getCurrentAgent<T>()` returns:
- `agent` - The current agent instance
- `connection` - Connection object (if applicable)
- `request` - Request object (if applicable)

---

## State Synchronization

### Optimistic Updates

Update UI immediately, then persist:

```typescript
async onMessage(connection: Connection, message: string) {
  const data = JSON.parse(message);

  if (data.type === "update_preference") {
    this.setState({
      ...this.state,
      preferences: {
        ...this.state.preferences,
        [data.key]: data.value,
      },
    });

    await this.sql`
      INSERT OR REPLACE INTO preferences (key, value)
      VALUES (${data.key}, ${data.value})
    `;
  }
}
```

### Conflict Resolution

Handle concurrent updates with versioning:

```typescript
interface State {
  document: {
    content: string;
    version: number;
    lastModifiedBy: string;
  };
}

async updateDocument(userId: string, newContent: string, expectedVersion: number) {
  if (this.state.document.version !== expectedVersion) {
    throw new Error("Conflict: document was modified by another user");
  }

  this.setState({
    ...this.state,
    document: {
      content: newContent,
      version: expectedVersion + 1,
      lastModifiedBy: userId,
    },
  });
}
```

### Per-Connection State

Track ephemeral state for each connected client:

```typescript
export class MultiUserAgent extends Agent<Env, State> {
  private connectionState = new Map<string, {
    userId: string;
    cursor: { x: number; y: number };
    lastActivity: number;
  }>();

  async onConnect(connection: Connection) {
    this.connectionState.set(connection.id, {
      userId: "",
      cursor: { x: 0, y: 0 },
      lastActivity: Date.now(),
    });
  }

  async onClose(connection: Connection) {
    this.connectionState.delete(connection.id);
  }
}
```

---

## State Migration

When state schema changes:

```typescript
interface StateV2 {
  messages: Array<{ id: string; content: string; timestamp: string }>;
  version: 2;
}

export class MigratingAgent extends Agent<Env, StateV2> {
  initialState: StateV2 = {
    messages: [],
    version: 2,
  };

  async onStart() {
    const rawState = this.state as any;

    if (!rawState.version || rawState.version < 2) {
      const migratedMessages = (rawState.messages || []).map(
        (content: string, i: number) => ({
          id: `migrated-${i}`,
          content,
          timestamp: new Date().toISOString(),
        })
      );

      this.setState({
        messages: migratedMessages,
        version: 2,
      });
    }
  }
}
```

---

## State Size Management

Keep state lean for performance:

```typescript
export class LeanStateAgent extends Agent<Env, State> {
  private readonly MAX_RECENT_MESSAGES = 100;

  async addMessage(message: Message) {
    await this.sql`INSERT INTO messages (id, content) VALUES (${message.id}, ${message.content})`;

    let recentMessages = [...this.state.recentMessages, message];
    if (recentMessages.length > this.MAX_RECENT_MESSAGES) {
      recentMessages = recentMessages.slice(-this.MAX_RECENT_MESSAGES);
    }

    this.setState({
      ...this.state,
      recentMessages,
      stats: {
        ...this.state.stats,
        totalMessages: this.state.stats.totalMessages + 1,
        lastActivity: new Date().toISOString(),
      },
    });
  }
}
```

---

## Debugging State

```typescript
async onMessage(connection: Connection, message: string) {
  const data = JSON.parse(message);

  if (data.type === "debug_state") {
    connection.send(JSON.stringify({
      type: "debug_response",
      state: this.state,
      stateSize: JSON.stringify(this.state).length,
      sqlTables: await this.sql`
        SELECT name FROM sqlite_master WHERE type='table'
      `,
    }));
  }
}
```
