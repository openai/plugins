import { readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { gzipSync } from "node:zlib";

const pluginRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const assetDir = resolve(pluginRoot, "assets");
const maxChunkChars = 120_000;
const widgetAssets = [
  "datascience-artifact-widget.html",
  "datascience-chart-widget.html",
  "datascience-table-widget.html",
  "portable-artifact-reader.html",
];

for (const asset of widgetAssets) {
  const path = resolve(assetDir, asset);
  const html = readFileSync(path, "utf8");
  assertBuiltWidgetHtml(asset, html);
  const normalized = sanitizePublicCopy(html).replace(/[ \t]+$/gm, "");
  const encoded = gzipSync(Buffer.from(normalized, "utf8"), { level: 9 }).toString("base64");
  const prefix = `${asset}.gz.b64.part`;

  for (const name of readdirSync(assetDir)) {
    if (name.startsWith(prefix)) rmSync(resolve(assetDir, name));
  }

  for (let offset = 0, index = 1; offset < encoded.length; offset += maxChunkChars, index += 1) {
    const chunk = encoded.slice(offset, offset + maxChunkChars);
    const chunkName = `${prefix}${String(index).padStart(3, "0")}`;
    writeFileSync(resolve(assetDir, chunkName), `${chunk}\n`);
  }

  writeFileSync(path, localDevRedirect(asset));
}

function assertBuiltWidgetHtml(asset, html) {
  if (html.includes("Redirecting to the local widget source") || html.includes("window.location.replace(target)")) {
    throw new Error(
      `${asset} is still the local development redirect; run npm run build before npm run normalize:assets`,
    );
  }
}

function sanitizePublicCopy(html) {
  return html
    .replace(/\bInternal error\b/g, "Widget error")
    .replace(/\binternal error\b/g, "widget error")
    .replace(/\bInternal\b/g, "Implementation")
    .replace(/\binternal\b/g, "implementation");
}

function localDevRedirect(asset) {
  const title = asset.includes("portable-artifact")
    ? "Data Analytics portable artifact reader"
    : asset.includes("artifact")
    ? "Data Analytics artifact app"
    : asset.includes("table")
      ? "Data Analytics table widget"
      : "Data Analytics chart widget";
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>${title}</title>
    <script type="module">
      const target = new URL("../src/${asset}", import.meta.url);
      target.search = window.location.search;
      window.location.replace(target);
    </script>
  </head>
  <body>
    <p>Redirecting to the local widget source for development.</p>
    <p><a href="../src/${asset}">Open ${title}</a></p>
  </body>
</html>
`;
}
