---
name: box-content-api
description: Build and troubleshoot Box integrations for uploads, folders, folder listings, downloads and previews, shared links, collaborations, search, metadata, event-driven automations, and Box AI retrieval flows. Use when Codex needs to add Box APIs or SDKs to an app, wire Box-backed document workflows, organize or share content, react to new files, or fetch Box content for search, summarization, extraction, or question-answering.
---

# Box Content API

## Overview

Implement Box content workflows in application code. Reuse the repository's existing auth and HTTP or SDK stack whenever possible, identify the acting Box identity before coding, and make the smallest end-to-end path work before layering on sharing, metadata, webhooks, or AI.

## Route The Request

| If the user needs... | Primary object | Read first | Pair with | Minimal verification |
| --- | --- | --- | --- | --- |
| Local verification, manual smoke tests, or quick inspection from Codex without app code changes | Current CLI environment | `references/box-cli.md` | `references/auth-and-setup.md` | `scripts/box_cli_smoke.py check-auth` then a read command |
| Uploads, folders, listings, downloads, shared links, collaborations, or metadata | File or folder | `references/content-workflows.md` | `references/auth-and-setup.md` | Read-after-write call using the same actor |
| Organizing, reorganizing, or batch-moving files across folders; bulk metadata tagging; migrating folder structures | File set or folder tree | `references/bulk-operations.md` | `references/auth-and-setup.md`, `references/content-workflows.md`, `references/ai-and-retrieval.md` | Inventory source, verify move count matches plan |
| Event-driven ingestion, new-file triggers, or webhook debugging | Webhook or events feed | `references/webhooks-and-events.md` | `references/auth-and-setup.md`, `references/troubleshooting.md` | Signature check plus duplicate-delivery test |
| Search, document retrieval, summarization, extraction, or Box AI | Search result set or file content | `references/ai-and-retrieval.md` | `references/auth-and-setup.md` | Retrieval-quality check before answer formatting |
| 401, 403, 404, 409, 429, missing content, or wrong-actor bugs | Existing request path | `references/troubleshooting.md` | `references/auth-and-setup.md` | Reproduce with the exact actor, object ID, and endpoint |
| Unsure which workflow applies | Unknown | `references/workflows.md` | `references/auth-and-setup.md` | Choose the smallest Box object/action pair first |

## Workflow

Follow these steps in order when coding against Box.

1. Inspect the repository for existing Box auth, SDK or HTTP client, env vars, webhook handlers, Box ID persistence, and tests.
2. Determine the acting identity before choosing endpoints: connected user, enterprise service account, app user, or platform-provided token.
3. Identify the primary Box object and choose the matching reference from the routing table above.
4. Confirm whether the task changes access or data exposure. Shared links, collaborations, auth changes, large-scale downloads, and broad AI retrieval all need explicit user confirmation before widening access or scope.
5. Read only the matching reference files:
   - Auth setup, actor selection, SDK vs REST: `references/auth-and-setup.md`
   - Box CLI local verification: `references/box-cli.md`
   - Workflow router: `references/workflows.md`
   - Content operations: `references/content-workflows.md`
   - Bulk file organization, batch moves, folder restructuring: `references/bulk-operations.md`
   - Webhooks and events: `references/webhooks-and-events.md`
   - AI and retrieval: `references/ai-and-retrieval.md`
   - Debugging and failure modes: `references/troubleshooting.md`
6. Implement the smallest end-to-end flow that proves the integration works.
7. Add a runnable verification step. Prefer the repository's tests first; otherwise use `scripts/box_cli_smoke.py` when Box CLI is available and authenticated, and `scripts/box_rest.py` as a fallback.
8. Summarize the deliverable with auth context, Box IDs, env vars or config, and the exact verification command or test.

## Guardrails

