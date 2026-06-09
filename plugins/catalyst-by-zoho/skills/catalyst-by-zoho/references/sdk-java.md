# Java SDK Reference

> **Supported Java versions:** 8, 11, 17
> **External docs:** https://docs.catalyst.zoho.com/en/sdk/java/v1/overview/

## Maven Dependency

Repository: `https://maven.zohodl.com`

```xml
<repository>
  <id>zoho-dl</id>
  <url>https://maven.zohodl.com</url>
</repository>

<dependency>
  <groupId>com.zc</groupId>
  <artifactId>zcatalyst-sdk</artifactId>
  <version>1.15.0</version>
</dependency>
```

---

## Initialization

```java
// Default project initialization (uses request context)
ZCProject.initProject();

// Admin scope initialization
ZCProject adminProject = ZCProject.initProject("admin", ZCUserScope.ADMIN);

// User scope initialization
ZCProject userProject = ZCProject.initProject("user", ZCUserScope.USER);
```

---

## Data Store

### Core Classes

- **ZCObject** - Main data store access
- **ZCTable** - Represents a table
- **ZCRowObject** - Represents a row/record

### Insert Single Row

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

ZCRowObject row = ZCRowObject.getInstance();
row.set("column_name", "value");
row.set("numeric_column", 123);

ZCRowObject insertedRow = table.insertRow(row);
long rowId = insertedRow.getRowId();
```

### Insert Multiple Rows

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

List<ZCRowObject> rows = new ArrayList<>();

ZCRowObject row1 = ZCRowObject.getInstance();
row1.set("Name", "Alice");
rows.add(row1);

ZCRowObject row2 = ZCRowObject.getInstance();
row2.set("Name", "Bob");
rows.add(row2);

List<ZCRowObject> insertedRows = table.insertRows(rows);
```

### Get Single Row

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

ZCRowObject row = table.getRow(rowId);
String value = row.get("column_name").toString();
```

### Get All Rows (Paginated)

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

// Basic fetch
List<ZCRowObject> rows = table.getRows();

// Paginated fetch
ZCRowPagedResponse pagedResponse = table.getPagedRows();
List<ZCRowObject> currentPage = pagedResponse.getCurrentPageData();
boolean hasNext = pagedResponse.hasNextPage();
ZCRowPagedResponse nextPage = pagedResponse.getNextPage();
```

### Update Row

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

ZCRowObject row = ZCRowObject.getInstance();
row.set("ROWID", rowId);
row.set("column_name", "updated_value");

ZCRowObject updatedRow = table.updateRow(row);
```

### Delete Row

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

table.deleteRow(rowId);
```

---

## ZCQL

```java
// Basic query
ZCQL zcql = ZCQL.getInstance();
List<ZCRowObject> results = zcql.executeQuery("SELECT * FROM TableName WHERE column = 'value'");

// V2 query execution
List<ZCRowObject> results = zcql.executeQuery("SELECT * FROM TableName", true);

// OLAP query (for analytical/aggregation queries)
List<ZCRowObject> results = zcql.executeQuery("SELECT COUNT(*) FROM TableName", true, true);
```

---

## Cache

### Core Classes

- **ZCCache** - Cache access point
- **ZCSegment** - Cache segment
- **ZCCacheObject** - Individual cache entry

### Put (with Expiry)

```java
ZCCache cache = ZCCache.getInstance();
ZCSegment segment = cache.getSegment(segmentId);

// Put with expiry (in milliseconds)
ZCCacheObject cacheObject = segment.put("cacheKey", "cacheValue", 3600000L);
```

### Get

```java
ZCCache cache = ZCCache.getInstance();
ZCSegment segment = cache.getSegment(segmentId);

ZCCacheObject cacheObject = segment.get("cacheKey");
String value = cacheObject.getValue();
```

### Update

```java
ZCCache cache = ZCCache.getInstance();
ZCSegment segment = cache.getSegment(segmentId);

ZCCacheObject updated = segment.update("cacheKey", "newValue", 7200000L);
```

