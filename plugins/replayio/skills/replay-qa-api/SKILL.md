---
name: "replay-qa-api"
description: "Use when calling Replay QA's REST API directly from Codex. Covers bearer-token setup, Replay recording prerequisites, project creation from Replay recordings or target URLs, polling, bug retrieval, journeys, test runs, explorations, and fix workflow discipline."
---

# Replay QA API

Use the Replay QA REST API directly when a task needs Replay QA analysis.
This skill is instructions-only: do not use Replay MCP tools, Codex apps, or plugin hooks as substitutes for Replay QA REST API calls.

## Replay.io Skill Prerequisite

Before making any Replay QA API call, make sure the `replayio` skill in this same Codex plugin bundle has been loaded and applied for the current session.

If setup is unknown, load `../replayio/SKILL.md` first and follow it before continuing. In particular, verify:

- `REPLAY_API_KEY` is mapped from `SECRET_REPLAY_API_KEY` when available.
- `REPLAY_QA_API_KEY` is mapped from `SECRET_REPLAY_QA_API_KEY`.
- `AGENT_BROWSER_EXECUTABLE_PATH` points at Replay Chromium.
- `RECORD_ALL_CONTENT` and `RECORD_REPLAY_VERBOSE` are set.
- Any Replay recording referenced by Replay QA has uploaded or has a concrete recording UUID.

Do not proceed with project creation or polling if this prerequisite is unknown. Load and apply the `replayio` skill first, then return to this skill.

## Authentication

Replay QA API tokens are bearer tokens that start with `lqa_`. Generate one in Replay QA Settings and store it as `SECRET_REPLAY_QA_API_KEY` when the host supports project secrets. Map it before calling the API:

```bash
if [ -z "${REPLAY_QA_API_KEY:-}" ] && [ -n "${SECRET_REPLAY_QA_API_KEY:-}" ]; then
  export REPLAY_QA_API_KEY="$SECRET_REPLAY_QA_API_KEY"
fi

test -n "${REPLAY_QA_API_KEY:-}"
```

Never print the token.

## Base URL

Use:

```bash
export REPLAY_QA_API_BASE="${REPLAY_QA_API_BASE:-https://qa.replay.io/api/v1}"
```

All requests need:

```bash
-H "Authorization: Bearer $REPLAY_QA_API_KEY"
-H "Content-Type: application/json"
```

## Create A Project From A Replay Recording

Use this when you already have an uploaded Replay recording UUID. When `recording_id` is present, `target_url` is not required.

Required input:

- `name`: clear project or scenario name.
- `recording_id`: Replay recording UUID.
- `instructions`: include the raw test source URL when possible and the exact failure message or stack.
- `webhook_url`: optional.

```bash
curl -sS -X POST "$REPLAY_QA_API_BASE/projects" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "S01 - checkout total does not update",
    "recording_id": "00000000-0000-0000-0000-000000000000",
    "instructions": "Analyze this Replay recording of a failing automated test.\n\nTest source:\nhttps://raw.githubusercontent.com/org/repo/refs/heads/branch/tests/checkout.spec.ts\n\nError:\nExpected checkout total to update after clicking Confirm Checkout.\n\nExplain the root cause and the code change that should fix it."
  }'
```

Save the returned project `id` and project `url` if present. If only an id is returned, the overview URL is:

```text
https://qa.replay.io/p/:projectId/overview
```

## Create A Project For Live App Exploration

Use this when Replay QA should explore an app URL instead of analyzing one recording.

```bash
curl -sS -X POST "$REPLAY_QA_API_BASE/projects" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Todo app smoke exploration",
    "target_url": "https://example.com",
    "instructions": "Explore the main user flows and report correctness, polish, and UX bugs."
  }'
```

Optional fields supported by the API include `webhook_url`, `backend_recording_url`, `backend_log_url`, `logins`, and `design_document`. Only include credentials when the user explicitly provided them for this app.

## Poll Project Status

Poll every 30 seconds until the project reports completion. Status can be returned either at the top level or under `project.status`, so inspect the response shape instead of assuming one field.

```bash
PROJECT_ID="..."

curl -sS "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/status" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

For long-running analysis, report that Replay QA is still processing rather than guessing from partial data.

## Fetch Bugs

List bugs:

```bash
curl -sS "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/bugs?page_size=100" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

Filter open bugs:

```bash
curl -sS "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/bugs?status=open&page_size=100" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

Fetch full bug detail:

```bash
BUG_ID="..."

curl -sS "$REPLAY_QA_API_BASE/bugs/$BUG_ID" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

Use bug detail as the source of truth for root cause, reproduction steps, expected behavior, actual behavior, severity, and Replay evidence.

## Journeys, Test Runs, And Explorations

List journeys:

```bash
curl -sS "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/journeys?page_size=100" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

List test runs:

```bash
curl -sS "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/test-runs?page_size=100" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

List explorations:

```bash
curl -sS "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/explorations?page_size=100" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY"
```

Start another exploration:

```bash
curl -sS -X POST "$REPLAY_QA_API_BASE/projects/$PROJECT_ID/explorations" \
  -H "Authorization: Bearer $REPLAY_QA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Re-test checkout, saved drafts, and navigation edge cases.",
    "agent_count": 3
  }'
```

`agent_count` must be between 1 and 10.

## Fix Workflow Discipline

When Replay QA is used to guide fixes:

1. Create Replay QA projects for all selected failing recordings before fixing.
2. Wait for each selected project to finish analysis.
3. Fetch full bug details.
4. Group bugs by root cause and affected file.
5. Patch only from Replay QA evidence plus the current source file.
6. Re-run the app or tests with Replay agent-browser recording enabled.
7. Report project IDs, bug IDs, recording IDs, files changed, and remaining undiagnosed failures.

Do not infer a root cause from source reading while Replay QA analysis is still pending.

## API Reference

Key endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/projects` | List projects |
| `POST` | `/projects` | Create a recording-analysis or app-exploration project |
| `GET` | `/projects/{project_id}` | Get project details |
| `GET` | `/projects/{project_id}/status` | Get project summary/status |
| `GET` | `/projects/{project_id}/bugs` | List bugs |
| `GET` | `/bugs/{bug_id}` | Get bug detail |
| `GET` | `/projects/{project_id}/journeys` | List journeys |
| `GET` | `/projects/{project_id}/test-runs` | List test runs |
| `GET` | `/projects/{project_id}/explorations` | List explorations |
| `POST` | `/projects/{project_id}/explorations` | Start a new exploration |

OpenAPI spec:

```text
https://qa.replay.io/api/v1/openapi.json
```

## Reporting

When reporting Replay QA API work, include:

- Project ID and URL, if returned.
- Recording ID or target URL analyzed.
- Status response summary.
- Bug count and each bug ID inspected.
- Root cause and recommended fix from bug detail.
- Any 401, 404, rate limit, or incomplete-analysis blocker.
