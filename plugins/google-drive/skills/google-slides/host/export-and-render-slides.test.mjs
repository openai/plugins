import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { promisify } from "node:util";

import { exportAndRenderSlides } from "./export-and-render-slides.mjs";

const execFileAsync = promisify(execFile);
const pdfBytes = Buffer.from("%PDF-1.7\nGoogle Slides regression\n%%EOF\n");
const pdfSha256 = createHash("sha256").update(pdfBytes).digest("hex");

function createOversizedPdf() {
  const bytes = Buffer.alloc(10 * 1024 * 1024 + 1, 0x20);
  bytes.set(Buffer.from("%PDF-1.7\n"));
  bytes.set(Buffer.from("\n%%EOF\n"), bytes.length - 7);
  return bytes;
}

async function runLocalCommand(cmd, workdir) {
  try {
    const { stdout, stderr } = await execFileAsync("/bin/sh", ["-c", cmd], {
      cwd: workdir,
      encoding: "utf8",
      maxBuffer: 1024 * 1024,
    });
    return { exit_code: 0, output: `${stdout}${stderr}` };
  } catch (error) {
    return {
      exit_code: Number.isInteger(error.code) ? error.code : 1,
      output: `${error.stdout ?? ""}${error.stderr ?? error.message}`,
    };
  }
}

async function createFixture(t, {
  raw,
  includeLegacyReceiver = false,
  pdf = pdfBytes,
} = {}) {
  const workspace = await mkdtemp(join(tmpdir(), "google-slides-materialization-"));
  t.after(async () => {
    await rm(workspace, { recursive: true, force: true });
  });
  const source = join(workspace, "connector-results", "presentation.pdf");
  const outputDir = join(workspace, "renders");
  const calls = [];
  const frames = [];

  await runLocalCommand(`/bin/mkdir -p '${join(workspace, "connector-results")}'`, workspace);
  await writeFile(source, pdf);
  const reference = {
    file_id: "sediment://test-presentation",
    download_url: "sediment://test-presentation",
    file_name: "presentation.pdf",
    mime_type: "application/pdf",
  };
  const defaultResponse = {
    structuredContent: { file_uri: reference, size: pdf.length, workspace_path: source },
  };

  const tools = {
    async mcp__codex_apps__google_drive_fetch(args) {
      calls.push({ kind: "fetch", args });
      return typeof raw === "function"
        ? raw({ source, reference, workspace, outputDir, pdfBytes: pdf, args })
        : raw ?? defaultResponse;
    },
    async exec_command({ cmd, workdir }) {
      calls.push({ kind: "command", cmd, workdir });
      if (cmd.startsWith("/bin/mkdir -p ") || cmd.startsWith("/bin/test ! -e ")) {
        return runLocalCommand(cmd, workdir);
      }
      if (cmd.startsWith("/usr/bin/perl -e ")) {
        return runLocalCommand(cmd, workdir);
      }
      if (cmd.startsWith("/usr/bin/perl ") && cmd.includes("slides-stdin-receiver.pl")) {
        return { session_id: 41, output: "SLIDES_BRIDGE_READY\n" };
      }
      if (cmd.includes(" -png -r ")) return { exit_code: 0, output: "" };
      if (cmd.startsWith("/usr/bin/find ")) {
        return { exit_code: 0, output: `${outputDir}/slide-1.png\n` };
      }
      assert.fail(`Unexpected command: ${cmd}`);
    },
  };

  if (includeLegacyReceiver) {
    tools.write_stdin = async ({ chars }) => {
      if (chars.startsWith("D\t")) {
        const [, , encoded] = chars.slice(0, -1).split("\t");
        frames.push(Buffer.from(encoded, "base64"));
        return { exit_code: null, output: "" };
      }
      if (chars === "C\u0003") {
        const bytes = Buffer.concat(frames);
        await writeFile(join(outputDir, "presentation.pdf"), bytes, { flag: "wx" });
        const sha256 = createHash("sha256").update(bytes).digest("hex");
        return {
          exit_code: 0,
          output: `SLIDES_BRIDGE_COMMITTED ${bytes.length} ${sha256}\n`,
        };
      }
      assert.fail(`Unexpected legacy receiver frame: ${chars}`);
    };
  }

  const render = (overrides = {}) => exportAndRenderSlides({
    presentationId: "native-presentation",
    outputDir,
    workspaceRoot: workspace,
    skillRoot: "/trusted/google-slides",
    pdftoppmPath: "/usr/bin/pdftoppm",
    tools,
    ...overrides,
  });

  return { workspace, source, outputDir, reference, tools, calls, render };
}

