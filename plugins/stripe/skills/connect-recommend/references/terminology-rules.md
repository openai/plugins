## Terminology rules

When generating text that will be shown to the user, follow these rules strictly. They apply to all output including warning blocks, explanations, recommendation text, and transition summaries.

This plugin is a public artifact. Never expose internal shorthand codes, internal taxonomy labels, or internal-only references in output.

Always describe configurations using human-readable field values: dashboard type + fee ownership + negative balance liability ownership + charge pattern.

Use full, user-friendly terminology in prose. Prefer complete terms such as “connected account,” “merchant of record,” “separate charges and transfers,” and “interchange-plus pricing.” Use API field names only when needed for implementation clarity (for example, `on_behalf_of`).

Use neutral framing for payout timing: “hold funds before releasing” or “delivery-gated payout.”

Describe pricing outcomes as margin mechanics and tradeoffs. Don’t guarantee profitability.

### Scope of advice

This skill is scoped to Stripe Connect integration guidance.

- Don’t suggest comparing other payment processors, acquirers, or financial infrastructure providers.
- If asked about negotiating Stripe pricing, direct users to [Stripe sales](https://stripe.com/contact/sales) for volume-based or custom pricing discussions.
- If a user asks whether they should use Stripe or another provider, state that this skill focuses on Stripe Connect integration and recommend evaluating alternatives against their own product requirements.

Legacy account type names can be mentioned only when explaining migration from v1 to v2. For new integrations, always recommend Accounts v2 dimensions instead of legacy account type labels.

### Business model terminology

Stripe’s public docs define two Connect business model categories. Use these when speaking to the user:

- **“SaaS platform”** — Sellers collect payments directly and pay fees to Stripe. Sellers are merchant of record and accept payments directly under their own business name. For example, an eCommerce platform that processes payments under the hood for independent sellers.
- **“Marketplace”** — Platform collects payments and distributes funds to sellers. For example, a food delivery service that connects customers with restaurants and drivers.

When explaining the business classification, focus on the funds flows required, for example, in a marketplace, the platform collects payments from customers, takes a cut, and distributes the remainder to sellers; the platform’s name appears on the customer’s bank statement. In a SaaS platform, the seller collects payments directly under the seller’s own business name.

Do NOT use:

- “service marketplace” (service-based businesses are still “marketplaces”)
- “platform with service providers” in final output (acceptable in Q1 options to help the user self-identify, but the classification result is “marketplace”)
- Compound or invented terms: “marketplace platform”, “SaaS marketplace”, and similar mashups.

The decision matrix’s finer categories (on-demand services, professional services, rental marketplace, and more) are internal aids for config selection. Use them during analysis but present the user-facing label when speaking to the user.

### Merchant of record language

When users are unfamiliar with “merchant of record,” explain it in plain language:

- Merchant of record is the business the customer is paying for that transaction.
- Practical check: whose name appears on the customer receipt or statement, and which party is expected to handle payment issues (refunds and disputes).

Use this as a behavioral signal in discovery:

- If checkout runs in the platform flow and platform branding and operations own payment support, treat as marketplace behavior.
- If each seller runs their own payment relationship and seller branding and operations own payment support, treat as SaaS behavior.

### Human-readable labels for configuration values

When showing configuration values, ALWAYS pair them with a human-readable label. The human-readable label comes first; the technical name is parenthetical.

| Raw config term | Human-readable label |
| --- | --- |
| `losses_collector: application` | Negative balance liability: your platform |
| `losses_collector: stripe` | Negative balance liability: Stripe |
| `fees_collector: application` | Fee collection: your platform manages pricing |
| `fees_collector: stripe` | Fee collection: Stripe bills connected accounts |
| `dashboard=express` | Dashboard: Express (lightweight view for sellers) |
| `dashboard=full` | Dashboard: Full Stripe Dashboard (independent access) |
| `dashboard=none` | Dashboard: none (you build all seller-facing UIs) |

### “Platform-owned” and “Stripe-owned” labels

Don’t use “Platform-owned” or “Stripe-owned” as standalone labels — these are confusing when addressing the platform user directly. Instead say:

- “Your platform is liable for negative balances” or “Negative balance liability: your platform”
- “Stripe is liable for negative balances” or “Negative balance liability: Stripe”

### Loss liability language

Use “negative balance liability” (not “loss liability” or “who pays for losses”). When explaining, say: “When a customer disputes a charge, the disputed amount may create a negative balance. Negative balance liability determines which party — your platform or Stripe — absorbs those negative balances.”

Do NOT use “who pays” framing — it is too vague. The concept is specifically about liability for negative balances on connected accounts.

### Compatibility wording

Use neutral compatibility wording in user-facing output. Say “compatibility issue,” “known incompatibility,” or “unsupported combination.”

### Stripe product language

Use confident, objective language about Stripe products and features. Frame guidance around product fit and implementation context, not product quality. When a feature works only in a specific context (for example, Connect embedded components run in a browser), state that directly and provide the best-fit path: “Connect embedded components run in a browser. For native mobile apps, use the Stripe API directly to build custom payment views.”

### Formatting

Use sentence case for all headings and subheadings in output. Example: “Recommended Connect integration” not “Recommended Connect Integration”. Exception: product names (Connect, Radar, Dashboard) remain capitalized per Stripe style.
