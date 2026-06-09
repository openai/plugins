# Node.js SDK Reference (zcatalyst-sdk-node)

Install via `npm install zcatalyst-sdk-node`.
External docs: https://docs.catalyst.zoho.com/en/sdk/nodejs/v2/overview/

> All versions earlier than 2.5.0 are deprecated. Always use the latest version.

---

## Initialization

```js
const catalyst = require('zcatalyst-sdk-node');

// --- Advanced I/O (Express) ---
// In an Express-based Advanced I/O function, pass the Express request object:
app.post('/api/action', async (req, res) => {
  const catalystApp = catalyst.initialize(req);
  // ... use catalystApp
});

// --- Basic I/O ---
// In a Basic I/O function, pass the context object:
module.exports = async (context, basicIO) => {
  const catalystApp = catalyst.initialize(context);
  // ... use catalystApp
  basicIO.write(JSON.stringify({ status: 'ok' }));
  context.close();
};

// --- Event Function ---
module.exports = async (event, context) => {
  const catalystApp = catalyst.initialize(context);
  // event.data contains the event payload
  context.close();
};

// --- Cron Function ---
module.exports = async (cronDetails, context) => {
  const catalystApp = catalyst.initialize(context);
  // cronDetails contains cron metadata
  context.close();
};

// --- AppSail ---
// In an AppSail app (Express), same pattern as Advanced I/O:
const catalystApp = catalyst.initialize(req);

// --- Admin Scope vs User Scope ---
// Scopes apply to Data Store, File Store, and ZCQL operations.
// Admin scope bypasses row-level permissions:
const adminApp = catalyst.initialize(req, { scope: 'admin' });

// User scope restricts to the authenticated user's rows:
const userApp = catalyst.initialize(req, { scope: 'user' });
```

---

## Data Store

```js
// Get a table reference (by name or table ID)
const table = catalystApp.datastore().table('Shipments');
// Or by ID: catalystApp.datastore().table(23aborTableId);

// --- Insert a single row ---
const row = await table.insertRow({
  Name: 'Alice',
  Email: 'alice@example.com'
});
// row.ROWID is the auto-generated unique identifier

// --- Insert multiple rows ---
const rows = await table.insertRows([
  { Name: 'Bob', Email: 'bob@example.com' },
  { Name: 'Carol', Email: 'carol@example.com' }
]);

// --- Get a single row by ROWID ---
const singleRow = await table.getRow('123456000000012345');

// --- Get paginated rows ---
// Returns up to 200 rows per page by default.
const result = await table.getPagedRows({
  nextToken: 'token_from_previous_call', // optional
  maxRows: 100                           // optional, default 200
});
const data = result.data;
const hasMore = result.more_records;
const nextToken = result.next_token;

// --- Update a row (ROWID is required) ---
const updated = await table.updateRow({
  ROWID: '123456000000012345',
  Name: 'Alice Updated'
});

// --- Delete a row ---
await table.deleteRow('123456000000012345');
```

---

## ZCQL

```js
const zcql = catalystApp.zcql();

// --- Execute a ZCQL query ---
// Supports SELECT, INSERT, UPDATE, DELETE, and JOIN queries.
const rows = await zcql.executeZCQLQuery('SELECT * FROM Shipments WHERE Status = \'Active\'');

// INSERT via ZCQL
await zcql.executeZCQLQuery(
  'INSERT INTO Shipments (Name, Status) VALUES (\'Package A\', \'Pending\')'
);

// UPDATE via ZCQL
await zcql.executeZCQLQuery(
  'UPDATE Shipments SET Status = \'Shipped\' WHERE ROWID = \'123456000000012345\''
);

// DELETE via ZCQL
await zcql.executeZCQLQuery(
  'DELETE FROM Shipments WHERE ROWID = \'123456000000012345\''
);

// --- Execute an OLAP query ---
// OLAP queries aggregate data across large datasets.
const olapResult = await zcql.executeOLAPQuery(
  'SELECT Status, COUNT(ROWID) AS cnt FROM Shipments GROUP BY Status'
);
```

---

## Cache

