import { useState, useMemo, useEffect } from "react";
import { currentCart } from "@wix/ecom";
import AddToCartButton from "./AddToCartButton";
import BackInStockForm from "./BackInStockForm";

interface Choice { choiceId?: string | null; name?: string | null; key?: string | null; }
interface Option { _id?: string | null; name?: string | null; choicesSettings?: { choices?: Choice[]; }; }
// Modifiers: customization choices without separate variants/inventory/price.
interface FreeTextSettings { title?: string | null; key?: string | null; maxLength?: number | null; }
interface Modifier {
  // SDK convention: outer entity IDs are `_id` (same as Variant/Option/Product).
  // REST returns `id`; @wix/stores remaps to `_id` in the SDK response.
  _id?: string | null;
  name?: string | null;
  key?: string | null;
  mandatory?: boolean;
  modifierRenderType?: string | null;   // "TEXT_CHOICES" | "SWATCH_CHOICES" | "FREE_TEXT"
  choicesSettings?: { choices?: Choice[] };
  freeTextSettings?: FreeTextSettings;
}
interface VariantChoice { optionChoiceIds?: { optionId?: string; choiceId?: string; }; }
interface Variant {
  _id?: string | null;
  choices?: VariantChoice[];
  price?: { actual?: { amount?: string; formattedAmount?: string; }; };
  // productsV3 also exposes a per-variant inventoryStatus, but it's a STALE
  // cached flag — a variant with live quantity 0 can still report
  // `inStock: true`. Only used as a last-resort fallback when the
  // inventoryByVariant prop is empty. The authoritative signal is
  // inventoryItemsV3 — see the page-level query in PRODUCT_PAGES.md.
  inventoryStatus?: { inStock?: boolean; preorderEnabled?: boolean };
  // Future-proofing: if a future wiring passes real quantities in props
  // (e.g. via @wix/inventory join by variantId), maxQuantity honors them.
  stock?: { quantity?: number | null; inStock?: boolean; };
  inventoryItem?: { quantity?: number | null; inStock?: boolean; trackQuantity?: boolean };
}
interface Stock { trackInventory?: boolean; inventoryStatus?: string; quantity?: number | null; }
interface VariantStock { quantity: number; trackQuantity: boolean; preorderEnabled: boolean }

// Single `product` prop (the full productsV3 object) mirrors ProductCard's
// contract so both components take the same shape. Keeps `[slug].astro`
// mount sites greppable: <ProductPurchase client:load product={product}
// inventoryByVariant={inventoryByVariant} />.
interface ProductLike {
  _id?: string | null;
  name?: string | null;
  actualPriceRange?: { minValue?: { currency?: string | null } | null } | null;
  options?: Option[] | null;
  modifiers?: Modifier[] | null;
  variantsInfo?: { variants?: Variant[] } | null;
  stock?: Stock | null;
}
interface ProductPurchaseProps {
  product: ProductLike;
  // Live per-variant stock from inventoryItemsV3, keyed by variantId.
  // AUTHORITATIVE source for OOS gating. productsV3's cached inStock flag is
  // not reliable — see PRODUCT_PAGES.md anti-patterns table.
  inventoryByVariant?: Record<string, VariantStock>;
  // SSR probe result from getBackInStockEnabled() — gates the OOS subscribe
  // form. When false, OOS branches render only the existing "Out of Stock"
  // / "Sold Out" stock-status copy. See references/BACK_IN_STOCK.md.
  backInStockEnabled?: boolean;
  // Numeric product price for the back-in-stock subscribe call. The Wix
  // endpoint validates `itemDetails.price >= 0` and rejects formatted
  // strings; pass a number, not "$695".
  priceAmount?: number;
}