test("renders a materialized reference-only PDF without inline content", async (t) => {
  const fixture = await createFixture(t);
  const result = await fixture.render();

  assert.equal(result.status, "complete");
  assert.deepEqual(result.pdf, {
    path: join(fixture.outputDir, "presentation.pdf"),
    bytes: pdfBytes.length,
    sha256: pdfSha256,
  });
  assert.deepEqual(await readFile(result.pdf.path), pdfBytes);
  assert.deepEqual(result.images, [{
    page: 1,
    path: join(fixture.outputDir, "slide-1.png"),
  }]);
  assert.equal(result.connectorTool, "mcp__codex_apps__google_drive_fetch");
  assert.deepEqual(fixture.calls.filter((call) => call.kind === "fetch"), [{
    kind: "fetch",
    args: {
      url: "https://docs.google.com/presentation/d/native-presentation",
      download_raw_file: true,
      raw_export_mime_type: "application/pdf",
      include_base64: false,
    },
  }]);
  assert.equal(typeof fixture.tools.write_stdin, "undefined");
});

test("preserves a Fiber workspace_path from the outer result envelope", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ source, reference }) => ({
      workspace_path: source,
      structuredContent: { result: { file_uri: reference, size: pdfBytes.length } },
    }),
  });

  const result = await fixture.render();
  assert.deepEqual(await readFile(result.pdf.path), pdfBytes);
  assert.equal(result.pdf.sha256, pdfSha256);
});

test("renders an oversized native PDF through canonical raw fetch", async (t) => {
  const largePdf = createOversizedPdf();
  const fixture = await createFixture(t, { pdf: largePdf });

  const result = await fixture.render();

  assert.deepEqual(await readFile(result.pdf.path), largePdf);
  assert.equal(result.pdf.bytes, largePdf.length);
  assert.equal(result.pdf.sha256, createHash("sha256").update(largePdf).digest("hex"));
  assert.equal(result.connectorTool, "mcp__codex_apps__google_drive_fetch");
  assert.deepEqual(fixture.calls.filter((call) => call.kind === "fetch"), [{
    kind: "fetch",
    args: {
      url: "https://docs.google.com/presentation/d/native-presentation",
      download_raw_file: true,
      raw_export_mime_type: "application/pdf",
      include_base64: false,
    },
  }]);
  assert.equal(typeof fixture.tools.write_stdin, "undefined");
});

test("prefers a materialized raw file over duplicate inline base64", async (t) => {
  const inlinePdf = Buffer.from("%PDF-1.7\ninline fallback must not win\n%%EOF\n");
  const fixture = await createFixture(t, {
    raw: ({ source, reference }) => ({
      structuredContent: {
        file_uri: reference,
        workspace_path: source,
        size: pdfBytes.length,
        content: inlinePdf.toString("base64"),
        mimeType: "application/pdf",
        base64Encoded: true,
      },
    }),
  });

  const result = await fixture.render();

  assert.deepEqual(await readFile(result.pdf.path), pdfBytes);
  assert.equal(result.pdf.sha256, pdfSha256);
  assert.equal(result.connectorTool, "mcp__codex_apps__google_drive_fetch");
  assert.deepEqual(fixture.calls.filter((call) => call.kind === "fetch"), [{
    kind: "fetch",
    args: {
      url: "https://docs.google.com/presentation/d/native-presentation",
      download_raw_file: true,
      raw_export_mime_type: "application/pdf",
      include_base64: false,
    },
  }]);
  assert.equal(typeof fixture.tools.write_stdin, "undefined");
});

