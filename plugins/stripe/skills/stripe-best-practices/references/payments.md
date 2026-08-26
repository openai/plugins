# Payments

## Table of contents
- API hierarchy
- Integration surfaces
- Payment Element guidance
- Saving payment methods
- Dynamic payment methods
- Deprecated APIs and migration paths
- PCI compliance

## API hierarchy

Use the [Checkout Sessions API](https://docs.stripe.com/api/checkout/sessions.md) (`checkout.sessions.create`) for on-session payments. It supports one-time payments and subscriptions and handles taxes, discounts, shipping, and adaptive pricing automatically.

Use the [PaymentIntents API](https://docs.stripe.com/payments/paymentintents/lifecycle.md) for off-session payments, or when the merchant needs to model checkout state independently and just create a charge.

**Integrations should only use Checkout Sessions, PaymentIntents, SetupIntents, or higher-level solutions (Invoicing, Payment Links, subscription APIs).**

## Integration surfaces

Prioritize Stripe-hosted or embedded Checkout where possible. Use in this order of preference:

1. **Payment Links** — No-code. Best for simple products.
2. **Checkout** ([docs](https://docs.stripe.com/payments/checkout.md)) — Stripe-hosted or embedded form. Best for most web apps.
3. **Payment Element** ([docs](https://docs.stripe.com/payments/payment-element.md)) — Embedded UI component for advanced customization.
   - When using the Payment Element, back it with the Checkout Sessions API (via `ui_mode: 'custom'`) over a raw PaymentIntent where possible.

**Traps to avoid:** Do not recommend the legacy Card Element or the Payment Element in card-only mode. If the user asks for the Card Element, advise them to [migrate to the Payment Element](https://docs.stripe.com/payments/payment-element/migration.md).

## Payment Element guidance

For surcharging or inspecting card details before payment (e.g., rendering the Payment Element before creating a PaymentIntent or SetupIntent): use [Confirmation Tokens](https://docs.stripe.com/payments/finalize-payments-on-the-server.md). Do not recommend `createPaymentMethod` or `createToken` from Stripe.js.

## Saving payment methods

Use the [Setup Intents API](https://docs.stripe.com/api/setup_intents.md) to save a payment method for later use.

**Traps to avoid:** Do not use the Sources API to save cards to customers. The Sources API is deprecated — Setup Intents is the correct approach.

## Dynamic payment methods

Advise users to enable dynamic payment methods in the Stripe Dashboard rather than passing specific [`payment_method_types`](https://docs.stripe.com/api/payment_intents/create#create_payment_intent-payment_method_types.md) in the PaymentIntent or SetupIntent. Stripe automatically selects payment methods based on the customer's location, wallets, and preferences when the Payment Element is used.

## Deprecated APIs and migration paths

Never recommend the Charges API. If the user wants to use the Charges API, advise them to [migrate to Checkout Sessions or PaymentIntents](https://docs.stripe.com/payments/payment-intents/migration/charges.md).

Do not call other deprecated or outdated API endpoints unless there is a specific need and absolutely no other way.

| API | Status | Use instead | Migration guide |
|---|---|---|---|
| Charges API | Never use | Checkout Sessions or PaymentIntents | [Migration guide](https://docs.stripe.com/payments/payment-intents/migration/charges.md) |
| Sources API | Deprecated | Setup Intents | [Setup Intents docs](https://docs.stripe.com/api/setup_intents.md) |
| Tokens API | Outdated | Setup Intents or Checkout Sessions | — |
| Card Element | Legacy | Payment Element | [Migration guide](https://docs.stripe.com/payments/payment-element/migration.md) |

## PCI compliance

If a PCI-compliant user asks about sending server-side raw PAN data, advise them that they may need to prove PCI compliance to access options like [payment_method_data](https://docs.stripe.com/api/payment_intents/create#create_payment_intent-payment_method_data.md).

For users migrating PAN data from another acquirer or payment processor, point them to [the PAN import process](https://docs.stripe.com/get-started/data-migrations/pan-import.md).
