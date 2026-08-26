---
name: box
description: >
  Foundation skill for working with Box. Use this whenever the user mentions
  Box — authentication and MCP/CLI setup, choosing between MCP/CLI/REST,
  rate-limit and pacing guidance, troubleshooting Box errors
  (401/403/404/409/429), or working with Box MCP tools (files, search,
  collaboration, AI, hubs, doc gen). Start here for any Box task even if the
  user doesn't name a specific tool, then route to the right reference.
---

# Box

## Overview

This is the foundation skill for any Box task. It routes a request to the right
tool (MCP, CLI, or REST) and the right domain reference. Use it to:

- Inventory which Box tooling is available (MCP → CLI → REST) and set up what is missing.
- Choose the correct tool for an operation using the tool selection table below.
- Identify which reference file covers the user's domain.
- Diagnose common Box errors (401/403/404/409/429, missing content, wrong actor).

Always start here—even when the user does not name a specific tool—then route
to the deeper reference.

## Route The Request

### Tool selection

First confirm which resources you actually have access to and are able to access. After, use this table to pick the right tool for the operation:

| Operation type | Prefer | Rationale |
| --- | --- | --- |
| Most agent workflows (search, AI, content management, metadata, hubs) | MCP | Structured I/O, concurrent-safe, covers the common cases |
| Bulk operations (batch moves, folder trees, batch metadata) | CLI | Compact output, `--fields` filtering, full API surface without requiring manual REST auth |
| Verification and smoke tests | CLI | Reproducible, user can copy-paste commands |
| Operations outside MCP scope | CLI | Full API coverage |
| Last-resort fallback when MCP is unavailable and CLI is unavailable or not an option | Direct REST | Only after explicit user confirmation and REST auth setup guidance |
| Building application code (SDK/REST endpoints, webhook handlers) | SDK or REST in code | Not agent tooling — write code the user ships |

The table above is the single source of truth for tool selection — the sections below reference it rather than restate it. When tooling is unavailable, escalate in this order: guide the user through MCP setup first, then CLI setup, and only fall back to direct REST as a last resort after the user explicitly confirms REST fallback is acceptable.

### Domain routing

Choose which reference files to read based on what the user needs:

| If the user needs... | Read first | Pair with | Minimal verification |
| --- | --- | --- | --- |
| Uploads, folders, listings, downloads, previews, moves, or metadata | `references/content-workflows.md` | `references/auth-and-setup.md` | Read-after-write call using the same actor |
| Sharing, collaborations (users/groups), or shared links | `references/collaboration.md` | `references/content-workflows.md`, `references/auth-and-setup.md` | List collaborations before and after changes |
| Finding files or folders (keyword, folder name, metadata search) | `references/mcp-search.md` | `references/auth-and-setup.md` | Confirm item details before acting |
| Box AI Q&A, summarization, extraction, or document retrieval | `references/ai-and-retrieval.md` | `references/auth-and-setup.md` | Retrieval-quality check before answer formatting |
| Box Hubs — creating, curating, or querying a hub | `references/mcp-hubs.md` | `references/ai-and-retrieval.md`, `references/auth-and-setup.md` | Confirm hub items after changes |
| Document generation from templates (Doc Gen) | `references/mcp-doc-gen.md` | `references/content-workflows.md`, `references/auth-and-setup.md` | Confirm template and destination before batch |
| Organizing, reorganizing, or batch-moving files across folders; bulk metadata tagging; migrating folder structures | `references/bulk-operations.md` | `references/content-workflows.md`, `references/auth-and-setup.md`, `references/ai-and-retrieval.md` | Inventory source, verify move count matches plan |
| Event-driven ingestion, new-file triggers, or webhook debugging | `references/webhooks-and-events.md` | `references/auth-and-setup.md`, `references/troubleshooting.md` | Signature check plus duplicate-delivery test |
| 401, 403, 404, 409, 429, missing content, or wrong-actor bugs | `references/troubleshooting.md` | `references/auth-and-setup.md` | Reproduce with the exact actor, object ID, and endpoint |
| Unsure which workflow applies | `references/workflows.md` | `references/auth-and-setup.md` | Choose the smallest Box object/action pair first |

## MCP

The Box MCP server is the default tooling for agent workflows. It provides structured I/O, is concurrent-safe, and covers the common cases (search, Box AI, content management, metadata, hubs). See the tool selection table above for when to prefer it over CLI or REST.

### Availability check

