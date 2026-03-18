---
name: ai-generation-persistence
description: "AI generation persistence patterns — unique IDs, addressable URLs, database storage, and cost tracking for every LLM generation"
summary: "Persist every AI generation: unique ID, save to DB/Blob, addressable URL /chat/[id], track token cost"
metadata:
  priority: 6
  docs:
    - "https://sdk.vercel.ai/docs/ai-sdk-ui/storing-messages"
  sitemap: "https://sdk.vercel.ai/sitemap.xml"
  pathPatterns:
    - "app/api/generate/**"
    - "app/api/generations/**"
    - "src/app/api/generate/**"
    - "src/app/api/generations/**"
    - "app/chat/[id]/**"
    - "app/generate/[id]/**"
    - "src/app/chat/[id]/**"
    - "src/app/generate/[id]/**"
    - "lib/generations/**"
    - "src/lib/generations/**"
  bashPatterns: []
  importPatterns:
    - "ai"
    - "@ai-sdk/*"
    - "@vercel/blob"
    - "nanoid"
    - "@paralleldrive/cuid2"
  promptSignals:
    phrases:
      - "save generations"
      - "persist generations"
      - "generation history"
      - "chat history"
      - "save chat"
      - "generation id"
      - "ai chat"
      - "chat app"
      - "chatbot"
      - "image generation"
      - "text generation"
      - "ai app"
    allOf:
      - [generate, save]
      - [generate, persist]
      - [generate, store]
      - [ai, persist]
      - [ai, history]
      - [ai, database]
      - [chat, persist]
      - [chat, database]
      - [chat, url]
      - [generation, url]
      - [generation, id]
      - [image, generate]
      - [stream, save]
      - [stream, persist]
    anyOf:
      - "shareable"
      - "retrievable"
      - "permalink"
      - "cost tracking"
      - "token usage"
      - "nanoid"
      - "cuid"
      - "openai"
      - "anthropic"
      - "llm"
      - "gpt"
      - "claude"
    noneOf:
      - "github actions"
      - "ci workflow"
    minScore: 6
validate:
  -
    pattern: "streamText\\(|generateText\\("
    message: "Ensure this AI generation is persisted with a unique ID (nanoid/cuid2) — generations are expensive assets that should be saved and addressable via URL"
    severity: warn
    skipIfFileContains: "nanoid|cuid|createId|randomUUID|uuid"
retrieval:
  aliases:
    - ai storage
    - generation history
    - llm persistence
    - ai audit
  intents:
    - save ai generations
    - track llm costs
    - store completions
    - persist ai output
  entities:
    - generation ID
    - addressable URL
    - cost tracking
    - LLM generation
chainTo:
  -
    pattern: 'streamText\s*\(|generateText\s*\('
    targetSkill: ai-gateway
    message: 'AI generation call without cost tracking — loading AI Gateway guidance for OIDC auth, usage attribution, and per-generation cost visibility.'
    skipIfFileContains: 'gateway\(|@ai-sdk/gateway|ai-gateway|providerOptions.*gateway|usage.*cost|trackUsage'
  -
    pattern: 'from\s+[''"]@vercel/blob[''""]'
    targetSkill: vercel-storage
    message: 'Vercel Blob import detected for generation persistence — loading Storage guidance for blob upload patterns, ETags, and client upload helpers.'
    skipIfFileContains: 'put\(\s*.*\{.*access|del\(\s*.*url'

---

# AI Generation Persistence

**AI generations are expensive, non-reproducible assets. Never discard them.**

Every call to an LLM costs real money and produces unique output that cannot be exactly reproduced. Treat generations like database records — assign an ID, persist immediately, and make them retrievable.

## Core Rules

1. **Generate an ID before the LLM call** — use `nanoid()` or `createId()` from `@paralleldrive/cuid2`
2. **Persist every generation** — text and metadata to database, images and files to Vercel Blob
3. **Make every generation addressable** — URL pattern: `/chat/[id]`, `/generate/[id]`, `/image/[id]`
4. **Track metadata** — model name, token usage, estimated cost, timestamp, user ID
5. **Never stream without saving** — if the user refreshes, the generation must survive

## Generate-Then-Redirect Pattern

The standard UX flow for AI features: create the resource first, then redirect to its page.

