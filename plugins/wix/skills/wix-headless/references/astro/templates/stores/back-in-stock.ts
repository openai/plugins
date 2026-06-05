// SSR-only probe for the Wix back-in-stock service. Returns true when the
// dashboard's "Start Collecting Requests" toggle is on for Wix Stores;
// `[slug].astro` passes the boolean through to ProductPurchase, which
// renders the subscribe form in OOS branches when the prop is true.
//
// Wix's back-in-stock service identifies the Stores integration by the
// Stores SUB-PAGE registration id (1380b703-…), NOT by the install/catalog
// appId (215238eb-…) that the public docs and other catalog endpoints use.
// Against a Catalog-V3 site the request-collection endpoints behave as follows:
//   - PUT /settings returned `collectionStates: [{appId: "1380b703-…",
//     collectingRequests: true}]`.
//   - POST /settings/start-collecting with `215238eb-…` returned
//     428 NOT_SUPPORTED_APP_DEF_ID.
//   - POST /back-in-stock-notification-requests with catalogReference.appId
//     `215238eb-…` returned 428 REQUEST_COLLECTION_DISABLED.
//   - POST /back-in-stock-notification-requests with catalogReference.appId
//     `1380b703-…` succeeded and returned a RECEIVED request.
// Treat 1380b703-… as the canonical id for this service. The install/
// catalog id 215238eb-… is exported in case other endpoints need it.
//
// The matching subscribe call goes through @wix/ecom's
// backInStockNotifications.createBackInStockNotificationRequest from the
// React island directly — visitor scope is enough, no client-side
// elevation, no Astro API route. The cloud-provider-fetch-adapter that
// ships with the Wix scaffold returns 403 to the browser on app-defined
// POST routes; the SDK call avoids that surface entirely. So this file
// exports only the SSR probe — there's no REQUESTS_URL constant.

import { auth, httpClient } from "@wix/essentials";

export const WIX_STORES_BACK_IN_STOCK_APP_ID =
  "1380b703-ce81-ff05-f115-39571d94dfcd";
export const WIX_STORES_INSTALL_APP_ID =
  "215238eb-22a5-4c36-9e7b-e7c08025e04e";

export const SETTINGS_URL =
  "https://www.wixapis.com/back-in-stock-service/v1/back-in-stock-notification-requests/settings";

interface BackInStockCollectionState {
  appId?: string;
  collectingRequests?: boolean;
}

let cached: Promise<boolean> | null = null;

export async function getBackInStockEnabled(): Promise<boolean> {
  if (cached) return cached;
  cached = (async () => {
    try {
      const elevated = auth.elevate(httpClient.fetchWithAuth);
      const res = await elevated(SETTINGS_URL, { method: "PUT" });
      if (!res.ok) return false;
      const data = await res.json();
      const states: BackInStockCollectionState[] =
        data?.settings?.collectionStates ?? [];
      return states.some(
        (s) =>
          s.appId === WIX_STORES_BACK_IN_STOCK_APP_ID &&
          s.collectingRequests === true,
      );
    } catch (err) {
      console.error("[back-in-stock] getSettings probe failed:", err);
      return false;
    }
  })();
  return cached;
}