```js
const cache = catalystApp.cache();

// --- Get a segment instance ---
const segment = cache.segment(segmentId);

// --- Put a key-value pair ---
// Default expiry is 48 hours. Expiry is in milliseconds.
await segment.put('sessionToken', 'abc123xyz');

// With custom expiry (e.g., 1 hour = 3600000 ms)
await segment.put('tempData', 'value', 3600000);

// --- Get a cached value ---
const value = await segment.getValue('sessionToken');

// Get full cache item details (key, value, expiry info)
const item = await segment.get('sessionToken');

// --- Update a cached value ---
await segment.update('sessionToken', 'newValue456');

// --- Delete a cached key ---
await segment.delete('sessionToken');
```

---

## File Store

```js
const filestore = catalystApp.filestore();
const folder = filestore.folder(folderId);

// --- Upload a file (max 100 MB) ---
const fs = require('fs');
const fileStream = fs.createReadStream('/path/to/document.pdf');
const uploadedFile = await folder.uploadFile({
  code: fileStream,
  name: 'document.pdf'
});
// uploadedFile.id contains the file ID

// --- Download a file ---
const downloadStream = await folder.downloadFile(fileId);
// Pipe to response or write to disk:
downloadStream.pipe(res);

// --- Delete a file ---
await folder.deleteFile(fileId);

// --- Get file details ---
const fileDetails = await folder.getFileDetails(fileId);
```

---

## Authentication / User Management

```js
// --- userManagement() is the primary accessor in newer SDK versions ---
const userManagement = catalystApp.userManagement();

// --- Get current user (user whose scope is active) ---
const currentUser = await userManagement.getCurrentUser();

// --- Register a new user ---
const newUser = await userManagement.registerUser({
  first_name: 'John',
  last_name: 'Doe',
  email_id: 'john@example.com',
  role_id: '123456000000007003' // role ID from your project
});

// --- Get user details by user ID ---
const userDetails = await userManagement.getUserDetails(userId);

// --- Delete a user ---
await userManagement.deleteUser(userId);

// --- authentication() accessor for org-level operations ---
const auth = catalystApp.authentication();

// Get all org IDs associated with the project
const orgIds = await auth.getAllOrgIds();

// Add a user to an org
await auth.addUserToOrg(orgId, {
  email_id: 'user@example.com',
  role_id: roleId
});

// Get all users in an org
const orgUsers = await auth.getAllUsersInOrg(orgId);

// Enable a user
await auth.enableUser(userId);

// Disable a user
await auth.disableUser(userId);

// Reset a user's password
await auth.resetPassword(userId);

// Generate a server-side token
const token = await auth.generateServerToken();
```

---

## Email

```js
const mail = catalystApp.mail();

// --- Send an email ---
await mail.sendMail({
  from_email: 'noreply@yourdomain.com',
  to_email: ['recipient@example.com'],
  cc: ['cc@example.com'],           // optional
  bcc: ['bcc@example.com'],         // optional
  reply_to: ['replyto@example.com'],// optional
  subject: 'Order Confirmation',
  content: '<h1>Thank you for your order!</h1><p>Your order #1234 is confirmed.</p>',
  attachments: [                     // optional
    {
      name: 'invoice.pdf',
      content: fs.createReadStream('/path/to/invoice.pdf')
    }
  ]
});
```

---

## Search

```js
const search = catalystApp.search();

// --- Execute a search query ---
// Searches indexed columns across specified tables.
const results = await search.executeSearchQuery({
  search: 'shipping delayed',
  search_table_columns: {
    Shipments: ['TrackingNotes', 'Description'],
    Orders: ['CustomerName', 'OrderNotes']
  }
});
```

---

## Connections

```js
const connection = catalystApp.connection();

// --- Get connection credentials ---
// Retrieves OAuth tokens for a configured Catalyst Connection.
const credentials = await connection.getConnectorCredentials(connectorName);
// credentials.access_token is the OAuth access token
```

---

## Circuits

```js
const circuit = catalystApp.circuit();

// --- Execute a circuit ---
const result = await circuit.execute(circuitId, {
  key1: 'value1',
  key2: 'value2'
});
// result contains the circuit execution output
```

---

## NoSQL

