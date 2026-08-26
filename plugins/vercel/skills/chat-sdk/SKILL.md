---
name: chat-sdk
description: Vercel Chat SDK expert guidance. Use when building multi-platform chat bots — Slack, Telegram, Microsoft Teams, Discord, Google Chat, GitHub, Linear — with a single codebase. Covers the Chat class, adapters, threads, messages, cards, modals, streaming, state management, and webhook setup.
metadata:
  priority: 8
  docs:
    - "https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot"
    - "https://github.com/vercel/ai-chatbot"
  sitemap: "https://sdk.vercel.ai/sitemap.xml"
  pathPatterns:
    - "app/api/chat/**"
    - "app/api/chat-bot/**"
    - "app/api/bot/**"
    - "app/api/slack/**"
    - "app/api/teams/**"
    - "app/api/discord/**"
    - "app/api/gchat/**"
    - "app/api/telegram/**"
    - "app/api/github-bot/**"
    - "app/api/linear-bot/**"
    - "app/api/webhooks/slack/**"
    - "app/api/webhooks/teams/**"
    - "app/api/webhooks/discord/**"
    - "app/api/webhooks/gchat/**"
    - "app/api/webhooks/telegram/**"
    - "app/api/webhooks/github/**"
    - "app/api/webhooks/linear/**"
    - "src/app/api/chat/**"
    - "src/app/api/chat-bot/**"
    - "src/app/api/bot/**"
    - "src/app/api/slack/**"
    - "src/app/api/teams/**"
    - "src/app/api/discord/**"
    - "src/app/api/gchat/**"
    - "src/app/api/telegram/**"
    - "lib/bot.*"
    - "lib/bot/**"
    - "src/lib/bot.*"
    - "src/lib/bot/**"
    - "lib/chat-bot/**"
    - "src/lib/chat-bot/**"
    - "bot/**"
    - "pages/api/bot.*"
    - "pages/api/bot/**"
    - "src/pages/api/bot.*"
    - "src/pages/api/bot/**"
    - "tests/**/bot*"
    - "test/**/bot*"
    - "fixtures/replay/**"
    - "apps/*/app/api/bot/**"
    - "apps/*/app/api/slack/**"
    - "apps/*/app/api/teams/**"
    - "apps/*/app/api/discord/**"
    - "apps/*/lib/bot/**"
    - "apps/*/src/lib/bot/**"
  importPatterns:
    - "chat"
    - "@chat-adapter/*"
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bchat\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bchat\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bchat\b'
    - '\byarn\s+add\s+[^\n]*\bchat\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@chat-adapter/'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@chat-adapter/'
    - '\bbun\s+(install|i|add)\s+[^\n]*@chat-adapter/'
    - '\byarn\s+add\s+[^\n]*@chat-adapter/'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@chat-adapter/telegram'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@chat-adapter/telegram'
    - '\bbun\s+(install|i|add)\s+[^\n]*@chat-adapter/telegram'
    - '\byarn\s+add\s+[^\n]*@chat-adapter/telegram'
  promptSignals:
    phrases:
      - "chat sdk"
      - "chat bot"
      - "chatbot"
      - "conversational interface"
      - "slack bot"
      - "telegram bot"
      - "discord bot"
      - "teams bot"
    allOf:
      - [bot, platform]
      - [bot, multi]
    anyOf:
      - "onNewMention"
      - "onSubscribedMessage"
      - "chat adapter"
      - "cross-platform bot"
    noneOf:
      - "useChat"
    minScore: 6
---

# Chat SDK

Unified TypeScript SDK for building chat bots across Slack, Teams, Google Chat, Discord, Telegram, GitHub, Linear, and WhatsApp. Write bot logic once, deploy everywhere.

## Start with published sources

When Chat SDK is installed in a user project, inspect the published files that ship in `node_modules`:

```
node_modules/chat/docs/                    # bundled docs
node_modules/chat/dist/index.d.ts          # core API types
node_modules/chat/dist/jsx-runtime.d.ts    # JSX runtime types
node_modules/chat/docs/contributing/       # adapter-authoring docs
node_modules/chat/docs/guides/             # framework/platform guides
```

