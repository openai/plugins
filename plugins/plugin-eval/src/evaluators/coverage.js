import fs from "node:fs/promises";
import path from "node:path";

import { createArtifact, createCheck, createMetric } from "../core/schema.js";
import { pathExists, readJson, readText, relativePath } from "../lib/files.js";

async function findCoverageFiles(rootPath) {
  const results = [];
  const ignored = new Set([".git", "node_modules", ".venv", "venv", "__pycache__"]);

  async function visit(currentPath) {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        if (ignored.has(entry.name)) {
          continue;
        }
        await visit(entryPath);
        continue;
      }
      if (
        entry.isFile() &&
        ["lcov.info", "coverage.xml", "coverage-final.json", "coverage-summary.json"].includes(entry.name)
      ) {
        results.push(entryPath);
      }
    }
  }

  await visit(rootPath);
  return results.sort();
}

async function parseLcov(filePath) {
  const text = await readText(filePath);
  let found = 0;
  let hit = 0;
  for (const line of text.split("\n")) {
    if (line.startsWith("LF:")) {
      found += Number(line.slice(3));
    } else if (line.startsWith("LH:")) {
      hit += Number(line.slice(3));
    }
  }
  return found > 0 ? Number(((hit / found) * 100).toFixed(2)) : null;
}

async function parseCoverageXml(filePath) {
  const text = await readText(filePath);
  const lineRateMatch = /line-rate="([^"]+)"/.exec(text);
  if (lineRateMatch) {
    return Number((Number(lineRateMatch[1]) * 100).toFixed(2));
  }
  const coveredMatch = /lines-covered="([^"]+)"/.exec(text);
  const validMatch = /lines-valid="([^"]+)"/.exec(text);
  if (coveredMatch && validMatch && Number(validMatch[1]) > 0) {
    return Number(((Number(coveredMatch[1]) / Number(validMatch[1])) * 100).toFixed(2));
  }
  return null;
}

async function parseCoverageJson(filePath) {
  const payload = await readJson(filePath);
  if (payload.total?.lines?.pct != null) {
    return Number(payload.total.lines.pct);
  }

  const fileEntries = Object.values(payload).filter((value) => value && typeof value === "object" && value.s);
  let totalStatements = 0;
  let coveredStatements = 0;
  for (const entry of fileEntries) {
    for (const count of Object.values(entry.s)) {
      totalStatements += 1;
      if (Number(count) > 0) {
        coveredStatements += 1;
      }
    }
  }
  if (totalStatements === 0) {
    return null;
  }
  return Number(((coveredStatements / totalStatements) * 100).toFixed(2));
}

async function parseCoverageFile(filePath) {
  if (filePath.endsWith("lcov.info")) {
    return parseLcov(filePath);
  }
  if (filePath.endsWith("coverage.xml")) {
    return parseCoverageXml(filePath);
  }
  if (filePath.endsWith(".json")) {
    return parseCoverageJson(filePath);
  }
  return null;
}

export async function analyzeCoverageArtifacts(rootPath) {
  const checks = [];
  const metrics = [];
  const artifacts = [];
  const coverageFiles = await findCoverageFiles(rootPath);

  metrics.push(
    createMetric({
      id: "coverage_artifact_count",
      category: "coverage",
      value: coverageFiles.length,
      unit: "files",
      band: coverageFiles.length > 0 ? "good" : "info",
    }),
  );

  if (coverageFiles.length === 0) {
    checks.push(
      createCheck({
        id: "coverage-artifacts-unavailable",
        category: "coverage",
        severity: "info",
        status: "info",
        message: "No coverage artifacts were found for this target.",
        evidence: [relativePath(process.cwd(), rootPath)],
        remediation: ["Generate `lcov.info`, `coverage.xml`, or an Istanbul coverage JSON file if you want coverage scoring."],
      }),
    );
    return { checks, metrics, artifacts };
  }

  const fileSummaries = [];
  for (const filePath of coverageFiles) {
    const coverage = await parseCoverageFile(filePath);
    if (coverage != null) {
      fileSummaries.push({
        path: relativePath(rootPath, filePath),
        coverage,
      });
    }
  }

  if (fileSummaries.length > 0) {
    const bestCoverage = Math.max(...fileSummaries.map((item) => item.coverage));
    metrics.push(
      createMetric({
        id: "coverage_percent",
        category: "coverage",
        value: bestCoverage,
        unit: "percent",
        band: bestCoverage >= 85 ? "good" : bestCoverage >= 70 ? "moderate" : "heavy",
      }),
    );
    if (bestCoverage < 70) {
      checks.push(
        createCheck({
          id: "coverage-low",
          category: "coverage",
          severity: "warning",
          status: "warn",
          message: "Coverage artifacts were found, but the measured coverage is low.",
          evidence: fileSummaries.map((item) => `${item.path}: ${item.coverage}%`),
          remediation: ["Increase test coverage on the code that carries the most complexity or risk."],
        }),
      );
    }
  }

  artifacts.push(
    createArtifact({
      id: "coverage-artifacts",
      type: "coverage",
      label: "Coverage artifacts",
      description: "Coverage files discovered during evaluation.",
      data: {
        files: fileSummaries,
      },
    }),
  );

  return { checks, metrics, artifacts };
}