```js
const nosql = catalystApp.nosql();
const { NoSQLItem } = require('zcatalyst-sdk-node/lib/no-sql');

// --- Get a table reference ---
const table = nosql.table('SessionStore');

// --- Insert items ---
const item = new NoSQLItem();
item.put('userId', 'string', 'user_001');
item.put('loginTime', 'number', Date.now());
item.put('active', 'boolean', true);

await table.insertItems([item]);

// --- Fetch items by partition key ---
const fetched = await table.fetchItems({
  partitionKey: { name: 'userId', value: 'user_001' }
});

// --- Query table (using partition key and sort key conditions) ---
const queryResult = await table.queryTable({
  partitionKey: { name: 'userId', value: 'user_001' },
  sortKey: {
    name: 'loginTime',
    operator: 'GREATERTHAN',
    value: 1700000000000
  },
  consistent_read: false,
  limit: 50,
  ascending: true
});
// Supported operators: EQUALS, BETWEEN, GREATERTHAN, LESSERTHAN,
//   GREATERTHANOREQUALTO, LESSERTHANOREQUALTO

// --- Query a secondary index ---
const indexResult = await table.queryIndex('LoginTimeIndex', {
  partitionKey: { name: 'active', value: true },
  sortKey: {
    name: 'loginTime',
    operator: 'BETWEEN',
    value: [1700000000000, 1710000000000]
  },
  limit: 100,
  ascending: false
});

// --- Update items ---
const updateItem = new NoSQLItem();
updateItem.put('userId', 'string', 'user_001');
updateItem.put('loginTime', 'number', 1700000000001);
updateItem.put('active', 'boolean', false);

await table.updateItems([updateItem]);

// --- Delete items ---
await table.deleteItems([
  { partitionKey: 'user_001', sortKey: 1700000000001 }
]);
```

---

## Stratus Object Storage

### Bucket Operations

> ⚠️ **Stratus bucket names are globally unique** across ALL Catalyst projects and orgs. Generic names like `my-files` will likely already be taken. Use a project-specific suffix: `{app-name}-{project-id-prefix}` (e.g., `docvault-files-70699`). A `DUPLICATE_ENTRY` error on creation does NOT mean the bucket exists in your project — it may belong to another project entirely and will be inaccessible to you.

```js
const stratus = catalystApp.stratus();

// --- Get a bucket instance ---
const bucket = stratus.bucket('myapp-files-70699'); // Use project-specific name

// --- List all buckets ---
const buckets = await stratus.listBuckets();

// --- Get bucket details ---
const details = await bucket.getDetails();

// --- Get bucket CORS configuration ---
const cors = await bucket.getCors();
```

### Listing Objects

```js
// --- List paged objects ---
const pagedResult = await bucket.listPagedObjects({
  prefix: 'uploads/',       // optional: filter by prefix
  maxKeys: 100,             // optional: max objects per page
  continuationToken: token  // optional: for pagination
});

// --- List iterable objects (async iterator) ---
for await (const obj of bucket.listIterableObjects({ prefix: 'uploads/' })) {
  console.log(obj.key, obj.size);
}
```

### Downloading Objects

```js
// --- Check object availability (HEAD) ---
const head = await bucket.headObject('uploads/report.pdf');
// head includes content_length, content_type, last_modified, etc.

// With options
const headVersioned = await bucket.headObject('uploads/report.pdf', {
  versionId: 'v123',
  throwErr: false // returns null instead of throwing if not found
});

// --- Download an object (GET) ---
const stream = await bucket.getObject('uploads/report.pdf');
stream.pipe(fs.createWriteStream('/tmp/report.pdf'));

// With range header (partial download)
const partialStream = await bucket.getObject('uploads/report.pdf', {
  range: 'bytes=0-1023'
});

// --- TransferManager: range-based download ---
const transferManager = bucket.transferManager();
const iterableStream = await transferManager.getIterableObject('uploads/large-file.zip', {
  partSize: 10 * 1024 * 1024 // 10 MB per part
});
const writeStream = fs.createWriteStream('/tmp/large-file.zip');
for await (const chunk of iterableStream) {
  writeStream.write(chunk);
}
writeStream.end();
```

### Pre-Signed URLs

```js
// --- Generate a pre-signed URL for GET (download) ---
const getUrl = await bucket.generatePreSignedUrl('uploads/report.pdf', {
  expiresIn: 3600,         // seconds until expiry
  activationDate: new Date(), // optional: when the URL becomes active
  versionId: 'v123'        // optional: specific version
});

// --- Generate a pre-signed URL for PUT (upload) ---
const putUrl = await bucket.generatePreSignedUrl('uploads/new-file.pdf', {
  expiresIn: 3600,
  method: 'PUT'
});
```

### Uploading Objects

