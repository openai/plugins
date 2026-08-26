---
name: email-to-estimate-invoice
description: Turn a customer email thread into a ready-to-send QuickBooks estimate or invoice. Use when the user asks to "create an invoice from my email thread", "draft an estimate based on what I quoted this customer over email", "bill this customer for the work we discussed and send it to them", "turn this email into an invoice", "make an estimate from this thread", or wants to go from an email conversation to a QuickBooks sales document without re-keying line items.
---

# Email to Estimate or Invoice

## Goal
Turn a customer email thread into a clean, accurate QuickBooks estimate or invoice by reading the thread through the user's installed email connector, extracting scope/quantities/pricing, resolving the customer and products in QuickBooks, drafting the document, and sending only after explicit user approval.

## Default assumptions
- Treat "my customer", "this client", and "them" as the counterparty named or implied in the email thread.
- Before reading anything, **see if the user has an email connector available to read emails (like Gmail or Outlook)**. Use whichever connector is installed - native Gmail, Outlook, Microsoft 365, IMAP, or a third-party connector such as Pipedream-hosted Gmail. Never hardcode a single provider, never require Gmail specifically, and phrase actions to the user as "read the email thread" or "use your email connector".
- If the user names a customer or thread subject, use that to locate the right conversation.
- Default to **invoice** when the user says "bill", "charge", or "invoice"; default to **estimate** when they say "quote", "proposal", or "estimate".
- If estimate vs invoice is ambiguous, ask once before creating the document.
- Use the connected QuickBooks company currency unless the email specifies otherwise.
- Do not invent line-item amounts, quantities, or prices that are not supported by the email content. Ask the user to fill gaps.

## Required tool sequence

### Phase 1 - Read and extract (email connector)
1. **See if the user has an email connector available** to read emails (like Gmail or Outlook). Look across the available tools for any email-reading capability - native Gmail, Outlook, Microsoft 365 / Office 365, IMAP, a Pipedream-hosted Gmail / Outlook MCP, or any other connector that can list or read email threads. Use whichever one is available; do not assume a specific provider.
2. **If you cannot find a suitable email connector**, do this in order before giving up:
   a. Tell the user no email connector is currently connected and that you need one to read the thread automatically.
   b. Ask the user what email product they use (Gmail, Outlook / Microsoft 365, Apple Mail / iCloud, Yahoo, or other) and **whether they'd like to set up that email connector now**.
   c. If the user wants to set one up, help them establish it: search the available connectors and marketplace for a matching one, surface concrete candidates by name, and walk through the install / authorization steps (for example installing the native Gmail or Outlook connector, or - if the native one is unavailable - adding a Pipedream-hosted Gmail MCP as a custom connector). After they confirm setup is complete, restart the flow from step 1.
   d. As a fallback, offer to let them paste or attach the email thread instead. Do not invent thread content.
3. Once a connector is available, read the relevant email thread through it.
4. Extract and normalize:
   - Counterparty name and email address
   - Scope of work or project description
   - Line items: description, quantity, **unit price**, and extended amount (for display only)
   - Subtotal, tax, discount, and total if present
   - Currency, transaction date, due date, payment terms (e.g. Net 30), or quote expiry if mentioned
   - Keep **unit price** and **extended amount** separate. Extended = unit price × quantity. Never collapse them into one number.
5. If the thread cannot be located, ask the user to paste the thread content or identify the correct conversation. Do not proceed with invented data.

### Phase 2 - Resolve customer (QuickBooks app tools)
6. Call `qbo_contact_search_customer` with the counterparty name and email when available.
7. If `requires_clarification=true`, present candidates and ask the user to pick before continuing.
8. If no customer is found, summarize the customer you will create (display name, email) and ask for confirmation before calling `qbo_contact_create_customer`.

### Phase 3 - Resolve products (QuickBooks app tools)
9. For each distinct line-item description, call `qbo_catalog_search_products` with up to 20 descriptions in one call when possible.
10. If any item has `requires_clarification=true`, ask the user to pick the correct product before continuing.
11. If any item has `found=false`, **STOP** before calling `qbo_catalog_create_product`. Show the user the exact product you propose to create (name, type, unit price) and **wait for an explicit "yes" / "create it" / "go ahead" from the user**. Do not treat the original request (for example "invoice X for $20 for coffee") as implicit consent to create a new product. Ask for unit price if it was not supplied. **Do not set `taxable` unless the user (or email thread) explicitly stated taxability** — omit the field so `qbo_catalog_create_product` falls back to the QuickBooks company default. Only after the user confirms may you call `qbo_catalog_create_product`.

### Phase 4 - Draft document (QuickBooks app tools)
12. Decide document type:
    - Estimate: quote/proposal/estimate language, no explicit billing request
    - Invoice: bill/invoice/charge/payment-due language
    - Ambiguous: ask the user
