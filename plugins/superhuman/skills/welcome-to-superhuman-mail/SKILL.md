---
name: welcome-to-superhuman-mail
description: Welcome and onboard a new user to Superhuman Mail MCP. Use when the user is new to Superhuman Mail, asks what Superhuman Mail can do, wants a guided tour, setup walkthrough, first actions, examples for email or calendar workflows, help adding accounts, client-specific tool approval settings, Gmail/Outlook/app options, or says they want to get started with Superhuman Mail.
---

# Welcome to Superhuman Mail

Guide the user through a short, interactive onboarding for Superhuman Mail. Keep it warm, concise, and choice-driven. Do not run account, email, calendar, or send actions until the user chooses them. After the user completes any onboarding task, show the full menu again and ask what they want to try next.

## Opening

Welcome the user to Superhuman Mail and explain that they can use it to:

- Search and answer questions across email and calendar.
- Draft, edit, schedule, and send emails.
- Create or update calendar events.
- Use Superhuman features outside this MCP client in Gmail, Outlook, desktop, and mobile apps.

Then present the onboarding as a menu and ask what they want to try first. If the client supports buttons or quick replies, use them. Re-present this same menu after each completed task unless the user says they are done.

Suggested menu:

1. Add another email account
2. Draft a first email
3. Ask questions of my inbox
4. Tune tool approval settings
5. Use Superhuman in Gmail & Outlook, and apps
6. Create or update a calendar event
7. Watch video tutorials for more ideas

## Add another email account

Tell the user they can add multiple Gmail or Outlook accounts to Superhuman Mail.

If the client supports buttons, show:

- **Add account** - call the `add_account` tool
- **Skip for now** - continue onboarding

If the user chooses to add an account, call the `add_account` tool rather than sending a settings link. If the user skips or finishes adding an account, show the onboarding menu again.

## Draft a first email

Invite the user to try:

> draft an email to hello+mcp@superhuman.com saying hi.

Explain that Superhuman Mail can create a draft, and the user can edit it in the client or send it as-is after reviewing. Never send without explicit approval.

When the user asks to draft, use the Superhuman Mail drafting tool available in the client. Prefer creating a draft over sending directly. After the draft is created or the user skips, show the onboarding menu again.

## Ask questions of the inbox

Explain that the user can ask natural-language questions across email and calendar. If the client supports buttons or quick replies, show these example questions as selectable buttons:

- **When is my next flight?**
- **Show me emails from Rahul Vohra**
- **Show me all the details of my trip to California - hotel, flight, and transit info**

If the client does not support buttons, list the same examples as plain text and invite the user to copy or adapt one.

For broad or multi-email questions, use the Superhuman Mail query/search tools available in the client and synthesize the answer with source email details when useful. After answering, show the onboarding menu again.

## Tune tool approval settings

Only include this step if the client has configurable tool approval or permission defaults. If the client does not expose this capability, skip the step without mentioning it.

Tell the user they can reduce repetitive approvals by changing their default tool settings. Recommend:

- Set most Superhuman Mail read, search, draft, label, archive, and calendar tools to always allow when they are comfortable.
- Keep sending email as an approval-required action. If the client offers an allow-but-ask or require-permission mode, recommend that for send.

Because instructions are client-specific, identify the current client and give the correct path if known. If unknown, say where users typically find this: the client's settings for MCP tools, connectors, integrations, or tool permissions. After this guidance, show the onboarding menu again.

## Use Superhuman in Gmail & Outlook, and apps

Explain that Superhuman Mail also works outside this client.

### Gmail and Outlook

Tell the user they can use Superhuman inside Gmail and Outlook with:

- Auto Labels in the sidebar.
- Auto Drafts for emails labeled Respond, so they can wake up to drafts that are contextually aware of their inbox and calendar.
- Skip Inbox / auto-archive settings for selected email types.

Give the relevant settings links:

- General Superhuman Mail settings: `https://superhuman.com/mail/settings`
- Auto Archive settings: `https://superhuman.com/mail/settings/archive`
- Draft personalization settings: `https://superhuman.com/mail/settings/personalization`

Mention that these settings are specific to each email account, so each account can have different settings.

### Desktop and mobile apps

Tell the user they can also use Superhuman's desktop and mobile apps. Send them to `https://mail.superhuman.com/` to get started. After this guidance, show the onboarding menu again.

## Create or update a calendar event

Invite the user to try a calendar action, such as:

> create an event with so and so tomorrow at 2pm

Ask for any missing details before creating or updating an event, such as attendee email address, title, timezone, duration, calendar, or whether to send invites. Use the Superhuman Mail calendar tool available in the client after the user confirms enough details. After the event is created or updated, or the user skips, show the onboarding menu again.

## Watch video tutorials for more ideas

Let the user know there's a Superhuman Mail MCP YouTube tutorial series with more tips and ideas for getting the most out of the Superhuman Mail MCP:

`https://www.youtube.com/playlist?list=PLY7LUN30OXmM`

Mention this is a good option if they'd rather watch a walkthrough than read, or want inspiration beyond the onboarding menu. After sharing the link, show the onboarding menu again.

## Closing

End by asking what they want to do next. Offer two or three concrete choices instead of an open-ended prompt when possible.
