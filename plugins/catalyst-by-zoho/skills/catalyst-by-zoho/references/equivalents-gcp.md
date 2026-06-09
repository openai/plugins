# Catalyst ↔ GCP Equivalents

Maps every Catalyst service to its closest GCP equivalent. Use this to help users who come from GCP
understand Catalyst concepts, or to translate requests phrased as "I need something like Cloud Run/Pub-Sub".

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Compute

### Functions → Google Cloud Functions

Key differences:
- Catalyst bundles 7 specialized function types with distinct handler signatures; GCP uses a single
  function model with event sources configured externally.
- Catalyst provides an SDK (`zcatalyst-sdk-node`) initialized via `catalyst.initialize(context)` — simpler than GCP client library setup.
- Security Rules (`optional`/`required`) are built in — no separate Cloud Endpoints/API Gateway
  auth layer needed.
- Cold starts exist on both platforms.

**When a user says → they mean:**
- "I need a Cloud Function" → Catalyst Advanced I/O Function (HTTP-based)
- "I need a Cloud Function triggered by events" → Catalyst Event Function + Signals
- "I need a scheduled Cloud Function" → Job Scheduling
- "I need a background worker" → Catalyst Job Function

### AppSail → Google Cloud Run

Key differences:
- AppSail supports both managed runtimes (Node.js, Java, Python) AND custom Docker containers,
  mirroring Cloud Run's model.
