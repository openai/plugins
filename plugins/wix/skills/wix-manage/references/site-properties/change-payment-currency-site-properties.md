---
name: "RECIPE: Change a Site's Payment (Store) Currency via Site Properties API"
description: "Updates the site-level payment currency (store billing currency) using Site Properties API, including the required request body shape and field mask."
---

# RECIPE: Change a Site's Payment (Store) Currency via Site Properties API

## Goal
Update a Wix site's **payment currency** (the ISO-4217 currency code used to bill customers) programmatically.

## When to use
- You need to switch a site's store/payment currency (for example, from `USD` to `EUR`).
- You want to automate regional/business setup for sites.

## Important notes before you start
- The `paymentCurrency` field is part of **Site Properties** (often shown in the dashboard under regional/business info).
- A successful update increments the Site Properties `version`.
- Use a **field mask** (`fields.paths`) to indicate which fields you're updating.

## Step 1 — (Optional) Read current site properties version
This is useful to understand the current snapshot version and other regional fields.

```bash
curl -X GET 'https://www.wixapis.com/site-properties/v4/properties' \
  -H 'Authorization: <AUTH>'
```

## Step 2 — Update the payment currency
Use the `PATCH /site-properties/v4/properties` endpoint: put the new currency under `properties.paymentCurrency` and include a `fields.paths` mask.

```bash
curl -X PATCH 'https://www.wixapis.com/site-properties/v4/properties' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: <AUTH>' \
  --data-binary '{
    "properties": {
      "paymentCurrency": "EUR"
    },
    "fields": {
      "paths": ["paymentCurrency"]
    }
  }'
```

### Expected response
A successful call returns an updated Site Properties snapshot version, for example:

```json
{ "version": "123" }
```

## Gotchas & troubleshooting
- **Always send a field mask**: omitting `fields.paths` will fail with `400` and `"Illegal request - No updates on request body"`.
- Currency must be a **3-letter ISO-4217** code (for example, `USD`, `CAD`, `EUR`, `GBP`).

## Related APIs
- **Site Properties API**: [REST](https://dev.wix.com/docs/api-reference/business-management/site-properties/properties/introduction)
- Stores Currency Converter (conversion utilities, not for setting the site currency):
  - `POST https://www.wixapis.com/currency_converter/v1/currencies/amounts/{from}/convert/{to}`
