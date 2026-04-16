---
name: transaction-cleanup
description: |-
  Complete missing items on your transactions using Ramp MCP tools — memos, accounting categories,
  funds, trips, attendees, and missing receipts. Use when: 'add memo', 'categorize transactions',
  'missing items', 'transaction cleanup', 'fix my transactions', 'set tracking category',
  'assign to fund', 'bulk memo update', 'get memo suggestions', 'which transactions are missing
  receipts/memos/accounting', or similar transaction-maintenance requests. Do NOT use for
  receipt image uploads (use receipt-compliance) or approvals/rejections (use approval-dashboard).
---

## Non-Negotiables

- Scope to the user's own transactions by default using `ramp_get_user_transactions` with `transactions_to_retrieve: "my_transactions"`.
- Show the transaction details before editing. Never blind-edit.
- For bulk edits, present the plan and confirm before executing.
- Include `user_submitted_fields` when calling `ramp_edit_transaction` to distinguish user-provided vs agent-inferred edits.
- All MCP tool calls must include a `rationale`.
- Prefer the MCP transaction tools over generic SQL/database tools for user-facing cleanup tasks.

## Workflow

### Step 1: Find transactions needing attention

List the user's recent transactions. Default to the last 30 days if the user doesn't specify a date range.

```json
{
  "tool": "ramp_get_user_transactions",
  "args": {
    "transactions_to_retrieve": "my_transactions",
    "from_date": "2026-03-15",
    "page_size": 50,
    "include_count": true,
    "rationale": "Retrieve the current user's recent cleared transactions so I can identify missing items and show the transaction details before making any edits."
  }
}
```

**Response shape:**
```json
{
  "transactions": [
    {
      "transaction_uuid": "ab512db5-...",
      "spent_by_user": "Jane Smith",
      "amount": "$36.87",
      "transaction_time": "2026-02-07T00:51:33+00:00",
      "merchant_name": "Uber",
      "merchant_category": "Taxi and Rideshare",
      "reason_or_justification": "Team transportation",
      "spend_allocation_name": "Marketing Budget",
      "spend_allocation_id": "2946abc3-...",
      "receipt_uuids": null,
      "trip_uuid": null,
      "trip_name": null,
      "accounting_categories": null,
      "attendees": null,
      "suggested_memos": [],
      "suggested_codings": [],
      "suggested_funds": [],
      "missing_items": null,
      "transaction_link": "https://app.ramp.com/business-overview/transactions/ab512db5-..."
    }
  ],
  "total_count": 92,
  "next_page_cursor": "gAAAAABp..."
}
```

**Important:** The `missing_items`, `suggested_memos`, `suggested_codings`, and `suggested_funds` fields in the list response are often `null` or empty even when items are actually missing or suggestions exist. Always use the dedicated per-transaction tools (`ramp_get_transaction_missing_items`, `ramp_get_transaction_suggested_memos`) for reliable data.

For any transaction, check what's missing:

```json
{
  "tool": "ramp_get_transaction_missing_items",
  "args": {
    "id": "{transaction_uuid}",
    "rationale": "Check whether this transaction is missing a receipt, memo, or accounting items before proposing any cleanup."
  }
}
```

**Response shape:**
```json
{
  "transaction_id": "ab512db5-...",
  "missing_receipt": false,
  "missing_memo": false,
  "missing_accounting_items": []
}
```

Returns:
- `missing_receipt` (bool)
- `missing_memo` (bool)
- `missing_accounting_items` (array of category names)

If the user asks which transactions are missing items, iterate through the surfaced transactions, check missing items on each, and group the results by memo, accounting items, and receipt.

**Latency note:** Each call to `ramp_get_transaction_missing_items` is a separate MCP round-trip. For large transaction sets (20+), check the first 10–15, report results, and ask the user if they want to continue checking the rest rather than blocking on 50 sequential calls.

### Step 2: Get AI-suggested memos

Before writing memos manually, check if Ramp has suggestions:

```json
{
  "tool": "ramp_get_transaction_suggested_memos",
  "args": {
    "id": "{transaction_uuid}",
    "rationale": "Fetch Ramp's suggested memos for this transaction before proposing or applying a manual memo."
  }
}
```

**Response shape:**
```json
{
  "id": "ab512db5-...",
  "memos": [
    "CKO travel",
    "Team transportation",
    "Ground transportation for CKO"
  ]
}
```

Returns `memos[]` — an array of suggested memo strings. May be empty if there isn't enough context for suggestions.

### Step 3: Get full transaction details

When you need the complete picture of a transaction before editing (current memo, fund, tracking categories, comments):

```json
{
  "tool": "ramp_get_full_transaction_metadata",
  "args": {
    "id": "{transaction_uuid}",
    "rationale": "View complete transaction details before proposing edits."
  }
}
```

**Response shape:**
```json
{
  "id": "ab512db5-...",
  "amount_cents": 3687,
  "merchant_name": "Uber",
  "memo": "Team transportation",
  "memo_source": "RECURRING_MEMO_MERCHANT",
  "created_at": "2026-02-07T00:51:33",
  "personal_repayment_state": null,
  "tracking_categories": [],
  "fund_name": "Marketing Budget",
  "user_name": "Jane Smith",
  "comments": {
    "count": 0,
    "comments": []
  }
}
```

### Step 4: Edit transactions

#### Set a memo

```json
{
  "tool": "ramp_edit_transaction",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "memo": "Q2 team offsite catering",
    "user_submitted_fields": ["memo"],
    "rationale": "Set the memo on this transaction based on the user's explicit instruction."
  }
}
```

To clear a memo, pass an empty string as the memo value.

**Post-edit behavior:** The `ramp_edit_transaction` response includes updated `missing_items` and suggestions. After a successful edit, check this response to see if there are remaining missing items and prompt the user for the next one. The tool's own description specifies this order: receipt → memo → accounting categories → funds → trip → attendees. If all agent-fillable items are complete, provide the `transaction_link` URL so the user can finish any remaining items (like receipt upload) in the Ramp UI.

#### Assign to a fund / spend allocation

To find available funds for the current user:

```json
{
  "tool": "ramp_get_user_funds",
  "args": {
    "funds_to_retrieve": "MY_FUNDS",
    "include_balance": true,
    "rationale": "List the current user's available funds so I can identify which fund to apply to the transaction."
  }
}
```

**Response shape:**
```json
{
  "funds": [
    {
      "id": "a974b0c1-...",
      "name": "KYC (Know Your Customer)",
      "state": "ACTIVE",
      "balance_info": "$0.00 / $50.00 ($50.00 remaining)",
      "restrictions": null,
      "lock": null,
      "member_locks": [],
      "members": []
    }
  ],
  "total_count": 10
}
```

You can also scope funds to a specific transaction using `for_transaction_id`, or search by name using `search_by_fund_display_name`.

Then edit:

```json
{
  "tool": "ramp_edit_transaction",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "fund_uuid": "{fund_id}",
    "user_submitted_fields": ["fund_uuid"],
    "rationale": "Assign the selected fund to this transaction based on the user's instruction."
  }
}
```

#### Set tracking categories (accounting codes)

First, get available categories:

```json
{
  "tool": "ramp_get_tracking_categories",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "include_hidden": false,
    "rationale": "Retrieve the active tracking categories available for this transaction so I can identify the correct accounting category to set."
  }
}
```

**Response shape:**
```json
{
  "tracking_categories": [
    {
      "tracking_category_uuid": "afe32ec7-...",
      "name": "Department",
      "type": "OTHER",
      "input_type": "SINGLE_CHOICE",
      "is_hidden": false
    }
  ]
}
```

Then get options for the selected category. Always pass `transaction_uuid` and set `include_hidden` to `false` when coding a specific transaction — this applies subsidiary/conditional filtering. Use `query_string` to search by name:

```json
{
  "tool": "ramp_get_tracking_category_options",
  "args": {
    "tracking_category_uuid": "{tracking_category_uuid}",
    "transaction_uuid": "{transaction_uuid}",
    "include_hidden": false,
    "query_string": "Marketing",
    "page_size": 50,
    "rationale": "Find the matching tracking category option to apply to this transaction."
  }
}
```

