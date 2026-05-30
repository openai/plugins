#!/usr/bin/env node

import fs from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const pptxgen = require("pptxgenjs");

const SLIDE_WIDTH = 13.333;
const SLIDE_HEIGHT = 7.5;
const SLIDE_MARGIN = 0.35;

function parseArgs(argv) {
  const args = { format: "pdf" };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--input") args.input = argv[++index];
    else if (token === "--format") args.format = argv[++index];
    else if (token === "--output") args.output = argv[++index];
    else if (token === "--output-dir") args.outputDir = argv[++index];
  }
  if (!args.input) throw new Error("Missing --input <html>");
  if (!["pdf", "pptx", "both"].includes(args.format)) {
    throw new Error(`Unsupported --format ${args.format}`);
  }
  return args;
}

function inputPath(value) {
  if (value.startsWith("file://")) {
    return new URL(value);
  }
  if (/^https?:\/\//.test(value)) {
    return value;
  }
  return pathToFileURL(path.resolve(value));
}

function outputPath(args, format) {
  if (args.output) return path.resolve(args.output);
  const rawInput = args.input.startsWith("file://") ? new URL(args.input).pathname : args.input;
  const input = /^https?:\/\//.test(args.input) ? "report.html" : rawInput;
  const parsed = path.parse(input);
  const directory = args.outputDir ? path.resolve(args.outputDir) : parsed.dir || process.cwd();
  return path.join(directory, `${parsed.name}.${format}`);
}

function cachedHeadlessShellPath() {
  const cacheRoot = path.join(os.homedir(), "Library", "Caches", "ms-playwright");
  if (!fs.existsSync(cacheRoot)) return null;
  const candidates = fs.readdirSync(cacheRoot)
    .filter(name => name.startsWith("chromium_headless_shell-"))
    .sort((left, right) => {
      const leftVersion = Number(left.split("-").pop());
      const rightVersion = Number(right.split("-").pop());
      return rightVersion - leftVersion;
    });
  for (const name of candidates) {
    const candidate = path.join(
      cacheRoot,
      name,
      "chrome-headless-shell-mac-arm64",
      "chrome-headless-shell",
    );
    if (fs.existsSync(candidate)) return candidate;
  }
  return null;
}

async function launchBrowser() {
  try {
    return await chromium.launch({ headless: true });
  } catch (error) {
    const headlessShell = cachedHeadlessShellPath();
    if (headlessShell) {
      return chromium.launch({ executablePath: headlessShell, headless: true });
    }
    const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
    if (fs.existsSync(chromePath)) {
      return chromium.launch({ executablePath: chromePath, headless: true });
    }
    throw error;
  }
}

async function loadPage(browser, source) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
  await page.goto(inputPath(source).toString(), { waitUntil: "networkidle" });
  await page.addStyleTag({
    content: ".export-toolbar{display:none!important}body{background:#F6F5F4!important}",
  });
  return page;
}

async function exportPdf(page, destination) {
  await fs.promises.mkdir(path.dirname(destination), { recursive: true });
  await page.emulateMedia({ media: "print" });
  await page.pdf({
    path: destination,
    format: "Letter",
    printBackground: true,
    margin: { top: "0.3in", right: "0.25in", bottom: "0.3in", left: "0.25in" },
  });
  console.log(`Wrote PDF: ${destination}`);
}

function imageFit(box) {
  const maxWidth = SLIDE_WIDTH - SLIDE_MARGIN * 2;
  const maxHeight = SLIDE_HEIGHT - SLIDE_MARGIN * 2;
  let width = maxWidth;
  let height = width * (box.height / box.width);
  if (height > maxHeight) {
    height = maxHeight;
    width = height * (box.width / box.height);
  }
  return {
    x: (SLIDE_WIDTH - width) / 2,
    y: (SLIDE_HEIGHT - height) / 2,
    w: width,
    h: height,
  };
}

async function exportPptx(page, destination) {
  await fs.promises.mkdir(path.dirname(destination), { recursive: true });
  const tempDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), "morningstar-report-"));
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "Morningstar";
  pptx.subject = "Morningstar fund summary";
  pptx.company = "Morningstar";

  const elements = await page.$$(".header, .section, .footer");
  const targets = elements.length ? elements : [await page.$("body")];
  let slideCount = 0;

  for (const element of targets) {
    if (!element) continue;
    const box = await element.boundingBox();
    if (!box || box.width < 20 || box.height < 20) continue;
    const imagePath = path.join(tempDir, `slide-${slideCount + 1}.png`);
    await element.screenshot({ path: imagePath });

    const slide = pptx.addSlide();
    slide.background = { color: "F6F5F4" };
    slide.addImage({ path: imagePath, ...imageFit(box) });
    slideCount += 1;
  }

  if (slideCount === 0) throw new Error("No report sections were available for PPTX export");
  await pptx.writeFile({ fileName: destination });
  console.log(`Wrote PPTX: ${destination}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const browser = await launchBrowser();
  try {
    const page = await loadPage(browser, args.input);
    if (args.format === "pdf" || args.format === "both") {
      await exportPdf(page, outputPath(args, "pdf"));
    }
    if (args.format === "pptx" || args.format === "both") {
      await exportPptx(page, outputPath(args, "pptx"));
    }
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(`Export failed: ${error.message}`);
  process.exit(1);
});
