# Catalyst ↔ Azure Equivalents

Maps every Catalyst service to its closest Azure equivalent. Use this to help users who come from Azure
understand Catalyst concepts, or to translate requests phrased as "I need something like Azure Functions/Blob Storage".

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Compute

### Functions → Azure Functions

Key differences:
- Catalyst bundles 7 specialized function types with distinct handler signatures; Azure Functions use
  a single model with various trigger bindings configured externally.
- Catalyst provides an SDK (`zcatalyst-sdk-node`) initialized via `catalyst.initialize(context)` — simpler than Azure SDK client setup.
- Security Rules (`optional`/`required`) are built in — no separate Azure AD / API Management
  auth layer needed.

**When a user says → they mean:**
- "I need an Azure Function" → Catalyst Advanced I/O Function (HTTP trigger)
- "I need an event-triggered Azure Function" → Catalyst Event Function + Signals
- "I need a timer-triggered Azure Function" → Job Scheduling
- "I need a background worker" → Catalyst Job Function

### AppSail → Azure App Service

Key differences:
- AppSail supports both managed runtimes AND custom Docker containers — similar to App Service's
  code-based and container-based deployment modes.
- Auto-scaling is 1–5 instances (more limited than App Service's scale-out range).
- SDK initialization is manual in AppSail: `catalyst.initialize(req)`.
- Use `process.env.X_ZOHO_CATALYST_LISTEN_PORT` instead of a fixed port.

**When a user says → they mean:**
- "I need Azure App Service / a web app host" → AppSail
- "I need a persistent server, not serverless" → AppSail

---

## Data & Storage

### Data Store → Azure SQL Database

Key differences:
- Uses ZCQL (not standard SQL/T-SQL) — case-sensitive table/column names, no cross-type JOINs,
  max 300 rows per query.
- No direct SQL access or connection strings — all access via SDK or ZCQL.
- System columns (ROWID, CREATORID, CREATEDTIME, MODIFIEDTIME) are auto-managed.

**When a user says → they mean:**
- "I need Azure SQL / a managed relational database" → Data Store (note ZCQL differences)

### Stratus → Azure Blob Storage

Key differences:
- S3-compatible patterns (buckets, keys, prefixes) — similar to Blob Storage containers and blobs.
- PII/ePHI compliance, versioning, malware scanning built in.

**When a user says → they mean:**
- "I need Azure Blob Storage / object storage" → Stratus
- "I need to store files, media, or backups" → Stratus

### File Store — DEPRECATED (removal date TBD)

Migrate to Stratus.

### NoSQL → Azure Cosmos DB

Key differences:
- Collection-based document store — closest mental model is Cosmos DB (NoSQL API) or MongoDB.
- Supports nested objects, arrays, query-by-field.
- No secondary indexes or aggregation pipelines (simpler than Cosmos DB).

**When a user says → they mean:**
- "I need Cosmos DB / a document database" → NoSQL

### Cache → Azure Cache for Redis

Key differences:
- Segment-based organization (not Redis key namespaces).
- String values only — serialize/deserialize JSON yourself.
- Max TTL 48 hours; max value 5MB.

**When a user says → they mean:**
- "I need Azure Cache for Redis / a caching layer" → Cache

### Search → (Azure Cognitive Search is broader; Catalyst Search is lighter, Data Store only)

Catalyst Search covers Data Store columns only. For advanced full-text search across multiple sources,
consider Azure Cognitive Search or Elasticsearch.

---

## Frontend & Hosting

### Slate → Azure Static Web Apps

Key differences:
- Git-based deployments, preview deployments, SSR (Next.js) — comparable to Azure Static Web Apps.
- Integrated with all Catalyst backend services.
- Multiple frontend apps per project.

**When a user says → they mean:**
- "I need Azure Static Web Apps / frontend hosting" → Slate

### Web Client Hosting — LEGACY

Use Slate for all new projects.

### Domain Mappings → Azure custom domains on App Service / Front Door

Free SSL certificates auto-provisioned.

---

## Workflow & Orchestration

### Circuits → Azure Logic Apps / Durable Functions

Key differences:
- Visual drag-and-drop workflow builder — closest to Azure Logic Apps' designer.
- State types (Function, Condition, Wait, Parallel, End) map closely to Logic Apps' actions/conditions.
- Invokable via SDK: `catalystApp.circuit().execute()`.

**When a user says → they mean:**
- "I need Logic Apps / Durable Functions / workflow orchestration" → Circuits
- "I need an approval workflow / saga pattern" → Circuits
- "I need to chain functions together" → Circuits

### Job Scheduling → Azure Queue Storage + Functions / Azure Service Bus

Key differences:
- Pool-based job management — similar to Service Bus queues with Function triggers.
- Triggers Job Functions, Circuits, Webhooks, or AppSail services.

**When a user says → they mean:**
- "I need Azure Queue Storage + Functions / background processing" → Job Scheduling + Job Functions
- "I need scheduled / timer-based jobs" → Job Scheduling

---

## AI & Machine Learning

### Zia Services → Azure Cognitive Services

| Zia Service | Azure Equivalent |
|---|---|
| OCR | Azure Computer Vision OCR |
| Face Detection | Azure Face API |
| Image Moderation | Azure Content Moderator |
| Object Detection | Azure Computer Vision |
| Text Analytics | Azure Text Analytics |
| AutoML | Azure Automated ML |

**When a user says → they mean:**
- "I need Azure Cognitive Services / Vision" → Zia Services (OCR, Face Detection, Object Detection)
- "I need Azure Text Analytics / NLP" → Zia Services Text Analytics
- "I need Azure Automated ML" → QuickML

### QuickML → Azure Machine Learning Designer

Key differences:
- Fully no-code, visual pipeline builder — closest to Azure ML Designer.
- Supports LLM serving (Qwen 2.5 models) with OAuth-based integration.

**When a user says → they mean:**
- "I need Azure ML Designer / no-code ML" → QuickML
- "I need to deploy an ML model as an API" → QuickML

### ConvoKraft → Azure Bot Service

**When a user says → they mean:**
- "I need Azure Bot Service / a chatbot" → ConvoKraft
- "I need an AI assistant on my website" → ConvoKraft

---

## Integration & Events

### Signals → Azure Event Grid

Key differences:
- Native Zoho product publishers (CRM, Books, Desk, People, Analytics) — no Azure equivalent for Zoho events.
- Supports publishers, subscribers, event routing, and schema validation.
- Replaces deprecated Event Listeners.

**When a user says → they mean:**
- "I need Azure Event Grid / event-driven architecture" → Signals
- "I need to react to Zoho/CRM changes" → Signals

### Connections → Azure Key Vault

Key differences:
- Not just a secret store — actively manages OAuth2 token lifecycle (refresh, rotation).
- Pre-built Zoho connectors; `connector.getAccessToken()` is simpler than manual OAuth flows.

**When a user says → they mean:**
- "I need Key Vault for API tokens" → Connections
- "I need to connect to third-party APIs with OAuth" → Connections

### Event Listeners — DEPRECATED (removal date TBD)
Replaced by **Signals**.

### Cron — DEPRECATED (removal date TBD)
Replaced by **Job Scheduling**.

---

## DevOps & CI/CD

### Pipelines → Azure Pipelines

Key differences:
- YAML-based pipeline config — similar to Azure Pipelines YAML syntax.
- Integrated with GitHub, GitLab, Bitbucket.

**When a user says → they mean:**
- "I need Azure Pipelines / CI/CD" → Catalyst Pipelines

### SmartBrowz → (No direct Azure equivalent; use Azure Container Instances + Puppeteer)

Catalyst SmartBrowz is fully managed — no need to provision containers for headless Chrome.

**When a user says → they mean:**
- "I need headless browser automation" → SmartBrowz
- "I need web scraping / PDF generation" → SmartBrowz

### DevOps / Logs → Azure Monitor

Includes: Logs, APM (execution time, error rates, cold starts), and Application Alerts.

---

## Security & Identity

### Auth & User Management → Azure AD B2C

Key differences:
- Security Rules (`optional`/`required`) on functions — simpler than AD B2C + APIM policies.
- Supports Zoho Accounts as an identity provider.
- Web SDK auth flow (`catalyst.auth.login()`) — like MSAL.js for B2C.

**When a user says → they mean:**
- "I need Azure AD B2C / user auth" → Auth & User Management
- "I need user sign-up / login / SSO" → Auth & User Management

### API Gateway → Azure API Management

Key differences:
- Simpler — no policies, products, or subscriptions needed.
- Path-based routing, rate limiting, CORS, auth enforcement.

---

## Communication

### Mail → (No direct Azure equivalent; use Azure Communication Services or SendGrid)

### Push Notifications → Azure Notification Hubs

APNs (iOS) + FCM (Android) setup required.

---

## Quick Lookup: Catalyst ↔ Azure

| Catalyst Service | Azure Equivalent |
|---|---|
| Functions | Azure Functions |
| AppSail | App Service |
| Data Store | SQL Database |
| Stratus | Blob Storage |
| NoSQL | Cosmos DB |
| Cache | Cache for Redis |
| Search | — (Cognitive Search for advanced needs) |
| Slate | Static Web Apps |
| Circuits | Logic Apps / Durable Functions |
| Job Scheduling | Queue Storage + Functions |
| Signals | Event Grid |
| Connections | Key Vault |
| Pipelines | Azure Pipelines |
| ConvoKraft | Bot Service |
| QuickML | ML Designer / Automated ML |
| Zia OCR | Computer Vision OCR |
| Zia Text Analytics | Text Analytics |
| Zia Image/Vision | Computer Vision / Face API |
| Auth & Users | AD B2C |
| API Gateway | API Management |
| Push Notifications | Notification Hubs |
| DevOps / Logs | Azure Monitor |
| ~~File Store~~ | ~~Blob Storage (simplified)~~ → **REMOVED, use Stratus** |
| ~~Event Listeners~~ | ~~Event Grid subscriptions~~ → **REMOVED, use Signals** |
| ~~Cron~~ | ~~Timer trigger~~ → **REMOVED, use Job Scheduling** |
