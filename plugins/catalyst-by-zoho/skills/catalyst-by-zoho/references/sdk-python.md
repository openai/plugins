# Python SDK Reference (zcatalyst-sdk)

External docs: https://docs.catalyst.zoho.com/en/sdk/python/v1/overview/

## Installation

```bash
pip install zcatalyst-sdk
```

Requires **Python 3.9+**.

---

## Initialization

```python
import zcatalyst_sdk

# --- Advanced I/O (Flask) ---
# In a Flask-based Advanced I/O function, pass the Flask request object:
catalyst_app = zcatalyst_sdk.initialize(req=request)

# --- Basic I/O ---
# In a Basic I/O function, pass the context object:
catalyst_app = zcatalyst_sdk.initialize(req=context)

# --- Event / Cron Functions ---
# Same pattern — pass the context/event object provided by the runtime:
catalyst_app = zcatalyst_sdk.initialize(req=context)

# --- Admin Scope ---
# For operations that require admin-level access (e.g., user management):
admin_app = zcatalyst_sdk.initialize(req=request, scope='admin')
```

---

## Data Store

```python
# Get a table reference
table = catalyst_app.datastore().table("TableName")

# Insert a single row
row = table.insert_row({
    "Name": "Alice",
    "Email": "alice@example.com"
})

# Insert multiple rows
rows = table.insert_rows([
    {"Name": "Bob", "Email": "bob@example.com"},
    {"Name": "Carol", "Email": "carol@example.com"}
])

# Get a single row by ROWID
row = table.get_row(row_id)

# Get paged rows (paginated)
# Returns dict with keys: data, next_token, more_records
result = table.get_paged_rows(
    next_token="token_string",   # optional, for subsequent pages
    max_rows=200                 # optional, default varies
)
rows = result["data"]
has_more = result["more_records"]
next_token = result["next_token"]

# Update a row (ROWID is required in the dict)
updated_row = table.update_row({
    "ROWID": "123456000000012345",
    "Name": "Alice Updated"
})

# Delete a row by ROWID
table.delete_row(row_id)
```

---

## ZCQL

```python
zcql_service = catalyst_app.zcql()

# Execute a standard query
rows = zcql_service.execute_query("SELECT * FROM TableName WHERE Name = 'Alice'")

# Execute an OLAP query (aggregations, joins, etc.)
result = zcql_service.execute_olap_query("SELECT COUNT(ROWID) FROM TableName GROUP BY Status")
```

---

## Cache

```python
cache_service = catalyst_app.cache()

# Get a cache segment by ID
segment = cache_service.segment(segment_id)

# Put a value (with optional expiry in milliseconds)
segment.put("my_key", "my_value", expiry=3600000)

# Get a value
value = segment.get("my_key")

# Update a value
segment.update("my_key", "new_value", expiry=7200000)

# Delete a value
segment.delete("my_key")
```

---

## File Store

```python
filestore_service = catalyst_app.filestore()

# Get a folder reference by ID
folder = filestore_service.folder(folder_id)

# Upload a file (use 'rb' mode)
with open("/path/to/file.pdf", "rb") as f:
    uploaded = folder.upload_file(f)

# Download a file by file ID
file_content = folder.download_file(file_id)

# Delete a file by file ID
folder.delete_file(file_id)

# Get file details
details = folder.get_details(file_id)
```

---

## Authentication

```python
auth_service = catalyst_app.authentication()

# Register a new user
signup_config = {
    "platform_type": "web",
    "zaid": "your_zaid"
}
user_details = {
    "first_name": "Alice",
    "last_name": "Smith",
    "email_id": "alice@example.com"
}
result = auth_service.register_user(signup_config, user_details)

# Get current user details
user = auth_service.get_user_details()

# Delete a user by user ID
auth_service.delete_user(user_id)
```

---

## Email

