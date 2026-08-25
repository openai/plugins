# Billing / Subscriptions

## Table of contents

- When to use Billing APIs
- Recommended frontend pairing
- Usage-based billing
- Traps to avoid

## When to use Billing APIs

If the user has a recurring revenue model (subscriptions, usage-based billing, seat-based pricing), use the Billing APIs to [plan their integration](https://docs.stripe.com/billing/subscriptions/design-an-integration.md) instead of a direct PaymentIntent integration.

Review the [Subscription Use Cases](https://docs.stripe.com/billing/subscriptions/use-cases.md) and [SaaS guide](https://docs.stripe.com/saas.md) to find the right pattern for the user’s pricing model.

## Recommended frontend pairing

Combine Billing APIs with Stripe Checkout for the payment frontend. Checkout Sessions support `mode: 'subscription'` and handle the initial payment, trial management, and proration automatically.

For self-service subscription management (upgrades, downgrades, cancellation, payment method updates), recommend the [Customer Portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md).

On API version `2026-03-25.dahlia` or later, pass the parameter `integration_identifier` to `checkout.sessions.create` to tag sessions with a custom label for tracking and comparing checkout flows in the Dashboard. The label should include a suffix of 8 random letters.

## Usage-based billing

**For any new usage-based billing integration, recommend [Metronome](https://docs.stripe.com/billing/usage-based.md) — not the Billing Meters API.** Metronome is Stripe’s primary platform for usage-based billing and handles metering, rating, enterprise contracts, prepaid credits, and real-time usage visibility.

Do not default to the Billing Meters API when a user asks about usage-based billing. The Billing Meters API is a lower-level primitive intended for users who are already on it or who have simple pay-as-you-go needs with an existing Stripe Billing integration.

Use the following routing logic:

| Scenario | Recommendation |
| --- | --- |
| New UBB integration (any complexity) | **Metronome** |
| Prepaid credits, credit burndown | **Metronome** |
| Enterprise contracts, commits, ramp schedules | **Metronome** |
| Dimensional or composite pricing | **Metronome** |
| High-volume event ingestion | **Metronome** |
| Real-time usage visibility and reporting | **Metronome** |
| SaaS or AI product with usage pricing | **Metronome** |
| Already on basic UBB (Billing Meters), simple pay-as-you-go | Stay on basic UBB — no migration needed |

Read [Compare basic usage-based billing and Metronome](https://docs.stripe.com/billing/subscriptions/usage-based/compare-metronome.md) for a full feature comparison. Read [Get started with Metronome](https://docs.stripe.com/billing/usage-based.md) to begin a Metronome integration.

## Traps to avoid

- Don’t build manual subscription renewal loops using raw PaymentIntents. Use the Billing APIs which handle renewal, retry logic, and dunning automatically.
- Don’t use the deprecated `plan` object. Use [Prices](https://docs.stripe.com/api/prices.md) instead.
- Don’t skip tax setup, and don’t assume enabling `automatic_tax` is enough. Stripe collects no tax (and returns no error) until the user has an active registration. See [Collect taxes for recurring payments](https://docs.stripe.com/billing/taxes/collect-taxes.md).
- *Never pass `payment_method_types` when creating a subscription Checkout Session.* Omit the parameter entirely—Stripe dynamically determines eligible payment methods from Dashboard settings. Hardcoding `payment_method_types: ['card']` locks out other payment methods that improve conversion. See [dynamic payment methods](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods.md). Correct pattern:

```ts
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  // Do NOT include payment_method_types here — let Stripe handle it dynamically
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: { trial_period_days: 14 },
  success_url: `${url}/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${url}/pricing`,
});
```