If one of the paths below does not exist, that package is not installed in the project yet.

Read these before writing code:
- `node_modules/chat/docs/getting-started.mdx` — install and setup
- `node_modules/chat/docs/usage.mdx` — `Chat` config and lifecycle
- `node_modules/chat/docs/handling-events.mdx` — event routing and handlers
- `node_modules/chat/docs/threads-messages-channels.mdx` — thread/channel/message model
- `node_modules/chat/docs/posting-messages.mdx` — post, edit, delete, schedule
- `node_modules/chat/docs/streaming.mdx` — AI SDK integration and streaming semantics
- `node_modules/chat/docs/cards.mdx` — JSX cards
- `node_modules/chat/docs/actions.mdx` — button/select interactions
- `node_modules/chat/docs/modals.mdx` — modal submit/close flows
- `node_modules/chat/docs/slash-commands.mdx` — slash command routing
- `node_modules/chat/docs/direct-messages.mdx` — DM behavior and `openDM()`
- `node_modules/chat/docs/files.mdx` — attachments/uploads
- `node_modules/chat/docs/state.mdx` — persistence, locking, dedupe
- `node_modules/chat/docs/adapters.mdx` — cross-platform feature matrix
- `node_modules/chat/docs/api/chat.mdx` — exact `Chat` API
- `node_modules/chat/docs/api/thread.mdx` — exact `Thread` API
- `node_modules/chat/docs/api/message.mdx` — exact `Message` API
- `node_modules/chat/docs/api/modals.mdx` — modal element and event details

For the specific adapter or state package you are using, inspect that installed package's `dist/index.d.ts` export surface in `node_modules`.

## Quick start

```typescript
import { Chat } from "chat";
import { createSlackAdapter } from "@chat-adapter/slack";
import { createRedisState } from "@chat-adapter/state-redis";

const bot = new Chat({
  userName: "mybot",
  adapters: {
    slack: createSlackAdapter(),
  },
  state: createRedisState(),
  dedupeTtlMs: 600_000,
});

bot.onNewMention(async (thread) => {
  await thread.subscribe();
  await thread.post("Hello! I'm listening to this thread.");
});

bot.onSubscribedMessage(async (thread, message) => {
  await thread.post(`You said: ${message.text}`);
});
```

## Core concepts

- **Chat** — main entry point; coordinates adapters, routing, locks, and state
- **Adapters** — platform-specific integrations for Slack, Teams, Google Chat, Discord, Telegram, GitHub, Linear, and WhatsApp
- **State adapters** — persistence for subscriptions, locks, dedupe, and thread state
- **Thread** — conversation context with `post()`, `stream()`, `subscribe()`, `setState()`, `startTyping()`
- **Message** — normalized content with `text`, `formatted`, attachments, author info, and platform `raw`
- **Channel** — container for threads and top-level posts

## Event handlers

| Handler | Trigger |
|---------|---------|
| `onNewMention` | Bot @-mentioned in an unsubscribed thread |
| `onDirectMessage` | New DM in an unsubscribed DM thread |
| `onSubscribedMessage` | Any message in a subscribed thread |
| `onNewMessage(regex)` | Regex match in an unsubscribed thread |
| `onReaction(emojis?)` | Emoji added or removed |
| `onAction(actionIds?)` | Button clicks and select/radio interactions |
| `onModalSubmit(callbackId?)` | Modal form submitted |
| `onModalClose(callbackId?)` | Modal dismissed/cancelled |
| `onSlashCommand(commands?)` | Slash command invocation |
| `onAssistantThreadStarted` | Slack assistant thread opened |
| `onAssistantContextChanged` | Slack assistant context changed |
| `onAppHomeOpened` | Slack App Home opened |
| `onMemberJoinedChannel` | Slack member joined channel event |

Read `node_modules/chat/docs/handling-events.mdx`, `node_modules/chat/docs/actions.mdx`, `node_modules/chat/docs/modals.mdx`, and `node_modules/chat/docs/slash-commands.mdx` before wiring handlers. `onDirectMessage` behavior is documented in `node_modules/chat/docs/direct-messages.mdx`.

