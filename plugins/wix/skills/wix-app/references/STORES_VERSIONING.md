
# Wix Stores Catalog Versioning (V1 / V3)

Wix Stores has two catalog versions that are **NOT backwards compatible**. Apps **must support both** — single-version apps cannot list in the App Market and break on new sites.

| Version | Status | Modules |
|---------|--------|---------|
| **V1_CATALOG** | Legacy | `products`, `collections`, `inventory` |
| **V3_CATALOG** | Current | `productsV3`, `inventoryItemsV3`, `customizationsV3`, `ribbonsV3`, `brandsV3`, `infoSectionsV3` (all from `@wix/stores`); `categories` (from `@wix/categories`) |

---

## Mandatory: Detect Version First

**Every Stores flow must call `catalogVersioning.getCatalogVersion()` before any other Stores operation.** The version is permanent per site — cache it.

```typescript
import { catalogVersioning, products, productsV3 } from '@wix/stores';

export type CatalogVersion = 'V1_CATALOG' | 'V3_CATALOG' | 'STORES_NOT_INSTALLED';
let cached: CatalogVersion | undefined;

export async function getVersion(): Promise<CatalogVersion> {
  if (cached) return cached;
  const { catalogVersion } = await catalogVersioning.getCatalogVersion();
  cached = catalogVersion as CatalogVersion;
  return cached;
}
```

Handle `STORES_NOT_INSTALLED` gracefully — return empty results, do not throw.

---

## Module Map (V1 → V3)

| Concern | V1 (`@wix/stores`) | V3 (`@wix/stores` unless noted) |
|---------|--------------------|--------------------------------|
| Catalog version | `catalogVersioning` | `catalogVersioning` (same) |
| Products CRUD | `products` | `productsV3` |
| Inventory | `inventory` | `inventoryItemsV3` |
| Collections / Categories | Read: `collections`. **Write ops live on `products`** (`createCollection`, `updateCollection`, `addProductsToCollection`, …) | `@wix/categories` → `categories` |
| Custom text fields | `customTextFields` on product | `customizationsV3` (FREE_TEXT modifier) |
| Ribbons | inline `ribbon` string | `ribbonsV3` |
| Brand | inline `brand` string | `brandsV3` |
| Info sections | inline `additionalInfoSections` | `infoSectionsV3` |
| Subscriptions | dedicated subscriptions API | inline `subscriptionDetails` on product |

---

## Permissions

**Always include `SCOPE.STORES.CATALOG_READ_LIMITED`** — required by `getCatalogVersion()`. Request **both** V1 and V3 scopes for any operation you implement on both code paths.

| Operation | V1 scope | V3 scope |
|-----------|----------|----------|
| Get catalog version | `SCOPE.STORES.CATALOG_READ_LIMITED` | `SCOPE.STORES.CATALOG_READ_LIMITED` |
| Read products | `SCOPE.DC-STORES.READ-PRODUCTS` | `SCOPE.STORES.PRODUCT_READ` |
| Read hidden products / merchant data | `SCOPE.DC-STORES.READ-PRODUCTS` | `SCOPE.STORES.PRODUCT_READ_ADMIN` |
| Create / update / delete products | `SCOPE.DC-STORES.MANAGE-PRODUCTS` | `SCOPE.STORES.PRODUCT_WRITE` |
| Read inventory | `SCOPE.DC-STORES.READ-PRODUCTS` | `SCOPE.STORES.INVENTORY_ITEM_READ` |
| Update inventory | `SCOPE.DC-STORES.MANAGE-PRODUCTS` | `SCOPE.STORES.INVENTORY_ITEM_WRITE` |
| Read orders (unchanged) | `SCOPE.DC-STORES.READ-ORDERS` | `SCOPE.DC-STORES.READ-ORDERS` |
| Manage collections (V1) / categories (V3) | `SCOPE.DC-STORES.MANAGE-PRODUCTS` | `SCOPE.CATEGORIES.CATEGORY_WRITE` |
| Read categories (V3) | — | `SCOPE.CATEGORIES.CATEGORY_READ` |

---

## Major V3 Behavior Changes (gotchas)

