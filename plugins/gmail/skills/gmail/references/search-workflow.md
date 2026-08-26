# Search Workflow

Read this file when search quality materially affects the outcome, especially for triage, topic discovery, follow-up detection, attachment-heavy queries, or mailbox cleanup.

## Core Defaults

- Strongly prefer `search_emails` over `search_email_ids`.
- Use `search_email_ids` only when a downstream action specifically needs message IDs and the richer `search_emails` response will not help you make a better decision.
- Use Gmail query syntax as the primary search control surface.
- `search_emails` is message-level, not thread-grouped. If thread context matters, expand the specific messages of interest with `read_email_thread`.
- Label-aware search is supported. Use Gmail query syntax such as `label:foo` for label search, and use `tags` for built-in/system-label filtering when that is more direct.
- Prefer small pages for latency when using `search_emails`. In most cases, ask for about 20 results at a time rather than large pages. For `search_email_ids`, larger pages such as 100 can be reasonable when you only need IDs.
- Use `tags` only as `list[str]`. Do not pass a single string.
- Common system labels for `tags` include `INBOX`, `STARRED`, `TRASH`, `DRAFT`, `SENT`, `SPAM`, `UNREAD`, and `IMPORTANT`.
- For All Mail, prefer Gmail query syntax such as `in:anywhere` instead of guessing a tag value.

## Search Pattern

1. Start with a Gmail query that matches the task shape: inbox, unread, recent dates, sender set, topic, attachments, or `in:anywhere`.
2. Treat `search_emails` results as reverse chronological by default. The first page is the newest matching mail.
3. Inspect the first page of `search_emails` results before deciding to read bodies.
4. If the result set is promising but incomplete, continue with `next_page_token` for stable pagination into older matching results.
5. If the task is really about recurring senders, subscriptions, or engagement patterns, group or reason by normalized sender rather than message by message.
6. If the result set is noisy, tighten the search with exclusions, label filters, narrower date windows, or more specific topic terms.
7. Read bodies with `batch_read_email` only for the shortlisted messages whose snippets are insufficient.
8. Escalate to `read_email_thread` only when thread context changes the answer.

## Reading Strategy

- Use `search_emails` when snippets, sender metadata, subject lines, timestamps, and labels are enough to shortlist or summarize.
- When the question is sender-level, compare patterns across messages from the same sender before making a claim.
- Use `batch_read_email` when you need the body of multiple shortlisted emails.
- Use `read_email_thread` for thread summaries, reply drafting, or back-and-forth context.
- Calibrate depth to the task:
  - For recent or narrow requests, read only a small candidate set.
  - For broader audits or cleanup tasks, search more widely but still shortlist before reading bodies.

## Triage And Follow-Up

- For urgency-ranking or reply-needed tasks, favor human-origin and action-oriented messages.
- Rank urgency only after reading enough message content to justify the claim.
- State the search scope and coverage in the answer, especially when the result comes from a narrowed search or a sampled shortlist.
- Avoid absolute claims like "the only urgent email" unless the scan was comprehensive.

## Search Pitfalls

- Be careful with `has:attachment` and attachment-heavy searches. Gmail often counts calendar invites and `.ics` meeting traffic as attachments, so inspect a sample before concluding that the results are true file-sharing emails.
- Do not default to only the newest mail when the task is better expressed as a sender, topic, unread, or date-bounded query.
- Remember that `next_page_token` usually means older matching mail, not a resorted sample.
- Prefer refining the current search or paginating with `next_page_token` over rerunning a loose query that may reshuffle the result set.
- Do not request very large pages by default for `search_emails`. Large `max_results` values can add latency and make pagination failures more painful; start around 20 unless there is a strong reason to do more. `search_email_ids` is the main exception, where larger pages such as 100 can be worthwhile.
- Do not treat a broad stale-unread search as a proxy for sender-level behaviors like "newsletters I stopped reading." Those tasks usually need newsletter-like candidate queries and sender grouping.