test("rejects an invalid presentation ID before raw fetch", async (t) => {
  const fixture = await createFixture(t);

  await assert.rejects(
    fixture.render({
      presentationId: "native-presentation?credential=secret",
    }),
    /presentationId is invalid for a canonical raw fetch/,
  );
  assert.equal(fixture.calls.length, 0);
});

test("rejects an unmaterialized raw-fetch response", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ reference }) => ({
      structuredContent: {
        file_uri: reference,
      },
    }),
  });

  await assert.rejects(
    fixture.render(),
    /not materialized to workspace_path/,
  );
});

test("verifies raw-fetch file_size_bytes against the materialized PDF", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ source, reference }) => ({
      structuredContent: {
        file_uri: reference,
        workspace_path: source,
        file_size_bytes: pdfBytes.length + 1,
      },
    }),
  });

  await assert.rejects(
    fixture.render(),
    /does not match its declared byte length/,
  );
});

test("retries older fetch workers and consumes legacy b64_string during rollout", async (t) => {
  const fixture = await createFixture(t, {
    includeLegacyReceiver: true,
    raw: ({ args }) => args.include_base64 === false
      ? {
          isError: true,
          content: [{ type: "text", text: "InvalidActionArgumentsError: Invalid action arguments" }],
          structuredContent: { error_code: "INVALID_ARGUMENT" },
        }
      : {
          b64_string: pdfBytes.toString("base64"),
          structuredContent: {
            content: "Extracted PDF text that is not base64.",
            mime_type: "application/pdf",
          },
        },
  });

  const result = await fixture.render();
  assert.deepEqual(await readFile(result.pdf.path), pdfBytes);
  assert.equal(result.pdf.sha256, pdfSha256);
  assert.deepEqual(fixture.calls.filter((call) => call.kind === "fetch"), [
    {
      kind: "fetch",
      args: {
        url: "https://docs.google.com/presentation/d/native-presentation",
        download_raw_file: true,
        raw_export_mime_type: "application/pdf",
        include_base64: false,
      },
    },
    {
      kind: "fetch",
      args: {
        url: "https://docs.google.com/presentation/d/native-presentation",
        download_raw_file: true,
        raw_export_mime_type: "application/pdf",
      },
    },
  ]);
  assert.ok(fixture.calls.some((call) => call.cmd?.includes("slides-stdin-receiver.pl")));
});

test("ignores null file reference placeholders in legacy exports", async (t) => {
  const fixture = await createFixture(t, {
    includeLegacyReceiver: true,
    raw: {
      structuredContent: {
        content: pdfBytes.toString("base64"),
        mimeType: "application/pdf",
        base64Encoded: true,
        file_uri: null,
      },
    },
  });

  const result = await fixture.render();
  assert.deepEqual(await readFile(result.pdf.path), pdfBytes);
  assert.equal(result.pdf.sha256, pdfSha256);
  assert.ok(fixture.calls.some((call) => call.cmd?.includes("slides-stdin-receiver.pl")));
});

test("falls back to inline base64 when Fiber did not materialize a reference", async (t) => {
  const fixture = await createFixture(t, {
    includeLegacyReceiver: true,
    raw: ({ reference }) => ({
      b64_string: pdfBytes.toString("base64"),
      structuredContent: {
        result: {
          file_uri: reference,
          mime_type: "application/pdf",
        },
      },
    }),
  });

  const result = await fixture.render();
  assert.deepEqual(await readFile(result.pdf.path), pdfBytes);
  assert.equal(result.pdf.sha256, pdfSha256);
  assert.ok(fixture.calls.some((call) => call.cmd?.includes("slides-stdin-receiver.pl")));
});