**Response shape:**
```json
{
  "options": [
    {
      "tracking_category_option_uuid": "4653156e-...",
      "name": "Applied AI",
      "code": null,
      "is_hidden": false
    }
  ],
  "next_page_cursor": 97337367
}
```

Note: `next_page_cursor` is an **integer**, not a string. If present, pass it to get more results. Pagination is not supported when `query_string` is provided with semantic search enabled.

Then edit using `category_uuid` and `option_selection` (not the response field names):

```json
{
  "tool": "ramp_edit_transaction",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "tracking_category_selections": [
      {
        "category_uuid": "{tracking_category_uuid}",
        "option_selection": "{tracking_category_option_uuid}"
      }
    ],
    "user_submitted_fields": ["tracking_category_selections"],
    "rationale": "Apply the selected accounting category option to this transaction based on the user's instruction."
  }
}
```

#### Set attendees

If the user names attendees who are Ramp users, search for them first. The `transaction_id` param (note: **not** `transaction_uuid`) helps rank results by relevance:

```json
{
  "tool": "ramp_search_user",
  "args": {
    "search": "Jane Smith",
    "transaction_id": "{transaction_uuid}",
    "rationale": "Find the matching user to attach as an attendee to this transaction."
  }
}
```

**Response shape:**
```json
{
  "users": [
    {
      "id": "ed735740-...",
      "label": "Junho Choi",
      "description": "jchoi@ramp.com • Forward Deployed Engineering"
    }
  ]
}
```

Then edit. `attendee_selections` is an object (not an array) with fields for Ramp and non-Ramp attendees:

```json
{
  "tool": "ramp_edit_transaction",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "attendee_selections": {
      "non_ramp_attendees": [
        {"attendee_name": "External Guest", "attendee_email": "guest@other.com"}
      ],
      "include_self_as_attendee": false
    },
    "user_submitted_fields": ["attendee_selections"],
    "rationale": "Add the attendees specified by the user to this transaction."
  }
}
```

#### Set trip

To find candidate trips for the current user. Note: this tool does **not** accept a `transaction_uuid` — it returns the user's ongoing, upcoming, and recently completed trips:

```json
{
  "tool": "ramp_get_candidate_trips_for_transaction",
  "args": {
    "rationale": "Retrieve candidate trips that may be relevant to this transaction before assigning one."
  }
}
```

**Response shape:**
```json
{
  "trips": []
}
```

Returns an array of trip objects. May be empty if the user has no active or recent trips.

Then edit with the chosen trip:

```json
{
  "tool": "ramp_edit_transaction",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "trip_selection": {
      "trip_uuid": "{trip_uuid}"
    },
    "rationale": "Associate the selected trip with this transaction based on the user's instruction."
  }
}
```

If the user needs a new trip first, create one:

```json
{
  "tool": "ramp_create_trip",
  "args": {
    "name": "NYC Client Visit",
    "are_trip_dates_from_booking_receipt_or_user_input": true,
    "start_date": "2026-04-10",
    "end_date": "2026-04-12",
    "destinations": ["New York, NY"],
    "trip_purpose": "Client meetings",
    "rationale": "Create a new trip for the user to associate with their travel transactions."
  }
}
```

Required params: `name` (string), `are_trip_dates_from_booking_receipt_or_user_input` (boolean — set to `true` if dates come from the user or a booking receipt, `false` otherwise), `rationale` (string). Optional: `start_date`, `end_date`, `destinations` (array), `trip_purpose`.

### Step 5: Handle missing receipts

If `missing_receipt` is true, there are two options:

1. **Upload a receipt** — hand off to the receipt-compliance skill
2. **Mark as no receipt**

If the user says there was no receipt or wants to flag the transaction:

```json
{
  "tool": "ramp_mark_transaction_missing_receipt",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "rationale": "Flag this transaction as having no receipt because the user indicated no receipt is available."
  }
}
```