```python
email_service = catalyst_app.email()

email_service.send_mail({
    "from_email": "noreply@yourdomain.com",
    "to_email": ["recipient@example.com"],
    "cc": ["cc@example.com"],        # optional
    "bcc": ["bcc@example.com"],      # optional
    "reply_to": "reply@example.com", # optional
    "subject": "Hello from Catalyst",
    "content": "<h1>Welcome!</h1><p>This is a test email.</p>",
    "html_mode": True                # optional, defaults to True
})
```

---

## Search

```python
search_service = catalyst_app.search()

result = search_service.execute_search_query(
    "search term",
    search_config={
        "search_table_columns": {
            "TableName": ["ColumnName1", "ColumnName2"]
        }
    }
)
```

---

## Connections

```python
conn_service = catalyst_app.connections()

# Get OAuth credentials for a configured connection
credentials = conn_service.get_connection_credentials({
    "connection_name": "my_connection"
})
# credentials contains access_token, etc.
```

---

## Circuits

```python
circuit_service = catalyst_app.circuit()

# Execute a circuit by ID with input data
result = circuit_service.execute(circuit_id, {
    "key1": "value1",
    "key2": "value2"
})
```

---

## NoSQL

```python
nosql_service = catalyst_app.nosql()

# Get a table reference
table = nosql_service.table("NoSQLTableName")

# Insert items
table.insertItems([
    {"pk": "partition1", "sk": "sort1", "data": "value1"},
    {"pk": "partition2", "sk": "sort2", "data": "value2"}
])

# Fetch items by keys
items = table.fetchItems([
    {"pk": "partition1", "sk": "sort1"}
])

# Query a table (by partition key)
results = table.queryTable({
    "pk": "partition1",
    "query": {
        "condition": "sk BEGINS_WITH 'sort'",
        "limit": 10
    }
})

# Query a secondary index
results = table.queryIndex({
    "index_name": "MyIndex",
    "pk": "index_partition_value",
    "query": {
        "condition": "sk BEGINS_WITH 'prefix'"
    }
})

# Update items
table.updateItems([
    {
        "pk": "partition1",
        "sk": "sort1",
        "update_expression": "SET data = :val",
        "expression_values": {":val": "updated_value"}
    }
])

# Delete items
table.deleteItems([
    {"pk": "partition1", "sk": "sort1"}
])
```

---

## Stratus (Object Storage)

```python
stratus_service = catalyst_app.stratus()

# List all buckets
buckets = stratus_service.list_buckets()

# Get a bucket reference
bucket = stratus_service.bucket(bucket_name)

# Get bucket details
details = bucket.get_details()

# List objects in a bucket
objects = bucket.list_objects(prefix="folder/", max_keys=100)

# Upload an object
with open("/path/to/file.txt", "rb") as f:
    bucket.upload_object("folder/file.txt", f, content_type="text/plain")

# Download an object
content = bucket.download_object("folder/file.txt")

# Delete an object
bucket.delete_object("folder/file.txt")

# Rename an object
bucket.rename_object("folder/old_name.txt", "folder/new_name.txt")
```

---

## Bulk Data Store

```python
datastore = catalyst_app.datastore()

# Bulk Read — create a bulk read job for a table
bulk_read_job = datastore.bulkRead({
    "table_id": table_id,
    "query": {
        "criteria": {
            "column_name": "Status",
            "comparator": "equal",
            "value": "active"
        }
    }
})
# Poll job status and download CSV when complete

# Bulk Write — upload a CSV to bulk insert/update
bulk_write_job = datastore.bulkWrite({
    "table_id": table_id,
    "operation": "insert",  # or "update"
    "file_id": uploaded_file_id
})

# Bulk Delete — delete multiple rows
datastore.bulkDeleteRows(table_id, [row_id_1, row_id_2, row_id_3])
```

---

## Push Notifications

```python
push_service = catalyst_app.pushnotification()

# Send a web push notification
push_service.sendNotification({
    "subject": "New Update",
    "message": "A new feature has been released.",
    "recipients": ["user_id_1", "user_id_2"]
})

# Send a mobile push notification
push_service.sendMobileNotification({
    "message": "Your order has shipped!",
    "recipients": ["user_id_1"],
    "additional_data": {"order_id": "12345"}
})
```