### Delete

```java
ZCCache cache = ZCCache.getInstance();
ZCSegment segment = cache.getSegment(segmentId);

segment.delete("cacheKey");
```

---

## File Store

### Core Classes

- **ZCFile** - File store access
- **ZCFolder** - Represents a folder

### Upload File

```java
ZCFile fileStore = ZCFile.getInstance();
ZCFolder folder = fileStore.getFolder(folderId);

File file = new File("/path/to/file.pdf");
ZCFolder uploadedFile = folder.uploadFile(file);
long fileId = uploadedFile.getFileId();
```

### Download File

```java
ZCFile fileStore = ZCFile.getInstance();
ZCFolder folder = fileStore.getFolder(folderId);

InputStream inputStream = folder.downloadFile(fileId);
```

### Delete File

```java
ZCFile fileStore = ZCFile.getInstance();
ZCFolder folder = fileStore.getFolder(folderId);

folder.deleteFile(fileId);
```

### Get Folder Details

```java
ZCFile fileStore = ZCFile.getInstance();
ZCFolder folder = fileStore.getFolder(folderId);

ZCFolder folderDetails = folder.getFolderDetails();
```

---

## Authentication

### Core Classes

- **ZCUser** - User management
- **ZCSignUpData** - User registration data
- **ZCMailTemplateDetails** - Email template for registration

### Register User

```java
ZCUser userService = ZCUser.getInstance();

ZCSignUpData signUpData = ZCSignUpData.getInstance();
signUpData.setEmailId("user@example.com");
signUpData.setFirstName("John");
signUpData.setLastName("Doe");
signUpData.setRoleId("role_id");

ZCMailTemplateDetails mailTemplate = ZCMailTemplateDetails.getInstance();
mailTemplate.setSubject("Welcome to the App");
mailTemplate.setMessage("Click the link to verify your account.");

signUpData.setMailTemplateDetails(mailTemplate);

userService.registerUser(signUpData);
```

### Get User Details

```java
ZCUser userService = ZCUser.getInstance();
ZCUser userDetails = userService.getUserDetails(userId);
String email = userDetails.getEmailId();
String firstName = userDetails.getFirstName();
```

### Delete User

```java
ZCUser userService = ZCUser.getInstance();
userService.deleteUser(userId);
```

---

## Email

### Core Classes

- **ZCMail** - Mail service
- **ZCMailContent** - Mail content/configuration

### Send Mail

```java
ZCMail mail = ZCMail.getInstance();

ZCMailContent mailContent = ZCMailContent.getInstance();
mailContent.setFromEmail("sender@yourdomain.com");
mailContent.setToEmail("recipient@example.com");
mailContent.setSubject("Subject Line");
mailContent.setContent("<h1>Hello</h1><p>This is the email body.</p>");

// Optional settings
mailContent.setCcEmail("cc@example.com");
mailContent.setBccEmail("bcc@example.com");
mailContent.setReplyTo("reply@example.com");
mailContent.setHtml(true);

mail.sendMail(mailContent);
```

---

## Search

### Core Classes

- **ZCSearch** - Search service
- **ZCSearchDetails** - Search query configuration

### Execute Search Query

```java
ZCSearch search = ZCSearch.getInstance();

ZCSearchDetails searchDetails = ZCSearchDetails.getInstance();
searchDetails.setSearchQuery("search term");
searchDetails.setSearchTableColumns("TableName.column1,TableName.column2");

List<ZCRowObject> results = search.executeSearchQuery(searchDetails);
```

---

## Connections

### Get Access Token

```java
ZCConnection connection = ZCConnection.getInstance();
String accessToken = connection.getConnector("connector_name").getAccessToken();
```

---

## Circuits

### Execute Circuit

```java
ZCCircuit circuit = ZCCircuit.getInstance();

Map<String, Object> inputData = new HashMap<>();
inputData.put("param1", "value1");
inputData.put("param2", 42);

Object result = circuit.execute(circuitId, inputData);
```