If Ramp then asks for the reason (i.e., the user has already flagged it and now needs to explain why), provide it:

```json
{
  "tool": "ramp_provide_no_receipt_reason",
  "args": {
    "transaction_uuid": "{transaction_uuid}",
    "reason": "Digital subscription — no receipt issued",
    "rationale": "Provide the user's no-receipt explanation for this transaction."
  }
}
```

**Important:** Only call `ramp_provide_no_receipt_reason` when the user is responding to a prompt asking for a reason — not as a first step. Use `ramp_mark_transaction_missing_receipt` first to flag it.

## Bulk Cleanup Workflow

For cleaning up many transactions at once:

1. Fetch all transactions in the requested period with `ramp_get_user_transactions` (paginate with `next_page_cursor` if needed)
2. Check `ramp_get_transaction_missing_items` on the first batch (10–15 transactions). If the set is large, report progress and ask before continuing
3. Group results by what's missing: memo, accounting items, receipt
4. Present summary: "12 transactions need memos, 5 need accounting categories, 3 need receipts"
5. For memos: fetch suggestions for each via `ramp_get_transaction_suggested_memos`, present them, let the user confirm or edit
6. For categories: if most transactions share a category, offer to bulk-apply
7. Execute edits sequentially with `ramp_edit_transaction`, then report results

**Error handling:** If an edit fails mid-batch, report which transaction failed and why, then continue with the remaining transactions. Summarize successes and failures at the end.

Do not execute bulk edits until the user confirms the proposed plan.

## Provenance Tracking

The `user_submitted_fields` field tells Ramp which fields the user explicitly provided. This matters for compliance and provenance.

Include it when the user explicitly supplies or approves the value:
- `memo`
- `fund_uuid`
- `tracking_category_selections`
- `attendee_selections`

If the agent is applying a suggested memo that the user explicitly approved, that still counts as user-submitted intent.

## Example Session

```
User: I have a bunch of transactions that need memos

Agent: Let me check what's missing on your recent transactions.
> ramp_get_user_transactions({
    "transactions_to_retrieve": "my_transactions",
    "from_date": "2026-03-15",
    "page_size": 50,
    "include_count": true,
    "rationale": "Retrieve the user's recent cleared transactions so I can identify missing memo items."
  })

Found 8 transactions. Checking missing items on each...
> ramp_get_transaction_missing_items({"id": "{uuid}", "rationale": "Check missing items for cleanup."}) x8

Summary:
  5 need memos
  2 need accounting categories
  1 needs a receipt

Let me get memo suggestions for the 5:
> ramp_get_transaction_suggested_memos({"id": "{uuid}", "rationale": "Fetch memo suggestions."}) x5

Transaction                              Suggested memo
$135  Facebook Ads     2026-03-02       "Q1 paid social campaign"
$220  AWS              2026-03-05       "March infrastructure costs"
$89   Uber             2026-03-10       (no suggestion)
$450  WeWork           2026-03-12       "March coworking space"
$65   Doordash         2026-03-15       (no suggestion)

Want to accept these suggestions, edit them, or write your own?

User: Accept the suggestions for Facebook and AWS. The Uber was a client dinner ride, WeWork is fine, skip DoorDash for now.

Agent: Updating 4 transactions:
> ramp_edit_transaction({
    "transaction_uuid": "{fb-uuid}",
    "memo": "Q1 paid social campaign",
    "user_submitted_fields": ["memo"],
    "rationale": "Apply the memo the user approved."
  })
> ramp_edit_transaction({
    "transaction_uuid": "{aws-uuid}",
    "memo": "March infrastructure costs",
    "user_submitted_fields": ["memo"],
    "rationale": "Apply the memo the user approved."
  })
> ramp_edit_transaction({
    "transaction_uuid": "{uber-uuid}",
    "memo": "Client dinner transportation",
    "user_submitted_fields": ["memo"],
    "rationale": "Apply the memo the user specified."
  })
> ramp_edit_transaction({
    "transaction_uuid": "{wework-uuid}",
    "memo": "March coworking space",
    "user_submitted_fields": ["memo"],
    "rationale": "Apply the memo the user approved."
  })

All 4 memos set. 2 transactions still need accounting categories.
Want to tackle those?

User: Yes, they should both be under the "Marketing" department

Agent:
> ramp_get_tracking_categories({
    "transaction_uuid": "{uuid1}",
    "include_hidden": false,
    "rationale": "Find the relevant tracking category for this transaction."
  })

Found "Department" category (uuid: afe32ec7-...). Searching for Marketing option:

> ramp_get_tracking_category_options({
    "tracking_category_uuid": "afe32ec7-...",
    "transaction_uuid": "{uuid1}",
    "include_hidden": false,
    "query_string": "Marketing",
    "page_size": 50,
    "rationale": "Find the Marketing option for the Department tracking category."
  })

Found "Marketing" option (uuid: mkt-123). Applying to both:
> ramp_edit_transaction({
    "transaction_uuid": "{uuid1}",
    "tracking_category_selections": [{"category_uuid": "afe32ec7-...", "option_selection": "mkt-123"}],
    "user_submitted_fields": ["tracking_category_selections"],
    "rationale": "Apply the Marketing department the user selected."
  })
> ramp_edit_transaction({
    "transaction_uuid": "{uuid2}",
    "tracking_category_selections": [{"category_uuid": "afe32ec7-...", "option_selection": "mkt-123"}],
    "user_submitted_fields": ["tracking_category_selections"],
    "rationale": "Apply the Marketing department the user selected."
  })

Done. 1 transaction remaining needs a receipt — you can upload one (I'll hand off to receipt handling) or mark it as no receipt. What would you like to do?
```

