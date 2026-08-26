const READY_MARKER = "SLIDES_BRIDGE_READY";
const COMMITTED_MARKER = "SLIDES_BRIDGE_COMMITTED";
const RECORD_SEPARATOR = "\u0003";
const MAX_OUTPUT_BYTES = 64 * 1024 * 1024;
const FRAME_CHARS = 480000;

class TemplateReadError extends Error {
  constructor(message) {
    super(String(message).replace(/https?:\/\/[^\s\"'<>]+/gi, "[URL_REDACTED]"));
    this.name = "TemplateReadError";
  }
}

function assert(condition, message) {
  if (!condition) throw new TemplateReadError(message);
}

function normalizeAbsolutePath(value, label) {
  assert(typeof value === "string" && value.startsWith("/"), `${label} must be an absolute path`);
  assert(!/[\0\r\n]/.test(value), `${label} contains an invalid character`);
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
  );
  return normalizedPath;
}

function dirname(path) {
  const index = path.lastIndexOf("/");
  return index <= 0 ? "/" : path.slice(0, index);
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\"'\"'`)}'`;
}

function utf8Bytes(text) {
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
  let output = "";
  for (let index = 0; index < bytes.length; index += 3) {
    const first = bytes[index];
    const hasSecond = index + 1 < bytes.length;
    const hasThird = index + 2 < bytes.length;
    const second = hasSecond ? bytes[index + 1] : 0;
    const third = hasThird ? bytes[index + 2] : 0;
    output += alphabet[first >> 2];
    output += alphabet[((first & 0x03) << 4) | (second >> 4)];
    output += hasSecond ? alphabet[((second & 0x0f) << 2) | (third >> 6)] : "=";
    output += hasThird ? alphabet[third & 0x3f] : "=";
  }
  return output;
}

function normalizeToolName(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]/g, "");
}

function resolveGetPresentation(tools) {
  const preferred = "mcp__codex_apps__google_drive_get_presentation";
  if (typeof tools?.[preferred] === "function") return preferred;
  const matches = Object.keys(tools ?? {}).filter((name) =>
    typeof tools[name] === "function" && normalizeToolName(name).endsWith("googledrivegetpresentation"));
  assert(matches.length === 1, "Could not resolve the Google Drive get_presentation tool");
  return matches[0];
}

async function waitForMarker(tools, initial, sessionId, marker) {
  let result = initial;
  let output = String(result?.output ?? "");
  for (let attempt = 0; attempt < 5; attempt += 1) {
    if (output.includes(marker)) return { result, output };
    if (result?.exit_code !== null && result?.exit_code !== undefined) break;
    result = await tools.write_stdin({
      session_id: sessionId,
      chars: "",
      yield_time_ms: 1000,
      max_output_tokens: 1000,
    });
    output += String(result?.output ?? "");
  }
  throw new TemplateReadError(`File receiver did not report ${marker}`);
}

async function writeText({ text, outputPath, workspaceRoot, skillRoot, tools }) {
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const output = assertWithinRoot(outputPath, workspace, "outputPath");
  const receiver = assertWithinRoot(
    `${normalizeAbsolutePath(skillRoot, "skillRoot")}/host/slides-stdin-receiver.pl`,
    skillRoot,
    "receiverPath",
  );
  const bytes = utf8Bytes(text).length;
  assert(bytes <= MAX_OUTPUT_BYTES, `Presentation response is ${bytes} bytes; limit is ${MAX_OUTPUT_BYTES}`);

  const parent = dirname(output);
  const temporary = `${output}.stream-${Date.now()}-${Math.random().toString(16).slice(2)}.tmp`;
  let result = await tools.exec_command({
    cmd: `/bin/mkdir -p ${shellQuote(parent)}`,
    workdir: dirname(workspace),
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 1000,
  });
  assert(result.exit_code === 0, `Could not create output directory: ${result.output}`);
  result = await tools.exec_command({
    cmd: `/bin/test ! -e ${shellQuote(output)}`,
    workdir: workspace,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 1000,
  });
  assert(result.exit_code === 0, `Refusing to overwrite ${output}`);

  const started = await tools.exec_command({
    cmd: `/usr/bin/perl ${shellQuote(receiver)} ${shellQuote(output)} ${shellQuote(String(bytes))} - ${shellQuote(temporary)}`,
    workdir: workspace,
    login: false,
    tty: true,
    yield_time_ms: 1000,
    max_output_tokens: 1000,
  });
  const sessionId = started?.session_id;
  assert(Number.isInteger(sessionId), `Could not start file receiver: ${started?.output ?? "missing session"}`);

  const encoded = base64Text(text);
  try {
    await waitForMarker(tools, started, sessionId, READY_MARKER);
    let sequence = 0;
    for (let offset = 0; offset < encoded.length; offset += FRAME_CHARS) {
      const frame = `D\t${sequence}\t${encoded.slice(offset, offset + FRAME_CHARS)}${RECORD_SEPARATOR}`;
      const write = await tools.write_stdin({
        session_id: sessionId,
        chars: frame,
        yield_time_ms: 250,
        max_output_tokens: 1000,
      });
      assert(write?.exit_code === null || write?.exit_code === undefined, "File receiver exited before commit");
      sequence += 1;
    }
    const committed = await tools.write_stdin({
      session_id: sessionId,
      chars: `C${RECORD_SEPARATOR}`,
      yield_time_ms: 30000,
      max_output_tokens: 1000,
    });
    const completed = await waitForMarker(tools, committed, sessionId, COMMITTED_MARKER);
    const receipt = /SLIDES_BRIDGE_COMMITTED\s+(\d+)\s+([a-f0-9]{64})/i.exec(completed.output);
    assert(receipt, "File receiver returned an invalid receipt");
    assert(Number(receipt[1]) === bytes, "File receiver wrote the wrong byte count");
    assert(completed.result?.exit_code === 0, "File receiver did not exit cleanly");
    return { path: output, bytes, sha256: receipt[2].toLowerCase() };
  } catch (error) {
    try {
      await tools.write_stdin({ session_id: sessionId, chars: `A${RECORD_SEPARATOR}`, yield_time_ms: 1000, max_output_tokens: 1000 });
    } catch {
      // Receiver may already have exited.
    }
    throw error;
  }
}

export async function readTemplateToFile({
  presentationId = null,
  presentationUrl = null,
  outputPath,
  workspaceRoot,
  skillRoot,
  tools,
} = {}) {
  assert(Boolean(presentationId) !== Boolean(presentationUrl), "Provide exactly one of presentationId or presentationUrl");
  assert(tools && typeof tools.exec_command === "function" && typeof tools.write_stdin === "function", "Code-mode tools are required");
  const toolName = resolveGetPresentation(tools);
  const args = presentationId ? { presentation_id: presentationId } : { presentation_url: presentationUrl };
  const raw = await tools[toolName](args); // Omit `fields` to request the full presentation resource.
  assert(raw?.isError !== true && raw?.structuredContent?.result?.isError !== true, "Google Slides presentation read failed");
  const file = await writeText({
    text: `${JSON.stringify(raw, null, 2)}\n`,
    outputPath,
    workspaceRoot,
    skillRoot,
    tools,
  });
  return {
    status: "complete",
    presentationId: presentationId ?? null,
    usedPresentationUrl: Boolean(presentationUrl),
    connectorTool: toolName,
    file,
  };
}
