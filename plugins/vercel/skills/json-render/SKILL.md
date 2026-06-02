---
name: json-render
description: AI chat response rendering guidance — handling UIMessage parts, tool call displays, streaming states, and structured data presentation. Use when building custom chat UIs, rendering tool results, or troubleshooting AI response display issues.
metadata:
  priority: 4
  docs:
    - "https://nextjs.org/docs/app/api-reference/file-conventions/route"
  sitemap: "https://nextjs.org/sitemap.xml"
  pathPatterns:
    - 'components/chat/**'
    - 'components/chat-*.tsx'
    - 'components/chat-*.ts'
    - 'src/components/chat/**'
    - 'src/components/chat-*.tsx'
    - 'src/components/chat-*.ts'
    - 'components/message*.tsx'
    - 'src/components/message*.tsx'
  bashPatterns: []
---

# AI Chat Response Rendering

You are an expert in rendering AI SDK v6 chat responses — UIMessage parts, tool call results, streaming states, and structured data display in React applications.

## The Problem

When building chat interfaces with AI SDK v6, the raw message format includes multiple part types (text, tool calls, reasoning, images). Without proper rendering, responses appear as raw JSON or malformed output.

## AI SDK v6 Message Format

In v6, messages use the `UIMessage` type with a `parts` array:

```ts
interface UIMessage {
  id: string
  role: 'user' | 'assistant'
  parts: UIMessagePart[]
}

// Part types:
// - { type: 'text', text: string }
// - { type: 'tool-<toolName>', toolCallId: string, state: string, input?: unknown, output?: unknown }
//     state values: 'partial-call' | 'call' | 'output-available' | 'approval-requested' | 'approval-responded' | 'output-denied'
// - { type: 'reasoning', text: string }
// - { type: 'step-start' }  // internal, skip in rendering
```

## Recommended: Use AI Elements

The simplest approach is to use AI Elements, which handles all part types automatically:

```tsx
import { Message } from '@/components/ai-elements/message'
import { Conversation } from '@/components/ai-elements/conversation'

{messages.map((message) => (
  <Message key={message.id} message={message} />
))}
```

⤳ skill: ai-elements — Full component library for AI interfaces

## Manual Rendering Pattern

If you need custom rendering without AI Elements, follow this pattern:

```tsx
'use client'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'

export function Chat() {
  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: '/api/chat' }),
  })

  const isLoading = status === 'streaming' || status === 'submitted'

  return (
    <div>
      {messages.map((message) => (
        <div key={message.id}>
          {message.parts?.map((part, i) => {
            // 1. Text parts — render as formatted text
            if (part.type === 'text' && part.text.trim()) {
              return (
                <div key={i} className={
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-lg px-3 py-2'
                    : 'bg-muted rounded-lg px-3 py-2'
                }>
                  {part.text}
                </div>
              )
            }

            // 2. Tool parts — type is "tool-<toolName>"
            if (part.type.startsWith('tool-')) {
              const toolPart = part as {
                type: string
                toolCallId: string
                state: string
                input?: unknown
                output?: unknown
              }
              const toolName = toolPart.type.replace('tool-', '')

              if (toolPart.state === 'output-available' && toolPart.output) {
                return <ToolResultCard key={i} name={toolName} output={toolPart.output} />
              }

              if (toolPart.state === 'output-denied') {
                return (
                  <div key={i} className="text-sm text-muted-foreground">
                    {toolName} was denied
                  </div>
                )
              }

              if (toolPart.state === 'approval-requested') {
                return (
                  <div key={i} className="text-sm text-yellow-500">
                    {toolName} requires approval
                  </div>
                )
              }

              return (
                <div key={i} className="text-sm text-muted-foreground animate-pulse">
                  Running {toolName}...
                </div>
              )
            }

            // 3. Reasoning parts
            if (part.type === 'reasoning') {
              return (
                <details key={i} className="text-xs text-muted-foreground">
                  <summary>Thinking...</summary>
                  <p className="whitespace-pre-wrap">{(part as { text: string }).text}</p>
                </details>
              )
            }

            // 4. Skip unknown types (step-start, etc.)
            return null
          })}
        </div>
      ))}
    </div>
  )
}
```

## Rendering Tool Results as Cards

Instead of dumping raw JSON, render structured tool output as human-readable cards:

