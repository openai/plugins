# Additional Fees Service Plugin Reference

## Overview

The Additional Fees SPI lets you add custom fees to orders during checkout (handling fees, rush delivery charges, global order fees, etc.). Implement the `calculateAdditionalFees` handler — it calculates and returns the fees to apply.

## Request and Response Schema

Before implementing, call `ReadFullDocsMethodSchema` on the docs URL to get the full request/response types.

| Handler | Docs URL |
| --- | --- |
| `calculateAdditionalFees` | https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/additional-fees/additional-fees-service-plugin/calculate-additional-fees?apiView=SDK |

## Example: Global Additional Fee from Database Configuration

This example queries a CMS collection to retrieve a configurable global fee that applies to all orders.

```typescript
import { additionalFees } from '@wix/ecom/service-plugins';
import { auth } from '@wix/essentials';
import { items } from '@wix/data';

interface GlobalFeeConfig {
  _id: string;
  feeAmount: number;
  isEnabled: boolean;
}

additionalFees.provideHandlers({
  calculateAdditionalFees: async ({ request, metadata }) => {
    try {
      // Query the global additional fee configuration (elevated permissions required)
      const elevatedQuery = auth.elevate(items.query);
      const configResult = await elevatedQuery('global-additional-fee-config')
        .limit(1)
        .find();

      // If no configuration found or fee is disabled, return empty fees
      if (!configResult.items.length) {
        return {
          additionalFees: [],
          currency: metadata.currency || 'USD'
        };
      }

      const config = configResult.items[0] as GlobalFeeConfig;

      // Check if the fee is enabled and has a valid amount
      if (!config.isEnabled || !config.feeAmount || config.feeAmount <= 0) {
        return {
          additionalFees: [],
          currency: metadata.currency || 'USD'
        };
      }

      // Ensure currency matches site currency
      const responseCurrency = metadata.currency || 'USD';

      // Convert fee amount to string as required by Wix API
      const feeAmountString = config.feeAmount.toString();

      // Create the global additional fee
      const globalFee = {
        code: 'global-additional-fee',
        name: 'Global Additional Fee',
        translatedName: 'Global Additional Fee',
        price: feeAmountString,
        taxDetails: {
          taxable: true
        }
        // No lineItemIds specified - applies to entire cart
      };

      return {
        additionalFees: [globalFee],
        currency: responseCurrency
      };

    } catch (error) {
      return {
        additionalFees: [],
        currency: metadata.currency || 'USD'
      };
    }
  },
});
```

## Key Implementation Notes

1. **Elevate permissions for API calls** - Use `auth.elevate` from `@wix/essentials` when calling Wix APIs from service plugins
2. **Return empty array when no fees apply** - Always return `{ additionalFees: [], currency: "..." }` when conditions aren't met
3. **Price must be a string** - Convert numeric amounts to strings
4. **Handle errors gracefully** - Return empty fees on error rather than throwing
5. **Omit lineItemIds for cart-wide fees** - Only specify when fee applies to specific items
