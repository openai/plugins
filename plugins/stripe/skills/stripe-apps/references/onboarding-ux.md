# Onboarding UX — first-run user experience

## Onboarding UX

**Plain-language:** “When someone installs your app for the first time, the first thing they see is your app’s welcome or setup screen. This is called onboarding.”

Design this experience carefully — it determines whether merchants understand how to use your app or give up immediately.

**Canonical page:** https://docs.stripe.com/stripe-apps/patterns/onboarding-experience

Read this page using WebFetch for the correct component props and patterns.

## Options from simplest to most complex

### Option 1 — Zero-touch onboarding (easiest)

If your app only uses Stripe data and doesn’t need its own login, there’s nothing to set up. The app works immediately after install.

Use `fetchStripeSignature` to identify the user without a login screen — the user’s Stripe identity proves who they are.

**When to use:** When your app doesn’t need third-party credentials or a separate user account.

### Option 2 — OnboardingView component

Show a setup screen the first time the user opens the app. Use the `onboarding` viewport to show a dedicated onboarding page.

In `stripe-app.yaml`, add the `onboarding` viewport:

```yaml
ui_extension:
  views:
    - viewport: onboarding
      component: OnboardingView
    - viewport: stripe.dashboard.customer.detail
      component: App
```

For the correct `OnboardingView` component props and structure, read the canonical onboarding page. Key requirements:

- Use the `OnboardingView` component (not `ContextView`) for the onboarding viewport
- Include required props like `completed`, `tasks`, and `title`

### Option 3 — SignInView component (third-party login)

If users need to log in to a third-party service (connecting their Google account, Mailchimp, etc.), use `SignInView` to guide them.

For the correct `SignInView` props and usage, read: https://docs.stripe.com/stripe-apps/patterns/onboarding-experience

Use the Secret Store API to save the resulting OAuth token. See `backend.md`.

## Critical rule: always check onboarding status in every view

Don’t assume the user went through the onboarding flow in order. They might open a payment page before completing setup.

Check at the start of every page-specific view whether onboarding is complete. If not, show a prompt directing them to complete setup.

## Storing onboarding state

Use the Secret Store API to remember whether a user has completed onboarding.

For the correct Secret Store API patterns, read: https://docs.stripe.com/stripe-apps/store-secrets

Key facts:

- Use `user` scope for per-user onboarding state
- Use `account` scope for account-wide configuration
- Maximum 10 secrets per scope
