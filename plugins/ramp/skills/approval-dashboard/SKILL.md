---
name: approval-dashboard
description: |-
  Review and approve pending transactions, bills, reimbursements, and requests.
  Use when: 'approve', 'pending approvals', 'what needs my approval',
  'review transactions', 'approve bills', 'reject', 'approval queue',
  'clear my approvals'. Do NOT use for: transaction analysis, receipt uploads,
  or spend tracking.
---

## Non-Negotiables

- Always show the item details before approving or rejecting. Never blind-approve.
- Rejections require a reason. Approvals do not, but a note is helpful.
- Confirm with the user before executing approvals — especially bulk operations.
- Present items sorted by priority: highest dollar amount first.
- Amounts vary by endpoint: bills are in **cents** (divide by 100), reimbursements are in **dollars**, transactions are formatted strings ("$135.40").

## Workflow

### Step 1: Fetch all pending items

Run these in parallel to build the full approval queue. **Paginate each endpoint until there are no more results** — a single page may not return everything.

```python
# Pending transactions (paginate with next_page_cursor)
ramp_get_user_transactions({
  "rationale": "Retrieve transactions awaiting my approval",
  "transactions_to_retrieve": "transactions_awaiting_my_approval",
  "page_size": 50,
  "include_count": true
})

# Pending bills (paginate with page_cursor)
ramp_get_bills_for_approval({
  "rationale": "Retrieve bills pending my approval",
  "limit": 50
})

# Pending reimbursements (no cursor pagination tool surface — use limit)
ramp_get_reimbursements_for_approval({
  "rationale": "Retrieve reimbursements pending my approval",
  "limit": 50
})

# Pending requests (paginate with start; thoughts is required)
ramp_get_requests_to_review({
  "rationale": "Retrieve all pending requests for review",
  "thoughts": "Reviewing all pending requests",
  "page_size": 50
})
```

For each endpoint, check the pagination cursor in the response envelope. If it is not null, re-run the call with that cursor value (`next_page_cursor` for transactions, `page_cursor` for bills, `start` for requests) until all pages are fetched. Note: `ramp_get_reimbursements_for_approval` does not expose cursor-based pagination in this MCP surface — increase `limit` if you need more results. Aggregate results before presenting.

### Step 2: Present the queue

Summarize what's pending:

```
Approval queue: 14 items ($23,450 total)

Bills (4 items, $8,200):
  $3,500  HighSpot        Invoice #1234    Due 2026-03-28
  $2,500  Cometeer        Invoice #5678    Due 2026-04-01
  ...

Reimbursements (6 items, $2,100):
  $  520  Michael Scott   Uber rides       Submitted 2026-03-20
  $  312  Oscar Martinez  Office supplies  Submitted 2026-03-22
  ...

Transactions (3 items, $12,500):
  $5,000  Dana Alhasawi   AWS              2026-03-15
  ...

Requests (1 item, $650):
  ...
```

### Step 3: Review and act

For each item the user wants to act on, get details first:

```python
# Bill details
ramp_get_bill_details({
  "bill_id": "{bill_id}",
  "rationale": "Retrieve bill details before approval review"
})

# Transaction details
ramp_get_full_transaction_metadata({
  "id": "{transaction_uuid}",
  "rationale": "Retrieve full transaction details before approval review"
})

# Transaction missing items (if relevant)
ramp_get_transaction_missing_items({
  "id": "{transaction_uuid}",
  "rationale": "Check whether the transaction is missing receipt, memo, or coding items"
})

# Reimbursement details (use get with specific UUID)
ramp_get_reimbursements({
  "reimbursement_uuids": ["{uuid}"],
  "include_policy_assessment": true,
  "rationale": "Retrieve reimbursement details for approval review"
})
```

### Step 4: Execute approvals

```python
# Approve a transaction
ramp_approve_or_reject_transaction({
  "transaction_id": "{transaction_uuid}",
  "action": "APPROVE",
  "thoughts": "Reviewed — within policy",
  "rationale": "Approve the reviewed transaction"
})

# Reject a transaction (reason required)
ramp_approve_or_reject_transaction({
  "transaction_id": "{transaction_uuid}",
  "action": "REJECT_AND_REQUEST_CHANGES",
  "thoughts": "Missing receipt and over budget",
  "user_reason": "Please attach the receipt and update the memo",
  "rationale": "Reject the transaction and request changes"
})

# Approve a bill — not yet available via MCP tool.
# Bill approvals must be done in the Ramp app: https://app.ramp.com/bills

# Approve a reimbursement
ramp_approve_or_reject_reimbursement({
  "reimbursement_id": "{reimbursement_uuid}",
  "action": "approve",
  "rationale": "Approve the reviewed reimbursement"
})

# Reject a reimbursement
ramp_approve_or_reject_reimbursement({
  "reimbursement_id": "{reimbursement_uuid}",
  "action": "reject",
  "user_reason": "Receipt doesn't match the claimed amount",
  "rationale": "Reject the reimbursement with a clear reason"
})

# Approve a request
ramp_approve_or_reject_request({
  "request_uuid": "{request_uuid}",
  "action": "APPROVE",
  "thoughts": "Approved — within team budget",
  "rationale": "Approve the reviewed request"
})
```

