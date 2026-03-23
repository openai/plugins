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
retrieval:
  aliases:
    - chat ui
    - chatbot
    - conversation interface
    - messaging component
  intents:
    - build chatbot
    - add chat interface
    - create messaging ui
    - implement chat feature
  entities:
    - useChat
    - Message
    - ChatUI
    - StreamingMessage
    - chat-sdk
  examples:
    - build a chatbot interface
    - add chat to my app
    - create a messaging component
chainTo:
  -
    pattern: 'from\s+[''""]openai[''""]'
    targetSkill: ai-sdk
    message: 'Direct OpenAI SDK import in chat bot — loading AI SDK guidance for unified provider abstraction and streaming.'
  -
    pattern: 'from\s+[''\"](slack-bolt|@slack/bolt|@slack/web-api)[''"]|require\s*\(\s*[''\"](slack-bolt|@slack/bolt|@slack/web-api)[''"]|new\s+App\s*\(\s*\{\s*token'
    targetSkill: chat-sdk
    message: '@slack/bolt or @slack/web-api detected — use the Chat SDK with @chat-adapter/slack instead for a unified multi-platform bot that works across Slack, Teams, Discord, Telegram, and more.'
  -
    pattern: 'from\s+[''\"](discord\.js|discord-api-types|telegram-bot-api|telegraf|grammy)[''"]|require\s*\(\s*[''\"](discord\.js|telegraf|grammy)[''"]'
    targetSkill: chat-sdk
    message: 'Platform-specific bot library detected — use the Chat SDK with the corresponding @chat-adapter/* package for a unified multi-platform bot codebase.'
  -
    pattern: 'setTimeout\s*\(|setInterval\s*\(|while\s*\(\s*true'
    targetSkill: workflow
    message: 'Long-running or polling logic in chat bot — loading Workflow DevKit for durable execution that survives deploys.'
    skipIfFileContains: 'use workflow|from\s+[''"]workflow[''"]'
  -
    pattern: 'process\.env\.(OPENAI_API_KEY|ANTHROPIC_API_KEY)|from\s+[''"]@ai-sdk/(anthropic|openai)[''""]'
    targetSkill: ai-gateway
    message: 'Direct provider API key in chat bot — loading AI Gateway guidance for OIDC auth and model routing.'
    skipIfFileContains: 'gateway\(|@ai-sdk/gateway'
---

# Vercel Chat SDK

> **CRITICAL — Your training data is outdated for this library.** Chat SDK is new (v4.18+) and not in most training data. Before writing Chat SDK code, **fetch the docs** at https://chat-sdk.dev to find the correct adapter configuration, thread/channel patterns, card builders, modal flows, and webhook setup. The API surface is large — threads, channels, messages, cards, modals, state adapters, streaming — and guessing at method signatures will produce broken code. Check the GitHub repo at https://github.com/vercel/chat for working examples.

You are an expert in the Vercel Chat SDK. Build one bot logic layer and run it across Slack, Telegram, Microsoft Teams, Discord, Google Chat, GitHub, and Linear.

## Packages

- `chat@^4.18.0`
- `@chat-adapter/slack@^4.18.0`
- `@chat-adapter/telegram@^4.18.0`
- `@chat-adapter/teams@^4.18.0`
- `@chat-adapter/discord@^4.18.0`
- `@chat-adapter/gchat@^4.18.0`
- `@chat-adapter/github@^4.18.0`
- `@chat-adapter/linear@^4.18.0`
- `@chat-adapter/state-redis@^4.18.0`
- `@chat-adapter/state-ioredis@^4.18.0`
- `@chat-adapter/state-memory@^4.18.0`

## Installation

