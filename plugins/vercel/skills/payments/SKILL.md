---
name: payments
description: Stripe payments integration guidance — native Vercel Marketplace setup, checkout sessions, webhook handling, subscription billing, and the Stripe SDK. Use when implementing payments, subscriptions, or processing transactions.
metadata:
  priority: 5
  docs:
    - "https://docs.stripe.com"
    - "https://docs.stripe.com/payments/quickstart"
  sitemap: "https://docs.stripe.com/sitemap.xml"
  pathPatterns:
    - 'app/api/webhook/stripe/**'
    - 'app/api/webhooks/stripe/**'
    - 'src/app/api/webhook/stripe/**'
    - 'src/app/api/webhooks/stripe/**'
    - 'pages/api/webhook/stripe.*'
    - 'pages/api/webhooks/stripe.*'
    - 'app/api/checkout/**'
    - 'src/app/api/checkout/**'
    - 'app/api/stripe/**'
    - 'src/app/api/stripe/**'
    - 'lib/stripe.*'
    - 'src/lib/stripe.*'
    - 'utils/stripe.*'
    - 'src/utils/stripe.*'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bstripe\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bstripe\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bstripe\b'
    - '\byarn\s+add\s+[^\n]*\bstripe\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@stripe/stripe-js\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@stripe/stripe-js\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@stripe/stripe-js\b'
    - '\byarn\s+add\s+[^\n]*@stripe/stripe-js\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@stripe/react-stripe-js\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@stripe/react-stripe-js\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@stripe/react-stripe-js\b'
    - '\byarn\s+add\s+[^\n]*@stripe/react-stripe-js\b'
---

# Stripe Payments Integration

You are an expert in Stripe payments for Vercel-deployed applications — covering the native Vercel Marketplace integration, Checkout Sessions, webhook handling, subscription billing, and the Stripe Node.js SDK.

## Vercel Marketplace Setup (Recommended)

Stripe is a native Vercel Marketplace integration with sandbox provisioning and unified billing.

### Install via Marketplace

```bash
# Install Stripe from Vercel Marketplace (auto-provisions sandbox + env vars)
vercel integration add stripe
```

Auto-provisioned environment variables:
- `STRIPE_SECRET_KEY` — server-side API key
- `STRIPE_PUBLISHABLE_KEY` — client-side publishable key
- `STRIPE_WEBHOOK_SECRET` — webhook endpoint signing secret

### SDK Setup

```bash
# Server-side SDK
npm install stripe

# Client-side SDK (for Stripe Elements / Checkout)
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### Initialize the Stripe Client

```ts
// lib/stripe.ts
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-02-25.clover",
  typescript: true,
});
```

## Checkout Sessions

### Server Action (Recommended for 2026)

Server Actions are the preferred pattern for creating Checkout Sessions in Next.js 15+, eliminating the need for API routes:

```ts
// app/actions/checkout.ts
"use server";
import { redirect } from "next/navigation";
import { stripe } from "@/lib/stripe";

