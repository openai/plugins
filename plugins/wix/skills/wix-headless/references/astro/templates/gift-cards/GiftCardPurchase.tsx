import { useState } from "react";
import { currentCart } from "@wix/ecom";
import { trackEvent } from "../utils/analytics";
import {
  WIX_GIFT_CARDS_APP_ID,
  type GiftCardProduct,
  type GiftCardPresetVariant,
} from "../utils/gift-cards";

interface GiftCardPurchaseProps {
  product: GiftCardProduct;
}

// catalogReference shape captured from a real paid Wix-Editor order:
//   { appId: WIX_GIFT_CARDS_APP_ID,
//     catalogItemId: <giftCardProduct.id>,
//     options: { variantId, quantity, currency, giftingInfo, wixGiftCardsAppNewCatalog: true } }
// On ORDER_PAID, Wix's gift-card backend auto-issues a redeemable card with
// source: "ORDER" and emails the recipient — no follow-up API call needed.
export default function GiftCardPurchase({ product }: GiftCardPurchaseProps) {
  const [variantId, setVariantId] = useState<string>(product.presetVariants[0]?.id ?? "");
  const [recipientFirstName, setRecipientFirstName] = useState("");
  const [recipientLastName, setRecipientLastName] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [greetingMessage, setGreetingMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "adding" | "added" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const selectedVariant: GiftCardPresetVariant | undefined =
    product.presetVariants.find((v) => v.id === variantId);

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipientEmail);
  const canSubmit =
    !!selectedVariant &&
    recipientFirstName.trim().length > 0 &&
    emailValid &&
    status !== "adding";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || !selectedVariant) return;
    setStatus("adding");
    setError(null);
    try {
      const { cart } = await currentCart.addToCurrentCart({
        lineItems: [
          {
            catalogReference: {
              appId: WIX_GIFT_CARDS_APP_ID,
              catalogItemId: product.id,
              options: {
                variantId: selectedVariant.id,
                quantity: 1,
                giftingInfo: {
                  recipientInfo: {
                    email: recipientEmail.trim(),
                    firstName: recipientFirstName.trim(),
                    lastName: recipientLastName.trim(),
                  },
                  greetingMessage: greetingMessage.trim(),
                },
                wixGiftCardsAppNewCatalog: true,
              } as Record<string, unknown>,
            },
            quantity: 1,
          },
        ],
      });
      window.dispatchEvent(new CustomEvent("cart-updated", { detail: { cart, delta: 1 } }));
      trackEvent("AddToCart", {
        id: product.id,
        name: product.name,
        price: Number(selectedVariant.price.amount),
        quantity: 1,
        variant: selectedVariant.price.formattedAmount,
        origin: "Gift Card Page",
      });
      setStatus("added");
      window.location.href = "/cart";
    } catch (err: any) {
      console.error("[gift-cards] addToCurrentCart failed:", err);
      setError(err?.message ?? "Could not add the gift card to your cart. Please try again.");
      setStatus("error");
    }
  };

  return (
    <form className="gift-card-form" onSubmit={handleSubmit} noValidate>
      <fieldset className="gift-card-fieldset">
        <legend className="option-label">Amount</legend>
        <div className="gift-card-amounts">
          {product.presetVariants.map((v) => {
            const sel = v.id === variantId;
            return (
              <button
                key={v.id}
                type="button"
                onClick={() => setVariantId(v.id)}
                className={`option-pill${sel ? " selected" : ""}`}
                aria-pressed={sel}
              >
                {v.price.formattedAmount}
              </button>
            );
          })}
        </div>
      </fieldset>

      <div className="gift-card-grid">
        <label className="gift-card-field">
          <span className="option-label">Recipient first name *</span>
          <input
            type="text"
            value={recipientFirstName}
            onChange={(e) => setRecipientFirstName(e.target.value)}
            required
            autoComplete="off"
          />
        </label>

        <label className="gift-card-field">
          <span className="option-label">Recipient last name</span>
          <input
            type="text"
            value={recipientLastName}
            onChange={(e) => setRecipientLastName(e.target.value)}
            autoComplete="off"
          />
        </label>

        <label className="gift-card-field gift-card-field-wide">
          <span className="option-label">Recipient email *</span>
          <input
            type="email"
            value={recipientEmail}
            onChange={(e) => setRecipientEmail(e.target.value)}
            required
            autoComplete="off"
          />
        </label>

        <label className="gift-card-field gift-card-field-wide">
          <span className="option-label">Personal message</span>
          <textarea
            value={greetingMessage}
            onChange={(e) => setGreetingMessage(e.target.value.slice(0, 500))}
            maxLength={500}
            rows={3}
            placeholder="A short note to the recipient…"
          />
          <span className="gift-card-counter">{greetingMessage.length} / 500</span>
        </label>
      </div>

      {error && <p className="gift-card-error" role="alert">{error}</p>}

      <button
        type="submit"
        disabled={!canSubmit}
        className="add-to-cart-btn"
      >
        {status === "adding"
          ? "Adding…"
          : status === "added"
            ? "Added ✓"
            : selectedVariant
              ? `Add ${selectedVariant.price.formattedAmount} gift card to cart`
              : "Add to cart"}
      </button>
    </form>
  );
}
