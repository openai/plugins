# Dashboard Plugin Slots Reference

Slots are UI placeholders on dashboard pages of Wix first-party business apps. Each slot has a unique ID passed as the `extendsSlotId` scaffold param (written as `extends` in the generated `.extension.ts` file).

> **Authoritative slot list**: run `wix schema generate --type DASHBOARD_PLUGIN` for the live, complete `extendsSlotId` enum (each `anyOf` entry has the slot's human-readable title). This file documents per-slot parameters, dashboard paths, and use cases — content the schema does not carry.

**Key behaviors:**
- Some slots with the same ID appear on different pages. A plugin targeting such a slot is displayed on all pages containing it.
- Slots can host multiple plugins. Ordering varies by slot (see each entry).

---

## Wix Blog

### Overview Page

**Slot ID:** `65fae040-bbeb-4c62-ba14-e0ecb5e08661`

- **Dashboard path:** Blog > Overview
- **Location:** Top of page
- **Parameters:** None
- **Multi-plugin:** Vertical, newest at bottom
- **Use case:** Display blog analytics or quick-access management tools on the overview page.

### Categories Page

**Slot ID:** `0a208a9f-3b45-449c-ba8e-13a842ea5b84`

- **Dashboard path:** Blog > Categories
- **Location:** Top of page
- **Parameters:** None
- **Multi-plugin:** Vertical, newest at bottom
- **Use case:** Display category analytics or bulk category management tools.

### Posts Page

**Slot ID:** `46035d51-2ea9-4128-a216-1dba68664ffe`

- **Dashboard path:** Blog > Posts
- **Location:** Top of page
- **Parameters:** None
- **Multi-plugin:** Vertical, newest at bottom
- **Use case:** Display post analytics or quick-access post management tools.

### Tags Page

**Slot ID:** `0e336381-34a3-4f12-86f7-f98ab928f950`

- **Dashboard path:** Blog > Tags
- **Location:** Top of page
- **Parameters:** None
- **Multi-plugin:** Vertical, newest at bottom
- **Use case:** Display tag analytics or bulk tag management tools.

---

## Wix Bookings

### Staff Page

**Slot ID:** `261e84a2-31d0-4258-a035-10544d251108`

- **Dashboard path:** Settings > Booking Settings > Staff
- **Location:** Top of page
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `staffResourceId` | String | Staff resource ID |
  | `scheduleId` | String | Schedule ID |
  | `timezone` | String | Time zone |
- **Multi-plugin:** Vertical, newest at top
- **Use case:** Display staff availability analytics or performance metrics.

### Edit Staff Profile Page

**Slot ID:** `049fb0fe-cc4a-4e33-b0a9-d8cda8e7a79f`

- **Dashboard path:** Settings > Booking Settings > Staff > Edit or Add staff member
- **Location:** Top of page
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `staffId` | String | Staff member ID |
  | `staffResourceId` | String | Staff resource ID |
- **Multi-plugin:** Vertical, newest at top
- **Use case:** Extend the staff profile editing experience with custom functionality.

### Services Page

**Slot ID:** `78cc4a47-8f47-489b-acc2-fd9e4208c8bd`

- **Dashboard path:** Booking Calendar > Services
- **Location:** Between "Business setup recommendations" and "Service list"
- **Parameters:** None
- **Multi-plugin:** Horizontal, newest furthest left
- **Use case:** Display service analytics or integrate third-party booking tools.

### Calendar Page — Pre-Collect Payment Modal

**Slot ID:** `b92f0e25-535f-4bef-b130-8e5abc85b2fe`

- **Dashboard path:** Booking Calendar > Calendar
- **Location:** Custom modal displayed before the default Collect Payment modal
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `orderId` | String | Order ID |
  | `onSuccess()` | `() => Promise<void>` | Progresses to the next modal after successful order update |
  | `onCancel()` | `() => void` | Progresses to the next modal without changes |
  | `menuOption` | Object | Data for the selected menu item |
  | `menuOption.key` | String | `CHARGE_WITH_CREDIT_CARD`, `RECORD_ORDER_MANUAL_PAYMENT`, `CHARGE_WITH_INVOICE`, or `EXTENSION` |
  | `menuOption.componentId` | String | Component ID when `EXTENSION` key is triggered |
- **Multi-plugin:** Sequential modals, each appearing before the default modal
- **Use case:** Add items to an order such as additional services, notes, or booking fees like insurance.

> **Note:** This slot also appears on the Wix eCommerce Order Page.

### Booking List Page

**Slot ID:** `0f756363-1659-4929-b4ef-5ff2c458eb7d`

- **Dashboard path:** Booking Calendar > Booking List
- **Location:** Top of page
- **Parameters:** None
- **Multi-plugin:** Horizontal, newest furthest left
- **Use case:** Add custom widgets or tools at the top of the booking list.

---

## Wix eCommerce

### Order Page

**Slot ID:** `cb16162e-42aa-41bd-a644-dc570328c6cc`

- **Dashboard path:** Sales > Orders > Order
- **Location:** Right side of page, under the "Order info" (customer details) card
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `orderId` | String | Order ID |
  | `onOrderUpdate()` | `() => Promise<void>` | Callback that notifies the host page about an order update, prompting a UI refresh |
- **Multi-plugin:** Vertical, newest at bottom
- **Use case:** Display a map with the delivery courier's location for the order.

### Order Page — Pre-Collect Payment Modal

**Slot ID:** `b92f0e25-535f-4bef-b130-8e5abc85b2fe`

- **Dashboard path:** Sales > Orders > Order > Collect Payment
- **Location:** Custom modal displayed before the default Collect Payment modal
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `orderId` | String | Order ID |
  | `onSuccess()` | `() => Promise<void>` | Progresses to the next modal after successful order update |
  | `onCancel()` | `() => void` | Progresses to the next modal without changes |
  | `menuOption` | Object | Data for the selected menu item |
  | `menuOption.key` | String | `CHARGE_WITH_CREDIT_CARD`, `RECORD_ORDER_MANUAL_PAYMENT`, `CHARGE_WITH_INVOICE`, or `EXTENSION` |
  | `menuOption.componentId` | String | Component ID when `EXTENSION` key is triggered |
- **Multi-plugin:** Sequential modals, each appearing before the default modal
- **Use case:** Add items to an order such as additional items, notes, or extra fees.

> **Note:** This slot also appears on the Wix Bookings Calendar Page.

---

## Wix Events

### Event Page — Overview Tab

**Slot ID:** `d2c6965a-7d50-47a0-881a-beb184135df3`

- **Dashboard path:** Events > Published or Drafts > Event > Overview tab
- **Location:** Bottom of page
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `eventId` | String | Event ID |
- **Multi-plugin:** Vertical at bottom, newest at top
- **Use case:** Display earnings for each ticket type so the site owner can easily compare them.

### Event Page — Features Tab

**Slot ID:** `5566727b-e5a2-4a43-a26d-961aa4fe0898`

- **Dashboard path:** Events > Published or Drafts > Event > Features tab
- **Location:** Features grid (displayed as cards)
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `eventId` | String | Event ID |
- **Multi-plugin:** Cards next to each other in the features grid, newest at top
- **Use case:** Add an FAQ section to the event details.

### Event Page — Promotion Tab

**Slot ID:** `bc3b9b99-7a3a-4fb5-946f-078022277b6b`

- **Dashboard path:** Events > Published or Drafts > Event > Promotion tab
- **Location:** Bottom of page
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `eventId` | String | Event ID |
- **Multi-plugin:** Vertical at bottom, newest at top
- **Use case:** Send promotional emails to customers with abandoned checkouts.

### Event Page — Settings Tab

**Slot ID:** `c478b36b-7ce2-4564-afba-c2b0ca14bdea`

- **Dashboard path:** Events > Published or Drafts > Event > Settings tab
- **Location:** Bottom of page
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `eventId` | String | Event ID |
- **Multi-plugin:** Vertical at bottom, newest at top
- **Use case:** Set up event reminder emails to customers.

### Event Page — Tickets and Seating Tab

**Slot ID:** `80b95e22-26db-4063-a31f-76d4bb8797ba`

- **Dashboard path:** Events > Published or Drafts > Event > Tickets and Seating tab
- **Location:** Right side of page, below "Settings and discounts"
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `eventId` | String | Event ID |
- **Multi-plugin:** Vertical, newest at top
- **Use case:** Add a ticket sales scheduler to review current ticket sale status and set up start/end dates for all ticket sales.

---

## Wix Stores

### Products Page

**Slot ID:** `3ca518a6-8ae7-45aa-8cb9-afb3da945081`

- **Dashboard path:** Catalog > Store Products > Products
- **Location:** Top of page
- **Parameters:** None
- **Multi-plugin:** Horizontal, newest furthest right
- **Use case:** Add custom panels for external service integration or custom analytics tools.

### Inventory Page

**Slot ID:** `c9b19070-3e25-4f3d-9d27-4e0f74164835`

- **Dashboard path:** Catalog > Store Products > Inventory
- **Location:** Above inventory list
- **Parameters:** None
- **Multi-plugin:** Horizontal, newest furthest left
- **Use case:** Sum the total number of available items in each product category.

---

## Wix Restaurants

### Table Reservations Page

**Slot ID:** `7f71aacd-0cbf-4b73-9ea5-482e073ea237`

- **Dashboard path:** Table Reservations
- **Location:** Top of page
- **Parameters:**
  | Name | Type | Description |
  |------|------|-------------|
  | `currentReservationLocation` | Object | Object containing information about the reservation location |
  | `reservations` | Array | Array of objects with information about each reservation |
  | `requests` | Array | Array of objects with information about requested reservations |
- **Multi-plugin:** Horizontal, newest furthest right
- **Use case:** Display statistics for the currently selected reservation location.

---

## Wix CRM

No dashboard plugin slots available. CRM only exposes dashboard menu plugin slots.
