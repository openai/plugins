# Connector Runtime And Safety

When to read: always, before any content edits.

## Runtime Attachment

1. Confirm the target working doc URL and attach to that exact doc through the available Google Docs connector/app tools; do not leave editing work on a stale or different document.
2. This plugin runs in a blind Codex local-plugin environment. Use `node_repl` for source processing or helper code, not for Google Docs connector calls.
3. Connector calls are separate from `node_repl`; do not call Google Docs connector actions from inside `node_repl` or through embedded-runtime helper snippets.
4. Browser Use, visible-tab checks, cursor placement, screenshots, and rendered-page scans are unavailable and must not be required for success.
5. Reuse the current resolved target document id and `tabId` when available, but re-confirm them before writes.
6. Avoid repeated speculative attach or probe loops when a known document id and `tabId` can be reused.
7. Treat target document identity as a hard precondition for connector writes.
8. If the task uses source Docs, Slides, Slack, search results, or any other source material, re-confirm the destination Google Doc identity before writing.
9. Establish connector capability from evidence, not assumption. A missing `node_repl` helper binding or an inconvenient table target is not proof that the Google Docs connector is read-only or unavailable.

## Target-Document Invariant

1. If the agent is using the Google Docs connector to modify a document, the connector-visible document id and `tabId` must match the intended target before the write happens.
2. It is not enough that the URL was logged earlier or the title looks right.
3. A previous target confirmation goes stale after source gathering, switching between documents or document tabs, connector errors, or runtime reset.
4. Re-read `reference-foreground-guard.md` before each write batch when there is any risk that target identity changed.
5. End-state matters too: final readback must prove the intended destination document contains the intended edits.

## Section Targeting Before Writes

1. Before each edit pass, resolve the target section, paragraph, table, or cell through connector reads.
2. State or record the exact section name, range, table number, row, and column before writing when useful.
3. Before final handoff, re-read the edited area from the connector rather than relying on prior offsets.

## Required Write-Batch Check

1. Confirm the intended working doc URL.
2. Confirm the connector-visible document id and `tabId` when applicable.
3. Resolve the target range or structural anchor from fresh connector data.
4. Only then issue the connector write batch.

## Safety And Recovery

1. Resolve destructive write ranges from fresh reads.
2. Confirm the first and last paragraphs in the target span before deleting or replacing.
3. Prefer one section-sized write pass followed by verification over large speculative rewrites.
4. If formatting drift appears after a write, patch locally instead of redoing the full section.
5. If edits land in the wrong place, stop and re-resolve ranges instead of applying more corrective writes blindly.
6. When a task mixes text and figures, stabilize the text structure first. Do not interleave speculative image insertion with unfinished body edits in the same area.
7. If the connector is available, keep the text path connector-first and use only connector-supported figure insertion paths.
8. If the connector is unavailable, this blind plugin cannot safely edit the live Google Doc. Stop and report the runtime constraint instead of inventing a browser-only fallback.
9. Do not accept a shadow draft or external artifact as a substitute for editing the intended document unless the user explicitly approves that substitution.
10. Prefer the highest-quality connector-verified stable state over the most feature-complete unverified state. A well-structured brief with fewer connector-supported visuals is better than a document containing unverifiable or misplaced objects.
13. For template-fill tasks, preserve the template's canonical output shape. If the destination is a table-based or form-like template, a prose rewrite in plain document form is not an acceptable fallback unless the user explicitly asked for it.
14. If connector editing inside a template becomes unstable, recover within the template shape: use a fresh copy if needed, then smaller verified edits, but do not switch the deliverable into a different structure and still call it complete.
15. Do not treat one failed connector insert into an empty-looking container as proof that the connector path is blocked. Re-resolve the structure, confirm the exact target container, try a minimal verified write, and only then escalate to a narrower recovery path.
16. If connector metadata feels ambiguous around an empty target area, assume this is a targeting problem first, not a platform impossibility. Slow down, re-read the structure, and verify a single-cell or single-block pilot write before changing workflows.
17. Do not hand off a side artifact, backup draft, or alternate prose version as the primary deliverable just because the canonical document structure became harder to edit. Preserve the destination format unless the user explicitly approves a format change.
18. Do not describe expected runtime constraints as blockers if a viable connector completion path still exists. If the connector is missing, stop and explain that this blind plugin has no browser fallback.
19. Favor workflow discipline over recovery cleverness. A single clean path with early verification is better than a large recovery tree.
20. If a known-good workflow pattern fits the task, bias toward that pattern immediately instead of re-deciding the strategy after each obstacle.
21. Do not describe the connector as read-only unless a write-capability check in the current session failed in a way that specifically establishes read-only behavior. If no connector writes were even attempted, you do not know that it is read-only.
22. For structured template tasks, keep connector targeting failures separate from rendered-layout uncertainty. Do not infer visual success or failure without connector evidence.

## Template And Tabs

1. If a referenced doc is a template, create a copy before any edits.
2. If a doc contains tabs, carry the resolved `tabId` through every relevant call.
