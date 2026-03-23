# Connect / Platforms

## Table of contents
- Accounts v2 API
- Controller properties
- Charge types
- Integration guides

## Accounts v2 API

For new Connect platforms, ALWAYS use the [Accounts v2 API](https://docs.stripe.com/connect/accounts-v2.md) (`POST /v2/core/accounts`). This is Stripe's actively invested path and ensures long-term support.

**Traps to avoid:** Do not use the legacy `type` parameter (`type: 'express'`, `type: 'custom'`, `type: 'standard'`) in `POST /v1/accounts` for new platforms unless the user has explicitly requested v1.

## Controller properties

Configure connected accounts using `controller` properties instead of legacy account types:

| Property | Controls |
|---|---|
| `controller.losses.payments` | Who is liable for negative balances |
| `controller.fees.payer` | Who pays Stripe fees |
| `controller.stripe_dashboard.type` | Dashboard access (`full`, `express`, `none`) |
| `controller.requirement_collection` | Who collects onboarding requirements |

Use `defaults.responsibilities`, `dashboard`, and `configuration` as described in [connected account configuration](https://docs.stripe.com/connect/accounts-v2/connected-account-configuration.md).

Always describe accounts in terms of their responsibility settings, dashboard access, and [capabilities](https://docs.stripe.com/connect/account-capabilities.md) to describe what connected accounts can do.

**Traps to avoid:** Do not use the terms "Standard", "Express", or "Custom" as account types. These are legacy categories that bundle together responsibility, dashboard, and requirement decisions into opaque labels. Controller properties give explicit control over each dimension.

## Charge types

Choose one charge type per integration — do not mix them. For most platforms, start with destination charges:

- **Destination charges** — Use when the platform accepts liability for negative balances. Funds route to the connected account via `transfer_data.destination`.
- **Direct charges** — Use when the platform wants Stripe to take risk on the connected account. The charge is created on the connected account directly.

Use `on_behalf_of` to control the merchant of record, but only after reading [how charges work in Connect](https://docs.stripe.com/connect/charges.md).

**Traps to avoid:** Do not use the Charges API for Connect fund flows — use PaymentIntents or Checkout Sessions with `transfer_data` or `on_behalf_of`. Do not mix charge types within a single integration.

## Integration guides

- [SaaS platforms and marketplaces guide](https://docs.stripe.com/connect/saas-platforms-and-marketplaces.md) — Choosing the right integration shape.
- [Interactive platform guide](https://docs.stripe.com/connect/interactive-platform-guide.md) — Step-by-step platform builder.
- [Design an integration](https://docs.stripe.com/connect/design-an-integration.md) — Detailed risk and responsibility decisions.