```bash
# Core SDK
npm install chat@^4.18.0

# Platform adapters (install only what you need)
npm install @chat-adapter/slack@^4.18.0
npm install @chat-adapter/telegram@^4.18.0
npm install @chat-adapter/teams@^4.18.0
npm install @chat-adapter/discord@^4.18.0
npm install @chat-adapter/gchat@^4.18.0
npm install @chat-adapter/github@^4.18.0
npm install @chat-adapter/linear@^4.18.0

# State adapters (pick one)
npm install @chat-adapter/state-redis@^4.18.0
npm install @chat-adapter/state-ioredis@^4.18.0
npm install @chat-adapter/state-memory@^4.18.0
```

## Critical API Notes

- `Field` takes an `options` array of `{ label, value }` objects. Do not pass JSX child options.
- `Thread<TState>` / `Channel<TState>` generics require object state shapes (`Record<string, unknown>`), not primitives.
- Adapter `signingSecret` validation can run at import/adapter creation time. Use lazy initialization to avoid crashing at module import.

```ts
import { createSlackAdapter } from "@chat-adapter/slack";

let slackAdapter: ReturnType<typeof createSlackAdapter> | undefined;

export function getSlackAdapter() {
  if (!slackAdapter) {
    slackAdapter = createSlackAdapter({
      signingSecret: process.env.SLACK_SIGNING_SECRET!,
    });
  }
  return slackAdapter;
}
```

## Quick Start

```ts
import { Chat } from "chat";
import { createSlackAdapter } from "@chat-adapter/slack";
import { createTelegramAdapter } from "@chat-adapter/telegram";
import { createRedisState } from "@chat-adapter/state-redis";

const bot = new Chat({
  userName: "my-bot",
  adapters: {
    slack: createSlackAdapter(),
    telegram: createTelegramAdapter(),
  },
  state: createRedisState(),
  streamingUpdateIntervalMs: 1000,
  dedupeTtlMs: 10_000,
  fallbackStreamingPlaceholderText: "Thinking...",
});

bot.onNewMention(async (thread, message) => {
  await thread.subscribe();
  await thread.post(`Received: ${message.text}`);
});

bot.onSubscribedMessage(async (thread, message) => {
  await thread.post(`Echo: ${message.text}`);
});
```

## Public API Reference

### ChatConfig

```ts
interface ChatConfig<TAdapters> {
  userName: string;
  adapters: TAdapters;
  state: StateAdapter;
  logger?: Logger | LogLevel;
  streamingUpdateIntervalMs?: number;
  dedupeTtlMs?: number;
  fallbackStreamingPlaceholderText?: string | null;
}
```

- `dedupeTtlMs`: deduplicates repeated webhook deliveries.
- `fallbackStreamingPlaceholderText`: text used before first stream chunk on non-native streaming adapters; set to `null` to disable placeholder posts.

### Chat

```ts
class Chat {
  openDM(userId: string): Promise<Channel>;
  channel(channelId: string): Channel;
}
```

- `openDM()` opens or resolves a direct message channel outside the current thread context.
- `channel()` gets a channel handle for out-of-thread posting.

### Postable

`Thread` and `Channel` share the same `Postable` interface.

```ts
interface Postable<TState extends Record<string, unknown> = Record<string, unknown>> {
  post(content: PostableContent): Promise<SentMessage>;
  postEphemeral(
    userId: string,
    content: PostableContent,
  ): Promise<SentMessage | null>;
  mentionUser(userId: string): string;
  startTyping(): Promise<void>;
  messages: AsyncIterable<Message>;
  state: Promise<TState | null>;
  setState(
    partial: Partial<TState>,
    opts?: { replace?: boolean },
  ): Promise<void>;
}
```

### Thread

```ts
interface Thread<TState extends Record<string, unknown> = Record<string, unknown>> extends Postable<TState> {
  id: string;
  channelId: string;
  subscribe(): Promise<void>;
  unsubscribe(): Promise<void>;
  isSubscribed(): Promise<boolean>;
  refresh(): Promise<void>;
  createSentMessageFromMessage(message: Message): SentMessage;
}
```

### Message

