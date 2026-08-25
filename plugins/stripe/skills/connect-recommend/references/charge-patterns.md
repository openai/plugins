## Stripe Connect Charge Patterns

### Overview

Connect offers three ways to create charges involving connected accounts. The charge pattern determines who is the merchant of record, how funds flow, and how fees and refunds work.

### Comparison Table

| Feature | Direct Charges | Destination Charges | Separate Charges & Transfers |
| --- | --- | --- | --- |
| **Merchant of record** | Connected account | Platform | Platform |
| **Payment created on** | Connected account | Platform account | Platform account |
| **Statement descriptor** | Connected account’s | Platform’s (can set connected account’s) | Platform’s |
| **Platform fee** | `application_fee_amount` | `application_fee_amount` or calculate using `transfer_data.amount` | Manual calculation |
| **Refund source** | Connected account’s balance | Platform’s balance | Platform’s balance |
| **Multi-seller split** | No (one seller per charge) | No (one destination per charge) | Yes (multiple transfers) |
| **Account requirements** | Most v2 configs — see BLOCKED combinations in the controller compatibility note below; the only charge type safe with `losses_collector: 'stripe'` | Requires `losses_collector: 'application'` | Requires `losses_collector: 'application'` |
| **Complexity** | Low | Low | High |
| **Best for** | SaaS, seller-owned transactions | Marketplaces, on-demand | Multi-seller carts, complex splits |

### Direct Charges

> **Controller Property Compatibility:** Works with most controller configurations, but NOT all. BLOCKED combinations for direct charges include: `fees_collector: 'stripe' + losses_collector: 'application'` (full or none dashboard), and Express dashboard configs other than `application/application`. This is the **only** charge type safe with `losses_collector: 'stripe'`. If the platform wants Stripe to own losses, direct charges are the only option.

#### How it works

The charge is created directly on the connected account. The connected account is the merchant of record — their name appears on the customer’s bank statement. The platform collects an application fee.

#### Code pattern

```javascript
// Backend: Create PaymentIntent on connected account
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000, // $100.00
  currency: 'usd',
  application_fee_amount: 1500, // $15.00 platform fee
  metadata: {
    orderId: 'order_123',
  },
}, {
  stripeAccount: 'acct_connected_account_id', // Key: stripeAccount header
});

// Return client_secret to frontend
res.json({ clientSecret: paymentIntent.client_secret });
```

#### Frontend (with Stripe.js)

```javascript
// Must initialize Stripe with connected account
const stripe = await loadStripe('pk_test_...', {
  stripeAccount: 'acct_connected_account_id',
});

// Then confirm payment as usual
const result = await stripe.confirmPayment({
  elements,
  confirmParams: {
    return_url: 'https://yoursite.com/success',
  },
});
```

#### Fund flow

```
Customer pays $100
  → $100 lands in connected account's balance
  → $15 application fee transferred to platform
  → Connected account keeps $85
```

#### Refunds

```javascript
// Refund comes from connected account's balance
const refund = await stripe.refunds.create({
  charge: 'ch_xxx',
  // Optionally refund the application fee too:
  refund_application_fee: true,
}, {
  stripeAccount: 'acct_connected_account_id',
});
```

#### When to use

- Direct-charge integrations where sellers own the customer relationship (legacy v1 Standard-style pattern)
- SaaS platforms (Shopify model)
- When the connected account’s name should appear on bank statements
- When sellers handle their own disputes

> **Legacy mapping note (external docs terms):** Stripe docs still reference legacy v1 naming (`standard`, `express`, `custom`) and legacy fee-payer behaviors (`application_express`, `application_custom`) for older accounts. For migration mapping to Accounts v2 dimensions, see the “Legacy migration note” section in the account-types reference.

### Destination Charges

> **Controller Property Compatibility:** REQUIRES `losses_collector: 'application'`. Using destination charges with `losses_collector: 'stripe'` creates a liability-model mismatch for this charge flow. See `compatibility-matrix.md` for details.

#### How it works

The charge is created on the platform’s account. The platform is the merchant of record. Funds are automatically transferred to the connected account using `transfer_data`. This is a common pattern for marketplaces.

#### Code pattern

```javascript
// Backend: Create PaymentIntent on platform account
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000, // $100.00
  currency: 'usd',
  application_fee_amount: 1500, // $15.00 collected; platform net = $15.00 − Stripe processing fees
  transfer_data: {
    destination: 'acct_connected_account_id', // Funds go here
  },
  metadata: {
    bookingId: 'booking_123',
    riderId: 'user_456',
    operatorId: 'user_789',
  },
});

// Return client_secret to frontend
res.json({ clientSecret: paymentIntent.client_secret });
```

#### Alternative: Specify transfer amount instead of fee

```javascript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000, // $100.00
  currency: 'usd',
  transfer_data: {
    destination: 'acct_connected_account_id',
    amount: 8500, // $85.00 goes to connected account (platform keeps $15)
  },
});
```

#### Frontend (standard Stripe.js)

```javascript
// Initialize Stripe with platform's publishable key (no stripeAccount needed)
const stripe = await loadStripe('pk_test_platform_key');

const result = await stripe.confirmPayment({
  elements,
  confirmParams: {
    return_url: 'https://yoursite.com/success',
  },
});
```

#### Fund flow

```
Customer pays $100
  → $100 lands in platform's balance
  → $85 automatically transferred to connected account
  → Platform nets $15 (application_fee_amount) − Stripe processing fees
```

