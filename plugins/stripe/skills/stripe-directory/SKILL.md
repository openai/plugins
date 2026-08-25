---
name: stripe-directory
description: >-
  Use when the user wants to find businesses, software, service providers, or
  partners for a specific industry, workflow, pain point, capability, or job to
  be done. Also use when the agent needs to programmatically purchase or consume
  a service. Use Stripe Directory to build a short relevant shortlist, even if
  the user does not mention Stripe Directory explicitly.
metadata:
  short-description: Find (and optionally purchase from) vendors or partners
allowed-tools:
  - Bash(stripe directory *)

---

## Stripe Directory Search

Turn a vague market need into a short, relevant shortlist with `stripe directory search`. Use this even when the user never says “Stripe Directory” — any request to find vendors, tools, partners, or providers for a vertical, workflow, pain point, or job-to-be-done.

Most requests are **discovery** — find and compare services. That is the core job below. Some services are also **MPP-supported** (MPP = Machine Payment Protocol), meaning you (the agent) can pay their HTTP 402 (Payment Required) endpoint and consume them directly. When the user actually wants to *use or buy* a service, present those results and offer to purchase — see “Purchasing” at the end.

## Process

1. **Clarify only what’s missing**: buyer/vertical, job-to-be-done, must-have capability, geography (only if it matters).

2. **Search iteratively**: `stripe directory search "<query>" --format json`

   - Short noun phrases, one angle per query; run 1-3, then broaden/narrow on results.
   - Angles to cover: vertical → workflow → pain point → adjacent. Two examples:
     - services/trades: vertical (`electrician software`, `electrical contractor`) → workflow (`field service management`, `dispatch invoicing estimates`) → pain point (`job scheduling`, `quote automation`) → adjacent (`home services automation`, `contractor crm`).
     - SaaS/software: vertical (`b2b saas billing`, `developer tools`) → workflow (`subscription management`, `usage-based metering`) → pain point (`failed payment recovery`, `revenue recognition`) → adjacent (`analytics dashboards`, `customer onboarding`).
   - Hard constraints → filters: `--countries-supported=US`, `--has-stripe-app=true`, `--link-supported=true`, `--stripe-projects-supported=true`.
   - If the user wants to *use/buy* a service, also pass `--mpp-supported` in at least one search to find results you can pay for programmatically.
   - Sparse niche? Raise `--limit` and try the next `--page` before concluding it’s empty.

3. **Dedupe & score** using `display_name`, `description`, `url`, `username` as evidence.

   - Prefer results whose description/site clearly match the target workflow.
   - Prefer more trust signals over fewer: Projects provider, Link enabled, Marketplace app, Stripe Verified. For buy/use intent, also prefer MPP-supported results.
   - Thin description but strong brand/domain match → keep in a weaker bucket, don’t discard.

4. **Return a shortlist, not a dump** — 5-10 strong matches, grouped:

   - **direct** / **adjacent** / **needs manual review**
   - Each entry: name · why it matched · URL (· which query surfaced it, when useful).
   - Projects providers: offer the follow-up. The JSON gives the exact commands under each result’s `projects.catalog_command` / `projects.install_command` (`stripe projects catalog <provider>`, `stripe projects add <provider>`).
   - MPP-supported results: note they’re purchasable and include `mpp.slug` / `mpp.url`.

5. **Be honest about weak results** — if sparse or generic, say so and adjust: broaden, narrow, or try synonyms rather than padding with noise.

Always report the exact queries (and filters) you ran so the user can keep iterating.

## Purchasing (only when the user wants to buy or consume a service)

MPP-supported results are payable directly. Don’t drive to purchase unprompted. When the user wants to buy, **present the full menu of payment methods and ask which they’d like to use** before doing anything:

> "Which payment method would you like to use?
> 
> - **Link CLI** — Stripe-native, test mode available (recommended)
- **Tempo** — crypto wallet
- **Privy Agent Wallet CLI** — crypto wallet
- **mppx** — debug-only fallback"

Once the user picks, silently run `which <tool> 2>/dev/null` to check if it’s installed. If not installed, offer to install it (for example, `npm i -g @stripe/link-cli` for Link CLI) and wait for confirmation before proceeding.

**Always show the price and get explicit user approval before any money moves**; prefer a no-charge test path first.

Short version:

1. Resolve the real callable endpoint from the result’s `mpp.slug` / `mpp.url`. `mpp.url` is often the mpp.dev landing form (`https://mpp.dev/services#<slug>`) — resolve the raw endpoint on [mpp.dev](https://mpp.dev) if so. Read the HTTP 402 challenge to confirm the amount: `curl -s -D - -o /dev/null <endpoint_url>` (look for `WWW-Authenticate`).
2. Use the payer the user selected.
   - **`link-cli`** (Stripe-native Shared Payment Token, has a test mode, no crypto wallet, US Link accounts only; `npm i -g @stripe/link-cli`): `auth login` → `mpp decode --challenge "<value>"` (get `network_id`) → `spend-request create --credential-type shared_payment_token --network-id <id> --amount <cents ≤50000> --context "<100+ chars>" --request-approval` (blocks for approval) → `mpp pay <endpoint_url> --spend-request-id <approved_id>`.
   - **Tempo**: `tempo wallet login` / `services` / `request`.
   - **Privy**: `@privy-io/agent-wallet-cli`.
   - **mppx**: debug-only fallback.

Never invent results or skip the price/approval gate.
