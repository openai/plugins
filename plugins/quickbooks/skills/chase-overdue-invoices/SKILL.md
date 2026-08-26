---
name: chase-overdue-invoices
description: Send payment reminders for invoices with tone matched to aging. ALWAYS use this skill when the user asks to "send a reminder", "send reminder to invoice", "remind about invoice", "send a reminder to invoice 1234", "remind them about 4574", "send a firmer reminder for invoice 1042", "who owes me money", "show me overdue invoices", "chase down overdue invoices", "follow up on unpaid invoices", or "nudge customers who haven't paid". This skill MUST be loaded before calling qbo_sales_send_invoice_reminder to ensure confirmation and tone-matching.
---

# Chase Overdue Invoices

## Goal
Help the user understand who owes money, prioritize the right invoices to chase, draft appropriately toned reminders for single-invoice follow-ups, and send payment reminders only after explicit user confirmation — with safe handling of held sends.

## When to use
- **Send a reminder for an invoice** — "send a reminder to invoice 1234", "send reminder for 4574", "remind about invoice 1042". This is the primary use case.
- **Who owes me?** — read-only A/R triage: "who owes me money?", "what's overdue?", "show me everything 60+ days past due".
- **Remind / nudge / chase / follow up** on unpaid invoices — single, by filter, or by customer.
- **Tone a single reminder** — "send a firmer reminder for 1042", "send a gentle nudge for 1003 and mention the late fee".

**IMPORTANT:** This skill MUST be loaded before any call to `qbo_sales_send_invoice_reminder`. Never call the reminder tool directly without loading this skill first.

## When NOT to use
- Sending a **fresh** invoice for the first time (that is the create/send-invoice flow, not a reminder).
- Creating, updating, searching, duplicating, or deleting invoices.
- Printing or downloading an invoice as a PDF.
- A create-invoice request like "create an invoice for Acme" must NOT pull A/R aging or trigger this skill.

## Default assumptions
- Treat "my business", "my company", and "our customers" as the connected QuickBooks company.
- A/R aging reports are accrual-basis unless the user explicitly asks for cash basis.
- "Overdue" means unpaid invoices in buckets past due: **Current**, **1–30**, **31–60**, **61–90**, **91+** days.
- Read-only questions ("who owes me?", "what's overdue?") must **not** send reminders unless the user explicitly asks to send.
- For bulk reminders (more than one invoice), use the QBO reminder template only. Custom subject/body is allowed for **exactly one** invoice at a time.
- Reference QuickBooks tools by their registered names only. Do not redefine tool schemas or descriptions.

## How to identify an invoice to the user (read this before talking about any invoice)
Each invoice has two identifiers. Keep them straight:

- **Invoice number** — the customer-facing document number the merchant sets and the customer recognizes (e.g. `4574`, `1042`, `INV-ACME-404`). It can be numeric or alphanumeric. In tool output this is the **`reference_number`** field. **This is the number you show the user and put in an email** — it is exactly how invoices are referenced across QuickBooks and other channels. Some accounts have long auto-generated numbers; that is still the customer-facing number, so show it as-is.
- **Invoice ID** — the long global identifier in the `id` field (e.g. `djQuMTo5MzQx…:593`). It is **plumbing for tool calls only**. Never show it to the user, never put it in an email.

Rules:
- **Display = `reference_number`, wrapped as a link.** When you name an invoice to the user, use its `reference_number` and **render it as a markdown link to the invoice using the invoice's `link` field**: `[4574](<link>)`. Use the `link` value exactly as the tool returned it — do not build or edit the URL yourself. If an invoice has no `link`, show the bare `reference_number`. When you write "invoice 4574", `4574` must be the `reference_number` from a tool result.
- **Tool calls = the `id` as returned.** When calling `qbo_sales_send_invoice_reminder` (or any tool that needs an invoice identity), pass the **full `id`** value exactly as a retrieval tool returned it. The user never sees this.
- **Never show the full global `id`** (e.g. `djQuMTo5MzQx…:593`) as the invoice number.
- **Never construct, guess, or modify any identifier.** Resolve the user's spoken number to a real invoice via a retrieval tool; copy `reference_number` for display and pass the full `id` for the send.
- On an ID-related tool failure, retry **once** silently before reporting a problem. Do not expose ID formats or internal errors to the user.
- Call the tools to get invoice facts (number, balance, due date, email, status). Do **not** answer from memory or infer these.

## Required tool sequence