export default function ProductPurchase({
  product,
  inventoryByVariant = {},
  backInStockEnabled = false,
  priceAmount,
}: ProductPurchaseProps) {
  const productId = product._id ?? "";
  const productName = product.name ?? "";
  const currency = product.actualPriceRange?.minValue?.currency ?? undefined;
  const options = product.options ?? [];
  const modifiers = product.modifiers ?? [];
  const variantsInfo = product.variantsInfo ?? { variants: [] };
  const stock = product.stock ?? undefined;

  const variants = variantsInfo.variants ?? [];
  const hasMeaningfulOptions = options.length > 0 && options.some(
    (opt) => (opt.choicesSettings?.choices?.length ?? 0) > 1,
  );
  const [selections, setSelections] = useState<Record<string, string>>({});
  const handleSelect = (optionId: string, choiceId: string) =>
    setSelections((prev) => ({ ...prev, [optionId]: choiceId }));
  const allSelected = hasMeaningfulOptions && options.every((opt) => opt._id && selections[opt._id]);

  // Modifier state. Two parallel maps keyed by modifier._id, flattened below
  // into the shapes cart expects.
  const [modifierChoice, setModifierChoice] = useState<Record<string, string>>({});
  const [modifierText, setModifierText] = useState<Record<string, string>>({});
  const handleModifierChoice = (id: string, key: string) => setModifierChoice((p) => ({ ...p, [id]: key }));
  const handleModifierText = (id: string, v: string) => setModifierText((p) => ({ ...p, [id]: v }));

  const mandatoryModifiersSatisfied = useMemo(() => modifiers.every((m) => {
    if (!m.mandatory) return true;
    const id = m._id ?? "";
    if (m.modifierRenderType === "FREE_TEXT") return (modifierText[id] ?? "").trim().length > 0;
    return !!modifierChoice[id];
  }), [modifiers, modifierChoice, modifierText]);

  // Flatten to catalogReference shapes:
  //   options          → { [modifier.key]: choice.key }    for TEXT_CHOICES / SWATCH_CHOICES
  //   customTextFields → { [freeTextSettings.key]: text }  for FREE_TEXT
  const catalogModifierChoices = useMemo(() => {
    const out: Record<string, string> = {};
    for (const m of modifiers) {
      if (!m.key || !m._id || m.modifierRenderType === "FREE_TEXT") continue;
      const c = modifierChoice[m._id];
      if (c) out[m.key] = c;
    }
    return out;
  }, [modifiers, modifierChoice]);
  const catalogCustomTextFields = useMemo(() => {
    const out: Record<string, string> = {};
    for (const m of modifiers) {
      if (!m._id || m.modifierRenderType !== "FREE_TEXT") continue;
      const k = m.freeTextSettings?.key;
      const v = (modifierText[m._id] ?? "").trim();
      if (k && v) out[k] = v;
    }
    return out;
  }, [modifiers, modifierText]);

  const resolvedVariant = useMemo(() => {
    if (!hasMeaningfulOptions) return variants[0] ?? null;
    if (!allSelected) return null;
    return variants.find((v) =>
      (v.choices ?? []).every(
        (c) => c.optionChoiceIds?.optionId &&
          selections[c.optionChoiceIds.optionId] === c.optionChoiceIds.choiceId,
      ),
    ) ?? null;
  }, [hasMeaningfulOptions, allSelected, selections, variants]);

  const variantLabel = useMemo(() => {
    if (!hasMeaningfulOptions) return undefined;
    return options.map((opt) => {
      const choiceId = opt._id ? selections[opt._id] : undefined;
      const choice = opt.choicesSettings?.choices?.find((c) => c.choiceId === choiceId);
      return choice?.name ? `${opt.name}: ${choice.name}` : null;
    }).filter(Boolean).join(", ") || undefined;
  }, [hasMeaningfulOptions, options, selections]);

  const variantPrice = resolvedVariant?.price?.actual?.amount
    ? Number(resolvedVariant.price.actual.amount)
    : undefined;

  // Binary OOS gate:
  //  - Source of truth = inventoryByVariant (from inventoryItemsV3).
  //  - Fallback = productsV3's variantsInfo[].inventoryStatus.inStock
  //    (stale, don't trust it unless the live map is empty).
  //  - productOutOfStock short-circuits the whole render (applies to the
  //    entire product e.g. unpublished or fully sold out).
  //  - variantOutOfStock keeps option pills visible so the shopper can
  //    pick a different finish; hides the stepper + button.
  const isVariantSoldOut = (variant: Variant | null | undefined): boolean => {
    if (!variant?._id) return false;
    const live = inventoryByVariant[variant._id];
    if (live) {
      if (!live.trackQuantity) return false;
      if (live.preorderEnabled) return false;
      return live.quantity <= 0;
    }
    return (
      variant.inventoryStatus?.inStock === false &&
      variant.inventoryStatus?.preorderEnabled !== true
    );
  };
  const productOutOfStock = stock?.inventoryStatus === "OUT_OF_STOCK";
  const variantOutOfStock = isVariantSoldOut(resolvedVariant);
  const isOutOfStock = productOutOfStock;
  // maxQuantity caps the stepper. Primary source: inventoryByVariant (live
  // from inventoryItemsV3). Fallbacks cover partial wirings. The cart
  // backend still enforces stock on add-to-cart — this clamp just avoids
  // letting shoppers build a quantity they can't actually buy.
  const maxQuantity = useMemo(() => {
    const live = resolvedVariant?._id ? inventoryByVariant[resolvedVariant._id] : undefined;
    if (live) {
      if (!live.trackQuantity) return 99;
      if (live.preorderEnabled) return 99;
      return Math.max(1, live.quantity);
    }
    if (stock?.trackInventory === false) return 99;
    if (resolvedVariant?.stock?.quantity != null) return resolvedVariant.stock.quantity;
    if (resolvedVariant?.inventoryItem?.quantity != null) return resolvedVariant.inventoryItem.quantity;
    if (stock?.quantity != null) return stock.quantity;
    return 99;
  }, [inventoryByVariant, stock, resolvedVariant]);
  // Count how much of each variant is already in the cart so the stepper cap
  // reflects "stock minus already-in-cart" instead of raw stock. Wix enforces
  // the same rule at add-to-cart time — this is just so the UI doesn't let
  // the shopper think they can add "max" after already adding "max".
  const [qtyInCartByVariant, setQtyInCartByVariant] = useState<Record<string, number>>({});
  useEffect(() => {
    let cancelled = false;
    const syncCart = async () => {
      try {
        const cart = await currentCart.getCurrentCart();
        if (cancelled) return;
        const tally: Record<string, number> = {};
        for (const item of cart.lineItems ?? []) {
          const ref = item.catalogReference as any;
          if (ref?.catalogItemId !== productId) continue;
          const vId = ref?.options?.variantId as string | undefined;
          if (!vId) continue;
          tally[vId] = (tally[vId] ?? 0) + (item.quantity ?? 0);
        }
        setQtyInCartByVariant(tally);
      } catch { if (!cancelled) setQtyInCartByVariant({}); }
    };
    syncCart();
    const handler = () => syncCart();
    window.addEventListener("cart-updated", handler);
    return () => { cancelled = true; window.removeEventListener("cart-updated", handler); };
  }, [productId]);

  const qtyInCartForResolved = resolvedVariant?._id ? qtyInCartByVariant[resolvedVariant._id] ?? 0 : 0;
  const effectiveMax = Math.max(0, maxQuantity - qtyInCartForResolved);
  const alreadyMaxedInCart = qtyInCartForResolved > 0 && effectiveMax === 0;

  const [quantity, setQuantity] = useState(1);
  // When max shrinks (variant switch, or cart sync), clamp the current selection.
  useEffect(() => { setQuantity((q) => Math.max(1, Math.min(q, Math.max(1, effectiveMax)))); }, [effectiveMax]);

  const quantitySelector = !isOutOfStock && (
    <div className="quantity-selector">
      <button className="quantity-btn" onClick={() => setQuantity((q) => Math.max(1, q - 1))} disabled={quantity <= 1}>−</button>
      <span className="quantity-value">{quantity}</span>
      <button className="quantity-btn" onClick={() => setQuantity((q) => Math.min(effectiveMax, q + 1))} disabled={quantity >= effectiveMax}>+</button>
    </div>
  );

  const inCartNote = qtyInCartForResolved > 0 && (
    <p className="stock-status" aria-live="polite">{qtyInCartForResolved} already in cart</p>
  );

  // Modifier selectors — rendered between options and quantity in both branches.
  const modifierSelectors = modifiers.length > 0 && (
    <>
      {modifiers.map((m) => {
        const id = m._id ?? "";
        const req = m.mandatory === true;
        if (m.modifierRenderType === "FREE_TEXT") {
          return (
            <div key={id} className="option-group">
              <div className="option-label">{m.name}{req && <span aria-hidden="true"> *</span>}</div>
              <textarea className="modifier-text"
                value={modifierText[id] ?? ""}
                onChange={(e) => handleModifierText(id, e.target.value)}
                placeholder={m.freeTextSettings?.title ?? ""}
                maxLength={m.freeTextSettings?.maxLength ?? undefined}
                rows={2} aria-label={m.name ?? ""} aria-required={req || undefined}
              />
            </div>
          );
        }
        const choices = m.choicesSettings?.choices ?? [];
        return (
          <div key={id} className="option-group">
            <div className="option-label">{m.name}{req && <span aria-hidden="true"> *</span>}</div>
            <div className="option-choices">
              {choices.map((c) => {
                const k = c.key ?? c.choiceId ?? "";
                const sel = modifierChoice[id] === k;
                return (
                  <button key={k} type="button" onClick={() => handleModifierChoice(id, k)}
                    className={`option-pill${sel ? " selected" : ""}`} aria-pressed={sel}>
                    {c.name}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </>
  );

  // Render the back-in-stock subscribe form in OOS branches when the
  // dashboard probe is on. Variant-aware: pass the resolved variantId when
  // a single variant is OOS, omit it when the whole product is OOS. The
  // form sends only required fields per the bare-fields rule
  // (BACK_IN_STOCK.md) — no itemUrl, no image.
  const renderBackInStockForm = (variantIdForForm?: string) =>
    backInStockEnabled ? (
      <BackInStockForm
        productId={productId}
        variantId={variantIdForForm}
        productName={productName}
        productPrice={variantPrice ?? priceAmount ?? 0}
        variantLabel={variantIdForForm ? variantLabel : undefined}
      />
    ) : null;

  if (isOutOfStock) {
    return (
      <div className="purchase-area">
        <p className="stock-status">Out of Stock</p>
        {renderBackInStockForm()}
      </div>
    );
  }

  if (!hasMeaningfulOptions) {
    const singleVariant = variants[0];
    const singleVariantOOS = isVariantSoldOut(singleVariant);
    if (singleVariantOOS) {
      return (
        <div className="purchase-area">
          <p className="stock-status">Sold Out</p>
          {renderBackInStockForm(singleVariant?._id ?? undefined)}
        </div>
      );
    }
    return (
      <div className="purchase-area">
        {modifierSelectors}
        {inCartNote}
        {alreadyMaxedInCart ? (
          <p className="stock-status">Maximum quantity already in cart</p>
        ) : (
          <>
            {quantitySelector}
            <AddToCartButton
              productId={productId} productName={productName}
              price={variantPrice} currency={currency}
              variantId={singleVariant?._id ?? undefined}
              quantity={quantity}
              modifierChoices={catalogModifierChoices}
              customTextFields={catalogCustomTextFields}
              disabled={!mandatoryModifiersSatisfied}
            />
          </>
        )}
      </div>
    );
  }

  return (
    <div className="purchase-area">
      {options.map((option) => {
        const choices = option.choicesSettings?.choices ?? [];
        const optionId = option._id ?? "";
        return (
          <div key={optionId} className="option-group">
            <div className="option-label">{option.name}</div>
            <div className="option-choices">
              {choices.map((choice) => {
                const choiceId = choice.choiceId ?? "";
                const isSelected = selections[optionId] === choiceId;
                return (
                  <button key={choiceId} onClick={() => handleSelect(optionId, choiceId)}
                    className={`option-pill${isSelected ? " selected" : ""}`}>
                    {choice.name}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
      {modifierSelectors}
      {variantOutOfStock ? (
        <>
          {renderBackInStockForm(resolvedVariant?._id ?? undefined)}
          <p className="stock-status back-in-stock-alt">
            Or try another option above.
          </p>
        </>
      ) : alreadyMaxedInCart ? (
        <>
          {inCartNote}
          <p className="stock-status">Maximum quantity already in cart</p>
        </>
      ) : (
        <>
          {inCartNote}
          {quantitySelector}
          <AddToCartButton
            productId={productId} productName={productName}
            price={variantPrice} currency={currency}
            variantId={resolvedVariant?._id ?? undefined}
            variantName={variantLabel} quantity={quantity}
            modifierChoices={catalogModifierChoices}
            customTextFields={catalogCustomTextFields}
            disabled={!resolvedVariant || !mandatoryModifiersSatisfied}
          />
        </>
      )}
    </div>
  );
}
