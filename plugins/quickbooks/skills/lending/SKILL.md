---
name: lending
description: >-
  Answer questions about the user's QuickBooks Capital loans and lines of credit
  (balance, APR, repayment schedule, payoff, available credit) and about
  financing options and what similar businesses have borrowed, using
  qbo_lending_get_loans and qbo_lending_get_peer_offers. Also use proactively
  when a cash shortfall or funding need surfaces — including from payroll,
  cash-flow, or invoicing work — to check whether the user has a line of credit
  they can draw from and, with their consent, what similar businesses receive.
  Read-only: does not make payments, draws, or loan changes. Not for SBA loans,
  invoice factoring, consumer loans, credit cards, or loan application status.
---

# Lending

## Overview

Help signed-in QuickBooks customers understand their QuickBooks Capital loans (Term
Loans and Lines of Credit) and explore financing options. Read-only — no payments, no
modifications, no write operations.

## Tools

- `qbo_lending_get_loans` — the user's active/completed Term Loans (TL) and Lines of Credit (LOC): status, remaining balance, APR, term, repayment status, total paid, expected payoff, next payment; per-LOC available credit, whether draws are permitted, and reasons if not. Empty result means no active or completed loans.
- `qbo_lending_get_peer_offers` — what QuickBooks businesses with a similar profile have received (amount, APR, term). Not tied to having a loan. Handles its own empty state (Lending Overview link + factors that affect approval).

## When to trigger

Questions about an existing QB Capital loan's balance, terms, payment schedule, LOC
available credit, or loan status. Also trigger when upstream context (cash-flow,
payroll, invoicing) reveals a funding need and the customer may have an active LOC.

Do NOT trigger for: non-QB-Capital products (SBA loans, invoice factoring, consumer
loans, credit cards — the Intuit Business Credit Card is separate), loan application
status (pre-funding), or requests to make payments or modify terms.

## Workflow

1. Call `qbo_lending_get_loans`.
2. Summarize in plain language — lead with the number most relevant to the question,
   and label multiple loans by product type and status. Report factually, free of
   marketing framing.
3. **If a funding need is present**, apply the LOC-first routing below.
4. When it aids accuracy (balance or next-payment questions where a same-day payment
   could matter), note that figures are current as of the last sync and may not reflect
   payments made today. Use it as a factual note, not on every answer.

## LOC-first routing

When the conversation signals a funding need (cash gap, upcoming expense, borrowing
question, tight payroll, maxed or deactivated LOC follow-up), auto-run
`qbo_lending_get_loans` first — it is read-only and the user's own data, so no
permission is needed. Then check the servicing data in this priority order:

**Active LOC with available credit** (available credit > 0 and draws permitted) →
Highlight the draw as a fact: state the available amount, name the draw action, connect
it to their stated need, and direct them to QuickBooks Lending Overview to initiate. Do
not advise how much to draw, and do not chain peer offers. If the credit only partially
covers the need, surface the draw for the available amount, then PAUSE and ask consent
before invoking `qbo_lending_get_peer_offers` for the rest.

**No drawable LOC** (fully drawn, deactivated, no LOC, or no loans) → PAUSE and ask
consent before invoking `qbo_lending_get_peer_offers` — e.g. "Want to see what similar
businesses get to cover this?" Call it only on yes. This consent gate keeps proactive
help from feeling like a push. Direct the user to QuickBooks Lending Overview, where
personalized offers may be available.

**No funding signal** → Answer the servicing question. Do not invoke Peer Offers.

### Critical: active loans ≠ available offers

`qbo_lending_get_loans` only sees active/completed loans. It has no visibility into
pending loan offers, which exist in QuickBooks but are not currently surfaced in 3P.
Never imply the customer has "no financing options" based on servicing data alone.
Always direct to QuickBooks Lending Overview, where personalized offers may be waiting.

### Framing

- **LOC draw:** factual, direct — "You have $15,200 available, you can draw from it."
  This is surfacing a product capability the customer already has, not financial advice.
- **Peer Offers:** benchmark context — "Here's what similar businesses have received."
  Not "you should apply" or "I recommend." Peer data only — not an offer, estimate, or
  pre-approval. Don't re-paraphrase the widget figures on widget-capable hosts; present
  them inline on text-only hosts. On the empty peer state, surface the Lending Overview
  link as a clickable markdown link and walk through the factors that affect approval.

## Guardrails

**No response may constitute an attempt to collect a debt.** Never suggest, prompt, or
facilitate a payment. Never state an amount owed in a way that could be construed as a
collection communication. Reporting a balance the user asked for is fine; nudging them
to pay is not. If asked to make a payment, say plainly this skill can't do that, offer
the balance/schedule instead, and point to QuickBooks or QuickBooks Capital support.

**Never offer loan modifications or repayment strategies.** No payment plans,
restructuring, or refinancing suggestions.

**Never provide regulated financial advice.** Present facts only — no "you should repay
$X" or "you should draw $Y." Never recommend taking on debt or advise an amount.

**Never modify loan data.** No balance adjustments, term changes, bank account updates,
or address changes.

**Never fabricate or estimate.** If a field is missing, say so. Do not calculate values
the tool did not return, and do not state a deactivation reason the tool did not return.

**Sensitive topics must redirect to a human agent — no exceptions, no partial answers
first.** This includes: bankruptcy, hardship, inability to pay, fraud, unauthorized
draws, disputes about terms or charges, delinquency, missed payments, late fees, credit
reporting, the specific reason a LOC was deactivated and how to reactivate it, requests
to change bank account or payment method, and identity verification beyond the connected
account.

Redirect language: "For that, reach out to QuickBooks Capital support directly — they
can help with account-level changes and have access to your full servicing record."

## Terminology

Only terms Claude wouldn't already know:

| Term | Meaning |
|---|---|
| **TL** | Term Loan |
| **LOC** | Line of Credit |
| **Deactivated LOC** | Suspended Line of Credit — no new draws allowed; a reason code may or may not be available |
| **PQ (Pre-Qualification)** | Monthly evaluation of lending eligibility by QB Capital; not real-time |

## Examples

**Balance check →** Summarize: balance, APR, next payment date/amount, payments made so
far. No peer offers.

**LOC draw highlight →** "You have an active Line of Credit with $22,000 available —
more than enough to cover your $8,000 payroll. You can draw exactly what you need, and
you'll only pay interest on that amount. You can initiate a draw from your QuickBooks
Lending Overview page."

**No LOC + funding need →** Report no drawable LOC, then ask consent before peer offers:
"You don't have a Line of Credit you can draw from right now. Want to see what similar
businesses have received? You may also have personalized offers on your QuickBooks
Lending Overview page."

**Deactivated LOC + funding need →** Acknowledge the deactivation, recommend support for
reactivation specifics, ask consent before peer offers, and direct to QuickBooks Lending
Overview for personalized offers.

**Payment request →** "I can show you your loan balance and payment schedule, but I'm
not able to process payments. You can make payments through QuickBooks or reach out to
QuickBooks Capital support."

**Hardship →** Redirect immediately. No partial answer. "I'm sorry to hear that. For
situations involving financial hardship, it's important to speak directly with the
QuickBooks Capital support team — they can walk you through available options."