---

## NoSQL

### Core Classes

- **ZCNoSQL** - NoSQL access point
- **ZCNoSQLTable** - Represents a NoSQL table
- **ZCNoSQLItem** - Represents a NoSQL item/document

### Get Table Metadata

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTableMetadata("TableName");
```

### Insert Items

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTable("TableName");

ZCNoSQLItem item = ZCNoSQLItem.getInstance();
item.put("partitionKey", "pk_value");
item.put("sortKey", "sk_value");
item.put("attribute1", "value1");

table.insertItems(Collections.singletonList(item));
```

### Fetch Items

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTable("TableName");

List<ZCNoSQLItem> items = table.fetchItems();
```

### Query Table

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTable("TableName");

Map<String, Object> queryParams = new HashMap<>();
queryParams.put("partitionKey", "pk_value");

List<ZCNoSQLItem> results = table.queryTable(queryParams);
```

### Query Index

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTable("TableName");

Map<String, Object> queryParams = new HashMap<>();
queryParams.put("indexName", "myIndex");
queryParams.put("partitionKey", "pk_value");

List<ZCNoSQLItem> results = table.queryIndex(queryParams);
```

### Update Items

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTable("TableName");

ZCNoSQLItem item = ZCNoSQLItem.getInstance();
item.put("partitionKey", "pk_value");
item.put("sortKey", "sk_value");
item.put("attribute1", "updated_value");

table.updateItems(Collections.singletonList(item));
```

### Delete Items

```java
ZCNoSQL nosql = ZCNoSQL.getInstance();
ZCNoSQLTable table = nosql.getTable("TableName");

ZCNoSQLItem item = ZCNoSQLItem.getInstance();
item.put("partitionKey", "pk_value");
item.put("sortKey", "sk_value");

table.deleteItems(Collections.singletonList(item));
```

---

## Stratus

### Core Classes

- **ZCStratus** - Stratus (object storage) access point
- **ZCStratusBucket** - Represents a storage bucket

### Bucket Operations

```java
ZCStratus stratus = ZCStratus.getInstance();

// Check if bucket exists
boolean exists = stratus.checkBucket("bucket-name");

// List all buckets
List<ZCStratusBucket> buckets = stratus.listBuckets();

// Get bucket details
ZCStratusBucket bucket = stratus.getDetails("bucket-name");

// Get CORS configuration
Object corsConfig = stratus.getCORS("bucket-name");
```

### Object Operations

```java
ZCStratus stratus = ZCStratus.getInstance();

// List objects in bucket
List<Object> objects = stratus.listObjects("bucket-name");

// Check if object exists
boolean objExists = stratus.checkObject("bucket-name", "object-key");

// Upload object
File file = new File("/path/to/file.txt");
stratus.uploadObject("bucket-name", "object-key", file);

// Download object
InputStream stream = stratus.downloadObject("bucket-name", "object-key");

// Copy object
stratus.copyObject("source-bucket", "source-key", "dest-bucket", "dest-key");

// Rename object
stratus.renameObject("bucket-name", "old-key", "new-key");

// Delete objects
List<String> keys = Arrays.asList("key1", "key2");
stratus.deleteObjects("bucket-name", keys);

// Extract zipped object
stratus.extractZippedObject("bucket-name", "archive.zip", "destination-prefix/");

// List object versions
List<Object> versions = stratus.listObjectVersions("bucket-name", "object-key");

// Get object details/metadata
Object details = stratus.getObjectDetails("bucket-name", "object-key");

// Put object metadata
Map<String, String> metadata = new HashMap<>();
metadata.put("custom-key", "custom-value");
stratus.putObjectMeta("bucket-name", "object-key", metadata);
```

---

## Bulk Data Store

### Bulk Read

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

// Initiate bulk read job
long jobId = table.bulkRead();
```

### Bulk Write

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

// Bulk write from CSV file
File csvFile = new File("/path/to/data.csv");
long jobId = table.bulkWrite(csvFile);
```

