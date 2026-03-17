# Slack mrkdwn Quick Reference

Use this reference when a Slack draft needs exact mrkdwn syntax.

## Slack Formatting (mrkdwn)

Slack uses its own markup syntax, `mrkdwn`, rather than standard Markdown.

| Format | Syntax |
| --- | --- |
| Bold | `*text*` |
| Italic | `_text_` |
| Strikethrough | `~text~` |
| Inline code | `` `code` `` |
| Code block | `` ```text``` `` |
| Quote | `> text` |
| Link | `<https://example.com|label>` |
| User mention | `<@U123456>` |
| Channel mention | `<#C123456>` |
| Bulleted list | `- item` |
| Numbered list | `1. item` |

## Usage Notes

- Use `*bold*` for heading-like standalone lines such as `*Next steps*`.
- Prefer `-` bullets for short updates and `1.` lists only when order matters.
- Avoid `@here` and `@channel` unless the user explicitly wants a broad mention.
