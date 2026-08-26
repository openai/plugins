# UI extensions — constraints and patterns

## UI extensions

UI extensions render custom UI inside the Stripe Dashboard. They run in a sandboxed iframe, which means they have different constraints from a normal React app.

## Canonical documentation

Before writing UI extension code, read these pages using WebFetch:

| Topic | URL |
| --- | --- |
| How UI extensions work (constraints, props, lifecycle) | https://docs.stripe.com/stripe-apps/how-ui-extensions-work |
| SDK API reference (Stripe client setup, context props) | https://docs.stripe.com/stripe-apps/reference/extensions-sdk-api |
| UI components catalog | https://docs.stripe.com/stripe-apps/components |
| Viewports reference | https://docs.stripe.com/stripe-apps/reference/viewports |
| Full-page apps (private preview) | https://docs.stripe.com/stripe-apps/patterns/full-page-apps |

## BLOCKED — these cause silent failures in the sandboxed iframe

| BLOCKED | Why |
| --- | --- |
| Any HTML element: `<div>`, `<span>`, `<p>`, `<button>`, `<input>`, `<form>`, `<h1>`-`<h6>` | Only SDK components render in the iframe |
| Tailwind, MUI, Bootstrap, styled-components, any CSS | Only `@stripe/ui-extension-sdk/ui` components |
| React 18+ APIs (`useId`, `useDeferredValue`, `useTransition`, concurrent features) | Stripe Apps run React 17.0.2 |
| `window`, `document`, `localStorage`, `sessionStorage` | Not available in sandboxed iframe |
| `react-hook-form` or any ref-based form library | Use uncontrolled components with `defaultValue` + `onChange` |
| Arbitrary `fetch()` calls to external URLs | Use `fetchStripeSignature` for your backend; use the SDK client for Stripe APIs |

## What you can use

- `@stripe/ui-extension-sdk/ui` — the Stripe UI component library (the **only** way to build UI)
- React 17 hooks and components
- The Stripe SDK client initialized per the Extensions SDK API docs
- `fetchStripeSignature` from `@stripe/ui-extension-sdk/utils` for authenticating to your own backend
- `environment.objectContext` to get the current Stripe object (e.g. the customer being viewed)
- `@stripe/ui-extension-sdk/testing` for unit tests

## Accessing Stripe data from the UI

For the correct way to initialize the Stripe client in a UI extension, read: https://docs.stripe.com/stripe-apps/reference/extensions-sdk-api

Key facts:

- `createHttpClient` from `@stripe/ui-extension-sdk/http_client` is an HTTP adapter passed to the Stripe constructor
- `STRIPE_API_KEY` is a special constant (not a real key) — it tells the SDK to use the app’s granted permissions
- After initialization, use standard Stripe SDK methods (e.g. `stripe.customers.retrieve()`)

### Current page context

Use `environment.objectContext` to get the Stripe object on the current page:

```tsx
const MyView = ({ environment }) => {
  const objectId = environment.objectContext?.id; // e.g. "cus_xxx"
};
```

### User context

The `userContext` prop provides the signed-in user’s identity. It is a **top-level prop** passed to your component (not nested under `environment`):

```tsx
const MyView = ({ userContext }) => {
  const accountId = userContext.account.id;
  const userId = userContext.id;
};
```

## Component basics

All UI is built with components from `@stripe/ui-extension-sdk/ui`. For the full component catalog and import paths, read: https://docs.stripe.com/stripe-apps/components

Common components include Box, Button, Icon, Inline, List, ListItem, Select, Spinner, TextField, and ContextView — but check the docs for the current list.

## Page-specific viewports

For apps that appear next to a Stripe object (customer, payment, etc.):

```yaml
ui_extension:
  views:
    - viewport: stripe.dashboard.customer.detail
      component: App
```

The component receives the current object’s ID via `environment.objectContext.id`.

## Full-page apps (private preview)

Full-page apps give your app a dedicated page in the Dashboard navigation. This feature is in **private preview** — confirm the user has access before suggesting this approach.

For implementation details, read: https://docs.stripe.com/stripe-apps/patterns/full-page-apps

The correct component for full-page apps is `FullPageView` (not `ContextView`).

## Testing UI extensions

Use `@stripe/ui-extension-sdk/testing` with Jest and `@testing-library/react`.

Key facts:

- Import `getMockContextProps` to create mock environment/userContext props
- Pass `objectContext` in the mock to simulate page-specific context (e.g. `{ id: "cus_test123", object: "customer" }`)
- Use standard `render` and `screen` from `@testing-library/react`

Run tests: `pnpm test`

## Declaring permissions in stripe-app.yaml

Every Stripe API resource your app accesses must be declared as a permission. Undeclared permissions cause API calls to fail with an invalid-request error.

Use the CLI to declare permissions (updates `stripe-app.yaml` automatically):

```bash
stripe apps grant permission "customer_read" "Display customer information in the app"
stripe apps grant permission "payment_intent_read" "Show payment history"
```

For the full permissions reference, read: https://docs.stripe.com/stripe-apps/reference/permissions
