# Pasted Gmail Links

Gmail web URLs are browser navigation links, not a documented Gmail API identifier format. Treat resolution as a narrow best-effort convenience, never as support for arbitrary Gmail URLs.

## Supported URL Shapes

Only attempt resolution for HTTPS URLs on the exact host `mail.google.com` with one of these shapes:

- `https://mail.google.com/mail/u/<account-index>/#<mailbox-view>/<token>`
- `https://mail.google.com/mail/#<mailbox-view>/<token>`

`<account-index>` must be decimal digits. `<mailbox-view>` must be one of `all`, `inbox`, `sent`, `starred`, `snoozed`, `drafts`, `trash`, `spam`, or `important`. The fragment must contain exactly the mailbox view and one non-empty token. Ignore a query suffix attached to the token, such as `?attachment_id=...`, but do not interpret it as part of the Gmail ID.

Do not attempt to extract an ID from search, label, category, settings, compose, or other Gmail routes. Do not accept lookalike hosts or non-HTTPS URLs.

## Bounded Resolution

1. Extract the opaque token without changing its case or otherwise transforming it.
2. Call `read_email_thread` with the token as a message ID, using the tool's default `id_type="message"` behavior.
3. Only when that exact lookup reports that the ID is invalid or not found, retry once with the same token and `id_type="thread"`.
4. If either lookup succeeds, use the returned thread as the requested context.
5. Do not broaden the attempt into `search_emails`, `search_email_ids`, subject guessing, sender guessing, pagination, or repeated retries.

The `/u/<account-index>/` segment is a browser account slot, not an instruction to select a connector account. Always use the currently connected Gmail account. If the link belongs to a different mailbox, report that mismatch instead of trying another account.

Do not perform the thread-ID retry after authentication, authorization, connector availability, rate-limit, or transient provider errors. Report those errors according to their actual cause.

## Fast-Fail Recovery

For an unsupported URL shape, fail immediately without calling Gmail tools. If both exact-ID attempts return invalid or not found, stop after the second attempt.

Tell the user that the Gmail link could not be resolved and ask for one of these fetchable alternatives:

- the sender, subject, and approximate date;
- an RFC 822 `Message-ID` header;
- the relevant email text pasted into the conversation.

If Gmail is disconnected or the link belongs to a different mailbox, ask the user to connect or select the mailbox that contains the message. Keep the explanation concise and do not imply that arbitrary Gmail web links are supported.
