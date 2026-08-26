# Discovery interview

## Discovery interview

Run this interview **before writing any code**. Ask one question at a time. Never use Stripe-internal jargon until after routing is complete.

### Question 1 — What do you want to do?

```
What would you like your app to do? Pick the option that sounds closest:

1. Show something or add a button/panel inside my Stripe Dashboard
   (for example: show a customer's loyalty points, add a "Send email" button)

2. Automatically do something when a payment or event happens
   (for example: send a confirmation email, update a spreadsheet, sync data)

3. Both — add something to the Dashboard AND react to Stripe events

4. Let merchants connect their Stripe account to my service without sharing API keys

5. Add custom logic to how Stripe calculates bills or routes payments
   (advanced — private preview)

6. I'm not sure — ask me more questions
```

**Routing:**

- Option 1 → UI extension. Ask Question 2.
- Option 2 → Backend-only app. Ask Question 3. Then read `backend.md`, `webhooks.md`, `authentication.md`, `workflow.md`.
- Option 3 → Full-stack app. Ask Question 2, then Question 3. Read all references.
- Option 4 → App-as-authentication. Read `authentication.md`, `workflow.md`.
- Option 5 → Extension interfaces (private preview). Tell the user: “This is in private preview — check [/stripe-apps](https://docs.stripe.com/stripe-apps.md) for the latest access information. I can help you get started once access is confirmed.”
- Option 6 → Ask follow-up: “What problem are you trying to solve? For example: tracking sales, notifying customers, connecting a third-party tool?”

### Question 2 — Where do you want your app to appear? (only if UI)

```
Where in the Stripe Dashboard should your app show up?

1. Next to a specific customer, payment, invoice, subscription, or product
2. Everywhere in the Dashboard as a floating side panel
3. As its own full-screen page
4. In the settings area of my app (after install)
5. As a setup guide when someone installs my app
6. I'm not sure
```

**Viewport routing:**

| Answer | Viewport(s) |
| --- | --- |
| Next to a customer | `stripe.dashboard.customer.detail` |
| Next to a payment | `stripe.dashboard.payment.detail` |
| Next to an invoice | `stripe.dashboard.invoice.detail` |
| Next to a subscription | `stripe.dashboard.subscription.detail` |
| Next to a product | `stripe.dashboard.product.detail` |
| On any list page | `stripe.dashboard.customer.list`, `.payment.list`, etc. |
| Everywhere (side panel) | `stripe.dashboard.drawer.default` |
| Full-screen page | Full-page app — `stripe.dashboard.fullpage` |
| Dashboard homepage | `stripe.dashboard.home.overview` |
| Settings | `settings` viewport |
| Setup guide (first run) | `onboarding` viewport |

If the answer is “full-screen page”, read `ui-extensions.md` (full-page apps section). If the answer is “setup guide”, also read `onboarding-ux.md`. If “I’m not sure”, ask: “When someone opens Stripe and looks at a customer’s page — would your app show up there? Or would it be more like its own separate page?”

### Question 3 — Who is this for?

```
Who will use this app?

1. Just me / my own Stripe account (private app)
2. Other Stripe users — I want to publish it to the marketplace
```

**Routing:**

- Option 1 → Private app. Simpler workflow — no marketplace submission needed.
- Option 2 → Public app. Will need account activation (verified email and business details). Note this in the plan.

### Question 3b — Authentication type (only for public apps that need backend access)

If the user chose public/marketplace AND their app needs to access merchant data from a backend, determine the authentication type. Read `authentication.md` for the full comparison — restricted API keys are the recommended default unless the app specifically needs Connect-style access or OAuth.

For private apps or frontend-only apps, skip this question — restricted API keys or platform keys both work, and RAKs are simpler.

### Question 4 — Will your app need to remember things or talk to other services?

```
Will your app need to:

1. Remember settings or store information (for example: a user's login for another service,
   preferences, or data not already in Stripe)
2. Talk to another service (for example: send emails, update a spreadsheet, call a third-party API)
3. No — it will only show Stripe data
```

**Routing:**

- Option 1 or 2 → Needs backend or Secret Store API. Read `backend.md`.
  - If storing credentials/tokens → use the Secret Store API (plain-language: “Stripe has a built-in secure place to store passwords and tokens — you don’t need to build your own database for secrets”)
  - If running server-side logic → needs a self-hosted backend
- Option 3 → Frontend-only. Only the SDK’s Stripe client and `@stripe/ui-extension-sdk/ui` needed. No backend.

### After the interview — show a summary

Before writing any code, confirm your understanding with the user:

```
Here's what I understood:

- You want to: [plain-language description of the goal]
- Your app will appear: [where, or "on a backend server"]
- It's for: [just you / other Stripe users]
- It needs to: [remember things / talk to [service] / just show Stripe data]

Does that sound right? I'll start building once you confirm.
```

Only proceed after the user confirms. If they correct anything, update your understanding and show the summary again.

### Private preview feature detection

Some Stripe Apps features are in **private preview** — they require the user to be gated in before they can use them. Detect these during or after the interview:

**Private preview features:**

| Feature | Trigger phrases (user might say) | What to tell the user |
| --- | --- | --- |
| Custom objects | “store custom data in Stripe”, “create my own data model”, “custom database in Stripe”, “custom fields on customers”, “structured data that isn’t in Stripe already” | “Custom objects let you define your own data types in Stripe, but this feature is currently in private preview. You’ll need to have access enabled on your account before we can use it. Can you confirm you’re gated in for custom objects?” |
| Extension interfaces | “change how Stripe calculates”, “custom billing logic”, “modify payment routing”, “override Stripe’s default behavior”, “custom tax calculation” | “Extension interfaces let your app hook into Stripe’s processing pipeline, but this is in private preview. Can you confirm you have access to extension interfaces on your account?” |
| Full-page apps | “full-screen page in Stripe”, “my own page in the Dashboard”, “not a side panel — a full page”, “standalone page inside Stripe” | “Full-page apps (using the `stripe.dashboard.fullpage` viewport) are in private preview. Can you confirm you have access to full-page apps on your account?” |

**When to check:**

- If the user picks Option 5 in Question 1 → extension interfaces (already handled)
- If the user’s description of what their app does (Question 1 or free-form description) implies custom objects or extension interfaces → ask before proceeding
- If the user mentions “custom objects” or “extension interfaces” by name at ANY point → confirm access

**How to proceed after confirmation:**

- User confirms access → continue building with that feature
- User says they don’t have access → suggest alternatives:
  - Instead of custom objects → use Secret Store API for key-value data, or store data in their own backend
  - Instead of extension interfaces → suggest a webhook-based approach that reacts to events rather than intercepting processing
- User is unsure → tell them: “You can check your access at the Stripe Apps page in your Dashboard, or ask your Stripe account representative. I can help you build with an alternative approach in the meantime.”

## Plain-language glossary

Use these explanations when you need to introduce technical terms after routing:

| Term | Plain-language explanation |
| --- | --- |
| UI extension | The part of your app that shows up inside the Stripe Dashboard |
| Viewport | Which specific Dashboard page your app appears on |
| Extension interface | A hook that lets your app change how Stripe processes billing or payments |
| Platform keys | How your app accesses merchant data when they install it — no manual key-sharing needed |
| Connected account | A merchant who has installed your app |
| Permissions | What Stripe data your app is allowed to read or write; must be declared before use |
| Secret Store | Stripe’s built-in way for your app to save sensitive information like passwords or tokens |
| stripe-app.yaml | The configuration file that tells Stripe what your app is called, what it needs access to, and where it appears |
| Custom objects | Custom data types you define and store inside Stripe (in private preview — requires access) |
| Sandbox | An isolated Stripe test environment for safe testing — useful for testing destructive operations or onboarding flows |
