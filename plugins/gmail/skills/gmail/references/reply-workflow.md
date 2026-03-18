# Reply Workflow

Read this file when the user wants to reply to an email, draft a response, decide whether to reply-all, or match the tone of an existing thread.

## Core Defaults

- Read the most recent thread items before drafting. At a minimum, inspect the latest message and enough recent context to understand who is asking for what, whether the thread already moved forward, and what tone the participants are using.
- Match the thread's tone unless the user asks for a deliberate change. Pay attention to formality, brevity, warmth, directness, and how participants greet or sign off.
- Before writing a greeting, self-reference, or signature that uses the user's name, call `get_profile` and treat that as the primary source of truth. If the profile is unavailable, prefer other first-party profile/contact context and ask the user before guessing.
- If the user asks to reply but not explicitly to send, default to a draft.
- Gmail compose is not plain-text only. The body input is treated as Markdown/plain text and the send path includes both plain text and generated HTML. Do not claim that the connector only supports plain-text emails, but also do not assume it supports arbitrary custom HTML authoring.

## Reply-All Etiquette

- Do not default to reply-all just because multiple recipients are present.
- Prefer replying only to the sender when the answer is mainly for them, when other recipients are merely copied for awareness, or when replying-all would create unnecessary noise.
- Prefer reply-all when the response materially affects the wider recipient set, preserves shared context people still need, answers a group question, or avoids hiding a decision from stakeholders who were clearly included on purpose.
- Be extra careful with external recipients, large lists, and mixed internal/external threads. If reply-all could create social or privacy risk, call that out.
- If the right audience is ambiguous, say so and identify the safest default.

## Reading Pattern

1. Inspect the most recent message first.
2. Read at least enough recent context to understand the latest ask, current status, open questions, and participants.
3. Escalate to `read_email_thread` when earlier back-and-forth changes the answer, recipient choice, or tone.
4. Preserve concrete facts from the thread such as dates, commitments, links, and names unless the user asks to change them.
5. Do not infer the user's name from their email address or make up a likely first name when signing the draft.

## Drafting Pattern

1. Acknowledge the latest relevant message.
2. Answer the actual ask before adding extras.
3. Keep the draft aligned with the user's goal: confirm, decline, follow up, clarify, or unblock.
4. If information is missing, produce the best draft you can and call out the unresolved detail separately.
5. Preserve subject intent and recipient intent unless the user asks to change them.
6. When formatting matters, write clean Markdown-friendly email body text rather than describing the output as plain text only.
