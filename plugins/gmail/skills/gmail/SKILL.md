---
name: gmail
description: Manage Gmail search, thread reading, summaries, reply or forward drafts, self-delivery, inbox triage, and label actions. Use for mailbox analysis, pasted Gmail links, email replies or forwards, inbox cleanup, or explicit Gmail writes.
---

# Gmail

- `search_emails` returns message-level summaries, not grouped threads. Shortlist first; use `batch_read_email` for several shortlisted bodies, and `read_email_thread` when surrounding conversation changes a summary, reply, recipient choice, or triage bucket. Use `search_email_ids` only when the next action specifically needs IDs. Pass `tags` as `list[str]` with uppercase system labels; use Gmail query syntax such as `label:foo` or `in:anywhere` for custom labels and All Mail.
- Continue older matching results with `next_page_token` instead of rerunning a loose query. For “newsletters I stopped reading” or similar sender-level questions, use newsletter-like candidate queries and group by normalized sender rather than treating stale unread as a proxy. `has:attachment` can include calendar and `.ics` traffic.

## Pasted Gmail links

- Treat Gmail web links as bounded best-effort only. Accept only HTTPS on exact host `mail.google.com` with `/mail/u/<decimal account-index>/#<view>/<token>` or `/mail/#<view>/<token>`; view is `all`, `inbox`, `sent`, `starred`, `snoozed`, `drafts`, `trash`, `spam`, or `important`, and the fragment must contain exactly one nonempty token. Ignore a token query suffix such as `?attachment_id=...`, preserve token case, and reject search/label/category/settings/compose routes, lookalike hosts, and non-HTTPS URLs without Gmail calls.
- For a supported link, call `read_email_thread` with the token using default `id_type="message"`; retry once with the same token and `id_type="thread"` only if the first lookup is invalid or not found. If either succeeds, use the returned thread as context. Never broaden into search, guessing, pagination, or repeated retries, and do not thread-retry after auth, authorization, availability, rate-limit, or transient errors.
- `/u/<index>/` is a browser slot, not connector account selection. After mismatch or two exact misses, stop and request sender + subject + approximate date, RFC 822 Message-ID, pasted email text, or the correct connected mailbox.

## Writes

- Send, archive, trash, label, or move only when the user clearly asked for that state change. Preserve exact recipients, subjects, quoted facts, dates, and links unless asked to change them; disambiguate competing threads or recipient identities before acting.
- `forward_emails` takes `message_ids: list[str]`, sends one separate new forwarded email per source message, inlines that source content, preserves its attachments, and places a `note` above it.
- After a Gmail write, report the completed operation and enough non-sensitive, user-meaningful context to verify it: for example, replied to “<subject>”, sent “<subject>” to <recipients>, or forwarded “<subject>” to <recipients>. Do not expose raw message or thread identifiers. If the action only created a draft, say so explicitly and never imply it was sent; avoid quoting body content or other sensitive details unless needed.
- After `create_draft`, include the returned `web_url` as an openable link so the user can review the saved draft in Gmail. Do not construct a Gmail URL from raw identifiers.
- For explicit self-delivery such as “email me,” call `send_email` directly with `to: "me"` and omit `cc` and `bcc`; do not draft or ask another confirmation merely because the body was generated this turn. This exception applies only to the authenticated account.
- `apply_labels_to_emails` takes message IDs and add/remove label names as lists plus `create_missing_labels: bool`; use `bulk_label_matching_emails` for a clear query-defined set and `apply_labels_to_emails` for an inspected ID shortlist.

## Triage

- Default direct inbox triage to `INBOX` plus a clear timeframe. When a low-signal notification may hide a long active thread, `read_email_thread` exposes `total_messages`; use it to detect the expansion risk before classifying.
