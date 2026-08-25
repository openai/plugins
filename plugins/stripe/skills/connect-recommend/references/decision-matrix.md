## Connect Integration Decision Matrix

### IMPORTANT: Use Accounts v2 API

**ALWAYS use the Accounts v2 API (`/v2/core/accounts`) for new integrations.** Do NOT use the legacy v1 API with `type: 'express'`, `type: 'standard'`, or `type: 'custom'`. These are legacy categories that bundle together responsibility, dashboard, and requirement decisions into opaque labels.

Instead, configure accounts using three independent dimensions:

- **Dashboard access**: `express` (lightweight), `full` (independent businesses), `none` (white-label)
- **Fee collection**: `stripe` (Stripe bills connected accounts) or `application` (platform manages billing)
- **Loss liability**: `stripe` (Stripe bears unresolved negative balances) or `application` (platform bears negative balances)

### Business Model → Recommendation Mapping

| Business Model | Dashboard | Fees | Losses | Charge Pattern | Onboarding | Reasoning |
| --- | --- | --- | --- | --- | --- | --- |
| **Marketplace** | `express` | `application` | `application` | Destination | Embedded | Platform owns customer relationship; platform-owned pricing + loss liability required for Express dashboard today |
| **On-demand services** | `express` | `application` | `application` | Destination | Embedded | Fast onboarding for drivers and providers; platform-owned pricing + loss liability required for Express |
| **Professional services** | `express` | `application` | `application` | Destination | Embedded | Similar to marketplace; platform-owned pricing + loss liability required for Express |
| **SaaS with payments** | `full` | `stripe` | `stripe` | Direct | Embedded | Sellers want independence, own Stripe accounts, own branding |
| **Crowdfunding** | `express` | `application` | `application` | Separate | Embedded | Multi-party splits and delayed release. Use transfer math (not `application_fee_amount`) and platform-owned loss liability for transfer reversals |
| **Subscription platforms** | `express` | `application` | `application` | Destination | Embedded | Recurring billing, platform manages subscriptions; platform-owned pricing + loss liability required for Express |
| **E-commerce (white-label)** | `none` | `application` | `application` | Destination or Direct | Embedded | Full branding control. Use embedded components for white-label feel. Going fully custom (no embedded components) adds significant complexity — the platform must build and maintain all connected account UX including onboarding remediation, refund and dispute flows, and ongoing requirement collection. |
| **Rental marketplace** | `express` | `application` | `application` | Destination | Embedded | Platform owns booking flow; platform-owned pricing + loss liability required for Express |
| **Event ticketing** | `express` | `application` | `application` | Destination | Embedded | Platform manages event and ticket flow; platform-owned pricing + loss liability required for Express |
| **B2B platforms** | `none` | `application` | `application` | Separate | Embedded | For complex enterprise multi-party flows, prefer Separate charges and transfers with transfer math. Don’t default to Destination in these scenarios. Often requires sales engagement for billing complexity — [Stripe sales](https://stripe.com/contact/sales). |

**Note:** `fees` and `losses` columns refer to `defaults.responsibilities.fees_collector` and `defaults.responsibilities.losses_collector` in the v2 API. Values are `"stripe"` or `"application"` (your platform).

### Decision Tree Logic

#### Account Configuration Selection (Accounts v2)

Rather than choosing a legacy “account type”, configure three independent dimensions:

**If the user asks “what account type should I use?” (or similar):** Reframe explicitly before giving settings: “In Accounts v2, avoid the legacy `type` parameter and configure behavior with explicit fields: `dashboard`, `defaults.responsibilities.fees_collector`, `defaults.responsibilities.losses_collector`, and the appropriate account configuration (`merchant` for direct charges or `recipient` for destination or separate flows).” Then provide the recommended field values.

**Dashboard access:**

```
What dashboard should connected accounts see?
├── No dashboard needed (fully embedded or white-label) → dashboard: "none"
├── Independent businesses needing full Stripe access → dashboard: "full"
└── Lightweight dashboard for sellers or providers → dashboard: "express" ← DEFAULT
```

**Responsibilities:**

```
Who collects fees and bears losses?
├── Marketplace (destination or separate charges) → fees_collector: "application", losses_collector: "application"
│   Platform is merchant of record and should be responsible for paying Stripe fees
│   Platform-owned pricing + loss liability is REQUIRED for Express dashboard today
│   Platform-owned loss liability enables connected account negative balances for transfer reversals
├── SaaS (direct charges) → fees_collector: "stripe", losses_collector: "stripe" ← DEFAULT
└── White-label or enterprise → fees_collector: "application", losses_collector: "application" (use embedded components; fully custom adds significant complexity)
```

**Detailed rules:**

- If sellers are independent businesses wanting their own Stripe access → `dashboard: "full"`
- If sellers need lightweight access (common for marketplaces) → `dashboard: "express"` (typical default)
- If fully white-labeled, sellers never see Stripe → `dashboard: "none"`
- Marketplace defaults: `dashboard: "express"` + `fees_collector: "application"` + `losses_collector: "application"`
- SaaS defaults: `dashboard: "full"` + `fees_collector: "stripe"` + `losses_collector: "stripe"`
- Hybrid Express defaults (same accounts used for direct + destination or separate): keep `dashboard: "express"` + `fees_collector: "application"` + `losses_collector: "application"` for both sides

#### Charge Pattern Selection

```
How many sellers per transaction?
├── Multiple sellers → Separate charges & transfers
└── One seller
    └── Who should the customer pay at checkout?
        ├── Seller runs checkout (seller name on receipt or statement) → Direct charges
        └── Platform runs checkout (platform name on receipt or statement) → Destination charges ← DEFAULT
```

**Detailed rules:**

- If platform owns customer relationship → **Destination** (most marketplaces)
- If seller owns customer relationship → **Direct** (SaaS model)
- If customers discover services on your platform and complete checkout in your platform flow (you own checkout UX, order confirmation, and payment operations) → **Destination**
- Language saying payments should “belong to” or be “associated with” sellers, or that sellers should “run their own account,” is usually a payout expectation (who receives proceeds) or a dashboard-access preference, not a checkout-ownership signal. Destination charges satisfy payout expectations through automatic transfers and Express dashboard satisfies “own account” expectations. Only choose Direct when sellers independently own the checkout flow (their own payment page, their branding on statements, they handle refunds and disputes).
- Choose **Direct** when the behavior is SaaS enablement: each seller runs their own payment relationship, customers pay the seller directly, seller branding appears on receipts and statements, and seller-side operations handle payment support, refunds, and disputes.
- If multi-party splits needed → **Separate** (carts, one payment split across multiple parties)
- If “platform collects then pays out” → **Destination**
- If “buyers pay sellers directly” → **Direct**
- If one payment maps to one connected account and funds transfer immediately (payout timing to bank is controlled by payout schedule, not release logic) → **Destination**
- If the platform needs to hold funds and only transfer to the connected account after a trigger (delivery, job completion, approval, campaign end) → **Separate** (use transfer math; don’t use `application_fee_amount`)
- If one payment must be split across multiple connected accounts (for example, a multi-vendor cart) → **Separate**
- For B2B enterprise flows with multi-party allocation, approval gates, or staged release, prefer **Separate** and do NOT default to **Destination**
- If unsure and the flow is single-recipient, immediate-transfer marketplace behavior → **Destination** (safest default)

#### Hybrid model guidance

Some platforms run two sides of business with the same connected accounts. This is supported, but every transaction must be explicitly classified to the correct side:

- **Connected account is merchant of record** → **Direct** charges
- **Platform is merchant of record** → **Destination** or **Separate** charges and transfers

When both sides share Express connected accounts, keep controller settings aligned with the allowed path in this guide: `dashboard: "express"` + `fees_collector: "application"` + `losses_collector: "application"` for both direct and destination or separate contexts.

Hybrid models add material complexity:

- Two payment flows to build and maintain (direct + destination or separate)
- Webhook handling across both payment lifecycle and transfer and reversal lifecycle
- Expanded end-to-end testing matrix (refunds, disputes, transfer reversals, negative balance behavior)

Launch the most business-critical side first, stabilize webhook and reconciliation behavior, then add the second side.

#### Onboarding Method Selection

```
How much control over onboarding UX?
├── "Stripe handles everything" → Embedded components (recommended default)
├── "Some customization" → Embedded components with [appearance options API](/connect/embedded-appearance-options)
└── "Fully custom" → API-based — NOT RECOMMENDED for platforms integrating without dedicated Stripe guidance.
    Requires building custom remediation flows. Direct to [Stripe sales](https://stripe.com/contact/sales).
```

**Detailed rules:**

- `dashboard: "express"` → **Embedded components** (recommended, keeps users in-app) or Stripe-hosted redirect (fallback)
- `dashboard: "full"` → **Embedded components** or Stripe-hosted redirect
- `dashboard: "none"` + want embedded → **[Embedded components](https://docs.stripe.com/connect/embedded-onboarding.md)**
- If unsure → **Embedded components** (Stripe handles requirement collection and ongoing compliance updates)
- Do NOT recommend API onboarding. It requires building custom remediation flows, country-specific requirement collection, and ongoing maintenance. If a user insists on fully custom onboarding, direct them to [Stripe sales](https://stripe.com/contact/sales).

#### Connected Account Configuration (v2)

**Marketplace connected accounts** (destination or separate charges):

- Use `configuration.recipient` (v2) — the connected account receives transfers from the platform, not direct payments
- Request `stripe_transfers` on `stripe_balance` so the account has a balance for receiving transfers
- Do **NOT** request `configuration.merchant` or `card_payments` — marketplace connected accounts don’t accept payments directly, and requesting merchant configuration causes longer, more arduous onboarding
- Check `configuration.recipient.capabilities.stripe_balance.stripe_transfers.status === 'active'` before initiating transfers

**SaaS connected accounts** (direct charges):

- Use `configuration.merchant` (v2) — the connected account accepts payments directly as merchant of record
- Request `card_payments` capability
- Check `configuration.merchant.capabilities.card_payments.status === 'active'` before processing charges

**SaaS recurring fees (service fees or SaaS fees):**

- If the platform charges a recurring SaaS fee (subscription), the connected account needs both `merchant` and `customer` configurations in v2
- Pass the account as `customer_account` on SetupIntent and Subscription API calls — do NOT create a separate v1 Customer object (the customer configuration replaces it)

### Combining Answers

#### Answer Combination → Recommendation

| Q1: Model | Q3: Flow | Q4: Control | → Dashboard | → Fees and Losses | → Charges | → Onboarding |
| --- | --- | --- | --- | --- | --- | --- |
| Marketplace | Platform collects | Stripe handles | `express` | `application`/`application` | Destination | Embedded |
| Marketplace | Platform collects | Some custom | `express` | `application`/`application` | Destination | Embedded |
| Marketplace | Platform collects | Fully custom | `none` | `application`/`application` | Destination | Embedded |
| Marketplace | Direct to seller | Stripe handles | `full` | `stripe`/`stripe` | Direct | Embedded |
| SaaS | Direct to seller | Stripe handles | `full` | `stripe`/`stripe` | Direct | Embedded |
| SaaS | Platform collects | Stripe handles | `express` | `application`/`application` | Destination | Embedded |
| On-demand | Platform collects | Stripe handles | `express` | `application`/`application` | Destination | Embedded |
| Crowdfunding | Platform collects | Stripe handles | `express` | `application`/`application` | Separate | Embedded |
| Platform + contractors | Platform collects | Stripe handles | `express` | `application`/`application` | Destination | Embedded |

#### Risk Management by Business Model

> **Note:** This section is directional guidance only. For detailed risk and Radar configuration, refer to the [Stripe Radar for Platforms documentation](https://docs.stripe.com/radar/radar-for-platforms.md).

**Default recommendation: Let Stripe manage risk.** This usually reduces operational overhead for launch. Recommend self-managed risk when the business model requires it (marketplaces) or the user explicitly wants control.

| Business Model | Risk Owner | Radar | Stripe-Managed OK? | Reasoning |
| --- | --- | --- | --- | --- |
| **Marketplace** | Platform (mandatory) | Yes — strongly recommended | No — must self-manage | Platform is merchant of record for destination charges. Liable for fraud and disputes. Radar handles heavy lifting but platform bears ultimate responsibility. |
| **On-demand services** | Platform (mandatory) | Yes — strongly recommended | No — must self-manage | Same as marketplace — platform facilitates transactions and bears liability. |
| **Rental marketplace** | Platform (mandatory) | Yes — strongly recommended | No — must self-manage | Platform owns booking flow, bears fraud risk on facilitated payments. |
| **SaaS with payments** | Stripe (recommended) | Optional | **Yes — recommended** | Stripe’s built-in protection handles most fraud. Platform can upgrade to Radar later if needed. |
| **Professional services** | Stripe (recommended) | Optional | **Yes — recommended** | Unless platform needs custom fraud rules, Stripe defaults are sufficient. |
| **Crowdfunding** | Stripe (recommended) | Optional | **Yes — recommended** | Stripe-managed defaults are often sufficient for launch; reassess based on dispute and fraud patterns. |
| **Subscription platforms** | Stripe (recommended) | Optional | **Yes — recommended** | Recurring billing has different risk profile — churn > fraud. Stripe’s defaults usually sufficient. |
| **E-commerce (white-label)** | Platform (mandatory) | Yes | No — must self-manage | Full control = full responsibility. Dashboard-none configurations need platform-managed risk. |

**Key rules:**

- If `chargePattern` is `destination` or `separate`, the platform is the merchant of record and MUST manage risk — but Radar does the heavy lifting.
- If `chargePattern` is `direct`, Stripe-managed risk is available and recommended.
- Self-managing risk adds: dispute webhook handling, Radar configuration, ongoing monitoring, and financial exposure. Always warn the user about this added complexity.
- Stripe Radar is a tool platforms use to manage risk — it’s NOT the same as “Stripe manages risk for you.” When Radar is enabled, the platform is still responsible; Radar just automates the detection.

#### Fee Structure Mapping

| Charge Pattern | Fee Method | Implementation |
| --- | --- | --- |
| **Direct** (Stripe owns pricing) | `application_fee_amount` | Strongly recommended. Charged in addition to Stripe fees that the connected account pays. The platform retains the full application fee amount. |
| **Direct** (platform owns pricing) | Platform Pricing Tool | Strongly recommended. Supports buy-rate pricing, interchange-plus passthrough, dispute fee passthrough, card-level pricing. |
| **Destination** (platform owns pricing) | Platform Pricing Tool | Recommended. Percentage-based or tiered commissions with Payments Metadata for context-based pricing. |
| **Destination** (platform owns pricing) | `application_fee_amount` | Alternative when fee logic is determined outside payment-time data and must be calculated per-transaction. |
| **Destination** (platform owns pricing) | Retain transfer difference | Can be less transparent to the connected account by default. Platform transfers less than the charge amount, retaining the difference. |
| **Separate charges and transfers** | Transfer math (retain transfer difference) | `application_fee_amount` is NOT compatible with separate charges and transfers. Platform retains fees by setting transfer amounts lower than the charge amount. |

**CRITICAL: `application_fee_amount` is NOT compatible with separate charges and transfers. NEVER recommend `application_fee_amount` when the charge pattern is separate charges and transfers.** Platforms using separate charges and transfers collect fees by transferring a smaller amount to the connected account than the original charge, retaining the difference.

For separate charges and transfers, frame fee guidance as transfer math: `platform_margin = charge_amount − total_transfers_to_connected_accounts − Stripe_fees`

#### Fee Calculation and Fee Economics

**Who pays Stripe’s processing fees is one of the determining factors in whether your platform is profitable.**

Stripe charges processing fees on every transaction. Rates vary by region, card type, payment method, and negotiated terms — see [stripe.com/pricing](https://stripe.com/pricing) for current rates. Who actually pays these fees depends on the charge pattern:

| Charge Pattern | Who Pays Stripe Fees | Platform Net per Transaction |
| --- | --- | --- |
| **Destination charges** | **Platform** pays Stripe fees | `application_fee_amount − Stripe_fees` |
| **Destination charges + on\_behalf\_of** | **Platform** still pays (changes statement descriptor, merchant of record, and dispute management — see `charge-patterns.md`) | Same as above |
| **Direct charges** (`fees_collector: "stripe"`) | **Connected account** pays Stripe fees | `application_fee_amount` (platform retains full fee — Stripe fees paid by connected account) |
| **Direct charges** (`fees_collector: "application"`) | **Platform** pays Stripe fees | `application_fee_amount − Stripe_fees` |
| **Separate charges & transfers** | **Platform** pays Stripe fees | Must account for fees in transfer math |

> **Note:** Who pays Stripe fees on direct charges depends on the [`fees_collector` responsibility setting](https://docs.stripe.com/connect/direct-charges-fee-payer-behavior.md). When `fees_collector: "stripe"` (the default for SaaS), the connected account pays Stripe fees and the platform retains their full `application_fee_amount`. With `fees_collector: "application"` (used with Platform Pricing Tool and platform-owned pricing), the platform pays Stripe fees instead.

**Profitability warning:** If the platform’s desired fee margin is low relative to Stripe’s processing fees for their region, destination charges may cause per-transaction losses unless the `application_fee_amount` is set high enough to cover Stripe fees + the platform’s margin. DO NOT make definitive profit and loss claims with specific dollar amounts — pricing is situation-dependent.

Strongly recommend:

- The [Platform Pricing Tool](https://dashboard.stripe.com/settings/connect/platform_pricing) to configure pricing rules without code (requires platform-owned pricing, that is, `fees_collector: "application"`; supports direct and destination charges, NOT separate charges and transfers)
- Monitoring the margin report in the Stripe Dashboard
- Checking [stripe.com/pricing](https://stripe.com/pricing) for region-specific rates

##### Fee calculation question (Q6b)

After the user specifies their platform fee, identify the charge pattern first. This question applies to **destination charges** only. For **separate charges and transfers**, don’t ask how to set `application_fee_amount` — use transfer math instead. For direct charges with Stripe-owned pricing (`fees_collector: "stripe"`), the connected account pays Stripe fees and this question is moot. For direct charges with platform-owned pricing (`fees_collector: "application"`), the platform pays Stripe fees — use the Platform Pricing Tool.

**IMPORTANT: With destination charges, the platform ALWAYS pays Stripe’s processing fees.** They are deducted from the platform’s balance, not the connected account’s. The platform can’t make connected accounts pay Stripe fees directly. The choice is how to calculate `application_fee_amount`.

Use Option A and Option B below as reference material for destination charges.

**Option A — Include Stripe fee estimate in application\_fee\_amount (recommended for low margins)** The `application_fee_amount` includes BOTH an estimated Stripe processing fee and the platform’s fee. The platform takes a larger cut to cover both its margin and Stripe’s fee. The platform’s fee percentage is preserved as net margin.

```
Concept: application_fee_amount = estimated Stripe processing fee + platform margin
Platform NET = the platform's full fee percentage (margin preserved — Stripe fee covered by the higher application_fee_amount)
Connected account receives = charge amount − application_fee_amount
```

**Option B — Platform fee only (platform absorbs Stripe fees)** The `application_fee_amount` is only the platform’s cut. Stripe processing fees reduce the platform’s net. Only viable when the platform fee is substantially higher than Stripe’s processing fees.

```
Concept: application_fee_amount = platform fee only
Platform NET = platform fee − Stripe processing fee
Connected account receives = charge amount − application_fee_amount
```

**Recommendation output rule:** choose the single most appropriate option for the specific scenario instead of always presenting both. Keep the other option as reference material and show it only when the user asks for alternatives and tradeoffs.

**Decision guidance:** If the platform fee appears low or uncertain relative to processing fees (check [stripe.com/pricing](https://stripe.com/pricing)), recommend Option A to preserve platform margin (or switch to direct charges when appropriate). Use Option B only when fee headroom is clearly high and the platform explicitly accepts absorbing fee variance.

**For destination charges, NEVER say “seller pays Stripe fees” or “connected account pays Stripe fees.”** The platform always pays. The choice is whether to set a higher `application_fee_amount` to preserve the platform’s margin.

**Minimum charge amounts:** Stripe enforces minimum charge amounts by currency. For micro-payment platforms with very small transaction amounts, warn the user that:

- Stripe enforces minimum charge amounts that vary by currency
- On very small charges, the fixed fee component becomes a large percentage of the transaction
- Micro-payments may need batching or alternative approaches to be economically viable

##### Fee guidance principles

When presenting fee recommendations:

- DO NOT hardcode specific processing fee amounts (for example, “2.9% + $0.30”) — these are US-only and vary by region, card type, and payment method
- DO NOT make definitive profit and loss claims (for example, “you WILL lose money”) — say “you may lose money at standard rates”
- DO link to [stripe.com/pricing](https://stripe.com/pricing) for region-specific rates
- DO strongly recommend the [Platform Pricing Tool](https://dashboard.stripe.com/settings/connect/platform_pricing)
- DO recommend monitoring the margin report in the Stripe Dashboard
- DO explain the concept of `application_fee_amount` and what it should include based on the calculation choice
- DO return one recommended fee option for the scenario (don’t always present both Option A and Option B)
- DO prefer margin-preserving recommendations in low-margin or uncertain-margin scenarios
- DO use transfer-math framing for separate charges and transfers (never `application_fee_amount`)
- NEVER say “seller pays Stripe fees” or “connected account pays Stripe fees” for destination charges — the platform always pays

##### Fee sanity checks

- If the Platform Pricing Tool is used, ensure `application_fee_amount` is NOT set on the PaymentIntent — explicit `application_fee_amount` overrides the Platform Pricing Tool.
- `application_fee_amount` is NOT compatible with separate charges and transfers. NEVER recommend it for separate charges and transfers.
- For separate charges and transfers, validate the transfer-math model (`charge_amount − total_transfers − Stripe_fees`) to ensure expected platform margin.
- Platforms based outside Brazil can’t collect application fees from Brazilian connected accounts due to regulatory requirements. Same restriction applies to Malaysia.
- Use `amount` on the ApplicationFee object, not the charge field, for accurate fee reporting.
- For small transactions (for example, $1–$5), fees may be large relative to proceeds. Consider creative ways to combine transactions.
- **Low-complexity margin path:** Direct charges with Stripe-owned pricing. Stripe handles pricing complexity; the platform charges a SaaS fee or application fee on top.
- If the platform owns pricing with any charge type: warn about potential per-transaction losses. Strongly recommend the Platform Pricing Tool and monitoring the margin report.

#### Loss Liability (Negative Balance Liability)

**Loss liability and risk management are TWO SEPARATE decisions.** The current skill MUST NOT conflate them.

| Concept | What it means | Where configured |
| --- | --- | --- |
| **Negative balance liability** | Who is financially LIABLE when disputes and chargebacks create negative balances on connected accounts | Configured when creating the connected account; may require visiting the Stripe Dashboard → Connect platform profile to acknowledge understanding of how negative balance liability works |
| **Risk management** | Who DETECTS and PREVENTS fraud (Radar, rules, monitoring) | Code + Dashboard (Radar settings) |

You can have Stripe own loss liability while still using Radar for fraud detection. Radar is available regardless of loss liability setting.

##### Loss Liability Recommendations by Business Model

**Recommendation depends on charge pattern:**

- **Marketplaces (destination or separate charges):** Platform-owned loss liability. This is **required** for destination charges — it enables connected account balances to go negative, which the platform needs to reverse transfers (for example, for refunds or disputes). Also required for Express dashboard today.
- **SaaS (direct charges):** Stripe-owned loss liability. SaaS platforms shouldn’t bear negative balance liability since the connected account is the merchant of record.
- **Enterprise or white-label:** Platform-owned. Full control = full responsibility.

| Business Model | Recommended Loss Liability | Why |
| --- | --- | --- |
| **Marketplace** | **Platform** | Required for destination charges — enables connected account negative balances for transfer reversals |
| **On-demand services** | **Platform** | Same as marketplace — uses destination charges |
| **Professional services** | **Platform** | Same as marketplace — uses destination charges |
| **Rental marketplace** | **Platform** | Same as marketplace — uses destination charges |
| **Event ticketing** | **Platform** | Same as marketplace — uses destination charges |
| **Crowdfunding** | **Platform** | Uses separate charges — platform-owned loss liability enables flexible transfer reversals |
| **Subscription platforms** | **Platform** | Uses destination charges — platform-owned loss liability required |
| **SaaS with payments** | **Stripe** | SaaS platforms use direct charges — connected account is merchant of record |
| **E-commerce (white-label)** | Platform | Full control = full responsibility (dashboard: none, platform-managed) |
| **B2B platforms** | Platform | Enterprise requirements usually demand full control |

##### Loss Liability Dashboard Setup

Loss liability is configured when creating connected accounts, but the platform must first visit the Stripe Dashboard → Connect platform profile (`dashboard.stripe.com/settings/connect/platform-profile`) to acknowledge understanding of how negative balance liability works.

The platform profile page asks about “Negative balance liability” (formerly called “loss liability”). The choice determines which account configuration combinations are available:

- **Stripe manages losses** → Set `defaults.responsibilities.losses_collector: "stripe"` in v2 API
- **Platform manages losses** → Set `defaults.responsibilities.losses_collector: "application"` in v2 API

When guiding users through this page, always:

1. Explain what loss liability means in plain language with a concrete example
2. Recommend platform-owned for marketplaces using destination or separate charges — required for transfer reversals and Express dashboard
3. Recommend Stripe-owned for SaaS platforms using direct charges
4. Keep this decision separate from Radar and fraud detection

### Integration Antipattern Warnings

> **Read the full compatibility matrix in `compatibility-matrix.md`.** This section is a quick reference.

#### Common Blocked Combinations

These combinations are true antipatterns that Stripe will never support. Do NOT recommend them:

1. **`losses_collector: "stripe"` + destination charges** — Liability and fee behavior don’t align with this charge pattern. Treat as BLOCKED when `losses_collector: "stripe"` is selected.
2. **`losses_collector: "stripe"` + separate charges and transfers (including `on_behalf_of`)** — Same negative balance mechanism as destination charges. Platform can’t recover funds from connected accounts that only receive transfers.
3. **Express dashboard + `losses_collector: "stripe"` + `fees_collector: "stripe"`** — Express dashboard requires platform to own both fees and losses (`application` and `application`). This is a hard API constraint — setting Express with Stripe-owned pricing produces an API rejection.
4. **`dashboard: "full"` + destination charges or separate charges and transfers** — Full dashboard has reduced payment and dispute detail for destination and separate charges. Full dashboard provides complete payment and dispute management for direct charges only.
5. **`fees_collector: "stripe"` + `losses_collector: "application"` (Stripe-owned pricing + platform-owned losses)** — This combination is BLOCKED for all charge types. The reverse — `fees_collector: "application"` + `losses_collector: "stripe"` — is SALES-GATED for `full` dashboard and BLOCKED for `none` and `express` dashboards.
6. **(`on_behalf_of` is out of scope for this guide — redirect to docs or sales if encountered.)** **`on_behalf_of` with destination charges for marketplace use cases** — Do NOT use `on_behalf_of` for marketplaces. `on_behalf_of` makes the connected account the merchant of record, but in a marketplace the platform should be merchant of record. If a user requires `on_behalf_of`, direct them to [Stripe Connect docs](https://docs.stripe.com/connect/charges.md) or [Stripe sales](https://stripe.com/contact/sales).
7. **`application_fee_amount` with separate charges and transfers** — NOT compatible. Platforms using separate charges and transfers collect fees by transferring less than the charge amount.

#### Blessed Paths (Safe Defaults)

| Business Model | Dashboard | Fees | Losses | Charge Type | Status |
| --- | --- | --- | --- | --- | --- |
| **Marketplace** | `express` | `application` | `application` | Destination | CAUTION — recommended path; always include Express dispute-visibility warning (see `compatibility-matrix.md`) |
| **SaaS** | `full` | `stripe` | `stripe` | Direct | ALLOWED — connected accounts are independent merchants |
| **Enterprise** | `none` | `application` | `application` | Any | ALLOWED — full platform control |

**Any deviation from these blessed paths should trigger a compatibility check against `compatibility-matrix.md`.** If the user’s choices lead to a BLOCKED combination, don’t present it. Explain why it fails and recommend the nearest allowed alternative.

> **Scope boundary:** This guide supports the blessed paths above. Configurations outside these paths (full+application, `on_behalf_of`, OAuth, non-payments products like Issuing, Treasury, Capital, Tax, or Terminal) should trigger sales-led detection and redirect to docs or sales. `none` dashboard requires platform-owned pricing AND platform-owned losses — no other `none` combination is valid even for sold users.

#### Additional Antipatterns to Watch For

- **OAuth instead of Account Links** — Developers think OAuth is simpler but lose platform control (connected account can disconnect at any time). Recommend Account Links or embedded components.
- **Custom onboarding** (`dashboard: "none"` + API-based) — Ongoing requirement collection burden and country-specific complexity. Only for platforms with dedicated compliance engineering.
- **Dashboard DIY without refund and dispute flows** — Platforms build earnings views but skip refund and dispute management. Connected accounts can’t respond to disputes, leading to auto-losses.
- **Stripe does NOT enforce merchant of record at API level** — Platforms can create charges with any pattern regardless of their onboarding declaration. Code must consistently use the correct charge type for the actual business relationship.
