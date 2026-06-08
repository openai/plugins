import { useState, useEffect, useRef } from "react";
import { currentCart } from "@wix/ecom";
import { redirects } from "@wix/redirects";
import { trackEvent } from "../utils/analytics";

// ── Types ──

interface DescriptionLine {
  name?: { translated?: string };
  plainText?: { translated?: string };
  colorInfo?: { translated?: string; code?: string };
}

interface Availability {
  status?: string;       // "AVAILABLE" | "NOT_AVAILABLE" | "NOT_FOUND" | "PARTIALLY_AVAILABLE"
  quantityAvailable?: number;
}

interface Modifier {
  label?: { translated?: string };
  quantity?: number;
  price?: { formattedConvertedAmount?: string };
}

interface ModifierGroup {
  name?: { translated?: string };
  modifiers?: Modifier[];
}

// Local structural type. The SDK's lineItem types use `string | null` for
// translated fields; we keep this local shape narrower for ergonomic
// destructuring and use `as unknown as LineItem[]` at SDK boundaries.
// Narrowing is safe because we null-check each field at the use site.
interface LineItem {
  _id?: string | null;
  productName?: { translated?: string };
  quantity?: number;
  price?: { amount?: string; formattedConvertedAmount?: string };
  fullPrice?: { formattedConvertedAmount?: string };
  lineItemPrice?: { amount?: string; formattedConvertedAmount?: string };
  image?: string;  // "wix:image://v1/<mediaId>/..." — always a string, NOT an object
  catalogReference?: { catalogItemId?: string };
  descriptionLines?: DescriptionLine[];
  availability?: Availability;
  modifierGroups?: ModifierGroup[];
  // The SDK returns `url` as an absolute URL string (e.g.
  // "https://<site>.wixsite.com/<name>/product-page/<slug>"); REST returns
  // an object `{ relativePath, url }`. Handle both in `resolveProductHref`.
  url?: string | { relativePath?: string; url?: string };
}

interface CartSummary {
  subtotal?: string;
  discount?: string;
  total?: string;
  discountNames: string[];
}

// No server-side props — cart is per-visitor and must not break SSR caching.
// Always fetched client-side on mount.

// ── Helpers ──

/**
 * Extract display text from a description line. Handles both plainText and
 * colorInfo types. colorInfo lines carry a human-readable name (e.g. "Dark Blue")
 * alongside the hex code — use the translated name, not the code.
 * Renders as "Title: Value", or just the title/value if one is missing.
 */
function formatDescriptionLine(line: DescriptionLine): string {
  const title = line.name?.translated;
  const value = line.plainText?.translated ?? line.colorInfo?.translated;
  if (title && value) return `${title}: ${value}`;
  return title ?? value ?? "";
}

/**
 * Resolve a cart line item image to a renderable CDN URL.
 * The ecom SDK returns lineItem.image as a plain string "wix:image://v1/<mediaId>/..."
 * (NOT an object { url } despite what the REST docs say).
 * Parse it to a Wix static CDN URL with resizing.
 */
function resolveCartImage(image: string | undefined, width: number, height: number): string | undefined {
  if (!image) return undefined;
  if (image.startsWith("wix:image://")) {
    const match = image.match(/wix:image:\/\/v1\/([^/]+)/);
    if (match) {
      return `https://static.wixstatic.com/media/${match[1]}/v1/fill/w_${width},h_${height},al_c,q_80/${match[1]}`;
    }
  }
  // Direct CDN URL — use as-is
  return image;
}

/** Whether a line item is unavailable (out of stock, deleted, or not found) */
function isItemUnavailable(item: LineItem): boolean {
  const status = item.availability?.status;
  return status === "NOT_AVAILABLE" || status === "NOT_FOUND";
}