```ts
class Message<TRaw = unknown> {
  id: string;
  threadId: string;
  text: string;
  isMention: boolean;
  raw: TRaw;

  toJSON(): SerializedMessage;
  static fromJSON(data: SerializedMessage): Message;
}
```

### SentMessage

```ts
interface SentMessage extends Message {
  edit(content: PostableContent): Promise<void>;
  delete(): Promise<void>;
  addReaction(emoji: string): Promise<void>;
  removeReaction(emoji: string): Promise<void>;
}
```

Reactions are on `SentMessage`, not `Message`:
`const sent = await thread.post('Done'); await sent.addReaction('thumbsup');`

```ts
const sent = await thread.post("Done");
await sent.addReaction("thumbsup");
```

### Channel

```ts
interface Channel<TState extends Record<string, unknown> = Record<string, unknown>> extends Postable<TState> {
  id: string;
  name?: string;
}
```

## Event Handlers

### Standard handlers

- `onNewMention(handler)`
- `onSubscribedMessage(handler)`
- `onNewMessage(pattern, handler)`
- `onReaction(filter?, handler)`
- `onAction(filter?, handler)`
- `onModalSubmit(filter?, handler)`
- `onModalClose(filter?, handler)`
- `onSlashCommand(filter?, handler)`
- `onMemberJoinedChannel(handler)`

```ts
bot.onMemberJoinedChannel(async (event) => {
  await event.thread.post(`Welcome ${event.user.fullName}!`);
});
```

### Handler overloads

`onAction`, `onModalSubmit`, `onModalClose`, and `onReaction` support:

- Catch-all: `bot.onAction(async (event) => { ... })`
- Single filter: `bot.onAction("approve", async (event) => { ... })`
- Array filter: `bot.onAction(["approve", "reject"], async (event) => { ... })`

### Event payload shapes

```ts
interface ActionEvent {
  actionId: string;
  value?: string;
  triggerId?: string;
  privateMetadata?: string;
  thread: Thread;
  relatedThread?: Thread;
  relatedMessage?: Message;
  openModal: (modal: JSX.Element) => Promise<void>;
}

interface ModalEvent {
  callbackId: string;
  values: Record<string, string>;
  triggerId?: string;
  privateMetadata?: string;
  relatedThread?: Thread;
  relatedMessage?: Message;
}
```

`onModalSubmit` may return `ModalResponse` to close, validate, update, or push another modal.

## Cards & Modals

### Cards

```tsx
await thread.post(
  <Card
    title="Build Status"
    subtitle="Production"
    imageUrl="https://example.com/preview.png"
  >
    <Text style="success">Deployment succeeded.</Text>
    <Text style="muted">Commit: a1b2c3d</Text>

    <Field
      id="deploy-target"
      label="Target"
      options={[
        { label: "Staging", value: "staging" },
        { label: "Production", value: "prod" },
      ]}
      value="prod"
    />

    <Table>
      <TableRow>
        <TableCell>Region</TableCell>
        <TableCell>us-east-1</TableCell>
      </TableRow>
      <TableRow>
        <TableCell>Latency</TableCell>
        <TableCell>128ms</TableCell>
      </TableRow>
    </Table>

    <Actions>
      <Button id="rollback" style="danger">
        Rollback
      </Button>
      <CardLink url="https://vercel.com/dashboard">Open Dashboard</CardLink>
    </Actions>
  </Card>,
);
```

Card additions to use when needed:

- `Card.subtitle`
- `Card.imageUrl`
- `CardLink`
- `Field` (`options` uses `{ label, value }[]`, not JSX children)
- `Table` / `TableRow` / `TableCell` — native per-platform table rendering (**new — Mar 6, 2026**; see below)
- `Text` styles (`default`, `muted`, `success`, `warning`, `danger`, `code`)

### Table — Per-Platform Rendering (New — Mar 6, 2026)

The `Table` component renders natively on each platform:

