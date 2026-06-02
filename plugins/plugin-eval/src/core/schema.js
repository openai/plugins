import { relativePath } from "../lib/files.js";

export const TOOL_NAME = "plugin-eval";
export const TOOL_VERSION = "0.1.0";
export const SCHEMA_VERSION = 1;

export function createEvaluationResult(target) {
  return {
    schemaVersion: SCHEMA_VERSION,
    tool: {
      name: TOOL_NAME,
      version: TOOL_VERSION,
    },
    createdAt: new Date().toISOString(),
    target: {
      ...target,
      relativePath: relativePath(process.cwd(), target.path),
    },
    summary: {
      score: 0,
      grade: "F",
      riskLevel: "high",
      riskReasons: [],
      scoreBreakdown: {
        startingScore: 100,
        totalDeductions: 0,
        finalScore: 0,
      },
      checkCounts: {
        total: 0,
        pass: 0,
        warn: 0,
        fail: 0,
        info: 0,
        error: 0,
        warning: 0,
      },
      deductions: [],
      categoryDeductions: [],
      topRecommendations: [],
      whyBullets: [],
      fixFirst: [],
      watchNext: [],
    },
    budgets: {},
    observedUsage: null,
    checks: [],
    metrics: [],
    artifacts: [],
    extensions: [],
    measurementPlan: null,
    improvementBrief: null,
    nextAction: null,
  };
}

export function createCheck({
  id,
  category,
  severity,
  status,
  message,
  evidence = [],
  remediation = [],
  source = "core",
  targetPath = null,
  why = null,
}) {
  return {
    id,
    category,
    severity,
    status,
    message,
    evidence,
    remediation,
    source,
    ...(why ? { why } : {}),
    ...(targetPath ? { targetPath } : {}),
  };
}

export function createMetric({
  id,
  category,
  value,
  unit,
  band = "info",
  source = "core",
  targetPath = null,
}) {
  return {
    id,
    category,
    value,
    unit,
    band,
    source,
    ...(targetPath ? { targetPath } : {}),
  };
}

export function createArtifact({
  id,
  type,
  label,
  description,
  data = null,
  path = null,
  source = "core",
}) {
  return {
    id,
    type,
    label,
    description,
    source,
    ...(path ? { path } : {}),
    ...(data ? { data } : {}),
  };
}
