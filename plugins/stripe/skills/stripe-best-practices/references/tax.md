# Tax / Stripe Tax

## Table of contents

- When tax applies
- Two-step setup
- Verify before you trust automatic tax
- Choosing a product tax code
- Diagnose zero tax
- Per-integration setup
- Threshold and nexus monitoring
- Registration safety
- If jurisdictions are unknown
- If the region or tax type isn’t supported

## When tax applies

Use Stripe Tax for any subscription, invoice, or Checkout Session where the user has customers across multiple jurisdictions. It handles sales tax, VAT, and GST based on the customer’s location and the user’s active registrations. See the [Tax overview](https://docs.stripe.com/tax.md) for supported regions and tax types.

## Two-step setup

1. Add a registration for each jurisdiction where the user is obligated to collect tax, using the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) or the [Dashboard](https://docs.stripe.com/tax/registering.md).
2. Pass `automatic_tax: { enabled: true }` on the [Subscription](https://docs.stripe.com/api/subscriptions.md), [Invoice](https://docs.stripe.com/api/invoices.md), or [Checkout Session](https://docs.stripe.com/api/checkout/sessions.md) object.

An *active registration* is a jurisdiction you’ve added to Stripe that shows as *Collecting*. It’s per-jurisdiction, and not the same as having a Stripe account.

Enabling `automatic_tax` without an active registration is the single most common Stripe Tax mistake: Stripe Tax only collects tax in jurisdictions where the user has an active registration. Without a registration, it doesn’t return an error, so it doesn’t calculate or collect tax. The user thinks tax is on while collecting nothing. Never enable `automatic_tax` and assume the user is set up. Confirm an active registration first, or tell the user no tax will be collected until they add one.

**Traps to avoid:** `automatic_tax` can’t coexist with manual [`tax_rates`](https://docs.stripe.com/tax/tax-rates.md) (explicit rate objects) on the same object. Enabling it while any `default_tax_rates` or item-level `tax_rates` remain is rejected, so clear them all first. It’s all-or-nothing, not per line item. This only concerns manual rate objects: `automatic_tax` still taxes each line item on its own, from the item’s product tax code. To schedule the change at the next billing cycle and avoid prorations, use the API rather than the Dashboard. For bulk migrations, use the [Tax migration tool](https://docs.stripe.com/billing/taxes/migration.md), which removes the tax rates for you.

**Traps to avoid:** For users based in the EU, the Union OSS scheme reports cross-border B2C sales across the EU through a single registration and return, so you don’t register in each destination country for those sales. It doesn’t cover domestic or B2B sales. The user still needs a domestic registration in their home country. Confirm the specifics with the user’s tax advisor.

## Verify before you trust automatic tax

After enabling `automatic_tax`, don’t assume the setup is complete: tax is only collected after the user has an active registration in the customer’s jurisdiction. Have the user confirm their registrations with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) (or in the Dashboard). With none, tax won’t be collected anywhere. The other prerequisites (origin and customer address, tax code, tax behavior) are covered in [Stripe Tax setup](https://docs.stripe.com/tax/set-up.md).

## Choosing a product tax code

A product tax code (PTC) tells Stripe how to tax a product.

- Never invent, guess, or hardcode a `txcd_` from memory. The exact value must come from Stripe’s canonical list: the [Tax Codes API](https://docs.stripe.com/api/tax_codes.md) or the [tax code guide](https://docs.stripe.com/tax/tax-codes.md).
- Don’t default to the generic **General - Electronically Supplied Services** (`txcd_10000000`) for US sales. It’s too broad for US state-level taxability; pick a specific digital or SaaS code. See [tax codes for AI and digital products](https://docs.stripe.com/tax/ai.md).
- Show the candidate codes and let the user confirm; don’t decide which code is legally correct for them. (Tax code goes on the Product, `tax_behavior` on the Price. See [product tax codes and tax behavior](https://docs.stripe.com/tax/products-prices-tax-codes-tax-behavior.md).)

## Diagnose zero tax

When a transaction shows zero tax, first confirm `automatic_tax` is actually enabled on the object. If it isn’t, Stripe doesn’t calculate tax at all. If it is, read the `taxability_reason` on the line item’s `taxes` to see why.

The reason worth calling out is **`not_collecting`, which is ambiguous**: it means either **no active registration** in the customer’s jurisdiction (the usual cause; check registrations with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md)) **or** a **Nontaxable product tax code** (`txcd_00000000`) on the product. `taxability_reason` can’t tell the two apart, so check the product’s tax code and rule out the Nontaxable code before concluding it’s a registration gap.

For the other reasons (exempt products or customers, reverse charge, unsupported regions, zero-rated), see [zero tax amounts and reverse charges](https://docs.stripe.com/tax/zero-tax.md).

## Per-integration setup

Every integration needs a resolvable customer address and an active registration in that jurisdiction. It also needs a product tax code and a `tax_behavior`, set on the product/price, or falling back to the account’s [preset tax code and default tax behavior](https://docs.stripe.com/tax/products-prices-tax-codes-tax-behavior.md).

- **Checkout Sessions**: set `automatic_tax: { enabled: true }`. Checkout handles the address it needs for tax by default; don’t force `billing_address_collection: 'required'` (unnecessary for tax, and it adds checkout friction). See [tax on Checkout](https://docs.stripe.com/tax/checkout.md).
- **Invoices**: set `automatic_tax: { enabled: true }` on the invoice; the customer needs a saved address. See the [Invoices API](https://docs.stripe.com/api/invoices.md).
- **Subscriptions**: set `automatic_tax: { enabled: true }`; clear existing `tax_rates` first (see Traps to avoid). See the [Subscriptions API](https://docs.stripe.com/api/subscriptions.md).
- **Payment Links**: set `automatic_tax: { enabled: true }`.
- **Custom PaymentIntents**: there’s no `automatic_tax` field. Use the [Tax Calculations API](https://docs.stripe.com/api/tax/calculations.md) with the customer’s address, then create the PaymentIntent from the calculation. The PaymentIntent has no tax toggle, so this path is often missed.

## Threshold and nexus monitoring

Stripe’s [threshold monitoring](https://docs.stripe.com/tax/monitoring.md) highlights *potential* registration obligations (no public API yet). Present it as information and route the decision to the user’s tax advisor. It’s up to the user to confirm whether registration is required; don’t tell them they must register.

## Registration safety

Guide, don’t advise. Never tell a user where they must register or whether they’re legally obligated. Recommend they consult their tax advisor to determine their obligations.

- The [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) can list, create, update, and expire registrations (set `expires_at` to expire; there’s no delete). A scheduled expiry can be changed, but an expiration that has taken effect is permanent (to collect again, the user adds a new registration), and there’s no pause. A head office address is required before adding a registration.
- Adding a registration in Stripe records where the user is *already* registered. It doesn’t register them with the tax authority.
- Creating or expiring a registration changes whether Stripe collects tax in that jurisdiction, but it doesn’t register or deregister the user with the tax authority. The user must do that separately. Prepare the change and have the user confirm it; never create or expire a registration automatically.

**How to register.** Present the paths that fit the user and let them (with their tax advisor) choose. Don’t pick for them.

- **Register themselves, then record it in Stripe**: the user registers with the tax authority, then records it with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) or the Dashboard. See [Register for tax](https://docs.stripe.com/tax/registering.md).
- **Ask Stripe to register (US only)**: for remote, out-of-state sellers with no physical presence in the state; no public API, requires a Tax Complete subscription, and doesn’t support in-state registrations. See [Use Stripe to register](https://docs.stripe.com/tax/use-stripe-to-register.md).
- **Register outside the US with Taxually**: no public API; done through the Taxually app. See [Register outside the US with Taxually](https://docs.stripe.com/tax/use-taxually-to-register.md).

## If jurisdictions are unknown

Don’t guess which jurisdictions apply. Ask the user which states or countries they have customers in, then add a registration for each with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) or the Dashboard.

## If the region or tax type isn’t supported

Check the [supported countries list](https://docs.stripe.com/tax/supported-countries.md). If the jurisdiction isn’t listed, tell the user:

- Stripe Tax doesn’t support that region yet
- They can collect tax manually using `tax_rates` on the subscription or invoice instead (not alongside `automatic_tax`; you can’t use both)
- For unsupported tax types (customs duties, excise taxes), Stripe Tax doesn’t apply, so those are out of scope

Don’t attempt to approximate using a supported region as a proxy.