- Auto-scaling is 1–5 instances (vs Cloud Run's 0–1000 range).
- SDK initialization is manual in AppSail: `catalyst.initialize(req)`.
- Use `process.env.X_ZOHO_CATALYST_LISTEN_PORT` instead of `PORT` (Cloud Run convention).

**When a user says → they mean:**
- "I need Cloud Run-style containers" → AppSail with Custom Runtime (Docker)
- "I need a persistent server, not serverless" → AppSail

---

## Data & Storage

### Data Store → Google Cloud SQL

Key differences:
- Uses ZCQL (not standard SQL) — case-sensitive table/column names, no cross-type JOINs,
  max 300 rows per query.
- No direct SQL access or connection strings — all access via SDK or ZCQL.
- System columns (ROWID, CREATORID, CREATEDTIME, MODIFIEDTIME) are auto-managed.

**When a user says → they mean:**
- "I need Cloud SQL / a managed relational database" → Data Store (note ZCQL differences)

### Stratus → Google Cloud Storage

Key differences:
- S3-compatible patterns (buckets, keys, prefixes).
- PII/ePHI compliance, versioning, malware scanning built in.

**When a user says → they mean:**
- "I need Cloud Storage / GCS" → Stratus
- "I need object/blob storage" → Stratus

### File Store — DEPRECATED (removal date TBD)

Migrate to Stratus.

### NoSQL → Google Cloud Firestore

Key differences:
- Collection-based document store — closest mental model is Firestore or MongoDB.
- Supports nested objects, arrays, query-by-field.
- No real-time listeners (no `onSnapshot` equivalent); no secondary indexes or aggregation pipelines.

**When a user says → they mean:**
- "I need Firestore" → NoSQL (for document/flexible schema) or Data Store (for relational/structured data)

### Cache → Google Cloud Memorystore

Key differences:
- Segment-based organization (not Redis key namespaces).
- String values only — serialize/deserialize JSON yourself.
- Max TTL 48 hours; max value 5MB.

**When a user says → they mean:**
- "I need Memorystore / Redis on GCP" → Cache (for basic caching needs)

### Search → (No direct GCP equivalent; closest is Vertex AI Search or self-hosted Elasticsearch)

Key differences:
- Catalyst Search covers Data Store tables only — not a general-purpose search engine.
- Enable per-column in console; simpler than managing Elasticsearch clusters.

---

## Frontend & Hosting

### Slate → Firebase Hosting / Cloud CDN

Key differences:
- Git-based deployments, preview deployments, SSR (Next.js) — similar to Firebase Hosting + Cloud Run for SSR.
- Integrated with all Catalyst backend services.

**When a user says → they mean:**
- "I need Firebase Hosting / GCP-based frontend hosting" → Slate

### Web Client Hosting — LEGACY

Use Slate for all new projects.

### Domain Mappings → Cloud Domains + Load Balancer

Free SSL certificates auto-provisioned.

---

## Workflow & Orchestration

### Circuits → Google Cloud Workflows

Key differences:
- Visual drag-and-drop builder — like Cloud Workflows but with a console UI.
- State types (Function, Condition, Wait, Parallel, End) map closely to Cloud Workflows steps.
- Invokable via SDK: `catalystApp.circuit().execute()`.

**When a user says → they mean:**
- "I need Cloud Workflows / workflow orchestration" → Circuits
- "I need to chain functions together" → Circuits

### Job Scheduling → Google Cloud Tasks

Key differences:
- Pool-based job management — similar to Cloud Tasks queues.
- Triggers Job Functions, Circuits, Webhooks, or AppSail services.

**When a user says → they mean:**
- "I need Cloud Tasks / background processing" → Job Scheduling + Job Functions
- "I need scheduled jobs" → Job Scheduling

---

## AI & Machine Learning

### Zia Services → Google Cloud Vision / Natural Language APIs

| Zia Service | GCP Equivalent |
|---|---|
| OCR | Cloud Vision OCR |
| Face Detection | Cloud Vision Face Detection |
| Image Moderation | Cloud Vision SafeSearch |
| Object Detection | Cloud Vision Object Localization |
| Text Analytics | Cloud Natural Language API |
| AutoML | Cloud AutoML |

**When a user says → they mean:**
- "I need Cloud Vision API" → Zia Services (OCR, Face Detection, Object Detection, Image Moderation)
- "I need Cloud Natural Language / NLP" → Zia Services Text Analytics
- "I need Cloud AutoML" → QuickML

### QuickML → Google Cloud AutoML

**When a user says → they mean:**
- "I need Cloud AutoML / no-code ML" → QuickML
- "I need to serve an ML model as an API" → QuickML

### ConvoKraft → Google Dialogflow

**When a user says → they mean:**
- "I need Dialogflow / a chatbot" → ConvoKraft
- "I need an AI assistant on my website" → ConvoKraft

---

## Integration & Events

### Signals → Google Cloud Pub/Sub

Key differences:
- Native Zoho product publishers (CRM, Books, Desk, People, Analytics) — no GCP equivalent for Zoho events.
- Supports publishers, subscribers, event routing, and schema validation.
- Replaces deprecated Event Listeners.

**When a user says → they mean:**
- "I need Cloud Pub/Sub / event-driven architecture" → Signals
- "I need to react to Zoho/CRM changes" → Signals

### Connections → Google Secret Manager

Key differences:
- Not just a secret store — actively manages OAuth2 token lifecycle (refresh, rotation).
- Pre-built Zoho connectors.

**When a user says → they mean:**
- "I need Secret Manager for API tokens" → Connections
- "I need to connect to third-party APIs with OAuth" → Connections

### Event Listeners — DEPRECATED (removal date TBD)
Replaced by **Signals**.

### Cron — DEPRECATED (removal date TBD)
Replaced by **Job Scheduling**.

---

## DevOps & CI/CD

### Pipelines → Google Cloud Build

Key differences:
- YAML-based pipeline config — similar to Cloud Build's `cloudbuild.yaml`.
- Integrated with GitHub, GitLab, Bitbucket.

**When a user says → they mean:**
- "I need Cloud Build / CI/CD" → Pipelines

### SmartBrowz → (No direct GCP equivalent; use Compute Engine/Cloud Run + Puppeteer)

Catalyst SmartBrowz is fully managed — no need to provision VMs or containers for headless Chrome.

**When a user says → they mean:**
- "I need headless browser automation on GCP" → SmartBrowz
- "I need web scraping / PDF generation" → SmartBrowz

### DevOps / Logs → Google Cloud Logging + Monitoring

Includes: Logs, APM (execution time, error rates, cold starts), and Application Alerts.

---

## Security & Identity

### Auth & User Management → Firebase Authentication (GCP-adjacent)

Key differences:
- Security Rules (`optional`/`required`) on functions — simpler than Firebase Auth + Firestore rules.
- Supports Zoho Accounts as an identity provider.

**When a user says → they mean:**
- "I need Firebase Auth / GCP-based user management" → Auth & User Management

### API Gateway → Google Cloud API Gateway

Key differences:
- Simpler — no OpenAPI spec required, no backend service configuration.
- Path-based routing, rate limiting, CORS, auth enforcement.

---

## Communication

### Mail → (No direct GCP equivalent; use SendGrid/Mailgun or GCP Workspace SMTP)

### Push Notifications → Firebase Cloud Messaging (FCM)

Catalyst Push Notifications integrates FCM for Android delivery.

---

## Quick Lookup: Catalyst ↔ GCP

| Catalyst Service | GCP Equivalent |
|---|---|
| Functions | Cloud Functions |
| AppSail | Cloud Run |
| Data Store | Cloud SQL |
| Stratus | Cloud Storage |
| NoSQL | Cloud Firestore |
| Cache | Cloud Memorystore |
| Search | — (Vertex AI Search for complex needs) |
| Slate | Firebase Hosting |
| Circuits | Cloud Workflows |
| Job Scheduling | Cloud Tasks |
| Signals | Cloud Pub/Sub |
| Connections | Secret Manager |
| Pipelines | Cloud Build |
| SmartBrowz | Cloud Run + Puppeteer (self-managed) |
| ConvoKraft | Dialogflow |
| QuickML | Cloud AutoML |
| Zia OCR | Vision OCR |
| Zia Text Analytics | Natural Language API |
| Zia Image/Vision | Vision API |
| Auth & Users | Firebase Auth |
| API Gateway | Cloud API Gateway |
| Push Notifications | Firebase Cloud Messaging (FCM) |
| DevOps / Logs | Cloud Logging + Monitoring |
| Domain Mapping | Cloud Domains + Load Balancer |
| ~~File Store~~ | — → **REMOVED, use Stratus** |
| ~~Event Listeners~~ | ~~Pub/Sub triggers~~ → **REMOVED, use Signals** |
| ~~Cron~~ | ~~Cloud Scheduler~~ → **REMOVED, use Job Scheduling** |
