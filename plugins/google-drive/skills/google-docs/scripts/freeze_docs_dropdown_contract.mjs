#!/usr/bin/env node
import { parseArgs } from "node:util";
import { readJson, writeJson } from "../runtime/dropdown-common.mjs";
import { freezeDropdownContract } from "../runtime/dropdown-contract.mjs";

const { values } = parseArgs({ options: {
  inventory: { type: "string" },
  decisions: { type: "string" },
  output: { type: "string" },
} });
for (const key of ["inventory", "decisions", "output"]) if (!values[key]) throw new Error(`--${key} is required`);
const inventory = await readJson(values.inventory);
const decisions = await readJson(values.decisions);
await writeJson(values.output, freezeDropdownContract({ inventory, ...decisions }));