```ts
// app/api/chat/route.ts
import { nanoid } from "nanoid";
import { db } from "@/lib/db";
import { redirect } from "next/navigation";

export async function POST(req: Request) {
  const { prompt, model } = await req.json();
  const id = nanoid();

  // Create the record BEFORE generation starts
  await db.insert(generations).values({
    id,
    prompt,
    model,
    status: "pending",
    createdAt: new Date(),
  });

  // Redirect to the generation page — it handles streaming
  redirect(`/chat/${id}`);
}
```

```tsx
// app/chat/[id]/page.tsx
import { db } from "@/lib/db";
import { notFound } from "next/navigation";

export default async function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const generation = await db.query.generations.findFirst({
    where: eq(generations.id, id),
  });
  if (!generation) notFound();

  // Render with streaming if still pending, or show saved result
  return <ChatView generation={generation} />;
}
```

This gives you: shareable URLs, back-button support, multi-tab sessions, and generation history for free.

## Persistence Schema

```ts
// lib/db/schema.ts
import { pgTable, text, integer, timestamp, jsonb } from "drizzle-orm/pg-core";

export const generations = pgTable("generations", {
  id: text("id").primaryKey(),            // nanoid
  userId: text("user_id"),                // auth user
  model: text("model").notNull(),         // "openai/gpt-5.4"
  prompt: text("prompt"),                 // input text
  result: text("result"),                 // generated output
  imageUrls: jsonb("image_urls"),         // Blob URLs for generated images
  tokenUsage: jsonb("token_usage"),       // { promptTokens, completionTokens }
  estimatedCostCents: integer("estimated_cost_cents"),
  status: text("status").default("pending"), // pending | streaming | complete | error
  createdAt: timestamp("created_at").defaultNow(),
});
```

## Storage Strategy

| Data Type | Storage | Why |
|-----------|---------|-----|
| Text, metadata, history | Neon Postgres via Drizzle | Queryable, relational, supports search |
| Generated images & files | Vercel Blob (`@vercel/blob`) | Permanent URLs, CDN-backed, no expiry |
| Prompt dedup cache | Upstash Redis | Fast lookup, TTL-based expiry |

## Image Persistence

Never serve generated images as ephemeral base64 or temporary URLs. Save to Blob immediately:

```ts
import { put } from "@vercel/blob";
import { generateText } from "ai";

const result = await generateText({ model, prompt });

// Save every generated image to permanent storage
const imageUrls: string[] = [];
for (const file of result.files ?? []) {
  if (file.mediaType?.startsWith("image/")) {
    const ext = file.mediaType.split("/")[1] || "png";
    const blob = await put(`generations/${generationId}.${ext}`, file.uint8Array, {
      access: "public",
      contentType: file.mediaType,
    });
    imageUrls.push(blob.url);
  }
}

// Update the generation record with permanent URLs
await db.update(generations)
  .set({ imageUrls, status: "complete" })
  .where(eq(generations.id, generationId));
```

## Cost Tracking

Extract usage from every generation and store it. This enables billing, budgeting, and abuse detection:

```ts
const result = await generateText({ model, prompt });

const usage = result.usage; // { promptTokens, completionTokens, totalTokens }
const estimatedCostCents = estimateCost(model, usage);

await db.update(generations).set({
  result: result.text,
  tokenUsage: usage,
  estimatedCostCents,
  status: "complete",
}).where(eq(generations.id, generationId));
```

## Prompt Dedup / Caching

Avoid paying for identical generations. Cache by content hash:

```ts
import { Redis } from "@upstash/redis";
import { createHash } from "crypto";

const redis = Redis.fromEnv();

function hashPrompt(model: string, prompt: string): string {
  return createHash("sha256").update(`${model}:${prompt}`).digest("hex");
}

// Check cache before generating
const cacheKey = `gen:${hashPrompt(model, prompt)}`;
const cached = await redis.get<string>(cacheKey);
if (cached) return cached; // Return cached generation ID

// After generation, cache the result
await redis.set(cacheKey, generationId, { ex: 3600 }); // 1hr TTL
```

## Anti-Patterns

- **Streaming to client without saving** — generation lost on page refresh. Always write to DB as tokens arrive or on completion.
- **Routes without `[id]` segments** — `/api/chat` with no ID means generations aren't addressable. Use `/chat/[id]`.
- **Re-generating identical prompts** — check cache first. Same prompt + same model = same cost for no new value.
- **Ephemeral base64 images** — generated images served inline are lost when the component unmounts. Save to Vercel Blob.
- **Missing metadata** — always store model name, token counts, and timestamp. You need this for cost tracking and debugging.
- **Client-only state** — storing generations only in React state or localStorage. Use a database — generations must survive across devices and sessions.
