import { createArtifact, createCheck, createMetric } from "../core/schema.js";
import { readText, relativePath } from "../lib/files.js";

function countMatches(text, expression) {
  return (text.match(expression) || []).length;
}

function countDecisionPoints(text) {
  return (
    countMatches(text, /\bif\b/g) +
    countMatches(text, /\bfor\b/g) +
    countMatches(text, /\bwhile\b/g) +
    countMatches(text, /\bcase\b/g) +
    countMatches(text, /\bcatch\b/g) +
    countMatches(text, /&&/g) +
    countMatches(text, /\|\|/g) +
    countMatches(text, /\?/g)
  );
}

function detectFunctions(lines) {
  const functions = [];
  const startMatchers = [
    /\b(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(([^)]*)\)\s*\{/,
    /\b(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>\s*\{/,
    /^\s*(?:public|private|protected|static|readonly|\s)*(?!if\b|for\b|while\b|switch\b|catch\b)([A-Za-z0-9_$]+)\s*\(([^)]*)\)\s*\{/,
  ];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const match = startMatchers.map((matcher) => matcher.exec(line)).find(Boolean);
    if (!match) {
      continue;
    }

    let braceBalance = countMatches(line, /\{/g) - countMatches(line, /\}/g);
    let endIndex = index;
    while (braceBalance > 0 && endIndex + 1 < lines.length) {
      endIndex += 1;
      braceBalance += countMatches(lines[endIndex], /\{/g) - countMatches(lines[endIndex], /\}/g);
    }

    const slice = lines.slice(index, endIndex + 1);
    const source = slice.join("\n");
    const params = match[2]
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean).length;

    let braceDepth = 0;
    let maxDepth = 0;
    for (const sliceLine of slice) {
      braceDepth += countMatches(sliceLine, /\{/g);
      maxDepth = Math.max(maxDepth, braceDepth);
      braceDepth -= countMatches(sliceLine, /\}/g);
    }

    functions.push({
      name: match[1],
      startLine: index + 1,
      endLine: endIndex + 1,
      length: slice.length,
      params,
      complexity: 1 + countDecisionPoints(source),
      nesting: Math.max(0, maxDepth - 1),
    });
  }

  return functions;
}

export async function analyzeTypeScriptFiles(filePaths, rootPath) {
  const checks = [];
  const metrics = [];
  const artifacts = [];

  if (filePaths.length === 0) {
    return { checks, metrics, artifacts };
  }

  const perFile = [];
  let totalCommentLines = 0;
  let totalCodeLines = 0;
  let totalLongLines = 0;
  let totalImports = 0;
  let totalClasses = 0;
  let maxComplexity = 0;
  let maxFunctionLength = 0;
  let maxNesting = 0;
  let functionCount = 0;
  let totalFunctionLength = 0;
  let testFileCount = 0;

  for (const filePath of filePaths) {
    const source = await readText(filePath);
    const lines = source.replace(/\r\n/g, "\n").split("\n");
    const functions = detectFunctions(lines);
    const commentLines = lines.filter((line) => line.trim().startsWith("//") || line.trim().startsWith("*") || line.trim().startsWith("/*")).length;
    const longLines = lines.filter((line) => line.length > 120).length;
    const imports = lines.filter((line) => line.trim().startsWith("import ")).length;
    const classes = countMatches(source, /\bclass\s+[A-Za-z0-9_$]+/g);
    const complexity = 1 + countDecisionPoints(source);
    const fileMaxComplexity = functions.reduce((max, fn) => Math.max(max, fn.complexity), complexity);
    const fileMaxFunctionLength = functions.reduce((max, fn) => Math.max(max, fn.length), 0);
    const fileMaxNesting = functions.reduce((max, fn) => Math.max(max, fn.nesting), 0);

    totalCommentLines += commentLines;
    totalCodeLines += lines.filter((line) => line.trim()).length;
    totalLongLines += longLines;
    totalImports += imports;
    totalClasses += classes;
    maxComplexity = Math.max(maxComplexity, fileMaxComplexity);
    maxFunctionLength = Math.max(maxFunctionLength, fileMaxFunctionLength);
    maxNesting = Math.max(maxNesting, fileMaxNesting);
    functionCount += functions.length;
    totalFunctionLength += functions.reduce((sum, fn) => sum + fn.length, 0);
    if (/(^|\/)(tests?|__tests__)\/|(\.test|\.spec)\./.test(filePath)) {
      testFileCount += 1;
    }

    perFile.push({
      path: relativePath(rootPath, filePath),
      functionCount: functions.length,
      complexity: fileMaxComplexity,
      maxFunctionLength: fileMaxFunctionLength,
      maxNesting: fileMaxNesting,
      longLines,
    });
  }

  const averageFunctionLength = functionCount > 0 ? Number((totalFunctionLength / functionCount).toFixed(2)) : 0;
  const commentRatio = totalCodeLines > 0 ? Number((totalCommentLines / totalCodeLines).toFixed(3)) : 0;

  metrics.push(
    createMetric({
      id: "ts_file_count",
      category: "code-quality",
      value: filePaths.length,
      unit: "files",
      band: filePaths.length > 0 ? "good" : "info",
    }),
    createMetric({
      id: "ts_function_count",
      category: "code-quality",
      value: functionCount,
      unit: "functions",
      band: functionCount > 0 ? "good" : "info",
    }),
    createMetric({
      id: "ts_max_cyclomatic_complexity",
      category: "complexity",
      value: maxComplexity,
      unit: "score",
      band: maxComplexity >= 18 ? "heavy" : maxComplexity >= 10 ? "moderate" : "good",
    }),
    createMetric({
      id: "ts_average_function_length",
      category: "readability",
      value: averageFunctionLength,
      unit: "lines",
      band: averageFunctionLength >= 50 ? "heavy" : averageFunctionLength >= 30 ? "moderate" : "good",
    }),
    createMetric({
      id: "ts_max_nesting_depth",
      category: "complexity",
      value: maxNesting,
      unit: "levels",
      band: maxNesting >= 5 ? "heavy" : maxNesting >= 3 ? "moderate" : "good",
    }),
    createMetric({
      id: "ts_comment_ratio",
      category: "readability",
      value: commentRatio,
      unit: "ratio",
      band: commentRatio < 0.03 ? "moderate" : "good",
    }),
    createMetric({
      id: "ts_test_file_count",
      category: "best-practice",
      value: testFileCount,
      unit: "files",
      band: testFileCount > 0 ? "good" : "moderate",
    }),
  );

  if (maxComplexity >= 18) {
    checks.push(
      createCheck({
        id: "ts-complexity-high",
        category: "complexity",
        severity: "warning",
        status: "warn",
        message: "At least one TypeScript function has high cyclomatic complexity.",
        evidence: [`Max complexity: ${maxComplexity}`],
        remediation: ["Split complex functions into smaller branches with clearer responsibilities."],
      }),
    );
  }

  if (maxFunctionLength >= 80) {
    checks.push(
      createCheck({
        id: "ts-function-length-high",
        category: "readability",
        severity: "warning",
        status: "warn",
        message: "At least one TypeScript function is long enough to hurt readability.",
        evidence: [`Max function length: ${maxFunctionLength} lines`],
        remediation: ["Break large functions into smaller helpers with single-purpose logic."],
      }),
    );
  }

  if (totalLongLines > 0) {
    checks.push(
      createCheck({
        id: "ts-long-lines",
        category: "readability",
        severity: "warning",
        status: "warn",
        message: "Some TypeScript lines exceed 120 characters.",
        evidence: [`Long lines: ${totalLongLines}`],
        remediation: ["Wrap long expressions and object literals to keep scanability high."],
      }),
    );
  }

  if (filePaths.length > 0 && testFileCount === 0) {
    checks.push(
      createCheck({
        id: "ts-tests-missing",
        category: "best-practice",
        severity: "warning",
        status: "warn",
        message: "TypeScript source files were found without matching test files.",
        evidence: [`Source files: ${filePaths.length}`],
        remediation: ["Add `.test.ts` or `.spec.ts` coverage for the main TypeScript logic."],
      }),
    );
  }

  artifacts.push(
    createArtifact({
      id: "ts-per-file-analysis",
      type: "analysis",
      label: "TypeScript per-file analysis",
      description: "Heuristic TypeScript quality and complexity breakdown by file.",
      data: {
        files: perFile,
      },
    }),
  );

  return { checks, metrics, artifacts };
}
