---
name: "Upload Media to Wix"
description: Uploads images and files to the Wix Media Manager using the Import File API. Covers importing from external URLs, checking file status, and using the returned wixstatic.com URL in other APIs.
---
# RECIPE: Upload Media to Wix Media Manager

Learn how to upload images and files to a Wix site's Media Manager using the REST API.

---

## Overview

The Wix Media Manager stores all media files for a site. When you need to use images or files in other Wix APIs, you should first upload them to the Media Manager to get a reliable wixstatic.com URL.

**Key Points:**
- Uploaded files are permanently stored on Wix servers
- You get back a `url` (wixstatic.com) that works reliably in other APIs
- External URLs can fail if the source server blocks requests - Media Manager URLs never fail

---

## Method: Import File from External URL

The simplest way to add media is to import it from an external URL. Wix will download and store the file.

### API Endpoint

```
POST https://www.wixapis.com/site-media/v1/files/import
```

### Request Example

```bash
curl -X POST 'https://www.wixapis.com/site-media/v1/files/import' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
    "url": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=400",
    "mimeType": "image/jpeg",
    "displayName": "My Image"
}'
```

### Request Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | The external URL of the file to import |
| `mimeType` | Recommended | MIME type (e.g., `image/jpeg`, `image/png`). If omitted, Wix tries to detect it |
| `displayName` | No | Display name in Media Manager. Include extension (e.g., `My Image.jpg`) |
| `parentFolderId` | No | Folder ID to store the file. Defaults to `media-root` |

### Response Example

```json
{
    "file": {
        "id": "e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "displayName": "My Image.jpg",
        "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "parentFolderId": "media-root",
        "mediaType": "IMAGE",
        "operationStatus": "PENDING",
        "sizeInBytes": "31911"
    }
}
```

### Key Response Fields

| Field | Description |
|-------|-------------|
| `id` | Media ID |
| `url` | **The wixstatic.com URL - use this in other APIs** |
| `operationStatus` | `PENDING` → `READY` when processed, or `FAILED` if import failed |

> **Can I Use the URL Immediately?**
>
> **In most cases, yes.** The returned `wixstatic.com` URL typically works immediately for basic use cases like adding to products or blog posts.
>
> **Wait for READY when:**
> - You need image dimensions or metadata
> - You're using image transformations (resize, crop)
> - You want guaranteed consistency for critical operations
>
> **Practical approach:** Try using the URL immediately. If it fails, poll until `operationStatus: "READY"`.

---

## Checking File Status

After importing, the file goes through async processing. For guaranteed consistency, verify `operationStatus: "READY"` before using the file.

### Get File by ID (Recommended)

Use this endpoint to check the status of a specific file:

```bash
curl -X GET 'https://www.wixapis.com/site-media/v1/files/get-file-by-id?fileId={fileId}' \
-H 'Authorization: <AUTH>'
```

**Example:**

```bash
curl -X GET 'https://www.wixapis.com/site-media/v1/files/get-file-by-id?fileId=e6a89e_9d32c0dbae954582bce7b2bf35981ca6~mv2.jpg' \
-H 'Authorization: <AUTH>'
```

### List Recent Files (Alternative)

If you need to find files without knowing the ID:

```bash
curl -X GET 'https://www.wixapis.com/site-media/v1/files?parentFolderId=media-root&mediaTypes=IMAGE&sort.fieldName=updatedDate&sort.order=DESC&paging.limit=5' \
-H 'Authorization: <AUTH>'
```

### Status Values

| Status | Meaning |
|--------|---------|
| `PENDING` | Still processing - wait before using |
| `READY` | File is ready to use |
| `FAILED` | Import failed |

### Response When Ready

```json
{
    "files": [{
        "id": "e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "operationStatus": "READY",
        "media": {
            "image": {
                "image": {
                    "height": 600,
                    "width": 400
                }
            }
        },
        "labels": ["cupcakes", "pastry", "dessert"]
    }]
}
```

> **Note:** Wix automatically generates labels (tags) for images using AI.

---

## Alternative: Upload from Local Device

If you need to upload files from a local device (not from a URL), use the two-step upload process:

### Step 1: Generate Upload URL

```bash
curl -X POST 'https://www.wixapis.com/site-media/v1/files/generate-upload-url' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
    "mimeType": "image/jpeg",
    "fileName": "my-photo.jpg"
}'
```

### Step 2: Upload to the Generated URL

```bash
curl -X PUT '<UPLOAD_URL_FROM_RESPONSE>' \
-H 'Content-Type: image/jpeg' \
--data-binary @my-photo.jpg
```

> **Note:** For files larger than 10MB, use the Resumable Upload URL API instead.

---

## Common Issues

### Issue 1: Import Fails (operationStatus: FAILED)

**Problem:** The file shows `operationStatus: "FAILED"` after import.

**Causes:**
- Source server blocks external requests (e.g., Wikipedia, some CDNs)
- Source server requires authentication
- Invalid URL or file not found
- File type not supported

**Solution:** Use image sources that allow hotlinking:
- Unsplash (`images.unsplash.com`)
- Pexels (`images.pexels.com`)
- Your own hosted images
- Public cloud storage (S3, GCS with public access)

### Issue 2: File Stuck in PENDING

**Problem:** File stays in `PENDING` status for a long time.

**Solution:**
- Large files take longer to process
- Check back after a few seconds
- If still pending after 30+ seconds, the import may have silently failed

---

## Summary

| Step | Action | Result |
|------|--------|--------|
| 1 | Call Import File API with external URL | Get file `id` and `url` with status `PENDING` |
| 2 | Poll List Files API | Wait for `operationStatus: "READY"` |
| 3 | Use in other APIs | Use the `url` field (wixstatic.com URL) |
