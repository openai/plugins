# Next.js App Router — File Convention Reference

## Special Files

| File | Purpose | Server/Client |
|------|---------|---------------|
| `layout.tsx` | Shared UI wrapper, preserves state | Server (default) |
| `page.tsx` | Unique route UI | Server (default) |
| `loading.tsx` | Suspense fallback | Server (default) |
| `error.tsx` | Error boundary | Client (required) |
| `not-found.tsx` | 404 UI | Server (default) |
| `route.ts` | API endpoint (Route Handler) | Server only |
| `template.tsx` | Layout that remounts on navigation | Server (default) |
| `default.tsx` | Parallel route fallback | Server (default) |
| `proxy.ts` | Network proxy (replaces middleware) | Server (Node.js) |
| `opengraph-image.tsx` | Auto-generated OG image for route | Server (Edge) |
| `twitter-image.tsx` | Auto-generated Twitter card image | Server (Edge) |

## Route Segments

| Pattern | Example | Matches |
|---------|---------|---------|
| `[id]` | `app/users/[id]/page.tsx` | `/users/123` |
| `[...slug]` | `app/docs/[...slug]/page.tsx` | `/docs/a/b/c` |
| `[[...slug]]` | `app/shop/[[...slug]]/page.tsx` | `/shop` or `/shop/a/b` |
| `(group)` | `app/(marketing)/page.tsx` | `/` (group ignored in URL) |
| `@slot` | `app/@sidebar/page.tsx` | Parallel route slot |

## Data Fetching Patterns

### Server Component (Default)
```tsx
export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

### With Params (Async in Next.js 16)
```tsx
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const user = await getUser(id)
  return <UserProfile user={user} />
}
```

### With Search Params (Async in Next.js 16)
```tsx
export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q } = await searchParams
  const results = await search(q)
  return <SearchResults results={results} />
}
```

### generateStaticParams (SSG)
```tsx
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await getPost(slug)
  return <Post post={post} />
}
```

### generateMetadata
```tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const product = await getProduct(id)
  return { title: product.name, description: product.description }
}
```
