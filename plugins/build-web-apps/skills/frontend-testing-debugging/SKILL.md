---
name: frontend-testing-debugging
description: "Use when testing, debugging, or making targeted improvements to rendered frontend apps through the Build Web Apps or web dev plugin: local dev servers, UI regressions, interaction bugs, console errors, responsive layout, and visual QA. Check whether the Browser plugin is available and use it first when it is; otherwise use regular Playwright with the recorded reason."
---

# Frontend Testing Debugging

## Invocation Contract

This skill should work from normal user prompts. Do not require the user to spell out Browser routing, screenshots, report shape, or fallback policy.

Use this skill when the user asks to use the Build Web Apps plugin, web dev plugin, frontend dev plugin, or frontend testing/debugging skill for a rendered frontend change, test, or bug investigation.

Examples that should trigger this full workflow:

- `please make an improvement to the web dashboard transaction search area and use the web dev plugin`
- `use the frontend dev plugin to polish this dashboard`
- `debug this UI with the Build Web Apps plugin`
- `test this localhost app and fix the broken interaction`

From a brief prompt, infer the target surface from the repo, currently open app/browser URL, nearby files, or running dev server. If the target URL is unclear, inspect the repo scripts and running local ports before asking the user.

For any code change to a rendered frontend surface, do the validation loop by default:

1. Identify the target flow.
2. Choose the Browser path below.
3. Make the smallest useful edit.
4. Validate the rendered behavior.
5. Reply with the QA final response report.

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

## QA Final Response Report

For any non-trivial rendered UI validation run, write the final response like a QA engineer verifying a code change. The response should make it easy for the user or PR reviewer to understand what changed, what was tested, what evidence proves it, and what remains untested.

Use this shape:

- **Summary**: one or two bullets explaining the user-visible change and whether QA passed.
- **Environment**: URL, viewport(s), Browser availability classification, and fallback reason if Playwright was used.
- **Changes Verified**: files or surfaces changed, plus the specific user-facing behavior expected.
- **Checks**: a pass/fail table for page identity, blank-page check, framework overlay check, console health, screenshot evidence, and interaction proof.
- **Interaction Loop**: exact interaction path tested, including the control or workflow exercised and the observed state change.
- **Evidence**: describe the screenshot evidence in the QA sections, then place the actual screenshots together at the end of the response as consecutive images. Include as many screenshots as are useful to prove the relevant before, after, interaction, responsive, error, or fixed states.
- **Commands / Browser APIs**: list the key command and Browser API sequence used, without dumping noisy logs.
- **Remaining Risk**: untested viewports, flows, browsers, data states, or known limitations.

If issues were found, lead with **Findings** before the summary. Each finding should include what the user sees, reproduction steps, screenshot/DOM/console evidence, likely owner or file when known, and the fix made or remaining blocker.

When using Browser screenshots that should be shown to the user, emit or display the screenshot through the Browser runtime so it can be referenced in chat. When using Playwright screenshots, save them outside the repo and reference them in chat. Include multiple screenshots when they help verify distinct states or flows.

Do not interleave screenshots throughout the written report. Put a short **Screenshots** section at the very end, and make it a consecutive image gallery with one image per line. Add short labels only when they clarify the state, for example `Before`, `After`, `Filtered results`, `Empty state`, or `Mobile`.

Do not create separate HTML reports by default. Only create a standalone report file when the user explicitly asks for one, and write it outside the repo unless the user explicitly asks for committed artifacts.

Do not write reports, screenshots, traces, or temporary scripts into the repo unless the user explicitly asks for committed artifacts.

## Related Skills

- Use `frontend-app-builder` when the task is design creation, redesign, or fidelity to an accepted concept.
- Use `react-best-practices` after meaningful React/Next.js component edits.
- Do not invoke Image Gen for ordinary debugging. Use it only when the task requires creating or revising visual assets, or when `frontend-app-builder` is already driving a concept-to-implementation fidelity loop.

## Final Response

Use the QA final response report format above. Keep it concise, but include enough concrete evidence that a PR reviewer can trust the validation without rerunning it immediately.

If Browser was absent and Playwright was used, end by suggesting that the user install the Browser plugin for a better frontend development experience with in-app navigation, screenshots, DOM snapshots, console logs, and interaction validation.
