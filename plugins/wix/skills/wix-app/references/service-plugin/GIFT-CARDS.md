# Gift Cards Service Plugin Reference

## Overview

The Gift Vouchers Provider SPI allows you to integrate external gift card or voucher systems with Wix eCommerce. This enables customers to redeem gift cards, check balances, and void transactions.

## Handlers

| Handler | Description |
| --- | --- |
| `redeem` | Process a gift card redemption during checkout |
| `getBalance` | Check the current balance of a gift card |
| `_void` | Cancel/void a previous redemption |

## Request and Response Schema

Before implementing, call `ReadFullDocsMethodSchema` on each docs URL to get the full request/response types.

| Handler | Docs URL |
| --- | --- |
| `redeem` | https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/payments/gift-cards/gift-cards-service-plugin/redeem?apiView=SDK |
| `getBalance` | https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/payments/gift-cards/gift-cards-service-plugin/get-balance?apiView=SDK |
| `_void` | https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/payments/gift-cards/gift-cards-service-plugin/void?apiView=SDK |

## Example: Gift Card Provider Implementation

This example shows a basic gift card provider with all three required handlers.

```typescript
import { giftVouchersProvider } from '@wix/ecom/service-plugins';

giftVouchersProvider.provideHandlers({
  redeem: async (payload) => {
    const { request, metadata } = payload;
    // Use the `request` and `metadata` received from Wix and
    // apply custom logic.
    return {
      // Return your response exactly as documented to integrate with Wix.
      // Return value example:
      remainingBalance: 80.00,
      currencyCode: metadata.currency || "ILS",
      transactionId: "00000000-0000-0000-0000-000000000001",
    };
  },
  _void: async (payload) => {
    const { request, metadata } = payload;
    // Use the `request` and `metadata` received from Wix and
    // apply custom logic.
    return {
      // Return your response exactly as documented to integrate with Wix.
      // Return value example:
      remainingBalance: 100.00,
      currencyCode: metadata.currency || "ILS",
    };
  },
  getBalance: async (payload) => {
    const { request, metadata } = payload;
    // Use the `request` and `metadata` received from Wix and
    // apply custom logic.
    return {
      // Return your response exactly as documented to integrate with Wix.
      // Return value example:
      balance: 100.00,
      currencyCode: metadata.currency || "ILS",
    };
  },
});
```

## Key Implementation Notes

1. **All three handlers required** - You must implement `redeem`, `getBalance`, and `_void`
2. **Transaction tracking** - The `redeem` handler must return a unique `transactionId` for tracking
3. **Balance as number** - Unlike other SPIs, balance values are numbers, not strings
4. **Void restores balance** - The `_void` handler should restore the redeemed amount back to the card
5. **Currency handling** - Use `metadata.currency` to get the site's currency setting
