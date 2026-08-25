const READY_MARKER = "SLIDES_BRIDGE_READY";
const COMMITTED_MARKER = "SLIDES_BRIDGE_COMMITTED";
const RECORD_SEPARATOR = "\u0003";
const MAX_PDF_BYTES = 32 * 1024 * 1024;
const FRAME_CHARS = 480000;
const CONNECTOR_TOOL_RESULTS_ROOT = "/workspace/.openai/connector_tool_results";
const PREPARE_LEGACY_OUTPUT = String.raw`
use strict;
use warnings;
use File::Basename qw(dirname);

@ARGV == 2 or die "invalid legacy PDF output arguments\n";
my ($output_path, $workspace_root) = @ARGV;
for my $path ($output_path, $workspace_root) {
  $path !~ /[\0\r\n]/ or die "invalid legacy PDF output path\n";
}

sub parts_below_root {
  my ($path, $root) = @_;
  ($path eq $root || index($path, "$root/") == 0)
    or die "legacy PDF output path must stay within the workspace\n";
  my $relative = substr($path, length($root));
  return grep { length($_) > 0 } split("/", $relative);
}

sub require_real_directory {
  my ($path) = @_;
  lstat($path) or die "could not inspect legacy PDF output path\n";
  -l _ and die "legacy PDF output path must not include symlinks\n";
  -d _ or die "legacy PDF output path component must be a directory\n";
}

require_real_directory($workspace_root);
my $cursor = $workspace_root;
for my $part (parts_below_root(dirname($output_path), $workspace_root)) {
  $cursor .= "/$part";
  if (lstat($cursor)) {
    -l _ and die "legacy PDF output path must not include symlinks\n";
    -d _ or die "legacy PDF output path component must be a directory\n";
  } else {
    mkdir($cursor, 0700) or die "could not create legacy PDF output directory\n";
  }
}
lstat($output_path) and die "refusing to overwrite an existing PDF\n";
`;
const COPY_MATERIALIZED_PDF = String.raw`
use strict;
use warnings;
use Fcntl qw(O_CREAT O_EXCL O_NOFOLLOW O_RDONLY O_WRONLY);
use Digest::SHA;
use File::Basename qw(dirname);

@ARGV == 7 or die "invalid materialized PDF arguments\n";
my (
  $source_path,
  $output_path,
  $maximum_bytes,
  $declared_bytes,
  $temporary_path,
  $source_root,
  $output_root,
) = @ARGV;
$maximum_bytes =~ /\A[0-9]+\z/ or die "invalid materialized PDF size limit\n";
($declared_bytes eq "-" || $declared_bytes =~ /\A[0-9]+\z/)
  or die "invalid declared materialized PDF size\n";
for my $path ($source_path, $output_path, $temporary_path, $source_root, $output_root) {
  $path !~ /[\0\r\n]/ or die "invalid materialized PDF path\n";
}

sub parts_below_root {
  my ($path, $root, $label) = @_;
  ($path eq $root || index($path, "$root/") == 0)
    or die "$label must stay within its trusted root\n";
  my $relative = substr($path, length($root));
  return grep { length($_) > 0 } split("/", $relative);
}

sub require_real_directory {
  my ($path, $label) = @_;
  lstat($path) or die "could not inspect $label\n";
  -l _ and die "$label must not include symlinks\n";
  -d _ or die "$label must be a directory\n";
}

sub reject_symlink_components {
  my ($root, $path, $label) = @_;
  require_real_directory($root, "$label root");
  my $cursor = $root;
  for my $part (parts_below_root($path, $root, $label)) {
    $cursor .= "/$part";
    lstat($cursor) or die "could not inspect $label\n";
    -l _ and die "$label must not include symlinks\n";
  }
}

sub ensure_directory_tree {
  my ($root, $directory, $label) = @_;
  require_real_directory($root, "$label root");
  my $cursor = $root;
  for my $part (parts_below_root($directory, $root, $label)) {
    $cursor .= "/$part";
    if (lstat($cursor)) {
      -l _ and die "$label must not include symlinks\n";
      -d _ or die "$label component must be a directory\n";
    } else {
      mkdir($cursor, 0700) or die "could not create $label\n";
    }
  }
}

ensure_directory_tree($output_root, dirname($output_path), "output path");
reject_symlink_components($source_root, $source_path, "materialized PDF path");
sysopen(my $source, $source_path, O_RDONLY | O_NOFOLLOW)
  or die "could not open the materialized PDF\n";
binmode($source);
-f $source or die "materialized PDF must be a regular file\n";
my @source_stat = stat($source);
@source_stat or die "could not stat the materialized PDF\n";
my $expected_bytes = $source_stat[7];
$expected_bytes >= 5 or die "materialized PDF does not contain a PDF header\n";
$expected_bytes <= $maximum_bytes or die "materialized PDF exceeds the byte limit\n";
($declared_bytes eq "-" || $expected_bytes == $declared_bytes)
  or die "materialized PDF does not match its declared byte length\n";
(!-e $output_path && !-e $temporary_path)
  or die "refusing to overwrite an existing PDF\n";

umask 0077;
sysopen(my $output, $temporary_path, O_WRONLY | O_CREAT | O_EXCL, 0600)
  or die "could not create a temporary materialized PDF\n";
binmode($output);
my $bytes_written = 0;
my $sha256 = Digest::SHA->new(256);
my $success = eval {
  while (1) {
    my $read = sysread($source, my $chunk, 64 * 1024);
    defined($read) or die "could not read the materialized PDF\n";
    last if $read == 0;
    if ($bytes_written == 0) {
      substr($chunk, 0, 5) eq "%PDF-"
        or die "materialized file does not contain a PDF header\n";
    }
    $bytes_written += $read;
    $bytes_written <= $maximum_bytes
      or die "materialized PDF exceeds the byte limit\n";
    my $offset = 0;
    while ($offset < $read) {
      my $written = syswrite($output, $chunk, $read - $offset, $offset);
      defined($written) && $written > 0
        or die "could not write the materialized PDF\n";
      $offset += $written;
    }
    $sha256->add($chunk);
  }
  $bytes_written == $expected_bytes
    or die "materialized PDF changed while it was being copied\n";
  close($source) or die "could not close the materialized PDF\n";
  close($output) or die "could not close the copied PDF\n";
  link($temporary_path, $output_path)
    or die "could not publish the materialized PDF without overwriting\n";
  unlink($temporary_path) or die "could not clean up the temporary PDF\n";
  print "SLIDES_BRIDGE_COMMITTED $bytes_written ", $sha256->hexdigest, "\n";
  1;
};
if (!$success) {
  my $reason = $@ || "could not materialize the PDF\n";
  close($output);
  unlink($temporary_path);
  die $reason;
}
`;

