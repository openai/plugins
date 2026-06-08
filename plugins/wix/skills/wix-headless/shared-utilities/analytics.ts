export type AnalyticsEventName =
  | "AddToCart"
  | "RemoveFromCart"
  | "InitiateCheckout"
  | "Purchase"
  | "ArticleView"
  | "FormSubmit"
  | "AddProductImpression"
  | "ViewContent"
  | "ClickProduct"
  | (string & {});

export function trackEvent(
  name: AnalyticsEventName,
  payload?: Record<string, unknown>,
): void {
  if (typeof window === "undefined") return;

  const event = { name, ...(payload ?? {}) };

  const w = window as unknown as {
    dataLayer?: unknown[];
    wixAnalytics?: { track(event: { name: string } & Record<string, unknown>): void };
  };

  if (w.wixAnalytics?.track) {
    w.wixAnalytics.track(event);
    return;
  }

  if (w.dataLayer) {
    w.dataLayer.push({ event: name, ...event });
    return;
  }

  const meta = import.meta as unknown as { env?: { DEV?: boolean } };
  if (meta.env?.DEV) {
    console.debug("[analytics]", event);
  }
}