| Platform | Rendering |
|---|---|
| Slack | Block Kit table blocks |
| Teams / Discord | GFM markdown tables |
| Google Chat | Monospace text widgets |
| Telegram | Code blocks |
| GitHub / Linear | Markdown tables (existing pipeline) |

Plain markdown tables (without `Table()`) also pass through the same adapter conversion pipeline.

```tsx
<Table>
  <TableRow>
    <TableCell>Region</TableCell>
    <TableCell>us-east-1</TableCell>
  </TableRow>
  <TableRow>
    <TableCell>Latency</TableCell>
    <TableCell>128ms</TableCell>
  </TableRow>
</Table>
```

### Modals

```tsx
await event.openModal(
  <Modal
    callbackId="deploy-form"
    title="Deploy"
    submitLabel="Deploy"
    closeLabel="Cancel"
    notifyOnClose
    privateMetadata={JSON.stringify({ releaseId: "rel_123" })}
  >
    <TextInput id="reason" label="Reason" multiline />
  </Modal>,
);
```

Use `privateMetadata` to pass contextual data into submit/close events.

## Companion Web UI and Card Design

Chat SDK payloads render natively in chat platforms, so shadcn isn't used in message markup. But when building a web control plane, thread inspector, or bot settings UI around Chat SDK, use shadcn + Geist by default. Thread dashboards: Tabs+Card+Table+Badge. Bot settings: Sheet+form controls. Logs/IDs/timestamps: Geist Mono with tabular-nums.

## Platform Adapters

### Slack

```ts
import { createSlackAdapter } from "@chat-adapter/slack";

const slack = createSlackAdapter();
// Env: SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET

const oauthSlack = createSlackAdapter({
  clientId: process.env.SLACK_CLIENT_ID!,
  clientSecret: process.env.SLACK_CLIENT_SECRET!,
  encryptionKey: process.env.SLACK_ENCRYPTION_KEY,
});
```

### Telegram

```ts
import { createTelegramAdapter } from "@chat-adapter/telegram";

const telegram = createTelegramAdapter();
// Env: TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET
```

### Microsoft Teams

```ts
import { createTeamsAdapter } from "@chat-adapter/teams";

const teams = createTeamsAdapter({
  appType: "singleTenant",
});
// Env: TEAMS_APP_ID, TEAMS_APP_PASSWORD, TEAMS_APP_TENANT_ID
```

### Discord

```ts
import { createDiscordAdapter } from "@chat-adapter/discord";

const discord = createDiscordAdapter();
// Env: DISCORD_BOT_TOKEN, DISCORD_PUBLIC_KEY, DISCORD_APPLICATION_ID, CRON_SECRET
```

For message content handlers, enable both Gateway intent and Message Content Intent in the Discord developer portal.

### Google Chat

```ts
import { createGoogleChatAdapter } from "@chat-adapter/gchat";

const gchat = createGoogleChatAdapter();
// Env: GOOGLE_CHAT_CREDENTIALS, GOOGLE_CHAT_USE_ADC
```

### GitHub

```ts
import { createGitHubAdapter } from "@chat-adapter/github";

const github = createGitHubAdapter({
  botUserId: process.env.GITHUB_BOT_USER_ID,
});
// Env: GITHUB_TOKEN or (GITHUB_APP_ID + GITHUB_PRIVATE_KEY),
//      GITHUB_WEBHOOK_SECRET, GITHUB_INSTALLATION_ID
```

### Linear

```ts
import { createLinearAdapter } from "@chat-adapter/linear";

const linear = createLinearAdapter({
  clientId: process.env.LINEAR_CLIENT_ID,
  clientSecret: process.env.LINEAR_CLIENT_SECRET,
  accessToken: process.env.LINEAR_ACCESS_TOKEN,
});
```

## State Adapters

### Redis (recommended)

```ts
import { createRedisState } from "@chat-adapter/state-redis";

const state = createRedisState();
// Env: REDIS_URL (or REDIS_HOST/REDIS_PORT/REDIS_PASSWORD)
```

