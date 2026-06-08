---
name: "Query Sites"
description: Lists and queries all sites associated with a Wix account using Sites API. Covers pagination with cursor-based navigation.
---
# Query Sites

This recipe demonstrates how to list and query all sites associated with a Wix account.

## Prerequisites

- Account-level API access
- Authorization for site listing permissions

## Required APIs

- **Query Sites API**: [REST](https://dev.wix.com/docs/api-reference/account-level/sites/sites/query-sites)

---

## Query All Sites

**Endpoint**: `POST https://www.wixapis.com/site-list/v2/sites/query`

**Request Body**:
```json
{
  "query": {
    "cursorPaging": {
      "limit": 50
    }
  }
}
```

**Request**:
```bash
curl -X POST \
  'https://www.wixapis.com/site-list/v2/sites/query' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "cursorPaging": {
        "limit": 50
      }
    }
  }'
```

---

## Response Structure

```json
{
  "sites": [
    {
      "id": "site-id-123",
      "name": "My Website",
      "displayName": "My Website",
      "siteUrl": "https://username.wixsite.com/mywebsite",
      "published": true,
      "createdDate": "2024-01-15T10:30:00Z",
      "updatedDate": "2024-06-20T14:45:00Z"
    }
  ],
  "pagingMetadata": {
    "count": 50,
    "cursors": {
      "next": "cursor-for-next-page"
    },
    "hasNext": true
  }
}
```

---

## Pagination

For accounts with many sites, use cursor-based pagination:

**First Request**:
```json
{
  "query": {
    "cursorPaging": {
      "limit": 50
    }
  }
}
```

**Next Page** (using cursor from response):
```json
{
  "query": {
    "cursorPaging": {
      "limit": 50,
      "cursor": "<cursor-from-previous-response>"
    }
  }
}
```

Continue until `hasNext` is `false`.

---

## Common Use Cases

### List All Sites
Retrieve all sites without filtering - useful for account dashboards or site selection interfaces.

### Find a Specific Site
After querying, filter results by name or ID to locate a specific site.

---

## Next Steps

After finding a site:
- Use the site ID for site-level API calls
- Create new sites using [Create Site from Template](create-site-from-template.md)
- Manage site settings and content