### Phase 1 — Understand receivables (skip when user names specific invoices)
**If the user names one or more specific invoices** (e.g. "send a reminder for INV-HAR-001", "remind them about 4574 and 1043"), **skip the aging summary entirely** and go straight to `qbo_sales_get_invoices` with `doc_numbers` to resolve those invoices. The aging tools are for discovery ("who owes me?"), not for acting on invoices the user already identified.

For discovery requests ("who owes me?", "what's overdue?", "show me 60+ days"):
1. Call `qbo_accounting_get_ar_aging_summary_text` to get bucket totals and customer-level overdue exposure. (Use the `_text` variant so the skill can synthesize the briefing instead of returning an interactive widget.) For a top-level "who owes me?" answer, **this one call is usually enough** — answer from it and stop.
2. Pull `qbo_accounting_get_ar_aging_detail` **only when** the user asks about specific customers or buckets, or when you need per-invoice numbers/due dates to act on a filtered set. Scope it to the customer or bucket in question rather than pulling everything.

For direct invoice requests:
3. Use `qbo_sales_get_invoices` to resolve a **specific** invoice the user named — pass the invoice number(s) via `doc_numbers`. This is your starting point when the user already knows which invoice(s) to remind. Do not call aging tools first.

### Resolving which invoices to remind — three routes
Pick the route that matches the request, then group the resolved invoices by customer (one `qbo_sales_send_invoice_reminder` call per customer, with that customer's invoice IDs as a list):

- **By invoice** — the user names one or more invoices ("remind them about 4574", "send reminders for 4574 and 1043"). The number they type is the **invoice number** (`reference_number`) you showed them. Resolve it with `qbo_sales_get_invoices` using `doc_numbers=["4574"]`. Keep the resolved invoice's full `id` for the send and its `reference_number` for display.
- **By filter** — the user describes a set ("everything overdue", "all open invoices", "due this week", "anything 60+ days"). Pull the set from `qbo_accounting_get_ar_aging_detail` (or `qbo_sales_get_invoices`), filtering to unpaid (open balance > 0) and the requested aging window.
- **By customer** — the user names a customer ("follow up with Acme Corp"). Find that customer's unpaid invoices (A/R detail filtered to the customer, or `qbo_sales_get_invoices`), then group them into one reminder call.

### Phase 2 — Prioritize and summarize
4. Build a prioritized chase list:
   - Rank buckets by severity: **91+** > **61–90** > **31–60** > **1–30** > **Current** (for overdue focus, deprioritize Current unless user asks for all open A/R)
   - Within a bucket, rank by largest balance first
   - Roll up per-customer totals when one customer has multiple overdue invoices
   - When you list individual invoices, show each as its **linked invoice number** (`[4574](<link>)`). The `reference_number` and `link` both come from `qbo_sales_get_invoices` — the aging detail report alone does not provide the per-invoice link, so resolve the invoices you intend to list (in as few scoped calls as possible).
5. Lead with an actionable summary, not a raw report dump.

### Phase 3 — Refine the set across turns (multi-turn)
6. The user may adjust the set conversationally before confirming — "actually just the 90+ ones", "drop 1003", "add 1007 too", "only Acme", "skip anyone I reminded this week". **Re-resolve the set whenever it changes** and re-state the updated list. Never send on a stale set.
7. For a **single** invoice, the user may also refine the email wording — "make it friendlier", "mention the late fee", "change the subject". Capture their wording into `custom_subject` / `custom_message` and show the exact text in the confirmation so they approve it before it sends.

### Phase 4 — Draft/preview the reminder email (REQUIRED before any send)

**This phase is REQUIRED. You must show the user what email will be sent before asking for confirmation.**

**Single invoice — draft a tone-matched email:**
For exactly one invoice, **do NOT use the default template**. Instead, draft a custom `custom_subject` and `custom_message` based on the invoice's aging bucket using the **Tone mapping** table below. Include the invoice number, amount, and due date. Show the drafted subject and body in the confirmation so the user approves the exact wording before it sends.

**Bulk (2+ invoices) — MUST fetch and show the actual template:**
8. **ALWAYS call `qbo_sales_get_settings`** with `{domain: "reminder_template", action: "get_global"}` to fetch the merchant's configured reminder email. This call is MANDATORY before any bulk confirmation - do NOT skip it or show a placeholder template.
   - **If the fetch succeeds:** Show the ACTUAL template returned by the tool in the confirmation with a labeled `Subject:` line and `Body:` block. Use the exact text from the tool response. Leave `[Invoice No.]` as-is and note it is filled in automatically per invoice.
   - **If the fetch fails** (timeout, error, unavailable): Tell the user "I could not retrieve your reminder email template" and note that QuickBooks will use its configured default. Still show the full invoice list before asking for confirmation.
   - **Never show a generic/placeholder template** like "Reminder: invoice {{invoice_number}} is overdue". Always call the tool first to get the real template.

**Confirmation format (REQUIRED for all sends):**

For **single invoice**:
```
## Reminder plan
**Invoice:** [<reference_number>](<link>) for <customer> - <amount> (<X> days overdue)
**Tone:** <bucket tone from table, e.g. "Urgent (91+ days)">

**Email that will be sent:**
**Subject:** <your drafted subject using the tone>
**Body:**
<your drafted body using the tone - MUST match the urgency level for the aging bucket>

Reply **yes** to send this reminder, or tell me what to change.
```

For **bulk (2+ invoices)**:
```
## Reminder plan
**Invoices to remind:** <count>
**Customers:** <customer list with totals>

**Reminder email template:**
**Subject:** <template subject from qbo_sales_get_settings>
**Body:**
<template body - note that [Invoice No.] is filled per invoice>
[If fetch failed: "QuickBooks will use your configured reminder template."]

**Invoices:**
| Invoice | Customer | Amount | Days overdue |
|---------|----------|--------|--------------|
| ... | ... | ... | ... |

*Note: Bulk reminders use the standard QuickBooks template for all invoices regardless of aging. Do NOT show a per-invoice tone column here — the template is the same for every invoice in the batch, so a tone label is misleading. For tone-customized emails, send invoices individually.*

Reply **yes** to send these reminders, or tell me what to change.
```

Never proceed to send without showing this confirmation with the email content (or a note about the default template if fetch failed).

### Phase 5 — Send with confirmation
9. Only after explicit user approval, call `qbo_sales_send_invoice_reminder` with the confirmed `invoice_ids` (grouped per customer). Do **not** pre-screen which invoices are eligible — just send; the tool surfaces holds reactively (see Hold resolution).
10. For a single-invoice send with tone, include the approved `custom_message` and/or `custom_subject`. **Never** pass these when sending more than one invoice — the tool rejects custom text on bulk reminders.
11. Per-invoice results are **SENT** or **FAILED** only — there is no "skipped". Do not report a held invoice as sent.

### Large batches
For a very large set, do not try to confirm hundreds of invoices in one message. Confirm and send in reasonable groups (e.g. by customer or by aging bucket), re-confirming each group. If a batch exceeds today's send limit, the send is **held** as `MCP-0022` (a surfaced hold, not a silent skip) — tell the user some are beyond today's limit and re-call with `over_cap_confirmed=true` to send what fits; the rest can go tomorrow.

## Keep the flow efficient (minimize tool calls and latency)
Aim to answer in the fewest tool calls that are still correct. The user is waiting on every call.

- **Lead with the summary.** `qbo_accounting_get_ar_aging_summary_text` already rolls up totals and per-customer overdue exposure. For "who owes me?" / "what's overdue?", answer from that single call. Do not pull invoice-level detail you were not asked for.
- **Fetch in bulk, not per-invoice.** When you need invoice detail, get it in as few scoped calls as possible — filter by `customer_id`, an aging window, or pass multiple IDs (`invoice_ids`, or `doc_numbers`) in one call. Never loop calling `qbo_sales_get_invoices` once per invoice across a large set.
- **Don't hand-compute a report the tools already produce.** If the aging summary returns the buckets, use them. Reserve manual roll-ups for genuinely missing data, and even then cap the work (see fallback below).
- **Resolve once, reuse.** Once you've resolved the working set (numbers, IDs, balances), reuse it across confirmation turns; only re-fetch the parts that actually changed when the user refines the set.
- **Get the template once.** Fetch the reminder template (Phase 4) once per send confirmation and reuse it for every invoice in that batch — it is global, not per-invoice.
- **Stop and ask instead of grinding.** If a request would require sifting through a very large number of invoices (e.g. hundreds), do **not** silently page through them. Give the customer-level summary from the aging report and ask the user to narrow ("which customer or aging bucket?") before pulling detail.

### Fallback when the aging tools are unavailable
If `qbo_accounting_get_ar_aging_summary_text` / `qbo_accounting_get_ar_aging_detail` are not available in the current tool set, do **not** page through hundreds of invoices to rebuild the report by hand. Instead: make **one** scoped `qbo_sales_get_invoices` call (filtered to a sensible recent window and/or a customer), present the customer-level overdue picture you can derive from it, and tell the user you can drill into a specific customer or bucket. Ask them to narrow rather than fetching the entire ledger.

## Tone mapping (CRITICAL - determines email wording)

Every invoice falls into an aging bucket that determines its tone. This applies to:
- **Single invoice sends**: You MUST draft a custom subject/body using the exact tone for that bucket
- **Bulk sends**: Group invoices by bucket in the confirmation table so the user sees each tone category

| Aging bucket | Tone label | Subject example | Body opening example |
|---|---|---|---|
| 1-30 days | Gentle | "Friendly reminder: Invoice [#] payment due" | "Hi [Customer], just a friendly reminder that invoice [#] for [amount] was due on [date]..." |
| 31-60 days | Standard | "Payment reminder: Invoice [#] is overdue" | "This is a reminder that invoice [#] for [amount] is now [X] days past due..." |
| 61-90 days | Firm | "Action required: Invoice [#] is significantly overdue" | "Invoice [#] for [amount] is now significantly overdue. Please remit payment immediately..." |
| 91+ days | **Urgent** | "**Urgent: Immediate attention required - Invoice [#]**" | "**This matter requires your immediate attention.** Invoice [#] for [amount] is now [X] days past due. Please contact us immediately to resolve this outstanding balance..." |

**Single invoice - MUST draft tone-matched email:**
- Calculate days overdue from due date
- Look up the bucket in the table above
- Draft `custom_subject` and `custom_message` using that bucket's tone - NOT the default template
- For 91+ days: the email MUST convey urgency (use words like "immediate attention", "urgent", "significantly past due")
- Show the drafted email in confirmation BEFORE sending

**Bulk sends - group by tone in confirmation:**
- All bulk reminders use the same QBO template (custom text is not allowed for bulk)
- BUT the confirmation table MUST group invoices by aging bucket so the user sees which tones apply
- Add a "Tone" column showing: Gentle (1-30), Standard (31-60), Firm (61-90), or **Urgent** (91+)

Match the user's requested tone ("firmer", "gentler") within the bucket baseline. Always include the invoice number (`reference_number`), amount, and due date in the drafted body.

## Hold resolution (MCP-0020 through MCP-0023)

`qbo_sales_send_invoice_reminder` may return a **hold** (`status: "error"`, nothing sent). These are surfaced **reactively** by the send — do not anticipate or pre-check them. Do not report held invoices as sent.

| Code | Meaning | What to tell the user | Resolution (re-call) |
|---|---|---|---|
| MCP-0020 | Pending bank-payment match | "Invoice #X may already be paid — there's a pending bank match." **Never say it IS paid.** | `pending_match_confirmed=true` **sends those invoices anyway** (they are eligible) |
| MCP-0021 | Invoice appears already paid | "Invoice #X appears already paid. Send the reminder anyway?" | `already_paid_confirmed=true` **drops** the held invoices and sends the rest |
| MCP-0023 | No email on file | "Invoice #X has no email on file. Give me an address and I'll send it, or I can skip it." | `emails={invoice_id: address}` **sends** it, OR `no_email_acknowledged=true` **drops** it |
| MCP-0022 | Over today's send limit | "Some invoices are beyond today's send limit. I can send the rest now; the others can go tomorrow." Do not recite a raw cap number. | `over_cap_confirmed=true` sends what fits now |

When multiple holds trip together, the response returns the highest-priority code in `error.code` and a `meta.gated` object listing every tripped group (each self-describes its confirm flag). Show the user all groups and confirm everything they approve in **one** re-call by setting each approved group's confirm flag.

## Safety rules
- **Never auto-send** reminders. Always send a confirmation and wait for an explicit "yes" — on every turn, on the final set and final text. A confirmation from an earlier turn does not carry over to a changed set.
- **Always show invoice details before asking for confirmation.** The confirmation must include the count of invoices, list of customers, invoice numbers, and amounts. Never ask "Reply yes" without first showing what will be sent.
- **Always attempt to show the email template.** Call `qbo_sales_get_settings` `{domain: "reminder_template", action: "get_global"}` before every bulk send. If it returns a template, the confirmation MUST include that `Subject:` + `Body:`. If the fetch fails (timeout, error, unavailable), still show the full invoice list and tell the user QuickBooks will use its default reminder template — then ask for confirmation.
- **Do not pre-screen** eligibility before sending. Just call the send; holds are surfaced reactively.
- **Never say an invoice IS paid** when MCP-0020 fires. Say it **may** already be paid due to a pending bank match.
- **Tone edits change wording only — never facts.** A custom subject/body may change tone or phrasing, but must never misstate the invoice's amount, balance, line items, due date, invoice number, or terms. Refuse such an edit (e.g. "tell them they owe $2,000" when they don't) and keep the correct facts or the original body. Never originate a tone variant the user did not ask for.
- **Single-invoice reminders use tone-drafted text.** For exactly one invoice, ALWAYS draft a custom subject/body using the Tone mapping table - do NOT use the default template.
- **Bulk reminders use the template only.** Never pass `custom_message` / `custom_subject` when sending more than one invoice.
- Read-only prompts must not trigger send tools unless the user explicitly asks to send.
- Do not provide legal or collections advice. Frame actions as operational follow-up only.

