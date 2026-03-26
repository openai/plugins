---
name: building-ai-agent-on-cloudflare
description: |
  Builds AI agents on Cloudflare using the Agents SDK with state management,
  real-time WebSockets, scheduled tasks, tool integration, and chat capabilities.
  Generates production-ready agent code deployed to Workers.

  Use when: user wants to "build an agent", "AI agent", "chat agent", "stateful
  agent", mentions "Agents SDK", needs "real-time AI", "WebSocket AI", or asks
  about agent "state management", "scheduled tasks", or "tool calling".
  Biases towards retrieval from Cloudflare docs over pre-trained knowledge.
---

# Building Cloudflare Agents

Your knowledge of the Agents SDK may be outdated. **Prefer retrieval over pre-training** for any agent-building task.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Agents SDK docs | `https://github.com/cloudflare/agents/tree/main/docs` | SDK API, state, routing, scheduling |
| Cloudflare Agents docs | `https://developers.cloudflare.com/agents/` | Platform integration, deployment |
| Workers docs | Search tool or `https://developers.cloudflare.com/workers/` | Runtime APIs, bindings, config |

## When to Use

- User wants to build an AI agent or chatbot
- User needs stateful, real-time AI interactions
- User asks about the Cloudflare Agents SDK
- User wants scheduled tasks or background AI work
- User needs WebSocket-based AI communication

## Prerequisites

- Cloudflare account with Workers enabled
- Node.js 18+ and npm/pnpm/yarn
- Wrangler CLI (`npm install -g wrangler`)

## Quick Start

```bash
npm create cloudflare@latest -- my-agent --template=cloudflare/agents-starter
cd my-agent
npm start
```

Agent runs at `http://localhost:8787`

## Core Concepts

### What is an Agent?

An Agent is a stateful, persistent AI service that:
- Maintains state across requests and reconnections
- Communicates via WebSockets or HTTP
- Runs on Cloudflare's edge via Durable Objects
- Can schedule tasks and call tools
- Scales horizontally (each user/session gets own instance)

### Agent Lifecycle

```
Client connects → Agent.onConnect() → Agent processes messages
                                    → Agent.onMessage()
                                    → Agent.setState() (persists + syncs)
Client disconnects → State persists → Client reconnects → State restored
```

## Basic Agent Structure

```typescript
import { Agent, Connection } from "agents";

interface Env {
  AI: Ai;  // Workers AI binding
}

interface State {
  messages: Array<{ role: string; content: string }>;
  preferences: Record<string, string>;
}

export class MyAgent extends Agent<Env, State> {
  // Initial state for new instances
  initialState: State = {
    messages: [],
    preferences: {},
  };

  // Called when agent starts or resumes
  async onStart() {
    console.log("Agent started with state:", this.state);
  }

  // Handle WebSocket connections
  async onConnect(connection: Connection) {
    connection.send(JSON.stringify({
      type: "welcome",
      history: this.state.messages,
    }));
  }

  // Handle incoming messages
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "chat") {
      await this.handleChat(connection, data.content);
    }
  }

  // Handle disconnections
  async onClose(connection: Connection) {
    console.log("Client disconnected");
  }

  // React to state changes
  onStateUpdate(state: State, source: string) {
    console.log("State updated by:", source);
  }

  private async handleChat(connection: Connection, userMessage: string) {
    // Add user message to history
    const messages = [
      ...this.state.messages,
      { role: "user", content: userMessage },
    ];

    // Call AI
    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages,
    });

    // Update state (persists and syncs to all clients)
    this.setState({
      ...this.state,
      messages: [
        ...messages,
        { role: "assistant", content: response.response },
      ],
    });

    // Send response
    connection.send(JSON.stringify({
      type: "response",
      content: response.response,
    }));
  }
}
```

## Entry Point Configuration

```typescript
// src/index.ts
import { routeAgentRequest } from "agents";
import { MyAgent } from "./agent";

export default {
  async fetch(request: Request, env: Env) {
    // routeAgentRequest handles routing to /agents/:class/:name
    return (
      (await routeAgentRequest(request, env)) ||
      new Response("Not found", { status: 404 })
    );
  },
};

export { MyAgent };
```

Clients connect via: `wss://my-agent.workers.dev/agents/MyAgent/session-id`

## Wrangler Configuration

