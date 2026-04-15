import path from "node:path";

import { walkFiles } from "../lib/files.js";
import { analyzePythonFiles } from "./python.js";
import { analyzeTypeScriptFiles } from "./typescript.js";

function filterLanguageFiles(files) {
  const tsFiles = [];
  const pyFiles = [];

  for (const filePath of files) {
    const extension = path.extname(filePath).toLowerCase();
    if ([".ts", ".tsx", ".mts", ".cts"].includes(extension)) {
      tsFiles.push(filePath);
    } else if (extension === ".py") {
      pyFiles.push(filePath);
    }
  }

  return { tsFiles, pyFiles };
}

export async function analyzeCodeMetrics(rootPath, target) {
  const files =
    target.kind === "file"
      ? [target.path]
      : await walkFiles(rootPath, {
          excludeDirs: [],
          skipTopLevel: target.kind === "directory" ? [] : ["fixtures", "__fixtures__"],
        });
  const { tsFiles, pyFiles } = filterLanguageFiles(files);

  const tsAnalysis = await analyzeTypeScriptFiles(tsFiles, rootPath);
  const pyAnalysis = await analyzePythonFiles(pyFiles, rootPath);

  return {
    checks: [...tsAnalysis.checks, ...pyAnalysis.checks],
    metrics: [...tsAnalysis.metrics, ...pyAnalysis.metrics],
    artifacts: [...tsAnalysis.artifacts, ...pyAnalysis.artifacts],
  };
}
