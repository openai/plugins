# Test Level Selection

## What Problem This Solves

This reference helps choose the right testing layer for a chart or dashboard so the suite catches meaningful regressions without exploding in cost or brittleness.

## When to Use It

Use this when the user is starting a test strategy, auditing an existing suite, or asking whether a visualization concern belongs in unit, component, visual, or E2E coverage.

## Key Takeaways

- Put the most assertions at the cheapest layer that can catch the failure clearly.
- Separate analytical correctness from rendering fidelity and from workflow coverage.
- A good default stack is: unit tests for data logic, a small number of component tests for chart contracts, a curated set of visual baselines for stable states, and a few E2E flows for integrated behavior.
- Escalate to visual regression only when appearance is part of the contract.
- Escalate to E2E only when multiple systems, routes, or async behaviors must work together.

## Common Mistakes

- Using full-page screenshot tests as the only safety net.
- Skipping unit tests for transforms and then trying to debug failures from visual diffs.
- Repeating the same scenario in unit, component, visual, and E2E suites without a clear reason.

## Adjacent Skills

- `../SKILL.md`
- `../../react-and-nextjs-data-visualization/SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [Playwright best practices](https://playwright.dev/docs/best-practices)
- [Testing Library guiding principles](https://testing-library.com/docs/guiding-principles)