```toml
name = "my-agent"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[ai]
binding = "AI"

[durable_objects]
bindings = [{ name = "AGENT", class_name = "MyAgent" }]

[[migrations]]
tag = "v1"
new_classes = ["MyAgent"]
```

## State Management

### Reading State

```typescript
// Current state is always available
const currentMessages = this.state.messages;
const userPrefs = this.state.preferences;
```

### Updating State

```typescript
// setState persists AND syncs to all connected clients
this.setState({
  ...this.state,
  messages: [...this.state.messages, newMessage],
});

// Partial updates work too
this.setState({
  preferences: { ...this.state.preferences, theme: "dark" },
});
```

### SQL Storage

For complex queries, use the embedded SQLite database:

```typescript
// Create tables
await this.sql`
  CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`;

// Insert
await this.sql`
  INSERT INTO documents (title, content)
  VALUES (${title}, ${content})
`;

// Query
const docs = await this.sql`
  SELECT * FROM documents WHERE title LIKE ${`%${search}%`}
`;
```

## Scheduled Tasks

Agents can schedule future work:

```typescript
async onMessage(connection: Connection, message: string) {
  const data = JSON.parse(message);

  if (data.type === "schedule_reminder") {
    // Schedule task for 1 hour from now
    const { id } = await this.schedule(3600, "sendReminder", {
      message: data.reminderText,
      userId: data.userId,
    });

    connection.send(JSON.stringify({ type: "scheduled", taskId: id }));
  }
}

// Called when scheduled task fires
async sendReminder(data: { message: string; userId: string }) {
  // Send notification, email, etc.
  console.log(`Reminder for ${data.userId}: ${data.message}`);

  // Can also update state
  this.setState({
    ...this.state,
    lastReminder: new Date().toISOString(),
  });
}
```

### Schedule Options

```typescript
// Delay in seconds
await this.schedule(60, "taskMethod", { data });

// Specific date
await this.schedule(new Date("2025-01-01T00:00:00Z"), "taskMethod", { data });

// Cron expression (recurring)
await this.schedule("0 9 * * *", "dailyTask", {});  // 9 AM daily
await this.schedule("*/5 * * * *", "everyFiveMinutes", {});  // Every 5 min

// Manage schedules
const schedules = await this.getSchedules();
await this.cancelSchedule(taskId);
```

## Chat Agent (AI-Powered)

For chat-focused agents, extend `AIChatAgent`:

```typescript
import { AIChatAgent } from "agents/ai-chat-agent";

export class ChatBot extends AIChatAgent<Env> {
  // Called for each user message
  async onChatMessage(message: string) {
    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        ...this.messages,  // Automatic history management
        { role: "user", content: message },
      ],
      stream: true,
    });

    // Stream response back to client
    return response;
  }
}
```

Features included:
- Automatic message history
- Resumable streaming (survives disconnects)
- Built-in `saveMessages()` for persistence

## Client Integration

### React Hook

```tsx
import { useAgent } from "agents/react";

function Chat() {
  const { state, send, connected } = useAgent({
    agent: "my-agent",
    name: userId,  // Agent instance ID
  });

  const sendMessage = (text: string) => {
    send(JSON.stringify({ type: "chat", content: text }));
  };

  return (
    <div>
      {state.messages.map((msg, i) => (
        <div key={i}>{msg.role}: {msg.content}</div>
      ))}
      <input onKeyDown={(e) => e.key === "Enter" && sendMessage(e.target.value)} />
    </div>
  );
}
```

### Vanilla JavaScript

```javascript
const ws = new WebSocket("wss://my-agent.workers.dev/agents/MyAgent/user123");

ws.onopen = () => {
  console.log("Connected to agent");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

ws.send(JSON.stringify({ type: "chat", content: "Hello!" }));
```

## Common Patterns

See [references/agent-patterns.md](references/agent-patterns.md) for:
- Tool calling and function execution
- Multi-agent orchestration
- RAG (Retrieval Augmented Generation)
- Human-in-the-loop workflows

## Deployment

```bash
# Deploy
npx wrangler deploy

# View logs
wrangler tail

# Test endpoint
curl https://my-agent.workers.dev/agents/MyAgent/test-user
```

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for common issues.

## References

- [references/examples.md](references/examples.md) — Official templates and production examples
- [references/agent-patterns.md](references/agent-patterns.md) — Advanced patterns
- [references/state-patterns.md](references/state-patterns.md) — State management strategies
- [references/troubleshooting.md](references/troubleshooting.md) — Error solutions
