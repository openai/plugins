# Catalyst ↔ Heroku (and Similar PaaS) Equivalents

Maps Catalyst services to Heroku and comparable PaaS platforms: Railway, Render, and Fly.io. Use this
when users come from a PaaS background or ask "can I deploy like Heroku?" / "is AppSail like Heroku dynos?".

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Service-by-Service Mapping

### Heroku Dynos / Railway Services / Render Web Services / Fly.io → Catalyst AppSail

AppSail is Catalyst's PaaS compute — the direct equivalent of Heroku dynos, Railway services, Render
web services, and Fly.io apps.

Key differences:
- Supported runtimes: Node.js, Java, Python (managed) OR custom Docker containers — similar to
  Render's Docker support and Fly.io's container model.
- Auto-scaling: 1–5 instances (more limited than Heroku's unlimited dyno scaling or Fly.io's
  flexible machine count).
- SDK initialization is manual: `catalyst.initialize(req)` — same mental model as initializing a
  database client or SDK in a Heroku/Railway app.
- Use `process.env.X_ZOHO_CATALYST_LISTEN_PORT` instead of `PORT` (Heroku/Railway convention).
- No Heroku "worker dyno" concept — use Job Scheduling + Job Functions for background processing.
- No Heroku "one-off dyno" for scripts — use Job Scheduling for ad-hoc job execution.

**When a user says → they mean:**
- "I want to deploy an Express app like on Heroku" → AppSail with managed Node.js runtime
- "I need Railway / Render deployment" → AppSail
- "I need Fly.io-style container deployment" → AppSail with Custom Runtime (Docker)
- "I need a persistent server, not serverless" → AppSail

---

### Heroku Postgres → Catalyst Data Store

Key differences:
- Data Store uses ZCQL (not standard SQL/Postgres) — case-sensitive table/column names,
  no cross-type JOINs, max 300 rows per query.
- No direct connection string — all access via SDK or ZCQL REST/SDK calls.
- No psql shell or raw SQL access.

**When a user says → they mean:**
- "I need Heroku Postgres / a database add-on" → Data Store (relational) or NoSQL (document schema)

---

### Railway Postgres / Render Postgres → Catalyst Data Store

Same as Heroku Postgres above.

---

### Heroku Redis / Railway Redis → Catalyst Cache

Key differences:
- Catalyst Cache is simpler — segment-based, string values only, max 48hr TTL, max 5MB per value.
- No pub/sub, streams, or Lua scripting (unlike full Redis).
- No persistent Redis — Cache is in-memory only.

**When a user says → they mean:**
- "I need Heroku Redis / Railway Redis / a caching layer" → Cache (for basic caching/session needs)
- For full Redis features, consider an external Redis provider.

---

### Heroku Scheduler → Catalyst Job Scheduling

Both run tasks on a schedule. Key differences:
- Job Scheduling supports on-demand jobs as well as scheduled ones.
- Job Scheduling can trigger Job Functions, Circuits, Webhooks, or AppSail services.
- More flexible targeting than Heroku Scheduler's single-command model.

**When a user says → they mean:**
- "I need Heroku Scheduler / a cron job" → Job Scheduling (not deprecated Cron function type)

---

### Heroku CI / GitHub Auto-Deploy → Catalyst Pipelines + Slate Git Deploy

- **Pipelines** handles full CI/CD with custom stages, tests, and multi-service deploys.
- **Slate** handles frontend git-based auto-build-and-deploy.

**When a user says → they mean:**
- "I need Heroku CI / automated deployment" → Pipelines

---

### Heroku Logs → Catalyst DevOps / Logs

Catalyst DevOps provides real-time Logs, APM (execution time, error rates, cold starts),
and Application Alerts — equivalent to `heroku logs --tail`.

---

### Heroku Add-ons (Storage, Email, etc.) → Catalyst Built-in Services

Unlike Heroku's marketplace of third-party add-ons, Catalyst provides most services natively:
- Storage → Stratus
- Email → Catalyst Mail
- Search → Catalyst Search
- AI/ML → Zia Services + QuickML

---

## Holistic Comparison: Heroku / Railway / Render / Fly.io vs Catalyst

| Dimension | Heroku | Railway | Render | Fly.io | Catalyst |
|---|---|---|---|---|---|
| App hosting | Dynos | Services | Web Services | Machines | AppSail |
| Database | Heroku Postgres | Postgres add-on | Postgres | — | Data Store (ZCQL) |
| Redis | Heroku Redis | Redis add-on | Redis | — | Cache |
| Object storage | — | — | — | — | Stratus |
| Background jobs | Worker dynos | — | Background workers | — | Job Scheduling + Job Functions |
| Scheduler | Heroku Scheduler | — | Cron Jobs | — | Job Scheduling |
| CI/CD | Heroku CI | GitHub Actions | Auto-deploy | — | Pipelines |
| Serverless functions | — | — | — | — | 7 function types |
| Workflow orchestration | — | — | — | — | Circuits |
| AI / ML | — | — | — | — | Zia Services + QuickML |
| Zoho integration | None | None | None | None | Native |
| Containers | — | Yes | Yes | Yes (primary) | AppSail Custom Runtime |

**Catalyst's key advantage over Heroku/Railway/Render/Fly.io:** Serverless functions, object storage,
AI/ML, event bus (Signals), workflow orchestration (Circuits), and native Zoho integration — all
in one platform, not just PaaS app hosting.

**Heroku/Railway/Render/Fly.io's key advantages over Catalyst:**
- Simpler mental model for "just deploy a web app".
- Direct SQL/database access (no ZCQL abstraction).
- More flexible scaling (especially Fly.io's global machine placement).
- Larger community and ecosystem.