export async function createCheckoutSession(priceId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/cancel`,
  });

  redirect(session.url!);
}
```

```tsx
// app/pricing/page.tsx
import { createCheckoutSession } from "@/app/actions/checkout";

export default function PricingPage() {
  return (
    <form action={createCheckoutSession.bind(null, "price_xxx")}>
      <button type="submit">Buy Now</button>
    </form>
  );
}
```

### Create a Checkout Session (API Route)

```ts
// app/api/checkout/route.ts
import { NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";

export async function POST(req: Request) {
  const { priceId } = await req.json();

  const session = await stripe.checkout.sessions.create({
    mode: "payment", // or "subscription" for recurring
    payment_method_types: ["card"],
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/cancel`,
  });

  return NextResponse.json({ url: session.url });
}
```

### Redirect to Checkout (Client)

```tsx
"use client";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export function CheckoutButton({ priceId }: { priceId: string }) {
  const handleCheckout = async () => {
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ priceId }),
    });
    const { url } = await res.json();
    window.location.href = url;
  };

  return <button onClick={handleCheckout}>Subscribe</button>;
}
```

## Webhook Handling

Stripe sends events to your webhook endpoint for asynchronous payment processing. Always verify the signature.

```ts
// app/api/webhook/stripe/route.ts
import { NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import Stripe from "stripe";

export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get("stripe-signature")!;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      // Fulfill the order — update database, send confirmation, etc.
      break;
    }
    case "invoice.payment_succeeded": {
      const invoice = event.data.object as Stripe.Invoice;
      // Handle successful subscription renewal
      break;
    }
    case "customer.subscription.deleted": {
      const subscription = event.data.object as Stripe.Subscription;
      // Handle cancellation — revoke access
      break;
    }
  }

  return NextResponse.json({ received: true });
}
```

**Important**: Webhook routes must read the raw body as text (not JSON) for signature verification. Do not add `bodyParser` or JSON middleware to webhook routes.

## Subscription Billing

### Create a Subscription Checkout

```ts
const session = await stripe.checkout.sessions.create({
  mode: "subscription",
  line_items: [{ price: priceId, quantity: 1 }],
  success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
});
```

### Customer Portal

Allow customers to manage their subscriptions:

```ts
// app/api/portal/route.ts
import { stripe } from "@/lib/stripe";

export async function POST(req: Request) {
  const { customerId } = await req.json();

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  });

  return Response.json({ url: session.url });
}
```

## Embedded Checkout (Recommended)

Stripe's Embedded Checkout renders inside your page via an iframe, keeping users on your domain while offloading PCI compliance to Stripe:

```ts
// app/actions/embedded-checkout.ts
"use server";
import { stripe } from "@/lib/stripe";

export async function createEmbeddedCheckout(priceId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: priceId, quantity: 1 }],
    ui_mode: "embedded",
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
  });

  return { clientSecret: session.client_secret! };
}
```

```tsx
"use client";
import { loadStripe } from "@stripe/stripe-js";
import { EmbeddedCheckoutProvider, EmbeddedCheckout } from "@stripe/react-stripe-js";
import { createEmbeddedCheckout } from "@/app/actions/embedded-checkout";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export function CheckoutEmbed({ priceId }: { priceId: string }) {
  return (
    <EmbeddedCheckoutProvider
      stripe={stripePromise}
      options={{ fetchClientSecret: () => createEmbeddedCheckout(priceId).then(r => r.clientSecret) }}
    >
      <EmbeddedCheckout />
    </EmbeddedCheckoutProvider>
  );
}
```

## Stripe Elements (Custom Forms)

```tsx
"use client";
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: `${window.location.origin}/success` },
    });

    if (error) console.error(error.message);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button type="submit" disabled={!stripe}>Pay</button>
    </form>
  );
}

export function PaymentForm({ clientSecret }: { clientSecret: string }) {
  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <CheckoutForm />
    </Elements>
  );
}
```

## Environment Variables

| Variable | Scope | Description |
|----------|-------|-------------|
| `STRIPE_SECRET_KEY` | Server | API secret key (starts with `sk_`) |
| `STRIPE_PUBLISHABLE_KEY` | Client | Publishable key (starts with `pk_`) |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Client | Alias exposed to browser via Next.js |
| `STRIPE_WEBHOOK_SECRET` | Server | Webhook signing secret (starts with `whsec_`) |

## Cross-References

- **Marketplace install and env var provisioning** → `⤳ skill: marketplace`
- **Webhook route patterns** → `⤳ skill: routing-middleware`
- **Environment variable management** → `⤳ skill: env-vars`
- **Serverless function config** → `⤳ skill: vercel-functions`

## Official Documentation

- [Stripe + Vercel Marketplace](https://vercel.com/marketplace/stripe)
- [Stripe Node.js SDK](https://docs.stripe.com/sdks)
- [Stripe Checkout](https://docs.stripe.com/payments/checkout)
- [Stripe Webhooks](https://docs.stripe.com/webhooks)
- [Stripe Elements](https://docs.stripe.com/payments/elements)
