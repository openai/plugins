# Export and Product Integration

## What Problem This Solves

This reference covers the product concerns that appear after the chart renders correctly.

## When to Use It

Use this when the chart must support export, embed, SSR, report generation, or application-specific integration constraints.

## Key Takeaways

- Plan export early for charts that must appear in reports or decks.
- Separate chart state from container and control state to make automation easier.
- Prefer deterministic chart dimensions and asset packaging.

## Common Mistakes

- Adding export paths only after shipping the interactive chart.
- Letting app-specific glue dominate chart design.

## Adjacent Skills

- `../SKILL.md`
- `../../reports-pdfs-and-slide-automation/SKILL.md`

## Source Links

- [Playwright Page PDF](https://playwright.dev/docs/api/class-page#page-pdf)