## Streaming

Pass any `AsyncIterable<string>` to `thread.post()` or `thread.stream()`. For AI SDK, prefer `result.fullStream` over `result.textStream` when available so step boundaries are preserved.

```typescript
import { ToolLoopAgent } from "ai";

const agent = new ToolLoopAgent({ model: "anthropic/claude-4.5-sonnet" });

bot.onNewMention(async (thread, message) => {
  const result = await agent.stream({ prompt: message.text });
  await thread.post(result.fullStream);
});
```

Key details:
- `streamingUpdateIntervalMs` controls post+edit fallback cadence
- `fallbackStreamingPlaceholderText` defaults to `"..."`; set `null` to disable
- Structured `StreamChunk` support is Slack-only; other adapters ignore non-text chunks

## Cards and modals (JSX)

Set `jsxImportSource: "chat"` in `tsconfig.json`.

Card components:
- `Card`, `CardText`, `Section`, `Fields`, `Field`, `Button`, `CardLink`, `LinkButton`, `Actions`, `Select`, `SelectOption`, `RadioSelect`, `Table`, `Image`, `Divider`

Modal components:
- `Modal`, `TextInput`, `Select`, `SelectOption`, `RadioSelect`

```tsx
await thread.post(
  <Card title="Order #1234">
    <CardText>Your order has been received.</CardText>
    <Actions>
      <Button id="approve" style="primary">Approve</Button>
      <Button id="reject" style="danger">Reject</Button>
    </Actions>
  </Card>
);
```

## Adapter inventory

### Official platform adapters

| Platform | Package | Factory |
|---------|---------|---------|
| Slack | `@chat-adapter/slack` | `createSlackAdapter` |
| Microsoft Teams | `@chat-adapter/teams` | `createTeamsAdapter` |
| Google Chat | `@chat-adapter/gchat` | `createGoogleChatAdapter` |
| Discord | `@chat-adapter/discord` | `createDiscordAdapter` |
| GitHub | `@chat-adapter/github` | `createGitHubAdapter` |
| Linear | `@chat-adapter/linear` | `createLinearAdapter` |
| Telegram | `@chat-adapter/telegram` | `createTelegramAdapter` |
| WhatsApp Business Cloud | `@chat-adapter/whatsapp` | `createWhatsAppAdapter` |

### Official state adapters

| State backend | Package | Factory |
|--------------|---------|---------|
| Redis | `@chat-adapter/state-redis` | `createRedisState` |
| ioredis | `@chat-adapter/state-ioredis` | `createIoRedisState` |
| PostgreSQL | `@chat-adapter/state-pg` | `createPostgresState` |
| Memory | `@chat-adapter/state-memory` | `createMemoryState` |

### Community adapters

- `chat-state-cloudflare-do`
- `@beeper/chat-adapter-matrix`
- `chat-adapter-imessage`
- `@bitbasti/chat-adapter-webex`
- `@resend/chat-sdk-adapter`
- `chat-adapter-baileys`

### Coming-soon platform entries

- Instagram
- Signal
- X
- Messenger

## Building a custom adapter

Read these published docs first:
- `node_modules/chat/docs/contributing/building.mdx`
- `node_modules/chat/docs/contributing/testing.mdx`
- `node_modules/chat/docs/contributing/publishing.mdx`

Also inspect:
- `node_modules/chat/dist/index.d.ts` — `Adapter` and related interfaces
- `node_modules/@chat-adapter/shared/dist/index.d.ts` — shared errors and utilities
- Installed official adapter `dist/index.d.ts` files — reference implementations for config and APIs

A custom adapter needs request verification, webhook parsing, message/thread/channel operations, ID encoding/decoding, and a format converter. Use `BaseFormatConverter` from `chat` and shared utilities from `@chat-adapter/shared`.

## Webhook setup

Each registered adapter exposes `bot.webhooks.<name>`. Wire those directly to your HTTP framework routes. See `node_modules/chat/docs/guides/slack-nextjs.mdx` and `node_modules/chat/docs/guides/discord-nuxt.mdx` for framework-specific route patterns.