## Output format

### Read-only summary (no send requested)

```markdown
## Who owes you money
**Company:** <connected company>
**As of:** <as-of date from aging report>

### Priority chase list
| Customer | Invoice # | Amount | Days overdue | Tone |
|---|---|---:|---:|---|
| <customer display name> | [<invoice number, e.g. 4574>](<invoice link>) | <amount> | <days> | <Urgent/Firm/Standard/Gentle> |

**Total overdue:** <amount>
**Top priority:** <1-2 sentence recommendation>
```

The **Invoice #** column is always the invoice's customer-facing **`reference_number`** (e.g. `4574`) rendered as a markdown link to the invoice's `link` — never the global `id`. Drop the link only when an invoice has no `link` field. The **Tone** column shows: Urgent (91+), Firm (61-90), Standard (31-60), or Gentle (1-30 days).

### Before sending (confirmation gate) - MUST include email preview AND tone

**Single invoice confirmation:**
```markdown
## Reminder plan
**Invoice:** [<reference_number>](<link>) for <customer> - <amount> (<X> days overdue)
**Tone:** <Gentle/Standard/Firm/Urgent> (<aging bucket>)

**Email that will be sent:**
**Subject:** <drafted subject matching the tone>
**Body:**
<drafted body matching the tone - for 91+ days, MUST convey urgency>

Reply **yes** to send, or tell me what to change.
```

