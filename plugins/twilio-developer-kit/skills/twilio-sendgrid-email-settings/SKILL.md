---
name: twilio-sendgrid-email-settings
description: >
  Configure SendGrid dynamic templates (Handlebars), tracking settings
  (opens, clicks, subscriptions), link branding for custom tracking
  domains, and content types (HTML, plain text, AMP). Use when customizing
  SendGrid email content, tracking behavior, or branded links. Requires a
  SendGrid API key (SG.-prefix) — not applicable to the Twilio Email API
  (comms.twilio.com).
---

## Overview

SendGrid email settings control how your messages are constructed, personalized, and tracked. Most configuration happens in the SendGrid Console, but templates and tracking can also be managed via API.

---

## Dynamic Templates

Templates use Handlebars syntax and are managed in Console > Email API > Dynamic Templates. Template IDs start with `d-`.

**Supported Handlebars helpers:**

| Helper | Use | Example |
|--------|-----|---------|
| `if` / `unless` | Conditional | `{{#if premium}}Welcome back!{{/if}}` |
| `each` | Iteration | `{{#each items}}{{this.name}}{{/each}}` |
| `equals` / `notEquals` | Comparison | `{{#equals status "active"}}...{{/equals}}` |
| `and` / `or` | Boolean logic | `{{#and premium verified}}...{{/and}}` |
| `greaterThan` / `lessThan` | Numeric | `{{#greaterThan count 5}}...{{/greaterThan}}` |
| `length` | Array/string | `{{length items}}` |
| `formatDate` | Date format | `{{formatDate date "MM/DD/YYYY"}}` |
| `insert` | Module insert | `{{insert "module_name"}}` |

**NOT supported:** Custom helpers, inline partials, `lookup`, `log`, `with`, `blockHelperMissing`. SendGrid implements a subset of Handlebars.js.

### Template Versions

- **Dynamic templates** (IDs starting with `d-`): Support Handlebars
- **Legacy transactional templates**: Use `-substitution-` syntax — not interchangeable with Handlebars

---

## Tracking Settings

| Setting | What it does | Caveat |
|---------|-------------|--------|
| **Open tracking** | Inserts a tracking pixel | Unreliable: Apple Mail Privacy Protection inflates opens; image-blocking clients produce false negatives |
| **Click tracking** | Rewrites URLs through SendGrid's redirect | Can trigger spam filters on some domains |
| **Subscription tracking** | Adds unsubscribe footer | Required for CAN-SPAM compliance |
| **Google Analytics** | Adds UTM parameters | Only for marketing campaigns |

Configure per-message or account-wide in Console > Settings > Tracking.

---

## Link Branding (Custom Tracking Domains)

By default, click-tracked links route through `url####.ct.sendgrid.net`. Link Branding lets you use your own domain (e.g., `links.yourdomain.com`) instead, which improves deliverability and builds trust.

**Setup:** Console > Settings > Sender Authentication > Link Branding

Requires a CNAME DNS record pointing your subdomain to `sendgrid.net`. Validate via API: `GET /v3/whitelabel/links/{id}/validate`

---

## Content Type Priority

When sending multiple content types, email clients display in this priority:

1. `text/x-amp-html` (AMP — only in supporting clients, requires sender registration)
2. `text/html` (standard — most clients)
3. `text/plain` (fallback)

Always include at least `text/plain` and `text/html`.

---

## CANNOT

- **Cannot use custom Handlebars helpers** — Only the built-in set listed above.
- **Cannot guarantee open tracking accuracy** — Pixel-based tracking is fundamentally unreliable. Do not use for business-critical logic.
- **Personalizations `subject` is a plain string override** — It bypasses the template subject. To use dynamic subjects, set Handlebars variables (e.g., `{{{subject}}}`) in the Dynamic Template's subject field and pass values via `dynamic_template_data`.
- **Undefined template variables are silent** — Missing keys in `dynamic_template_data` render as empty strings with no error.

---

## Next Steps

- **Send email:** `twilio-sendgrid-email-send`
- **Delivery tracking:** `twilio-sendgrid-webhooks`
- **Manage bounces/unsubscribes:** `twilio-sendgrid-suppressions`