1. **Every product has at least one variant.** `manageVariants` is gone. Single-variant products still expose price/sku via `variantsInfo.variants[0]`.
2. **`revision` required on update.** V3 uses optimistic concurrency — fetch current `revision`, pass it back. Each update increments it.
3. **Array fields overwrite, don't merge.** When updating `options`, `modifiers`, or `variantsInfo.variants`, send the entire array. `options` and `variantsInfo.variants` are coupled — update one, update the other.
4. **`queryProducts` (V3) does not return variants.** Use `getProduct` or the Read-Only Variants API.
5. **Hidden products require `SCOPE.STORES.PRODUCT_READ_ADMIN`** for V3 reads. The basic read scope only sees `visible: true`.
6. **Requested fields**: V3 needs `'CURRENCY'`, `'MERCHANT_DATA'`, `'URL'`, `'INFO_SECTION'`, etc. in the `fields` array to populate those fields.
7. **Prices are strings in V3, numbers in V1.** Enums are **UPPER_CASE in V3, lower-case in V1** (`PHYSICAL` vs `physical`).
8. **Categories require a `treeReference`** (`appNamespace` + `treeKey`) — V1 collections did not.
9. **V3 paging is cursor-only — no offset, no total count.** The V3 builder uses `.skipTo(cursor)` (not V1's `.skip(n)`), and the result has `cursors.next` + `hasNext()` but no `totalCount`. Don't build "page X of Y" UI for V3 — use Next/Previous.
10. **V3 product sort fields fail at runtime even when TypeScript accepts them.** TS allows `'_createdDate' | '_updatedDate' | 'slug' | 'visible'`, but real V3 sites return `Field '_createdDate' is not declared as sortable`. **Omit `sort` on V3 product queries** unless verified on a live V3 site.
11. **Stock status is UPPER_SNAKE_CASE on both versions** — `IN_STOCK`, `OUT_OF_STOCK`, `PARTIALLY_OUT_OF_STOCK`, plus `PREORDER` on V3. Never compare against lowercase.

---

## Copy-Paste Recipes

Each recipe handles both versions. `V3Product` and V1 `Product` types are **not** re-exported from `@wix/stores` top-level — let TS infer or use structural types.

### List products with pagination

Both versions expose a fluent query builder, but the paging method differs:

| Aspect | V1 (`products.queryProducts()`) | V3 (`productsV3.queryProducts()`) |
|--------|--------------------------------|----------------------------------|
| API style | Fluent builder: `.skip().limit().find()` | Fluent builder: `.skipTo(cursor).limit().find()` |
| Pagination | Offset (`.skip(n)`) | Cursor (`.skipTo(cursor)`) |
| Result `items` | `res.items` (V1 `Product[]`) | `res.items` (V3 `Product[]`) |
| Total count | `res.totalCount` | **None** — V3 only has `cursors.next` + `hasNext()` |
| `hasNext` | `res.hasNext()` (method) | `res.hasNext()` (method) |
| Next cursor | n/a | `res.cursors.next` (string) |

```typescript
import { catalogVersioning, products, productsV3 } from '@wix/stores';

export interface ProductsPage {
  products: unknown[];        // narrow at call site
  nextCursor: string | null;  // V3 only
  hasNext: boolean;
  totalCount: number | null;  // V1 only
}

export async function listProductsPage(
  limit: number,
  cursorOrSkip: string | number | undefined,
): Promise<ProductsPage> {
  const v = await getVersion();
  if (v === 'STORES_NOT_INSTALLED') {
    return { products: [], nextCursor: null, hasNext: false, totalCount: 0 };
  }

  if (v === 'V3_CATALOG') {
    let builder = productsV3.queryProducts().limit(limit);
    if (typeof cursorOrSkip === 'string') builder = builder.skipTo(cursorOrSkip);
    // Do NOT chain a sort — see gotcha #10.
    const res = await builder.find();
    return {
      products: res.items,
      nextCursor: res.cursors.next ?? null,
      hasNext: res.hasNext(),
      totalCount: null,
    };
  }

  const skip = typeof cursorOrSkip === 'number' ? cursorOrSkip : 0;
  const res = await products.queryProducts().skip(skip).limit(limit).find();
  return {
    products: res.items,
    nextCursor: null,
    hasNext: res.hasNext(),
    totalCount: res.totalCount ?? null,
  };
}
```

> **Two ways to call V3 `queryProducts`:** the canonical builder shown above, and a direct-call form `productsV3.queryProducts({ cursorPaging: { limit, cursor } })` returning a `Promise<{ products, pagingMetadata }>`. Both compile and run, but the builder is more idiomatic and matches V1's shape.

### Display price/stock without fetching variants

V3 `queryProducts` does not return variants. Read product-level rollup fields instead:

```typescript
function displayPrice(p: { actualPriceRange?: { minValue?: { amount?: string }; maxValue?: { amount?: string } } }): string {
  const min = p.actualPriceRange?.minValue?.amount;
  const max = p.actualPriceRange?.maxValue?.amount;
  if (!min) return '—';
  return max && max !== min ? `${min} – ${max}` : min;
}

function stockLabel(status: string | undefined): string {
  switch (status) {
    case 'IN_STOCK': return 'In Stock';
    case 'OUT_OF_STOCK': return 'Out of Stock';
    case 'PARTIALLY_OUT_OF_STOCK': return 'Limited';
    case 'PREORDER': return 'Pre-order';
    default: return '—';
  }
}
// V1 path: product.stock.inventoryStatus  (same UPPER_SNAKE_CASE values)
// V3 path: product.inventory.availabilityStatus (adds PREORDER)
// SKU lives on the variant — show "—" in lists, or use Read-Only Variants API.
```

### Get a single product

```typescript
if (v === 'V3_CATALOG') {
  const product = await productsV3.getProduct(id);  // returns Product directly
  return product;
}
const { product } = await products.getProduct(id);  // V1 wraps in { product }
return product;
```

### Create a product (single-variant, with price)

```typescript
if (v === 'V3_CATALOG') {
  const product = await productsV3.createProduct({
    name: 'My Product',
    productType: 'PHYSICAL',                            // UPPER_CASE
    variantsInfo: {
      variants: [{
        price: { actualPrice: { amount: '19.99' } },    // string, on the variant
        sku: 'SKU-001',
      }],
    },
  });
  return product;
}

const { product } = await products.createProduct({
  name: 'My Product',
  productType: 'physical',                              // lower-case
  priceData: { price: 19.99 },                          // number, on the product
  sku: 'SKU-001',
});
return product;
```

### Update a product (V3 needs `revision`)

```typescript
if (v === 'V3_CATALOG') {
  // Signature: updateProduct(_id, productFields). Returns Product directly.
  const current = await productsV3.getProduct(id);
  if (current.revision == null) throw new Error(`Product ${id} has no revision`);
  return await productsV3.updateProduct(id, {
    revision: current.revision,  // narrowed — required under exactOptionalPropertyTypes
    name: 'New name',
  });
}
// V1: updateProduct(id, productFields). Returns { product }.
const { product } = await products.updateProduct(id, { name: 'New name' });
return product;
```

### Delete a product

```typescript
if (v === 'V3_CATALOG') await productsV3.deleteProduct(id);
else await products.deleteProduct(id);
```

### Inventory: increment stock

```typescript
import { inventory, inventoryItemsV3 } from '@wix/stores';

if (v === 'V3_CATALOG') {
  // Per-variant; flat shape.
  await inventoryItemsV3.bulkIncrementInventoryItems([
    { inventoryItemId, incrementBy: 5 },
  ]);
} else {
  // Per-product (variant optional).
  await inventory.incrementInventory([
    { productId, variantId, incrementBy: 5 },
  ]);
}
```

To find a V3 inventory item ID, use `inventoryItemsV3.searchInventoryItems` filtered by `productId` / `variantId`.

### Query inventory

```typescript
if (v === 'V3_CATALOG') {
  const res = await inventoryItemsV3.queryInventoryItems().eq('productId', productId).find();
  return res.items;
}
// V1: filter is a JSON-stringified expression.
const res = await inventory.queryInventory({
  query: { filter: JSON.stringify({ productId }) },
});
return res.inventoryItems;
```

### Collections (V1) ↔ Categories (V3)

```typescript
// V1 write ops (createCollection, updateCollection, addProductsToCollection, …)
// live on the `products` namespace, NOT `collections`. The `collections` namespace is read-only.
import { products } from '@wix/stores';
import { categories } from '@wix/categories';

if (v === 'V3_CATALOG') {
  // V3 createCategory(category, options). treeReference is REQUIRED and goes in `options`.
  // For Wix Stores categories: appNamespace MUST be the literal "@wix/stores", treeKey is null.
  const category = await categories.createCategory(
    { name: 'Sale' },
    { treeReference: { appNamespace: '@wix/stores', treeKey: null } },
  );
  return category;
}
const { collection } = await products.createCollection({ name: 'Sale' });  // V1 returns { collection }
return collection;
```

V3 categories are tree-structured. Reference them on a product via `directCategories[]`, not `collectionIds[]`. **All Stores category API calls must pass `treeReference: { appNamespace: '@wix/stores', treeKey: null }` in `options`** — applies to `createCategory`, `updateCategory`, `queryCategories`, etc.

---

## V1 → V3 Field Mapping (most common)

For the full table see the [Catalog V1 to V3 Migration Guide](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/catalog-v1-to-v3-migration-guide?apiView=SDK).

| V1 | V3 |
|----|----|
| `priceData.price` (no discount) | `variantsInfo.variants[i].price.actualPrice.amount` |
| `priceData.price` (with discount) | `variantsInfo.variants[i].price.compareAtPrice.amount` |
| `priceData.discountedPrice` | `variantsInfo.variants[i].price.actualPrice.amount` |
| `priceData.currency` | `currency` (top-level, requested field) |
| `sku`, `weight` (single variant) | `variantsInfo.variants[0].sku` / `physicalProperties.weight` |
| `stock.quantity`, `stock.trackInventory` | Inventory Items API (`inventoryItemsV3`) |
| `stock.inventoryStatus` | `inventory.availabilityStatus` |
| `productType: "physical"` | `productType: "PHYSICAL"` (upper-case) |
| `additionalInfoSections[i]` | `infoSections[i]` (now requires `uniqueName`) |
| `customTextFields[i]` | `modifiers[i]` with `freeTextSettings` |
| `manageVariants: true` (creates variants) | `options[i]` |
| `manageVariants: false` (customizations) | `modifiers[i]` |
| `collectionIds[i]` | `directCategories[i].id` |
| `ribbon`, `brand` (string) | `ribbon.name`, `brand.name` (managed via `ribbonsV3` / `brandsV3`) |

**Pricing model** — V1 had a `discount` object; V3 removed it. Discounts are now expressed by the relationship between two fields on the variant: `actualPrice` (required, what the customer pays) vs `compareAtPrice` (optional, original price shown struck through). With discount: V1 `price`/`discountedPrice` → V3 `compareAtPrice`/`actualPrice`. Without discount: V1 `price` → V3 `actualPrice`, leave `compareAtPrice` empty.

---

## Webhooks

**Subscribe to BOTH V1 and V3 webhooks** so your app handles every site.

| V1 event | V3 event |
|----------|----------|
| `products.onProductCreated` / `onProductChanged` / `onProductDeleted` | `productsV3.onProductCreated` / `onProductUpdated` / `onProductDeleted` |
| `products.onProductVariantsChanged` | `productsV3.onProductUpdated` (with `variantsInfo` in `modifiedFields`) |
| `products.onProductCollectionCreated` / `onProductCollectionChanged` / `onProductCollectionDeleted` (yes — the collection webhooks live on the `products` namespace) | `categories.onCategoryCreated` / `onCategoryUpdated` / `onCategoryDeleted` |

Payload changes: V1 `changedFields` → V3 `modifiedFields`. Top-level `entityId` on all V3 payloads. V1 created-event entity → V3 `createdEvent.entityAsJson`. Order webhooks are unchanged — use `@wix/ecom` → `orders`.

---

## Falling back to MCP

This file covers the common 80%. For methods not listed (subscriptions, brands, ribbons, etc.) or full request schemas, use `SearchWixSDKDocumentation` then `ReadFullDocsArticle`. Always return the required permission scopes to the user.
