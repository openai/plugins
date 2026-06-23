# Agent Browser Workflows

Use the host agent browser with Replay Chromium selected by `AGENT_BROWSER_EXECUTABLE_PATH`.

## Standard Interaction Loop

```bash
export AGENT_BROWSER_EXECUTABLE_PATH="$HOME/.replay/runtimes/Replay-Chromium.app/Contents/MacOS/Chromium"
export RECORD_ALL_CONTENT='1'
export RECORD_REPLAY_VERBOSE='1'
```

Then drive the browser through the host browser API:

1. Open the target URL in the agent browser.
2. Take a DOM snapshot or screenshot.
3. Interact with stable locators or visible UI.
4. Re-snapshot after DOM changes or navigation.
5. Close the tab/session when done.
6. Run `replayio upload-all || replayio upload` if you need the Replay URL before reporting.

## Debugging And Inspection

Capture console messages and visual state after reproducing an issue. In Browser-plugin hosts:

```js
console.log(await tab.playwright.domSnapshot());
console.log(await tab.dev.logs({ levels: ["error", "warn"], limit: 100 }));
await nodeRepl.emitImage(await tab.screenshot({ fullPage: false }));
console.log(await tab.playwright.evaluate(() => ({
  href: location.href,
  title: document.title,
  localStorage: { ...localStorage },
  sessionStorage: { ...sessionStorage },
})));
```

Use Replay analysis tools only after the recording has uploaded and direct browser output is not enough to explain the issue.