```tsx
function ToolResultCard({ name, output }: { name: string; output: unknown }) {
  const data = output as Record<string, unknown>

  // Pattern: Check for known result shapes and render accordingly
  if (data?.success && data?.issue) {
    const issue = data.issue as { identifier?: string; title?: string }
    return (
      <div className="rounded border border-border bg-card p-2 text-sm">
        <span className="font-medium text-green-400">
          {name === 'createIssue' ? 'Created' : 'Updated'} {issue.identifier}
        </span>
        <p className="text-muted-foreground">{issue.title}</p>
      </div>
    )
  }

  if (data?.items && Array.isArray(data.items)) {
    return (
      <div className="rounded border border-border bg-card p-2 text-sm">
        <p className="font-medium">{data.items.length} results</p>
        {data.items.slice(0, 5).map((item: Record<string, unknown>, i: number) => (
          <p key={i} className="text-muted-foreground">{String(item.name || item.title || item.id)}</p>
        ))}
      </div>
    )
  }

  if (data?.error) {
    return (
      <div className="rounded border border-destructive/30 bg-destructive/10 p-2 text-sm text-destructive">
        {String(data.error)}
      </div>
    )
  }

  // Fallback: simple completion message (not raw JSON)
  return (
    <div className="rounded border border-border bg-card p-2 text-xs text-muted-foreground">
      {name} completed
    </div>
  )
}
```

## Server-Side Requirements

The server route must use the correct v6 response format:

```ts
// app/api/chat/route.ts
import { streamText, convertToModelMessages, gateway } from 'ai'

export async function POST(req: Request) {
  const { messages } = await req.json()

  // IMPORTANT: convertToModelMessages is async in v6
  const modelMessages = await convertToModelMessages(messages)

  const result = streamText({
    model: gateway('anthropic/claude-sonnet-4.6'),
    messages: modelMessages,
  })

  // Use toUIMessageStreamResponse for chat UIs (not toDataStreamResponse)
  return result.toUIMessageStreamResponse()
}
```

## Client-Side Requirements

```tsx
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'

const { messages, sendMessage, status } = useChat({
  // v6 uses transport instead of api
  transport: new DefaultChatTransport({ api: '/api/chat' }),
})

// v6 uses sendMessage instead of handleSubmit
sendMessage({ text: inputValue })

// Status values: 'ready' | 'submitted' | 'streaming'
const isLoading = status === 'streaming' || status === 'submitted'
```

## Common Mistakes

### 1. Raw JSON in chat responses

**Cause**: Rendering `message.content` instead of iterating `message.parts`.

**Fix**: Always iterate `message.parts` and handle each type:

```tsx
// WRONG — shows raw JSON
<div>{message.content}</div>

// RIGHT — renders each part type
{message.parts?.map((part, i) => {
  if (part.type === 'text') return <span key={i}>{part.text}</span>
  // ... handle other types
})}
```

### 2. Tool results showing as JSON blobs

**Cause**: Using `JSON.stringify(output)` as the display.

**Fix**: Create structured card components for known tool output shapes.

### 3. "Invalid prompt: messages do not contain..." error

**Cause**: Not converting UI messages to model messages on the server.

**Fix**: Use `await convertToModelMessages(messages)` — it's async in v6.

### 4. Messages not appearing / empty responses

**Cause**: Using `toDataStreamResponse()` instead of `toUIMessageStreamResponse()`.

**Fix**: Use `toUIMessageStreamResponse()` when the client uses `useChat` with `DefaultChatTransport`.

### 5. useChat not working with v6

**Cause**: Using the v5 `useChat({ api: '/api/chat' })` pattern.

**Fix**: Use `DefaultChatTransport`:

```tsx
// v5 (old)
const { messages, handleSubmit, input } = useChat({ api: '/api/chat' })

// v6 (current)
const { messages, sendMessage, status } = useChat({
  transport: new DefaultChatTransport({ api: '/api/chat' }),
})
```

## Decision Tree

```
Building a chat UI with AI SDK v6?
  └─ Want pre-built components?
       └─ Yes → Use AI Elements (⤳ skill: ai-elements)
       └─ No → Manual rendering with parts iteration
            └─ Tool results look like JSON?
                 └─ Create ToolResultCard components for each tool's output shape
            └─ Text not rendering?
                 └─ Check part.type === 'text' and use part.text
            └─ Server errors?
                 └─ Check: await convertToModelMessages(), toUIMessageStreamResponse()
```

## Server-Side Message Validation

Use `validateUIMessages` to validate incoming messages before processing:

```ts
import { validateUIMessages, convertToModelMessages, streamText, gateway } from 'ai'

export async function POST(req: Request) {
  const { messages } = await req.json()
  const validatedMessages = validateUIMessages(messages)
  const modelMessages = await convertToModelMessages(validatedMessages)
  // ...
}
```

## Official Documentation

- [AI SDK UI](https://ai-sdk.dev/docs/ai-sdk-ui)
- [useChat Reference](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot)
- [UIMessage Types](https://ai-sdk.dev/docs/reference/ai-sdk-core/ui-message)
- [AI Elements](https://ai-sdk.dev/elements)
