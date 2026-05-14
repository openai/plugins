---
name: twilio-sendgrid-suppressions
description: >
  Manage SendGrid email suppressions: bounces, blocks, spam reports,
  invalid emails, global unsubscribes, and ASM suppression groups.
  Covers when and how to remove suppressions, reputation impact, and
  category-based unsubscribe management. Use when debugging SendGrid
  delivery issues or building unsubscribe flows. Requires a SendGrid API
  key (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).
---

## Overview

Suppressions prevent SendGrid from sending to addresses that have bounced, reported spam, or unsubscribed. They protect your sender reputation but can also block legitimate re-sends if not managed correctly.

---

## Suppression Types

| Type | Endpoint | What triggers it | Auto-added? |
|------|----------|-----------------|-------------|
| **Hard Bounces** | `/v3/suppression/bounces` | Permanent delivery failure (invalid mailbox, domain doesn't exist) | Yes |
| **Soft Bounces** | No management API — automatic retry only | Temporary failure (mailbox full, server down) — SendGrid auto-retries before suppressing | Yes, after repeated failures |
| **Blocks** | `/v3/suppression/blocks` | Temporary rejection by receiving server (reputation, policy, content) | Yes |
| **Spam Reports** | `/v3/suppression/spam_reports` | Recipient marks email as spam | Yes |
| **Invalid Emails** | `/v3/suppression/invalid_emails` | Malformed email address | Yes |
| **Global Unsubscribes** | `/v3/suppression/unsubscribes` | Recipient unsubscribes from all email | Yes |
| **Group Unsubscribes (ASM)** | `/v3/asm/groups/{id}/suppressions` | Recipient unsubscribes from a category | Yes |

**Hard vs Soft bounces:** Hard bounces (permanent) immediately suppress the address. Soft bounces (temporary) trigger retries — SendGrid will retry delivery before eventually suppressing if the issue persists.

---

## Managing Suppressions

**List bounces (Python)**
```python
import os, requests

headers = {"Authorization": f"Bearer {os.environ['SENDGRID_API_KEY']}"}
response = requests.get("https://api.sendgrid.com/v3/suppression/bounces", headers=headers)
for bounce in response.json():
    print(f"{bounce['email']}: {bounce.get('reason', 'unknown')}")
```

**Remove a bounce (Python)**
```python
requests.delete(f"https://api.sendgrid.com/v3/suppression/bounces/{email}", headers=headers)
```

> **Caution:** Deleting suppression records (especially spam reports) allows re-sending to addresses that previously complained. Always confirm with the user before removal and document the business reason.

---

## ASM Suppression Groups

Use suppression groups for category-based unsubscribes (e.g., "Marketing", "Transactional", "Product Updates"). Recipients can unsubscribe from one category without being suppressed from all email.

**Create a group:**
```python
requests.post("https://api.sendgrid.com/v3/asm/groups",
    headers={**headers, "Content-Type": "application/json"},
    json={"name": "Marketing Emails", "description": "Promotional offers and updates"})
```

**Send with a suppression group:**
Include `asm.group_id` in your Mail Send request. Recipients see a "manage preferences" link instead of a global unsubscribe.

---

## Auto-Purge (Bounce & Block Cleanup)

Configure automatic purge schedules in Console > Settings > Mail Settings > Purge Bounces & Blocks:

- **Soft Bounces:** Auto-purge after N days (1–3,650 days)
- **Hard Bounces:** Auto-purge after N days (1–3,650 days)

**Caution:** Enabling auto-purge without a business reason allows re-sending to previously bounced addresses, which damages sender reputation. Do not use as a workaround to force delivery.

---

## Address Allow List

Console > Settings > Mail Settings > Address Allow List allows specific email addresses or domains to bypass all suppressions. Useful for internal testing addresses.

**Use with extreme caution** — never allowlist domains you don't control (e.g., `gmail.com`), and never use to bypass spam report suppressions.

---

## CANNOT

- **Suppressions are global by default** — A bounce or spam report on ANY email suppresses the address from ALL future sends. Use ASM groups to scope unsubscribes.
- **Removing a suppression does not fix the underlying issue** — Deleting a bounce record lets you retry, but the mailbox is likely still invalid. Re-sending to hard bounces damages sender reputation.
- **Cannot prevent spam report suppressions** — When a recipient marks you as spam, the suppression is automatic and cannot be overridden.
- **Cannot bulk-remove suppressions by domain** — Must remove individually by email address via API.

---

## Next Steps

- **Send email:** `twilio-sendgrid-email-send`
- **Delivery tracking:** `twilio-sendgrid-webhooks`
- **Account setup:** `twilio-sendgrid-account-setup`