- Call `who_am_i`. If it fails, try `mcp_auth`.
- If auth still fails, read `references/auth-and-setup.md` for MCP setup steps and walk the user through setup before considering other tooling.
- Record whether MCP is available.

### Tool availability and documentation

The updated/maintained list of Box MCP tools is documented at https://docs.box.com/en/box-mcp/tools. If an expected tool is missing or unavailable, see `references/troubleshooting.md` (MCP tool missing section) for diagnostic steps and admin-console enablement.

### General guidelines

- When listing folder contents, paginate if needed and summarize large directories rather than printing every item.
- Prefer reading file details with `get_file_details` before operating on a file — it confirms the file exists and shows current state.
- For exploratory or demo usage, prefer working within a dedicated folder rather than operating across the user's entire Box account.
- Avoid granting or assuming broad enterprise-wide access. Default to least-privilege — only access the folders and files the task requires.

### Usage

The Box MCP capabilities are documented in focused reference files. Use the domain routing table above to pick the right one for the task:

| MCP category | Reference |
| --- | --- |
| Files, folders, uploads, downloads, previews, metadata | `references/content-workflows.md` |
| Search (keyword, folder, metadata) | `references/mcp-search.md` |
| Collaborations (users/groups) and shared links | `references/collaboration.md` |
| Box AI Q&A, extraction, structured metadata extraction, and agents | `references/ai-and-retrieval.md` |
| Box Hubs creation, item management, and hub-level Q&A | `references/mcp-hubs.md` |
| Box Doc Gen templates and document generation batches | `references/mcp-doc-gen.md` |

## CLI / REST API

The tool selection table above governs when to reach for the CLI or direct REST. Both rank below MCP: CLI for operations outside MCP's scope or that need compact, field-filtered output, and direct REST only as a last-resort fallback after explicit user confirmation.

### CLI

#### Availability check

- Run `box users:get me --json`. Record whether CLI is available.
- If CLI is unavailable, walk the user through CLI setup and retry `box users:get me --json`.

#### Usage

- Read `references/box-cli.md` for CLI-first auth, smoke-test commands, safe verification patterns, and serial-execution constraints.

### REST API

Direct REST is the last-resort fallback per the tool selection table — only when MCP and CLI are both unavailable or declined.

Building application code (SDK/REST endpoints, webhook handlers) the user ships is a separate case — that is code you write, not agent tooling. Prefer an official Box SDK when one already exists in the codebase or for the target language.

#### Confirmation and setup

- Never use direct REST fallback silently. Ask the user for explicit confirmation before proceeding.
- Guide the user through token setup (`BOX_ACCESS_TOKEN`) and safe auth handling before issuing requests.
- Keep access tokens, client secrets, private keys, and webhook secrets in env vars or the project's secret manager.

#### Usage

- Read `references/rest-calls.md` for direct REST fallback patterns, auth setup, and safe request templates.

## Workflow

Follow these steps in order when coding against Box.

0. Inventory available Box tooling using the availability checks in the **MCP** and **CLI / REST API** sections above: check MCP first (`who_am_i` / `mcp_auth`), then CLI (`box users:get me --json`), and record which are available. When tooling is missing, follow the escalation order from **Route The Request** (MCP setup → CLI setup → REST after explicit confirmation). If the task is building application code (adding SDK endpoints, webhook handlers), tooling availability is secondary — proceed to step 1.
1. Inspect the repository for existing Box auth, SDK or HTTP client, env vars, webhook handlers, Box ID persistence, and tests.
2. Determine the acting identity before choosing endpoints: connected user, enterprise service account, app user, or platform-provided token.
3. Select the tool using the tool selection table and identify the domain reference using the domain routing table above.
4. Confirm whether the task changes access or data exposure. Shared links, collaborations, auth changes, large-scale downloads, and broad AI retrieval all need explicit user confirmation before widening access or scope.
5. Read the reference for the selected tool (MCP, CLI, or REST) and the domain reference identified by the tool selection and domain routing tables above. See the **References** section at the end of this file for the full annotated list of what each file covers.
6. Implement the smallest end-to-end flow that proves the integration works.
7. Add a runnable verification step. Prefer the repository's tests first; otherwise use native Box CLI commands when CLI is available and authenticated. Use direct Box REST verification only as a last resort after explicit user confirmation.
8. Summarize the deliverable with auth context, Box IDs, env vars or config, and the exact verification command or test.

## Guardrails


