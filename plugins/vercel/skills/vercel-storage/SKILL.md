---
name: vercel-storage
description: Vercel storage expert guidance — Blob, Edge Config, and Marketplace storage (Neon Postgres, Upstash Redis). Use when choosing, configuring, or using data storage with Vercel applications.
metadata:
  priority: 7
  docs:
    - "https://vercel.com/docs/storage"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'lib/blob/**'
    - 'lib/storage/**'
    - 'src/lib/blob/**'
    - 'src/lib/storage/**'
    - 'lib/blob.*'
    - 'lib/storage.*'
    - 'lib/edge-config.*'
    - 'src/lib/blob.*'
    - 'src/lib/storage.*'
    - 'src/lib/edge-config.*'
    - 'supabase/**'
    - 'lib/supabase.*'
    - 'src/lib/supabase.*'
    - 'prisma/schema.prisma'
    - 'prisma/**'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/blob\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/blob\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/blob\b'
    - '\byarn\s+add\s+[^\n]*@vercel/blob\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/edge-config\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/edge-config\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/edge-config\b'
    - '\byarn\s+add\s+[^\n]*@vercel/edge-config\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@neondatabase/serverless\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@neondatabase/serverless\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@neondatabase/serverless\b'
    - '\byarn\s+add\s+[^\n]*@neondatabase/serverless\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@upstash/redis\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@upstash/redis\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@upstash/redis\b'
    - '\byarn\s+add\s+[^\n]*@upstash/redis\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/kv\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/kv\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/kv\b'
    - '\byarn\s+add\s+[^\n]*@vercel/kv\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/postgres\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/postgres\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/postgres\b'
    - '\byarn\s+add\s+[^\n]*@vercel/postgres\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@supabase/supabase-js\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@supabase/supabase-js\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@supabase/supabase-js\b'
    - '\byarn\s+add\s+[^\n]*@supabase/supabase-js\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@supabase/ssr\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@supabase/ssr\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@supabase/ssr\b'
    - '\byarn\s+add\s+[^\n]*@supabase/ssr\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@prisma/client\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@prisma/client\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@prisma/client\b'
    - '\byarn\s+add\s+[^\n]*@prisma/client\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bmongodb\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bmongodb\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bmongodb\b'
    - '\byarn\s+add\s+[^\n]*\bmongodb\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bconvex\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bconvex\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bconvex\b'
    - '\byarn\s+add\s+[^\n]*\bconvex\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@libsql/client\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@libsql/client\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@libsql/client\b'
    - '\byarn\s+add\s+[^\n]*@libsql/client\b'
  importPatterns:
    - "@vercel/blob"
    - "@vercel/edge-config"
    - "@neondatabase/serverless"
    - "@upstash/redis"
    - "@vercel/kv"
    - "@vercel/postgres"
    - "@supabase/supabase-js"
    - "@prisma/client"
