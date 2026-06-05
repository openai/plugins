---
name: "Add Store Pages to Site"
description: Adds missing checkout and cart pages to a site when Stores app is installed. Used when store pages are missing after migration or setup issues.
---
# Add Store Pages to Site

This recipe demonstrates how to add checkout and cart pages to a Wix site when the Stores app is installed but pages are missing.

## Overview

When Wix Stores is installed on a site, it should automatically create cart and checkout pages. However, in some cases these pages may be missing. This recipe provides a way to add them programmatically.

## Prerequisites

- Wix Stores app installed on the site
- API access with site management permissions

---

## Step 1: Add Pages to Site

**Endpoint**: `POST https://www.wix.com/_api/add-pages-to-site/install`

**Request**:
```bash
curl -X POST \
  'https://www.wix.com/_api/add-pages-to-site/install' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Response**: Empty body on success.

### IMPORTANT NOTES:
- This endpoint adds missing store pages (cart, checkout) if they don't exist
- The request body is empty - no parameters needed
- Only required Authorization header

---

## When to Use This Recipe

Use this recipe when:
- Checkout flow fails because checkout page is missing
- Cart functionality doesn't work
- Store was migrated or had page issues
- You receive errors about missing store pages

---

## Next Steps

After adding pages:
- Verify checkout flow works by creating a test order
- Customize page designs if needed via the Editor
- Set up payment methods if not already configured
