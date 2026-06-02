# Data Mocking and Fixtures

## What Problem This Solves

This reference explains where to mock chart data, how to structure fixtures, and when to use synthetic or real examples for visualization QA.

## When to Use It

Use this when the user is deciding whether to mock fetches, loaders, hooks, or chart props, or when the suite needs fixtures that cover more than the happy path.

## Key Takeaways

- Mock at the network, repository, or loader boundary so the transformation and rendering stack remains real.
- Keep at least three fixture classes: canonical, edge-case, and stress or density.
- Edge fixtures should include nulls, zeros, negatives, ties, long labels, outliers, timezone boundaries, empty series, and missing categories where relevant.
- Use seeded synthetic data when scale or shape matters more than business meaning.
- Keep production-derived fixtures small, sanitized, and versioned only when they represent an important regression history.
- Make fixture ownership explicit so tests do not silently share mutable data.

## Common Mistakes

- Mocking inside scale or rendering code and then accidentally proving only the mock.
- Reusing one happy-path dataset for every chart state.
- Hand-authoring enormous fixtures when a tiny seeded generator would express the same risk more clearly.

## Adjacent Skills

- `../SKILL.md`
- `../../typescript-data-visualization-engineering/SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [Mock Service Worker](https://mswjs.io/docs/)
- [Playwright mocking](https://playwright.dev/docs/mock)
