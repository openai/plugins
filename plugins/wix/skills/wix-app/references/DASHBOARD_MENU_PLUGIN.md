
# Wix Dashboard Menu Plugin Builder

Dashboard menu plugins are menu items that integrate into predefined **menu slots** on dashboard pages managed by Wix first-party business apps (Wix Stores, Wix Bookings, Wix Blog, Wix eCommerce, Wix Events, Wix CRM, Wix Restaurants).

When clicked, a dashboard menu plugin either **navigates to a dashboard page** or **opens a dashboard modal**. They are configuration-only extensions — they do NOT have a React component file.

## Scaffold

Use `wix generate --params` with `extensionType: DASHBOARD_MENU_PLUGIN`. `extendsSlotId` comes from the [Slot Lookup Table](#slot-lookup-table) below; for the authoritative list of all supported `extendsSlotId` values, run `wix schema generate --type DASHBOARD_MENU_PLUGIN`. `action` must contain **exactly one** of `pageId` or `modalId`, referencing the `id` of an existing Dashboard Page or Dashboard Modal extension in the project. The CLI generates the folder, the configuration file, the UUID, and the `src/extensions.ts` registration.

## Architecture

Dashboard menu plugins operate as **click-to-action** menu items. They:

1. Appear as labeled items with an icon in a menu slot on a Wix app's dashboard page
2. When clicked, perform one of two actions:
   - **Navigate to a dashboard page** — redirects to a specified dashboard page
   - **Open a dashboard modal** — displays a specified dashboard modal

## The `extendsSlotId` Field

Specifies which dashboard menu slot hosts your menu plugin. Each Wix business app exposes menu slots on its dashboard pages. You must provide the exact slot ID.

**Important:** Some slots with the same ID appear on different pages within the dashboard. If you create a menu plugin for a slot that exists on multiple pages, the menu plugin is displayed on all of those pages.

For the complete list of available menu slot IDs, see the [Slot Lookup Table](#slot-lookup-table) below. Read only the vertical file that matches the user's request.

## The `action` Field

The `action` field determines what happens when the user clicks the menu item. Configure **exactly one** of the following:

| Action | Scaffold param | Value |
|---|---|---|
| Navigate to a dashboard page | `{ "action": { "pageId": "<PAGE_ID>" } }` | `pageId` is the `id` (UUID) of an existing dashboard page extension. |
| Open a dashboard modal | `{ "action": { "modalId": "<MODAL_ID>" } }` | `modalId` is the `id` (UUID) of an existing dashboard modal extension. |

## Icon Selection

The generated builder file has an `iconKey` field. It must be a valid icon name from the Wix Design System icon set (`@wix/wix-ui-icons-common`). Use the `wix-design-system` skill to look up available icon names and update the generated builder file accordingly.

## Dashboard-Menu-Plugin-specific Conventions

- A dashboard menu plugin does NOT have a React component — it is configuration-only.
- Do NOT confuse dashboard menu plugins with dashboard plugins — they are different extension types.

## Slot Lookup Table

Identify which Wix app the user is targeting, then read **only** the corresponding reference file for slot IDs.

| Wix App | Keywords | Slot Reference |
|---------|----------|----------------|
| Wix Blog | blog, posts, categories, tags, drafts, scheduled | [blog-slots.md](dashboard-menu-plugin/blog-slots.md) |
| Wix Bookings | bookings, calendar, services, staff, booking list | [bookings-slots.md](dashboard-menu-plugin/bookings-slots.md) |
| Wix CRM | CRM, contacts | [crm-slots.md](dashboard-menu-plugin/crm-slots.md) |
| Wix eCommerce | ecommerce, orders, payment | [ecommerce-slots.md](dashboard-menu-plugin/ecommerce-slots.md) |
| Wix Events | events, guests, RSVP, ticketed | [events-slots.md](dashboard-menu-plugin/events-slots.md) |
| Wix Stores | stores, products, inventory, catalog | [stores-slots.md](dashboard-menu-plugin/stores-slots.md) |
| Wix Restaurants | restaurants, reservations, online orders, menus | [restaurants-slots.md](dashboard-menu-plugin/restaurants-slots.md) |