### Bulk Delete Rows

```java
ZCObject object = ZCObject.getInstance();
ZCTable table = object.getTable("TableName");

// Delete multiple rows (max 200 per call)
List<Long> rowIds = Arrays.asList(1001L, 1002L, 1003L);
table.bulkDeleteRows(rowIds);
```

---

## Push Notifications

### Core Class

- **ZCPushNotification** - Push notification service

### Send Web Notification

```java
ZCPushNotification pushNotification = ZCPushNotification.getInstance();

Map<String, Object> notificationData = new HashMap<>();
notificationData.put("message", "You have a new update!");
notificationData.put("recipients", Arrays.asList("user1@example.com"));

pushNotification.sendNotification(notificationData);
```

### Send Mobile Notification

```java
ZCPushNotification pushNotification = ZCPushNotification.getInstance();

Map<String, Object> mobileNotification = new HashMap<>();
mobileNotification.put("message", "New mobile notification");
mobileNotification.put("recipients", Arrays.asList("user1@example.com"));
mobileNotification.put("additional_data", Map.of("key", "value"));

pushNotification.sendMobileNotification(mobileNotification);
```

---

## Zia Services

### Core Class

- **ZCZIA** - Zoho Intelligent Assistant services

### OCR (Optical Character Recognition)

```java
ZCZIA zia = ZCZIA.getInstance();

File imageFile = new File("/path/to/document.png");
Object ocrResult = zia.extractOpticalCharacters(imageFile);
```

### AutoML

```java
ZCZIA zia = ZCZIA.getInstance();

Map<String, Object> inputData = new HashMap<>();
inputData.put("feature1", "value1");
inputData.put("feature2", 42);

Object prediction = zia.executeAutoML("model_id", inputData);
```

### Sentiment Analysis

```java
ZCZIA zia = ZCZIA.getInstance();

List<String> documents = Arrays.asList(
    "This product is amazing!",
    "Terrible experience, would not recommend."
);

Object sentimentResult = zia.getSentimentAnalysis(documents);
```

### Named Entity Recognition

```java
ZCZIA zia = ZCZIA.getInstance();

List<String> documents = Arrays.asList("John Doe works at Zoho in Chennai.");
Object nerResult = zia.getNamedEntityRecognition(documents);
```

### Keyword Extraction

```java
ZCZIA zia = ZCZIA.getInstance();

List<String> documents = Arrays.asList("Cloud computing and artificial intelligence are transforming businesses.");
Object keywords = zia.getKeywordExtraction(documents);
```

### All Text Analytics (Combined)

```java
ZCZIA zia = ZCZIA.getInstance();

List<String> documents = Arrays.asList("Zoho Catalyst is a serverless platform.");
Object analytics = zia.getAllTextAnalytics(documents);
```

### Image Moderation

```java
ZCZIA zia = ZCZIA.getInstance();

File imageFile = new File("/path/to/image.jpg");
Object moderationResult = zia.moderateImage(imageFile);
```

### Face Detection

```java
ZCZIA zia = ZCZIA.getInstance();

File imageFile = new File("/path/to/photo.jpg");
Object faceResult = zia.detectFaces(imageFile);
```

### Barcode Scanning

```java
ZCZIA zia = ZCZIA.getInstance();

File barcodeImage = new File("/path/to/barcode.png");
Object barcodeResult = zia.scanBarcode(barcodeImage);
```

---

## SmartBrowz

### Core Class

- **ZCSmartBrowz** - Browser automation / headless browser service

### Browser Grid

```java
ZCSmartBrowz smartBrowz = ZCSmartBrowz.getInstance();

// Get a new browser grid instance
Object gridInstance = smartBrowz.getBrowserGridInstance();

// Get all browser grids
List<Object> grids = smartBrowz.getAllBrowserGrids();

// Get specific browser grid
Object grid = smartBrowz.getBrowserGrid(gridId);

// Stop a browser grid
smartBrowz.stopBrowserGrid(gridId);
```

