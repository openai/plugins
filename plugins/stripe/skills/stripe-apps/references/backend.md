# Backend — when and how to add server-side logic

## When you need a backend

You need a backend if your app needs to:

- Store data long-term (user preferences, linked accounts, custom records)
- Call APIs that require server-side secrets (API keys that can’t be in the browser)
- Run logic when the user isn’t in the Dashboard (webhooks, scheduled jobs)
- Call third-party services securely (email providers, CRMs, spreadsheet APIs)
- Perform actions that take longer than the UI can wait for

**You don’t need a backend if:**

- Your app only reads and displays Stripe data (use the SDK client directly in the UI)
- You only need to store a small amount of sensitive data — use the Secret Store API instead

## Canonical documentation

Before writing backend code, read these pages using WebFetch:

| Topic | URL |
| --- | --- |
| Backend implementation + fetchStripeSignature | https://docs.stripe.com/stripe-apps/build-backend |
| Authentication types (determines backend pattern) | https://docs.stripe.com/stripe-apps/api-authentication |
| Events and webhooks | https://docs.stripe.com/stripe-apps/events |
| Secret Store API | https://docs.stripe.com/stripe-apps/store-secrets |

## Backend architecture decisions

### Authentication type determines the backend pattern

Your app’s `stripe_api_access_type` controls how the backend authenticates. See `authentication.md` for the full breakdown of auth types and when to use each one.

### CORS configuration

CORS (`Access-Control-Allow-Origin: *`) is needed ONLY on endpoints called by the UI extension. The UI runs in a sandboxed iframe with a `null` origin — specific origin allowlisting will not work.

Webhook endpoints do NOT need CORS — they receive requests from Stripe’s servers, not from the browser.

### fetchStripeSignature verification

`fetchStripeSignature` is how the UI extension authenticates requests to your backend. The signed payload and verification method are documented at https://docs.stripe.com/stripe-apps/build-backend.

Key facts:

- The signing secret (starts with `absec_...`) is generated on first `stripe apps upload`
- The default signed payload contains `user_id` and `account_id` (field order matters)
- Extra data can be included by passing it to `fetchStripeSignature(payload)`
- Verification uses `stripe.webhooks.signature.verifyHeader()`

### Webhook configuration

Webhook setup depends on your app’s distribution and auth type:

| App type | Webhook setup |
| --- | --- |
| Private (your account only) | ONE standard webhook endpoint |
| Public with platform keys | ONE webhook with “Listen to events on Connected accounts” enabled |
| Public with restricted API keys | Can’t use Connect webhook fanout — each merchant manages their own webhooks |

The `event_read` permission MUST be declared in your manifest, plus read permissions for each event type you want to receive.

Read https://docs.stripe.com/stripe-apps/events for the full setup guide.

For firewall allowlisting of inbound webhook traffic, see https://docs.stripe.com/ips for Stripe’s IP addresses.

## Secret Store API

**Plain-language:** “Stripe has a built-in secure place to store passwords, tokens, and API keys for your app — you don’t need to build your own database for secrets.”

### Two scopes

| Scope | Use for | Example |
| --- | --- | --- |
| `account` | Shared across all users of an account | The business’s API key for an email service |
| `user` | Per-user secrets | An individual user’s OAuth access token |

### Limits and restrictions

- Maximum **10 secrets per scope** (account and user separately)
- Always list and delete before adding more if approaching the limit
- Do **not** store PCI-sensitive data (card numbers, CVVs, bank account numbers)

### Declaring the permission

In `stripe-app.yaml`:

```yaml
declarations:
  stripe_api_access:
    permissions:
      - permission: secret_write
        purpose: Store third-party credentials for the app
```

### Implementation

For the correct code patterns to read, write, and delete secrets, read: https://docs.stripe.com/stripe-apps/store-secrets

## Local development with a backend

Run your backend locally alongside `stripe apps start`:

```bash
# Terminal 1: start the app preview
stripe apps start

# Terminal 2: start your backend server
node server.js
```

For webhook forwarding during local development, see `references/webhooks.md`.