/**
 * Build a same-site link to the product detail page for this line item.
 *
 * `item.url` shape varies by caller:
 *   - `@wix/ecom` currentCart SDK: absolute URL string like
 *     "https://<site>.wixsite.com/<name>/product-page/<slug>"
 *   - REST: object `{ relativePath: "/product-page/<slug>", url: "..." }`
 *
 * Extract the slug after `/product-page/` either way and rewrite to the
 * headless `/products/<slug>` route. Returns undefined when the URL is
 * absent or doesn't follow the Stores route pattern.
 */
function resolveProductHref(item: LineItem): string | undefined {
  const url = item.url;
  if (!url) return undefined;
  const str = typeof url === "string" ? url : (url.relativePath ?? url.url);
  if (!str) return undefined;
  const match = str.match(/\/product-page\/([^/?#]+)/);
  return match ? `/products/${match[1]}` : undefined;
}

// Cached cart snapshot so re-navigation to /cart renders the previous state
// instantly, while the authoritative fetch runs in the background. Kept in
// sessionStorage (per-tab, cleared on close) so logout/device-sharing never
// shows a stale cart to a different identity.
const CART_CACHE_KEY = "cart:last-snapshot";
type CartSnapshot = { lineItems: LineItem[]; summary: CartSummary };

function readCartSnapshot(): CartSnapshot | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(CART_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed?.lineItems)) return null;
    return parsed as CartSnapshot;
  } catch {
    return null;
  }
}

function writeCartSnapshot(snapshot: CartSnapshot): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(CART_CACHE_KEY, JSON.stringify(snapshot));
  } catch {
    /* storage full / denied — ignore, fall back to fetch-only */
  }
}

/**
 * Extract cart-level totals + applied discount names from a cart response.
 *
 * `priceSummary` exposes:
 *  - `subtotal` — sum of line items BEFORE cart-level discounts (each line already
 *    reflects per-line automatic discounts, so this is "what the items cost")
 *  - `discount` — cart-level discount amount (automatic discounts, promo codes)
 *  - `total`    — subtotal − discount + shipping + tax (shipping + tax are
 *    typically zero before checkout is created)
 *
 * `appliedDiscounts[]` lists every discount Wix applied; `discountName` is the
 * merchant-facing label (e.g. "Spring Sale 20% off").
 *
 * Fallback: if `priceSummary.subtotal` is missing (some early-stage carts return
 * an empty summary until checkout is created), compute it client-side from
 * `lineItemPrice.amount` × rows. Shows something instead of a blank slot.
 */
function extractSummary(
  // `lineItems` is `any[]` — the SDK's LineItem shape (string | null on
  // translated fields) is structurally incompatible with our narrower local
  // LineItem. We only read `lineItemPrice.amount` here, which is loose anyway.
  cart: { priceSummary?: any; appliedDiscounts?: any[]; lineItems?: any[]; currency?: string } | undefined,
): CartSummary {
  const ps = cart?.priceSummary;
  let subtotal = ps?.subtotal?.formattedConvertedAmount as string | undefined;
  const discount = ps?.discount?.formattedConvertedAmount as string | undefined;
  const total = ps?.total?.formattedConvertedAmount as string | undefined;

  // Fallback subtotal from line items when priceSummary is empty.
  if (!subtotal && cart?.lineItems?.length) {
    const sum = cart.lineItems.reduce((acc, item) => {
      const amt = item.lineItemPrice?.amount;
      return amt ? acc + Number(amt) : acc;
    }, 0);
    if (sum > 0) {
      try {
        subtotal = new Intl.NumberFormat(undefined, {
          style: "currency",
          currency: cart.currency ?? "USD",
        }).format(sum);
      } catch {
        subtotal = sum.toFixed(2);
      }
    }
  }

  const discountNames = (cart?.appliedDiscounts ?? [])
    .map((d: any) => d?.discountName || d?.coupon?.name || d?.merchantDiscount?.discountName)
    .filter(Boolean);

  return { subtotal, discount, total, discountNames };
}

// ── Component ──