- Preserve the existing Box auth model unless the user explicitly asks to change it.
- Check the current official Box docs before introducing a new auth path, changing auth scope, or changing Box AI behavior.
- Prefer an official Box SDK when the codebase already uses one or the target language has a maintained SDK. Otherwise use direct REST calls with explicit request and response handling.
- In agent workflows, do not jump straight to direct REST when MCP or CLI can be set up. Offer setup guidance for MCP first and CLI second before proposing REST fallback.
- Never use direct REST fallback silently. Ask the user for explicit confirmation before proceeding with REST calls.
- Keep access tokens, client secrets, private keys, and webhook secrets in env vars or the project's secret manager.
- Distinguish file IDs, folder IDs, shared links, metadata template identifiers, and collaboration IDs.
- Treat shared links, collaborations, and metadata writes as permission-sensitive changes. Confirm audience, scope, and least privilege before coding or applying them.
- Require explicit confirmation before widening external access, switching the acting identity, or retrieving more document content than the task truly needs.
- When a task requires understanding document content, use Box AI as the first method attempted — it operates server-side and requires no downloads. See `references/ai-and-retrieval.md` for the full preference order and fallback chain.
- Pace Box AI calls at least 1–2 seconds apart. For bulk classification, use the sample-first strategy in `references/bulk-operations.md`.
- Avoid downloading file bodies or routing content through external AI pipelines when Box-native methods (Box AI, search, metadata, previews) can answer the question server-side.
- Request only the fields the application actually needs, and persist returned Box IDs instead of reconstructing paths later.
- Run Box CLI commands strictly one at a time — see `references/box-cli.md` for details. For bulk work, default to CLI and use REST only after MCP/CLI setup attempts fail or the user explicitly confirms REST fallback.
- Make webhook and event consumers idempotent. Box delivery and retry paths can produce duplicates.
- Keep AI retrieval narrow for search and Q&A tasks. Search and filter first, then retrieve only the files needed for the answer. This does not apply to Box AI classification — when classifying documents, Box AI should be tried first per the content-understanding guardrail above.
- Do not use `box configure:environments:get --current` as a routine auth check — it can print sensitive environment details.

## Verification

- Prefer the repository's existing tests or app flows when they already cover the changed Box behavior.
- If no better verification path exists, prefer native `box` CLI commands when `box` is installed and authenticated.
- Use direct REST verification only after confirming MCP and CLI are unavailable or not an option and after the user explicitly approves REST fallback.
- For REST fallback, guide the user through token setup (`BOX_ACCESS_TOKEN`) and safe auth handling before issuing requests.
- Confirm CLI auth with `box users:get me --json`.
- Verify mutations with a read-after-write call using the same actor, and record the object ID.
- For webhooks, test the minimal happy path, duplicate delivery, and signature failure handling.
- For AI flows, test retrieval quality separately from answer formatting.

For example smoke-check commands, see `references/box-cli.md` (Common verification commands).

## Deliverable

The final answer should include:

- Acting auth context used for the change
- Box object type and IDs touched
- Env vars, secrets, or config expected by the integration
- Files or endpoints added or changed
- Exact verification command, script, or test path
- Any permission-sensitive assumptions that still need confirmation

## References

- `references/content-workflows.md`: files and folders — uploads, downloads, previews, folder trees, moves, metadata; MCP tools + CLI/REST patterns
- `references/collaboration.md`: sharing and access — collaborator roles, shared links, external-sharing rules; MCP tools + CLI/REST patterns
- `references/mcp-search.md`: finding content — keyword, folder-name, and metadata search via MCP
- `references/ai-and-retrieval.md`: Box AI and retrieval — Q&A, extraction, agents, content understanding preference order; MCP tools + CLI commands
- `references/mcp-hubs.md`: Box Hubs — creation, item management, hub-level Q&A via MCP
- `references/mcp-doc-gen.md`: Box Doc Gen — template registration and document generation via MCP
- `references/bulk-operations.md`: organizing files at scale — batch moves, folder hierarchy creation, serial execution, and rate-limit handling
- `references/auth-and-setup.md`: auth path selection, MCP server setup, SDK vs REST choice, existing-codebase inspection, and current Box doc anchors
- `references/box-cli.md`: CLI-first local auth, smoke-test commands, and safe verification patterns
- `references/rest-calls.md`: direct REST fallback patterns, auth setup, and safe request templates
- `references/webhooks-and-events.md`: webhook setup, event-feed usage, idempotency, and verification
- `references/workflows.md`: quick workflow router when the task is ambiguous
- `references/troubleshooting.md`: common failure modes and a debugging checklist
