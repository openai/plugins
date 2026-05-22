# Lazy Loading, SSR, and Bundle Strategy

## What Problem This Solves

This reference covers how React and Next.js apps should load charting code without bloating initial render paths or causing SSR breakage.

## When to Use It

Use this when the chart runtime is heavy, browser-only, below the fold, or not required for the initial route render.

## Key Takeaways

- Use dynamic loading when a chart is not needed on first paint or should avoid SSR.
- Treat heavy visualization libraries as candidates for route-level or component-level splitting.
- Balance bundle savings against interaction delay and hydration complexity.

## Common Mistakes

- Loading large charting runtimes on every route by default.
- Disabling SSR everywhere instead of isolating the actual browser-only component.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [Next.js lazy loading](https://nextjs.org/docs/app/guides/lazy-loading)
- [Next.js dynamic imports lesson](https://nextjs.org/learn-pages-router/seo/improve/dynamic-import-components)
