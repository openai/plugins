import { useState, useEffect } from "react";
import { currentCart } from "@wix/ecom";

// CartView writes { lineItems, summary } to sessionStorage on every successful
// fetch/update. Read the snapshot here so the badge count renders instantly
// on every navigation instead of flashing empty while the fresh fetch runs.
// Same key as CartView; CartBadge is a read-only consumer.
const CART_CACHE_KEY = "cart:last-snapshot";

function readCachedCount(): number {
  if (typeof window === "undefined") return 0;
  try {
    const raw = window.sessionStorage.getItem(CART_CACHE_KEY);
    if (!raw) return 0;
    const parsed = JSON.parse(raw);
    const items = Array.isArray(parsed?.lineItems) ? parsed.lineItems : [];
    return items.reduce(
      (sum: number, item: any) => sum + (item?.quantity ?? 0),
      0,
    );
  } catch {
    return 0;
  }
}

export default function CartBadge() {
  const [count, setCount] = useState(() => readCachedCount());

  const fetchCount = async () => {
    try {
      const cart = await currentCart.getCurrentCart();
      const total = (cart.lineItems ?? []).reduce(
        (sum, item) => sum + (item.quantity ?? 0),
        0
      );
      setCount(total);
    } catch {
      setCount(0);
    }
  };

  useEffect(() => {
    // Always fetch client-side — cart count is per-visitor and must not
    // be server-rendered (would break SSR caching)
    fetchCount();

    const handleCartUpdate = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.cart?.lineItems) {
        const total = (detail.cart.lineItems as any[]).reduce(
          (sum: number, item: any) => sum + (item.quantity ?? 0),
          0
        );
        setCount(total);
      } else if (detail?.delta) {
        setCount((prev) => prev + detail.delta);
      } else {
        fetchCount();
      }
    };
    window.addEventListener("cart-updated", handleCartUpdate);
    return () => window.removeEventListener("cart-updated", handleCartUpdate);
  }, []);

  return (
    <a href="/cart" className="cart-badge" aria-label={count > 0 ? `Cart, ${count} items` : "Cart"}>
      <svg
        className="cart-badge-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
        focusable="false"
      >
        <path d="M5 8h14l-1.2 10.2a2 2 0 0 1-2 1.8H8.2a2 2 0 0 1-2-1.8L5 8Z" />
        <path d="M9 8V6a3 3 0 0 1 6 0v2" />
      </svg>
      {count > 0 && <span className="cart-badge-count">{count}</span>}
    </a>
  );
}
