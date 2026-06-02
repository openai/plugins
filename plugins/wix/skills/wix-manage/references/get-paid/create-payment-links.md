---
name: "Create Payment Links"
description: Creates payment links for collecting payments without a checkout flow. Covers store products (catalog items), custom line items, variants, due dates, and sending links via email.
---
# Create Payment Links

This recipe shows how to create and manage payment links using the current Payment Links REST API.

## Prerequisites

1. Site is premium.
2. Site is published.
3. Site is set up to accept payments (Wix Payments onboarding completed).
4. App has payment-link permissions.
5. Wix Stores is installed if you plan to charge for catalog products.

## Required APIs

- **Payment Links API**: [REST](https://dev.wix.com/docs/api-reference/business-management/get-paid/payment-links/payment-links/create-payment-link)
- **Products API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v1/catalog/query-products)

## Overview

Payment links are created at:

- `POST https://www.wixapis.com/payment-links/v1/payment-links`

Use one of these payment-link types:

- `ECOM`: charge for custom or catalog line items.
- `ECOM_ORDER`: collect payment for an existing unpaid eCommerce order.

## Step 1: Retrieve product details (optional)

If you plan to use catalog items, fetch the product first.

**Examples**:

- Catalog V1: `GET https://www.wixapis.com/stores/v1/products/{productId}`
- Catalog V1 query: `POST https://www.wixapis.com/stores/v1/products/query`

```json
{
  "query": {
    "paging": {
      "limit": 50,
      "offset": 0
    }
  }
}
```

## Step 2: Create an `ECOM` payment link with custom line items

```json
{
  "paymentLink": {
    "title": "Business Listing Fee",
    "description": "One-time listing fee",
    "currency": "USD",
    "type": "ECOM",
    "ecomPaymentLink": {
      "lineItems": [
        {
          "type": "CUSTOM",
          "customItem": {
            "name": "Listing Fee",
            "quantity": 1,
            "price": "200.00"
          }
        }
      ]
    }
  }
}
```

## Step 3: Create an `ECOM` payment link with catalog items

```json
{
  "paymentLink": {
    "title": "Product Payment",
    "currency": "USD",
    "type": "ECOM",
    "ecomPaymentLink": {
      "lineItems": [
        {
          "type": "CATALOG",
          "catalogItem": {
            "quantity": 1,
            "catalogReference": {
              "appId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
              "catalogItemId": "PRODUCT_ID",
              "options": {
                "variantId": "VARIANT_ID"
              }
            }
          }
        }
      ]
    }
  }
}
```

## Step 4: Create an `ECOM_ORDER` payment link for an existing order

```json
{
  "paymentLink": {
    "title": "Order Balance",
    "currency": "USD",
    "type": "ECOM_ORDER",
    "paymentsLimit": 1,
    "ecomOrderPaymentLink": {
      "orderId": "ORDER_ID",
      "amount": "50"
    }
  }
}
```

## Step 5: Send payment link to recipients

Use:

- `POST https://www.wixapis.com/payment-links/v1/payment-links/{paymentLinkId}/send`

Request body:

```json
{
  "paymentLinkId": "PAYMENT_LINK_ID",
  "recipients": [
    {
      "contactId": "CONTACT_ID",
      "sendMethods": ["EMAIL_METHOD"]
    }
  ]
}
```

## Step 6: Query and manage payment links

Query:

- `POST https://www.wixapis.com/payment-links/v1/payment-links/query`

```json
{
  "query": {
    "filter": {
      "status": "ACTIVE"
    },
    "cursorPaging": {
      "limit": 50
    }
  }
}
```

Get one:

- `GET https://www.wixapis.com/payment-links/v1/payment-links/{paymentLinkId}`

Deactivate:

- `POST https://www.wixapis.com/payment-links/v1/payment-links/{paymentLinkId}/deactivate`

Activate:

- `POST https://www.wixapis.com/payment-links/v1/payment-links/{paymentLinkId}/activate`

Delete (only when no payments were received):

- `DELETE https://www.wixapis.com/payment-links/v1/payment-links/{paymentLinkId}`

## Payment Link Statuses

| Status | Description |
|--------|-------------|
| `ACTIVE` | Link is active and can receive payments |
| `INACTIVE` | Link is inactive and cannot receive payments |
| `PAID` | Payment has been completed |
| `EXPIRED` | Link has passed its expiration date |

## Common Errors

| Error Code | Meaning |
|------------|---------|
| `UNPUBLISHED_SITE` | Site must be published before creating payment links |
| `MISSING_ACCEPT_PAYMENTS` | Site is not set up to accept payments |
| `FAILED_TO_INSTALL_ECOM` | Required eCommerce capability is missing |
| `RECIPIENT_NOT_FOUND` | Provided recipient contact does not exist |
| `ORDER_NOT_FOUND` | Provided order ID does not exist |
| `INVALID_PAYMENTS_LIMIT_FOR_ECOM_ORDER_PAYMENT_LINK` | `ECOM_ORDER` links require `paymentsLimit: 1` |

## Best Practices

1. Validate prerequisites first (premium, published, payments enabled).
2. Use `ECOM` for line-item collection and `ECOM_ORDER` for existing unpaid orders.
3. Use IDs from real entities (products, variants, contacts, orders).
4. Keep currency aligned with your business/order currency rules.
5. Persist payment-link IDs and monitor status via query/get methods.

## Related Documentation

- [Payment Links API Reference](https://dev.wix.com/docs/api-reference/business-management/get-paid/payment-links/payment-links/introduction)
- [Payments Overview](https://dev.wix.com/docs/api-reference/business-management/get-paid/payment-links/introduction)
- [Products API Reference](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v1/catalog/introduction)
- [Send Payment Link](https://dev.wix.com/docs/api-reference/business-management/get-paid/payment-links/payment-links/send-payment-link)
