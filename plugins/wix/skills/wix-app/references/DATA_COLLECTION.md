
# Wix Data Collection Builder

Creates CMS data collections for Wix CLI apps. The data collections extension allows your app to automatically create CMS collections when it's installed on a site. Collections store structured data that can be accessed from dashboard pages, site pages, backend code, and external applications.

**Important:** This extension automatically enables the site's code editor, which is required for the Wix Data APIs to work. Without this extension, apps using Data APIs would need the Wix user to manually enable the code editor on their site, which isn't guaranteed. With the data collections extension, your app can reliably use Data APIs to read and write data in the collections.

## Scaffold

Use `wix generate --params` with `extensionType: DATA_COLLECTION`. The only other param is `collectionName` (1-36 chars: letters, numbers, underscores, hyphens) — fields, permissions, displayName overrides, etc. are all edited after scaffolding in the generated file.

The CLI manages a shared aggregator file (`data-collections.extension.ts`) that imports every collection file and registers them in one `extensions.dataCollections({...})` builder. The aggregator and `src/extensions.ts` are updated automatically — don't edit them manually.

## App Namespace Handling

**App namespace is REQUIRED** for data collections to work. The namespace scopes your collection IDs to prevent conflicts between apps.

### Implementation Behavior

**If app namespace is provided in the prompt:**
- Use it in all code examples: `<actual-namespace>/collection-suffix`

**If app namespace is NOT provided:**
- Use the placeholder `<app-namespace>` in all code examples: `<app-namespace>/collection-suffix`
- Add to Manual Action Items: "Replace `<app-namespace>` with your actual app namespace from Wix Dev Center"

### Collection ID Format

- **In extension definition (`idSuffix`):** Use just the suffix, e.g., `"products"`. The CLI uses `collectionName` from the scaffold params as the `idSuffix` for the generated entry.
- **In API calls:** Use the full scoped ID: `"<app-namespace>/products"` — MUST match `idSuffix` exactly (case-sensitive, no camelCase/PascalCase transformation)
- **In `referencedCollectionId`:** Use the `idSuffix` only (not the full scoped ID) — the system resolves it automatically
- Example: If `idSuffix` is `"product-recommendations"`, API calls use `"<app-namespace>/product-recommendations"` NOT `"<app-namespace>/productRecommendations"`

## Collection File Shape

