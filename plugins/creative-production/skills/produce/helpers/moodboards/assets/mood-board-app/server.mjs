import { createReadStream } from "node:fs";
import { access } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const requestedPort = Number(process.env.PORT || 8794);
const maxAttempts = Number(process.env.CREATIVE_PRODUCTION_PORT_ATTEMPTS || 20);
const mimeTypes = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".png", "image/png"],
  [".svg", "image/svg+xml; charset=utf-8"],
  [".webp", "image/webp"],
]);
let port = requestedPort;

async function exists(filePath) {
  try { await access(filePath); return true; } catch { return false; }
}

async function serve(req, res) {
  const url = new URL(req.url, `http://127.0.0.1:${port}`);
  const normalized = url.pathname === "/" ? "/index.html" : url.pathname;
  const relative = path.normalize(normalized).replace(/^([/\\]*\.\.[/\\])+/, "").replace(/^[/\\]+/, "");
  let filePath = path.join(root, relative);
  if (!filePath.startsWith(`${root}${path.sep}`)) {
    res.writeHead(403).end("Forbidden");
    return;
  }
  if (normalized.startsWith("/components/empty-state-grid/assets/") && normalized.endsWith(".webp") && !(await exists(filePath))) {
    filePath = filePath.slice(0, -5) + ".svg";
  }
  if (!(await exists(filePath))) {
    res.writeHead(404).end("Not found");
    return;
  }
  res.writeHead(200, {
    "Content-Type": mimeTypes.get(path.extname(filePath)) || "application/octet-stream",
    "Cache-Control": "no-store",
  });
  createReadStream(filePath).pipe(res);
}

const server = http.createServer((req, res) => {
  if (req.method !== "GET") {
    res.writeHead(405).end("Method not allowed");
    return;
  }
  void serve(req, res).catch((error) => {
    res.writeHead(500).end(error.message);
  });
});

function listen(nextPort = requestedPort, remaining = maxAttempts) {
  port = nextPort;
  server.once("error", (error) => {
    if (error.code === "EADDRINUSE" && !process.env.PORT && remaining > 0) {
      listen(nextPort + 1, remaining - 1);
      return;
    }
    process.stderr.write(`${error.stack || error}\n`);
    process.exitCode = 1;
  });
  server.listen(port, "127.0.0.1", () => {
    process.stdout.write(`Creative Production preview: http://127.0.0.1:${port}\n`);
  });
}

listen();
