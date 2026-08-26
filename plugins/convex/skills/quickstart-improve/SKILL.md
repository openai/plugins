---
name: quickstart-improve
description: "Send THIS Codex session's transcript to the Convex quickstart backend for an AI post-mortem that improves the whole system (runbook, bootstrap, skills). TRIGGER when the user runs $quickstart-improve, or after a quickstart build says 'send feedback', 'report how that went', or 'help improve the quickstart'."
license: Apache-2.0
---

# Send session for review ($quickstart-improve)

Ships the current Codex session transcript to anteater's `/review` endpoint, which
runs an AI post-mortem and returns concrete findings to improve the runbook /
bootstrap / skills. The user's text after `$quickstart-improve` is an optional note
about how the run went (pass it as `--idea`).

Run it (QB_HARNESS=codex tells the helper to read the Codex transcript):
```bash
curl -fsSL "https://basic-anteater-667.convex.site/send-transcript" \
  | QB_HARNESS=codex bash -s -- --idea "<the user's note, or the app idea>"
```

Read the output:
- `REVIEW_DONE status=done` → summarize for the user: overall `outcome` + `summary`, then the top findings by `severity` (each: `title` → `target` → `suggestedFix`), then the `wins`. Keep it about the *system*, never paste back secrets (the helper already redacts).
- `REVIEW_PENDING` → it was submitted; the review is still running. Tell the user it's queued (the printed `/review/<id>` can be re-checked).
- `REVIEW_NO_TRANSCRIPT` / `REVIEW_TRANSCRIPT_TOO_SMALL` → no Codex transcript found; tell the user.
- `REVIEW_UPLOAD_FAILED` → the endpoint was unreachable (network/sandbox) — report it.