The CLI scaffolds `<CollectionName>.ts` as a `satisfies DataCollection` default export. The scaffolded `fields` and `dataPermissions` are placeholders — replace them with your real schema, and set permissions per the [Context-Based Permission Rules](#context-based-permission-rules) before shipping.

```typescript
import type { DataCollection } from '@wix/astro/builders';

export const collectionIdSuffix = '<CollectionName>';

export default {
  idSuffix: collectionIdSuffix,
  displayName: '<CollectionName>',
  displayField: 'title',            // Field shown when referencing items
  fields: [ /* field definitions */ ],
  dataPermissions: { /* itemRead, itemInsert, itemUpdate, itemRemove */ },
  indexes: [],
  initialData: [],
} satisfies DataCollection;
```

## Field Types

| Type              | Description                      | Use Case               |
| ----------------- | -------------------------------- | ---------------------- |
| `TEXT`            | Single-line text                 | Names, titles          |
| `RICH_TEXT`       | Formatted HTML text              | Blog content           |
| `RICH_CONTENT`    | Rich content with embedded media | Complex blog posts     |
| `NUMBER`          | Decimal numbers                  | Prices, quantities     |
| `BOOLEAN`         | True/false                       | Toggles, flags         |
| `DATE`            | Date only                        | Birthdays              |
| `DATETIME`        | Date with time                   | Timestamps             |
| `TIME`            | Time only                        | Schedules              |
| `IMAGE`           | Single image                     | Thumbnails             |
| `DOCUMENT`        | File attachment                  | PDFs                   |
| `VIDEO`           | Video file                       | Media                  |
| `AUDIO`           | Audio file                       | Podcasts               |
| `MEDIA_GALLERY`   | Multiple media                   | Galleries              |
| `REFERENCE`       | Link to one item                 | Author → User          |
| `MULTI_REFERENCE` | Link to many items               | Post → Tags            |
| `ADDRESS`         | Structured address               | Locations              |
| `URL`             | URL validation                   | Links                  |
| `PAGE_LINK`       | Link to Wix page                 | Internal navigation    |
| `LANGUAGE`        | Language code                    | Multi-language content |
| `OBJECT`          | JSON object                      | Flexible data          |
| `ARRAY`           | Array of values                  | Generic arrays         |
| `ARRAY_STRING`    | Array of strings                 | Tags list              |
| `ARRAY_DOCUMENT`  | Array of documents               | File collections       |
| `ANY`             | Any type                         | Most flexible          |

**CRITICAL: OBJECT fields require `objectOptions`.** When using `type: "OBJECT"`, you MUST include the `objectOptions` property — the API will reject OBJECT fields without it. Use an empty object `{}` if you don't need schema validation:

```json
{
  "key": "settings",
  "displayName": "Settings",
  "type": "OBJECT",
  "objectOptions": {}
}
```

For structured objects, define nested fields inside `objectOptions.fields`:

```json
{
  "key": "triggerRules",
  "displayName": "Trigger Rules",
  "type": "OBJECT",
  "objectOptions": {
    "fields": [
      { "key": "url", "displayName": "URL Condition", "type": "TEXT" },
      {
        "key": "scrollDepth",
        "displayName": "Scroll Depth %",
        "type": "NUMBER"
      },
      { "key": "dateStart", "displayName": "Start Date", "type": "DATE" }
    ]
  }
}
```

## Field Properties

```ts
{
  key: 'email',                         // required, lowerCamelCase ASCII
  type: 'TEXT',                         // required, see Field Types above
  displayName: 'Email Address',         // optional, CMS label
  description: "User's primary email",  // optional, help text
  encrypted: false,                     // optional, encrypt value at rest
  // arrayOptions / objectOptions / referenceOptions / multiReferenceOptions
  // only when type is ARRAY / OBJECT / REFERENCE / MULTI_REFERENCE
}
```

| Property      | Required | Description                          |
| ------------- | -------- | ------------------------------------ |
| `key`         | yes      | Field identifier (lowerCamelCase)    |
| `type`        | yes      | Field data type (see Field Types)    |
| `displayName` | no       | Label shown in CMS                   |
| `description` | no       | Help text                            |
| `encrypted`   | no       | Encrypt value at rest                |

**There is no field-level `required`, `defaultValue`, or `unique`.** The `DevCenterDataCollectionField` type does not accept them and TypeScript will reject the build. Use these alternatives instead:

- **Required values:** Validate in the dashboard form and/or service-plugin handler before inserting. Do not rely on the collection schema to enforce presence.
- **Defaults:** Set defaults in the insert path (dashboard handler, service plugin) or via the collection's `initialData` for seeded rows.
- **Uniqueness:** Declare a unique index in the collection's `indexes` array (see [Indexes](#indexes)). Uniqueness is an index-level concern, not a field-level one.

## Indexes

The `indexes` array on the collection accepts entries shaped like:

```ts
indexes: [
  {
    fields: [{ path: 'email', order: 'ASC' }],  // order is optional: 'ASC' | 'DESC'
    unique: true,                                // optional, enforces uniqueness across items
  },
  {
    fields: [
      { path: 'category' },
      { path: '_createdDate', order: 'DESC' },
    ],
  },
],
```

| Property        | Required | Description                                            |
| --------------- | -------- | ------------------------------------------------------ |
| `fields`        | yes      | One or more `{ path, order? }` entries (composite index when more than one) |
| `fields[].path` | yes      | Field key to index                                     |
| `fields[].order`| no       | `'ASC'` (default) or `'DESC'`                          |
| `unique`        | no       | Enforce uniqueness on the indexed field(s)             |

Leave `indexes: []` when no custom indexing is needed; the `_id` index is created automatically.

## Naming Conventions

- **Field keys:** `lowerCamelCase`, ASCII only (e.g., `productName`, `isActive`, `createdAt`)
- **Collection IDs (`idSuffix`):** `lower-kebab-case` or `lower_underscore` (e.g., `product-categories`, `blog_posts`)
- **Display names:** Human-readable, can contain spaces (e.g., `"Product Name"`, `"Is Active"`)

## System Fields (Automatic)

Every collection includes: `_id`, `_createdDate`, `_updatedDate`, `_owner`

## Permissions

Access levels control who can read, create, update, and delete items in collections.

| Level                | Description                                        |
| -------------------- | -------------------------------------------------- |
| `UNDEFINED`          | Not set (inherits defaults)                        |
| `ANYONE`             | Public access (including visitors)                 |
| `SITE_MEMBER`        | Any signed-in user (members and collaborators)     |
| `SITE_MEMBER_AUTHOR` | Signed-in users, but members only access own items |
| `CMS_EDITOR`         | Site collaborators with CMS Access permission      |
| `PRIVILEGED`         | CMS administrators and privileged users            |

**Common patterns:**

- Public content (default, recommended): `read: ANYONE, write: PRIVILEGED`
- User-generated content: `read: SITE_MEMBER, write: SITE_MEMBER_AUTHOR`
- Editorial workflow: `read: ANYONE, write: CMS_EDITOR`
- Private/admin: `read: PRIVILEGED, write: PRIVILEGED`

**Permission hierarchy** (most to least restrictive): `PRIVILEGED` > `CMS_EDITOR` > `SITE_MEMBER_AUTHOR` > `SITE_MEMBER` > `ANYONE` > `UNDEFINED`

### Context-Based Permission Rules

**CRITICAL: Permissions must match where and how the data is accessed.** The consumer of the data determines the minimum permission level — setting permissions more restrictive than the access context will cause runtime failures (empty results or permission-denied errors).

**Determine permissions by asking: "Who interacts with this data, and from where?"**

| Access Context | Who Sees / Uses It | Implication |
|---|---|---|
| **Custom element widget** (`CUSTOM_ELEMENT_WIDGET`) | Any site visitor (public) | Reads must be `ANYONE`. If the widget accepts input (e.g., reviews, submissions), inserts must also be `ANYONE` or `SITE_MEMBER`. |
| **Embedded Script** | Any site visitor (public) | Same as custom element widget — reads must be `ANYONE`. Writes depend on whether visitors can submit data. |
| **Dashboard Page** (`DASHBOARD_PAGE`) | Site owner / collaborators only | Can use `CMS_EDITOR` or `PRIVILEGED` for all operations since only authorized users access the dashboard. |
| **Backend code (site-side)** | Runs in visitor context | If called from page code or site-side modules, the caller has visitor-level permissions — data must be readable/writable at the appropriate public level. |
| **Backend code (elevated)** | Runs with `auth.elevate()` from `@wix/essentials` | Can bypass permissions, but the collection still needs correct defaults for any non-elevated callers. |

Use `SITE_MEMBER_AUTHOR` on `itemUpdate` / `itemRemove` when members should only modify their **own** items (e.g., a member can edit only their own reviews).

**How to apply this:**

1. **Identify every place the collection is read or written** — custom element widgets, dashboard pages, embedded scripts, backend APIs.
2. **Use the least restrictive context as the floor.** If a custom element widget reads the data AND a dashboard page also reads it, `itemRead` must be `ANYONE` (because the widget is public).
3. **Apply per-operation.** A collection can have `itemRead: ANYONE` (widget displays it) but `itemInsert: CMS_EDITOR` (only dashboard users add items). Each operation is independent.

## Relationships

**One-to-One / Many-to-One (REFERENCE):**

```json
{
  "key": "category",
  "displayName": "Category",
  "type": "REFERENCE",
  "referenceOptions": {
    "referencedCollectionId": "categories"
  }
}
```

**Many-to-Many (MULTI_REFERENCE):**

```json
{
  "key": "tags",
  "displayName": "Tags",
  "type": "MULTI_REFERENCE",
  "multiReferenceOptions": {
    "referencedCollectionId": "tags"
  }
}
```

**CRITICAL Constraints:**

- REFERENCE/MULTI_REFERENCE fields can ONLY link to other custom CMS collections defined in your app
- The `referencedCollectionId` MUST be the `idSuffix` of another collection in the same plan
- **NEVER use REFERENCE fields to link to Wix business entities** (Products, Orders, Contacts, Members, etc.)
- Use Wix SDK APIs to access Wix business entities instead

## App Version Updates

Changes to your data collections extension require releasing a new major version of your app. When a user updates to the new major version, their collections are updated as follows:

- **Adding a new collection:** The new collection is created on the site.
- **Removing a collection:** If the old app version defined a collection and the new version doesn't, the collection is removed from the site.
- **Modifying a collection schema:** Field additions, removals, and type changes are applied to the collection. Existing data is preserved.

**Important notes:**

- Collection changes only affect users who update to the new major version. Users who don't update retain their current collections.
- Collection changes take up to 5 minutes to propagate after an update.
- **Initial data is only imported when a collection is first created.** If a collection already contains data, `initialData` is ignored during updates.

## Wix CLI-Specific Constraints

### When NOT to use a Collection

Collections are for **data**, not configuration:

- **Embedded script settings** → use `embeddedScriptParameters` instead.
- **Custom element widget settings** → use the widget's `panel.tsx` (settings panel) instead. A widget-only blueprint usually needs **zero** collections.
- **Single-value config** (theme, mode, threshold) → put it in the host extension's settings, not a one-field collection.
- **Computed / aggregated values** (averages, counts) → calculate dynamically, don't store.

Common values that do **not** belong in a collection: colors, fonts, sizes, headlines, labels, messages, dates/times, coupon codes, display positions, feature toggles, frequencies, numeric thresholds.

Collections are for: business data (products, orders, inventory), user-generated content (reviews, comments, submissions), event logs, and multi-record relational data.

### Initial Data Rules

Each item in `initialData` must match the collection schema exactly:

- Field keys must be `lowerCamelCase` and match the schema
- `TEXT` → string, `NUMBER` → number, `BOOLEAN` → boolean
- `DATE`/`DATETIME` → use `{ "$date": "2024-01-15T10:30:00.000Z" }` format
- `REFERENCE` → provide the `idSuffix` of the referenced collection
- Required fields must always have values

## Examples

### Simple Collection with Initial Data

**Request:** "Create a collection for handling fees with example data"

Scaffold:

```bash
wix generate --params '{"extensionType":"DATA_COLLECTION","collectionName":"additional-fees"}'
```

Edit the generated `src/extensions/backend/data-collections/additional-fees.ts`:

```typescript
import type { DataCollection } from '@wix/astro/builders';

export const collectionIdSuffix = 'additional-fees';

export default {
  idSuffix: collectionIdSuffix,
  displayName: 'Additional Fees',
  displayField: 'title',
  fields: [
    { key: 'title', displayName: 'Fee Title', type: 'TEXT' },
    { key: 'amount', displayName: 'Fee Amount', type: 'NUMBER' },
  ],
  dataPermissions: {
    itemRead: 'ANYONE',
    itemInsert: 'PRIVILEGED',
    itemUpdate: 'PRIVILEGED',
    itemRemove: 'PRIVILEGED',
  },
  indexes: [],
  initialData: [
    { title: 'Handling Fee', amount: 5 },
    { title: 'Gift Wrapping', amount: 3.5 },
  ],
} satisfies DataCollection;
```

### Collection with Reference Relationship

**Request:** "Create collections for products and categories with relationships"

Run `wix generate --params` twice — once with `collectionName: "categories"` and once with `collectionName: "products"`. Then edit `src/extensions/backend/data-collections/products.ts` to add a `REFERENCE` field pointing at `categories` (`referenceOptions: { referencedCollectionId: "categories" }`). The aggregator `data-collections.extension.ts` is updated by the CLI automatically.

## Common Patterns

**Soft Delete:** Add `isDeleted` (BOOLEAN), defaulted at the insert path

**Status/Workflow:** Add `status` (TEXT) with values like draft/pending/published

**URL Slug:** Add `slug` (TEXT) plus a `{ fields: [{ path: 'slug' }], unique: true }` entry in `indexes` for SEO-friendly URLs

**Owner Tracking:** Add `createdBy` (REFERENCE → custom collection, not Members)

**Note:** For owner tracking, create a custom collection for users rather than referencing Wix Members directly.

## Reference Documentation

- [Wix Data SDK Reference](data-collection/WIX_DATA.md) - Complete reference for reading and writing data using `@wix/data`

### Public Documentation

- [About Data Collections Extensions](https://dev.wix.com/docs/build-apps/develop-your-app/extensions/backend-extensions/data-collections/about-data-collections-extensions) - When to use the extension, implementation options, and app version update behavior
- [Add a Data Collections Extension in the App Dashboard](https://dev.wix.com/docs/build-apps/develop-your-app/extensions/backend-extensions/data-collections/add-a-data-collections-extension-in-the-app-dashboard) - Step-by-step guide to configuring collections via the app dashboard JSON editor, with example configuration
- [Data Collections Extension JSON Reference](https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections-extension/introduction) - Complete JSON schema and field definitions for the data collections extension