- Preserve the existing Box auth model unless the user explicitly asks to change it.
- Check the current official Box docs before introducing a new auth path, changing auth scope, or changing Box AI behavior.
- Prefer an official Box SDK when the codebase already uses one or the target language has a maintained SDK. Otherwise use direct REST calls with explicit request and response handling.
- Keep access tokens, client secrets, private keys, and webhook secrets in env vars or the project's secret manager.
- Distinguish file IDs, folder IDs, shared links, metadata template identifiers, and collaboration IDs.
- Treat shared links, collaborations, and metadata writes as permission-sensitive changes. Confirm audience, scope, and least privilege before coding or applying them.
- Require explicit confirmation before widening external access, switching the acting identity, or retrieving more document content than the task truly needs.
- When a task requires understanding document content — classification, extraction, categorization — use Box AI (Q&A, extract) as the first method attempted. Box AI operates server-side and does not require downloading file bodies. Fall back to metadata inspection, previews, or local analysis only if Box AI is unavailable, not authorized, or returns an error on the first attempt.
- Pace Box AI calls at least 1–2 seconds apart. For content-based classification of many files, classify a small sample first to validate the prompt and discover whether cheaper signals (filename, extension, metadata) can sort the remaining files without additional AI calls.
- Avoid downloading file bodies or routing content through external AI pipelines when Box-native methods (Box AI, search, metadata, previews) can answer the question server-side.
- Request only the fields the application actually needs, and persist returned Box IDs instead of reconstructing paths later.
- Run Box CLI commands strictly one at a time. The CLI does not support concurrent invocations and parallel calls cause auth conflicts and dropped operations. For bulk work (organizing, batch moves, batch metadata), default to REST over CLI.
- Make webhook and event consumers idempotent. Box delivery and retry paths can produce duplicates.
- Keep AI retrieval narrow for search and Q&A tasks. Search and filter first, then retrieve only the files needed for the answer. This does not apply to Box AI classification — when classifying documents, Box AI should be tried first per the content-understanding guardrail above.
- Do not use `box configure:environments:get --current` as a routine auth check because it can print sensitive environment details.

## Verification

- Prefer the repository's existing tests, scripts, or app flows when they already cover the changed Box behavior.
- If no better verification path exists, prefer `scripts/box_cli_smoke.py` when `box` is installed and authenticated. Fall back to `scripts/box_rest.py` with `BOX_ACCESS_TOKEN` when CLI auth is unavailable or the task specifically needs direct bearer-token verification.
- Confirm CLI auth with `box users:get me --json` or `scripts/box_cli_smoke.py check-auth`.
- Verify mutations with a read-after-write call using the same actor, and record the object ID.
- For webhooks, test the minimal happy path, duplicate delivery, and signature failure handling.
- For AI flows, test retrieval quality separately from answer formatting.

Example smoke checks:

```bash
python3 scripts/box_cli_smoke.py check-auth
python3 scripts/box_cli_smoke.py get-folder 0 --fields id name item_collection
python3 scripts/box_cli_smoke.py list-folder-items 0 --max-items 20
python3 scripts/box_cli_smoke.py search "invoice" --limit 10
python3 scripts/box_rest.py get-item --item-type folder --item-id 0 --fields id name item_collection
```

## Deliverable

The final answer should include:

- Acting auth context used for the change
- Box object type and IDs touched
- Env vars, secrets, or config expected by the integration
- Files or endpoints added or changed
- Exact verification command, script, or test path
- Any permission-sensitive assumptions that still need confirmation

## References

- `references/auth-and-setup.md`: auth path selection, SDK vs REST choice, existing-codebase inspection, and current Box doc anchors
- `references/box-cli.md`: CLI-first local auth, smoke-test commands, and safe verification patterns
- `references/workflows.md`: quick workflow router when the task is ambiguous
- `references/content-workflows.md`: uploads, folders, listings, downloads, shared links, collaborations, metadata, and file moves
- `references/bulk-operations.md`: organizing files at scale, batch moves, folder hierarchy creation, serial execution, and rate-limit handling
- `references/webhooks-and-events.md`: webhook setup, event-feed usage, idempotency, and verification
- `references/ai-and-retrieval.md`: search-first retrieval, Box AI usage, and external AI guardrails
- `references/troubleshooting.md`: common failure modes and a debugging checklist
- `examples/box-content-api-prompts.md`: example prompts for realistic use cases
