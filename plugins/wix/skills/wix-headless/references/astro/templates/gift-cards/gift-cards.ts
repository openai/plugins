// Wix Gift Card app — eGift Card template fetch.
//
// The dashboard's Catalog → Gift Cards screen configures a single eGift Card
// "product" with preset denominations. That product is queryable via a public
// REST endpoint (POST /gift-cards/v1/gift-card-products/query). The JS SDK
// auto-package @wix/auto_sdk_ecom_gift-vouchers only exposes redemption
// methods (getGiftCard / redeemGiftCard / voidTransaction), so we hit REST
// directly using @wix/essentials httpClient.fetchWithAuth.
//
// The buy flow uses the standard cart: currentCart.addToCurrentCart with a
// catalogReference whose appId is WIX_GIFT_CARDS_APP_ID below. After payment,
// Wix's gift-card backend automatically issues a redeemable gift card with
// source: "ORDER" and emails the recipient — no follow-up API call needed.
//
// The appId is observable on installed sites and stable across sites. If Wix
// ever rotates it, update this constant; both the runtime probe and the buy
// flow will fail together (and the page hides gracefully — same as "app
// uninstalled").

import { httpClient } from "@wix/essentials";

export const WIX_GIFT_CARDS_APP_ID = "d80111c5-a0f4-47a8-b63a-65b54d774a27";

export interface GiftCardImage {
  id?: string;
  url?: string;
  height?: number;
  width?: number;
  altText?: string;
}

export interface GiftCardPresetVariant {
  id: string;
  price: { amount: string; formattedAmount: string; convertedAmount?: string; formattedConvertedAmount?: string };
  value: { amount: string; formattedAmount: string; convertedAmount?: string; formattedConvertedAmount?: string };
}

export interface GiftCardProduct {
  id: string;
  revision?: string;
  name: string;
  description: string;
  image?: GiftCardImage;
  expirationType?: string;
  presetVariants: GiftCardPresetVariant[];
}

const ENDPOINT = "https://www.wixapis.com/gift-cards/v1/gift-card-products/query";

// Module-level memoization. Navigation, the home teaser, and /gift-cards all
// call getGiftCardProduct() in the same request — coalesce them into one
// fetch by holding the in-flight promise at module scope.
let cached: Promise<GiftCardProduct | null> | null = null;

export async function getGiftCardProduct(): Promise<GiftCardProduct | null> {
  if (cached) return cached;
  cached = (async () => {
    try {
      const res = await httpClient.fetchWithAuth(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: { paging: { limit: 1 } } }),
      });
      if (!res.ok) return null;
      const data = await res.json();
      const products = data?.giftCardProducts;
      if (!Array.isArray(products) || products.length === 0) return null;
      return products[0] as GiftCardProduct;
    } catch (err) {
      console.error("[gift-cards] queryGiftCardProducts failed:", err);
      return null;
    }
  })();
  return cached;
}
