# Catalyst ↔ AWS Equivalents

Maps every Catalyst service to its closest AWS equivalent. Use this to help users who come from AWS
understand Catalyst concepts, or to translate requests phrased as "I need something like Lambda/S3/RDS".

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Compute

### Functions → AWS Lambda

Key differences from Lambda:
- Catalyst bundles 7 specialized function types with distinct handler signatures; Lambda uses a single
  model with event sources configured externally.
- Catalyst provides an SDK (`zcatalyst-sdk-node`) initialized via `catalyst.initialize(context)` — simpler than `require('aws-sdk')` with manual credential setup.
- Security Rules (`optional`/`required`) are built into function config — no separate
  IAM + API Gateway auth layer required as in AWS.
- Cold starts exist on both; Catalyst defaults to 128MB memory (max 1024MB), comparable to Lambda's range.

**When a user says → they mean:**
- "I need a Lambda function" → Catalyst Advanced I/O Function (most flexible, HTTP-based)
- "I need a Cloud Function triggered by events" → Catalyst Event Function + Signals
- "I need a scheduled Lambda" → Job Scheduling (not deprecated Cron)
- "I need a background worker" → Catalyst Job Function

### AppSail → AWS App Runner / Elastic Beanstalk

Key differences from App Runner:
- AppSail supports both managed runtimes (Node.js, Java, Python) AND custom Docker containers.
- Auto-scaling is 1–5 instances (more limited than App Runner's scale).
- SDK initialization is manual in AppSail: `catalyst.initialize(req)` — same mental model as
  initializing the AWS SDK in an ECS/App Runner container.
- Use `process.env.X_ZOHO_CATALYST_LISTEN_PORT` instead of a fixed port.

**When a user says → they mean:**
- "I want to deploy an Express app like on Elastic Beanstalk / App Runner" → AppSail with managed Node.js runtime
- "I need a persistent server, not serverless" → AppSail

---

## Data & Storage

### Data Store → Amazon RDS

Key differences:
- Uses ZCQL (not standard SQL) — case-sensitive table/column names, no cross-type JOINs,
  max 300 rows per query.
- No direct SQL access or connection strings — all access via SDK or ZCQL.
- System columns (ROWID, CREATORID, CREATEDTIME, MODIFIEDTIME) are auto-managed.

**When a user says → they mean:**
- "I need RDS / a relational database" → Data Store (note ZCQL differences)
- "I need a relational DB with an admin UI" → Data Store (web console)

### Stratus → Amazon S3

Key differences:
- S3-compatible patterns (buckets, keys, prefixes) — S3 users will feel at home.
- PII/ePHI compliance, versioning, malware scanning built in.
- No per-file size constraints at the default tier.

**When a user says → they mean:**
- "I need S3" → Stratus
- "I need object/blob storage" → Stratus
- "I need to store user uploads, media, or backups" → Stratus

### File Store → (A simplified S3 with folder semantics) — DEPRECATED (removal date TBD)

Migrate to Stratus. Only reference for legacy projects.

### NoSQL → Amazon DynamoDB

Key differences:
- Collection-based document store — closer to Firestore or MongoDB than DynamoDB.
- Supports nested objects, arrays, query-by-field.
- No secondary indexes or aggregation pipelines.

**When a user says → they mean:**
- "I need DynamoDB" → NoSQL (document model) or Data Store (relational model, depends on use case)

### Cache → Amazon ElastiCache (Redis/Memcached)

Key differences:
- Segment-based organization (not key namespaces like Redis).
- String values only — serialize/deserialize JSON yourself.
- Max TTL of 48 hours (ElastiCache/Redis has no default TTL limit).
- Max value size 5MB (vs Redis's 512MB).

**When a user says → they mean:**
- "I need ElastiCache / Redis" → Cache (for basic caching needs)
- "I need session storage" → Cache (note 48hr TTL limit)

### Search → Amazon OpenSearch / CloudSearch

Key differences:
- Searches Data Store tables only — not a general-purpose search engine like OpenSearch.
- Must enable per-column in console; simpler than managing OpenSearch clusters.

**When a user says → they mean:**
- "I need OpenSearch / CloudSearch" → Search (for Data Store data); suggest external service for complex needs

---

## Frontend & Hosting

### Slate → AWS Amplify Hosting

Key differences:
- Git-based deployments (GitHub, GitLab, Bitbucket), preview deployments, SSR (Next.js) — comparable to Amplify Hosting.
- Integrated with all Catalyst backend services — no need to wire up separate services as with Amplify.

**When a user says → they mean:**
- "I need Amplify Hosting" → Slate

### Web Client Hosting → AWS S3 Static Website Hosting — LEGACY

Use Slate for all new projects.

### Domain Mappings → Route 53 + CloudFront custom domains

Free SSL certificates auto-provisioned (like ACM + CloudFront on AWS).

---

## Workflow & Orchestration

### Circuits → AWS Step Functions

Key differences:
- Visual drag-and-drop builder in the console — like Step Functions Visual Workflow Studio.
- State types (Function, Condition, Wait, Parallel, End) map directly to Step Functions states
  (Task, Choice, Wait, Parallel, End).
- Invokable via SDK: `catalystApp.circuit().execute()` — same mental model as the Step Functions SDK.

**When a user says → they mean:**
- "I need Step Functions" → Circuits
- "I need workflow orchestration / a saga pattern / an approval workflow" → Circuits
- "I need to chain functions together" → Circuits

### Job Scheduling → AWS SQS + Lambda / AWS Batch

Key differences:
- Pool-based job management — similar to Batch job queues.
- Triggers Job Functions, Circuits, Webhooks, or AppSail services.
- Replaces deprecated Cron for scheduled tasks.

**When a user says → they mean:**
- "I need SQS + Lambda for background jobs" → Job Scheduling + Job Functions
- "I need scheduled / cron jobs" → Job Scheduling

---

## AI & Machine Learning

### Zia Services → Amazon Rekognition / Textract / Comprehend

| Zia Service | AWS Equivalent |
|---|---|
| OCR | Amazon Textract |
| Barcode Scanner | AWS (custom Lambda) |
| Face Detection | Amazon Rekognition |
| Image Moderation | Rekognition Content Moderation |
| Object Detection | Rekognition Labels |
| Text Analytics | Amazon Comprehend |
| AutoML | SageMaker Autopilot |

**When a user says → they mean:**
- "I need Rekognition" → Zia Services (Face Detection, Image Moderation, Object Detection)
- "I need Textract / OCR" → Zia Services OCR
- "I need Comprehend / NLP" → Zia Services Text Analytics

### QuickML → Amazon SageMaker Canvas

Key differences:
- Fully no-code, visual pipeline builder — closest to SageMaker Canvas.
- Supports LLM serving (Qwen 2.5 models) with chat interface and OAuth-based integration.
- Data connectors, preprocessing, and model deployment as API endpoints — all via console.

**When a user says → they mean:**
- "I need SageMaker / AutoML without code" → QuickML
- "I need to deploy an ML model as an API" → QuickML

### ConvoKraft → Amazon Lex

**When a user says → they mean:**
- "I need Lex / a chatbot" → ConvoKraft

---

## Integration & Events

### Signals → Amazon EventBridge

Key differences:
- Native Zoho product publishers (CRM, Books, Desk, People, Analytics) — no AWS equivalent for Zoho-specific events.
- Replaces deprecated Event Listeners for event-driven architectures.

**When a user says → they mean:**
- "I need EventBridge" → Signals
- "I need event-driven architecture" → Signals
- "I need to react to CRM / Zoho changes" → Signals

### Connections → AWS Secrets Manager

Key differences:
- Not just a secret store — actively manages OAuth2 token lifecycle (refresh, rotation).
- Pre-built Zoho connectors; `connector.getAccessToken()` is simpler than manual OAuth flows.

**When a user says → they mean:**
- "I need Secrets Manager for API tokens" → Connections
- "I need to connect to third-party APIs with OAuth" → Connections

### Event Listeners — DEPRECATED (removal date TBD)
Replaced by **Signals**.

### Cron — DEPRECATED (removal date TBD)
Replaced by **Job Scheduling**.

---

## DevOps & CI/CD

### Pipelines → AWS CodePipeline + CodeBuild

Key differences:
- YAML-based pipeline config — similar to CodeBuild buildspec.
- Integrated with GitHub, GitLab, Bitbucket.

**When a user says → they mean:**
- "I need CodePipeline / CodeBuild / CI/CD" → Pipelines

### SmartBrowz → AWS Lambda + Puppeteer Layer

Key differences:
- Fully managed headless browser — no need to package Puppeteer/Chromium in a Lambda layer.
- Supports scraping, screenshots, PDF generation, browser automation.
- Uses Browser Logic Functions with Puppeteer-like API.

**When a user says → they mean:**
- "I need Lambda Puppeteer / headless browser in the cloud" → SmartBrowz
- "I need web scraping / PDF from HTML" → SmartBrowz

### DevOps/Logs → Amazon CloudWatch

Includes: Logs, APM (execution time, error rates, cold starts), and Application Alerts.

---

## Security & Identity

### Auth & User Management → Amazon Cognito

Key differences:
- Security Rules (`optional`/`required`) are simpler than Cognito + API Gateway authorizers.
- Web SDK auth flow (`catalyst.auth.login()`) — like the Cognito Hosted UI or Amplify Auth.
- Supports Zoho Accounts as an identity provider.

**When a user says → they mean:**
- "I need Cognito" → Auth & User Management
- "I need user sign-up / login" → Auth & User Management

### API Gateway → Amazon API Gateway

Key differences:
- Simpler — no stages, usage plans, or Lambda authorizers needed.
- Path-based routing, rate limiting, CORS, auth enforcement via console or CLI.

---

## Communication

### Mail → Amazon SES

Domain verification required before sending.

### Push Notifications → Amazon SNS (mobile push)

APNs (iOS) + FCM (Android) setup required.

---

## Quick Lookup: Catalyst ↔ AWS

| Catalyst Service | AWS Equivalent |
|---|---|
| Functions | Lambda |
| AppSail | App Runner / Elastic Beanstalk |
| Data Store | RDS |
| Stratus | S3 |
| NoSQL | DynamoDB |
| Cache | ElastiCache |
| Search | OpenSearch / CloudSearch |
| Slate | Amplify Hosting |
| Circuits | Step Functions |
| Job Scheduling | SQS + Lambda / Batch |
| Signals | EventBridge |
| Connections | Secrets Manager |
| Pipelines | CodePipeline + CodeBuild |
| SmartBrowz | Lambda + Puppeteer layer |
| ConvoKraft | Lex |
| QuickML | SageMaker Canvas |
| Zia OCR | Textract |
| Zia Text Analytics | Comprehend |
| Zia Image/Vision | Rekognition |
| Auth & Users | Cognito |
| API Gateway | API Gateway |
| Mail | SES |
| Push Notifications | SNS |
| DevOps / Logs | CloudWatch |
| ~~File Store~~ | ~~S3 (simplified)~~ → **REMOVED, use Stratus** |
| ~~Event Listeners~~ | ~~EventBridge rules~~ → **REMOVED, use Signals** |
| ~~Cron~~ | ~~EventBridge Scheduler~~ → **REMOVED, use Job Scheduling** |
