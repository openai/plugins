---
name: "replayio"
description: "Use when you need to record or inspect an agent browser run in Replay, test a local app with the host agent browser using Replay Chromium, or use the Replay MCP server for deeper debugging of an uploaded recording."
---

# Replay Browser + Agent Browser + Replay MCP

Use the host **agent browser** with Replay Chromium whenever you need a recorded browser session. Do **not** drive the app with `playwright-cli` for normal browser work.

Before opening the agent browser, point it at Replay Chromium:

```bash
export AGENT_BROWSER_EXECUTABLE_PATH=/path/to/chromium
```

For the standard Replay install on macOS, the executable is usually:

```bash
export AGENT_BROWSER_EXECUTABLE_PATH="$HOME/.replay/runtimes/Replay-Chromium.app/Contents/MacOS/Chromium"
```

Recordings upload through the plugin's stop/idle hook as a safety net. If you need the Replay URL before reporting results, close the agent browser tab/session and force an upload with `replayio upload-all || replayio upload`.

## Direct Agent Browser First

Use the host agent browser directly for live browser control and first-pass inspection. Do not reach for the Replay MCP server just to click, type, read DOM state, inspect console output, check network requests, take screenshots, read storage, or check cookies.

Use the Replay MCP server only after a recording has uploaded and you need deeper Replay-specific debugging, such as inspecting execution history, narrowing a time-travel debugging problem, or investigating details that the live agent browser cannot answer.

In Browser-plugin hosts, follow the Browser skill and use the selected `iab` browser. Typical direct checks look like this:

```js
await browser.nameSession("replay repro");
if (typeof tab === "undefined") {
  globalThis.tab = await browser.tabs.new();
}
await tab.goto(URL);
console.log(await tab.playwright.domSnapshot());
console.log(await tab.title());
console.log(await tab.url());
console.log(await tab.dev.logs({ levels: ["error"], limit: 50 }));
await nodeRepl.emitImage(await tab.screenshot({ fullPage: false }));
```

Use the browser API's Playwright/DOM/vision helpers for interaction; the key restriction is to avoid the external `playwright-cli` path.

## Close-When-Done Contract

After you finish a test run, **before reporting the outcome to the user**, close the agent browser tab or session using the host browser API.

In Browser-plugin hosts:

```js
await tab.close();
```

Then, if you need the uploaded Replay URL before your response, run:

```bash
replayio upload-all || replayio upload
```

Do not leave a browser open at the end of your turn. If you forget, the stop/idle hook will attempt to upload pending recordings as a safety net, but you may not see the resulting Replay URL before responding.

**Exception - authentication wall:** If you must stop because the user needs to sign in interactively (see below), **do not** close the browser just to retry or reset. Leaving the session open preserves the headed window they should use; closing can end the recording before login is done.

## Web App Authentication Walls

If you hit a **login or authorization barrier** you cannot complete with automation alone - for example a sign-in page, SSO redirect, MFA step, CAPTCHA, or consent screen - **do not** close the browser and loop on reopen/retry. That drops useful context and trains failing retries.

Instead:

1. **Stop driving the browser** for this turn.
2. Briefly report what blocked you (URL or visible state).
3. Ask the user to complete sign-in **in the existing headed browser session** when that is possible (or give them the exact URL if they must use another window).
4. Ask them to **send another message when they are logged in** so you can attach to the same session or continue from an authenticated page.
5. End your turn there; resume only after they confirm.

Do not treat an auth wall as a generic error to brute-force by closing and reopening the Replay browser.

## The Reliable Path

1. Verify the Replay runtime exists and the CLI is logged in.
2. Resolve the Replay Chromium executable path.
3. Export `AGENT_BROWSER_EXECUTABLE_PATH` to that executable **before** opening the agent browser.
4. Set both `RECORD_ALL_CONTENT='1'` and `RECORD_REPLAY_VERBOSE='1'`.
5. If Replay QA will be used, map `REPLAY_QA_API_KEY` from `SECRET_REPLAY_QA_API_KEY` when available.
6. If testing a local app, start it first and verify the actual reachable URL.
7. Drive and inspect the page directly with the host agent browser, not `playwright-cli`.
8. Use fresh DOM snapshots or screenshots after navigation and major UI changes.
9. Close the agent browser tab/session when done.
10. Run `replayio upload-all || replayio upload` if you need the uploaded Replay URL before reporting results.

## Prerequisites

Check Replay first:

```bash
replayio info
replayio whoami
```

If Replay is missing, verify `npx` exists:

```bash
command -v npx >/dev/null 2>&1
```

If `npx` is missing, stop and ask the user to install Node.js/npm. If `npx` exists, install Replay:

```bash
npx @replayio/replay install
```

If not logged in, authenticate:

```bash
replayio login
```

## Replay MCP Authentication (Private Recordings)

Replay MCP calls are authorized **per user**. If tools return **Access denied**, you are usually not authenticated to Replay **as the same account that owns the recording**.

- **Cursor**: open **Settings -> MCP**, select the **Replay** server, and complete **Sign in / Connect / Reconnect** so Cursor can finish the **OAuth** flow (including **dynamic client registration** when supported). Stay on `https://dispatch.replay.io/mcp` (do not swap in unrelated endpoints unless Replay explicitly instructs you to).
- **Other hosts**: follow that host's MCP authentication mechanism (some environments use API keys or separate app connectors instead of OAuth).

## Agent Browser Executable Path

The agent browser should launch Replay Chromium through `AGENT_BROWSER_EXECUTABLE_PATH`:

```bash
export AGENT_BROWSER_EXECUTABLE_PATH="$HOME/.replay/runtimes/Replay-Chromium.app/Contents/MacOS/Chromium"
```

Verify the executable exists before browser work:

```bash
test -x "$AGENT_BROWSER_EXECUTABLE_PATH"
```

Do not configure `.playwright/cli.config.json` for normal runs, and do not switch back to `playwright-cli` just to select the browser executable. If the agent browser was already running before the environment variable was set, restart or reconnect the agent browser so it picks up the Replay Chromium path.

## Recording Environment

Set recording flags before the run:

```bash
export RECORD_ALL_CONTENT='1'
export RECORD_REPLAY_VERBOSE='1'
```

Some hosts or hooks may set these automatically. If in doubt, set them explicitly before opening the agent browser.

## Replay QA Environment

If Replay QA will be used, map the Replay QA API secret before calling the Replay QA API skill:

```bash
if [ -z "${REPLAY_QA_API_KEY:-}" ] && [ -n "${SECRET_REPLAY_QA_API_KEY:-}" ]; then
  export REPLAY_QA_API_KEY="$SECRET_REPLAY_QA_API_KEY"
fi

test -n "${REPLAY_QA_API_KEY:-}"
```

Never print the token. Replay QA tokens start with `lqa_`.

## Local App Check

If testing a local app:

1. Start the app first.
2. Use the URL the dev server actually prints.
3. Do not assume the requested port is the final port. Some dev servers auto-increment when the port is busy.
4. Verify reachability before opening the browser.

```bash
curl -I http://127.0.0.1:4323/todos
```

If a localhost request fails even though a process is clearly listening, you may be in a restricted sandbox. Rerun the browser and reachability checks outside the sandbox.

## Reliable Agent Browser Workflow

```bash
export AGENT_BROWSER_EXECUTABLE_PATH="$HOME/.replay/runtimes/Replay-Chromium.app/Contents/MacOS/Chromium"
export RECORD_ALL_CONTENT='1'
export RECORD_REPLAY_VERBOSE='1'
```

Then use the host agent browser. In Browser-plugin hosts:

```js
const URL = "http://127.0.0.1:4323/todos";
await browser.nameSession("replay todos");
if (typeof tab === "undefined") {
  globalThis.tab = await browser.tabs.new();
}
await tab.goto(URL);
console.log(await tab.playwright.domSnapshot());
await tab.playwright.getByLabel("New todo", { exact: false }).fill("Buy milk", {});
await tab.playwright.getByRole("button", { name: "Add" }).click({});
console.log(await tab.playwright.domSnapshot());
console.log(await tab.dev.logs({ levels: ["error"], limit: 50 }));
await nodeRepl.emitImage(await tab.screenshot({ fullPage: false }));
await tab.close();
```

Use `domSnapshot()` before constructing locators, and again after DOM changes or navigation.

## Attach To An Already-Open Agent Browser

If the agent browser is already running, attach through the host browser API instead of starting a new CLI session.

In Browser-plugin hosts:

```js
const tabs = await browser.tabs.list();
console.log(tabs);
globalThis.tab = tabs.length > 0 ? await browser.tabs.get(tabs[0].id) : await browser.tabs.new();
```

## Analyzing Uploaded Recordings

First inspect the live run with direct agent-browser APIs. Once a recording has uploaded, use the `replay` MCP server tools only when you need deeper Replay-specific debugging beyond direct browser output. Codex connects to Replay through the app configured in `.app.json`, which provides app-level authentication and exposes the Replay MCP tools.

## Replay MCP Widgets

Replay MCP tool calls may return both text `content` for the model and `structuredContent` for an MCP Apps widget. In MCP Apps-aware hosts, prefer the rendered widget for dense debugging views such as Logpoint output, React component trees, Redux actions, network details, screenshots, source code, profiles, and exception stacks.

When a widget is visible, use it as evidence instead of restating every detail in prose. Use follow-up actions or related Replay MCP tools when the widget points to a specific point, source, component, request, or stack frame that needs deeper inspection.

## Recording Uploads

The plugin's stop/idle hook attempts to upload pending Replay recordings automatically at the end of the turn. Because agent-browser interactions do not necessarily run through a shell close command, force an upload yourself when you need the Replay URL before reporting results:

```bash
replayio upload-all || replayio upload
```

If you need to inspect the upload state yourself:

```bash
replayio list
```

## Troubleshooting

- If the agent browser does not record, verify `AGENT_BROWSER_EXECUTABLE_PATH` points at Replay Chromium and restart/reconnect the agent browser after setting it.
- If `test -x "$AGENT_BROWSER_EXECUTABLE_PATH"` fails, run `npx @replayio/replay install` or fix the path.
- If no Replay URL is available before you respond, close the agent browser tab/session and run `replayio upload-all || replayio upload`.
- If the app is on localhost, verify the exact URL with `curl -I` before opening the browser.
- If the requested port was busy, use the actual port printed by the dev server.
- Prefer direct agent-browser inspection (DOM snapshots, console logs, screenshots, storage, cookies, network tools when available) before using the Replay MCP server.
- If Replay authentication fails, run `replayio login` or reconnect the relevant Replay app/integration.
- If Replay QA returns 401, verify `REPLAY_QA_API_KEY` is set from `SECRET_REPLAY_QA_API_KEY` and starts with `lqa_`.
- If the **application under test** requires interactive login, follow **Web App Authentication Walls** - do not close-and-retry the browser session in a loop.

## References

- Agent browser reference: `references/cli.md`
- Workflow notes: `references/workflows.md`
- [Replay docs](https://docs.replay.io)