```js
// --- putObject with a stream ---
const uploadStream = fs.createReadStream('/path/to/file.pdf');
await bucket.putObject('uploads/file.pdf', uploadStream);

// --- putObject with a string ---
await bucket.putObject('configs/settings.json', JSON.stringify({ theme: 'dark' }));

// --- putObject with options ---
await bucket.putObject('uploads/file.pdf', uploadStream, {
  overwrite: true,                 // overwrite if exists (default behavior without versioning)
  ttl: 86400,                     // time-to-live in seconds (auto-delete after 24h)
  metaData: {                     // custom metadata
    uploadedBy: 'automation',
    category: 'reports'
  },
  extractUpload: true              // extract ZIP contents and upload each file separately
});

// --- Multipart upload (recommended for files >= 100 MB) ---
const multipart = bucket.multipart();

// Step 1: Initiate
const upload = await multipart.initiateMultipartUpload('uploads/huge-video.mp4');
const uploadId = upload.uploadId;

// Step 2: Upload parts (1 to 1000 parts allowed, min 5 MB per part except last)
const part1 = await multipart.uploadPart('uploads/huge-video.mp4', uploadId, {
  partNumber: 1,
  body: fs.createReadStream('/path/to/part1')
});
const part2 = await multipart.uploadPart('uploads/huge-video.mp4', uploadId, {
  partNumber: 2,
  body: fs.createReadStream('/path/to/part2')
});

// Step 3: Complete multipart upload
await multipart.completeMultipartUpload('uploads/huge-video.mp4', uploadId, [
  { partNumber: 1, eTag: part1.eTag },
  { partNumber: 2, eTag: part2.eTag }
]);

// --- TransferManager: automatic multipart upload ---
const tm = bucket.transferManager();
await tm.putObjectAsParts('uploads/huge-video.mp4', fs.createReadStream('/path/to/video.mp4'), {
  partSize: 10 * 1024 * 1024 // 10 MB per part
});
```

### Object Management

```js
// --- Unzip an object (extract in-place) ---
await bucket.unzipObject('uploads/archive.zip', {
  targetPrefix: 'extracted/'   // optional: extract to a specific prefix
});

// --- Rename / move an object ---
await bucket.renameObject('uploads/old-name.pdf', 'uploads/new-name.pdf');

// --- Delete a single object ---
await bucket.deleteObject('uploads/file.pdf');

// --- Delete multiple objects ---
await bucket.deleteObjects([
  { key: 'uploads/file1.pdf' },
  { key: 'uploads/file2.pdf', versionId: 'v456' }
]);

// --- Truncate a bucket (delete all objects) ---
await bucket.truncate();

// --- Delete a path (all objects under a prefix) ---
await bucket.deletePath('uploads/temp/');
```

### Object Versions

```js
// --- List iterable versions (async iterator) ---
for await (const version of bucket.listIterableVersions({ prefix: 'uploads/report.pdf' })) {
  console.log(version.versionId, version.lastModified, version.isLatest);
}
```

---

## Bulk Data Store Operations

```js
const datastore = catalystApp.datastore();
const table = datastore.table('Shipments');

// --- Bulk Read ---
// Creates a bulk read job that generates a CSV file with the results.
const bulkReadJob = table.bulkJob('read');
const readResult = await bulkReadJob.createJob({
  table_identifier: 'Shipments',
  criteria: {                  // optional: filter rows
    group_operator: 'AND',
    group: [
      {
        column: 'Status',
        comparator: 'equal',
        value: 'Active'
      }
    ]
  }
});
// Poll readResult.job_id for status; download CSV when complete.
const jobStatus = await bulkReadJob.getJobStatus(readResult.job_id);

// --- Bulk Write ---
// Upload CSV data first to Stratus, then reference it in the write job.
const bulkWriteJob = table.bulkJob('write');
const writeResult = await bulkWriteJob.createJob({
  table_identifier: 'Shipments',
  file_details: {
    bucketName: 'my-bucket',
    objectKey: 'imports/shipments.csv',
    versionID: 'v1'         // optional: if versioning is enabled
  }
});

// --- Bulk Delete (max 200 rows per call) ---
const rowIds = [
  '123456000000012345',
  '123456000000012346',
  '123456000000012347'
];
await table.deleteRows(rowIds);
```

---

## Push Notifications

