# Next.js Client and Server Boundaries

## What Problem This Solves

This reference helps decide which parts of a visualization belong in Server Components and which belong in Client Components.

## When to Use It

Use this when the application uses Next.js and chart code may touch browser-only APIs, measurements, pointer events, or heavy charting libraries.

## Key Takeaways

- Keep data fetching and framing layout on the server when possible.
- Move interactive charts, container measurement, browser-only APIs, and imperative libraries into Client Components.
- Make client-only boundaries explicit rather than letting hydration problems surface accidentally.

## Common Mistakes

- Pulling an entire route into the client when only the chart widget needs browser APIs.
- Importing browser-only chart runtimes in server-safe code paths.

## Adjacent Skills

- `../SKILL.md`
- `../../reports-pdfs-and-slide-automation/SKILL.md`

## Source Links

- [Next.js Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)
