# Self-Delivery

Read this file when the user explicitly asks to send content to their own Gmail account, including requests such as "email me," "send this to me," "email this report to myself," or automated delivery to the user.

## Workflow

- Call `send_email` directly with `to: "me"` and omit `cc` and `bcc`.
- Do not create a draft or ask for another confirmation merely because the email body was generated during the turn.
- Use this exception only for the authenticated Gmail account. If another recipient is requested or the destination is ambiguous, follow the normal send-safety rules instead.
