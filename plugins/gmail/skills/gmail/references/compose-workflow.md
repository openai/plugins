# Compose Workflow

Read this file when the user wants to compose, draft, or send a new email, including sending generated content to their own Gmail account.

## Core Defaults

- If the user asks to compose or draft but does not explicitly ask to send, prepare a draft.
- Preserve the requested recipients, subject, facts, dates, and links. Clarify any destination or recipient ambiguity before acting.
- For recipients other than the authenticated Gmail account, follow the normal send-safety rules and require explicit confirmation before sending.

## Self-Delivery

- When the user explicitly asks to email or send something to themselves, including from an automation, call `send_email` directly with `to: "me"` and omit `cc` and `bcc`.
- Do not create a draft or ask for another confirmation merely because the email body was generated during the turn.
- Use this exception only for the authenticated Gmail account. If another recipient is requested or the destination is ambiguous, follow the normal send-safety rules instead.