#### Refunds

```javascript
// Refund comes from platform's balance
const refund = await stripe.refunds.create({
  payment_intent: 'pi_xxx',
  // Optionally:
  reverse_transfer: true, // Claw back from connected account
  refund_application_fee: true, // Refund the platform fee too
});
```

#### When to use

- **Marketplaces** where the platform owns the customer relationship
- On-demand platforms (Uber, DoorDash model)
- When you want the platform name on bank statements
- Express dashboard accounts (common pairing)
- When the platform handles disputes
- **NOT for hold-and-release or delivery-gated payouts** — funds transfer automatically to the connected account upon payment success. Use separate charges and transfers for delivery-gated payouts or any scenario requiring the platform to hold funds before releasing.

#### Destination Charges with `on_behalf_of`

> **Not covered by this guide.** `on_behalf_of` is an advanced variant that changes the merchant of record to the connected account while the charge lives on the platform. It has narrow use cases and significant complexity.
> 
> If your integration requires `on_behalf_of`, consult the [Stripe Connect documentation](https://docs.stripe.com/connect/charges.md) or [contact Stripe sales](https://stripe.com/contact/sales).
> 
> **Do NOT use `on_behalf_of` for marketplace use cases** — the platform should be the merchant of record. Use regular destination charges instead.

### Separate Charges and Transfers

> **Controller Property Compatibility:** REQUIRES `losses_collector: 'application'`. Same negative balance liability issue as destination charges — using separate charges and transfers with `losses_collector: 'stripe'` means the platform actually carries the losses despite the configuration. See `compatibility-matrix.md` for details.

#### How it works

The charge and transfer are separate API calls. This gives maximum flexibility — you can split a single payment across multiple connected accounts, delay transfers, or create complex fee structures.

#### Code pattern

```javascript
// Step 1: Create PaymentIntent (no transfer_data)
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000, // $100.00
  currency: 'usd',
  metadata: {
    orderId: 'order_123',
  },
});

// Step 2: After payment_intent.succeeded webhook fires — latest_charge is null
// at creation time and only populated on the confirmed PaymentIntent from the event
// IMPORTANT: Always verify the webhook signature before processing event data.
// See https://stripe.com/docs/webhooks/signatures for verification steps.
const confirmedIntent = event.data.object; // payment_intent.succeeded payload
const transfer = await stripe.transfers.create({
  amount: 8500, // $85.00 to connected account
  currency: 'usd',
  destination: 'acct_connected_account_id',
  source_transaction: confirmedIntent.latest_charge, // charge ID from confirmed PaymentIntent
  metadata: {
    orderId: 'order_123',
  },
});
```

#### Multi-seller split

```javascript
// One payment, multiple sellers (for example, a multi-seller cart)
await stripe.paymentIntents.create({
  amount: 25000, // $250.00 total
  currency: 'usd',
});

// After payment_intent.succeeded webhook fires — latest_charge is null at creation time.
// IMPORTANT: Always verify the webhook signature before processing event data.
// See https://stripe.com/docs/webhooks/signatures for verification steps.
const confirmedIntent = event.data.object; // payment_intent.succeeded payload
const chargeId = confirmedIntent.latest_charge;

// Transfer to seller A
await stripe.transfers.create({
  amount: 8000,
  currency: 'usd',
  destination: 'acct_seller_a',
  source_transaction: chargeId,
});

// Transfer to seller B
await stripe.transfers.create({
  amount: 12000,
  currency: 'usd',
  destination: 'acct_seller_b',
  source_transaction: chargeId,
});

// Platform keeps $50 (25000 - 8000 - 12000 = 5000)
```

#### Fund flow

```
Customer pays $250
  → $250 lands in platform's balance
  → Platform creates transfer: $80 to Seller A
  → Platform creates transfer: $120 to Seller B
  → Platform keeps $50
```

#### Refunds

```javascript
// Refund the charge
const refund = await stripe.refunds.create({
  charge: 'ch_xxx',
});

// Manually reverse transfers
await stripe.transfers.createReversal('tr_seller_a', {
  amount: 8000,
});
await stripe.transfers.createReversal('tr_seller_b', {
  amount: 12000,
});
```

#### When to use

- Multi-seller carts (one payment, multiple recipients)
- Delayed payouts (hold funds, transfer later)
- Hold-and-release / delivery-gated payout (payment precedes delivery, platform releases funds on confirmation)
- Delivery-gated payouts (collect payment now, transfer to seller after fulfillment)
- Complex fee structures or splits
- When you need maximum control over fund flow timing
- Crowdfunding-style platforms

### Decision Guide

```
Is there one seller per transaction?
├── Yes → Does the platform need to hold funds before releasing to the seller?
│   ├── Yes (hold-and-release or delivery confirmation) → SEPARATE CHARGES & TRANSFERS
│   └── No → Is the seller the merchant of record?
│       ├── Yes → DIRECT CHARGES
│       └── No → DESTINATION CHARGES ← Common marketplace default
└── No (multiple sellers) → SEPARATE CHARGES & TRANSFERS
```

**Quick rules:**

- **Marketplace with one seller, immediate payout** → Destination charges
- **Marketplace with hold-and-release or delivery-gated payout** → Separate charges and transfers
- **SaaS where seller owns the relationship** → Direct charges
- **Multi-seller cart or complex splits** → Separate charges and transfers
