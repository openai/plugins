import test from "node:test";
import assert from "node:assert/strict";

import { choosePath } from "../src/sample.ts";

test("choosePath keeps fast items", () => {
  assert.deepEqual(choosePath(["fast:item", "archived:slow"], false, true), ["FAST:ITEM"]);
});
