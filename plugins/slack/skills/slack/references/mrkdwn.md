# Slack mrkdwn Quick Reference

Use this file when a Slack draft needs exact formatting instead of generic prose.

## Headings

Slack has no true heading syntax. Emulate headings with a bold standalone line:

- `*Launch status*`
- `*Next steps*`

## Lists

Use hyphen bullets for short scannable lists:

- `- First item`
- `- Second item`

Use numbered lists only when order matters:

- `1. First step`
- `2. Second step`

## Links

Use Slack link syntax when the URL should be hidden behind readable text:

- `<https://example.com|Design spec>`

Use raw URLs only when the destination itself is the important detail.

## Mentions

Use mentions deliberately:

- `@name` for a direct callout when the connector returns the display form
- `@here` only for active participants when urgency is justified
- `@channel` only for broad announcements that clearly warrant interrupting everyone

If the audience is unclear, draft the message without a mass mention first.

## Quotes

Use block quotes for a short excerpt or prior decision:

- `> Shipping moved to Thursday.`

Do not quote long passages when a summary would be easier to scan.

## Code

Use inline code for short literals:

- `` `npm run build` ``
- `` `customer_id` ``

Use fenced code blocks for longer commands or snippets:

```text
```bash
npm run build
```
```

## Message Hygiene

- Keep the most important point in the first line.
- Prefer one clear ask over several loosely related asks.
- Split long updates into short paragraphs or bullets.
- Keep links near the sentence that explains why they matter.
- If a draft is announcement-length, end with the explicit next action or owner.
