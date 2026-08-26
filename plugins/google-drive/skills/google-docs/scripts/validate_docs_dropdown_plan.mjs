#!/usr/bin/env node
import { parseArgs } from "node:util";
import { readJson, sha256File, writeJson } from "../runtime/dropdown-common.mjs";
import { validateDropdownPlan } from "../runtime/dropdown-plan.mjs";

const { values } = parseArgs({
  options: {
    plan: { type: "string" },
    inventory: { type: "string" },
    contract: { type: "string" },
    executor: { type: "string" },
    output: { type: "string" },
  },
});

for (const key of ["plan", "inventory", "contract", "executor", "output"]) {
  if (!values[key]) throw new Error(`--${key} is required`);
}

const [plan, inventory, contract] = await Promise.all([
  readJson(values.plan),
  readJson(values.inventory),
  readJson(values.contract),
]);
const validation = validateDropdownPlan(plan, { inventory, contract });
await writeJson(values.output, {
  validationVersion: 1,
  kind: "google-docs-v2-dropdown-plan-validation",
  planFileSha256: await sha256File(values.plan),
  inventoryFileSha256: await sha256File(values.inventory),
  contractFileSha256: await sha256File(values.contract),
  executorFileSha256: await sha256File(values.executor),
  summary: validation.summary,
});