### PDF Generation

```java
ZCSmartBrowz smartBrowz = ZCSmartBrowz.getInstance();

Map<String, Object> pdfOptions = new HashMap<>();
pdfOptions.put("url", "https://example.com");
pdfOptions.put("format", "A4");

InputStream pdfStream = smartBrowz.generatePDF(pdfOptions);
```

### Screenshot Generation

```java
ZCSmartBrowz smartBrowz = ZCSmartBrowz.getInstance();

Map<String, Object> screenshotOptions = new HashMap<>();
screenshotOptions.put("url", "https://example.com");
screenshotOptions.put("width", 1920);
screenshotOptions.put("height", 1080);

InputStream screenshotStream = smartBrowz.generateScreenshot(screenshotOptions);
```

---

## Job Scheduling

### Core Class

- **ZCJobScheduling** - Job and cron management

### Job Pool Operations

```java
ZCJobScheduling jobScheduling = ZCJobScheduling.getInstance();

// Get all job pools
List<Object> pools = jobScheduling.getAllJobPools();

// Get specific job pool
Object pool = jobScheduling.getJobPool(poolId);
```

### Job Operations

```java
ZCJobScheduling jobScheduling = ZCJobScheduling.getInstance();

// Create a job
Map<String, Object> jobConfig = new HashMap<>();
jobConfig.put("job_pool_id", poolId);
jobConfig.put("job_name", "MyJob");
jobConfig.put("target_url", "/server/myfunction/execute");

Object job = jobScheduling.createJob(jobConfig);

// Get a job
Object jobDetails = jobScheduling.getJob(jobId);

// Delete a job
jobScheduling.deleteJob(jobId);
```

### Cron Operations

```java
ZCJobScheduling jobScheduling = ZCJobScheduling.getInstance();

// Create a one-time cron
Map<String, Object> oneTimeCron = new HashMap<>();
oneTimeCron.put("cron_name", "OneTimeCron");
oneTimeCron.put("job_id", jobId);
oneTimeCron.put("time", "2026-06-01T10:00:00Z");
Object cron = jobScheduling.createOneTimeCron(oneTimeCron);

// Create a recurring cron
Map<String, Object> recurringCron = new HashMap<>();
recurringCron.put("cron_name", "RecurringCron");
recurringCron.put("job_id", jobId);
recurringCron.put("frequency_type", "hourly");
recurringCron.put("hour", 1);
Object recurring = jobScheduling.createRecurringCron(recurringCron);

// Create cron with expression
Map<String, Object> cronExpr = new HashMap<>();
cronExpr.put("cron_name", "ExpressionCron");
cronExpr.put("job_id", jobId);
cronExpr.put("cron_expression", "0 0 12 * * ?");
Object exprCron = jobScheduling.createCronExpression(cronExpr);

// Get / List crons
Object cronDetails = jobScheduling.getCron(cronId);
List<Object> allCrons = jobScheduling.getAllCrons();

// Update cron
Map<String, Object> updateData = new HashMap<>();
updateData.put("cron_name", "UpdatedCronName");
jobScheduling.updateCron(cronId, updateData);

// Pause / Resume / Run / Delete cron
jobScheduling.pauseCron(cronId);
jobScheduling.resumeCron(cronId);
jobScheduling.runCron(cronId);
jobScheduling.deleteCron(cronId);
```

---

## Pipelines

### Core Class

- **ZCPipeline** - Pipeline orchestration

### Get Pipeline Details

```java
ZCPipeline pipeline = ZCPipeline.getInstance();
Object pipelineDetails = pipeline.getPipelineDetails(pipelineId);
```

### Execute Pipeline

```java
ZCPipeline pipeline = ZCPipeline.getInstance();

Map<String, Object> pipelineInput = new HashMap<>();
pipelineInput.put("param1", "value1");
pipelineInput.put("param2", "value2");

Object executionResult = pipeline.executePipeline(pipelineId, pipelineInput);
```
