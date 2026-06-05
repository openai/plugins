---
name: "Install Wix Apps"
description: Installs Wix apps on a site using Apps Installer API. Covers enabling Velo (Wix Code), app installation, and common app definition IDs.
---
# Install Wix Apps on a Site

This recipe guides you through installing Wix apps on a site using the Apps Installer REST API, including enabling Velo (Wix Code) when needed.

## Prerequisites

- Site ID where apps will be installed
- Knowledge of which app to install (see [Apps Created by Wix](https://dev.wix.com/docs/api-reference/articles/work-with-wix-apis/platform/about-apps-created-by-wix))

## Required APIs

- **Apps Installer API**: [REST](https://dev.wix.com/docs/api-reference/business-management/app-installation/app-installation/install-app)

---
## Step 0: Find the App ID (skip if you already have it)

If you already know the `appDefId` (e.g. from the table of Wix-built apps below), skip to Step 1.

For any third-party app, or any app you only know by name, resolve the ID first using the Search Market Listings API.

**Endpoint**: `POST https://www.wixapis.com/devcenter/app-market-listing/v1/market-listings/search`

**Request**:
```bash
curl -X POST \
  'https://www.wixapis.com/devcenter/app-market-listing/v1/market-listings/search' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{ "searchTerm": "Usercentrics" }'
```

**Response** (truncated):
```json
{
  "marketListings": [
    {
      "appId": "b8cfbda5-91e8-45ad-8c8d-4d4700534ab5",
      "basicInfo": { "name": "Usercentrics for Wix", ... }
    }
  ]
}
```

Use the returned `appId` as the `appDefId` in Step 2.

### IMPORTANT NOTES
- The `appDefId` field in the install request and the `appId` field returned here are the same value
- If multiple results come back, match on `basicInfo.name` to confirm you have the right app before installing
- Only listings with `status: "PUBLISHED"` can be installed
## Step 1: Enable Velo (Wix Code) if Needed

If you receive the error `WDE0110: Wix Code not enabled`, you must first enable Velo on the site.

**Endpoint**: `POST https://www.wixapis.com/mcp-serverless/v1/velo/provision`

**Request**:
```bash
curl -X POST \
  'https://www.wixapis.com/mcp-serverless/v1/velo/provision/' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Response**: Empty body on success.

### IMPORTANT NOTES:
- Only call this endpoint if you receive the `WDE0110` error
- This is a one-time operation per site

---

## Step 2: Install the Wix App

Use the Apps Installer API to install any Wix app on a site.

**Endpoint**: `POST https://www.wixapis.com/apps-installer-service/v1/app-instance/install`

**Request Body**:
```json
{
  "tenant": {
    "tenantType": "SITE",
    "id": "<SITE_ID>"
  },
  "appInstance": {
    "appDefId": "<APP_DEF_ID>"
  }
}
```

**Request**:
```bash
curl -X POST \
  'https://www.wixapis.com/apps-installer-service/v1/app-instance/install' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "tenant": {
      "tenantType": "SITE",
      "id": "<SITE_ID>"
    },
    "appInstance": {
      "appDefId": "<APP_DEF_ID>"
    }
  }'
```

### Common App Definition IDs

Before installing, refer to the [Apps Created by Wix](https://dev.wix.com/docs/api-reference/articles/work-with-wix-apis/platform/about-apps-created-by-wix) documentation to find the correct `appDefId` for the app you want to install.

Some common apps:
| App | appDefId |
|-----|----------|
| Wix Stores | `215238eb-22a5-4c36-9e7b-e7c08025e04e` |
| Wix Bookings | `13d21c63-b5ec-5912-8397-c3a5ddb27a97` |
| Wix Blog | `14bcded7-0066-7c35-14d7-466cb3f09103` |
| Wix Events | `140603ad-af8d-84a5-2c80-a0f60cb47351` |
| Wix Pricing Plans | `1522827f-c56c-a5c9-2ac9-00f9e6ae12d3` |

### IMPORTANT NOTES:
- NEVER guess the `appDefId`. For Wix-built apps, use the table above. For any other app, resolve the ID using Step 0 (Search Market Listings).
- The `tenantType` MUST be `SITE`
- The `id` in tenant is the site's metaSiteId

---

## Error Handling

### App Not Installed Error
If you receive an error indicating a required app is not installed, use this recipe to install it before proceeding.

### WDE0110: Wix Code not enabled
Call the Velo provision endpoint (Step 1) first, then retry the original operation.

---

## Next Steps

After installing an app:
- Configure the app's settings using its specific APIs
- Set up any required app-specific data (products for Stores, services for Bookings, etc.)

---

## Common Pitfalls

- **"I don't have the appDefId"** → Run Step 0. The table in Step 2 only covers Wix-built apps; the App Market has thousands of others.
- **Don't try to scrape the App Market website to find IDs** — pages are client-rendered and the appId is not in the HTML. Use Search Market Listings instead.
- **Don't try `InstallAppFromShareUrl` as a workaround for unknown IDs** — `shareUrlId` is an internal identifier you generally don't have either.
