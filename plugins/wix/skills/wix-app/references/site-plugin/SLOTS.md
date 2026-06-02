# Site Plugin Slots Reference

This reference provides detailed information about all available slots for site plugins across Wix business solutions.

> **Authoritative slot list**: run `wix schema generate --type SITE_PLUGIN` for the live, complete `slotId` enum (each `anyOf` entry has the slot's human-readable title). This file documents per-slot runtime APIs, App Definition IDs, UX notes, and design constraints — content the schema does not carry.

## Host Apps

| Wix App           | App Definition ID                      | Supported Pages/Widgets                                       |
| ----------------- | -------------------------------------- | ------------------------------------------------------------- |
| Wix Stores (Old)  | `1380b703-ce81-ff05-f115-39571d94dfcd` | Product Page (Old Version), Category Page, Shop Page, Gallery Widget |
| Wix Stores (New)  | `a0c68605-c2e7-4c8d-9ea1-767f9770e087` | Product Page (New Version)                                    |
| Wix eCommerce     | —                                      | Checkout Page, Side Cart                                      |
| Wix Bookings      | `13d21c63-b5ec-5912-8397-c3a5ddb27a97` | Service Page                                                  |
| Wix Events        | `140603ad-af8d-84a5-2c80-a0f60cb47351` | Event Details Page                                            |
| Wix Blog          | `14bcded7-0066-7c35-14d7-466cb3f09103` | Post Page                                                     |
| Wix Restaurants   | `13e8d036-5516-6104-b456-c8466db39542` | —                                                             |

---

## Wix Stores Slots

### Product Page (New Version)

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `a0c68605-c2e7-4c8d-9ea1-767f9770e087`   |
| `widgetId`        | `6a25b678-53ec-4b37-a190-65fcd1ca1a63`   |

**Note:** If using the `product-page-media-1` slot, it may overlap with the thumbnail images on the left side in desktop view. Consider offering settings in your app to control the left padding. ([Wix docs reference](https://dev.wix.com/docs/build-apps/develop-your-app/extensions/site-extensions/site-plugins/supported-wix-app-pages/wix-stores/wix-stores-product-page))

**Plugin API Properties:**
- `productId` (string) - The ID of the product on the product page
- `selectedVariantId` (string) - The ID of the selected product variant. Only available after the site visitor picks all required product choices. Until all required choices are selected, this is `undefined`
- `selectedChoices` (object) - An object containing all choices the site visitor picks. Each key is an option name and each value is the selected option (e.g., `{ color: "green", size: "large" }`)
- `quantity` (number) - The number of product items the site visitor wants to buy
- `customText` (string[]) - An array of text values entered by the site visitor in custom text fields (e.g., personalization). Each entry corresponds to a different custom text field on the product page

### Product Page (Old Version)

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `1380b703-ce81-ff05-f115-39571d94dfcd`   |
| `widgetId`        | `13a94f09-2766-3c40-4a32-8edb5acdd8bc`   |

**Note:** Available slots vary by layout (Classic, Simple, Sleek, Spotlight, Stunning). Check which Wix Stores version is installed before building plugins, as slots differ between versions. Your app should include placements for both versions for maximum compatibility.

**Plugin API Properties:** Same as New Version above.

### Category Page

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `1380b703-ce81-ff05-f115-39571d94dfcd`   |
| `widgetId`        | `bda15dc1-816d-4ff3-8dcb-1172d5343cce`  |

**Plugin API Properties:**
- `categoryId` (string) - The ID of the category

### Shop Page

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `1380b703-ce81-ff05-f115-39571d94dfcd`   |
| `widgetId`        | `1380bba0-253e-a800-a235-88821cf3f8a4`   |

**Plugin API Properties:**
- `categoryId` (string) - The category ID

### Gallery Widget

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `1380b703-ce81-ff05-f115-39571d94dfcd`   |
| `widgetId`        | `13afb094-84f9-739f-44fd-78d036adb028`   |

**Plugin API Properties:**
- `categoryId` (string) - The category ID

**Note:** When selecting slots, use the same slot across Shop page, Gallery widget, and Category page to ensure compatibility across different Wix site setups.

---

## Wix eCommerce Slots

### Checkout Page

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `1380b703-ce81-ff05-f115-39571d94dfcd`   |
| `widgetId`        | `14fd5970-8072-c276-1246-058b79e70c1a`   |

**Note:** Some checkout plugins may not support automatic addition upon installation. Create a dashboard page to manage your site plugin.

**Checkout Plugin API Properties:**
- `checkoutId` (string) - ID of the current checkout process
- `stepId` (string) - Current step: `contact-details`, `delivery-method`, `payment-and-billing`, or `place-order`
- `checkoutUpdatedDate` (string) - When checkout was last updated

**Checkout Plugin API Functions:**
- `onRefreshCheckout(callback: () => void)` - An event handler that accepts a callback function invoked whenever the checkout needs to be refreshed

**Note:** The delivery-method step slot uses a **different API** — see Delivery Step Options Slot API below. Check the schema for its exact `slotId`.

#### Delivery Step Options Slot API

The delivery-method step slot has its own API that is different from the other checkout slots.

**Properties:**
- `checkoutId` (string) - ID of the current checkout process
- `checkoutUpdatedDate` (string) - When checkout was last updated
- `selectedDeliveryOptionCarrierId` (string) - The ID of the carrier for the selected delivery option
- `selectedDeliveryOptionId` (string) - The ID of the selected delivery option
- `deliveryStepState` (string) - The current state of the delivery step. Possible values: `open` or `summary`

**Functions:**
- `onRefreshCheckout(callback: () => Promise)` - Event handler invoked whenever the checkout needs to be refreshed
- `disableContinueButton(callback: (isDisabled: boolean) => void)` - Event handler to control the checkout's continue button. Call with `true` to disable or `false` to enable

### Side Cart

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `1380b703-ce81-ff05-f115-39571d94dfcd`   |
| `widgetId`        | `49dbb2d9-d9e5-4605-a147-e926605bf164`  |

**Note:** Some side cart plugins may not support automatic addition upon installation. Create a dashboard page to manage your site plugin.

**Design Guidelines:**

The Side Cart uses a `4px` baseline grid. Don't add extra spacing around your plugin — the slot handles spacing automatically.

| Slot                                  | Recommended Height | Max Height |
| ------------------------------------- | ------------------ | ---------- |
| `side-cart:header:after-1`            | `30px`             | `70px`     |
| `side-cart:line-items:after-1`        | `50px`             | `150px`    |
| `side-cart:customer-input:after-1`    | `24px`             | `150px`    |
| `side-cart:footer:actions:before-1`   | `50px`             | `70px`     |
| `side-cart:footer:actions:after-1`    | `50px`             | `70px`     |

---

## Wix Blog Slots

### Post Page

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `14bcded7-0066-7c35-14d7-466cb3f09103`   |
| `widgetId`        | `211b5287-14e2-4690-bb71-525908938c81`   |

**Plugin API Properties:**
- `postId` (string) - The ID of the current post

---

## Wix Bookings Slots

### Service Page

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `13d21c63-b5ec-5912-8397-c3a5ddb27a97`   |
| `widgetId`        | `a91a0543-d4bd-4e6b-b315-9410aa27bcde`  |

The Service Page can host a single plugin that users are free to reposition within the page by reordering the Service Page sections.

**Plugin API Properties:**
- `bookingsServiceId` (string) - The ID of the Wix Bookings service currently applied on the plugin's host

---

## Wix Events Slots

### Event Details Page

| Property          | Value                                    |
| ----------------- | ---------------------------------------- |
| `appDefinitionId` | `140603ad-af8d-84a5-2c80-a0f60cb47351`   |
| `widgetId`        | `14d2abc2-5350-6322-487d-8c16ff833c8a`  |

**Plugin API Properties:**
- `eventId` (string) - The ID of the event currently applied on the plugin's host

---

## Multiple Placements

You can configure a single plugin to appear in multiple slots:

```typescript
placements: [
  {
    appDefinitionId: '1380b703-ce81-ff05-f115-39571d94dfcd',
    widgetId: '13a94f09-2766-3c40-4a32-8edb5acdd8bc',
    slotId: 'product-page-details-2',
  },
  {
    appDefinitionId: 'a0c68605-c2e7-4c8d-9ea1-767f9770e087',
    widgetId: '6a25b678-53ec-4b37-a190-65fcd1ca1a63',
    slotId: 'product-page-details-2',
  },
]
```

**Note:** If you have multiple placements for slots on a single page, the plugin will be added to the first available slot according to the order you defined. If that slot is occupied, it will be placed in the next available slot. If there are no available slots, it will not be placed. Users may manually move the plugin to their desired location in the editor.

## Slot Limitations

- Each slot has specific size constraints defined by the host app
- Some slots may only be available in certain editor types (Wix Editor, Editor X, Wix Studio)
- Multiple plugins can occupy the same slot, displayed next to each other and ordered by creation date