### ioredis (cluster/sentinel)

```ts
import { createIoRedisState } from "@chat-adapter/state-ioredis";

const state = createIoRedisState({
  // cluster/sentinel options
});
```

### Memory (dev/test only)

```ts
import { MemoryState } from "@chat-adapter/state-memory";

const state = new MemoryState();
```

## Webhook Setup

### Next.js App Router

```ts
// app/api/webhooks/slack/route.ts
import { bot } from "@/lib/bot";
import { after } from "next/server";

export async function POST(req: Request) {
  return bot.webhooks.slack(req, {
    waitUntil: (p) => after(() => p),
  });
}
```

```ts
// app/api/webhooks/telegram/route.ts
import { bot } from "@/lib/bot";

export async function POST(req: Request) {
  return bot.webhooks.telegram(req);
}
```

### Pages Router

```ts
// pages/api/bot.ts
export default async function handler(req, res) {
  const response = await bot.webhooks.slack(req);
  res.status(response.status).send(await response.text());
}
```

## Integration Patterns

### Out-of-thread routing with `openDM()` and `channel()`

```ts
bot.onAction("handoff", async (event) => {
  const dm = await bot.openDM(event.user.id);
  await dm.post("A human will follow up shortly.");

  const ops = bot.channel("ops-alerts");
  await ops.post(`Escalated by ${event.user.fullName}`);
});
```

### Workflow-safe serialization with `registerSingleton()` and `reviver()`

```ts
bot.registerSingleton();

const serialized = JSON.stringify({ thread });
const revived = JSON.parse(serialized, bot.reviver());
await revived.thread.post("Resumed workflow step");
```

### Slack OAuth callback handling

```ts
// app/api/webhooks/slack/oauth/callback/route.ts
import { bot } from "@/lib/bot";

export async function GET(req: Request) {
  return bot.oauth.slack.callback(req);
}
```

## Gotchas

### Routing

1. `onNewMention` only fires for unsubscribed threads; call `thread.subscribe()` to receive follow-ups.
2. DMs are treated as direct intent and set `message.isMention = true`.
3. `onNewMessage(pattern, handler)` only applies before subscription; use `onSubscribedMessage` after subscribe.
4. Catch-all and filtered handlers can both run; registration order determines execution order.
5. Out-of-thread routing via `openDM()` / `channel()` needs platform permissions for DM/channel posting.

### Streaming

6. Slack supports native streaming with real-time bold, italic, list, and other formatting rendered as the response arrives. Teams/Discord/Google Chat/Telegram use post+edit fallback.
7. Fallback adapters now convert markdown to each platform's native format at every intermediate edit — users no longer see raw `**bold**` syntax during streaming.
8. `fallbackStreamingPlaceholderText: null` disables placeholder messages on fallback adapters.
9. `streamingUpdateIntervalMs` too low can trigger rate limits on post+edit adapters.
10. `dedupeTtlMs` should cover webhook retry windows to avoid duplicate responses.
11. `startTyping()` is adapter-dependent and may no-op on platforms without typing indicators.

### Adapter-specific

11. Google Chat auth uses `GOOGLE_CHAT_CREDENTIALS` + `GOOGLE_CHAT_USE_ADC`; domain-wide delegation/impersonation is required for some org posting scenarios.
12. Teams requires `appType` plus `TEAMS_APP_TENANT_ID`; reactions/history/typing features are limited compared with Slack.
13. Discord content-based handlers require Message Content Intent enabled in addition to Gateway connectivity.
14. GitHub and Linear adapters do not support interactive card actions/modals; design around comments/status updates instead.
15. GitHub App installs need `GITHUB_INSTALLATION_ID` and often adapter `botUserId`; Linear OAuth setups need `clientId`, `clientSecret`, and `LINEAR_ACCESS_TOKEN`.

## Official Docs

- [Chat SDK documentation](https://chat-sdk.dev)
- [GitHub: vercel/chat](https://github.com/vercel/chat)