export default function CartView() {
  // Hydrate from the last cart snapshot so re-navigating to /cart renders the
  // previous state immediately — no empty/loading flash. The authoritative
  // fetch in useEffect below reconciles shortly after.
  const cached = typeof window !== "undefined" ? readCartSnapshot() : null;
  const [items, setItems] = useState<LineItem[]>(cached?.lineItems ?? []);
  const [summary, setSummary] = useState<CartSummary>(
    cached?.summary ?? { discountNames: [] },
  );
  // `loading` is only true when there's no cached snapshot to render from.
  const [loading, setLoading] = useState(!cached);
  const [checkingOut, setCheckingOut] = useState(false);
  const qtyTimers = useRef(new Map<string, ReturnType<typeof setTimeout>>());

  useEffect(() => {
    loadCart();
  }, []);

  // getCurrentCart() returns the cart object directly — NOT wrapped in { cart }.
  // Totals + applied discounts all live under priceSummary + appliedDiscounts.
  const loadCart = async () => {
    try {
      const cart = await currentCart.getCurrentCart();
      const lineItems = (cart.lineItems as unknown as LineItem[]) ?? [];
      const nextSummary = extractSummary(cart);
      setItems(lineItems);
      setSummary(nextSummary);
      writeCartSnapshot({ lineItems, summary: nextSummary });
    } catch {
      // Leave any cached state in place on transient errors.
      if (!cached) {
        setItems([]);
        setSummary({ discountNames: [] });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = (itemId: string, quantity: number) => {
    // Optimistic: update local state immediately
    setItems((prev) =>
      prev.map((it) => (it._id === itemId ? { ...it, quantity } : it))
    );

    // Debounce API call — rapid clicks coalesce into one request
    const prev = qtyTimers.current.get(itemId);
    if (prev) clearTimeout(prev);
    qtyTimers.current.set(
      itemId,
      setTimeout(async () => {
        qtyTimers.current.delete(itemId);
        try {
          const { cart } = await currentCart.updateCurrentCartLineItemQuantity([
            { _id: itemId, quantity },
          ]);
          if (!cart) return;
          window.dispatchEvent(new CustomEvent("cart-updated", { detail: { cart } }));
          const nextItems = (cart.lineItems as unknown as LineItem[]) ?? [];
          const nextSummary = extractSummary(cart);
          setItems(nextItems);
          setSummary(nextSummary);
          writeCartSnapshot({ lineItems: nextItems, summary: nextSummary });
        } catch {
          await loadCart();
        }
      }, 300)
    );
  };

  const handleRemoveItem = async (itemId: string) => {
    const removed = items.find((item) => item._id === itemId);
    if (removed) {
      trackEvent("RemoveFromCart", {
        id: removed.catalogReference?.catalogItemId ?? removed._id,
        name: removed.productName?.translated,
        price: removed.price?.amount ? Number(removed.price.amount) : undefined,
        quantity: removed.quantity,
        origin: "Cart",
      });
    }

    // Optimistic: remove from local state immediately
    setItems((prev) => prev.filter((it) => it._id !== itemId));

    try {
      const { cart } = await currentCart.removeLineItemsFromCurrentCart([itemId]);
      if (!cart) return;
      window.dispatchEvent(new CustomEvent("cart-updated", { detail: { cart } }));
      const nextItems = (cart.lineItems as unknown as LineItem[]) ?? [];
      const nextSummary = extractSummary(cart);
      setItems(nextItems);
      setSummary(nextSummary);
      writeCartSnapshot({ lineItems: nextItems, summary: nextSummary });
    } catch {
      await loadCart();
    }
  };

  const handleCheckout = async () => {
    setCheckingOut(true);
    try {
      trackEvent("InitiateCheckout", {
        contents: items.map((item) => ({
          id: item.catalogReference?.catalogItemId ?? item._id,
          name: item.productName?.translated,
          price: item.price?.amount ? Number(item.price.amount) : undefined,
          quantity: item.quantity,
        })),
        origin: "Cart",
      });

      const { checkoutId } = await currentCart.createCheckoutFromCurrentCart({
        channelType: currentCart.ChannelType.WEB,
      });

      const { redirectSession } = await redirects.createRedirectSession({
        ecomCheckout: { checkoutId },
        callbacks: {
          postFlowUrl: window.location.origin,
          thankYouPageUrl: `${window.location.origin}/thank-you`,
          cartPageUrl: `${window.location.origin}/cart`,
        },
      });

      if (redirectSession?.fullUrl) {
        window.location.href = redirectSession.fullUrl;
      }
    } catch {
      setCheckingOut(false);
    }
  };

  // ── Render ──

  if (loading) {
    return <p className="cart-empty">Loading cart...</p>;
  }

  if (items.length === 0) {
    return (
      <div className="cart-empty">
        <p>Your cart is empty.</p>
        <a href="/products" className="checkout-btn">Browse Products</a>
      </div>
    );
  }

  const hasUnavailable = items.some(isItemUnavailable);

  return (
    <div className="grid grid-cols-1 md:grid-cols-[1fr_22rem] gap-2xl md:gap-3xl md:items-start">
      {/* ── Left column: line items ── */}
      <div className="flex flex-col gap-lg">
        {items.map((item) => {
          const unavailable = isItemUnavailable(item);
          const maxQty = item.availability?.quantityAvailable ?? 99;
          const hasDiscount =
            item.fullPrice?.formattedConvertedAmount &&
            item.fullPrice.formattedConvertedAmount !== item.price?.formattedConvertedAmount;

          return (
            <div
              key={item._id}
              className={`flex gap-lg pb-lg border-b border-rule last:border-0${unavailable ? " unavailable" : ""}`}
            >
              {/* Product image + name link back to the product detail page
                  for available items. Unavailable lines render as plain text. */}
              {(() => {
                const productHref = !unavailable ? resolveProductHref(item) : undefined;
                const imgSrc = resolveCartImage(item.image, 160, 160);
                const imageNode = imgSrc ? (
                  <img src={imgSrc} alt={item.productName?.translated ?? ""} className="cart-item-image" />
                ) : (
                  <div className="cart-item-image cart-item-image-placeholder" aria-hidden="true" />
                );
                return productHref ? (
                  <a href={productHref} className="cart-item-image-link" aria-label={item.productName?.translated ?? "Product"}>
                    {imageNode}
                  </a>
                ) : imageNode;
              })()}

              <div className="cart-item-info">
                <h3 className="cart-item-name">
                  {(() => {
                    const productHref = !unavailable ? resolveProductHref(item) : undefined;
                    return productHref ? (
                      <a href={productHref} className="cart-item-name-link">
                        {item.productName?.translated}
                      </a>
                    ) : item.productName?.translated;
                  })()}
                </h3>

                {/* Description lines — option selections (Size, Color, etc.)
                    Both plainText and colorInfo types are handled by formatDescriptionLine. */}
                {(item.descriptionLines ?? []).map((line, i) => {
                  const text = formatDescriptionLine(line);
                  return text ? (
                    <p key={i} className="cart-item-option">{text}</p>
                  ) : null;
                })}

                {/* Modifier groups — extras/add-ons */}
                {(item.modifierGroups ?? []).map((group, gi) => (
                  <div key={gi} className="cart-item-modifiers">
                    {(group.modifiers ?? []).map((mod, mi) => (
                      <p key={mi} className="cart-item-option">
                        {mod.label?.translated}
                        {mod.quantity && mod.quantity > 1 ? ` ×${mod.quantity}` : ""}
                        {mod.price?.formattedConvertedAmount
                          ? ` (+${mod.price.formattedConvertedAmount})`
                          : ""}
                      </p>
                    ))}
                  </div>
                ))}

                {/* Quantity selector or unavailable label */}
                {unavailable ? (
                  <p className="cart-item-unavailable">
                    {item.availability?.status === "NOT_FOUND"
                      ? "This item is no longer available"
                      : "Out of Stock"}
                  </p>
                ) : (
                  <div className="cart-item-qty">
                    <button
                      className="qty-btn"
                      disabled={!item.quantity || item.quantity <= 1}
                      onClick={() =>
                        item._id && handleUpdateQuantity(item._id, (item.quantity ?? 1) - 1)
                      }
                    >
                      −
                    </button>
                    <span className="qty-value">{item.quantity}</span>
                    <button
                      className="qty-btn"
                      disabled={(item.quantity ?? 0) >= maxQty}
                      onClick={() =>
                        item._id && handleUpdateQuantity(item._id, (item.quantity ?? 1) + 1)
                      }
                    >
                      +
                    </button>
                  </div>
                )}
              </div>

              {/* Price display — THREE fields, each with a different meaning:
                  - fullPrice: per-unit price BEFORE discount (strikethrough when discounted)
                  - price:     per-unit price AFTER discount (the actual unit price)
                  - lineItemPrice: total for the line (price × quantity)
                  Show fullPrice and price side by side (both per-unit).
                  Show lineItemPrice below ONLY when qty > 1 (otherwise it equals price). */}
              <div className="cart-item-actions">
                <div className="cart-item-prices">
                  {hasDiscount && (
                    <span className="cart-item-full-price">{item.fullPrice!.formattedConvertedAmount}</span>
                  )}
                  <span className="cart-item-unit-price">{item.price?.formattedConvertedAmount}</span>
                </div>
                {(item.quantity ?? 1) > 1 && (
                  <p className="cart-item-line-total">
                    {item.lineItemPrice?.formattedConvertedAmount}
                  </p>
                )}
                <button
                  onClick={() => item._id && handleRemoveItem(item._id)}
                  className="cart-item-remove"
                >
                  Remove
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Right column: order summary ──
          Always render `Subtotal`. Three ways discounts surface — all values
          come from the API, we don't compute amounts client-side:
            1. Cart-level discount with amount (coupons, cart-level promos) →
               `priceSummary.discount` populated → render `cart-discount` row
               with amount + optional name.
            2. Applied-promotion name only (common for line-item automatic
               discounts, where `priceSummary.discount` stays empty but
               `appliedDiscounts[].discountName` carries the promo label) →
               render `cart-applied-discounts` row: name only, no amount.
               Per-line savings show inline via fullPrice/price strikethrough.
            3. No discount → no row.
          Render `Total` when it differs from subtotal.
          See extractSummary() above. */}
      <div className="cart-summary">
        <div className="flex justify-between items-baseline">
          <span>Subtotal</span>
          <span>{summary.subtotal}</span>
        </div>
        {summary.discount ? (
          <div className="cart-discount">
            <span>
              Discount
              {summary.discountNames.length > 0 && (
                <span className="cart-discount-name"> · {summary.discountNames.join(", ")}</span>
              )}
            </span>
            <span className="cart-discount-amount">−{summary.discount}</span>
          </div>
        ) : summary.discountNames.length > 0 ? (
          <div className="cart-applied-discounts">
            <span>Applied discount</span>
            <span className="cart-applied-discounts-name">{summary.discountNames.join(", ")}</span>
          </div>
        ) : null}
        {summary.total && summary.total !== summary.subtotal && (
          <div className="cart-total">
            <span>Total</span>
            <span>{summary.total}</span>
          </div>
        )}
        {hasUnavailable && (
          <p className="cart-item-unavailable">
            Remove unavailable items before checking out.
          </p>
        )}
        <button
          onClick={handleCheckout}
          disabled={checkingOut || hasUnavailable}
          className="checkout-btn"
        >
          {checkingOut ? "Redirecting to checkout..." : "Proceed to Checkout"}
        </button>
      </div>
    </div>
  );
}