### Step 5: Add comments (optional)

Leave a comment on any Ramp object for context:

```python
ramp_post_comment({
  "ramp_object_uuid": "{object_uuid}",
  "ramp_object_type": "transaction",
  "message": "Approved — this covers the Q1 offsite catering",
  "rationale": "Leave context on the approved object"
})
```

Valid object types: `bill`, `booking_request`, `card`, `payee`, `provisional_bill`, `reimbursement`, `spend_intent`, `spend_request`, `ticket`, `transaction`, `vendor_payment`.

## Bulk Approval

When the user wants to approve multiple items at once:

1. Present all items with amounts and details
2. Ask: "Approve all N items, or would you like to review individually?"
3. If bulk: confirm once, then execute sequentially
4. Report results: "Approved 12/14 items. 2 failed: [reasons]"

## Transaction Approval Actions

| Action | When to use |
|---|---|
| `APPROVE` | Item is within policy, receipt/memo present |
| `REJECT_AND_REQUEST_CHANGES` | Needs corrections — missing memo, wrong coding, etc. |
| `REJECT_AND_REQUEST_FULL_REPAYMENT` | Personal expense or policy violation requiring repayment |

## Example Session

```
User: What needs my approval?

Agent: Let me check all your pending queues.
> ramp_get_user_transactions({ "rationale": "Checking approval queue", "transactions_to_retrieve": "transactions_awaiting_my_approval", "page_size": 50, "include_count": true })
> ramp_get_bills_for_approval({ "rationale": "Checking approval queue", "limit": 50 })
> ramp_get_reimbursements_for_approval({ "rationale": "Checking approval queue", "limit": 50 })
> ramp_get_requests_to_review({ "rationale": "Checking approval queue", "thoughts": "Checking approval queue", "page_size": 50 })

Approval queue: 6 items ($4,350 total)

Bills (2 items, $2,700):
  $2,200  HighSpot        Invoice #4401    Due 2026-03-28
  $  500  Cometeer        Invoice #882     Due 2026-04-01

Reimbursements (3 items, $1,430):
  $  520  Michael Scott   Uber rides       Submitted 2026-03-20
  $  312  Oscar Martinez  Office supplies  Submitted 2026-03-22
  $  598  Jan Levinson    Flight change    Submitted 2026-03-23

Transactions (1 item, $220):
  $  220  Dana Alhasawi   DoorDash         2026-03-15

Want to review individually or approve all?

User: Approve the bills and reimbursements. Let me see the transaction first.

Agent: I can approve the reimbursements now. Bills must be approved in the Ramp app — I'll send you the links.
> ramp_approve_or_reject_reimbursement({ "reimbursement_id": "reimb-001", "action": "approve", "rationale": "Approve reviewed reimbursement" })
> ramp_approve_or_reject_reimbursement({ "reimbursement_id": "reimb-002", "action": "approve", "rationale": "Approve reviewed reimbursement" })
> ramp_approve_or_reject_reimbursement({ "reimbursement_id": "reimb-003", "action": "approve", "rationale": "Approve reviewed reimbursement" })

3 reimbursements approved. For the 2 bills, approve them here:
  https://app.ramp.com/bills/bill-001
  https://app.ramp.com/bills/bill-002

Now let me get details on that DoorDash transaction:
> ramp_get_full_transaction_metadata({ "id": "txn-001", "rationale": "Retrieve transaction details before approval review" })
> ramp_get_transaction_missing_items({ "id": "txn-001", "rationale": "Check whether the transaction is missing required items" })

DoorDash $220 — Dana Alhasawi, 2026-03-15
Memo: "Team lunch"  |  Receipt: attached  |  Accounting: complete

User: Approve it

Agent: > ramp_approve_or_reject_transaction({ "transaction_id": "txn-001", "action": "APPROVE", "thoughts": "Team lunch — receipt and memo present", "rationale": "Approve the reviewed transaction" })
Done. Approval queue is clear.
```

## When NOT to Use

- **Editing transaction memos or categories** — use transaction-cleanup

## Gotchas

| Issue | Fix |
|---|---|
| Bill amounts are in cents | Divide by 100 for display |
| Reimbursement amounts are in dollars | Display as-is |
| Transaction amounts are formatted strings | Strip "$" and "," for sorting/totaling |
| `requests pending` requires `--thoughts` | Always include it — describe what you're doing |
| Bill approvals are not yet exposed in this MCP surface | Send the user to the Ramp app for bill approval |
| No undo for approvals | Confirm with user before executing. Consider dry-run style confirmation in chat before write calls. |
| Pagination varies | Check the response cursor fields. Pass them via `next_page_cursor` (transactions), `page_cursor` (bills), `start` (requests). Reimbursements: `limit` only in this MCP surface. |
