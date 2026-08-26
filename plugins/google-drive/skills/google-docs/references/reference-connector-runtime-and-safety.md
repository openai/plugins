# Connector Runtime And Safety

When to read: for non-meeting structural writes, template-preserving edits, recovery, or any connector creation/edit workflow whose safety rules are not fully covered by a task-specific fast-path reference.

## Runtime Attachment

1. Confirm the target working doc URL and attach to that exact doc through the available Google Docs connector/app tools; for connector-native creation, use the create response as the new target identity. Do not leave work on a stale or different document.
2. This plugin runs in a blind Codex local-plugin environment. Use Google Docs connector/app tools directly for document reads and writes.
3. Do not use code-mode bridge writes, nested Codex connector writes, browser-only edits, or local helper scripts as the normal write path for this skill.
4. Browser Use, visible-tab checks, cursor placement, screenshots, and live browser-rendered page scans are unavailable and must not be required for success.
5. Reuse the current resolved target document id and `tabId` when available, but re-confirm them before writes.
6. Avoid repeated speculative attach or probe loops when a known document id and `tabId` can be reused.
7. Treat target document identity as a hard precondition for connector writes.
8. If the task uses source Docs, Slides, Slack, search results, or any other source material, re-confirm the destination Google Doc identity before writing.
9. Establish connector capability from evidence, not assumption. Missing convenience wrappers or an inconvenient table target are not proof that the Google Docs connector is read-only or unavailable.

## Direct Structure Planning

Use connector readback as the source of truth.

Default workflow:

1. Call the narrowest connector read that still exposes the needed structure.
2. Use full `get_document` for tabs, headings, paragraph indexes, text styles, paragraph styles, tables, lists, smart chips, and building-block-like regions.
3. Record compact working notes from the response before writing: document id, URL, `revisionId`, tab id, target section ranges, paragraph element ranges, table coordinates, style anchors, chip element types, and list state.
4. Compose request objects directly from those notes and the examples in `reference-direct-request-composition.md`.
5. Use connector reads again after writes, after source/destination switching, after a connector error, when another user may have edited the doc, or when the previous read lacks a field required for a safe write.

Do not replace structure readback with Drive `fetch`, plain-text export, or HTML export. Those surfaces are useful only for separate export/verification tasks after the connector-visible structure is understood.

Do not use exact text range searches as the primary way to target chip display text or repeated sections. Chip display text can appear in `get_document` element properties even when exact-text helpers do not return a useful range.

If the connector response is too large to reason over directly, do not invent a local parsing script during the edit. Narrow the next connector read to the relevant tab, section, paragraph range, table, or exact non-chip anchor, then continue from connector-visible indexes.

## Target-Document Invariant

1. If the agent is using the Google Docs connector to create or modify document content, the connector-visible document id and `tabId` must match the intended target before the write happens.
2. It is not enough that the URL was logged earlier or the title looks right.
3. Target confirmation goes stale after source gathering, switching between documents or document tabs, connector errors, or runtime reset.
4. Apply the target-document guard before each write batch. Re-read `reference-foreground-guard.md` only when the rule is unclear or target identity changed.
5. End-state matters too: final readback must prove the intended destination document contains the intended edits.

## Section Targeting Before Writes

1. Before each edit pass, resolve the target section, paragraph, table, or cell from current connector readback.
2. State or record the exact section name, range, table number, row, and column before writing when useful.
3. For repeated headings or repeated labels, prefer a range bounded by neighboring unique structure over a global text match.
4. Before final handoff, re-read the edited area from the connector rather than relying on saved offsets.

## Required Write-Batch Check

Before every connector write batch:

1. Confirm the intended working doc URL.
2. Confirm the connector-visible document id and `tabId` when applicable.
3. Confirm the current `revisionId` if using `write_control.requiredRevisionId`.
4. Resolve the target range or structural anchor from connector readback.
5. Review the request array for index shifts, tab ids, destructive ranges, and unsupported approximations.
6. Only then issue the connector write batch.

## Safety And Recovery

1. Resolve destructive write ranges from current connector data, or from a fresh read if the current data is stale.
2. Confirm the first and last paragraphs in the target span before deleting or replacing.
3. Prefer one section-sized write pass followed by verification over large speculative rewrites.
4. If formatting drift appears after a write, patch locally instead of redoing the full section.
5. If edits land in the wrong place, stop and re-resolve ranges instead of applying more corrective writes blindly.
6. When a task mixes text and figures, stabilize the text structure first. Do not interleave speculative image insertion with unfinished body edits in the same area.
7. If the connector is available, keep the text path connector-first and use only connector-supported figure insertion paths.
8. If the connector is unavailable, this blind plugin cannot safely create or edit the live Google Doc. Stop and report the runtime constraint instead of inventing a browser-only fallback.
9. Do not accept a shadow draft or external file as a substitute for editing the intended document unless the user explicitly approves that substitution.
10. Prefer the highest-quality connector-verified stable state over the most feature-complete unverified state.
11. For template-fill tasks, preserve the template's canonical output shape. If the destination is a table-based or form-like template, a prose rewrite in plain document form is not an acceptable fallback unless the user explicitly asked for it.
12. If connector editing inside a template becomes unstable, recover within the template shape: use a fresh copy if needed, then smaller verified edits, but do not switch the deliverable into a different structure and still call it complete.
13. Do not treat one failed connector insert into an empty-looking container as proof that the connector path is blocked. Re-resolve the structure, confirm the exact target container, try a minimal verified write, and only then escalate to a narrower recovery path.
14. If connector metadata feels ambiguous around an empty target area, assume this is a targeting problem first, not a platform impossibility. Slow down, re-read the structure, and verify a single-cell or single-block pilot write before changing workflows.
15. Do not hand off a side file, backup draft, or alternate prose version as the primary deliverable just because the canonical document structure became harder to edit. Preserve the destination format unless the user explicitly approves a format change.
16. Do not describe expected runtime constraints as blockers if a viable connector completion path still exists. If the connector is missing, stop and explain that this blind plugin has no browser fallback.
17. Favor workflow discipline over recovery cleverness. A single clean path with early verification is better than a large recovery tree.
18. Do not describe the connector as read-only unless a write-capability check in the current session failed in a way that specifically establishes read-only behavior. If no connector writes were even attempted, you do not know that it is read-only.
19. For structured template tasks, keep connector targeting failures separate from rendered-layout uncertainty. Do not infer visual success or failure without connector evidence.

## Template And Tabs

1. If a referenced doc is a template, create a copy before any edits.
2. If a doc contains tabs, carry the resolved `tabId` through every relevant call.
