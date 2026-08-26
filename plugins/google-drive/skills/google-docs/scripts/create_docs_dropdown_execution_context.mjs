#!/usr/bin/env node
import { parseArgs } from "node:util";
import { resolve } from "node:path";
import { writeJson } from "../runtime/dropdown-common.mjs";

const { values } = parseArgs({ options: {
  "workspace-root": { type: "string" },
  "target-document-id": { type: "string" },
  executor: { type: "string" },
  output: { type: "string" },
} });
for (const key of ["workspace-root", "target-document-id", "executor", "output"]) if (!values[key]) throw new Error(`--${key} is required`);
await writeJson(values.output, {
  version: 1,
  kind: "google-docs-v2-dropdown-execution-context",
  workspaceRoot: resolve(values["workspace-root"]),
  targetDocumentId: values["target-document-id"],
  executorPath: resolve(values.executor),
});