**Bulk confirmation:**
```markdown
## Reminder plan
**Invoices to remind:** <count>
**Customers:** <list with totals>

**Reminder email template:**
**Subject:** <template subject from qbo_sales_get_settings>
**Body:**
<template body - [Invoice No.] filled per invoice>
<If fetch failed: "QuickBooks will use your configured reminder template.">

**Invoices:**
| Invoice | Customer | Amount | Days overdue |
|---------|----------|--------|--------------|
| [#](<link>) | <name> | <amt> | <days> |

*Bulk reminders use the standard QuickBooks template for all invoices regardless of aging. For tone-customized emails, send individually.*

Reply **yes** to send, or tell me what to change.
```

**The email preview is REQUIRED.** For bulk sends, always call `qbo_sales_get_settings` first and show the result. Do NOT include a per-invoice Tone column on bulk confirmations — the template is the same for every invoice in the batch, so a per-invoice tone label is misleading. For single invoice, show the tone-drafted subject/body matching the aging bucket's urgency level.

### After send

```markdown
## Reminders sent
**Sent:** <count>
**Failed / held:** <count if any>

<If holds remain, list them with next-step options. Do not claim held invoices were sent.>
```

After sending, confirm which invoices went to which customers and stop. Do not pre-emptively offer to send more reminders or chain into other invoice actions.

## Style requirements
- Lead with who to chase first and why, not the report mechanics.
- **Always identify an invoice by its customer-facing number (`reference_number`, e.g. "invoice 4574") and the customer's display name, and link the number to the invoice** using its `link` field (`[4574](<link>)`). Never show the full global `id` (e.g. `djQuMTo…:593`) as the invoice number.
- Use exact amounts and invoice numbers from tool outputs.
- Round large dollar values for readability; preserve precision on individual invoice balances.
- For bulk sends, keep confirmation concise — list invoice numbers (`reference_number`) and customer names, not full email bodies.
- Tie every recommendation to concrete A/R data from the aging tools.
