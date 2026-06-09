# Catalyst ↔ Firebase Equivalents

Firebase is one of the closest conceptual analogues to Catalyst — both are integrated full-stack platforms
combining auth, database, storage, functions, and hosting. Use this file when users come from Firebase
or ask "is Catalyst like Firebase?" / "how does Firestore map to Catalyst?".

> **Deprecated services:** Event Listeners → Signals, File Store → Stratus, Cron → Job
> Scheduling (deprecated, removal date TBD). Never recommend deprecated components for new projects.

---

## Service-by-Service Mapping

### Firebase Authentication → Catalyst Auth & User Management

Key similarities:
- Both provide client-side auth SDKs (`catalyst.auth.login()` ≈ `firebase.auth().signInWith...`).
- Both support custom SSO and third-party identity providers.

Key differences:
- Catalyst's Security Rules (`optional`/`required`) live on each function — simpler than
  Firebase's per-collection Firestore security rules.
- Catalyst supports Zoho Accounts as a native identity provider.
- No Firebase App Check equivalent; Catalyst uses function-level access control instead.

**When a user says → they mean:**
- "I need Firebase Authentication" → Auth & User Management
- "I need user sign-up / login" → Auth & User Management

---

### Firebase Firestore → Catalyst NoSQL

**For Firestore users:** Use Catalyst **NoSQL** — collection-based document store with nested objects
and query-by-field. Closest mental model.

Key differences from Firestore:
- No real-time listeners (`onSnapshot` has no equivalent in Catalyst).
- No secondary indexes or aggregation pipelines.
- No subcollections — use flat document structure or top-level collections.
- Query model is simpler (field equality / range — no compound index requirements).

**When a user says → they mean:**
- "I need Firestore" → NoSQL

---

### Firebase Realtime Database → Catalyst NoSQL or Data Store

- Use **NoSQL** for flexible/document schema (closer mental model to RTDB's JSON tree).
- Use **Data Store** for structured/relational data with ZCQL queries.
- Catalyst has no real-time push equivalent — use Signals for event-driven updates between services,
  or client-side polling for UI refresh.

**When a user says → they mean:**
- "I need Realtime Database" → NoSQL (flexible schema) or Data Store (structured)

---

### Firebase Storage → Catalyst Stratus

Key differences:
- Stratus is S3-compatible (bucket/object model) — more flexible than Firebase Storage's folder/path model.
- Stratus supports versioning, multipart upload, malware scanning, and PII/ePHI compliance.
- No Firebase Storage Security Rules equivalent — access is controlled via function-level Security Rules
  or pre-signed URL patterns in the SDK.

**When a user says → they mean:**
- "I need Firebase Storage" → Stratus

---

### Cloud Functions for Firebase → Catalyst Functions

Key differences:
- Firebase Functions support TypeScript/JS only; Catalyst supports Node.js, Java, and Python.
- Catalyst has 7 specialized function types with distinct handler signatures; Firebase has one model
  with various trigger types (HTTP, Firestore, Auth, Pub/Sub, etc.).
- Catalyst SDK (`zcatalyst-sdk-node`) is initialized via `catalyst.initialize(context)`; Firebase uses `admin.initializeApp()`.
- No direct equivalent to Firebase's `onDocumentCreated`/`onDocumentUpdated` triggers — use
  Signals (event bus) or Job Scheduling to replicate that pattern.

**When a user says → they mean:**
- "I need Cloud Functions for Firebase (HTTP)" → Advanced I/O Function
- "I need a Firestore-triggered function" → Event Function + Signals (Signals publishes the change event)
- "I need an Auth-triggered function" → Event Function + Signals

---

### Firebase Hosting → Catalyst Slate

Key differences:
- Slate supports SSR (Next.js) natively — Firebase Hosting requires Cloud Run for SSR.
- Slate supports multiple frontend apps per Catalyst project; Firebase Hosting is typically one
  deployment target per project (preview channels aside).
- Both support custom domains with auto-SSL.
- Both support git-based deployments (Slate via Pipelines or console; Firebase via Firebase CLI).

**When a user says → they mean:**
- "I need Firebase Hosting" → Slate
- "I need frontend hosting with SSR" → Slate
- "I need preview deployments" → Slate

---

### Firebase Cloud Messaging (FCM) → Catalyst Push Notifications

Catalyst Push Notifications integrates FCM (Android) and APNs (iOS) as the underlying delivery layer.
The Catalyst SDK wraps this — FCM setup (Server Key) is still required.

---

### Firebase ML → Zia Services + QuickML

| Firebase ML Feature | Catalyst Equivalent |
|---|---|
| Vision APIs (labels, text, faces) | Zia Services (OCR, Face Detection, Object Detection) |
| Natural Language | Zia Services Text Analytics |
| Custom Model Hosting | QuickML (no-code model training + API deployment) |
| AutoML (Vision/NL) | QuickML |

---

### Firebase Extensions → Catalyst CodeLib

Both provide pre-built, deployable functionality. CodeLib is Catalyst's equivalent of Firebase Extensions
— reusable modules deployable into a project.

---

## Real-time: What Firebase Has That Catalyst Does Not

Firebase's key capability not replicated in Catalyst:
- **Real-time listeners** (`onSnapshot`, RTDB `on('value')`) — Catalyst has no push-based real-time
  data sync to clients.

Workarounds:
- Use **Signals** to propagate events between backend services.
- Use **client-side polling** (setInterval + REST/SDK call) for UI refresh.
- For chat/collaboration use cases, consider a dedicated WebSocket layer via AppSail.

---

## Holistic Comparison: Firebase vs Catalyst

| Dimension | Firebase | Catalyst |
|---|---|---|
| Database | Firestore (document) + RTDB | Data Store (relational, ZCQL) + NoSQL (document) |
| Storage | Firebase Storage | Stratus (S3-compatible) |
| Auth | Firebase Auth | Auth & User Management |
| Functions | Cloud Functions for Firebase (JS/TS) | 7 function types (Node.js / Java / Python) |
| Hosting | Firebase Hosting (static + SPA; SSR via Cloud Run) | Slate (static + SSR natively) |
| Events | Firestore/Auth/Storage triggers | Signals (event bus with Zoho integration) |
| Real-time | Yes (`onSnapshot`, RTDB) | No native real-time |
| Zoho integration | None | Native (CRM, Books, Desk, People, Analytics, etc.) |
| Workflow orchestration | — | Circuits (visual, Step Functions-like) |
| Background jobs | — | Job Scheduling |
| AI / ML | Firebase ML (vision, NLP) | Zia Services + QuickML + ConvoKraft |
| Pricing | Pay-as-you-go (Blaze) / Spark (free) | Pay-as-you-go / Subscription + $250 trial credits |

**Catalyst's key advantages over Firebase:**
- Native Zoho product integration eliminates glue code for Zoho-ecosystem businesses.
- Relational database with ZCQL alongside a document NoSQL store.
- Richer compute model (7 function types, AppSail, Circuits, Job Scheduling).
- Richer AI/ML surface (Zia Services, QuickML, ConvoKraft, SmartBrowz).

**Firebase's key advantages over Catalyst:**
- Real-time data sync (`onSnapshot`) with no polling required.
- Larger community, ecosystem, and third-party library support.
- Deep Google Cloud integration (BigQuery export, Cloud Run triggers, etc.).