```js
const pushNotification = catalystApp.pushNotification();

// --- Send web push notification (up to 50 users per call) ---
const webNotif = pushNotification.web();
await webNotif.sendNotification({
  message: 'Your order has been shipped!',
  recipients: [userId1, userId2]      // user IDs or email addresses
});

// --- Send mobile push notification ---
const mobileNotif = pushNotification.mobile(appId);

// Android notification
await mobileNotif.sendAndroidNotification({
  message: 'New update available',
  recipients: [userId],
  additional_data: {                 // optional: custom payload
    orderId: '12345'
  }
});

// iOS notification
await mobileNotif.sendIOSNotification({
  message: 'New update available',
  recipients: [userId],
  badge_count: 1,                    // optional
  additional_data: {
    orderId: '12345'
  }
});
```

---

## Zia Services

### OCR (Optical Character Recognition)

```js
const zia = catalystApp.zia();

// --- Extract text from an image or document ---
const ocrResult = await zia.extractOpticalCharacters({
  image_url: 'https://example.com/receipt.jpg'
  // OR pass a file stream:
  // image: fs.createReadStream('/path/to/receipt.jpg')
});
```

### AutoML

```js
// --- Execute a prediction using a trained AutoML model ---
// Supports Binary Classification, Multi-Class Classification, and Regression.
const prediction = await zia.executeAutoML(modelId, {
  feature1: 'value1',
  feature2: 42,
  feature3: true
});
```

### Sentiment Analysis

```js
const sentiment = await zia.getSentimentAnalysis([
  'The product quality is amazing!',
  'Delivery was too slow and the packaging was damaged.'
]);
// Each result has: sentiment (positive/negative/neutral), confidence
```

### Named Entity Recognition (NER)

```js
const entities = await zia.getNamedEntityRecognition([
  'John Doe from Acme Corp signed the contract on January 15, 2025.'
]);
// Extracts entities like person names, organizations, dates, etc.
```

### Keyword Extraction

```js
const keywords = await zia.getKeywordExtraction([
  'Machine learning models improve predictive accuracy in healthcare diagnostics.'
]);
// Returns keywords and keyphrases
```

### All Text Analytics (combined)

```js
const allAnalytics = await zia.getAllTextAnalytics([
  'The quarterly revenue exceeded expectations, driven by strong sales in APAC.'
]);
// Returns sentiment, NER, and keyword extraction in one call
```

### Image Moderation

```js
const moderation = await zia.moderateImage({
  image_url: 'https://example.com/photo.jpg'
  // OR: image: fs.createReadStream('/path/to/photo.jpg')
});
// Returns confidence scores for nudity, violence, etc.
```

### Face Detection

```js
const faces = await zia.detectFaces({
  image_url: 'https://example.com/group-photo.jpg'
});
// Returns detected faces with age, gender, emotion, bounding box
```

### Object Recognition

```js
const objects = await zia.recognizeObjects({
  image_url: 'https://example.com/scene.jpg'
});
// Returns identified objects with confidence scores
```

### Barcode Scanning

```js
const barcodes = await zia.scanBarcode({
  image_url: 'https://example.com/barcode.jpg'
});
// Supports Codabar, EAN-13, ITF, UPC-A, QR Code, and more
```

---

## SmartBrowz

```js
const smartBrowz = catalystApp.SmartBrowz();

// --- Browser Grid ---
const grid = smartBrowz.browserGrid();

// Get all browser grids
const allGrids = await grid.getAllGrids();

// Get a specific grid by ID
const specificGrid = await grid.getGrid(gridId);

// Get a specific node in a grid
const node = await grid.getNode(gridId, nodeId);

// Stop a browser grid
await grid.stopGrid(gridId);

// --- Generate PDF ---
const pdfBuffer = await smartBrowz.generatePDF({
  url: 'https://example.com/report',          // Generate from URL
  // OR: html: '<h1>Hello</h1>',              // Generate from HTML
  // OR: template_id: 'tpl_123',              // Generate from template
  output: {
    format: 'A4',
    landscape: false,
    print_background: true
  },
  password: 'secret123'                        // optional: password-protect PDF
});

// --- Generate Screenshot ---
const screenshotBuffer = await smartBrowz.generateScreenshot({
  url: 'https://example.com/dashboard',
  output: {
    format: 'png',       // 'png' or 'webp'
    full_page: true,
    quality: 90
  }
});

// --- Dataverse (web scraping/extraction) ---
const extractedData = await smartBrowz.dataverse({
  url: 'https://example.com/products',
  extraction_rules: {
    title: { selector: 'h1.product-title', type: 'text' },
    price: { selector: '.price', type: 'text' }
  }
});
```

---

## Job Scheduling

### Jobs

