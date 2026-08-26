import { createHash, randomBytes } from "node:crypto";
import { execFile } from "node:child_process";
import { createReadStream } from "node:fs";
import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const port = Number(process.env.PORT || 8798);
const runToken = process.env.BV_RUN_TOKEN || randomBytes(24).toString("base64url");
const dataDir = path.join(__dirname, "data");
const pluginRoot = process.env.CREATIVE_PRODUCTION_PLUGIN_ROOT || "";
const imageGenerationRunner = process.env.CREATIVE_PRODUCTION_IMAGE_GENERATION_RUNNER || "";
const pythonBin = process.env.CREATIVE_PRODUCTION_PYTHON || "python3";
const generationWorkspace = process.env.CREATIVE_PRODUCTION_WORKSPACE || "";
const imageMaxConcurrency = positiveInteger(process.env.CREATIVE_PRODUCTION_IMAGE_MAX_CONCURRENCY, 64);
const imageMaxAttempts = process.env.CREATIVE_PRODUCTION_IMAGE_MAX_ATTEMPTS || "2";
const imageTimeoutSeconds = process.env.CREATIVE_PRODUCTION_IMAGE_TIMEOUT_SECONDS || "600";
const generatedDir = path.join(__dirname, "generated");

await fs.mkdir(generatedDir, { recursive: true });
await fs.mkdir(dataDir, { recursive: true });

function positiveInteger(value, fallback) {
  const parsed = Number(value);
  if (Number.isInteger(parsed) && parsed > 0) return parsed;
  return fallback;
}

const mimeTypes = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".md", "text/markdown; charset=utf-8"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".webp", "image/webp"],
  [".svg", "image/svg+xml; charset=utf-8"]
]);

function corsHeaders(req) {
  const origin = req.headers.origin;
  const allowedOrigins = new Set([
    `http://127.0.0.1:${port}`,
    `http://localhost:${port}`,
  ]);
  if (!origin || !allowedOrigins.has(origin)) return {};
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "content-type,x-bv-run-token",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Vary": "Origin",
  };
}

function hostIsAllowed(req) {
  const host = req.headers.host;
  return !host || host === `127.0.0.1:${port}` || host === `localhost:${port}`;
}

function originIsAllowed(req) {
  const origin = req.headers.origin;
  return !origin || origin === `http://127.0.0.1:${port}` || origin === `http://localhost:${port}`;
}

function rejectUnsafeRequest(req, res) {
  if (!hostIsAllowed(req) || !originIsAllowed(req)) {
    sendJson(req, res, 403, { error: "Request origin is not allowed." });
    return true;
  }
  return false;
}

function requireRunToken(req, res) {
  if (req.headers["x-bv-run-token"] !== runToken) {
    sendJson(req, res, 403, { error: "Missing or invalid Creative Production run token." });
    return false;
  }
  return true;
}

function injectRunToken(html) {
  const script = `<script>window.BV_RUN_TOKEN=${JSON.stringify(runToken)};</script>`;
  if (html.includes("</head>")) return html.replace("</head>", `  ${script}\n</head>`);
  return `${script}\n${html}`;
}

function send(req, res, status, body, contentType = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": contentType,
    ...corsHeaders(req),
  });
  res.end(body);
}

function sendJson(req, res, status, body) {
  send(req, res, status, JSON.stringify(body), "application/json; charset=utf-8");
}

