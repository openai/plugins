#!/usr/bin/env node
import { parseArgs } from "node:util";
import { readJson, writeJson } from "../runtime/dropdown-common.mjs";
import { buildDropdownInventory } from "../runtime/dropdown-inventory.mjs";

const { values } = parseArgs({ options: {
  document: { type: "string" },
  dropdowns: { type: "string" },
  "document-id": { type: "string" },
  "tab-id": { type: "string" },
  output: { type: "string" },
} });
for (const key of ["document", "dropdowns", "output"]) if (!values[key]) throw new Error(`--${key} is required`);
const inventory = buildDropdownInventory({
  documentResult: await readJson(values.document),
  dropdownResult: await readJson(values.dropdowns),
  documentId: values["document-id"] ?? null,
  tabId: values["tab-id"] ?? null,
});
await writeJson(values.output, inventory);
