---
name: swr
description: SWR data-fetching expert guidance. Use when building React apps with client-side data fetching, caching, revalidation, mutations, optimistic UI, pagination, or infinite loading using the SWR library.
metadata:
  priority: 4
  docs:
    - "https://swr.vercel.app/docs"
  sitemap: "https://swr.vercel.app/sitemap.xml"
  pathPatterns:
    - 'lib/fetcher.*'
    - 'src/lib/fetcher.*'
    - 'utils/fetcher.*'
    - 'src/utils/fetcher.*'
    - 'hooks/use*SWR*'
    - 'src/hooks/use*SWR*'
    - 'hooks/useFetch*'
    - 'src/hooks/useFetch*'
  importPatterns:
    - 'swr'
    - 'swr/*'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bswr\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bswr\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bswr\b'
    - '\byarn\s+add\s+[^\n]*\bswr\b'
  promptSignals:
    phrases:
      - "swr"
      - "useswr"
      - "stale-while-revalidate"
    allOf:
      - [data fetching, client]
      - [cache, revalidat]
    anyOf:
      - "mutation"
      - "optimistic"
      - "infinite loading"
      - "pagination"
    noneOf: []
    minScore: 6
retrieval:
  aliases:
    - data fetching
    - client cache
    - stale while revalidate
    - react hooks data
  intents:
    - refresh stale client cache after a mutation
    - fetch and cache API data on the client side
    - add infinite scroll or paginated data loading
    - keep UI in sync with server data automatically
    - revalidate cached data after updating a record
  entities:
    - useSWR
    - useSWRMutation
    - useSWRInfinite
    - mutate
    - SWRConfig
    - fetcher
  examples:
    - refresh stale client cache after mutation
    - load more items on scroll
    - revalidate data when the window regains focus
    - fetch data client side with caching
    - add infinite scrolling to load more items
chainTo:
  -
    pattern: 'from\s+[''\"](openai|@anthropic-ai/sdk|anthropic)[''"]|new\s+(OpenAI|Anthropic)\('
    targetSkill: ai-sdk
    message: 'Direct AI provider SDK detected alongside SWR — loading AI SDK guidance for unified streaming and provider-agnostic patterns.'
  -
    pattern: 'from\s+[''""]@vercel/(postgres|kv)[''""]'
    targetSkill: vercel-storage
    message: '@vercel/postgres and @vercel/kv are sunset — loading Vercel Storage guidance for Neon and Upstash migration.'
  -
    pattern: 'useEffect\s*\([^)]*\)\s*\{[^}]*fetch\s*\(|useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*fetch\s*\('
    targetSkill: swr
    message: 'Manual useEffect+fetch pattern detected — SWR provides automatic caching, deduplication, revalidation, and error retry. Replace with useSWR for cleaner data fetching.'
  -
    pattern: 'from\s+[''\"](axios)[''"]|require\s*\(\s*[''\"](axios)[''"]'
    targetSkill: swr
    message: 'Axios detected in React component — SWR with a native fetch wrapper provides caching, deduplication, and revalidation that axios alone cannot. Use useSWR with a fetcher function instead.'

---

# SWR — React Hooks for Data Fetching

You are an expert in SWR v2 (latest: 2.4.1), the React Hooks library for data fetching by Vercel. SWR implements the stale-while-revalidate HTTP cache invalidation strategy — serve from cache first, then revalidate in the background.

## Installation

```bash
npm install swr
```

## Core API

### `useSWR`

```tsx
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(res => res.json())

function Profile() {
  const { data, error, isLoading, mutate } = useSWR('/api/user', fetcher)

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading data</div>
  return <div>Hello, {data.name}</div>
}
```

**Key parameters:**
- `key` — unique string, array, or function identifying the resource (often a URL)
- `fetcher` — async function that receives the key and returns data
- `options` — optional config object

**Return values:** `data`, `error`, `isLoading`, `isValidating`, `mutate`

