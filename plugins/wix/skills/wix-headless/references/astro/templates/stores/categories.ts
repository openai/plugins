// Wix Stores Categories — visible, in-use categories under the @wix/stores
// tree. Drops the auto-provisioned "All Products" root and any category
// with zero items so the storefront only surfaces curator-meaningful
// buckets. Returns [] on any failure so consumers can render gracefully.
//
// Only one category-tree is in scope here: @wix/stores. Sites with multiple
// stores trees (B2B, marketplaces) should pass an explicit treeKey.

// The official `@wix/categories` package re-exports these functions; the
// auto_sdk module is already on disk via every other @wix/* package's
// transitive deps, so no extra `npm install` is needed.
import * as categories from "@wix/auto_sdk_categories_categories";
import { productsV3 } from "@wix/stores";

const STORES_NAMESPACE = "@wix/stores";
const STORES_APP_ID = "215238eb-22a5-4c36-9e7b-e7c08025e04e";
const ALL_PRODUCTS_HANDLE = "online_stores_all_products";

// Module-level TTL cache — opportunistic across requests on warm worker
// isolates, harmless on cold starts. Categories rarely change; 5 min is fine.
// Errors are NOT cached so a transient failure doesn't lock out the listing.
const CATEGORIES_TTL_MS = 5 * 60 * 1000;
let categoriesCache: { at: number; data: StoreCategory[]; bySlug: Map<string, StoreCategory> } | null = null;
let inflightCategories: Promise<StoreCategory[]> | null = null;

// Per-category product-ID list — cached under the same TTL so the
// 2-call listProductsInCategory pipeline doesn't re-fetch IDs on every page.
const categoryItemIdsCache = new Map<string, { at: number; ids: string[] }>();

export interface StoreCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  itemCounter: number;
  imageUrl?: string;
}

function toStoreCategory(c: any): StoreCategory | null {
  if (!c?._id || !c?.slug || !c?.name) return null;
  return {
    id: c._id,
    name: c.name,
    slug: c.slug,
    description: c.description ?? undefined,
    itemCounter: typeof c.itemCounter === "number" ? c.itemCounter : 0,
    imageUrl: c.image?.url ?? undefined,
  };
}

async function fetchCategories(): Promise<StoreCategory[]> {
  // The SDK builder rejects empty filter expressions with INVALID_FILTER.
  // `.eq("visible", true)` is the constraint we want anyway and satisfies
  // the validator.
  const res = await categories
    .queryCategories({
      treeReference: { appNamespace: STORES_NAMESPACE },
    })
    .eq("visible", true)
    .ascending("name")
    .limit(100)
    .find();
  return (res.items ?? [])
    .filter((c: any) => c?.handle !== ALL_PRODUCTS_HANDLE)
    .filter((c: any) => typeof c?.itemCounter === "number" && c.itemCounter > 0)
    .map(toStoreCategory)
    .filter((c): c is StoreCategory => c !== null);
}

export async function listStoreCategories(): Promise<StoreCategory[]> {
  if (categoriesCache && Date.now() - categoriesCache.at < CATEGORIES_TTL_MS) {
    return categoriesCache.data;
  }
  if (inflightCategories) return inflightCategories;
  inflightCategories = (async () => {
    try {
      const data = await fetchCategories();
      const bySlug = new Map(data.map((c) => [c.slug, c]));
      categoriesCache = { at: Date.now(), data, bySlug };
      return data;
    } catch (err) {
      console.error("[categories] list failed:", err);
      return [];
    } finally {
      inflightCategories = null;
    }
  })();
  return inflightCategories;
}

export async function getCategoryBySlug(slug: string): Promise<StoreCategory | null> {
  const all = await listStoreCategories();
  return categoriesCache?.bySlug.get(slug) ?? all.find((c) => c.slug === slug) ?? null;
}

async function fetchCategoryItemIds(categoryId: string): Promise<string[]> {
  try {
    const res = await categories.listItemsInCategory(
      categoryId,
      { appNamespace: STORES_NAMESPACE },
    );
    return (res.items ?? [])
      .map((it: any) => it?.catalogItemId)
      .filter((id: any): id is string => typeof id === "string" && id.length > 0);
  } catch (err) {
    console.error("[categories] listItemsInCategory failed:", err);
    return [];
  }
}

async function getCategoryItemIds(categoryId: string): Promise<string[]> {
  const cached = categoryItemIdsCache.get(categoryId);
  if (cached && Date.now() - cached.at < CATEGORIES_TTL_MS) return cached.ids;
  const ids = await fetchCategoryItemIds(categoryId);
  categoryItemIdsCache.set(categoryId, { at: Date.now(), ids });
  return ids;
}

export interface ProductPage {
  items: any[];
  nextCursor: string | null;
  prevCursor: string | null;
}

// Cursor-paginated product list for a single category. Two calls under the
// hood — there is no Wix endpoint that does category filter + cursor paging
// in one shot. The cursor we surface is the productsV3 cursor, so paging is
// stable as long as the category membership doesn't change mid-session.
export async function listProductsInCategory(
  categoryId: string,
  opts: { limit: number; cursor?: string },
): Promise<ProductPage> {
  try {
    const ids = await getCategoryItemIds(categoryId);
    if (ids.length === 0) {
      return { items: [], nextCursor: null, prevCursor: null };
    }
    let builder = productsV3
      .queryProducts({ fields: ["CURRENCY"] })
      .in("_id", ids)
      .limit(opts.limit);
    if (opts.cursor) builder = builder.skipTo(opts.cursor);
    const result = await builder.find();
    return {
      items: result.items ?? [],
      nextCursor: result.cursors?.next ?? null,
      prevCursor: result.cursors?.prev ?? null,
    };
  } catch (err) {
    console.error(`[categories] listProductsInCategory(${categoryId}) failed:`, err);
    return { items: [], nextCursor: null, prevCursor: null };
  }
}

export { STORES_APP_ID };
