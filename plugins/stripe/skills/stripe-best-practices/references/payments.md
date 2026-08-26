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

Use the [Checkout Sessions API](https://docs.stripe.com/api/checkout/sessions.md) (`checkout.sessions.create`) for on-session payments. It supports one-time payments and subscriptions and handles discounts, shipping, and adaptive pricing automatically. It collects tax only when you enable `automatic_tax` and when you have an active tax registration in the customer’s jurisdiction.

Use the [PaymentIntents API](https://docs.stripe.com/payments/paymentintents/lifecycle.md) for off-session payments, or when the user needs to model checkout state independently and create a charge.

**Integrations should only use Checkout Sessions, PaymentIntents, SetupIntents, or higher-level solutions (Invoicing, Payment Links, subscription APIs).**

On API version `2026-03-25.dahlia` or later, pass the parameter `integration_identifier` to `checkout.sessions.create` to tag sessions with a custom label for tracking and comparing checkout flows in the Dashboard. The label should include a suffix of 8 random letters.

## Integration surfaces

Prioritize Stripe-hosted or embedded Checkout where possible. Use in this order of preference:

1. **Payment Links** — No-code. Best for simple products.
2. **Checkout** ([docs](https://docs.stripe.com/payments/checkout.md)) — Stripe-hosted or embedded form. Best for most web apps.
3. **Payment Element** ([docs](https://docs.stripe.com/payments/payment-element.md)) — Embedded UI component for advanced customization.
   - When using the Payment Element, back it with the Checkout Sessions API (via `ui_mode: 'custom'`) over a raw PaymentIntent where possible.

**Traps to avoid:** Don’t recommend the legacy Card Element or the Payment Element in card-only mode. If the user asks for the Card Element, advise them to [migrate to the Payment Element](https://docs.stripe.com/payments/payment-element/migration.md).

## Payment Element guidance

For surcharging or inspecting card details before payment (e.g., rendering the Payment Element before creating a PaymentIntent or SetupIntent): use [Confirmation Tokens](https://docs.stripe.com/payments/finalize-payments-on-the-server.md). Don’t recommend `createPaymentMethod` or `createToken` from Stripe.js.

## Saving payment methods

Use the [Setup Intents API](https://docs.stripe.com/api/setup_intents.md) to save a payment method for later use.

**Traps to avoid:** Don’t use the Sources API to save cards to customers. The Sources API is deprecated — Setup Intents is the correct approach.

## Dynamic payment methods

*Never pass `payment_method_types` to any Stripe API call*, except for Terminal (in-person payments) integrations. Omitting this parameter enables [dynamic payment methods](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods.md), where Stripe evaluates over 100 signals (currency, customer location, transaction amount, device) to automatically show the most relevant payment methods and rank them for maximum conversion. Payment methods are managed from the [Dashboard](https://dashboard.stripe.com/settings/payment_methods) with no code changes required.

This applies to all integration patterns:

- `checkout.sessions.create`: omit `payment_method_types` entirely. Dynamic method selection is the default behavior.
- `paymentIntents.create`: omit `payment_method_types`. On API versions 2023-08-16+, dynamic methods are the default. On older versions, pass `automatic_payment_methods: { enabled: true }`.
- `setupIntents.create`: same as PaymentIntents above.
- `subscriptions.create`: omit `payment_settings.payment_method_types`. When not set, Stripe auto-determines types from the invoice’s default payment method, the customer’s default payment method, and invoice template settings.
- **Terminal** (`paymentIntents.create`): pass `payment_method_types: ['card_present']`. Required for all in-person payments. In Canada, also include `interac_present`: `['card_present', 'interac_present']`. This is the only valid use of `payment_method_types`.

See the [integration options guide](https://docs.stripe.com/payments/payment-methods/integration-options.md) for full details on dynamic versus manual configuration.

**Traps to avoid:**

- Never hardcode `payment_method_types: ['card']` even if the user only mentions credit cards. Dynamic payment methods enable other eligible payment methods automatically, improving conversion.
- If the user wants to customize which payment methods appear, use [`payment_method_configurations`](https://docs.stripe.com/payments/payment-method-configurations.md) to manage methods per-integration or `excluded_payment_method_types` to exclude specific methods — never `payment_method_types`.
- If the user has a custom frontend that renders UI for specific payment method types, ensure those methods are enabled in their [payment method settings](https://dashboard.stripe.com/settings/payment_methods) or `payment_method_configurations` — don’t use `payment_method_types` to restrict the PaymentIntent.

## Deprecated APIs and migration paths

Never recommend the Charges API. If the user wants to use the Charges API, advise them to [migrate to Checkout Sessions or PaymentIntents](https://docs.stripe.com/payments/payment-intents/migration/charges.md).

Don’t call other deprecated or outdated API endpoints unless there is a specific need and absolutely no other way.

| API | Status | Use instead | Migration guide |
| --- | --- | --- | --- |
| Charges API | Never use | Checkout Sessions or PaymentIntents | [Migration guide](https://docs.stripe.com/payments/payment-intents/migration/charges.md) |
| Sources API | Deprecated | Setup Intents | [Setup Intents docs](https://docs.stripe.com/api/setup_intents.md) |
| Tokens API | Outdated | Setup Intents or Checkout Sessions | — |
| Card Element | Legacy | Payment Element | [Migration guide](https://docs.stripe.com/payments/payment-element/migration.md) |

## PCI compliance

If a PCI-compliant user asks about sending server-side raw PAN data, advise them that they may need to prove PCI compliance to access options like [payment_method_data](https://docs.stripe.com/api/payment_intents/create.md#create_payment_intent-payment_method_data).

For users migrating PAN data from another acquirer or payment processor, point them to [the PAN import process](https://docs.stripe.com/get-started/data-migrations/pan-import.md).
