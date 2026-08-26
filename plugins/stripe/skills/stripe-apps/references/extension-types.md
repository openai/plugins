# Extension types

## Extension types

Stripe Apps supports five extension types. Use the discovery interview in `discovery.md` to determine which one the user needs.

### 1. UI extension — “show something in the Dashboard”

Renders custom UI inside the Stripe Dashboard using the Stripe UI toolkit. Runs in a sandboxed iframe.

**Plain-language examples:**

- “Show a customer’s loyalty points next to their Stripe profile”
- “Add a button to send a custom invoice email”
- “Build a full-screen analytics dashboard inside Stripe”
- “Show a customer’s order history from my store next to their Stripe data”

**What you can build:**

- Page-specific panels (next to a customer, payment, invoice, subscription, or product)
- A side panel that appears everywhere in the Dashboard
- A full-screen page inside the Dashboard
- A setup/onboarding screen when users first install the app
- An app settings page

**Key constraints:**

- React 17 only (not 18+)
- Only `@stripe/ui-extension-sdk/ui` components — no Tailwind, HTML, or third-party UI libraries
- Can’t access `window`, `document`, or `localStorage`
- Must use the SDK’s Stripe API client (see canonical docs for initialization pattern)

**Read:** `ui-extensions.md`, `workflow.md`

### 2. Backend-only app — “react to events, no Dashboard UI”

Runs on the developer’s server. Receives Stripe webhooks and calls the Stripe API. No Dashboard UI.

**Plain-language examples:**

- “Email a download link after a payment”
- “Sync purchases to a Google Sheet”
- “Create an order in my fulfillment system when a payment succeeds”
- “Notify my team on Slack when a new subscription starts”

**How it works:**

- Your server receives Stripe events (webhooks)
- Your server calls the Stripe API using platform keys (no manual key-sharing with merchants)
- No UI — all logic runs server-side

**Read:** `authentication.md`, `webhooks.md`, `backend.md`, `workflow.md`

### 3. Full-stack app — “Dashboard UI + backend server”

Combines a UI extension with a backend server. The UI can show data from external services and trigger server-side actions.

**Plain-language examples:**

- “Show my customer’s loyalty points in Stripe AND update them when they make a purchase”
- “Let merchants configure their email templates from the Dashboard, then send emails from my server”
- “Show real-time shipping status next to each payment”

**How it works:**

- UI extension in the Dashboard for user interaction
- Backend server for data storage, third-party API calls, and webhook processing
- UI authenticates to the backend using `fetchStripeSignature`

**Read:** all reference files

### 4. Extension interfaces — “plug into Stripe’s billing or payments engine” (private preview)

Lets your app change how Stripe processes billing or payments. Available types:

**Billing extensions:**

- Custom discount calculation
- Custom proration calculation
- Custom customer balance handling
- Custom recurring billing item handling

**Payments orchestration:**

- Custom payment routing

**Private preview:** Extension interfaces are not generally available. If the user asks for this:

1. Explain it’s in private preview
2. Tell them to check the Stripe Apps documentation for the latest access information
3. Ask them to check access and return when they have it
4. Do not attempt to build anything until access is confirmed

### 5. Embedded apps — “embed a third-party Stripe App inside your platform” (private preview)

For Connect platforms that want to surface third-party Stripe Apps (like QuickBooks, Xero, or Mailchimp) directly inside their own product.

**This is different from building an app.** Embedded apps are for platforms that want to *host* existing apps, not for building new ones.

**Private preview:** If the user asks for this, point them to https://docs.stripe.com/stripe-apps/embedded-apps.

## Full viewport routing table

For UI extensions — maps plain-language descriptions to viewport IDs:

| What the user wants | Viewport ID |
| --- | --- |
| Next to a specific customer | `stripe.dashboard.customer.detail` |
| On the customers list page | `stripe.dashboard.customer.list` |
| Next to a specific payment | `stripe.dashboard.payment.detail` |
| On the payments list page | `stripe.dashboard.payment.list` |
| Next to a specific invoice | `stripe.dashboard.invoice.detail` |
| On the invoices list page | `stripe.dashboard.invoice.list` |
| Next to a specific subscription | `stripe.dashboard.subscription.detail` |
| On the subscriptions list page | `stripe.dashboard.subscription.list` |
| Next to a specific product | `stripe.dashboard.product.detail` |
| On the products list page | `stripe.dashboard.product.list` |
| Everywhere in the Dashboard (side panel) | `stripe.dashboard.drawer.default` |
| As its own full-screen page | Full-page app — `stripe.dashboard.fullpage` |
| On the Dashboard homepage | `stripe.dashboard.home.overview` |
| App settings page | `settings` |
| First-run setup after install | `onboarding` |

For the full viewport reference, see https://docs.stripe.com/stripe-apps/reference/viewports.