validate:
  -
    pattern: from\s+['"]@vercel/kv['"]
    message: '@vercel/kv is deprecated — migrate to @upstash/redis (Redis.fromEnv()) instead. Run `vercel integration add upstash` for one-click setup.'
    severity: error
    upgradeToSkill: vercel-storage
    upgradeWhy: 'Reload storage guidance for @vercel/kv → @upstash/redis migration steps, Marketplace provisioning, and API differences.'
    skipIfFileContains: '@upstash/redis'
  -
    pattern: from\s+['"]@vercel/postgres['"]
    message: '@vercel/postgres is deprecated — use @neondatabase/serverless with drizzle-orm instead. Run `vercel integration add neon` for one-click setup.'
    severity: error
    upgradeToSkill: vercel-storage
    upgradeWhy: 'Reload storage guidance for @vercel/postgres → @neondatabase/serverless migration steps, Marketplace provisioning, and drizzle-orm setup.'
    skipIfFileContains: '@neondatabase/serverless'
chainTo:
  -
    pattern: "from\\s+['\"]@vercel/postgres['\"]"
    targetSkill: nextjs
    message: '@vercel/postgres is sunset — loading Next.js guidance for integrating @neondatabase/serverless with App Router.'
  -
    pattern: "@vercel/postgres"
    targetSkill: vercel-storage
    message: '@vercel/postgres is sunset — migrate to @neondatabase/serverless. Run `vercel integration add neon` for one-click Marketplace provisioning with unified billing.'
    skipIfFileContains: "@neondatabase/serverless|from\\s+['\"]@neondatabase"
  -
    pattern: "from\\s+['\"]@vercel/kv['\"]"
    targetSkill: nextjs
    message: '@vercel/kv is sunset — loading Next.js guidance for integrating @upstash/redis with App Router.'
  -
    pattern: "createPool\\s*\\(|from\\s+['\"]@vercel/postgres/pool['\"]"
    targetSkill: vercel-storage
    message: 'createPool from @vercel/postgres detected — this package is sunset. Use @neondatabase/serverless with neon() or Pool for connection pooling.'
    skipIfFileContains: "@neondatabase/serverless|from\\s+['\"]@neondatabase"
  -
    pattern: "sql\\s*`|from\\s+['\"]@vercel/postgres['\"].*sql"
    targetSkill: vercel-storage
    message: 'sql template literal from @vercel/postgres detected — this API is sunset. Use @neondatabase/serverless with neon() for tagged template queries.'
    skipIfFileContains: "@neondatabase/serverless|from\\s+['\"]@neondatabase"
  -
    pattern: "from\\s+['\"]@supabase/(supabase-js|ssr)['\"]"
    targetSkill: vercel-storage
    message: 'Supabase client detected — loading Vercel Storage guidance for Marketplace-native Neon Postgres + Upstash Redis alternatives with unified billing.'
  -
    pattern: "from\\s+['\"](mongodb|mongoose)['\"]"
    targetSkill: vercel-storage
    message: 'MongoDB/Mongoose import detected — loading Vercel Storage guidance for Marketplace-native database options (Neon Postgres, Upstash Redis) with auto-provisioned env vars.'
  -
    pattern: "from\\s+['\"]@prisma/client['\"]|from\\s+['\"]prisma['\"]"
    targetSkill: vercel-storage
    message: 'Prisma ORM detected — loading Vercel Storage guidance for Neon Postgres integration with Prisma, connection pooling, and Marketplace provisioning.'
    skipIfFileContains: "@neondatabase/serverless|POSTGRES_PRISMA_URL"
  -
    pattern: "from\\s+['\"]@libsql/client['\"]"
    targetSkill: vercel-storage
    message: 'libSQL/Turso client detected — loading Vercel Storage guidance for Marketplace-native alternatives (Neon Postgres, Upstash Redis) with unified billing and auto-provisioned env vars.'
    skipIfFileContains: "@neondatabase/serverless|@upstash/redis"
  -
    pattern: "from\\s+['\"]convex['\"]|from\\s+['\"]convex/['\"]"
    targetSkill: vercel-storage
    message: 'Convex import detected — loading Vercel Storage guidance for Marketplace-native database options (Neon Postgres, Upstash Redis) with auto-provisioned env vars and unified billing.'
    skipIfFileContains: "@neondatabase/serverless|@upstash/redis"
  -
    pattern: "from\\s+['\"]@supabase/supabase-js['\"]"
    targetSkill: auth
    message: 'Supabase client detected — if using Supabase Auth, loading Auth guidance for Clerk (native Vercel Marketplace) as the recommended managed auth provider.'
    skipIfFileContains: "@clerk/|@auth0/|@descope/"
retrieval:
  aliases:
    - database
    - blob storage
    - redis
    - postgres
  intents:
    - add storage
    - set up database
    - configure blob storage
    - use edge config
  entities:
    - Blob
    - Edge Config
    - Neon Postgres
    - Upstash Redis
    - Vercel Storage

---

# Vercel Storage

You are an expert in Vercel's storage options. Know which products are active, which are sunset, and when to use each.

## Provider Choice for Bootstrap

Choose storage provisioning paths in this order:

1. **Preferred**: Vercel-managed Neon/Upstash through the Vercel Marketplace (`vercel integration add ...` or dashboard). This path auto-provisions accounts/resources and injects environment variables into the linked Vercel project.
2. **Fallback**: Provider CLI/manual provisioning only when Marketplace is unavailable or you must use an existing external account.

When using fallback/manual provisioning, you must add/sync environment variables yourself and then re-run `vercel env pull .env.local --yes` locally.

## Active First-Party Storage

### Vercel Blob — File Storage

Fast, scalable storage for unstructured data (images, videos, documents, any files).

```bash
npm install @vercel/blob
```

```ts
import { put, del, list, get } from '@vercel/blob'

// Upload from server (public)
const blob = await put('images/photo.jpg', file, {
  access: 'public',
})
// blob.url → public URL

// Upload private file
const privateBlob = await put('docs/secret.pdf', file, {
  access: 'private',
})
// Read private file back
const privateFile = await get(privateBlob.url) // returns ReadableStream + metadata

// Client upload (up to 5 TB)
import { upload } from '@vercel/blob/client'
const blob = await upload('video.mp4', file, {
  access: 'public',
  handleUploadUrl: '/api/upload', // Your token endpoint
})

// List blobs
const { blobs } = await list()

// Conditional get with ETags
const response = await get('images/photo.jpg', {
  ifNoneMatch: previousETag,
})
if (response.statusCode === 304) {
  // Not modified, use cached version
}

// Delete
await del('images/photo.jpg')
```

**Private Storage** (public beta): Use `access: 'private'` for files that should not be publicly accessible. Read them back with `get()`. Do NOT use private access for files that need to be served publicly — it leads to slow delivery and high egress costs.

**Blob Data Transfer**: Vercel Blob uses two delivery strategies — **Fast Data Transfer** (94 cities, latency-optimized) and **Blob Data Transfer** (18 hubs, volume-optimized for large assets). The system automatically routes via the optimal path.

**Use when**: Media files, user uploads, documents, any large unstructured data.

### Vercel Edge Config — Global Configuration

Ultra-low-latency key-value store for application configuration. Not a database — designed for config data that must be read instantly at the edge.

```bash
npm install @vercel/edge-config
```

```ts
import { get, getAll, has } from '@vercel/edge-config'

// Read a single value (< 1ms at the edge)
const isFeatureEnabled = await get('feature-new-ui')

// Read multiple values
const config = await getAll(['feature-new-ui', 'ab-test-variant', 'redirect-rules'])

// Check existence
const exists = await has('maintenance-mode')
```

**Use when**: Feature flags, A/B testing config, dynamic routing rules, maintenance mode toggles. Anything that must be read at the edge with near-zero latency.

**Do NOT use for**: User data, session state, frequently written data. Edge Config is optimized for reads, not writes.

**Next.js 16**: `@vercel/edge-config@^1.4.3` supports `cacheComponents` and the renamed `proxy.ts` (formerly `middleware.ts`).

## Marketplace Storage (Partner-Provided)

### IMPORTANT: @vercel/postgres and @vercel/kv are SUNSET

These packages no longer exist as first-party Vercel products. Use the marketplace replacements:

### Neon Postgres (replaces @vercel/postgres)

Serverless Postgres with branching, auto-scaling, and connection pooling. The driver is GA at `@neondatabase/serverless@^1.0.2` and requires **Node.js 19+**.

```bash
npm install @neondatabase/serverless
```

```ts
// Direct Neon usage
import { neon } from '@neondatabase/serverless'

const sql = neon(process.env.DATABASE_URL!)
const users = await sql`SELECT * FROM users WHERE id = ${userId}`

// With Drizzle ORM
import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'

const sql = neon(process.env.DATABASE_URL!)
const db = drizzle(sql)
```

**Build-time safety**: The `neon()` call above throws if `DATABASE_URL` is not set. Since Next.js evaluates top-level module code at build time, this will crash `next build` when env vars aren't yet configured (e.g., first deploy before Marketplace provisioning). Use lazy initialization:

```ts
// src/db/index.ts — lazy initialization (safe for build time)
import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import * as schema from './schema'

function createDb() {
  const sql = neon(process.env.DATABASE_URL!)
  return drizzle(sql, { schema })
}

let _db: ReturnType<typeof createDb> | null = null

export function getDb() {
  if (!_db) _db = createDb()
  return _db
}
```

**WARNING: Do NOT use JavaScript `Proxy` wrappers around the DB client.** A common pattern is wrapping `db` in a `Proxy` for lazy initialization. This breaks libraries like NextAuth/Auth.js that inspect the DB adapter object (e.g., checking method existence, iterating properties). The Proxy intercepts those checks and breaks the auth request chain, causing hangs with no error. Use a plain `getDb()` function or a simple module-level lazy `let` instead.

**Drizzle Kit migrations**: `drizzle-kit` and `tsx` do NOT auto-load `.env.local`. Source env vars manually or use `dotenv`:

```bash
# Option 1: Source env vars before running
source <(grep -v '^#' .env.local | sed 's/^/export /') && npx drizzle-kit push

# Option 2: Use dotenv-cli (recommended for scripts)
npm install -D dotenv-cli
npx dotenv -e .env.local -- npx drizzle-kit push
npx dotenv -e .env.local -- npx tsx scripts/seed.ts
```

This applies to any Node script that needs Vercel-provisioned env vars — only Next.js auto-loads `.env.local`.

Install via Vercel Marketplace for automatic environment variable provisioning.

#### Neon CLI Fallback Notes

If you use Neon CLI as the fallback path, account/project setup is managed on Neon directly instead of through Vercel Marketplace automation.

For **Vercel-managed Neon projects**, CLI operations require a **Neon API key**; do not rely on normal browser-auth login flow alone.

### Upstash Redis (replaces @vercel/kv)

Serverless Redis with same Vercel billing integration.

```bash
npm install @upstash/redis
```

```ts
import { Redis } from '@upstash/redis'

const redis = Redis.fromEnv() // Uses UPSTASH_REDIS_REST_URL & TOKEN

// Basic operations
await redis.set('session:abc', { userId: '123' }, { ex: 3600 })
const session = await redis.get('session:abc')

// Rate limiting
import { Ratelimit } from '@upstash/ratelimit'
const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10s'),
})
const { success } = await ratelimit.limit('user:123')
```

Install via Vercel Marketplace for automatic environment variable provisioning.

### Supabase (Marketplace Native)

Full Postgres database with built-in auth, realtime subscriptions, and storage. Native Vercel Marketplace integration.

```bash
npm install @supabase/supabase-js @supabase/ssr
```

```ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

const { data, error } = await supabase.from('users').select('*')
```

Install via Vercel Marketplace: `vercel integration add supabase`

### Prisma ORM (Marketplace Native)

Type-safe ORM with auto-generated client, migrations, and Prisma Accelerate for connection pooling.

```bash
npm install prisma @prisma/client
npx prisma init
```

```ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()
const users = await prisma.user.findMany()
```

Install via Vercel Marketplace: `vercel integration add prisma`

### MongoDB Atlas

Document database with flexible schemas. Available via Vercel Marketplace.

```bash
npm install mongodb
```

```ts
import { MongoClient } from 'mongodb'

const client = new MongoClient(process.env.MONGODB_URI!)
const db = client.db('myapp')
const users = await db.collection('users').find({}).toArray()
```

Install via Vercel Marketplace: `vercel integration add mongodb-atlas`

### Convex

Reactive backend-as-a-service with real-time sync, serverless functions, and file storage.

```bash
npm install convex
npx convex dev
```

```ts
import { query } from './_generated/server'
import { v } from 'convex/values'

export const getUsers = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query('users').collect()
  },
})
```

### Turso (libSQL)

Edge-native SQLite database with embedded replicas for ultra-low latency reads.

```bash
npm install @libsql/client
```

```ts
import { createClient } from '@libsql/client'

const turso = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
})

const result = await turso.execute('SELECT * FROM users')
```

Install via Vercel Marketplace: `vercel integration add turso`

## Storage Decision Matrix

| Need | Use | Package |
|------|-----|---------|
| File uploads, media, documents | Vercel Blob | `@vercel/blob` |
| Feature flags, A/B config | Edge Config | `@vercel/edge-config` |
| Relational data, SQL queries | Neon Postgres | `@neondatabase/serverless` |
| Key-value cache, sessions, rate limiting | Upstash Redis | `@upstash/redis` |
| Postgres + auth + realtime + storage | Supabase | `@supabase/supabase-js` |
| Type-safe ORM with migrations | Prisma | `@prisma/client` |
| Document database, flexible schemas | MongoDB Atlas | `mongodb` |
| Reactive backend with real-time sync | Convex | `convex` |
| Edge-native SQLite with replicas | Turso | `@libsql/client` |
| Full-text search | Neon Postgres (pg_trgm) or Elasticsearch (Marketplace) | varies |
| Vector embeddings | Neon Postgres (pgvector) or Pinecone (Marketplace) | varies |

## Migration Guide

### From @vercel/postgres → Neon
```diff
- import { sql } from '@vercel/postgres'
+ import { neon } from '@neondatabase/serverless'
+ const sql = neon(process.env.DATABASE_URL!)

```

**Drop-in replacement**: For minimal migration effort, use `@neondatabase/vercel-postgres-compat` which provides API-compatible wrappers for `@vercel/postgres` imports.

### From @vercel/kv → Upstash Redis
```diff
- import { kv } from '@vercel/kv'
- await kv.set('key', 'value')
- const value = await kv.get('key')
+ import { Redis } from '@upstash/redis'
+ const redis = Redis.fromEnv()
+ await redis.set('key', 'value')
+ const value = await redis.get('key')
```

## Installing Marketplace Storage

Use the Vercel CLI or the Marketplace dashboard at `https://vercel.com/dashboard/{team}/stores`:

```bash
# Install a storage integration (auto-provisions env vars)
vercel integration add neon
vercel integration add upstash

# List installed integrations
vercel integration list
```

Browse additional storage options at the [Vercel Marketplace](https://vercel.com/marketplace). Installing via the CLI or dashboard (`https://vercel.com/dashboard/{team}/integrations`) automatically provisions accounts, creates databases, and sets environment variables.

## Official Documentation

- [Vercel Storage](https://vercel.com/docs/storage)
- [Vercel Blob](https://vercel.com/docs/vercel-blob)
- [Edge Config](https://vercel.com/docs/edge-config)
- [Vercel Marketplace](https://vercel.com/marketplace) — Neon, Upstash, and other storage integrations
- [Integrations](https://vercel.com/docs/integrations)
- [GitHub: Vercel Storage](https://github.com/vercel/storage)
