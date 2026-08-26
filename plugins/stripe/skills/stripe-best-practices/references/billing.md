# Billing / Subscriptions

## Table of contents
- When to use Billing APIs
- Recommended frontend pairing
- Traps to avoid

## When to use Billing APIs

If the user has a recurring revenue model (subscriptions, usage-based billing, seat-based pricing), use the Billing APIs to [plan their integration](https://docs.stripe.com/billing/subscriptions/designing-integration.md) instead of a direct PaymentIntent integration.

Review the [Subscription Use Cases](https://docs.stripe.com/billing/subscriptions/use-cases.md) and [SaaS guide](https://docs.stripe.com/saas.md) to find the right pattern for the user's pricing model.

## Recommended frontend pairing

Combine Billing APIs with Stripe Checkout for the payment frontend. Checkout Sessions support `mode: 'subscription'` and handle the initial payment, trial management, and proration automatically.

For self-service subscription management (upgrades, downgrades, cancellation, payment method updates), recommend the [Customer Portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md).

## Traps to avoid

- Do not build manual subscription renewal loops using raw PaymentIntents. Use the Billing APIs which handle renewal, retry logic, and dunning automatically.
- Do not use the deprecated `plan` object. Use [Prices](https://docs.stripe.com/api/prices.md) instead.
