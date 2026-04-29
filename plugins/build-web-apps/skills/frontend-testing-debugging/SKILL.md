---
name: frontend-testing-debugging
description: "Use when testing or debugging rendered frontend apps: local dev servers, UI regressions, interaction bugs, console errors, responsive layout, and visual QA. Check whether the Browser plugin is available and use it first when it is; otherwise use regular Playwright with the recorded reason."
---

# Frontend Testing Debugging

## Choose The Browser Path

First classify Browser availability:

- **Available**: the Browser plugin and its `browser` skill are listed in the session. Read and follow that skill before any browser action.
- **Absent**: the Browser plugin or `browser` skill is not listed. Use regular Playwright and record `Browser plugin not available`.
- **Invocation failed**: Browser appears available, but the skill/runtime, Node REPL JavaScript setup, tab acquisition, or navigation fails. Treat this as a Browser-path blocker.

Do not use regular Playwright, external Chrome, or shell `open` first when Browser is available.

Only switch from a failed Browser invocation to regular Playwright if the user already allowed fallback or the task explicitly permits non-Browser validation. In that case, report the exact Browser failure and the fallback decision.

## Target Flow

Before browser validation, define the target flow in one sentence:

`The flow under test is: [entry route] -> [user action or state] -> [expected rendered result].`

If the user asked for general smoke testing, use:

`The flow under test is: app loads -> first meaningful screen renders -> primary visible controls respond without runtime errors.`

## Browser Plugin Loop

Run Browser commands through the Node REPL JavaScript tool described by the Browser skill. Do not invent a separate browser setup path. Keep using the same tab binding unless the Browser skill says otherwise.

Required sequence:

1. Load the Browser runtime exactly as the Browser skill instructs.
2. Name the session with `agent.browser.nameSession("...")`.
3. Acquire a tab with `agent.browser.tabs.selected()` or `agent.browser.tabs.new()`.
4. Navigate with `tab.goto(url)`.
5. Run the required checks below.
6. Interact with scoped `tab.playwright` locators or Browser skill interaction APIs.
7. After edits, call `await tab.reload()`, then repeat the checks and the failing interaction.

For each UI-changing action, collect the cheapest proof that the next state is correct: fresh DOM snapshot, visible text/state, URL change, focused control, toast, modal, screenshot, or console log.

### Required Browser Checks

Run these checks before claiming the rendered app works:

1. **Page identity**: `await tab.url()` and `await tab.title()` match the intended page.
2. **Not blank**: `await tab.playwright.domSnapshot()` contains meaningful app content, not an empty shell.
3. **No framework overlay**: the snapshot or screenshot does not show a Next.js, Vite, Webpack, or framework error overlay.
4. **Console health**: `await tab.dev.logs({ levels: ["error", "warn"], limit: 50 })` has no relevant app errors, or each relevant error is explained.
5. **Screenshot evidence**: `await display(await tab.playwright.screenshot({ fullPage: false }))` supports visual claims.
6. **Interaction proof**: at least one target-flow interaction is exercised and followed by a state check.

For visual work, add desktop plus one mobile-sized viewport when practical. For reference-driven work, keep a short mismatch ledger: reference evidence, rendered evidence, fix or intentional deviation.

## Playwright Loop

Use this branch when Browser is not available, or when the user has allowed fallback after a Browser invocation failure.

Use this order:

1. Find scripts in `package.json`.
2. Start the app with the repo's package manager and keep the requested host exact.
3. Prefer the repo's e2e script if present.
4. Otherwise run `pnpm exec playwright test` or the package-manager equivalent when Playwright is configured.
5. If there is no project Playwright workflow, verify Playwright with `pnpm exec playwright --version`, then capture a screenshot with `pnpm exec playwright screenshot <url> /tmp/frontend-check.png`.
6. For deeper debugging, create a small temporary Playwright script outside committed source that opens the URL, captures console errors, screenshots, and runs the target interaction.
7. After edits, rerun the same command or script.

Do not install new browser dependencies unless the task requires it and the user has allowed dependency changes.

## Validation Checklist

- Keep the requested host exact.
- Verify controls update real UI state.
- Check the first viewport before scrolling, plus desktop and one mobile-sized viewport when practical.
- Look for clipping, overlap, unreadable text, wrapping, layout shift, missing assets, z-index issues, scroll traps, stale loading, and broken states.
- For reference-driven work, compare the rendered screenshot against the reference and keep a short mismatch ledger.
- A passing build is not enough when rendered validation was requested.

## HTML Test Report

For any non-trivial rendered UI validation run, create a self-contained HTML report outside the repo so it does not pollute the git diff. Default path:

`/tmp/frontend-test-report-<timestamp>.html`

The report should include:

- Target flow, URL, viewport(s), Browser availability classification, and fallback reason if Playwright was used.
- A pass/fail table for page identity, blank-page check, framework overlay check, console health, screenshot evidence, and interaction proof.
- Findings with reproduction steps, evidence, likely owner or file, fix made, and remaining blocker.
- Screenshots embedded as `data:image/png;base64,...` URLs so the report remains portable even when chat-rendered images fail to load.
- Console errors and warnings, trimmed DOM evidence, and the command or Browser API sequence used.

Do not include credentials, auth tokens, cookies, API keys, secret values, or sensitive personal, financial, medical, legal, or HR data in reports. If visible evidence contains sensitive data, redact it, omit the screenshot or DOM excerpt, and say what was omitted and why.

When using Browser screenshots, convert the screenshot image with `.toBase64()` and embed the returned string in an `<img>` tag. When using Playwright screenshots, base64-encode the saved PNG before writing the report.

Do not write reports, screenshots, traces, or temporary scripts into the repo unless the user explicitly asks for committed artifacts. If a report path is generated, include it in the final response.

## Related Skills

- Use `frontend-app-builder` when the task is design creation, redesign, or fidelity to an accepted concept.
- Use `react-best-practices` after meaningful React/Next.js component edits.
- Do not invoke Image Gen for ordinary debugging. Use it only when the task requires creating or revising visual assets, or when `frontend-app-builder` is already driving a concept-to-implementation fidelity loop.

## Final Response

If issues were found, lead with findings:

- What the user sees.
- Reproduction steps.
- Evidence from screenshot, DOM, console, URL, or logs.
- Likely owner or file, when known.
- Fix made or remaining blocker.

If the flow passed, include URL, viewports, Browser method used or Playwright fallback reason, interactions or visual surfaces tested, console/runtime status, report path, fixes made, and remaining untested surfaces.

If Browser was absent and Playwright was used, end by suggesting that the user install the Browser plugin for a better frontend development experience with in-app navigation, screenshots, DOM snapshots, console logs, and interaction validation.
