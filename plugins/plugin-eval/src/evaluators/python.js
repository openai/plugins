import { createArtifact, createCheck, createMetric } from "../core/schema.js";
import { readText, relativePath } from "../lib/files.js";

function countMatches(text, expression) {
  return (text.match(expression) || []).length;
}

function countDecisionPoints(text) {
  return (
    countMatches(text, /\bif\b/g) +
    countMatches(text, /\belif\b/g) +
    countMatches(text, /\bfor\b/g) +
    countMatches(text, /\bwhile\b/g) +
    countMatches(text, /\bexcept\b/g) +
    countMatches(text, /\band\b/g) +
    countMatches(text, /\bor\b/g)
  );
}

function detectFunctions(lines) {
  const functions = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const match = /^(\s*)(?:async\s+def|def)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*:/.exec(line);
    if (!match) {
      continue;
    }

    const indent = match[1].length;
    let endIndex = index;
    for (let cursor = index + 1; cursor < lines.length; cursor += 1) {
      const cursorLine = lines[cursor];
      const trimmed = cursorLine.trim();
      if (!trimmed) {
        continue;
      }
      const cursorIndent = cursorLine.length - cursorLine.trimStart().length;
      if (cursorIndent <= indent && !trimmed.startsWith("#")) {
        break;
      }
      endIndex = cursor;
    }

    const slice = lines.slice(index, endIndex + 1);
    const source = slice.join("\n");
    const maxIndent = slice.reduce((max, sliceLine) => {
      if (!sliceLine.trim()) {
        return max;
      }
      const currentIndent = sliceLine.length - sliceLine.trimStart().length;
      return Math.max(max, currentIndent);
    }, indent);
    const params = match[3]
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean).length;

    functions.push({
      name: match[2],
      startLine: index + 1,
      endLine: endIndex + 1,
      length: slice.length,
      params,
      complexity: 1 + countDecisionPoints(source),
      nesting: Math.max(0, Math.round((maxIndent - indent) / 4)),
    });
  }
  return functions;
}

export async function analyzePythonFiles(filePaths, rootPath) {
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
    const commentLines = lines.filter((line) => line.trim().startsWith("#")).length;
    const longLines = lines.filter((line) => line.length > 120).length;
    const imports = lines.filter((line) => /^(\s*)(import|from)\b/.test(line)).length;
    const classes = countMatches(source, /^\s*class\s+[A-Za-z0-9_]+/gm);
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
    if (/(^|\/)(tests?|__tests__)\/|(^|\/)test_[^/]+\.py$/.test(filePath)) {
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
      id: "py_file_count",
      category: "code-quality",
      value: filePaths.length,
      unit: "files",
      band: filePaths.length > 0 ? "good" : "info",
    }),
    createMetric({
      id: "py_function_count",
      category: "code-quality",
      value: functionCount,
      unit: "functions",
      band: functionCount > 0 ? "good" : "info",
    }),
    createMetric({
      id: "py_max_cyclomatic_complexity",
      category: "complexity",
      value: maxComplexity,
      unit: "score",
      band: maxComplexity >= 18 ? "heavy" : maxComplexity >= 10 ? "moderate" : "good",
    }),
    createMetric({
      id: "py_average_function_length",
      category: "readability",
      value: averageFunctionLength,
      unit: "lines",
      band: averageFunctionLength >= 50 ? "heavy" : averageFunctionLength >= 30 ? "moderate" : "good",
    }),
    createMetric({
      id: "py_max_nesting_depth",
      category: "complexity",
      value: maxNesting,
      unit: "levels",
      band: maxNesting >= 5 ? "heavy" : maxNesting >= 3 ? "moderate" : "good",
    }),
    createMetric({
      id: "py_comment_ratio",
      category: "readability",
      value: commentRatio,
      unit: "ratio",
      band: commentRatio < 0.03 ? "moderate" : "good",
    }),
    createMetric({
      id: "py_test_file_count",
      category: "best-practice",
      value: testFileCount,
      unit: "files",
      band: testFileCount > 0 ? "good" : "moderate",
    }),
  );

  if (maxComplexity >= 18) {
    checks.push(
      createCheck({
        id: "py-complexity-high",
        category: "complexity",
        severity: "warning",
        status: "warn",
        message: "At least one Python function has high cyclomatic complexity.",
        evidence: [`Max complexity: ${maxComplexity}`],
        remediation: ["Split complex functions into smaller helpers or guard clauses."],
      }),
    );
  }

  if (maxFunctionLength >= 80) {
    checks.push(
      createCheck({
        id: "py-function-length-high",
        category: "readability",
        severity: "warning",
        status: "warn",
        message: "At least one Python function is long enough to hurt readability.",
        evidence: [`Max function length: ${maxFunctionLength} lines`],
        remediation: ["Break large functions into smaller helpers with clear names."],
      }),
    );
  }

  if (totalLongLines > 0) {
    checks.push(
      createCheck({
        id: "py-long-lines",
        category: "readability",
        severity: "warning",
        status: "warn",
        message: "Some Python lines exceed 120 characters.",
        evidence: [`Long lines: ${totalLongLines}`],
        remediation: ["Wrap long expressions and keep docstrings or SQL fragments easier to scan."],
      }),
    );
  }

  if (filePaths.length > 0 && testFileCount === 0) {
    checks.push(
      createCheck({
        id: "py-tests-missing",
        category: "best-practice",
        severity: "warning",
        status: "warn",
        message: "Python source files were found without matching test files.",
        evidence: [`Source files: ${filePaths.length}`],
        remediation: ["Add `test_*.py` or `tests/` coverage for the main Python logic."],
      }),
    );
  }

  artifacts.push(
    createArtifact({
      id: "py-per-file-analysis",
      type: "analysis",
      label: "Python per-file analysis",
      description: "Heuristic Python quality and complexity breakdown by file.",
      data: {
        files: perFile,
      },
    }),
  );

  return { checks, metrics, artifacts };
}