```js
const jobScheduling = catalystApp.jobScheduling();

// --- Submit a job targeting a Function ---
const jobResult = await jobScheduling.submitJob({
  job_name: 'process-orders',
  jobpool_name: 'OrderPool',
  target_type: 'Function',
  target_name: 'ProcessOrderFunction',
  job_config: {                     // optional: custom params passed to the target
    batchSize: 50,
    region: 'US'
  }
});

// --- Submit a job targeting a Circuit ---
await jobScheduling.submitJob({
  job_name: 'etl-pipeline',
  jobpool_name: 'DataPool',
  target_type: 'Circuit',
  target_name: 'ETLCircuit'
});

// --- Submit a job targeting a Webhook ---
await jobScheduling.submitJob({
  job_name: 'notify-webhook',
  jobpool_name: 'NotifyPool',
  target_type: 'Webhook',
  target_name: 'SlackWebhook'
});

// --- Submit a job targeting an AppSail service ---
await jobScheduling.submitJob({
  job_name: 'cleanup-task',
  jobpool_name: 'MaintenancePool',
  target_type: 'AppSail',
  target_name: 'CleanupService'
});

// --- Delete a job ---
await jobScheduling.deleteJob(jobId);
```

### Crons

```js
const cron = jobScheduling.cron();

// --- Create a One-Time cron ---
const oneTimeCron = await cron.createCron({
  cron_name: 'one-time-report',
  description: 'Generate end-of-month report',
  jobpool_name: 'ReportPool',
  cron_type: 'OneTime',
  schedule: {
    time: '2025-12-31T23:59:00Z'
  },
  job_config: { reportType: 'monthly' }
});

// --- Create a Periodic/Every cron (recurring, < 24h interval) ---
const periodicCron = await cron.createCron({
  cron_name: 'health-check',
  description: 'Check system health every 15 minutes',
  jobpool_name: 'MonitorPool',
  cron_type: 'Periodic',
  schedule: {
    every: 15,
    unit: 'minutes'          // 'minutes' or 'hours'
  }
});

// --- Create a Daily/Calendar cron ---
const dailyCron = await cron.createCron({
  cron_name: 'daily-digest',
  description: 'Send daily email digest at 9 AM',
  jobpool_name: 'EmailPool',
  cron_type: 'Calendar',
  schedule: {
    time: '09:00',
    timezone: 'Asia/Kolkata',
    days_of_week: ['MON', 'TUE', 'WED', 'THU', 'FRI']
  }
});

// --- Create a Monthly cron ---
const monthlyCron = await cron.createCron({
  cron_name: 'monthly-invoice',
  description: 'Generate invoices on the 1st of each month',
  jobpool_name: 'BillingPool',
  cron_type: 'Calendar',
  schedule: {
    time: '00:00',
    timezone: 'UTC',
    days_of_month: [1]
  }
});

// --- Create a Yearly cron ---
const yearlyCron = await cron.createCron({
  cron_name: 'annual-cleanup',
  description: 'Yearly data archival',
  jobpool_name: 'ArchivePool',
  cron_type: 'Calendar',
  schedule: {
    time: '02:00',
    timezone: 'UTC',
    months: ['JAN'],
    days_of_month: [1]
  }
});

// --- Create a cron using cron expressions ---
const exprCron = await cron.createCron({
  cron_name: 'custom-schedule',
  jobpool_name: 'CustomPool',
  cron_type: 'CronExpression',
  schedule: {
    cron_expression: '0 */6 * * *'  // every 6 hours
  }
});

// --- Cron management ---
const cronDetails = await cron.getCron(cronId);
await cron.updateCron(cronId, { description: 'Updated description' });
await cron.pauseCron(cronId);
await cron.resumeCron(cronId);
await cron.runCron(cronId);          // manually trigger a cron immediately
await cron.deleteCron(cronId);
```

---

## Pipelines

```js
const pipeline = catalystApp.pipeline();

// --- Get pipeline details ---
const details = await pipeline.getPipelineDetails(pipelineId);

// --- Execute a pipeline ---
const result = await pipeline.executePipeline(pipelineId, {
  inputParam1: 'value1',
  inputParam2: 'value2'
});
```

---

## Connectors

```js
const connector = catalystApp.connector();

// --- Get a connector token ---
// Retrieves OAuth credentials for a configured Catalyst Connector.
const tokenDetails = await connector.getConnectorToken(connectorName);
// tokenDetails.access_token contains the usable OAuth access token
```
