# Authentication — platform keys, OAuth, restricted API keys

## Authentication

How your app authenticates and accesses Stripe data for merchants who install it.

**Canonical page:** https://docs.stripe.com/stripe-apps/api-authentication

Read this page using WebFetch before implementing authentication patterns.

## Three authentication types

Stripe Apps supports three authentication methods, configured via `stripe_api_access_type` in the app manifest:

| Auth type | Manifest value | How it works | Best for |
| --- | --- | --- | --- |
| Restricted API key (recommended) | `restricted_api_key` | Stripe generates a scoped key at install; merchant provides it to your system | Private apps, simpler integrations, apps that don’t need Connect-style access |
| Platform keys | `platform` | Your secret key + `Stripe-Account` header to act on behalf of installers | Public/marketplace apps that need to act across many merchants |
| OAuth 2.0 | `oauth` | Standard OAuth flow generates access tokens per-account | Apps where merchant must be merchant-of-record |

### Choosing the right type

**Default to restricted API keys** unless you have a specific reason to use platform keys or OAuth. RAKs are simpler, more secure (scoped permissions), and don’t create a Connect-style relationship.

Use a different type when:

1. **You need Connect webhook fanout** (events from all merchants to one endpoint): Platform keys.
2. **You’re building a public marketplace app acting across many merchants:** Platform keys.
3. **The merchant must be the merchant-of-record for charges:** OAuth.
4. **Private app or fewer merchants, no Connect fanout needed:** Restricted API keys (simplest).

## Platform keys

Your app’s API key acts on behalf of a merchant’s account using the `Stripe-Account` header:

```javascript
// Use a restricted API key when possible; fall back to secret key only for platform-key apps
const stripe = require("stripe")(process.env.STRIPE_API_KEY);

await stripe.customers.list({}, {
  stripeAccount: "acct_xxxxx", // the merchant's account ID
});
```

**How to get the merchant’s account ID:**

- From a webhook event: `event.account`
- From `fetchStripeSignature` payload: the signed data includes `account_id`
- From the UI extension: `userContext.account.id` (top-level prop)

**Key fact:** Platform keys use the same `Stripe-Account` header mechanism as Stripe Connect. Installers are NOT onboarded as connected accounts in the traditional sense — the header simply authorizes your key to access their account within the app’s declared permissions.

## OAuth 2.0

Use OAuth when the connected account needs to be the merchant of record for charges, or when you need the merchant’s own Stripe identity on API calls.

Most apps do NOT need OAuth. Use platform keys unless you specifically need this.

For implementation, read: https://docs.stripe.com/stripe-apps/pkce-oauth-flow

## Restricted API keys

With RAK apps, Stripe generates a restricted key at install time with only the permissions your app declared. The merchant copies this key to your system.

Key differences from platform keys:

- No Connect-style relationship is created
- Can’t use Connect webhook fanout (each merchant manages their own webhooks)
- Simpler model for private apps or apps with fewer merchants

## Authenticating the UI to your backend (fetchStripeSignature)

`fetchStripeSignature` proves to your backend that a request came from a legitimate app installation.

Key facts:

- The signed payload contains `user_id` and `account_id` by default (field order matters)
- You can include additional data by passing it to `fetchStripeSignature(extraPayload)`
- Backend verifies with `stripe.webhooks.signature.verifyHeader()`
- The signing secret (starts with `absec_...`) is generated on first `stripe apps upload`

For the full implementation pattern, read: https://docs.stripe.com/stripe-apps/build-backend

## Identifying the installing merchant

When a merchant installs your app, Stripe sends an `account.application.authorized` event. When they uninstall, it sends `account.application.deauthorized`.

Store the account ID from `event.account` to make future API calls on their behalf.

## Permission scopes

Use the CLI to add permissions to your app:

```bash
stripe apps grant permission "customer_read" "Read customer data to show in the Dashboard"
stripe apps grant permission "event_read" "Receive webhook events"
```

This updates `stripe-app.yaml` with the correct format automatically.

**When you change permissions:** existing users must re-authorize. The app returns an invalid-request error for undeclared permissions until the user re-authorizes. See `publishing.md` for details.