### `useSWRMutation` — Remote Mutations

```tsx
import useSWRMutation from 'swr/mutation'

async function updateUser(url: string, { arg }: { arg: { name: string } }) {
  return fetch(url, { method: 'POST', body: JSON.stringify(arg) }).then(res => res.json())
}

function Profile() {
  const { trigger, isMutating } = useSWRMutation('/api/user', updateUser)

  return (
    <button disabled={isMutating} onClick={() => trigger({ name: 'New Name' })}>
      Update
    </button>
  )
}
```

### `useSWRInfinite` — Pagination & Infinite Loading

```tsx
import useSWRInfinite from 'swr/infinite'

const getKey = (pageIndex: number, previousPageData: any[]) => {
  if (previousPageData && !previousPageData.length) return null
  return `/api/items?page=${pageIndex}`
}

function Items() {
  const { data, size, setSize, isLoading } = useSWRInfinite(getKey, fetcher)
  const items = data ? data.flat() : []

  return (
    <>
      {items.map(item => <div key={item.id}>{item.name}</div>)}
      <button onClick={() => setSize(size + 1)}>Load More</button>
    </>
  )
}
```

## Global Configuration

Wrap your app (or a subtree) with `SWRConfig` to set defaults:

```tsx
import { SWRConfig } from 'swr'

function App() {
  return (
    <SWRConfig value={{
      fetcher: (url: string) => fetch(url).then(res => res.json()),
      revalidateOnFocus: false,
      dedupingInterval: 5000,
    }}>
      <Dashboard />
    </SWRConfig>
  )
}
```

## Revalidation Strategies

| Strategy | Option | Default |
|---|---|---|
| On window focus | `revalidateOnFocus` | `true` |
| On network recovery | `revalidateOnReconnect` | `true` |
| On mount if stale | `revalidateIfStale` | `true` |
| Polling | `refreshInterval` | `0` (disabled) |
| Manual | Call `mutate()` | — |

## Optimistic Updates

```tsx
const { trigger } = useSWRMutation('/api/user', updateUser, {
  optimisticData: (current) => ({ ...current, name: 'New Name' }),
  rollbackOnError: true,
  populateCache: true,
  revalidate: false,
})
```

## Conditional Fetching

Pass `null` or a falsy key to skip fetching:

```tsx
const { data } = useSWR(userId ? `/api/user/${userId}` : null, fetcher)
```

## Error Retry

SWR retries on error by default with exponential backoff. Customize with:

```tsx
useSWR(key, fetcher, {
  onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
    if (error.status === 404) return // Don't retry on 404
    if (retryCount >= 3) return      // Max 3 retries
    setTimeout(() => revalidate({ retryCount }), 5000)
  },
})
```

## `useSWRSubscription` — Real-Time Data Sources

Subscribe to real-time data (WebSockets, SSE, etc.) with automatic deduplication:

```tsx
import useSWRSubscription from 'swr/subscription'

function LivePrice({ symbol }: { symbol: string }) {
  const { data } = useSWRSubscription(
    `wss://stream.example.com/${symbol}`,
    (key, { next }) => {
      const ws = new WebSocket(key)
      ws.onmessage = (event) => next(null, JSON.parse(event.data))
      ws.onerror = (event) => next(event)
      return () => ws.close()
    }
  )

  return <span>{data?.price}</span>
}
```

The `subscribe` function receives a `next(error, data)` callback and must return a cleanup function. Multiple components using the same key share a single subscription.

## Key Rules

- **Keys must be unique** — two `useSWR` calls with the same key share cache and deduplicate requests
- **Fetcher is optional** when set via `SWRConfig`
- **`mutate(key)`** globally revalidates any hook matching that key
- **Array keys** like `useSWR(['/api/user', id], fetcher)` — the fetcher receives the full array
- **Never call hooks conditionally** — use conditional keys (`null`) instead