---

## Zia Services

```python
zia_service = catalyst_app.zia()

# OCR — Extract text from an image
with open("document.png", "rb") as f:
    ocr_result = zia_service.extractOpticalCharacters(f, {
        "language": "eng",
        "model_type": "OCR"
    })

# AutoML — Execute an AutoML model prediction
automl_result = zia_service.executeAutoML(model_id, {
    "feature1": "value1",
    "feature2": 42
})

# Sentiment Analysis
sentiment = zia_service.getSentimentAnalysis(["I love this product!", "Terrible experience."])

# Named Entity Recognition
entities = zia_service.getNamedEntityRecognition(["Zoho Corporation is based in Chennai, India."])

# Keyword Extraction
keywords = zia_service.getKeywordExtraction(["Catalyst is a serverless platform for building applications."])

# All Text Analytics (sentiment + NER + keywords combined)
analytics = zia_service.getAllTextAnalytics(["Zoho Catalyst makes development easy and fast."])

# Image Moderation
with open("image.jpg", "rb") as f:
    moderation = zia_service.moderateImage(f)

# Face Detection
with open("photo.jpg", "rb") as f:
    faces = zia_service.detectFaces(f)

# Object Recognition
with open("scene.jpg", "rb") as f:
    objects = zia_service.recognizeObjects(f)

# Barcode Scanning
with open("barcode.png", "rb") as f:
    barcode = zia_service.scanBarcode(f)
```

---

## SmartBrowz

```python
smart_browz_service = catalyst_app.smart_browz()

# Generate output from an HTML template
output = smart_browz_service.generate_output_from_template({
    "template_id": template_id,
    "template_data": {"name": "Alice", "amount": "$100"},
    "output_type": "pdf"
})

# Convert a URL or HTML content to PDF
pdf = smart_browz_service.convert_to_pdf({
    "url": "https://example.com",
    "pdf_options": {
        "format": "A4",
        "print_background": True,
        "margin": {"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
    },
    "page_options": {
        "width": 1280,
        "height": 800
    },
    "navigation_options": {
        "wait_until": "networkidle0",
        "timeout": 30000
    }
})

# Take a screenshot of a URL
screenshot = smart_browz_service.take_screenshot({
    "url": "https://example.com",
    "screenshot_options": {
        "full_page": True,
        "type": "png",
        "quality": 80,
        "clip": {"x": 0, "y": 0, "width": 1280, "height": 800}
    },
    "page_options": {
        "width": 1440,
        "height": 900
    },
    "navigation_options": {
        "wait_until": "networkidle2",
        "timeout": 60000
    }
})
```

---

## Job Scheduling

```python
job_service = catalyst_app.job_scheduling()

# Get a pool reference by ID
pool = job_service.pool(pool_id)

# Submit a one-time job
job = pool.submit_job({
    "job_name": "data_sync",
    "target_function": "sync_function",
    "params": {"source": "db1", "target": "db2"},
    "schedule": "one_time"
})

# Create a cron job — various schedule types
# Interval-based cron
cron = pool.create_cron({
    "cron_name": "hourly_cleanup",
    "target_function": "cleanup_function",
    "cron_type": "interval",
    "repeat_interval": 3600,  # seconds
    "params": {"retain_days": 30}
})

# Calendar-based cron (specific time)
cron = pool.create_cron({
    "cron_name": "daily_report",
    "target_function": "generate_report",
    "cron_type": "calendar",
    "cron_expression": "0 9 * * *",  # every day at 9 AM
    "params": {"report_type": "daily_summary"}
})

# Fixed-delay cron
cron = pool.create_cron({
    "cron_name": "queue_processor",
    "target_function": "process_queue",
    "cron_type": "fixed_delay",
    "repeat_interval": 300,  # 5 minutes after previous run completes
    "params": {}
})
```
