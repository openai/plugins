# Avoiding Brittle Over-Testing

## What Problem This Solves

This reference helps the skill trim visualization suites that are expensive, flaky, or full of assertions that do not protect meaningful behavior.

## When to Use It

Use this when a chart test suite is slow, constantly red for low-signal reasons, or packed with snapshots and visual baselines that nobody trusts.

## Key Takeaways

- Do not test the same rule at every layer unless the project has a specific regression history that justifies it.
- Avoid asserting exact tick counts, path strings, inline styles, or generated markup unless that detail is part of the public contract.
- Keep screenshot coverage narrow and intentional; a few trusted baselines beat dozens of noisy ones.
- Trust well-established libraries for their own internals and focus your assertions on your adapters, data contracts, and user-visible behavior.
- Delete or downgrade tests that mostly fail for harmless rendering drift, unrelated theme updates, or timing noise.
- Add stronger fixtures and better determinism before adding more assertions.

## Common Mistakes

- Approving visual baseline churn without understanding what changed.
- Snapshotting every prop combination instead of choosing representative states.
- Treating flaky chart tests as unavoidable rather than as a signal that the boundary or fixture strategy is wrong.

## Adjacent Skills

- `../SKILL.md`
- `../../react-and-nextjs-data-visualization/SKILL.md`
- `../../typescript-data-visualization-engineering/SKILL.md`

## Source Links

- [Playwright retries](https://playwright.dev/docs/test-retries)
- [Testing Library FAQ](https://testing-library.com/docs/dom-testing-library/faq)
