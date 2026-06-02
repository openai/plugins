# PDF Generation Paths

## What Problem This Solves

This reference helps choose the best PDF workflow for a given report or automation task.

## When to Use It

Use this when deciding between HTML-first PDF rendering and lower-level PDF construction.

## Key Takeaways

- HTML plus browser PDF is often the most reliable path for styled reports.
- Lower-level PDF libraries are best when the layout is not naturally HTML-first.

## Common Mistakes

- Using low-level PDF primitives for content that would be easier to express in HTML and CSS.
- Leaving page breaks, headers, and figure slot rules undefined.

## Adjacent Skills

- `../SKILL.md`

## Source Links

- [Playwright Page PDF](https://playwright.dev/docs/api/class-page#page-pdf)
- [pdf-lib](https://pdf-lib.js.org/)
