# Cloud Scale Components Reference

## Table of Contents
1. [Data Store](#data-store)
2. [ZCQL (Catalyst Query Language)](#zcql)
3. [Stratus (Object Storage)](#stratus)
4. [NoSQL](#nosql)
5. [Cache](#cache)
6. [Search](#search)
7. [Authentication & User Management](#authentication--user-management)
8. [API Gateway](#api-gateway)
9. [Connections](#connections)
10. [Mail](#mail)
11. [Push Notifications](#push-notifications)
12. [Web Client Hosting](#web-client-hosting)
13. [Domain Mappings](#domain-mappings)
14. [Deprecated Components](#deprecated-components)

---

## Data Store

Catalyst Data Store is a fully-managed relational database. Tables are created and managed via the console.

### Concurrency limits

Each function has a default limit of **10 concurrent executions** per environment.

When the concurrency limit is hit, additional invocations are queued and then rejected
with HTTP 429 (Too Many Requests) if the queue is full.

To increase the limit, contact Catalyst support.

**Design for concurrency:** Use idempotent handlers, avoid shared mutable state,
and monitor via DevOps → Logs for throttling signals (HTTP 429 responses).

### System columns (auto-managed, present in every table)
- `ROWID` — unique row identifier (bigint, auto-increment)
- `CREATORID` — user ID of the creator
- `CREATEDTIME` — timestamp of creation
- `MODIFIEDTIME` — timestamp of last modification

### CREATEDTIME timezone behavior

`CREATEDTIME` and `MODIFIEDTIME` are stored in the **project's configured timezone** (e.g. Asia/Kolkata
for IST), but without a UTC offset marker. This means `new Date(row.CREATEDTIME)` treats the value
as UTC, causing an off-by-hours error equal to the timezone offset.

Passing the raw string to `new Date()` produces unpredictable results because Node.js
parses space-separated datetime strings as local time (not UTC). The correct approach
is to force UTC parsing by appending 'Z', then subtract the project timezone offset.

```javascript
// WRONG — space-separated datetime is parsed as LOCAL time in Node.js (not UTC):
const created = new Date(row.CREATEDTIME); // Unpredictable — depends on server timezone

// CORRECT — force UTC interpretation, then adjust for the project timezone:
function parseCatalystTime(catalystTimestamp, tzOffsetMinutes) {
  // tzOffsetMinutes: positive = ahead of UTC, e.g. IST = +330
  // Step 1: Parse as UTC by appending 'Z'
  const utcDate = new Date(catalystTimestamp.replace(' ', 'T').replace(/:(\d{3})$/, '.$1') + 'Z');
  // Step 2: The timestamp was actually in project timezone, so subtract the offset
  return new Date(utcDate.getTime() - tzOffsetMinutes * 60 * 1000);
}
// For IST (UTC+5:30 = +330 minutes):
const created = parseCatalystTime(row.CREATEDTIME, 330);
```

The project timezone is set during `catalyst init` and stored in `.catalystrc` (`timezone` field).

### CRUD Operations (Node.js SDK)

```javascript
// Get a table reference
const table = catalystApp.datastore().table('Employees');
// or by ID: const table = catalystApp.datastore().table(TABLE_ID);

// INSERT a row
const insertedRow = await table.insertRow({
  Name: 'Alice',
  Email: 'alice@example.com',
  Department: 'Engineering',
  Salary: 85000
});
console.log('Inserted ROWID:', insertedRow.ROWID);

// GET a row by ROWID
const row = await table.getRow(ROWID);

// GET all rows (paginated, max 200 per call)
const allRows = await table.getAllRows({
  nextToken: null,     // for pagination
  maxRows: 100         // max 200
});

// UPDATE a row (must include ROWID)
const updatedRow = await table.updateRow({
  ROWID: '12345',
  Salary: 90000
});

// DELETE a row
await table.deleteRow(ROWID);

// BULK INSERT (up to 200 rows)
const rows = [
  { Name: 'Bob', Email: 'bob@example.com' },
  { Name: 'Carol', Email: 'carol@example.com' }
];
const insertedRows = await table.insertRows(rows);

// BULK UPDATE (up to 200 rows, each must have ROWID)
const updatedRows = await table.updateRows([
  { ROWID: '123', Name: 'Robert' },
  { ROWID: '456', Name: 'Caroline' }
]);

// BULK DELETE
await table.deleteRows([ROWID_1, ROWID_2]);
```

### Column types supported
- Text, Integer, BigInt, Decimal, Double
- Boolean, Date, DateTime
- Foreign Key (references another table's ROWID)
- Text Area (for large text)
- Encrypted Text (for sensitive data)

### Data Store limitations

**Emoji and 4-byte UTF-8 characters**: Catalyst Data Store does not support 4-byte UTF-8 characters
(emoji, supplementary CJK, etc.) in Text or Text Area columns. These characters are silently
truncated or stored as `?` with no error thrown. Validate or strip emoji before inserting if your
data may contain them:

```javascript
// Strip 4-byte UTF-8 characters before inserting
function stripEmoji(str) {
  return str.replace(/[\u{10000}-\u{10FFFF}]/gu, '');
}
const safeName = stripEmoji(userInput);
await table.insertRow({ Name: safeName });
```

---

## ZCQL

ZCQL is Catalyst's query language, modeled after SQL with important differences.

### Basic queries
```javascript
const zcql = catalystApp.zcql();

// SELECT
const result = await zcql.executeZCQLQuery(
  "SELECT * FROM Employees WHERE Department = 'Engineering'"
);

// SELECT with conditions
const result = await zcql.executeZCQLQuery(
  "SELECT Name, Email FROM Employees WHERE Salary > 80000 ORDER BY Name ASC LIMIT 50"
);

// INSERT (prefer SDK methods, but ZCQL supports it)
await zcql.executeZCQLQuery(
  "INSERT INTO Employees (Name, Email) VALUES ('Dave', 'dave@example.com')"
);

// UPDATE
await zcql.executeZCQLQuery(
  "UPDATE Employees SET Salary = 95000 WHERE ROWID = 12345"
);

// DELETE
await zcql.executeZCQLQuery(
  "DELETE FROM Employees WHERE Department = 'Obsolete'"
);

// Aggregate functions
const result = await zcql.executeZCQLQuery(
  "SELECT COUNT(ROWID) AS total, AVG(Salary) AS avg_salary FROM Employees"
);
```

### Result structure — unwrapping

`executeZCQLQuery` returns an array of objects where each object wraps the row under the table name
as a key. You must unwrap before accessing fields:

```javascript
const result = await zcql.executeZCQLQuery("SELECT * FROM Employees");
// Raw result shape:
// [{ Employees: { ROWID: "123", Name: "Alice", Department: "Engineering" } }, ...]

// Unwrap to get plain row objects:
const rows = result.map(r => r.Employees).filter(Boolean);
// rows → [{ ROWID: "123", Name: "Alice", Department: "Engineering" }, ...]

// Generic helper for any table:
function unwrapZcql(result, tableName) {
  return result.map(r => r[tableName]).filter(Boolean);
}
const employees = unwrapZcql(result, 'Employees');
```

Important: the table name key is **case-sensitive** and must match the table name exactly as defined
in the console. Aggregate queries (e.g. `COUNT`, `AVG`) return a different shape — access via
`result[0]?.Employees` or inspect the raw result first.

### ZCQL differences from standard SQL
- Table names are **case-sensitive** — must match exactly as created in the console
- Column names are **case-sensitive**
- String values use **single quotes only**
- Supported aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
- `LIKE` operator is supported for pattern matching
- `IN`, `NOT IN`, `BETWEEN` are supported
- `ORDER BY` and `LIMIT` are supported
- `GROUP BY` and `HAVING` are supported
- `COALESCE` function is supported
- `DISTINCT` is supported
- **No JOINs** between tables of different types (you can join within the same Data Store)
- Results always include system columns unless you select specific columns
- Maximum 300 rows returned per query unless using pagination
- `LIMIT` maximum value is 300; use `LIMIT offset, count` syntax for pagination

### Pagination with ZCQL

#### Offset-based pagination (preferred)
```javascript
const PAGE_SIZE = 300;
let offset = 0;
let allResults = [];

while (true) {
  const batch = await zcql.executeZCQLQuery(
    `SELECT * FROM Employees ORDER BY ROWID LIMIT ${offset}, ${PAGE_SIZE}`
  );
  const rows = batch.map(r => r.Employees).filter(Boolean);
  if (rows.length === 0) break;
  allResults = allResults.concat(rows);
  if (rows.length < PAGE_SIZE) break;  // last page
  offset += PAGE_SIZE;
}
```

#### ROWID-based pagination (alternative)
```javascript
// Useful when rows may be deleted mid-fetch
let lastRowId = 0;
let allResults = [];

while (true) {
  const batch = await zcql.executeZCQLQuery(
    `SELECT * FROM Employees WHERE ROWID > ${lastRowId} ORDER BY ROWID LIMIT 300`
  );
  const rows = batch.map(r => r.Employees).filter(Boolean);
  if (rows.length === 0) break;
  allResults = allResults.concat(rows);
  lastRowId = rows[rows.length - 1].ROWID;
}
```

### JOINs

ZCQL supports INNER JOIN and LEFT JOIN between tables in the same Data Store:

```sql
-- INNER JOIN
SELECT E.Name, D.DeptName
FROM Employees E
INNER JOIN Departments D ON E.DeptId = D.ROWID

-- LEFT JOIN
SELECT E.Name, D.DeptName
FROM Employees E
LEFT JOIN Departments D ON E.DeptId = D.ROWID
```

Limitations:
- Only INNER JOIN and LEFT JOIN are supported (no RIGHT or FULL OUTER JOIN)
- Cross-table JOINs only — no cross-type JOINs (e.g., Data Store to NoSQL)
- JOINs are subject to the same 300-row result limit

### Transactions

Catalyst Data Store does **not** support multi-statement transactions. There is no
BEGIN / COMMIT / ROLLBACK.

**Workarounds for atomic operations:**
- Use single ZCQL statements that update multiple rows atomically (e.g., bulk UPDATE)
- Implement application-level saga patterns using Circuits for multi-step workflows
- Use optimistic concurrency control: read MODIFIEDTIME before update, verify it hasn't
  changed before writing, retry on conflict

---

## Stratus (Object Storage)

**Stratus is the preferred storage solution for ALL file/object storage needs in new Catalyst projects.**
S3-compatible object storage with bucket-based organization. Replaces the removed File Store.

### Key features
- **Buckets & Objects**: Data stored as objects in buckets, each with a unique Object URL
- **Path support**: Objects can be organized with path prefixes (e.g., `data/reports/file.json`)
- **Versioning**: Store multiple versions of each object, access by `versionId`
- **Data Encryption**: Encryption at rest and in flight when enabled
- **PII/ePHI**: HIPAA-compliant storage for sensitive/personally identifiable information
- **Malware scanning**: Automatic background scanning; infected objects are deleted immediately
- **Multipart uploads**: Upload large objects in parallel parts; auto-split if parts not specified
- **Transfer Manager**: Range-based downloads (specify start/end byte range for large objects)
- **Custom permissions**: JSON-based per-object and per-directory access rules
- **Third-party migration**: Direct migration from Amazon S3 and Google Cloud Storage via console

### Permission templates
- **Authenticated**: Only authenticated app users can access objects (default for most apps)
- **Public**: Any internet user can access objects without authorization
- Custom JSON rules can override per-object using `rule_id`, `condition`, `allowed_actions`
  (`GetObject`, `PutObject`, `DeleteObject`), `paths`, and `effect` (`allow`/`deny`)

### SDK Operations (Node.js)
```javascript
const stratus = catalystApp.stratus();
const bucket = stratus.bucket('my-bucket');
// Bucket name from Console → Cloud Scale → Stratus

// Upload an object
await bucket.putObject({
  key: 'data/file.json',
  body: JSON.stringify(data),
  contentType: 'application/json'
});

// Get/download an object
const obj = await bucket.getObject('data/file.json');

// Get a specific version (when versioning enabled)
const versionedObj = await bucket.getObject('data/file.json', {
  versionId: '01hter85pvexb8s2s2842rpswh'
});

// Delete an object
await bucket.deleteObject('data/file.json');

// List objects (with pagination)
const objects = await bucket.listObjects({
  prefix: 'data/',
  maxKeys: 100,
  continuationToken: null  // for pagination
});

// Check if bucket exists
const exists = await stratus.headBucket('my-bucket');
```

### SDK availability
- Server: Node.js (`catalystApp.stratus()`), Java (`ZCStratus.getInstance()`), Python
- Client: Web SDK, Android SDK, iOS SDK, Flutter SDK
- REST API: Full API support for all Stratus operations

### Upload size limits

- **Single-shot upload:** up to 100 MB
- **Multipart upload:** required for files larger than 100 MB

### Multipart upload (large files)

For files larger than 100 MB, use multipart upload:

```javascript
const stratus = catalystApp.stratus();
const bucket = stratus.bucket('my-bucket');

// Step 1: Initiate multipart upload
const upload = await bucket.initiateMultipartUpload({ key: 'large-file.zip' });
const uploadId = upload.uploadId;

// Step 2: Upload parts (each 5–100 MB)
const parts = [];
for (let i = 0; i < chunks.length; i++) {
  const part = await bucket.uploadPart({
    key: 'large-file.zip',
    uploadId,
    partNumber: i + 1,
    body: chunks[i]
  });
  parts.push({ partNumber: i + 1, eTag: part.eTag });
}

// Step 3: Complete upload
await bucket.completeMultipartUpload({
  key: 'large-file.zip',
  uploadId,
  parts
});
```

### Signed URLs (time-limited access)

```javascript
// Generate a pre-signed download URL (expires in 1 hour)
const url = await bucket.getSignedUrl({
  key: 'confidential-report.pdf',
  expiresIn: 3600 // seconds
});
// Share `url` with the client — no auth needed to download within the expiry window
```

---

## NoSQL

Document database for semi-structured data.

```javascript
const nosql = catalystApp.nosql();

// Access a collection
const collection = nosql.collection('UserProfiles');
// Collection name from Console → Cloud Scale → NoSQL

// Insert a document
const doc = await collection.insertDocument({
  userId: 'u123',
  preferences: { theme: 'dark', language: 'en' },
  tags: ['premium', 'beta']
});

// Get a document
const fetchedDoc = await collection.getDocument(DOCUMENT_ID);

// Update a document
await collection.updateDocument(DOCUMENT_ID, {
  preferences: { theme: 'light' }
});

// Delete a document
await collection.deleteDocument(DOCUMENT_ID);

// Query documents
const results = await collection.queryDocuments({
  filter: { 'preferences.theme': 'dark' }
});
```

---

## Cache

In-memory cache for ephemeral, real-time data. Organized in segments.

```javascript
const cache = catalystApp.cache();
const segment = cache.segment(SEGMENT_ID);
// Segment ID from Console → Cloud Scale → Cache → segment list

// Put a value (TTL in seconds, max 172800 = 48 hours)
await segment.put('user:123', JSON.stringify({ name: 'Alice' }), 3600);

// Get a value
const value = await segment.getValue('user:123');

// Delete a value
await segment.delete('user:123');

// Update a value
await segment.update('user:123', JSON.stringify({ name: 'Alice Updated' }));
```

Important: Cache values are strings only. Serialize/deserialize JSON yourself. Max value size: 5MB.
Max TTL: 48 hours (172800 seconds). Data is ephemeral and not persisted.

---

## Search

Full-text search across Data Store tables.

```javascript
const search = catalystApp.search();

// Search across all searchable columns
const results = await search.searchQuery('engineering manager', {
  search_table_columns: {
    Employees: ['Name', 'Title', 'Department']
  }
});
```

Search must be enabled per-column in the console. Only Text and Text Area columns can be searched.

---

## Authentication & User Management

```javascript
const userMgmt = catalystApp.userManagement();

// Get current user
const currentUser = await userMgmt.getCurrentUser();

// Get all users
const users = await userMgmt.getAllUsers();

// Get a specific user
const user = await userMgmt.getUserDetails(USER_ID);

// Delete a user
await userMgmt.deleteUser(USER_ID);

// Register a new user (sends invite email) <!-- VERIFY: single-arg vs two-arg form with platform team -->
const signupConfig = { platform_type: 'web', zaid: 'YOUR_ZAID' }; // ZAID from Settings → Environments
const userConfig = {
  email_id: 'newuser@example.com',
  first_name: 'New',
  last_name: 'User'
};
const newUser = await userMgmt.registerUser(signupConfig, userConfig);
```

Auth types supported: Catalyst built-in auth, Zoho accounts, custom SSO.

> **Embedded sign-in widget has no built-in signup flow.** `catalyst.auth.signIn("divId", config)`
> renders a Zoho IAM login iframe — there is no sign-up button or registration form inside it.
> For apps that require user registration, build a custom sign-up form and call
> `catalyst.auth.signUp()` from the Web SDK. Toggle between the login iframe and the custom form
> in your UI:
>
> ```javascript
> // Custom sign-up form handler
> await catalyst.auth.signUp({
>   first_name: firstName,
>   last_name: lastName,
>   email_id: email,
>   platform_type: 'web',
>   redirect_url: window.location.origin + '/app/index.html'
> });
> // The user receives a verification email from Zoho to activate their account.
> ```

### Authentication patterns

| Pattern | How to initialize | Use case |
|---------|------------------|----------|
| User-scoped (in Functions) | `catalyst.initialize(req)` | Operations on behalf of the logged-in user |
| Admin-scoped (in Functions) | `catalyst.initialize(req, { scope: 'admin' })` | System-level operations, background tasks |
| Admin-scoped (in AppSail) | Same as above | Server-to-server calls, scheduled tasks |

**For long-running AppSail services:** Use admin credentials for server-to-server calls.
Admin tokens are generated per-request and don't expire mid-operation.

> **DataStore permissions and App Users:** By default, the App User role has **Read-only** access to DataStore tables. Insert, Update, and Delete operations will return `"No privileges to perform this action"` even when the user is authenticated. Fix this in one of two ways:
> 1. **Console (recommended for most apps):** Data Store → select table → Permissions → enable Read, Insert, Update, Delete for the "App User" role. Repeat for each table.
> 2. **Admin-scoped SDK in backend:** Use `catalyst.initialize(req, { scope: 'admin' })` for DataStore operations. Still use user-scoped SDK (`catalyst.initialize(req)`) to call `getCurrentUser()` for authentication verification.
>
> ```javascript
> // Verify auth with user-scoped SDK
> const catalystApp = catalyst.initialize(req);
> const currentUser = await catalystApp.userManagement().getCurrentUser();
>
> // Perform DataStore ops with admin-scoped SDK
> const adminApp = catalyst.initialize(req, { scope: 'admin' });
> const dataStore = adminApp.datastore();
> const zcql = adminApp.zcql();
> ```

**Cross-project API calls:** Use Connections to authenticate between Catalyst projects
or between Catalyst and external Zoho services. Connections handle token refresh automatically.

---

## API Gateway

Create APIs that route to functions. Configured in the console or via CLI.

Features:
- Path-based routing to functions
- Rate limiting and throttling
- Authentication enforcement
- CORS configuration
- Request/response transformation
- API versioning

Enable via CLI:
```bash
catalyst api-gateway:enable
catalyst api-gateway:status
catalyst api-gateway:disable
```

### API Gateway configuration

API Gateway can be configured via the Catalyst Console or a config file.

**Console:** Catalyst Console → API Gateway → Routes

**Example route mapping:**
| Path pattern | Target | Auth | Rate limit |
|-------------|--------|------|------------|
| `/api/users/*` | Advanced I/O: `user_api` | required | 100 req/min |
| `/api/public/*` | Advanced I/O: `public_api` | optional | 50 req/min |
| `/api/admin/*` | Advanced I/O: `admin_api` | required | 20 req/min |

**CORS configuration (per-route):**
- Allowed Origins: `*` (or specific domains)
- Allowed Methods: `GET, POST, PUT, DELETE, OPTIONS`
- Allowed Headers: `Content-Type, Authorization`
- Max Age: `86400` (seconds)

API Gateway is the recommended way to expose functions publicly with rate limiting and
auth enforcement, rather than setting individual function security rules to `optional`.

---

## Connections

Token manager for third-party service integrations.

```javascript
const connection = catalystApp.connection();

// Get a connector by name
const connector = connection.getConnector('ZohoCRM');

// Get access token
const token = await connector.getAccessToken();
```

Connections handle OAuth2 token refresh automatically. Set up connection details in the console.

---

## Mail

Send emails from your application.

```javascript
const email = catalystApp.email();

await email.sendMail({
  from_email: 'noreply@yourdomain.com',
  to_email: ['user@example.com'],
  subject: 'Welcome!',
  content: '<h1>Hello!</h1><p>Welcome to our app.</p>',
  html_mode: true
});
```

Requires email configuration in the console (domain verification, sender setup).

---

## Push Notifications

Send push notifications to mobile/web apps.

```javascript
const pushNotification = catalystApp.pushNotification();

// Send to specific users
await pushNotification.sendNotification({
  message: 'New update available!',
  recipients: [USER_ID_1, USER_ID_2]
});
```

Requires push notification setup in project settings (APNs for iOS, FCM for Android).

---

## Web Client Hosting

> **⚠️ Legacy frontend hosting.** For new projects, use **Slate** instead — it offers Git-based workflows,
> framework-native builds, SSR support, and preview deployments. Web Client Hosting is the older approach
> using the `client/` directory.

Host frontend applications on Catalyst's CDN.

- Deploy via CLI: `catalyst deploy --only client`
- Supports any frontend framework (React, Vue, Angular, vanilla HTML/CSS/JS)
- Client files go in the `client/` directory
- `index.html` is the entry point
- Supports versioning — previous deployments are retained
- Custom domain mapping available

---

## Domain Mappings

Map custom domains to your Catalyst app.

- Configure in the console under Cloud Scale → Domain Mappings
- Free SSL certificates provided automatically
- Supports subdomain mapping
- DNS configuration required (CNAME record)

---

## Deprecated Components

> **⚠️ The following components are deprecated** (announced August 27, 2025, originally scheduled for removal April 30, 2026 — still functional with deprecation warnings, removal date TBD).
> Never use these for new projects. Users who signed up after August 27, 2025 cannot access them.

### File Store — DEPRECATED → Use Stratus

Simple file storage with folder-based organization. 100MB-per-file limit. File Store supports
direct migration to Stratus via the console before removal.

```javascript
// REMOVED — use catalystApp.stratus() instead
const fileStore = catalystApp.filestore();
const folder = fileStore.folder(FOLDER_ID);
await folder.uploadFile({ code: fileBuffer, name: 'report.pdf' });
const fileContent = await folder.downloadFile(FILE_ID);
await folder.deleteFile(FILE_ID);
const files = await folder.getAllFiles();
```

### Event Listeners — DEPRECATED → Use Signals

React to events by triggering Event Functions. Three categories: Component Events (Data Store/File
Store changes), Custom Events (triggered via SDK/API), Zoho Events. No direct migration to Signals
— business logic must be rebuilt.

```javascript
// DEPRECATED — use Signals instead
const event = catalystApp.event();
await event.trigger('my_custom_event', { key: 'value', timestamp: Date.now() });
```

### Cron — DEPRECATED → Use Job Scheduling

Schedule jobs that invoke Cron Functions. One-time or recurring (cron expressions). No direct
migration to Job Scheduling — schedulers must be reconfigured.
