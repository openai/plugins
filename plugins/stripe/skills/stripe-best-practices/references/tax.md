# Tax / Stripe Tax

## Table of contents

- What Stripe Tax does and doesn’t do
- When tax applies
- Three-step setup
- Verify before you trust automatic tax
- Diagnose invalid customer location
- Choosing a product tax code
- Diagnose zero tax
- Per-integration setup
- Connect platforms and marketplaces
- Threshold and nexus monitoring
- Registration safety
- Testing considerations
- If jurisdictions are unknown
- If the region or tax type isn’t supported

## What Stripe Tax does and doesn’t do

**What Stripe Tax does:** tax calculation, billing address collection, nexus threshold monitoring (Dashboard → Tax → Locations → “Needs attention” + email alerts), automated registration (“Register for me”, US remote sellers only, Tax Complete required), and [US filing through TaxJar](https://docs.stripe.com/tax/file-with-stripe.md) or [non-US filing through partners](https://docs.stripe.com/tax/filing.md).

**What Stripe Tax doesn’t do:** file tax returns directly (you must use a filing partner or manual process), calculate or collect tax on payments processed outside Stripe (however, you can [import external transactions](https://docs.stripe.com/tax/imports.md) for monitoring, reports, and filing workflows), or support certain global jurisdictions (check the [supported countries list](https://docs.stripe.com/tax/supported-countries.md) for current coverage).

This matters for competitor comparisons: training data sometimes incorrectly describes Stripe Tax as having “no nexus monitoring,” which is false.

## When tax applies

Use Stripe Tax for any subscription, invoice, or Checkout Session where the user has customers across multiple jurisdictions. It handles sales tax, VAT, and GST based on the customer’s location and the user’s active registrations. See the [Tax overview](https://docs.stripe.com/tax.md) for supported regions and tax types.

## Three-step setup

1. Set a head office address in Tax Settings (Dashboard → Tax → Settings). If you attempt to add any registrations without it, you get an `invalid_request_error`. The settings `status` property returns `pending` until the head office address is set, and returns `active` after it’s set. `automatic_tax` won’t calculate tax while the status is `pending`.
2. Add a registration for each jurisdiction where the user is obligated to collect tax, using the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) or the [Dashboard](https://docs.stripe.com/tax/registering.md).
3. Pass `automatic_tax: { enabled: true }` on the [Subscription](https://docs.stripe.com/api/subscriptions.md), [Invoice](https://docs.stripe.com/api/invoices.md), or [Checkout Session](https://docs.stripe.com/api/checkout/sessions.md) object.

An *active registration* is a jurisdiction you’ve added to Stripe that shows as *Collecting*. It’s per-jurisdiction, and not the same as having a Stripe account.

Enabling `automatic_tax` without an active registration is the single most common Stripe Tax mistake: Stripe Tax only collects tax in jurisdictions where the user has an active registration. Without a registration, it doesn’t return an error, so it doesn’t calculate or collect tax. The user thinks tax is on while collecting nothing. Never enable `automatic_tax` and assume the user is set up. Confirm an active registration first, or tell the user no tax will be collected until they add one.

**Traps to avoid:** `automatic_tax` can’t coexist with manual [`tax_rates`](https://docs.stripe.com/tax/tax-rates.md) (explicit rate objects) on the same object. Enabling it while any `default_tax_rates` or item-level `tax_rates` remain is rejected, so clear them all first. It’s all-or-nothing, not per line item. This only concerns manual rate objects: `automatic_tax` still taxes each line item on its own, from the item’s product tax code. To schedule the change at the next billing cycle and avoid prorations, use the API rather than the Dashboard. For bulk migrations, use the [Tax migration tool](https://docs.stripe.com/billing/taxes/migration.md), which removes the tax rates for you.

**Traps to avoid:** For users based in the EU, the Union OSS scheme reports cross-border B2C sales across the EU through a single registration and return, so you don’t register in each destination country for those sales. It doesn’t cover domestic or B2B sales. The user still needs a domestic registration in their home country. Confirm the specifics with the user’s tax advisor.

## Verify before you trust automatic tax

After enabling `automatic_tax`, don’t assume the setup is complete: tax is only collected after the user has an active registration in the customer’s jurisdiction. Have the user confirm their registrations with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) (or in the Dashboard). With none, tax won’t be collected anywhere. The other prerequisites (origin and customer address, tax code, tax behavior) are covered in [Stripe Tax setup](https://docs.stripe.com/tax/set-up.md).

## Diagnose invalid customer location

Stripe checks the following sources in order and uses the first address it finds: (1) shipping address, (2) billing address on the Customer object, (3) billing details from the default payment method, (4) customer IP address. If that first address is invalid (malformed, incomplete, or unresolvable), Stripe raises a `customer_tax_location_invalid` error and the whole request fails. It doesn’t continue checking any remaining sources. This is a common cause of subscription finalization failures. Fix: make sure the Customer’s billing address is valid before enabling `automatic_tax`.

## Choosing a product tax code

A product tax code (PTC) tells Stripe how to tax a product.

- Never invent, guess, or hardcode a `txcd_` from memory. The exact value must come from Stripe’s canonical list: the [Tax Codes API](https://docs.stripe.com/api/tax_codes.md) or the [tax code guide](https://docs.stripe.com/tax/tax-codes.md).
- Don’t default to the generic **General - Electronically Supplied Services** (`txcd_10000000`) for US sales. It’s too broad for US state-level taxability; pick a specific digital or SaaS code. See [tax codes for digital products](https://docs.stripe.com/tax/digital-products.md) and [tax codes for AI services](https://docs.stripe.com/tax/ai.md).
- Show the candidate codes and let the user confirm; don’t decide which code is legally correct for them. (Tax code goes on the Product, `tax_behavior` on the Price. See [product tax codes and tax behavior](https://docs.stripe.com/tax/products-prices-tax-codes-tax-behavior.md).)

## Diagnose zero tax

When a transaction shows zero tax, first confirm `automatic_tax` is actually enabled on the object. If it isn’t, Stripe doesn’t calculate tax at all. If it is, read the `taxability_reason` on the line item’s `taxes` to see why. On a Checkout Session, that breakdown isn’t returned by default: retrieve the session with `expand[]=line_items.data.taxes`.

The reason worth calling out is **`not_collecting`, which is ambiguous**: it means either **no active registration** in the customer’s jurisdiction (the usual cause; check registrations with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md)) **or** a **Nontaxable product tax code** (`txcd_00000000`) on the product. `taxability_reason` can’t tell the two apart, so check the product’s tax code and rule out the Nontaxable code before concluding it’s a registration gap.

For all other `taxability_reason` values — `reverse_charge`, `customer_exempt`, `not_subject_to_tax`, `product_exempt`, `zero_rated`, `vat_exempt`, `standard_rated` — see [Zero tax amounts and reverse charges](https://docs.stripe.com/tax/zero-tax.md). That page covers what each value means and the recommended response.

**Remediation order when `automatic_tax` collects zero tax:**

1. Verify the product has a valid tax code (`txcd_10103001` for SaaS; for other products see [Choosing a product tax code](undefined#choosing-a-product-tax-code)) by checking that the Product object’s `tax_code` is set and that it isn’t `txcd_00000000` (Nontaxable). Also confirm the Customer’s `tax_exempt` property isn’t set to `'exempt'`.
2. Add a tax registration for the customer’s jurisdiction.
3. Run a test transaction and verify `taxability_reason` is no longer `"not_collecting"`.

Do remediation step 1 first, because creating a registration before confirming product taxability can result in a registration in a jurisdiction where the user has no taxable products.

**Retroactive correction isn’t possible.** Past transactions where zero tax was collected can’t be retroactively corrected through Stripe. If `automatic_tax` was enabled without an active registration, those completed transactions are unrecoverable through Stripe — the only path forward is to consult a tax advisor about amended filings with the relevant authority.

## Per-integration setup

Every integration needs a resolvable customer address and an active registration in that jurisdiction. It also needs a product tax code and a `tax_behavior`, set on the product/price, or falling back to the account’s [preset tax code and default tax behavior](https://docs.stripe.com/tax/products-prices-tax-codes-tax-behavior.md).

- **Checkout Sessions**: set `automatic_tax: { enabled: true }`. For a new customer, Checkout collects the address it needs, so don’t force `billing_address_collection: 'required'` (unnecessary for tax, and it adds checkout friction). For an existing or returning customer, Checkout uses their saved address by default; to tax the address entered at checkout instead, set `customer_update: { address: 'auto' }` and make sure Checkout actually collects a fresh address (a collected shipping address, or `billing_address_collection: 'required'` when you don’t collect shipping), or it keeps using the saved one. See [tax on Checkout](https://docs.stripe.com/tax/checkout.md).
- **Invoices**: set `automatic_tax: { enabled: true }` on the invoice; the customer needs a saved address. See the [Invoices API](https://docs.stripe.com/api/invoices.md).
- **Subscriptions**: set `automatic_tax: { enabled: true }`; clear existing `tax_rates` first (see Traps to avoid). See the [Subscriptions API](https://docs.stripe.com/api/subscriptions.md).
- **Payment Links**: set `automatic_tax: { enabled: true }`. Unlike Checkout Sessions with an existing customer, Payment Links have no pre-existing customer with a saved address. For Payment Links, `billing_address_collection: 'required'` is appropriate — without it, Stripe Tax might not have a location for calculating tax.
- **Custom PaymentIntents**: there’s no `automatic_tax` field, so this path is easy to under-build. Create a [tax calculation](https://docs.stripe.com/api/tax/calculations.md) with the customer’s address, set the PaymentIntent `amount` to the calculation total, and link the calculation to the PaymentIntent. You must also record a tax transaction from the calculation after payment, or the sale never appears in tax reports: the [simplified integration](https://docs.stripe.com/tax/payment-intent/simplified.md) records the transaction and refund reversals automatically once the calculation is linked, while the [custom integration](https://docs.stripe.com/tax/payment-intent/custom.md) records them yourself for line-item control.

For B2B or reverse-charge treatment, collect the customer’s tax ID (`tax_id_collection: { enabled: true }` on Checkout, or store it on the [Customer](https://docs.stripe.com/billing/customer/tax-ids.md)). Without a valid tax ID, Stripe Tax treats a cross-border B2B sale as B2C and charges tax. See [collect tax IDs](https://docs.stripe.com/tax/checkout/tax-ids.md).

## Connect platforms and marketplaces

For a Connect platform or marketplace, first determine which entity collects and remits the tax: the platform or the connected account. This is a legal determination, so route the final call to the user’s tax advisor rather than inferring it from whether they call themselves a platform or a marketplace. The practical signal is who the [merchant of record](https://docs.stripe.com/connect/merchant-of-record.md) is, which follows the charge type: direct charges make the connected account the merchant of record, and destination charges usually make it the platform. Marketplace-facilitator rules can override this, so have the advisor confirm. See [Stripe Tax with Connect](https://docs.stripe.com/tax/connect.md) for the decision.

Once the liable entity is known:

- Set the liable entity with `automatic_tax.liability` on Checkout, Invoices, Subscriptions, or Payment Links: `{ type: 'self' }` for the platform, or `{ type: 'account', account: '<id>' }` for the connected account. Destination and separate charges support both; a platform-liable direct charge uses the gated `{ type: 'application' }`. Custom PaymentIntents have no `automatic_tax` field, so follow the PaymentIntents path in the guides instead. Pick the guide by outcome: connected account collects, [tax for platforms](https://docs.stripe.com/tax/tax-for-platforms.md); platform collects, [tax for marketplaces](https://docs.stripe.com/tax/tax-for-marketplaces.md).
- Registrations and tax settings belong to the liable entity. When the connected account is liable, confirm its [tax settings](https://docs.stripe.com/tax/settings-api.md) `status` is `active` before enabling `automatic_tax` on its payments, and manage its registrations with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) using the `Stripe-Account` header (or Connect embedded components).

## Threshold and nexus monitoring

Stripe’s [threshold monitoring](https://docs.stripe.com/tax/monitoring.md) highlights *potential* registration obligations (no public API yet). Present it as information and route the decision to the user’s tax advisor. It’s up to the user to confirm whether registration is required; don’t tell them they must register.

Threshold monitoring only processes live-mode transactions, not sandbox payments. Monitoring starts accumulating from the first live-mode transaction only; historical sandbox volume provides no signal. Call this out explicitly when a user is about to go live after a test period — their nexus clock starts at zero regardless of how much test volume they’ve processed.

## Registration safety

Guide, don’t advise. Never tell a user where they must register or whether they’re legally obligated. Recommend they consult their tax advisor to determine their obligations.

- The [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) can list, create, update, and expire registrations (set `expires_at` to expire; there’s no delete). A scheduled expiry can be changed, but an expiration that has taken effect is permanent (to collect again, the user adds a new registration), and there’s no pause. A head office address is required before adding a registration.
- Adding a registration in Stripe records where the user is *already* registered. It doesn’t register them with the tax authority.
- Creating or expiring a registration changes whether Stripe collects tax in that jurisdiction, but it doesn’t register or deregister the user with the tax authority. The user must do that separately. Prepare the change and have the user confirm it; never create or expire a registration automatically.

**How to register.** Present the paths that fit the user and let them (with their tax advisor) choose. Don’t pick for them.

- **Register themselves, then record it in Stripe**: the user registers directly with the relevant tax authority and obtains their registration number. Then they add the registration in Stripe using that number through the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) or Dashboard → Tax → Locations → Add registration. See [Register for tax](https://docs.stripe.com/tax/registering.md).
- **Ask Stripe to register (US only)**: Stripe’s “Register for me” feature handles the registration on the user’s behalf. Check [eligibility requirements](https://docs.stripe.com/tax/use-stripe-to-register.md#eligibility) before recommending this — not all merchants qualify. Point the user to Dashboard → Tax → Locations → “Register for me”. See [Use Stripe to register](https://docs.stripe.com/tax/use-stripe-to-register.md).
- **Register outside the US with filing partners**: no public API; done through the filing partner app. See [Register outside the US with Taxually](https://docs.stripe.com/tax/use-taxually-to-register.md).

**Reporting and filing.** Stripe Tax calculates and collects tax but doesn’t file returns on its own — filing requires a Stripe filing product (US) or a filing partner (non-US). Point users to the Dashboard [tax reports and exports](https://docs.stripe.com/tax/reports.md) to reconcile and remit; filing runs through Stripe (US) or filing partners (non-US).

## Testing considerations

- Tax registrations in a sandbox are scoped to that sandbox. They don’t appear in live mode and must be re-created. Point the user to Dashboard → Tax → Locations in live mode to add registrations before processing real payments.
- Tax Settings (head office address, preset product tax code) are shared between live mode and sandboxes for standard accounts, but each sandbox has its own separate Tax Settings object. Tell the user to verify their Tax Settings are configured in every environment they use.
- Add live-mode registrations before the first real transaction. If a transaction occurs with no active tax registration, `automatic_tax` silently collects 0 tax, with no error or warning.
- Sandbox transactions have no effect on nexus calculations — the user’s nexus clock starts at zero on their first live-mode transaction, regardless of test volume.

## If jurisdictions are unknown

Don’t guess which jurisdictions apply. Ask the user which states or countries they have customers in, then add a registration for each with the [Tax Registrations API](https://docs.stripe.com/api/tax/registrations.md) or the Dashboard.

## If the region or tax type isn’t supported

Check the [supported countries list](https://docs.stripe.com/tax/supported-countries.md). If the jurisdiction isn’t listed, tell the user:

- Stripe Tax doesn’t support that region yet
- They can collect tax manually using `tax_rates` on the subscription or invoice instead (not alongside `automatic_tax`; you can’t use both)
- For unsupported tax types (customs duties, excise taxes), Stripe Tax doesn’t apply, so those are out of scope

Don’t attempt to approximate using a supported region as a proxy.