test("rejects a materialized path outside the trusted workspace", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ reference }) => ({
      structuredContent: {
        file_uri: reference,
        workspace_path: "/private/unrelated/presentation.pdf",
      },
    }),
  });

  await assert.rejects(fixture.render(), /must stay within the task workspace/);
});

test("rejects a materialized export with a non-PDF MIME type", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ source, reference }) => ({
      structuredContent: {
        file_uri: { ...reference, mime_type: "text/plain" },
        workspace_path: source,
      },
    }),
  });

  await assert.rejects(fixture.render(), /text\/plain instead of application\/pdf/);
});

test("rejects PDFs exceeding the 32 MiB renderer limit", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ source, reference }) => ({
      structuredContent: {
        file_uri: reference,
        workspace_path: source,
        size: 32 * 1024 * 1024 + 1,
      },
    }),
  });

  await assert.rejects(fixture.render(), /limit is 33554432/);
});

test("verifies the materialized file starts with a real PDF header", async (t) => {
  const fixture = await createFixture(t);
  await writeFile(fixture.source, Buffer.alloc(pdfBytes.length, "x"));

  await assert.rejects(fixture.render(), /does not contain a PDF header/);
});

test("does not overwrite an existing presentation PDF", async (t) => {
  const fixture = await createFixture(t);
  await runLocalCommand(`/bin/mkdir -p '${fixture.outputDir}'`, fixture.workspace);
  const existing = Buffer.from("preserve-existing-pdf");
  await writeFile(join(fixture.outputDir, "presentation.pdf"), existing);

  await assert.rejects(fixture.render(), /refusing to overwrite an existing PDF/);
  assert.deepEqual(await readFile(join(fixture.outputDir, "presentation.pdf")), existing);
});

test("rejects a symlink instead of following a materialized source", async (t) => {
  const fixture = await createFixture(t);
  const original = join(fixture.workspace, "original.pdf");
  await writeFile(original, pdfBytes);
  await rm(fixture.source);
  await symlink(original, fixture.source);

  await assert.rejects(fixture.render(), /materialized PDF path must not include symlinks/);
});

test("rejects a symlinked intermediate materialized source directory", async (t) => {
  const fixture = await createFixture(t);
  const actualResults = join(fixture.workspace, "actual-results");
  await rm(join(fixture.workspace, "connector-results"), { recursive: true, force: true });
  await mkdir(actualResults);
  await writeFile(join(actualResults, "presentation.pdf"), pdfBytes);
  await symlink(actualResults, join(fixture.workspace, "connector-results"));

  await assert.rejects(fixture.render(), /materialized PDF path must not include symlinks/);
});

test("rejects a symlinked output directory component", async (t) => {
  const fixture = await createFixture(t);
  const actualRenders = join(fixture.workspace, "actual-renders");
  await mkdir(actualRenders);
  await symlink(actualRenders, fixture.outputDir);

  await assert.rejects(fixture.render(), /output path must not include symlinks/);
});

test("rejects a symlinked legacy inline output directory component", async (t) => {
  const fixture = await createFixture(t, {
    includeLegacyReceiver: true,
    raw: {
      structuredContent: {
        content: pdfBytes.toString("base64"),
        mimeType: "application/pdf",
        base64Encoded: true,
      },
    },
  });
  const actualRenders = join(fixture.workspace, "actual-renders");
  await mkdir(actualRenders);
  await symlink(actualRenders, fixture.outputDir);

  await assert.rejects(
    fixture.render(),
    /legacy PDF output path must not include symlinks/,
  );
});

test("rejects a materialized file that disagrees with its declared size", async (t) => {
  const fixture = await createFixture(t, {
    raw: ({ source, reference }) => ({
      structuredContent: {
        file_uri: reference,
        workspace_path: source,
        size: pdfBytes.length + 1,
      },
    }),
  });

  await assert.rejects(fixture.render(), /does not match its declared byte length/);
});
