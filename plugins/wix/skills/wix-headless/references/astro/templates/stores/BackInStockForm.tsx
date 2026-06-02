import { useState } from "react";
import { backInStockNotifications } from "@wix/ecom";
import { WIX_STORES_BACK_IN_STOCK_APP_ID } from "../utils/back-in-stock";

interface BackInStockFormProps {
  productId: string;
  variantId?: string;
  productName: string;
  // Numeric price (number or numeric string). The Wix backend validates
  // `itemDetails.price >= 0` against the parsed decimal, so currency-
  // formatted strings ("$695") are stripped here before submission.
  productPrice: number | string;
  variantLabel?: string;
}

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; alreadySubscribed?: boolean }
  | { kind: "error"; message: string };

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function normalizePrice(raw: number | string): string {
  const s =
    typeof raw === "number" ? String(raw) : String(raw).replace(/[^0-9.]/g, "");
  const n = Number(s);
  return Number.isFinite(n) && n >= 0 ? s : "0";
}

function readErrorCode(err: unknown): string | undefined {
  if (!err || typeof err !== "object") return undefined;
  // Wix SDK errors expose details.applicationError.code; some shapes also
  // surface a top-level details.code or http status. Try the common ones.
  const e = err as Record<string, any>;
  return (
    e?.details?.applicationError?.code ??
    e?.details?.code ??
    e?.applicationError?.code ??
    undefined
  );
}

export default function BackInStockForm({
  productId,
  variantId,
  productName,
  productPrice,
  variantLabel,
}: BackInStockFormProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  const submitting = status.kind === "submitting";
  const success = status.kind === "success";

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (submitting) return;
    if (!EMAIL_RE.test(email)) {
      setStatus({ kind: "error", message: "Enter a valid email." });
      return;
    }
    setStatus({ kind: "submitting" });

    // Bare-fields rule: the SDK throws an opaque
    // "TypeError: Failed to construct 'URL': Invalid URL" when the optional
    // request.itemUrl or itemDetails.image fields are present, even with
    // browser-valid URLs. Send only the four required fields:
    // catalogReference, email, name, price. The dashboard's Back-in-Stock
    // Requests view + the customer notification email both work without
    // them; the email just won't have a thumbnail and the dashboard uses
    // its default item URL.
    const request = {
      catalogReference: {
        appId: WIX_STORES_BACK_IN_STOCK_APP_ID,
        catalogItemId: productId,
        ...(variantId ? { options: { variantId } } : {}),
      },
      email,
    };
    const itemDetails = {
      name: productName,
      price: normalizePrice(productPrice),
    };

    try {
      await backInStockNotifications.createBackInStockNotificationRequest(
        request,
        itemDetails,
      );
      setStatus({ kind: "success" });
    } catch (err) {
      const code = readErrorCode(err);
      if (code === "BACK_IN_STOCK_NOTIFICATION_REQUEST_ALREADY_EXISTS") {
        setStatus({ kind: "success", alreadySubscribed: true });
        return;
      }
      if (code === "REQUEST_COLLECTION_DISABLED") {
        setStatus({
          kind: "error",
          message: "Notifications aren't being collected right now.",
        });
        return;
      }
      console.error("[back-in-stock] subscribe failed:", err);
      setStatus({
        kind: "error",
        message: "Something went wrong. Please try again.",
      });
    }
  }

  if (success) {
    return (
      <div className="back-in-stock-success" role="status" aria-live="polite">
        <p className="back-in-stock-success-headline">
          {status.alreadySubscribed
            ? "You're already on the list."
            : "We'll let you know."}
        </p>
        <p className="back-in-stock-success-detail">
          {status.alreadySubscribed
            ? `We had your note for ${productName}${variantLabel ? ` (${variantLabel})` : ""}. We'll email ${email} the moment it's back.`
            : `We'll email ${email} the moment ${productName}${variantLabel ? ` (${variantLabel})` : ""} is back in stock.`}
        </p>
      </div>
    );
  }

  return (
    <form className="back-in-stock-form" onSubmit={handleSubmit} noValidate>
      <div className="back-in-stock-headline">
        <span className="back-in-stock-eyebrow">Currently sold out</span>
        <p className="back-in-stock-lede">
          Leave your email and we'll notify you the moment
          {variantLabel ? ` ${variantLabel.toLowerCase()}` : ""} is back in
          stock.
        </p>
      </div>
      <label className="back-in-stock-label" htmlFor="back-in-stock-email">
        Email
      </label>
      <div className="back-in-stock-row">
        <input
          id="back-in-stock-email"
          type="email"
          inputMode="email"
          autoComplete="email"
          required
          placeholder="you@example.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (status.kind === "error") setStatus({ kind: "idle" });
          }}
          className="back-in-stock-input"
          aria-invalid={status.kind === "error"}
          disabled={submitting}
        />
        <button
          type="submit"
          className="back-in-stock-submit"
          disabled={submitting || email.trim().length === 0}
        >
          {submitting ? "Sending…" : "Notify me"}
        </button>
      </div>
      {status.kind === "error" && (
        <p className="back-in-stock-error" role="alert">
          {status.message}
        </p>
      )}
    </form>
  );
}
