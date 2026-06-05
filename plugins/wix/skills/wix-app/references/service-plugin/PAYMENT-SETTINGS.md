# Payment Settings Service Plugin Reference

## Overview

The Payment Settings SPI lets you integrate custom payment settings with the Wix eCommerce payment process. It's called during payment processing (e.g., when a customer enters credit card details) and returns settings that Wix passes to the payment provider. A common use case is enforcing 3D Secure (3DS) for certain transactions. Implement the `getPaymentSettings` handler.

## Request and Response Schema

Before implementing, call `ReadFullDocsMethodSchema` on the docs URL to get the full request/response types.

| Handler | Docs URL |
| --- | --- |
| `getPaymentSettings` | https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/payments/payment-settings/payment-settings-integration-service-plugin/get-payment-settings?apiView=SDK |

## Example: Require 3DS for High-Value Transactions

This example enforces 3D Secure authentication for orders above a certain threshold.

```typescript
import { paymentSettings } from '@wix/ecom/service-plugins';

// Configuration
const HIGH_VALUE_THRESHOLD = 1000;

paymentSettings.provideHandlers({
  getPaymentSettings: async ({ request, metadata }) => {
    try {
      // Get the order total
      const orderTotal = request.order?.totals?.total || 0;

      // Determine if 3DS is required based on order value
      const require3DS = orderTotal >= HIGH_VALUE_THRESHOLD;

      return {
        paymentSettings: {
          requires3dSecure: require3DS
        }
      };
    } catch (error) {
      // Default to not requiring 3DS on error
      return {
        paymentSettings: {
          requires3dSecure: false
        }
      };
    }
  },
});
```

## Example: Region-Based 3DS Requirements

This example requires 3D Secure for specific countries or regions.

```typescript
import { paymentSettings } from '@wix/ecom/service-plugins';

// Countries that require 3DS
const REQUIRE_3DS_COUNTRIES = ['GB', 'FR', 'DE', 'IT', 'ES'];

paymentSettings.provideHandlers({
  getPaymentSettings: async ({ request, metadata }) => {
    try {
      // Get billing country from order
      const billingCountry = request.order?.billingInfo?.address?.country;

      // Check if country requires 3DS
      const require3DS = billingCountry
        ? REQUIRE_3DS_COUNTRIES.includes(billingCountry)
        : false;

      return {
        paymentSettings: {
          requires3dSecure: require3DS
        }
      };
    } catch (error) {
      // Default to not requiring 3DS on error
      return {
        paymentSettings: {
          requires3dSecure: false
        }
      };
    }
  },
});
```

## Key Implementation Notes

1. **Payment provider required** - Site must have a payment provider connected to collect payments
2. **Provider support required** - The payment provider must support the settings (e.g., not all providers support 3DS)
3. **Called during checkout** - This handler is invoked when the customer enters payment details during checkout
4. **Settings passed to provider** - The returned settings are passed to the payment provider for enforcement
5. **Fallback configuration** - Use the `fallbackValueForRequires3dSecure` builder field to set a default value if the SPI call fails (defaults to `false`)
6. **Handle errors gracefully** - Return sensible defaults on error rather than throwing

