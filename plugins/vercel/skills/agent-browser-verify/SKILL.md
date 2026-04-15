---
name: agent-browser-verify
description: Automated browser verification for dev servers. Triggers when a dev server starts to run a visual gut-check with agent-browser — verifies the page loads, checks for console errors, validates key UI elements, and reports pass/fail before continuing.
metadata:
  priority: 2
  docs:
    - "https://openai.com/index/introducing-codex/"
  pathPatterns: []
  bashPatterns:
    - '\bnext\s+dev\b'
    - '\bnpm\s+run\s+dev\b'
    - '\bpnpm\s+dev\b'
    - '\bbun\s+run\s+dev\b'
    - '\byarn\s+dev\b'
    - '\bvite\s*(dev)?\b'
    - '\bnuxt\s+dev\b'
    - '\bvercel\s+dev\b'
  promptSignals:
    phrases:
      - "check the page"
      - "check the browser"
      - "check the site"
      - "is the page working"
      - "is it loading"
      - "blank page"
      - "white screen"
      - "nothing showing"
      - "page is broken"
      - "screenshot the page"
      - "take a screenshot"
      - "check for errors"
      - "console errors"
      - "browser errors"
      - "page is stuck"
      - "page is hanging"
      - "page not loading"
      - "page frozen"
      - "spinner not stopping"
      - "page not responding"
      - "page won't load"
      - "page will not load"
      - "nothing renders"
      - "nothing rendered"
      - "ui is broken"
      - "screen is blank"
      - "screen is white"
      - "app won't load"
    allOf:
      - [check, page]
      - [check, browser]
      - [check, site]
      - [blank, page]
      - [white, screen]
      - [console, errors]
      - [page, broken]
      - [page, loading]
      - [not, rendering]
      - [page, stuck]
      - [page, hanging]
      - [page, frozen]
      - [page, timeout]
    anyOf:
      - "page"
      - "browser"
      - "screen"
      - "rendering"
      - "visual"
      - "spinner"
      - "loading"
    minScore: 6
---

# Dev Server Verification with agent-browser

**You MUST verify the dev server with agent-browser after starting it.** Do not assume the page works just because the dev server process started. Many issues (blank pages, hydration errors, missing env vars, broken imports) are only visible in the browser. Run this verification before continuing with any other work:

## Quick Verification Flow

```bash
# 1. Open the dev server
agent-browser open http://localhost:3000
agent-browser wait --load networkidle

# 2. Screenshot for visual check
agent-browser screenshot --annotate

# 3. Check for errors
agent-browser eval 'JSON.stringify(window.__consoleErrors || [])'

# 4. Snapshot interactive elements
agent-browser snapshot -i
```

## Verification Checklist

Run each check and report results:

1. **Page loads** — `agent-browser open` succeeds without timeout
2. **No blank page** — snapshot shows meaningful content (not empty body)
3. **No error overlay** — no Next.js/Vite error overlay detected
4. **Console errors** — evaluate `document.querySelectorAll('[data-nextjs-dialog]')` for error modals
5. **Key elements render** — snapshot `-i` shows expected interactive elements
6. **Navigation works** — if multiple routes exist, verify at least the home route

## Error Detection

```bash
# Check for framework error overlays
agent-browser eval 'document.querySelector("[data-nextjs-dialog], .vite-error-overlay, #webpack-dev-server-client-overlay") ? "ERROR_OVERLAY" : "OK"'

# Check page isn't blank
agent-browser eval 'document.body.innerText.trim().length > 0 ? "HAS_CONTENT" : "BLANK"'
```

## On Failure

If verification fails:

1. Screenshot the error state: `agent-browser screenshot error-state.png`
2. Capture the error overlay text or console output
3. Close the browser: `agent-browser close`
4. Fix the issue in code
5. Re-run verification (max 2 retry cycles to avoid infinite loops)

## Diagnosing a Hanging or Stuck Page

When the page appears stuck (spinner, blank content after load, frozen UI), the browser is only half the story. Correlate what you see in the browser with server-side evidence:

### 1. Capture Browser Evidence

```bash
# Screenshot the stuck state
agent-browser screenshot stuck-state.png

# Check for pending network requests (XHR/fetch that never resolved)
agent-browser eval 'JSON.stringify(performance.getEntriesByType("resource").filter(r => r.duration === 0).map(r => r.name))'

# Check console for errors or warnings
agent-browser eval 'JSON.stringify(window.__consoleErrors || [])'

# Look for fetch calls to workflow/API routes that are pending
agent-browser eval 'document.querySelector("[data-nextjs-dialog]") ? "ERROR_OVERLAY" : "OK"'
```

### 2. Check Server Logs

After capturing browser state, immediately check the backend:

```bash
# Stream Vercel runtime logs for the deployment
vercel logs --follow

# If using Workflow DevKit, check run status
npx workflow inspect runs
npx workflow inspect run <run_id>

# Check workflow health
npx workflow health
```

### 3. Correlate Browser + Server

| Browser Shows | Server Shows | Likely Issue |
|--------------|-------------|-------------|
| Spinner / loading forever | No recent function invocations | API route not being called — check fetch URL in client code |
| Spinner / loading forever | Function started but no step logs | Workflow step is stuck — add `console.log` at step entry/exit |
| Blank page, no errors | Build succeeded, no runtime errors | Hydration issue or missing data — check SSR vs client rendering |
| Network request pending | 504 Gateway Timeout in logs | Function timeout — increase `maxDuration` or optimize step |
| Console: "Failed to fetch" | OIDC/credential error in logs | Missing `vercel env pull` — run `vercel link && vercel env pull` |
| Error overlay visible | Stack trace in runtime logs | Read the server error — it usually has more detail than the client |

### 4. Fix and Re-verify

After fixing the issue:

```bash
# Re-open and verify the fix
agent-browser open http://localhost:3000
agent-browser wait --load networkidle
agent-browser screenshot after-fix.png
agent-browser eval 'document.body.innerText.trim().length > 0 ? "HAS_CONTENT" : "BLANK"'
agent-browser close
```

## On Success

```bash
agent-browser close
```

Report: "Dev server verified — page loads, no errors detected, key UI elements render correctly."

## Suggest Verification After Implementation

When you finish building or implementing a feature (wrote code, created routes, set up a project), briefly let the user know they can ask you to verify everything works with a browser check. One sentence is enough. Don't force it if only a small fix or question was involved.
