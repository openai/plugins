# Slack Authoring Reference

Use this reference when writing Slack-ready text for these skills.

## Authoring Contract

- Write clean Markdown-style text plus explicit Slack mention syntax.
- The active Slack runtime may convert Markdown into Slack mrkdwn or blocks before sending. Follow the live tool contract if it is more specific than this file.
- Keep Slack-specific mention syntax for users and channels. Use user-group mention syntax only when the runtime can actually resolve the group.

## Common Syntax

| Intent | Preferred authoring |
| --- | --- |
| Strong emphasis | `**text**` in Markdown-converting paths, or the live tool's required bold syntax |
| Emphasis | `*text*` or the live tool's required italic syntax |
| Strikethrough | `~~text~~` |
| Inline code | `` `code` `` |
| Code block | `` ```text``` `` |
| Quote | `> text` |
| Link | `[label](https://example.com)` |
| User mention | `<@U123456>` |
| Channel mention | `<#C123456>` |
| User group mention | `<!subteam^S123456>` |
| Bulleted list | `- item` |
| Numbered list | `1. item` |

## Usage Notes

- Prefer short paragraphs and `-` bullets for Slack posts.
- Use heading-like standalone lines sparingly. Keep them short.
- Do not rely on bare `@name` text for mentions.
- Avoid `@here`, `@channel`, and similar broad notifications unless the user explicitly asked for them.