## When NOT to Use

- **Uploading receipt images/files** — use receipt-compliance
- **Approving or rejecting transactions/reimbursements/requests** — use approval-dashboard
- **Company-wide spend reporting or analysis** — use reporting/query workflows, not transaction cleanup
- **Card lock/unlock flows** — use the card-management skill
- **Reimbursement drafting/editing** — use `ramp_edit_reimbursement` (different tool, different params — notably `reimbursement_uuid` not `transaction_uuid`, and `trip_uuid` not `trip_selection`)

## Gotchas

| Issue | Fix |
|---|---|
| MCP tools require `rationale` | Include a concise reason on every tool call |
| List endpoint `missing_items` / `suggested_memos` fields are often null/empty | Always use `ramp_get_transaction_missing_items` and `ramp_get_transaction_suggested_memos` for reliable data |
| `ramp_get_candidate_trips_for_transaction` takes no `transaction_uuid` | It returns the user's recent/ongoing trips globally — match to the transaction by date yourself |
| Tracking category options `next_page_cursor` is an integer | Pass it as a number, not a string |
| Tracking category edit payload uses different field names than the response | Use `category_uuid` + `option_selection`, not `tracking_category_uuid` + `tracking_category_option_uuid` |
| `ramp_search_user` param is `transaction_id` | Not `transaction_uuid` — even though you pass a UUID value |
| `ramp_create_trip` requires `are_trip_dates_from_booking_receipt_or_user_input` | Boolean, required — set `true` if dates came from user or booking, `false` otherwise |
| Bulk missing-items checks are sequential | Each is a separate MCP call — batch in groups of 10–15 to avoid long waits |
| `ramp_provide_no_receipt_reason` is a follow-up tool | Only call it after `ramp_mark_transaction_missing_receipt`, when Ramp asks for a reason |
| `state` filter values are lowercase | Use `cleared`, `declined`, etc. |
| `transactions_to_retrieve` is required | Default to `"my_transactions"` for this skill |
| Text search across transactions | Use `reason_memo_merchant_or_user_name_text_search` param on `ramp_get_user_transactions` |
| Missing receipt requires separate tools | Use `ramp_mark_transaction_missing_receipt` and `ramp_provide_no_receipt_reason`, not `ramp_edit_transaction` |
| Failed edits in a bulk run | Report the failure, continue with remaining transactions, summarize at the end |