class SlidesRenderError extends Error {
  constructor(message) {
    super(String(message).replace(/https?:\/\/[^\s\"'<>]+/gi, "[URL_REDACTED]"));
    this.name = "SlidesRenderError";
  }
}

function assert(condition, message) {
  if (!condition) throw new SlidesRenderError(message);
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
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

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\"'\"'`)}'`;
}

function dirname(path) {
  const index = path.lastIndexOf("/");
  return index <= 0 ? "/" : path.slice(0, index);
}

function normalizeToolName(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]/g, "");
}

function resolveFetch(tools) {
  const preferred = "mcp__codex_apps__google_drive_fetch";
  if (typeof tools?.[preferred] === "function") return preferred;
  const matches = Object.keys(tools ?? {}).filter((name) =>
    typeof tools[name] === "function" && normalizeToolName(name).endsWith("googledrivefetch"));
  assert(matches.length === 1, "Could not resolve the Google Drive fetch tool");
  return matches[0];
}

function canonicalPresentationUrl(presentationId) {
  assert(
    /^[A-Za-z0-9_-]+$/.test(presentationId),
    "presentationId is invalid for a canonical raw fetch",
  );
  return `https://docs.google.com/presentation/d/${presentationId}`;
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function unwrapToolResult(raw) {
  assert(raw?.isError !== true, "Google Drive PDF export failed");
  if (raw?.structuredContent?.result !== undefined) return raw.structuredContent.result;
  if (raw?.structuredContent !== undefined) return raw.structuredContent;
  const text = Array.isArray(raw?.content)
    ? raw.content.find((item) => item?.type === "text" && typeof item.text === "string")?.text
    : null;
  return text ? parseJson(text) ?? raw : raw;
}

function isUnsupportedIncludeBase64Error(value) {
  let text;
  try {
    text = JSON.stringify(value);
  } catch {
    text = String(value);
  }
  return /InvalidActionArgumentsError|invalid_action_arguments|unknown\s+(?:argument|parameter)|unexpected\s+(?:argument|field)|extra\s+(?:argument|field)/i.test(
    String(text ?? ""),
  );
}

async function fetchPdf({ connectorTool, presentationId, tools }) {
  const args = {
    url: canonicalPresentationUrl(presentationId),
    download_raw_file: true,
    raw_export_mime_type: "application/pdf",
  };
  try {
    const raw = await tools[connectorTool]({ ...args, include_base64: false });
    if (raw?.isError !== true || !isUnsupportedIncludeBase64Error(raw)) return raw;
  } catch (error) {
    if (!isUnsupportedIncludeBase64Error(error)) throw error;
  }
  return tools[connectorTool](args);
}

function findPdfPayload(root) {
  const queue = [root];
  const seen = new Set();
  let inlineContentPayload = null;
  while (queue.length > 0 && seen.size < 10000) {
    const value = queue.shift();
    if ((!isRecord(value) && !Array.isArray(value)) || seen.has(value)) continue;
    seen.add(value);
    if (isRecord(value) && typeof value.b64_string === "string") {
      return {
        ...value,
        content: value.b64_string,
        mimeType: value.mimeType ?? value.mime_type ?? "application/pdf",
      };
    }
    if (isRecord(value) && typeof value.content === "string" && value.content.length > 0) {
      const mimeType = value.mimeType ?? value.mime_type ?? null;
      if (
        inlineContentPayload === null
        && (value.base64Encoded === true || mimeType === "application/pdf")
      ) {
        inlineContentPayload = value;
      }
    }
    for (const child of Array.isArray(value) ? value : Object.values(value)) {
      if (isRecord(child) || Array.isArray(child)) queue.push(child);
    }
  }
  if (inlineContentPayload !== null) return inlineContentPayload;
  throw new SlidesRenderError("PDF export did not contain base64 PDF content");
}

function decodedBase64Bytes(value) {
  if (value.length === 0 || value.length % 4 !== 0) return null;
  const padding = value.endsWith("==") ? 2 : value.endsWith("=") ? 1 : 0;
  return (value.length / 4) * 3 - padding;
}

function validatePdfPayload(value) {
  const payload = findPdfPayload(value);
  const base64 = payload.content;
  const mimeType = payload.mimeType ?? payload.mime_type ?? "application/pdf";
  assert(mimeType === "application/pdf", `Export returned ${mimeType} instead of application/pdf`);
  assert(/^[A-Za-z0-9+/]*={0,2}$/.test(base64), "PDF export contains invalid base64");
  assert(base64.startsWith("JVBERi0"), "PDF export does not start with a PDF header");
  const bytes = decodedBase64Bytes(base64);
  assert(Number.isInteger(bytes) && bytes > 0, "PDF export has an invalid decoded byte length");
  assert(bytes <= MAX_PDF_BYTES, `PDF export is ${bytes} bytes; limit is ${MAX_PDF_BYTES}`);
  return { base64, bytes };
}

function findMaterializedPdf(raw, result, workspaceRoot) {
  const candidates = [
    result,
    raw,
    raw?.result,
    raw?.structuredContent,
    raw?.structuredContent?.result,
  ].filter(isRecord);
  const referenceOwner = candidates.find((candidate) =>
    isRecord(candidate.file_uri));
  if (!referenceOwner) return null;

  const reference = referenceOwner.file_uri;
  const pathOwner = candidates.find((candidate) =>
    typeof candidate.workspace_path === "string");
  if (!pathOwner) return { missingWorkspacePath: true };

  const source = normalizeAbsolutePath(pathOwner.workspace_path, "workspace_path");
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const insideWorkspace = source === workspace || source.startsWith(`${workspace}/`);
  const insideConnectorResults = source.startsWith(`${CONNECTOR_TOOL_RESULTS_ROOT}/`);
  assert(
    insideWorkspace || insideConnectorResults,
    "Materialized PDF workspace_path must stay within the task workspace or connector tool results",
  );

  const mimeType = reference.mime_type
    ?? referenceOwner.mime_type
    ?? referenceOwner.mimeType
    ?? result?.mime_type
    ?? result?.mimeType;
  assert(mimeType === "application/pdf", `Export returned ${mimeType} instead of application/pdf`);

  const declaredBytes = referenceOwner.size
    ?? referenceOwner.file_size_bytes
    ?? reference.size
    ?? result?.size
    ?? result?.file_size_bytes;
  if (declaredBytes !== null && declaredBytes !== undefined) {
    assert(
      Number.isSafeInteger(declaredBytes) && declaredBytes > 0,
      "Materialized PDF has an invalid declared byte length",
    );
    assert(
      declaredBytes <= MAX_PDF_BYTES,
      `PDF export is ${declaredBytes} bytes; limit is ${MAX_PDF_BYTES}`,
    );
  }

  return { source, declaredBytes, missingWorkspacePath: false };
}

async function copyMaterializedPdf({ source, declaredBytes, outputPath, workspaceRoot, tools }) {
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const output = assertWithinRoot(outputPath, workspace, "outputPath");
  const temporary = `${output}.stream-${Date.now()}-${Math.random().toString(16).slice(2)}.tmp`;
  const sourceRoot = source.startsWith(`${CONNECTOR_TOOL_RESULTS_ROOT}/`)
    ? CONNECTOR_TOOL_RESULTS_ROOT
    : workspace;

  const result = await tools.exec_command({
    cmd: `/usr/bin/perl -e ${shellQuote(COPY_MATERIALIZED_PDF)} -- ${shellQuote(source)} ${shellQuote(output)} ${shellQuote(String(MAX_PDF_BYTES))} ${shellQuote(declaredBytes === null || declaredBytes === undefined ? "-" : String(declaredBytes))} ${shellQuote(temporary)} ${shellQuote(sourceRoot)} ${shellQuote(workspace)}`,
    workdir: workspace,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 1000,
  });
  assert(result.exit_code === 0, `Could not copy the materialized PDF: ${result.output}`);
  const receipt = /SLIDES_BRIDGE_COMMITTED\s+(\d+)\s+([a-f0-9]{64})/i.exec(
    String(result.output ?? ""),
  );
  assert(receipt, "Materialized PDF returned an invalid copy receipt");
  const bytes = Number(receipt[1]);
  assert(Number.isSafeInteger(bytes) && bytes > 0, "Materialized PDF has an invalid byte length");
  assert(bytes <= MAX_PDF_BYTES, `PDF export is ${bytes} bytes; limit is ${MAX_PDF_BYTES}`);
  if (declaredBytes !== null && declaredBytes !== undefined) {
    assert(bytes === declaredBytes, "Materialized PDF does not match its declared byte length");
  }
  return { path: output, bytes, sha256: receipt[2].toLowerCase() };
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
  throw new SlidesRenderError(`File receiver did not report ${marker}`);
}

async function writeBase64({ base64, bytes, outputPath, workspaceRoot, skillRoot, tools }) {
  assert(typeof tools.write_stdin === "function", "Legacy PDF exports require a code-mode file receiver");
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const output = assertWithinRoot(outputPath, workspace, "outputPath");
  const receiver = assertWithinRoot(
    `${normalizeAbsolutePath(skillRoot, "skillRoot")}/host/slides-stdin-receiver.pl`,
    skillRoot,
    "receiverPath",
  );
  const temporary = `${output}.stream-${Date.now()}-${Math.random().toString(16).slice(2)}.tmp`;

  let result = await tools.exec_command({
    cmd: `/usr/bin/perl -e ${shellQuote(PREPARE_LEGACY_OUTPUT)} -- ${shellQuote(output)} ${shellQuote(workspace)}`,
    workdir: workspace,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 1000,
  });
  assert(result.exit_code === 0, `Could not prepare legacy PDF output: ${result.output}`);

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

  try {
    await waitForMarker(tools, started, sessionId, READY_MARKER);
    let sequence = 0;
    for (let offset = 0; offset < base64.length; offset += FRAME_CHARS) {
      const write = await tools.write_stdin({
        session_id: sessionId,
        chars: `D\t${sequence}\t${base64.slice(offset, offset + FRAME_CHARS)}${RECORD_SEPARATOR}`,
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

function pageNumber(path) {
  const match = /-(\d+)\.png$/.exec(path);
  return match ? Number(match[1]) : Number.MAX_SAFE_INTEGER;
}

async function loadSlideOrder({ designSystemPath, presentationId, workspaceRoot, tools }) {
  if (designSystemPath === null || designSystemPath === undefined) return null;
  const path = assertWithinRoot(designSystemPath, workspaceRoot, "designSystemPath");
  const result = await tools.exec_command({
    cmd: `jq -c '{presentationId:.source.presentation.id,slides:([.slides[]|{slideIndex:.index,slideObjectId:.slideId,titlePreview:(.titlePreview//null),layoutId:(.layoutId//null),isSkipped:(.isSkipped==true)}]|sort_by(.slideIndex))}' ${shellQuote(path)}`,
    workdir: dirname(path),
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 20000,
  });
  assert(result.exit_code === 0, `Could not read slide order from the design system: ${result.output}`);
  const parsed = parseJson(String(result.output ?? "").trim());
  assert(isRecord(parsed) && Array.isArray(parsed.slides), "Design system did not contain an ordered slides array");
  assert(parsed.presentationId === presentationId, "Design system presentation ID does not match presentationId");
  const seen = new Set();
  parsed.slides.forEach((slide, index) => {
    assert(isRecord(slide), `Design system slide ${index + 1} is invalid`);
    assert(slide.slideIndex === index, `Design system slide indices are not contiguous at page ${index + 1}`);
    assert(typeof slide.slideObjectId === "string" && slide.slideObjectId.length > 0, `Design system slide ${index + 1} omitted slideId`);
    assert(!seen.has(slide.slideObjectId), `Design system contains duplicate slide ID ${slide.slideObjectId}`);
    seen.add(slide.slideObjectId);
  });
  return { path, slides: parsed.slides };
}

export async function exportAndRenderSlides({
  presentationId,
  outputDir,
  workspaceRoot,
  skillRoot,
  designSystemPath = null,
  pdftoppmPath,
  dpi = 120,
  tools,
} = {}) {
  assert(typeof presentationId === "string" && presentationId.length > 0, "presentationId is required");
  assert(tools && typeof tools.exec_command === "function", "Code-mode tools are required");
  assert(Number.isInteger(dpi) && dpi >= 36 && dpi <= 300, "dpi must be an integer from 36 to 300");
  const workspace = normalizeAbsolutePath(workspaceRoot, "workspaceRoot");
  const output = assertWithinRoot(outputDir, workspace, "outputDir");
  const renderer = normalizeAbsolutePath(pdftoppmPath, "pdftoppmPath");
  const pdfPath = `${output}/presentation.pdf`;
  const slideOrder = await loadSlideOrder({ designSystemPath, presentationId, workspaceRoot: workspace, tools });

  const connectorTool = resolveFetch(tools);
  const raw = await fetchPdf({ connectorTool, presentationId, tools });
  const result = unwrapToolResult(raw);
  const materialized = findMaterializedPdf(raw, result, workspace);
  let pdf;
  if (materialized?.source) {
    pdf = await copyMaterializedPdf({
      source: materialized.source,
      declaredBytes: materialized.declaredBytes,
      outputPath: pdfPath,
      workspaceRoot: workspace,
      tools,
    });
  } else {
    let payload;
    try {
      payload = validatePdfPayload([result, raw]);
    } catch (error) {
      if (materialized?.missingWorkspacePath) {
        throw new SlidesRenderError(
          "Google Drive PDF file reference was not materialized to workspace_path and no valid inline fallback was available",
        );
      }
      throw error;
    }
    pdf = await writeBase64({
      base64: payload.base64,
      bytes: payload.bytes,
      outputPath: pdfPath,
      workspaceRoot: workspace,
      skillRoot,
      tools,
    });
  }

  const rendered = await tools.exec_command({
    cmd: `${shellQuote(renderer)} -png -r ${dpi} ${shellQuote(pdfPath)} ${shellQuote(`${output}/slide`)}`,
    workdir: output,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 5000,
  });
  assert(rendered.exit_code === 0, `pdftoppm failed: ${rendered.output}`);
  const listed = await tools.exec_command({
    cmd: `/usr/bin/find ${shellQuote(output)} -maxdepth 1 -type f -name 'slide-*.png' -print`,
    workdir: output,
    login: false,
    yield_time_ms: 30000,
    max_output_tokens: 20000,
  });
  assert(listed.exit_code === 0, `Could not list rendered slides: ${listed.output}`);
  const images = String(listed.output ?? "")
    .split("\n")
    .map((value) => value.trim())
    .filter(Boolean)
    .sort((left, right) => pageNumber(left) - pageNumber(right));
  assert(images.length > 0, "pdftoppm produced no slide images");
  if (slideOrder) {
    assert(
      slideOrder.slides.length === images.length,
      `PDF page count ${images.length} does not match design system slide count ${slideOrder.slides.length}`,
    );
  }
  const mappedImages = images.map((path, index) => ({
    page: index + 1,
    path,
    ...(slideOrder ? slideOrder.slides[index] : {}),
  }));

  return {
    status: "complete",
    presentationId,
    connectorTool,
    pdf,
    dpi,
    pageCount: images.length,
    designSystemPath: slideOrder?.path ?? null,
    images: mappedImages,
  };
}
