#!/usr/bin/env node

import { pathToFileURL } from "node:url";

const RESOURCE_TYPES = new Map([
  ["document", "document"],
  ["spreadsheets", "spreadsheet"],
  ["presentation", "presentation"],
]);

const LOCATION_KEYS = new Set([
  "bookmark",
  "gid",
  "heading",
  "range",
  "slide",
  "tab",
]);

function parseUrl(value) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new TypeError("A non-empty Google Workspace URL is required.");
  }
  let parsed;
  try {
    parsed = new URL(value.trim());
  } catch {
    throw new TypeError("The supplied value is not a valid absolute URL.");
  }
  if (/(^|\.)google\.com$/i.test(parsed.hostname) && parsed.pathname === "/url") {
    const target = parsed.searchParams.get("q") ?? parsed.searchParams.get("url");
    if (!target) throw new TypeError("Google redirect URL does not contain a target.");
    try {
      parsed = new URL(target);
    } catch {
      throw new TypeError("Google redirect target is not a valid absolute URL.");
    }
  }
  return parsed;
}

function hasLocationIntent(url) {
  for (const key of url.searchParams.keys()) {
    if (LOCATION_KEYS.has(key.toLowerCase())) return true;
  }
  let hash = url.hash.slice(1);
  try {
    hash = decodeURIComponent(hash);
  } catch {
    // Retain the original hash when it contains malformed escaping.
  }
  return /(?:^|[?&#])(bookmark|gid|heading|range|slide|tab)=/i.test(hash);
}

export function canonicalizeGoogleWorkspaceUrl(value) {
  const parsed = parseUrl(value);
  if (parsed.protocol !== "https:" || parsed.hostname.toLowerCase() !== "docs.google.com") {
    throw new TypeError("URL is not a supported Google Docs, Sheets, or Slides URL.");
  }

  const segments = parsed.pathname.split("/").filter(Boolean);
  const resourceSegment = segments[0];
  const resourceType = RESOURCE_TYPES.get(resourceSegment);
  const dIndex = segments.indexOf("d");
  const fileId = dIndex >= 0 ? segments[dIndex + 1] : null;
  if (!resourceType || !fileId || !/^[A-Za-z0-9_-]+$/.test(fileId)) {
    throw new TypeError("URL does not contain a supported Google Workspace file ID.");
  }

  const canonicalUri = `https://docs.google.com/${resourceSegment}/d/${fileId}/edit`;
  const unwrappedUri = parsed.toString();
  const locationSpecific = hasLocationIntent(parsed);

  return {
    kind: "google-workspace-rich-link-target",
    resourceType,
    fileId,
    canonicalUri,
    deepLinkUri: locationSpecific ? unwrappedUri : null,
    originalUri: value.trim(),
    unwrappedUri,
  };
}

function main(args) {
  if (args.length === 0) {
    throw new TypeError("Usage: canonicalize_google_workspace_url.mjs <url> [url ...]");
  }
  const results = args.map(canonicalizeGoogleWorkspaceUrl);
  process.stdout.write(`${JSON.stringify(results.length === 1 ? results[0] : results, null, 2)}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    main(process.argv.slice(2));
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
