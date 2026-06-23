# Agent Browser Reference

Configure the browser executable before opening the host agent browser:

```bash
export AGENT_BROWSER_EXECUTABLE_PATH="$HOME/.replay/runtimes/Replay-Chromium.app/Contents/MacOS/Chromium"
export RECORD_ALL_CONTENT='1'
export RECORD_REPLAY_VERBOSE='1'
```

The Replay plugin no longer expects normal browser work to go through `playwright-cli`. Use the host agent browser or browser tool directly, with Replay Chromium selected by `AGENT_BROWSER_EXECUTABLE_PATH`.

## Basics

The exact API is host-specific. In Browser-plugin hosts, use the selected `iab` browser:

```js
await browser.nameSession("replay run");
if (typeof tab === "undefined") {
  globalThis.tab = await browser.tabs.new();
}
await tab.goto("https://example.com");
console.log(await tab.playwright.domSnapshot());
await nodeRepl.emitImage(await tab.screenshot({ fullPage: false }));
await tab.close();
```

## Inspection

Use direct agent-browser inspection before reaching for Replay analysis tools:

- DOM snapshots for locator ground truth.
- Console and developer logs from the browser API.
- Screenshots for visual state.
- Read-only page evaluation for state such as title, URL, local storage, and session storage.
- Host-provided network and cookie tools when available.

Use Replay analysis tools only after the recording has uploaded and direct browser output is not enough to explain the issue.
