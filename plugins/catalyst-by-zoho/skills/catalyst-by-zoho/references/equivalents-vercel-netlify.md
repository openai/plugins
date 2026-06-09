# Catalyst ↔ Vercel / Netlify Equivalents

Maps Catalyst services to their Vercel and Netlify equivalents. Use this when users come from Vercel
or Netlify, or ask "can I deploy like Vercel?" / "is there a Netlify equivalent?".

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Service-by-Service Mapping

### Vercel Hosting / Netlify Hosting → Catalyst Slate

Slate is the direct equivalent — git-based deployments, branch preview URLs, custom domains,
auto-SSL, and SSR support.

Key differences from Vercel/Netlify:
- Slate integrates with all Catalyst backend services (Data Store, Functions, Auth) natively —
  no need to wire up external DB, auth, or storage as with Vercel + Supabase or Netlify + external DB.
- Multiple frontend apps per Catalyst project (Vercel and Netlify are typically 1 repo → 1 deployment).
- Slate supports Next.js SSR, React, Vue, Angular, Svelte, SolidJS, Preact, Astro, Nuxt, Vite.
- Preview deployments for branches — same as Vercel's preview URLs and Netlify's Deploy Previews.

**When a user says → they mean:**
- "I want to deploy like Vercel / Netlify" → Slate
- "I need preview deployments" → Slate
- "I need frontend hosting with SSR" → Slate
- "I need a CDN for my Next.js / React / Vue app" → Slate

---

### Vercel Serverless Functions → Catalyst Advanced I/O Functions

Key differences from Vercel Functions:
- Catalyst has 7 specialized function types; Vercel uses a single function model.
- Catalyst SDK (`zcatalyst-sdk-node`) is initialized via `catalyst.initialize(context)`; Vercel uses standard Node.js `import`.
- Security Rules (`optional`/`required`) are built in — no need for separate auth middleware.
- Catalyst supports Node.js, Java, and Python; Vercel Functions support JS/TS and Go/Python/Ruby.

**When a user says → they mean:**
- "I need Vercel Serverless Functions" → Advanced I/O Function (HTTP-based)
- "I need a background Vercel Function" → Job Function + Job Scheduling

---

### Netlify Functions → Catalyst Advanced I/O Functions

Same mapping as Vercel above. Netlify Functions are AWS Lambda under the hood — Catalyst Advanced I/O
Functions are the equivalent.

**When a user says → they mean:**
- "I need Netlify Functions" → Advanced I/O Function

---

### Vercel KV → Catalyst Cache

Key differences:
- Catalyst Cache uses segment-based organization (vs Vercel KV's Redis-compatible key namespaces).
- String values only — serialize/deserialize JSON yourself.
- Max TTL 48 hours; max value 5MB.
- No Redis pub/sub or streams.

**When a user says → they mean:**
- "I need Vercel KV" → Cache (for basic caching/session needs)

---

### Vercel Blob → Catalyst Stratus

Key differences:
- Stratus is S3-compatible (bucket/object model) — similar to Vercel Blob's blob store but with
  more features (versioning, malware scanning, PII/ePHI compliance, multipart upload).

**When a user says → they mean:**
- "I need Vercel Blob / file storage" → Stratus

---

### Vercel Postgres (Neon) → Catalyst Data Store

Key differences:
- Data Store uses ZCQL (not standard SQL/Postgres) — case-sensitive names, 300-row query limit,
  no direct connection strings.
- No full Postgres feature set (no stored procedures, no extensions, no pgvector).

**When a user says → they mean:**
- "I need Vercel Postgres / a database" → Data Store (for relational) or NoSQL (for document schema)

---

### Netlify Identity → Catalyst Auth & User Management

Both provide user sign-up, login, and JWT-based auth for frontend apps.

Key differences:
- Catalyst supports Zoho Accounts as an identity provider.
- Catalyst's Security Rules on functions replace Netlify Identity's role-based route protection.

**When a user says → they mean:**
- "I need Netlify Identity / user auth" → Auth & User Management

---

### Netlify CI/CD / Vercel Git Deploy → Catalyst Pipelines + Slate Git Deploy

- **Slate** handles frontend Git-based auto-build-and-deploy (like Vercel/Netlify's primary deploy flow).
- **Pipelines** handles full CI/CD pipelines with custom stages, tests, and multi-service deploys.

**When a user says → they mean:**
- "I need Netlify CI / Vercel CI" → Pipelines (for custom CI) or Slate Git Deploy (for frontend auto-deploy)

---

### Vercel Edge Config → Catalyst Cache

Low-latency key-value config reads — use Catalyst Cache for similar patterns.

---

### Vercel Analytics / Netlify Analytics → Catalyst DevOps / APM

Catalyst DevOps provides Logs, APM (execution time, error rates, cold starts), and Application Alerts.

---

## Holistic Comparison: Vercel / Netlify vs Catalyst

| Dimension | Vercel | Netlify | Catalyst |
|---|---|---|---|
| Frontend hosting | Yes (primary focus) | Yes (primary focus) | Slate |
| SSR | Next.js / Edge Runtime | Netlify Edge Functions | Next.js + React / Vue / Angular / Svelte / more |
| Serverless functions | Vercel Functions | Netlify Functions | 7 function types (Node.js / Java / Python) |
| Database | Vercel Postgres (Neon) | — | Data Store (ZCQL) + NoSQL |
| Storage | Vercel Blob | — | Stratus (S3-compatible) |
| Cache / KV | Vercel KV | — | Cache |
| Auth | — | Netlify Identity | Auth & User Management |
| CI/CD | Git-based auto-deploy | Git-based auto-deploy | Pipelines + Slate Git Deploy |
| Background jobs | — | Background Functions (beta) | Job Scheduling + Job Functions |
| Workflow orchestration | — | — | Circuits |
| AI / ML | — | — | Zia Services + QuickML + ConvoKraft |
| Zoho integration | None | None | Native |
| Monitoring | Vercel Analytics | Netlify Analytics | DevOps / APM / Logs |

**Catalyst's key advantage over Vercel/Netlify:** Full-stack backend depth — relational DB, object storage,
job scheduling, workflow orchestration, and AI/ML are all built in. Vercel and Netlify are
frontend-first platforms that require external services for any meaningful backend.

**Vercel/Netlify's key advantages over Catalyst:** Larger ecosystem, more framework integrations,
simpler DX for frontend-only projects, edge runtime for globally distributed low-latency functions.
