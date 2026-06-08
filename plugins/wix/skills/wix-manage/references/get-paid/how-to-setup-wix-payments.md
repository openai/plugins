---
name: "How to Setup Wix Payments"
description: Configures Wix Payments as the payment provider. Covers eligibility checking, business verification, bank account setup, and payment method configuration (cards, PayPal, Apple Pay).
---
# How to Set Up Wix Payments

This recipe covers the setup flow needed before creating payment links or collecting payments.

## Step 1: Collect required user inputs

Before connecting Wix Payments, collect and confirm:

1. Terms acceptance: https://www.wix.com/about/terms-of-payments
2. First name
3. Last name
4. Product/service description (minimum meaningful business description)

## Step 2: Connect Wix Payments account

Call:

- `POST https://www.wixapis.com/payments/v1/wix-payments-account/connect`

```json
{
  "account": {
    "firstName": "<USER_FIRST_NAME>",
    "lastName": "<USER_LAST_NAME>",
    "tosAccepted": true,
    "productDescription": "<PRODUCT_DESCRIPTION>"
  }
}
```

## Step 3: Handle common setup blockers

### Location-related failure

If setup fails due to location details, update the business location and retry:

- `PUT https://www.wixapis.com/locations/v1/locations/{locationId}`
- Reference: [Update Location](https://dev.wix.com/docs/api-reference/business-management/locations/update-location)

### Already connected

If the API returns an "already connected" style response, skip reconnect and continue with onboarding checks.

## Step 4: Complete dashboard onboarding

Connecting the account is not always the final step. To receive payments, the site owner may still need to complete Wix Payments onboarding in the site dashboard.

## Important Notes

1. Never invent or assume user identity/business details.
2. Always obtain explicit user consent before calling connect.
3. Use the exact accepted values provided by the user.
4. Verify readiness by testing a real payment flow (for example, create payment link) after setup.