13. Create the draft **once**:
    - Estimate path: `qbo_sales_create_estimate`
    - Invoice path: `qbo_sales_create_invoice`
14. Pass resolved `customer_id`, product IDs, descriptions, quantities, and **unit rates** from prior tool results. Do not guess IDs.
15. **CRITICAL - `amount` means unit rate, not line total.** On `qbo_sales_create_invoice` / `qbo_sales_create_estimate`, each line's `amount` is the **unit price/rate**. QuickBooks computes line total as `amount × quantity`.
    - Example: 14.5 hours at $210/hr → `quantity: 14.5`, `amount: 210` (NOT `amount: 3045`).
    - NEVER put the extended/line total in `amount` when `quantity ≠ 1`. That double-counts and inflates the invoice (e.g. $4,631 becomes ~$45,738).
    - Credits/retainers: use a negative **unit** amount with `quantity: 1` (e.g. `amount: -500`).
16. **Required create arg shapes** (ChatGPT Apps / Codex Desktop are strict). Prefer this exact structure:
    ```json
    {
      "customer_data": { "customer_id": "<id>" },
      "line_items": {
        "line_items": [
          {
            "product_id": "<id>",
            "description": "<text>",
            "quantity": 14.5,
            "amount": 210,
            "taxable": false
          }
        ]
      },
      "invoice_reference_number": { "reference_number": "NS-STRAT-26" }
    }
    ```
    - `line_items` must be an **object** with nested `line_items` array (not a bare top-level array).
    - Each line must include `product_id`, `description`, `amount` (unit rate), `quantity`, and `taxable`.
    - `invoice_reference_number` must be an **object** `{ "reference_number": "..." }`, not a bare string.
    - Do **not** pass `payment_term` as the string `"Net 30"` or `{ "name": "Net 30" }`. Prefer omitting `payment_term` so the company default applies. If you must set terms, pass a term object that includes a real QuickBooks term `id` from a prior term lookup/create tool — never a bare name string.
    - Put customer memo/note on `customer_address_info.note_to_customer`, never under `payment_details`.
17. After create, compare the tool result total to the email/extracted total. If they differ materially, **do not create another invoice**. Explain the mismatch and ask the user whether to delete/recreate or update.

### Phase 5 - Confirm and send (QuickBooks app tools)
18. Present a draft preview to the user before any send action.
19. Only after explicit user approval:
    - Estimate path: `qbo_sales_send_estimate`
    - Invoice path: `qbo_sales_send_invoice`
20. For send calls, use the customer email from the thread or QuickBooks record when available. If no email is known, ask the user for the delivery address before sending.

## Safety rules
- **Never auto-send.** Always show the draft and get explicit approval before `qbo_sales_send_estimate` or `qbo_sales_send_invoice`.
- **Never auto-create** a customer or product. Always show the exact record you propose to create and wait for an explicit user "yes" / "create it" / "go ahead". The user's original request (e.g. "invoice X for $20 for coffee") is NOT implicit consent to create new customers or products - it only authorizes the invoice itself, conditional on the underlying records being approved.
- **Never invent** line items, prices, or totals not grounded in the email thread.
- **Never put extended/line totals in `amount`.** `amount` is always unit rate; line total = amount × quantity.
- **One successful create only.** Do not call create again to "fix" a bad draft. If the draft is wrong, tell the user and ask before delete + recreate, or use update with correct shapes.
- **On connector/schema validation errors** (`Parameters failed connector schema validation…`): fix the argument shape and retry **the same operation once**. Do not open a create → update → create loop. Do not create a second invoice because the first call failed validation.
- Reference QuickBooks tools by their registered names only. Do not redefine tool schemas or descriptions.
- If any tool returns an error or incomplete data, explain the gap and stop rather than fabricating a successful outcome.

## Output format
Use this structure unless the user asks for a different format:

```markdown
## Email-to-document summary
**Customer:** <name + email>
**Source:** <email thread subject or identifier>
**Document type:** <estimate or invoice>

### Extracted from email
| Line item | Qty | Unit price | Amount |
|---|---:|---:|---:|
| <description> | <qty> | <price> | <amount> |

**Subtotal / tax / total:** <amounts from email or draft>

### QuickBooks draft
**Status:** Draft created - not sent yet
**Reference:** <estimate or invoice number if returned>
**Total:** <draft total from tool result>
**Open in QuickBooks:** <link from tool result when available>

### Ready to send?
I've drafted this <estimate/invoice> for <customer>. Reply **yes** to send it to <email>, or tell me what to change first.
```

After a successful send, confirm with document number/reference and that the email was sent. Do not list full line-item tables in the final confirmation unless the user asks.

## Style requirements
- Lead with what you extracted and what you created, not the tool sequence.
- Use exact numbers from tool outputs when available.
- Keep language plain and business-owner friendly.
- When the email is informal or incomplete, say what you inferred and what you still need from the user.
- Do not provide tax, legal, or collections advice. Frame next steps as operational actions only.
