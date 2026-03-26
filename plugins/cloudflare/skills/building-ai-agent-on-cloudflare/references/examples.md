# Project Bootstrapping

Instructions for creating new agent projects.

---

## Create Command

Execute in terminal to generate a new project:

```bash
npm create cloudflare@latest -- my-agent \
  --template=cloudflare/agents-starter
```

Or use npx directly:

```bash
npx create-cloudflare@latest --template cloudflare/agents-starter
```

Includes:
- Persistent data via `this.setState` and `this.sql`
- WebSocket real-time connections
- Workers AI bindings ready
- React chat interface example

---

## Project Layout

Generated structure:

```
my-agent/
├── src/
│   ├── app.tsx       # React chat interface
│   ├── server.ts     # Agent implementation
│   ├── tools.ts      # Tool definitions
│   └── utils.ts      # Helpers
├── wrangler.toml     # Platform configuration
└── package.json
```

---

## Agent Variations

**Chat-focused:**

Inherit from base `Agent` class, implement `onMessage` handler:
- Manual conversation tracking
- Full control over responses
- Integrates with any AI provider

**Persistent data:**

Use `this.setState()` for automatic persistence:
- JSON-serializable data
- Auto-syncs to connected clients
- Survives instance eviction

**Per-session isolation:**

Route by unique identifier in URL path:
- Each identifier gets dedicated instance
- Isolated data storage
- Horizontal scaling automatic

---

## Platform Documentation

- developers.cloudflare.com/agents/
- developers.cloudflare.com/agents/getting-started/
- developers.cloudflare.com/agents/api-reference/

**Source repositories:**
- `github.com/cloudflare/agents-starter` (starter template)
- `github.com/cloudflare/agents/tree/main/examples` (reference implementations)

**Related services:**

- developers.cloudflare.com/workers-ai/ (AI models)
- developers.cloudflare.com/vectorize/ (vector search)
- developers.cloudflare.com/d1/ (SQL database)

---

## Reference Implementations

Located at `github.com/cloudflare/agents/tree/main/examples`:

| Example | Description |
|---------|-------------|
| `resumable-stream-chat` | Chat with reconnection-safe streaming |
| `email-agent` | Handle incoming emails via Email Routing |
| `mcp-client` | Connect agents to external MCP servers |
| `mcp-worker` | Expose agent capabilities via MCP protocol |
| `cross-domain` | Multi-domain authentication patterns |
| `tictactoe` | Multiplayer game with shared state |
| `a2a` | Agent-to-agent communication |
| `codemode` | Code transformation workflows |
| `playground` | Interactive testing sandbox |

Browse each folder for complete implementation code and wrangler configuration.

---

## Selection Matrix

| Goal | Approach |
|------|----------|
| Conversational bot | Agent + onMessage handler |
| Custom data schema | Agent + setState() |
| Knowledge retrieval | Agent + Vectorize |
| Background jobs | Agent + schedule() |
| External integrations | Agent + tool definitions |

---

## Commands Reference

**Local execution:**

```bash
cd my-agent
npm install
npm start
# Accessible at http://localhost:8787
```

**Production push:**

```bash
npx wrangler deploy
# Accessible at https://[name].[subdomain].workers.dev
```

**WebSocket connection:**

```javascript
// URL pattern: /agents/:className/:instanceName
const socket = new WebSocket("wss://my-agent.workers.dev/agents/MyAgent/session-123");

socket.onmessage = (e) => {
  console.log("Received:", JSON.parse(e.data));
};

socket.send(JSON.stringify({ type: "chat", content: "Hello" }));
```

**React integration:**

```tsx
import { useAgent } from "agents/react";

function Chat() {
  const { state, send } = useAgent({
    agent: "my-agent",
    name: "session-123",
  });

  // state auto-updates, send() dispatches messages
}
```

---

## Key Methods (from Agent class)

| Method | Purpose |
|--------|---------|
| `onStart()` | Runs on instance startup |
| `onConnect()` | Handles new WebSocket connections |
| `onMessage()` | Processes incoming messages |
| `onClose()` | Cleanup on disconnect |
| `setState()` | Persist and broadcast data |
| `this.sql` | Query embedded SQLite |
| `schedule()` | Delayed/recurring tasks |
| `broadcast()` | Message all connections |

---

## Help Channels

- Cloudflare Discord
- GitHub discussions on cloudflare/agents repository
