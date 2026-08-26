---
name: stripe-docs
description: >-
  Use when the user or agent needs to read, search, or look up Stripe
  documentation or API reference. Prefer this over curl or WebFetch for any
  docs.stripe.com content.
metadata:
  short-description: Read and search Stripe documentation from the terminal
allowed-tools:
  - Bash(stripe docs *)

---

Use `stripe docs` instead of fetching [docs.stripe.com](https://docs.stripe.com/.md) content directly with `curl` or `WebFetch`.

- Fetches Markdown automatically
- Purpose-built for agents and terminal workflows

## Read a page by its web path

```bash
stripe docs /payments
```

## Search documentation by keyword

```bash
stripe docs search "payment intents"
```

## Look up API reference

```bash
# By resource name
stripe docs api product

# By HTTP method and path
stripe docs api GET /v1/products

# By event type
stripe docs api product.created
```
