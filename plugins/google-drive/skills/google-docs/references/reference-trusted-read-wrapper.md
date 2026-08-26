# File-Backed Trusted Read

When to read: before the first write to an existing Google Doc, including template fills, reference adaptations, meeting-notes insertion, post-import repairs, and ordinary edits whose surrounding structure has not yet been inspected.

## Purpose

Use the checked-in bridge at `host/docs-trusted-read-file-bridge.mjs` for the initial full read. The bridge calls authenticated connector tools, runs the trusted control detector, persists the rich responses and normalized document content in a thread-scoped workspace, and returns only compact control awareness and immutable file metadata.

This read is advisory. It does not mutate the document, gate writes, select a route, or prove that an opaque private-use marker is a dropdown. It makes protected controls visible without putting the complete connector response into model context.

## Data Boundary

Keep the data plane on disk:

- `document-result.json`: complete raw `get_document` response for exact scripts or exceptional structural inspection.
- `dropdown-result.json`: revision-aligned provider dropdown response when that capability exists.
- `control-inventory.json`: all protected controls, locators, containers, native elements, and warnings.
- `document-outline.json`: normalized paragraph records with styles, lists, tables, links, and inline control bindings.
- `document-text.md`: model-readable content with explicit protected-control annotations.

Return only the compact manifest to model context. Do not transport connector results with `text()`, `apply_patch`, temporary JSON assembled by the model, or a model-authored detector.

## Load The Bridge

Load the checked-in bridge once per code-mode session. The byte check prevents truncated source from being evaluated.

```js
const bridgeKey = `google_docs_trusted_read_bridge:${SKILL_DIR}`;
let bridgeSource = load(bridgeKey);
if (!bridgeSource) {
  const bridgePath = `${SKILL_DIR}/host/docs-trusted-read-file-bridge.mjs`;
  const metadata = await tools.exec_command({
    cmd: `/usr/bin/wc -l -c < '${bridgePath}'`,
    workdir: SKILL_DIR,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 1000,
  });
  const [reportedLines, expectedBytes] = metadata.output.trim().split(/\s+/).map(Number);
  if (metadata.exit_code !== 0 || !Number.isInteger(reportedLines) ||
      !Number.isInteger(expectedBytes) || reportedLines < 0 || expectedBytes < 1) {
    throw new Error("Could not stat the Docs trusted-read bridge");
  }
  const lineCount = Math.max(1, reportedLines + 1);
  const ranges = Array.from(
    { length: Math.ceil(lineCount / 200) },
    (_, index) => [index * 200 + 1, Math.min(lineCount, (index + 1) * 200)],
  );
  const chunks = await Promise.all(ranges.map(([start, end]) =>
    tools.exec_command({
      cmd: `/usr/bin/sed -n '${start},${end}p' '${bridgePath}'`,
      workdir: SKILL_DIR,
      login: false,
      yield_time_ms: 30000,
      max_output_tokens: 14000,
    })
  ));
  if (chunks.some((chunk) => chunk.exit_code !== 0)) {
    throw new Error("Could not load every Docs trusted-read bridge chunk");
  }
  bridgeSource = chunks.map((chunk) => chunk.output).join("");
  const actualBytes = encodeURIComponent(bridgeSource)
    .replace(/%[0-9A-F]{2}/gi, "_")
    .length;
  if (actualBytes !== expectedBytes) throw new Error("Could not load the complete Docs trusted-read bridge");
  store(bridgeKey, bridgeSource);
}

const trustedReadBridge = new Function(
  `${bridgeSource.replace(/^\s*export\s+/gm, "")}\n` +
  "return { executeDocsTrustedReadToFiles };",
)();
```

Do not emit `bridgeSource` or rich connector results with `text()`.

## Invoke The Read

Use one unique output directory per target revision and tab:

```js
const trustedRead = await trustedReadBridge.executeDocsTrustedReadToFiles({
  documentId: TARGET_DOCUMENT_ID,
  tabId: TARGET_TAB_ID,
  outputDir: `${WORKSPACE}/bridge/trusted-read-01`,
  workspaceRoot: WORKSPACE,
  skillRoot: SKILL_DIR,
  tools,
});
text(JSON.stringify(trustedRead));
```

Pass exactly one of `documentId` or `documentUrl`. `tabId` is optional. Do not use ordinary `import()` inside the standard execution isolate, evaluate the raw wrapper separately, recreate the detector, or stage connector responses through `store()` and `apply_patch`.

The compact result always includes:

- target identity and revision;
- `dropdownMetadata` availability and revision status;
- `controlAwareness` counts, native-element counts, preservation guidance, and affected-paragraph count;
- advisory `warnings`;
- exact paths, byte counts, and hashes for every persisted artifact.

When `controlAwareness.hasProtectedControls` is true, the model is already on notice before writing. Read `files.document_text.path` for content and `files.control_inventory.path` for exact protected ranges when needed.

## Read Document Content

Read `document-text.md`, not the rich connector response, for normal authoring. Its paragraphs include connector indexes, heading/list/table metadata, native links and chips, and annotations such as:

```text
⟦PROTECTED: opaqueTemplateControl/copy-only@750:751 U+E907 — preserve this control and its containing structure⟧
```

For a document that fits comfortably in context, read the returned file directly:

```js
const normalizedContent = await tools.exec_command({
  cmd: `/bin/cat -- '${trustedRead.files.document_text.path}'`,
  workdir: WORKSPACE,
  login: false,
  yield_time_ms: 30000,
  max_output_tokens: 30000,
});
if (normalizedContent.exit_code !== 0) throw new Error("Could not read normalized Google Docs content");
text(normalizedContent.output);
```

The trusted-read call itself returns only the compact manifest; this explicit file read is the point where normalized document content enters model context.

For a small document, read the normalized file once. For a large document, search it and read bounded sections. Read `document-outline.json` when machine-readable paragraph records are useful. Inspect `document-result.json` only when a required field is absent from the normalized artifacts.

Do not insert the displayed `⟦PROTECTED_CONTROL ...⟧` token into Google Docs. It is an on-disk annotation, not document content.

## Interpretation

- `dropdownControl`: provider metadata identified a native dropdown and exposed exact readable semantics.
- `opaqueTemplateControl`: a private-use marker or unclassified control was found. Preserve it and its containing structure, but do not claim dropdown semantics.

The bridge always requires `getDocument`. When `getDocumentDropdowns` is available, it reads dropdown metadata from the same document revision and upgrades matching controls. When that capability is unavailable, fails, or returns a mismatched revision, unmatched private-use elements remain opaque copy-only controls.

Continue with direct connector writes unless the user asks to create a dropdown, replace its options, or change its selected value; those intents still use exact dropdown code mode.

## Follow-Up Reads

After the initial file-backed read, use the narrowest normal connector read needed for targeting and verification. Re-run the bridge into a new immutable output directory when the target document or tab changes, the initial context becomes stale, or work moves near controls outside the scanned scope.
