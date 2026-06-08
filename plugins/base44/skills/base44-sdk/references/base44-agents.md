# Agents Module

AI agent conversations and messages via `base44.agents`.

> **Note:** This module requires a logged-in user. All agent methods work in the context of the authenticated user.

## Contents
- [Concepts](#concepts)
- [Methods](#methods)
- [Examples](#examples) (Create, Get Conversations, List, Subscribe, Send Message, WhatsApp)
- [Message Structure](#message-structure)
- [Conversation Structure](#conversation-structure)
- [Common Patterns](#common-patterns)

## Concepts

- **Conversation**: A dialogue between user and an AI agent. Has unique ID, agent name, user reference, and metadata.
- **Message**: Single message in a conversation. Has role (`user`, `assistant`, `system`), content, timestamps, and optional metadata.

## Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `createConversation(params)` | `Promise<Conversation>` | Create a new conversation with an agent |
| `getConversations()` | `Promise<Conversation[]>` | Get all user's conversations |
| `getConversation(id)` | `Promise<Conversation>` | Get conversation with messages (includes full tool call results) |
| `listConversations(filterParams)` | `Promise<Conversation[]>` | Filter/sort/paginate conversations |
| `subscribeToConversation(id, onUpdate?)` | `() => void` | Realtime updates via WebSocket; tool call data truncated (returns unsubscribe function) |
| `addMessage(conversation, message)` | `Promise<Message>` | Send a message |
| `getWhatsAppConnectURL(agentName)` | `string` | Get WhatsApp connection URL for agent |

## Examples

### Create Conversation

```javascript
const conversation = await base44.agents.createConversation({
  agent_name: "support-agent",
  metadata: {
    order_id: "ORD-123",
    category: "billing"
  }
});

console.log(conversation.id);
```

### Get All Conversations

```javascript
const conversations = await base44.agents.getConversations();

conversations.forEach(conv => {
  console.log(conv.id, conv.agent_name, conv.created_date);
});
```

### Get Single Conversation (with messages)

Returns the complete stored conversation including full tool call results (unlike the realtime subscription, which truncates tool call data).

```javascript
const conversation = await base44.agents.getConversation("conv-id-123");

console.log(conversation.messages);
```

### List with Filters

```javascript
// Using filterParams object with q, sort, limit, skip, fields
const recent = await base44.agents.listConversations({
  q: { agent_name: "support-agent" },
  sort: "-created_date",
  limit: 10,
  skip: 0
});

// Filter by metadata
const highPriority = await base44.agents.listConversations({
  q: {
    agent_name: "support-agent",
    "metadata.priority": "high"
  },
  sort: "-updated_date",
  limit: 20
});
```

### Subscribe to Updates (Realtime)

When receiving messages through this subscription, tool call data is truncated for efficiency (`arguments_string` limited to 500 characters, `results` to 50). Use `getConversation()` after the message completes to retrieve full tool call data.

```javascript
const unsubscribe = base44.agents.subscribeToConversation(
  "conv-id-123",
  (updatedConversation) => {
    // Called when new messages arrive
    console.log("New messages:", updatedConversation.messages);
  }
);

// Later: unsubscribe
unsubscribe();
```

### Send a Message

```javascript
const conversation = await base44.agents.getConversation("conv-id-123");

await base44.agents.addMessage(conversation, {
  role: "user",
  content: "What's the weather like today?"
});
```

### Get WhatsApp Connection URL

```javascript
const whatsappUrl = base44.agents.getWhatsAppConnectURL("support-agent");
// Returns URL for users to connect with agent via WhatsApp
console.log(whatsappUrl);
```

## Message Structure

```javascript
{
  role: "user" | "assistant" | "system",
  content: "Message text or structured object",
  created_date: "2024-01-15T10:30:00Z",
  updated_date: "2024-01-15T10:30:00Z",
  
  // Optional fields
  reasoning: {
    content: "Agent's reasoning process",
    timing: 1500
  },
  tool_calls: [{
    name: "search",
    arguments: { query: "weather" },
    result: { ... },
    status: "success"
  }],
  file_urls: ["https://..."],
  usage: {
    prompt_tokens: 150,
    completion_tokens: 50
  },
  metadata: { ... },
  custom_context: { ... }
}
```

## Conversation Structure

```javascript
{
  id: "conv-id-123",
  app_id: "app-id",
  agent_name: "support-agent",
  created_by_id: "user-id",
  created_date: "2024-01-15T10:00:00Z",
  updated_date: "2024-01-15T10:30:00Z",
  messages: [ ... ],
  metadata: { ... }
}
```

## Common Patterns

### Chat Interface

```javascript
// Load conversation
const conv = await base44.agents.getConversation(conversationId);
setMessages(conv.messages);

// Subscribe to updates
const unsubscribe = base44.agents.subscribeToConversation(conversationId, (updated) => {
  setMessages(updated.messages);
});

// Send message
async function sendMessage(text) {
  await base44.agents.addMessage(conv, { role: "user", content: text });
}

// Cleanup on unmount
return () => unsubscribe();
```

## Type Definitions

### AgentNameRegistry and AgentName

**How to get typed agent names:** The Base44 CLI can generate an augmentation of `AgentNameRegistry` from your project. For how to run it, use the **base44-cli** skill.

```typescript
/**
 * Registry of agent names.
 * Augment this interface to enable autocomplete for agent names.
 * Typically populated by the Base44 CLI type generator.
 */
interface AgentNameRegistry {}

/**
 * Agent name type - uses registry keys if augmented, otherwise string.
 */
type AgentName = keyof AgentNameRegistry extends never ? string : keyof AgentNameRegistry;
```

### AgentConversation

```typescript
/** An agent conversation containing messages exchanged with an AI agent. */
interface AgentConversation {
  /** Unique identifier for the conversation. */
  id: string;
  /** Application ID. */
  app_id: string;
  /** Name of the agent in this conversation. */
  agent_name: string;
  /** ID of the user who created the conversation. */
  created_by_id: string;
  /** When the conversation was created. */
  created_date: string;
  /** When the conversation was last updated. */
  updated_date: string;
  /** Array of messages in the conversation. */
  messages: AgentMessage[];
  /** Optional metadata associated with the conversation. */
  metadata?: Record<string, any>;
}
```

### AgentMessage

```typescript
/** A message in an agent conversation. */
interface AgentMessage {
  /** Unique identifier for the message. */
  id: string;
  /** Role of the message sender. */
  role: "user" | "assistant" | "system";
  /** When the message was created. */
  created_date: string;
  /** When the message was last updated. */
  updated_date: string;
  /** Message content. */
  content?: string | Record<string, any>;
  /** Optional reasoning information for the message. */
  reasoning?: AgentMessageReasoning | null;
  /** URLs to files attached to the message. */
  file_urls?: string[];
  /** Tool calls made by the agent. */
  tool_calls?: AgentMessageToolCall[];
  /** Token usage statistics. */
  usage?: AgentMessageUsage;
  /** Whether the message is hidden from the user. */
  hidden?: boolean;
  /** Custom context provided with the message. */
  custom_context?: AgentMessageCustomContext[];
  /** Model used to generate the message. */
  model?: string;
  /** Checkpoint ID for the message. */
  checkpoint_id?: string;
  /** Metadata about when and by whom the message was created. */
  metadata?: AgentMessageMetadata;
}
```

### Supporting Types

```typescript
/** Reasoning information for an agent message. */
interface AgentMessageReasoning {
  /** When reasoning started. */
  start_date: string;
  /** When reasoning ended. */
  end_date?: string;
  /** Reasoning content. */
  content: string;
}

/** A tool call made by the agent. */
interface AgentMessageToolCall {
  /** Tool call ID. */
  id: string;
  /** Name of the tool called. */
  name: string;
  /** Arguments passed to the tool as JSON string. */
  arguments_string: string;
  /** Status of the tool call. */
  status: "running" | "success" | "error" | "stopped";
  /** Results from the tool call. */
  results?: string;
}

/** Token usage statistics for an agent message. */
interface AgentMessageUsage {
  /** Number of tokens in the prompt. */
  prompt_tokens?: number;
  /** Number of tokens in the completion. */
  completion_tokens?: number;
}

/** Custom context provided with an agent message. */
interface AgentMessageCustomContext {
  /** Context message. */
  message: string;
  /** Associated data for the context. */
  data: Record<string, any>;
  /** Type of context. */
  type: string;
}

/** Metadata about when and by whom a message was created. */
interface AgentMessageMetadata {
  /** When the message was created. */
  created_date: string;
  /** Email of the user who created the message. */
  created_by_email: string;
  /** Full name of the user who created the message. */
  created_by_full_name: string;
}
```

### CreateConversationParams

```typescript
/** Parameters for creating a new conversation. */
interface CreateConversationParams {
  /** The name of the agent to create a conversation with. */
  agent_name: AgentName;
  /** Optional metadata to attach to the conversation. */
  metadata?: Record<string, any>;
}
```

### ModelFilterParams

```typescript
/** Parameters for filtering, sorting, and paginating conversations. */
interface ModelFilterParams {
  /** Query object with field-value pairs for filtering. */
  q?: Record<string, any>;
  /** Sort parameter (e.g., "-created_date" for descending). */
  sort?: string | null;
  /** Maximum number of results to return. */
  limit?: number | null;
  /** Number of results to skip for pagination. */
  skip?: number | null;
  /** Array of field names to include in the response. */
  fields?: string[] | null;
}
```

### AgentsModule

```typescript
/** Agents module for managing AI agent conversations. */
interface AgentsModule {
  /** Gets all conversations from all agents in the app. */
  getConversations(): Promise<AgentConversation[]>;

  /** Gets a specific conversation by ID. Returns complete stored conversation including full tool call results. */
  getConversation(conversationId: string): Promise<AgentConversation | undefined>;

  /** Lists conversations with filtering, sorting, and pagination. */
  listConversations(filterParams: ModelFilterParams): Promise<AgentConversation[]>;

  /** Creates a new conversation with an agent. */
  createConversation(conversation: CreateConversationParams): Promise<AgentConversation>;

  /** Adds a message to a conversation. */
  addMessage(conversation: AgentConversation, message: Partial<AgentMessage>): Promise<AgentMessage>;

  /** Subscribes to realtime updates for a conversation. Returns unsubscribe function. */
  subscribeToConversation(conversationId: string, onUpdate?: (conversation: AgentConversation) => void): () => void;

  /** Gets WhatsApp connection URL for an agent. */
  getWhatsAppConnectURL(agentName: AgentName): string;
}
```
