/*
 * Dependency-free file bridge for Google Docs trusted reads.
 *
 * The bridge invokes authenticated connector reads inside the code-mode isolate,
 * persists rich responses through a private no-echo receiver, and returns only
 * compact control awareness plus immutable file metadata.
 */

const BRIDGE_VERSION = "3.6";
const DEFAULT_MAX_READ_BYTES = 4 * 1024 * 1024;
const DEFAULT_MAX_WRITE_BYTES = 32 * 1024 * 1024;
const DEFAULT_MAX_WRITE_STDIN_CHARS = 512 * 1024;
const MAX_WRITE_STDIN_CHARS = 1024 * 1024;
const DEFAULT_RECEIVER_POLL_ATTEMPTS = 4;
const WRITE_STDIN_RECORD_SEPARATOR = "\u0003";
const RECEIVER_READY_MARKER = "DOCS_BRIDGE_READY";
const RECEIVER_COMMITTED_MARKER = "DOCS_BRIDGE_COMMITTED";
const TRUSTED_SOURCE_SHA256 = new Map([
  ["/host/docs-trusted-read-wrapper.mjs", "c7c1affe5fd3e37924f005c27aa0d6ffbc10e1d2d7ca8fb55d8f38f288ca2ead"],
  ["/runtime/docs-read-normalizer.mjs", "324de06dedc0476c91f7f3d2fe4b15c4cb992ace2afb9e57df498a994020878a"],
]);