async function readJson(req) {
  let body = "";
  for await (const chunk of req) body += chunk;
  return JSON.parse(body || "{}");
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function cacheName(route) {
  const key = createHash("sha256")
    .update(JSON.stringify({
      id: route.id,
      prompt: route.prompt
    }))
    .digest("hex")
    .slice(0, 32);
  return `${key}.png`;
}

async function generateRoute(route) {
  if (!route?.id || !route?.prompt) {
    throw new Error("Each route needs an id and prompt.");
  }

  const filename = cacheName(route);
  const filePath = path.join(generatedDir, filename);

  if (!(await fileExists(filePath))) {
    await runImageGenerationJobs([{ id: route.id, prompt: route.prompt, output: filename }]);
  }

  return {
    id: route.id,
    url: `/generated/${filename}`
  };
}

async function runImageGenerationJobs(jobs) {
  if (!imageGenerationRunner) {
    throw new Error("Image generation is not configured. Missing CREATIVE_PRODUCTION_IMAGE_GENERATION_RUNNER.");
  }
  if (!(await fileExists(imageGenerationRunner))) {
    throw new Error(`Configured image generation runner does not exist: ${imageGenerationRunner}`);
  }
  if (!generationWorkspace) {
    throw new Error("Image generation is not configured. Missing CREATIVE_PRODUCTION_WORKSPACE.");
  }
  const batchId = createHash("sha256").update(JSON.stringify(jobs)).digest("hex").slice(0, 16);
  const batchDir = path.join(generatedDir, ".image-generation", batchId);
  await fs.mkdir(batchDir, { recursive: true });
  const jobFile = path.join(batchDir, "jobs.jsonl");
  await fs.writeFile(jobFile, `${jobs.map((job) => JSON.stringify(job)).join("\n")}\n`, "utf8");
  const effectiveImageMaxConcurrency = Math.min(jobs.length, imageMaxConcurrency);
  await new Promise((resolve, reject) => {
    execFile(
      pythonBin,
      [
        imageGenerationRunner,
        "--input", jobFile,
        "--out-dir", batchDir,
        "--workspace", generationWorkspace,
        "--max-concurrency", String(effectiveImageMaxConcurrency),
        "--max-attempts", imageMaxAttempts,
        "--timeout-seconds", imageTimeoutSeconds,
      ],
      { cwd: pluginRoot || process.cwd() },
      (error, stdout, stderr) => {
        if (error) {
          reject(new Error(stderr || stdout || error.message));
          return;
        }
        resolve();
      }
    );
  });
  const summary = JSON.parse(await fs.readFile(path.join(batchDir, "image-generation-results.json"), "utf8"));
  for (const result of summary.results || []) {
    if (result.status !== "complete" || !result.image_path) {
      throw new Error(result.error || "Image generation failed.");
    }
    const job = jobs.find((item) => item.id === result.id);
    await fs.copyFile(result.image_path, path.join(generatedDir, job?.output || path.basename(result.image_path)));
  }
}

async function readSpecWithCachedImages() {
  const content = await fs.readFile(path.join(dataDir, "style-spec.json"), "utf8");
  const spec = JSON.parse(content);
  spec.routes = await Promise.all((spec.routes || []).map(async (route) => {
    const filename = cacheName(route);
    const filePath = path.join(generatedDir, filename);
    if (await fileExists(filePath)) {
      return { ...route, imageUrl: `/generated/${filename}` };
    }
    return route;
  }));
  return spec;
}

function markdownFromHandoff(handoff) {
  const selected = handoff.selected_style_route;
  const rejected = handoff.rejected_directions || [];
  const preserve = handoff.prompt_style_metadata?.preserve || [];
  const avoid = handoff.prompt_style_metadata?.avoid || [];
  return [
    `# ${handoff.meta?.title || "Style Explorer Handoff"}`,
    "",
    `Anchor: ${handoff.meta?.anchor || "unspecified"}`,
    `Final owner: ${handoff.final_owner || "produce"}`,
    "",
    "## Selected Style Route",
    selected ? `- ${selected.label || selected.id}: ${selected.rationale || selected.prompt || ""}` : "- None selected",
    "",
    "## Rejected Directions",
    rejected.length ? rejected.map((item) => `- ${item.label || item.id}`).join("\n") : "- None",
    "",
    "## Preserve",
    preserve.length ? preserve.map((item) => `- ${item}`).join("\n") : "- None specified",
    "",
    "## Avoid",
    avoid.length ? avoid.map((item) => `- ${item}`).join("\n") : "- None specified",
    ""
  ].join("\n");
}

async function persistFeedback(handoff) {
  await fs.writeFile(
    path.join(dataDir, "selected-style-route.json"),
    JSON.stringify(handoff, null, 2) + "\n",
    "utf8"
  );
  await fs.writeFile(path.join(dataDir, "handoff.md"), markdownFromHandoff(handoff), "utf8");
  return {
    json: "/data/selected-style-route.json",
    markdown: "/data/handoff.md"
  };
}

async function serveFile(req, res, pathname) {
  const normalized = pathname === "/" ? "/index.html" : pathname;
  const safePath = path.normalize(normalized).replace(/^(\.\.[/\\])+/, "");
  const filePath = path.join(__dirname, safePath);

  if (!filePath.startsWith(__dirname) || !(await fileExists(filePath))) {
    send(req, res, 404, "Not found");
    return;
  }

  const ext = path.extname(filePath);
  if (ext === ".html") {
    send(req, res, 200, injectRunToken(await fs.readFile(filePath, "utf8")), mimeTypes.get(ext));
    return;
  }

  res.writeHead(200, {
    "Content-Type": mimeTypes.get(ext) || "application/octet-stream",
    "Cache-Control": normalized.startsWith("/generated/") ? "public, max-age=31536000, immutable" : "no-cache",
    ...corsHeaders(req),
  });
  createReadStream(filePath).pipe(res);
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "OPTIONS") {
      if (rejectUnsafeRequest(req, res)) return;
      sendJson(req, res, 204, {});
      return;
    }

    const url = new URL(req.url, `http://127.0.0.1:${port}`);

    if (rejectUnsafeRequest(req, res)) return;

    if (req.method === "GET" && url.pathname === "/api/spec") {
      sendJson(req, res, 200, await readSpecWithCachedImages());
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/session") {
      sendJson(req, res, 200, { runToken });
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/image") {
      if (!requireRunToken(req, res)) return;
      const body = await readJson(req);
      if (body.confirmGenerate !== true) {
        sendJson(req, res, 400, { error: "Image generation requires confirmGenerate: true." });
        return;
      }
      sendJson(req, res, 200, await generateRoute(body.route));
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/feedback") {
      if (!requireRunToken(req, res)) return;
      const body = await readJson(req);
      sendJson(req, res, 200, await persistFeedback(body));
      return;
    }

    if (req.method === "GET") {
      await serveFile(req, res, url.pathname);
      return;
    }

    send(req, res, 405, "Method not allowed");
  } catch (error) {
    sendJson(req, res, 500, { error: error.message || "Unknown server error." });
  }
});

server.listen(port, "127.0.0.1", () => {
  console.log(`Style Explorer: http://127.0.0.1:${port}`);
  console.log(`Image generation runner: ${imageGenerationRunner}`);
});
