# Shipping Rates Service Plugin Reference

## Overview

The Shipping Rates SPI lets you provide custom shipping options and calculate shipping costs based on order details, destination, weight, or any custom logic. Implement the `getShippingRates` handler — it returns the available shipping options with their costs.

## Request and Response Schema

Before implementing, call `ReadFullDocsMethodSchema` on the docs URL to get the full request/response types.

| Handler | Docs URL |
| --- | --- |
| `getShippingRates` | https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/shipping-rates/shipping-rates-integration-service-plugin/get-shipping-rates?apiView=SDK |

## Example: International Shipping with Handling Fee

This example provides an international shipping option with an additional handling fee charge.

```typescript
import { shippingRates } from "@wix/ecom/service-plugins";
import { ChargeType } from "@wix/auto_sdk_ecom_shipping-rates";

shippingRates.provideHandlers({
  getShippingRates: async (payload) => {
    const { request, metadata } = payload;
    // Use the `request` and `metadata` received from Wix and
    // apply custom logic.
    return {
      // Return your response exactly as documented to integrate with Wix.
      // Return value example:
      shippingRates: [
        {
          code: "usps-international",
          title: "USPS - International",
          logistics: {
            deliveryTime: "2-5 days",
          },
          cost: {
            price: "15",
            currency: metadata.currency || "ILS",
            additionalCharges: [
              {
                price: "10",
                type: ChargeType.HANDLING_FEE,
                details: "Handling fee of $5 applied for fragile items.",
              },
            ],
          },
        },
      ],
    };
  },
});
```

## Key Implementation Notes

1. **Price as string** - All price values must be strings, not numbers
2. **Currency from metadata** - Use `metadata.currency` to get the site's currency
3. **Multiple options** - You can return multiple shipping rate options for customer to choose
4. **Unique codes** - Each shipping option needs a unique `code` identifier
5. **Additional charges** - Use `additionalCharges` array for itemized extra costs like handling fees
