---
name: "Payment Links for Bookings"
description: Creates payment links for unpaid bookings using Payment Links API. Links booking IDs to payment requests with proper redirect handling.
---
# Payment Links for Bookings

Use this recipe to collect payment for booking-related flows by generating payment links with the Payment Links API.

## When to Use Which Type

### Use `ECOM_ORDER` for existing unpaid orders

If a booking already has an associated unpaid eCommerce order, create an `ECOM_ORDER` payment link.

```json
{
  "paymentLink": {
    "title": "Booking Balance",
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

Notes:
- `orderId` must exist and be unpaid.
- `ECOM_ORDER` links require `paymentsLimit: 1`.

### Use `ECOM` for ad-hoc booking charges

If there is no existing order, create an `ECOM` payment link with custom line items.

```json
{
  "paymentLink": {
    "title": "Booking Fee",
    "currency": "USD",
    "type": "ECOM",
    "ecomPaymentLink": {
      "lineItems": [
        {
          "type": "CUSTOM",
          "customItem": {
            "name": "Booking Fee",
            "quantity": 1,
            "price": "50.00"
          }
        }
      ]
    }
  }
}
```

## Send Flow

Creating a payment link does not deliver it. Send it explicitly:

- `POST https://www.wixapis.com/payment-links/v1/payment-links/{paymentLinkId}/send`

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

## Prerequisites

Before creating booking payment links, ensure:

1. Site is premium.
2. Site is published.
3. Site is set up to accept payments.
4. Required payment-link permissions are granted to the app.
5. Recipient contacts exist if you plan to send links.

## Common Errors

| Error Code | Meaning |
|------------|---------|
| `UNPUBLISHED_SITE` | Site must be published before creating payment links |
| `MISSING_ACCEPT_PAYMENTS` | Site is not set up to accept payments |
| `ORDER_NOT_FOUND` | The provided order ID does not exist |
| `INVALID_PAYMENTS_LIMIT_FOR_ECOM_ORDER_PAYMENT_LINK` | `ECOM_ORDER` links require `paymentsLimit: 1` |
| `RECIPIENT_NOT_FOUND` | Recipient contact ID does not exist |

## API Documentation References

- [Create Payment Link](https://dev.wix.com/docs/api-reference/business-management/get-paid/payment-links/payment-links/create-payment-link)
- [Send Payment Link](https://dev.wix.com/docs/api-reference/business-management/get-paid/payment-links/payment-links/send-payment-link)
