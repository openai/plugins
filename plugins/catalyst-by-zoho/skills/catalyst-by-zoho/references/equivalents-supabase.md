# Catalyst ↔ Supabase Equivalents

Supabase is one of the closest conceptual analogues to Catalyst — both are integrated full-stack
platforms combining a relational database, auth, storage, and serverless functions. Use this file
when users come from Supabase or ask "is Catalyst like Supabase?" / "how does Supabase Postgres map
to Catalyst?".

This file also includes the full holistic comparison across all Catalyst-comparable full-stack platforms.

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Service-by-Service Mapping

### Supabase Postgres → Catalyst Data Store

Key similarities:
- Both provide a managed relational database with a web console for table management.
- Both auto-generate system columns: Supabase generates `id`, `created_at`; Catalyst generates
  ROWID, CREATORID, CREATEDTIME, MODIFIEDTIME.
- Both provide a table editor in the dashboard for manual data management.

Key differences:
- Data Store uses **ZCQL** (not standard SQL/Postgres) — case-sensitive table/column names,
  no cross-type JOINs, max 300 rows per query.
- No direct SQL access or connection strings — all access via SDK or ZCQL.
- No row-level security (RLS) — Catalyst uses function-level Security Rules instead.
- No stored procedures, triggers, views, or Postgres extensions (no pgvector, PostGIS, etc.).
- No Supabase "Realtime" equivalent — Catalyst has no row-change push events.

**When a user says → they mean:**
- "I need Supabase tables / Postgres" → Data Store (note ZCQL differences from Postgres)
- "I need a relational DB with an admin UI" → Data Store (web console)

---

### Supabase Auth → Catalyst Auth & User Management

Key similarities:
- Both provide sign-up, login, password reset, and social auth flows.
- Both have client-side SDK auth flows.

Key differences:
- Catalyst's Security Rules on functions (`optional`/`required`) replace Supabase Auth's
  Row Level Security for API access control — simpler but less granular than RLS.
- Catalyst supports Zoho Accounts as a native identity provider.
- No Supabase Auth's "magic link" or "phone OTP" equivalent in Catalyst by default.

**When a user says → they mean:**
- "I need Supabase Auth / user auth" → Auth & User Management

---

### Supabase Storage → Catalyst Stratus

Key similarities:
- Both use a bucket-based organization model.

Key differences:
- Stratus is fully S3-compatible — more flexible and feature-rich than Supabase Storage.
- Stratus supports versioning, multipart upload, malware scanning, and PII/ePHI compliance.
- Access control via function-level Security Rules or pre-signed URL patterns (not Supabase's
  per-bucket/per-object security policies).

**When a user says → they mean:**
- "I need Supabase Storage / file storage" → Stratus

---

### Supabase Edge Functions → Catalyst Advanced I/O Functions

Key differences:
- Supabase Edge Functions run on Deno with TypeScript; Catalyst supports Node.js, Java, and Python.
- Catalyst has 7 specialized function types; Supabase has one function type.
- Catalyst SDK (`zcatalyst-sdk-node`) is initialized via `catalyst.initialize(context)`; Supabase uses Deno imports.

**When a user says → they mean:**
- "I need Supabase Edge Functions" → Advanced I/O Function (HTTP-based)

---

### Supabase Realtime → No direct equivalent

Catalyst has no real-time push equivalent for database row changes. Workarounds:
- Use **Signals** to propagate events between backend services (e.g., trigger a downstream service
  when a Data Store record changes — but not for client-side push).
- Use **client-side polling** (setInterval + REST/SDK call) for UI refresh.
- For chat/collaboration use cases, consider a dedicated WebSocket layer via AppSail.

---

### Supabase Vector / pgvector → No direct equivalent

Catalyst has no vector database. For vector search use cases:
- Use **Zia Services** for ML inference (classification, object detection, text analytics).
- Use **QuickML** for custom model training and deployment.
- For semantic search / RAG, use an external vector DB (Pinecone, Weaviate, etc.) alongside Catalyst.

---

### Supabase Cron (pg_cron) → Catalyst Job Scheduling

**When a user says → they mean:**
- "I need Supabase Cron / pg_cron" → Job Scheduling

---

### Supabase Webhooks / Database Webhooks → Catalyst Signals

Supabase Database Webhooks fire on row changes; Catalyst Signals provide an event bus for routing
events between services. Use Signals to implement event-driven patterns.

---

### Supabase Studio → Catalyst Console

Both are web-based dashboards for managing the full project — tables, functions, storage, auth,
logs, and settings.

---

## Holistic Comparison: Catalyst vs Full-Stack Platforms

| Full-Stack Platform | Similarity to Catalyst |
|---|---|
| **Supabase** | Database + Auth + Storage + Functions + Realtime — similar integrated model; Catalyst adds relational + document DBs, Circuits, Job Scheduling, AI/ML, and native Zoho integration; Supabase has real-time and full Postgres |
| **Firebase** | Auth + Firestore + Storage + Functions + Hosting — similar BaaS philosophy; Catalyst adds structured relational DB, richer compute types, Zoho integration; Firebase has real-time that Catalyst lacks |
| **AWS Amplify** | Frontend hosting + Auth + API + Storage — similar full-stack DX; Catalyst is simpler to set up and doesn't require stitching together AWS services |
| **Vercel** | Frontend + Serverless + Storage + KV — frontend-first platform; no built-in relational DB, no auth, less backend depth |
| **Netlify** | Frontend + Functions + Identity + Forms — similar but less backend depth |
| **Railway** | Full-stack hosting + DB + Redis — similar simplicity; PaaS model vs serverless |
| **Heroku** | PaaS hosting + managed DB — AppSail ≈ Heroku dynos; Catalyst adds serverless functions, AI/ML, and Zoho integration |

**Catalyst's unique position:** The only platform with native integration across the entire Zoho
product ecosystem (CRM, Books, Desk, People, Analytics, etc.) via Signals and Connections —
eliminating the "glue code" problem entirely for businesses already using Zoho products.

**Feature gap summary (what Catalyst does not have vs full-stack competitors):**
| Capability | Missing in Catalyst | Best Alternative |
|---|---|---|
| Real-time push | No `onSnapshot` / RTDB | Poll or use Signals for backend events |
| Full Postgres (SQL) | ZCQL only (no stored procs, extensions) | External Postgres if needed |
| pgvector / vector search | No vector DB | External vector DB + Zia for inference |
| Row-level security (RLS) | Function-level Security Rules instead | Design auth at function boundary |
