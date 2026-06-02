
# Wix Dashboard Page Builder

Dashboard pages appear in the site owner's Wix dashboard and enable site administrators to manage data, configure settings, and perform admin tasks.

## Scaffold

Use `wix generate --params` with all required fields:

```bash
wix generate --params '{"extensionType":"DASHBOARD_PAGE","title":"<title>","route":"<route>"}'
```

| Field | Constraint |
| --- | --- |
| `title` | Display name shown in the dashboard sidebar. |
| `route` | URL path segment (lowercase alphanumeric + hyphens). The page is served at `/dashboard/<route>`. The scaffold param is `route`; the builder file's runtime field is `routePath`. |

The CLI generates the folder, `page.tsx`, the builder file, the UUID, and the `src/extensions.ts` registration. After scaffolding, implement the page UI in the generated `page.tsx`.

## Capabilities

### Data Operations (Wix Data SDK)

See [Wix Data Reference](data-collection/WIX_DATA.md) in the Data Collection reference for complete documentation.

**Summary:**

- Read: `items.query('Collection').filter/sort.limit.find()` → `{ items, totalCount, hasNext }`
- Write: `items.insert | update | remove`. Ensure collection permissions allow the action

**Query methods:** `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `between`, `contains`, `startsWith`, `endsWith`, `hasSome`, `hasAll`, `isEmpty`, `isNotEmpty`, `and`, `or`, `not`, `ascending`, `descending`, `limit`, `skip`, `include`

### Dashboard APIs

See [Dashboard API Reference](dashboard-page/DASHBOARD_API.md) for complete documentation including all methods, page IDs, and examples.

**Key methods:**

- `dashboard.navigate()` - Navigate between dashboard pages
- `dashboard.observeState()` - Receive contextual state and environmental information
- `dashboard.showToast()` - Display toast notifications
- `dashboard.openModal()` - Open dashboard modal extensions (see [Dashboard Modal reference](DASHBOARD_MODAL.md))
- `dashboard.navigateBack()` - Navigate back to previous page
- `dashboard.getPageUrl()` - Get full URL for a dashboard page
- `dashboard.openMediaManager()` - Open Wix Media Manager
- `dashboard.onBeforeUnload()` - Register beforeunload handler
- `dashboard.addSitePlugin()` - Add site plugin to slots
- `dashboard.setPageTitle()` - Set page title in browser tab
- `dashboard.onLayerStateChange()` - Handle foreground/background state changes

**CRITICAL: Using Modals in Dashboard Pages**

When you need to display popup forms, confirmations, detail views, or any dialog overlays from a dashboard page, you **MUST** use dashboard modals, not regular React modals or WDS Modal components.

- **Use dashboard modals** for: edit forms, delete confirmations, detail views, settings dialogs, any popup content
- **Do NOT use** WDS `Modal` component or custom React modal implementations
- **See [Dashboard Modal reference](DASHBOARD_MODAL.md)** for complete implementation guide

Dashboard modals are opened using `dashboard.openModal()` and provide proper integration with the dashboard lifecycle, state management, and navigation.

**Ecom Navigation:** See [Ecom Navigation Reference](dashboard-page/ECOM_NAVIGATION.md) for ecom-specific navigation helpers.

### Embedded Script Configuration API

When building a dashboard page to configure an embedded script, see [Dynamic Parameters Reference](dashboard-page/DYNAMIC_PARAMETERS.md) for complete implementation guide.

**Key points:**

- Use `embeddedScripts` from `@wix/app-management`
- Parameters are returned as strings - handle type conversions when loading
- All parameters must be saved as strings (convert booleans/numbers to strings)
- Use `withProviders` wrapper when dynamic parameters are present

## Optional builder fields

The CLI scaffolds the builder with `id`, `title`, `routePath`, and `component`. To customize sidebar placement and routing, edit the generated builder file to set:

- `additionalRoutes` (string[]): extra routes leading to this page.
- `sidebar.disabled` (boolean, default false): hide page from sidebar.
- `sidebar.priority` (number): sidebar ordering; lower is higher priority.
- `sidebar.whenActive.selectedPageId` (string): which page appears selected when this page is active.
- `sidebar.whenActive.hideSidebar` (boolean): hide sidebar when this page is active.

## Examples

### Data Management Table

**Request:** "Create a dashboard page to manage blog posts"

**Output:** Page with table displaying posts, search toolbar, add/edit/delete actions, empty state.

### Settings Form

**Request:** "Build a settings page for notification preferences"

**Output:** Page with form fields, save button with toast confirmation, unsaved changes warning.

### Order Management

**Request:** "Create an admin panel for customer orders"

**Output:** Page with orders table, status badges, filters, detail dashboard modal (using [Dashboard Modal reference](DASHBOARD_MODAL.md)), status update actions.

### Embedded Script Configuration

**Request:** "Create a settings page for the coupon popup embedded script"

**Output:** Page with form fields for popup headline, coupon code, minimum cart value, and enable toggle. Uses `embeddedScripts` API to load/save parameters.

```typescript
// Key pattern for embedded script configuration pages
import { embeddedScripts } from "@wix/app-management";