export class DocsTrustedReadBridgeError extends Error {
  constructor(message, { path = null, operation = null, cause = null } = {}) {
    super(redactText(message));
    this.name = "DocsTrustedReadBridgeError";
    this.path = path;
    this.operation = operation;
    this.cause = cause;
  }
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function assert(condition, message, details = {}) {
  if (!condition) throw new DocsTrustedReadBridgeError(message, details);
}

function redactText(value) {
  return String(value ?? "")
    .replace(/https?:\/\/[^\s"'<>]+/gi, (url) => /(?:x-goog-|x-amz-|access_token=|signature=)/i.test(url) ? "[EPHEMERAL_URL_REDACTED]" : url)
    .replace(/\b(authorization\s*:\s*bearer|bearer)\s+[A-Za-z0-9._~+\/=:-]+/gi, "$1 [REDACTED]")
    .replace(/\b(x-api-key|api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[:=]\s*["']?[^\s"',;}\]]*/gi, "$1=[REDACTED]");
}

function normalizeAbsolutePath(value, label) {
  assert(typeof value === "string" && value.startsWith("/"), `${label} must be an absolute path`, { path: value, operation: "validate-path" });
  assert(!/[\0\r\n]/.test(value), `${label} contains an invalid path character`, { path: value, operation: "validate-path" });
  const parts = [];
  for (const part of value.split("/")) {
    if (!part || part === ".") continue;
    if (part === "..") parts.pop();
    else parts.push(part);
  }
  return `/${parts.join("/")}`;
}

function assertWithinRoot(path, root, label) {
  const normalizedPath = normalizeAbsolutePath(path, label);
  const normalizedRoot = normalizeAbsolutePath(root, `${label} root`);
  assert(
    normalizedPath === normalizedRoot || normalizedPath.startsWith(`${normalizedRoot}/`),
    `${label} must stay within ${normalizedRoot}`,
    { path: normalizedPath, operation: "validate-path" },
  );
  return normalizedPath;
}

function dirname(path) {
  const index = path.lastIndexOf("/");
  return index <= 0 ? "/" : path.slice(0, index);
}

function joinPath(root, child) {
  assert(typeof child === "string" && child.length > 0 && !child.includes("/"), "Output filename must be one path segment", { path: child, operation: "join-path" });
  return `${root.replace(/\/+$/, "")}/${child}`;
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'"'"'`)}'`;
}

function utf8Bytes(text) {
  if (typeof TextEncoder === "function") return new TextEncoder().encode(text);
  const bytes = [];
  for (let index = 0; index < text.length; index += 1) {
    let codePoint = text.charCodeAt(index);
    if (codePoint >= 0xd800 && codePoint <= 0xdbff && index + 1 < text.length) {
      const next = text.charCodeAt(index + 1);
      if (next >= 0xdc00 && next <= 0xdfff) {
        codePoint = 0x10000 + ((codePoint - 0xd800) << 10) + (next - 0xdc00);
        index += 1;
      }
    }
    if (codePoint <= 0x7f) bytes.push(codePoint);
    else if (codePoint <= 0x7ff) bytes.push(0xc0 | (codePoint >> 6), 0x80 | (codePoint & 0x3f));
    else if (codePoint <= 0xffff) bytes.push(0xe0 | (codePoint >> 12), 0x80 | ((codePoint >> 6) & 0x3f), 0x80 | (codePoint & 0x3f));
    else bytes.push(0xf0 | (codePoint >> 18), 0x80 | ((codePoint >> 12) & 0x3f), 0x80 | ((codePoint >> 6) & 0x3f), 0x80 | (codePoint & 0x3f));
  }
  return Uint8Array.from(bytes);
}

function base64Text(text) {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  const bytes = utf8Bytes(text);
  const chunks = [];
  let chunk = "";
  for (let index = 0; index < bytes.length; index += 3) {
    const first = bytes[index];
    const hasSecond = index + 1 < bytes.length;
    const hasThird = index + 2 < bytes.length;
    const second = hasSecond ? bytes[index + 1] : 0;
    const third = hasThird ? bytes[index + 2] : 0;
    chunk += alphabet[first >> 2];
    chunk += alphabet[((first & 0x03) << 4) | (second >> 4)];
    chunk += hasSecond ? alphabet[((second & 0x0f) << 2) | (third >> 6)] : "=";
    chunk += hasThird ? alphabet[third & 0x3f] : "=";
    if (chunk.length >= 8192) {
      chunks.push(chunk);
      chunk = "";
    }
  }
  if (chunk) chunks.push(chunk);
  return chunks.join("");
}

const SHA256_K = [
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

export function sha256Text(text) {
  const bytes = utf8Bytes(text);
  const paddedLength = Math.ceil((bytes.length + 9) / 64) * 64;
  const padded = new Uint8Array(paddedLength);
  padded.set(bytes);
  padded[bytes.length] = 0x80;
  const bitLength = BigInt(bytes.length) * 8n;
  const view = new DataView(padded.buffer);
  view.setUint32(paddedLength - 8, Number((bitLength >> 32n) & 0xffffffffn));
  view.setUint32(paddedLength - 4, Number(bitLength & 0xffffffffn));
  const state = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
  const words = new Uint32Array(64);
  const rotateRight = (input, shift) => (input >>> shift) | (input << (32 - shift));
  for (let offset = 0; offset < paddedLength; offset += 64) {
    for (let index = 0; index < 16; index += 1) words[index] = view.getUint32(offset + index * 4);
    for (let index = 16; index < 64; index += 1) {
      const s0 = rotateRight(words[index - 15], 7) ^ rotateRight(words[index - 15], 18) ^ (words[index - 15] >>> 3);
      const s1 = rotateRight(words[index - 2], 17) ^ rotateRight(words[index - 2], 19) ^ (words[index - 2] >>> 10);
      words[index] = (words[index - 16] + s0 + words[index - 7] + s1) >>> 0;
    }
    let [a, b, c, d, e, f, g, h] = state;
    for (let index = 0; index < 64; index += 1) {
      const s1 = rotateRight(e, 6) ^ rotateRight(e, 11) ^ rotateRight(e, 25);
      const choice = (e & f) ^ (~e & g);
      const temp1 = (h + s1 + choice + SHA256_K[index] + words[index]) >>> 0;
      const s0 = rotateRight(a, 2) ^ rotateRight(a, 13) ^ rotateRight(a, 22);
      const majority = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (s0 + majority) >>> 0;
      h = g; g = f; f = e; e = (d + temp1) >>> 0; d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
    }
    state[0] = (state[0] + a) >>> 0; state[1] = (state[1] + b) >>> 0;
    state[2] = (state[2] + c) >>> 0; state[3] = (state[3] + d) >>> 0;
    state[4] = (state[4] + e) >>> 0; state[5] = (state[5] + f) >>> 0;
    state[6] = (state[6] + g) >>> 0; state[7] = (state[7] + h) >>> 0;
  }
  return [...state].map((value) => value.toString(16).padStart(8, "0")).join("");
}

function fileArtifact(path, text) {
  const normalized = text.endsWith("\n") ? text : `${text}\n`;
  return {
    path,
    text: normalized,
    metadata: { path, bytes: utf8Bytes(normalized).length, sha256: sha256Text(normalized) },
  };
}

function jsonArtifact(path, value) {
  return fileArtifact(path, JSON.stringify(value, null, 2));
}

function compactError(error) {
  return {
    name: error?.name ?? "Error",
    message: redactText(error?.message ?? String(error)),
    operation: error?.operation ?? null,
  };
}

function moduleFactory(source, exports, label) {
  assert(typeof source === "string" && source.length > 0, `${label} source is empty`, { operation: "evaluate-module" });
  assert(!/^\s*import\s/m.test(source), `${label} must remain dependency-free`, { operation: "evaluate-module" });
  try {
    const executableSource = source
      .replace(/^\s*export\s+\{[^}]*\};?\s*$/gm, "")
      .replace(/^\s*export\s+/gm, "");
    return new Function(`${executableSource}\nreturn { ${exports.join(", ")} };`)();
  } catch (error) {
    throw new DocsTrustedReadBridgeError(`Could not evaluate ${label}: ${error?.message ?? String(error)}`, { operation: "evaluate-module", cause: error });
  }
}

async function loadTrustedModule(fileIO, path, exports, label) {
  const trusted = [...TRUSTED_SOURCE_SHA256].find(([suffix]) => path.endsWith(suffix));
  assert(trusted, `${label} path is not trusted`, { path, operation: "evaluate-module" });
  const source = await fileIO.readText(path);
  assert(sha256Text(source) === trusted[1], `${label} source hash does not match the Google Docs trust catalog`, { path, operation: "evaluate-module" });
  return moduleFactory(source, exports, label);
}

export function createToolBackedFileIO({
  tools,
  workspaceRoot,
  skillRoot,
  receiverPath,
  maxReadBytes = DEFAULT_MAX_READ_BYTES,
  maxWriteBytes = DEFAULT_MAX_WRITE_BYTES,
  maxWriteStdinChars = DEFAULT_MAX_WRITE_STDIN_CHARS,
} = {}) {
  assert(isRecord(tools), "tools is required", { operation: "create-file-io" });
  assert(typeof tools.exec_command === "function", "tools.exec_command is required", { operation: "create-file-io" });
  assert(typeof tools.write_stdin === "function", "tools.write_stdin is required", { operation: "create-file-io" });
  assert(Number.isInteger(maxWriteStdinChars) && maxWriteStdinChars >= 128 && maxWriteStdinChars <= MAX_WRITE_STDIN_CHARS, "maxWriteStdinChars is invalid", { operation: "create-file-io" });
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const skill = normalizeAbsolutePath(skillRoot, "skillRoot");
  const receiver = assertWithinRoot(receiverPath, skill, "receiverPath");

  const validateReadable = (path) => {
    const normalized = normalizeAbsolutePath(path, "read path");
    assert(
      normalized === workspace || normalized.startsWith(`${workspace}/`) || normalized === skill || normalized.startsWith(`${skill}/`),
      "Read path is outside the allowed roots",
      { path: normalized, operation: "read-file" },
    );
    return normalized;
  };
  const validateWritable = (path) => assertWithinRoot(path, workspace, "write path");
  const run = (cmd, maxOutputTokens = 2000) => tools.exec_command({
    cmd,
    workdir: workspace,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: maxOutputTokens,
  });

  const waitForMarker = async ({ initial, sessionId, marker, operation }) => {
    let result = initial;
    let output = String(result?.output ?? "");
    for (let attempt = 0; attempt <= DEFAULT_RECEIVER_POLL_ATTEMPTS; attempt += 1) {
      if (output.includes(marker)) return { result, output };
      if (result?.exit_code !== null && result?.exit_code !== undefined) break;
      result = await tools.write_stdin({ session_id: sessionId, chars: "", yield_time_ms: 1000, max_output_tokens: 1000 });
      output += String(result?.output ?? "");
    }
    throw new DocsTrustedReadBridgeError(`Streaming receiver did not report ${marker}`, { operation });
  };

  const streamText = async (path, text) => {
    const absolute = validateWritable(path);
    const normalized = text.endsWith("\n") ? text : `${text}\n`;
    const bytes = utf8Bytes(normalized).length;
    assert(bytes <= maxWriteBytes, `${absolute} exceeds the bridge writer limit`, { path: absolute, operation: "write-file" });
    const encoded = base64Text(normalized);
    const expectedSha256 = sha256Text(normalized);
    const temporary = `${absolute}.docs-bridge-${expectedSha256.slice(0, 16)}.tmp`;
    const parent = dirname(absolute);
    const mkdir = await run(`/bin/mkdir -p ${shellQuote(parent)}`, 1000);
    assert(mkdir.exit_code === 0, `Could not create bridge output directory: ${mkdir.output ?? ""}`, { path: parent, operation: "write-file" });
    const absent = await run(`/bin/sh -c ${shellQuote('for candidate; do test ! -e "$candidate" || exit 1; done')} sh ${shellQuote(absolute)} ${shellQuote(temporary)}`, 1000);
    assert(absent.exit_code === 0, "Refusing to overwrite a bridge artifact", { path: absolute, operation: "write-file" });
    const start = await tools.exec_command({
      cmd: `/usr/bin/perl ${shellQuote(receiver)} ${shellQuote(absolute)} ${shellQuote(String(bytes))} ${shellQuote(expectedSha256)} ${shellQuote(temporary)}`,
      workdir: workspace,
      login: false,
      tty: true,
      yield_time_ms: 1000,
      max_output_tokens: 1000,
    });
    const sessionId = start?.session_id;
    assert(Number.isInteger(sessionId), "Could not start the no-echo receiver", { path: absolute, operation: "write-file" });
    try {
      await waitForMarker({ initial: start, sessionId, marker: RECEIVER_READY_MARKER, operation: "write-file" });
      const chunkChars = Math.floor((maxWriteStdinChars - 64) / 4) * 4;
      let sequence = 0;
      for (let offset = 0; offset < encoded.length; offset += chunkChars) {
        const frame = `D\t${sequence}\t${encoded.slice(offset, offset + chunkChars)}${WRITE_STDIN_RECORD_SEPARATOR}`;
        const result = await tools.write_stdin({ session_id: sessionId, chars: frame, yield_time_ms: 250, max_output_tokens: 1000 });
        assert(result?.exit_code === null || result?.exit_code === undefined, "Receiver exited before commit", { path: absolute, operation: "write-file" });
        sequence += 1;
      }
      const commit = await tools.write_stdin({ session_id: sessionId, chars: `C${WRITE_STDIN_RECORD_SEPARATOR}`, yield_time_ms: 30000, max_output_tokens: 1000 });
      const completed = await waitForMarker({ initial: commit, sessionId, marker: RECEIVER_COMMITTED_MARKER, operation: "write-file" });
      const receipt = new RegExp(`${RECEIVER_COMMITTED_MARKER}\\s+(\\d+)\\s+([a-f0-9]{64})`, "i").exec(completed.output);
      assert(receipt && Number(receipt[1]) === bytes && receipt[2].toLowerCase() === expectedSha256, "Receiver commit receipt did not match", { path: absolute, operation: "write-file" });
      assert(completed.result?.exit_code === 0, "Receiver did not exit cleanly", { path: absolute, operation: "write-file" });
      return { path: absolute, bytes, sha256: expectedSha256 };
    } catch (error) {
      try {
        await tools.write_stdin({ session_id: sessionId, chars: `A${WRITE_STDIN_RECORD_SEPARATOR}`, yield_time_ms: 1000, max_output_tokens: 1000 });
      } catch {}
      await run(`/bin/rm -f -- ${shellQuote(temporary)}`, 1000);
      throw error;
    }
  };

  return {
    async readText(path) {
      const absolute = validateReadable(path);
      const size = await run(`/usr/bin/wc -c < ${shellQuote(absolute)}`, 1000);
      assert(size.exit_code === 0, `Could not stat ${absolute}`, { path: absolute, operation: "read-file" });
      const expectedBytes = Number(String(size.output).trim());
      assert(Number.isInteger(expectedBytes) && expectedBytes >= 0 && expectedBytes <= maxReadBytes, `Invalid or oversized read for ${absolute}`, { path: absolute, operation: "read-file" });
      const result = await run(`/bin/cat -- ${shellQuote(absolute)}`, Math.max(4000, Math.ceil(expectedBytes / 2)));
      assert(result.exit_code === 0 && utf8Bytes(result.output).length === expectedBytes, `Read of ${absolute} failed or was truncated`, { path: absolute, operation: "read-file" });
      return result.output;
    },
    async writeBatch(entries) {
      assert(Array.isArray(entries) && entries.length > 0, "writeBatch entries are required", { operation: "write-file" });
      const paths = entries.map((entry) => validateWritable(entry.path));
      assert(new Set(paths).size === paths.length, "writeBatch paths must be unique", { operation: "write-file" });
      const metadata = [];
      for (const entry of entries) metadata.push(await streamText(entry.path, entry.text));
      return metadata;
    },
    async exists(path) {
      const absolute = validateReadable(path);
      const result = await run(`/bin/test -e ${shellQuote(absolute)}`, 1000);
      if (result.exit_code === 0) return true;
      if (result.exit_code === 1) return false;
      throw new DocsTrustedReadBridgeError(`Could not inspect ${absolute}`, { path: absolute, operation: "inspect-file" });
    },
  };
}

function validateFileIO(fileIO) {
  assert(isRecord(fileIO), "fileIO is required", { operation: "validate-file-io" });
  assert(typeof fileIO.readText === "function", "fileIO.readText is required", { operation: "validate-file-io" });
  assert(typeof fileIO.writeBatch === "function", "fileIO.writeBatch is required", { operation: "validate-file-io" });
  assert(typeof fileIO.exists === "function", "fileIO.exists is required", { operation: "validate-file-io" });
  return fileIO;
}

function compactControlAwareness(trustedRead, normalized) {
  const inventory = trustedRead.derivedControlInventory;
  return {
    hasProtectedControls: inventory.hasProtectedControls,
    authoritativeDropdownCount: inventory.authoritativeDropdownCount,
    opaqueControlCount: inventory.opaqueControlCount,
    affectedParagraphCount: normalized.controlSummary.affectedParagraphs,
    nativeElementCounts: inventory.nativeElementCounts,
    preservationRequired: trustedRead.editGuidance.requiresTargetedPreservation,
    recommendedBehavior: trustedRead.editGuidance.recommendedBehavior,
  };
}

export async function executeDocsTrustedReadToFiles({
  documentId = null,
  documentUrl = null,
  tabId = null,
  outputDir,
  workspaceRoot,
  skillRoot,
  tools,
  fileIO = null,
  capabilityOverrides = {},
  maxReadBytes = DEFAULT_MAX_READ_BYTES,
  maxWriteBytes = DEFAULT_MAX_WRITE_BYTES,
} = {}) {
  assert(Boolean(documentId) !== Boolean(documentUrl), "Provide exactly one of documentId or documentUrl", { operation: "validate-input" });
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const skill = normalizeAbsolutePath(skillRoot, "skillRoot");
  const output = assertWithinRoot(outputDir, workspace, "outputDir");
  const wrapperPath = assertWithinRoot(`${skill}/host/docs-trusted-read-wrapper.mjs`, skill, "wrapperPath");
  const normalizerPath = assertWithinRoot(`${skill}/runtime/docs-read-normalizer.mjs`, skill, "normalizerPath");
  const io = fileIO ? validateFileIO(fileIO) : createToolBackedFileIO({
    tools,
    workspaceRoot: workspace,
    skillRoot: skill,
    receiverPath: `${skill}/host/docs-stdin-receiver.pl`,
    maxReadBytes,
    maxWriteBytes,
  });
  assert(!(await io.exists(output)), "Trusted-read output directory already exists", { path: output, operation: "validate-output" });

  let trustedRead = null;
  let normalizedResult = null;
  let caught = null;
  try {
    const [wrapper, normalizer] = await Promise.all([
      loadTrustedModule(io, wrapperPath, ["readGoogleDocWithControlInventory"], "trusted read wrapper"),
      loadTrustedModule(io, normalizerPath, ["normalizeGoogleDocumentRead", "renderNormalizedDocumentText"], "document read normalizer"),
    ]);
    trustedRead = await wrapper.readGoogleDocWithControlInventory({ documentId, documentUrl, tabId, tools, capabilityOverrides });
    normalizedResult = normalizer.normalizeGoogleDocumentRead({
      documentResult: trustedRead.documentResult,
      trustedReadContext: trustedRead,
      selectedTabId: tabId,
    });
  } catch (error) {
    caught = error;
  }

  const status = caught ? "failed" : "complete";
  const dataArtifacts = [];
  if (trustedRead && normalizedResult) {
    dataArtifacts.push(jsonArtifact(joinPath(output, "document-result.json"), trustedRead.documentResult));
    if (trustedRead.dropdownResult !== null && trustedRead.dropdownResult !== undefined) {
      dataArtifacts.push(jsonArtifact(joinPath(output, "dropdown-result.json"), trustedRead.dropdownResult));
    }
    dataArtifacts.push(jsonArtifact(joinPath(output, "control-inventory.json"), {
      version: trustedRead.version,
      kind: trustedRead.kind,
      target: trustedRead.target,
      dropdownMetadata: trustedRead.dropdownMetadata,
      derivedControlInventory: trustedRead.derivedControlInventory,
      editGuidance: trustedRead.editGuidance,
    }));
    dataArtifacts.push(jsonArtifact(joinPath(output, "document-outline.json"), normalizedResult.normalized));
    dataArtifacts.push(fileArtifact(joinPath(output, "document-text.md"), normalizedResult.markdown));
  }

  const controlAwareness = trustedRead && normalizedResult
    ? compactControlAwareness(trustedRead, normalizedResult.normalized)
    : null;
  const receipt = {
    bridgeVersion: BRIDGE_VERSION,
    kind: "google-docs-trusted-read-receipt",
    status,
    target: trustedRead?.target ?? { documentId, documentUrl, selectedTabId: tabId },
    dropdownMetadata: trustedRead?.dropdownMetadata ?? null,
    controlAwareness,
    warnings: trustedRead?.editGuidance?.warnings ?? [],
    error: caught ? compactError(caught) : null,
  };
  const receiptArtifact = jsonArtifact(joinPath(output, "receipt.json"), receipt);
  const committedArtifacts = [...dataArtifacts, receiptArtifact];
  await io.writeBatch(committedArtifacts.map(({ path, text }) => ({ path, text })));

  const files = Object.fromEntries(committedArtifacts.map((artifact) => {
    const key = artifact.path.slice(output.length + 1).replace(/\.[^.]+$/, "").replace(/-/g, "_");
    return [key, artifact.metadata];
  }));
  const manifest = {
    bridgeVersion: BRIDGE_VERSION,
    kind: "google-docs-trusted-read",
    status,
    outputDir: output,
    target: receipt.target,
    dropdownMetadata: receipt.dropdownMetadata,
    controlAwareness,
    warnings: receipt.warnings,
    files,
    error: receipt.error,
  };
  const manifestArtifact = jsonArtifact(joinPath(output, "manifest.json"), manifest);
  await io.writeBatch([{ path: manifestArtifact.path, text: manifestArtifact.text }]);
  return { ...manifest, manifestFile: manifestArtifact.metadata };
}

export { BRIDGE_VERSION };
