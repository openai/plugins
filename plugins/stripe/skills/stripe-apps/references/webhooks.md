# Webhooks — event delivery for Stripe Apps

## Webhooks

How your Stripe App receives and processes events (payments, customers, installs, etc.).

**Canonical page:** https://docs.stripe.com/stripe-apps/events

Read this page using WebFetch before implementing webhook handlers.

## Webhook configuration depends on app type

| App type | Auth type | Webhook setup |
| --- | --- | --- |
| Private (your account only) | Any | ONE standard webhook endpoint |
| Public/marketplace | Platform keys | ONE webhook with “Listen to events on Connected accounts” enabled |
| Public/marketplace | Restricted API keys | Can’t use Connect webhook fanout — each merchant manages their own |

A second test-mode endpoint is recommended for public apps but is not required.

## Required permissions

The `event_read` permission MUST be declared in your manifest for webhook event access, plus read permissions for each event type. Use the CLI to declare permissions:

```bash
stripe apps grant permission "event_read" "Receive webhook events"
stripe apps grant permission "payment_intent_read" "React to successful payments"
stripe apps grant permission "customer_read" "React to customer changes"
```

## Webhook handler requirements

For every webhook handler:

1. Use `stripe.webhooks.constructEvent()` to verify signatures
2. For public platform-key apps: check `event.account` to identify which merchant triggered the event
3. Use `stripeAccount` option to act on behalf of merchants (platform keys only)

## Local development

### Private app (events from your own account)

```bash
stripe listen --forward-to localhost:<PORT>/webhook
```

### Public platform-key app (events from connected accounts)

```bash
stripe listen --forward-connect-to localhost:<PORT>/webhook
```

**Important:** `--forward-to` only captures your own account’s events. Use `--forward-connect-to` for connected account events.

## Triggering test events

```bash
# Private app:
stripe trigger payment_intent.succeeded

# Public app (simulates connected account event):
stripe trigger --stripe-account payment_intent.succeeded
```

## Verifying webhook signatures

Always verify signatures to ensure the request came from Stripe. For the complete webhook verification pattern, read: https://docs.stripe.com/stripe-apps/build-backend

Key implementation facts:

- Use `stripe.webhooks.constructEvent()` with the raw request body and your webhook signing secret
- For platform-key apps, check `event.account` to identify which merchant triggered the event
- Use a restricted API key when possible (see `authentication.md`); use the secret key only for platform-key apps
- Return 200 quickly; process asynchronously if needed

## Handling installs and uninstalls

| Event | When it fires | What to do |
| --- | --- | --- |
| `account.application.authorized` | A merchant installs your app | Store the merchant’s account ID |
| `account.application.deauthorized` | A merchant uninstalls your app | Clean up stored data |

## Setting up webhooks in the Dashboard

1. Go to [Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Enter your endpoint URL
4. Select events to listen for
5. For public platform-key apps: check **“Listen to events on Connected accounts”**
6. Copy the signing secret to your environment variables

During local development, use `stripe listen` instead.