// Load on mount
useEffect(() => {
  const load = async () => {
    const script = await embeddedScripts.getEmbeddedScript();
    const data = script.parameters || {};
    setOptions({
      headline: data.headline || "Default",
      enabled: data.enabled === "true",
      threshold: Number(data.threshold) || 0,
    });
  };
  load();
}, []);

// Save handler
const handleSave = async () => {
  await embeddedScripts.embedScript({
    parameters: {
      headline: options.headline,
      enabled: String(options.enabled),
      threshold: String(options.threshold),
    },
  });
  dashboard.showToast({ message: "Saved!", type: "success" });
};
```


## API Spec Support

When an API specification is provided, you can make API calls to those endpoints. See [API Spec Reference](dashboard-page/API_SPEC.md) for details on how to use API specs in dashboard pages.


## Layout Guidelines

Layout determines how users interact with your dashboard content. It establishes the structure, hierarchy, and rhythm of your dashboard page, contributing to the overall coherence and user experience. By making mindful and calculated choices in how you organize your content, users can move around more smoothly, saving time and frustration when completing tasks.

### Design Principles

To create dashboard pages optimized for user experience, follow these design principles:

1. **Consistent:** Maintain repetitive layouts and content patterns for intuitive and easy-to-read pages.
2. **Inclusive:** Create layouts and content that adapt well to various screen sizes.
3. **Balanced:** Emphasize the priority of regions and content elements through deliberate management of size and white space.
4. **Connected:** Minimize the distance between related regions or content elements to enhance cohesion and navigation.


### Screen Size

Dashboard pages are designed to accommodate various screen sizes rather than being tailored to one specific resolution. The primary content should be at the top of the page to ensure users immediately understand the purpose of the page.

> **Note:** Content displayed in the top 600 pixels of the page will be visible for the majority of users.


### Base Unit

The base unit establishes the increment by which all elements and measurements are multiplied. This practice ensures consistency in the spacing and sizing of design elements.

> **Note:** The design system is based on a 6px unit.

The layout grid, spacing tokens, and nearly all visual elements and sizes adhere to multiples of six (6, 12, 18, 24, etc.), with only occasional exceptions.

| TOKEN | SIZE | USE FOR |
|-------|------|---------|
| SP1 | 6px | Spacing between components |
| SP2 | 12px | Spacing between components |
| SP3 | 18px | Spacing between components |
| SP4 | 24px | Spacing between components, layout spacing |
| SP5 | 30px | Layout spacing |
| SP6 | 36px | Layout spacing |
| SP7 | 42px | Layout spacing |
| SP8 | 48px | Layout spacing |
| SP10 | 54px | Layout spacing |
| SP11 | 60px | Layout spacing |


### Layout Structure

To best design the layout for your app, understand:

1. The core frame of the app (Application frame)
2. The placement and alignment of each segment within the grid layout (Grid layout)
3. The content to appear in the grid (Common layouts)

#### Application Frame

The dashboard app frame is used by the majority of Wix applications settings. Dashboard pages consist of 4 areas:

| AREA | USAGE |
|------|-------|
| 1. Global navigation (top bar) | General navigation at the top of a page which allows users to navigate between different environments. Full width container with a fixed height of 48px. |
| 2. Sidebar navigation | Local navigation of an environment. Container with a fixed width of 228px. |
| 3. Content area | Page content area with a width that's adaptive to screen size. |
| 4. Side panel (optional) | An optional panel that shows additional actions or content associated with the content of a page. Fixed width of 420px. Can either overlay the main content area or push it from the right side. |

**Side Panel Guidelines:**
- Let the side panel overlay main content when it contains supplementary actions or settings, such as data filters
- Push main content with the side panel when users must see the full context to continue


#### Grid Layout

The system uses a fluid grid layout with a fixed maximum width. It uses columns that scale and resize the content accordingly.

The grid is constructed from 3 elements:
- **Columns** - The design system uses a 12-column grid. Column width is fluid and changes according to the page width.
- **Gutters** - The gaps between the columns. Gutter width has a fixed value of 24px.
- **Margins** - By default, a page's content area has 48px side margins and a 48px bottom margin.

**Grid Specifications:**
- Minimum content area width: 864 pixels (each grid column is 50px wide)
- Maximum content area width: 1248px (each column is 82px wide)
- Wider screens maintain 1248px content width with side margins stretching to center content
- Use 24px gap between cards both vertically and horizontally


### Common Layouts

Page layouts can be divided by intention into the following types:

#### 1. Form Layouts

Forms are pages that allow users to fill in data or edit existing data. Two variations:

- **2/3 layout with optional sidebar (8/4 column split)** - Provides flexibility to expose primary and secondary content at the same time
- **Full width (12 columns)** - Supports advanced product needs with complex structures

Both form page layouts include mandatory **Save** and **Cancel** actions in the header and footer areas.

**2/3 Layout Best Practices:**
- Use to expose primary and secondary content at the same time
- Keep the form easy to scan and comprehend
- Display a live content preview on the side (widget can be sticky)
- Use 8 columns for forms to keep text lines and input fields narrow for quicker reading
- Bring actions closer to related titles (e.g., toggle switches near settings)

**Full Width Layout Best Practices:**
- Use when a form includes complex structures such as tables
- Use for list items that contain many data columns

**Combining Layouts:**
- Avoid coast-to-coast inputs; keep inputs to 2/3 width of a card, or lay them out in two columns
- Use white space on the right side for content preview
- Use full width for tables with many columns and dividers that separate sections

> **Note:** A column is easy to read if it is wide enough to accommodate an average of 10 words per line.

#### 2. Display Layouts

Display pages showcase data or content without accepting input from users. They can contain minor actions such as data filtering.

**List (Table):**
- Tables display large data sets and provide users with a quick overview
- Use a 12-column layout for tables
- Enables users to manipulate and act on a data set

**List (Grid) Options:**
- 2 columns (6/6 split) - For items with lengthy descriptions
- 3 columns (4/4/4 split) - For visual items with multiple data types
- 4 columns (3/3/3/3 split) - For user-generated galleries and collections, reveals up to 50% more content above the fold than 4/4/4
- Custom - For mixed content needs

**Grid Selection Considerations:**
- Total amount of items to show
- Content to display in each list item
- What objects the list items reflect (match physical shapes when applicable)

**Dashboards:**
Display different types of data on a specific topic using a combination grid.

Column span recommendations:
- **3 or 4 columns** - For list items, previews, marketing, statistics, and charts
- **12 columns (full width)** - For tables and marketing content
- **8 columns** - For lists, tables with few data columns, setup wizards, and charts
- **6 columns** - For lists, tables with few data columns, and statistics

**Empty States:**
- Use full width layout for empty state of a page
- Indicates feature/product has no data yet, all data cleared, or not set up yet
- Include clear CTA indicating what to do to fill the page
- Can combine with other layout elements such as tabs, statistics widgets, or marketing cards

#### 3. Marketing Layouts

Marketing pages promote new products that site owners are not aware of yet. Built using the `<MarketingPageLayout/>` component split into 2 columns:

1. Promo messaging
2. Visual representation of product and features

Optional footer area can display features or testimonials list.

#### 4. Wizard Layouts

Wizard pages guide users through setting up a product or feature. They split complex forms into steps for easier completion.

**Entry Points:**
- A marketing page
- A marketing card
- The primary action of a page
- An empty state

> **Note:** Wizards must have a final destination. After completing all steps, users should end up on a relevant page: a dashboard, a details page, or any other relevant location.


### Related WDS Components

- `<Page />` - Main page wrapper
- `<Layout />` - Grid layout container
- `<MarketingPageLayout />` - Marketing page wrapper
- `<Card />` - Content container with 24px gaps between cards
