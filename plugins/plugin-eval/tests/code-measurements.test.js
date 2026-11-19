import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { analyzePythonFiles } from "../src/evaluators/python.js";
import { analyzeTypeScriptFiles } from "../src/evaluators/typescript.js";

async function measure(t, language, source, name = language === "py" ? "sample.py" : "sample.ts") {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "plugin-eval-code-"));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const file = path.join(root, name);
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, source);
  const result = await (language === "py" ? analyzePythonFiles : analyzeTypeScriptFiles)([file], root);
  return {
    result,
    metric: (suffix) => result.metrics.find((item) => item.id === `${language}_${suffix}`).value,
    file: result.artifacts[0].data.files[0],
  };
}

test("py: continuation alignment is not control-flow nesting", async (t) => {
  const actual = await measure(t, "py", "def example():\n    values = [\n                         1,\n                         2,\n    ]\n    return values\n");
  assert.equal(actual.metric("max_nesting_depth"), 0);
});

test("py: nested control flow contributes to nesting depth", async (t) => {
  const actual = await measure(t, "py", "def example(x):\n    if x:\n        for item in x:\n            print(item)\n");
  assert.equal(actual.metric("max_nesting_depth"), 2);
});

test("ts: compact nested functions do not leak decisions into their enclosing function", async (t) => {
  const actual = await measure(t, "ts", "function outer(){function inner(x){ if(x){} } if(a){} if(b){} }");
  assert.equal(actual.metric("max_cyclomatic_complexity"), 3);
});

test("ts: semicolonless types do not consume following async functions", async (t) => {
  const actual = await measure(t, "ts", `type Value = string\nasync function complex(x) { ${"if (x) { x += 1; } ".repeat(18)} }`);
  assert.equal(actual.metric("function_count"), 1);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 19);
});

for (const language of ["py", "ts"]) {
  test(`${language}: max complexity measures one function rather than the entire file`, async (t) => {
    const source = Array.from({ length: 20 }, (_, i) => language === "py"
      ? `def simple_${i}(x):\n    if x:\n        return x\n`
      : `function simple_${i}(x) { if (x) { return x; } }`).join("\n");
    const actual = await measure(t, language, source);
    assert.equal(actual.metric("function_count"), 20);
    assert.equal(actual.metric("max_cyclomatic_complexity"), 2);
    assert.equal(actual.file.complexity, 2);
    assert.equal(actual.result.checks.some((item) => item.id === `${language}-complexity-high`), false);
  });

  test(`${language}: a single complex function still produces a warning`, async (t) => {
    const source = language === "py"
      ? `def complex(x):\n${"    if x:\n        x += 1\n".repeat(18)}`
      : `function complex(x) { ${"if (x) { x += 1; } ".repeat(18)} }`;
    const actual = await measure(t, language, source);
    assert.equal(actual.metric("max_cyclomatic_complexity"), 19);
    assert.equal(actual.result.checks.some((item) => item.id === `${language}-complexity-high`), true);
  });

  test(`${language}: module decisions without functions have no maximum function complexity`, async (t) => {
    const actual = await measure(t, language, language === "py" ? "if True:\n    pass\n" : "if (ready) { run(); }");
    assert.equal(actual.metric("function_count"), 0);
    assert.equal(actual.metric("max_cyclomatic_complexity"), 0);
  });

  test(`${language}: comments and strings cannot create functions or decisions`, async (t) => {
    const source = language === "py"
      ? `text = '''\ndef fake(x):\n    if x and x or x:\n        for item in x: pass\n'''\ndef real():\n    """if elif for while except and or"""\n    # if elif for while except and or\n    return "if for while except and or"\n`
      : `/*\nfunction fake(x) { if (x && x || x) {} }\n*/\nfunction real() {\n  const text = "} if for while case catch && || ? {";\n  const template = \`if for while { } ?\`;\n  // } if for while case catch && || ?\n  return text;\n}`;
    const actual = await measure(t, language, source);
    assert.equal(actual.metric("function_count"), 1);
    assert.equal(actual.metric("max_cyclomatic_complexity"), 1);
    assert.equal(actual.file.maxFunctionLength, language === "py" ? 4 : 6);
  });

  test(`${language}: nested function decisions are measured independently`, async (t) => {
    const source = language === "py"
      ? "def outer(x):\n    if x: pass\n    def inner(y):\n        if y and x: pass\n    return inner\n"
      : "function outer(x) {\n  if (x) {}\n  function inner(y) { if (y && x) {} }\n  return inner;\n}";
    const actual = await measure(t, language, source);
    assert.equal(actual.metric("function_count"), 2);
    assert.equal(actual.metric("max_cyclomatic_complexity"), 3);
  });

  test(`${language}: native test-directory paths count as tests`, async (t) => {
    const actual = await measure(t, language, language === "py" ? "def example(): pass" : "function example() {}", path.join("tests", `example.${language}`));
    assert.equal(actual.metric("test_file_count"), 1);
    assert.equal(actual.result.checks.some((item) => item.id === `${language}-tests-missing`), false);
  });
}

test("Python: multiline signatures, annotations and continuation indentation retain function scope", async (t) => {
  const actual = await measure(t, "py", `async def example(\n    value: dict[str, int],\n    callback=lambda x: x,\n) -> int:\n    result = (\nvalue.get("x")\n    )\n    if result and value:\n        return result\n    return 0\n`);
  assert.equal(actual.metric("function_count"), 1);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 3);
  assert.equal(actual.file.maxFunctionLength, 10);
});

test("TypeScript: multiline typed functions and methods are detected", async (t) => {
  const actual = await measure(t, "ts", `function example(\n  value: number,\n): number {\n  if (value) return value;\n  return 0;\n}\nclass Example {\n  method(value: number): number {\n    if (value) return value;\n    return 0;\n  }\n}\nconst arrow = (\n  value: number,\n): number => { if (value) return value; return 0; };`);
  assert.equal(actual.metric("function_count"), 3);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 2);
});

test("TypeScript: optional types, optional chains and nullish operators are not ternaries", async (t) => {
  const actual = await measure(t, "ts", "function example(value?: { item?: number }): number {\n  const item = value?.item ?? 0;\n  return item ? item : 1;\n}");
  assert.equal(actual.metric("function_count"), 1);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 2);
});

test("TypeScript: single-parameter block arrows are independent functions", async (t) => {
  const actual = await measure(t, "ts", "const outer = value => {\n  if (value) {}\n  const inner = other => { if (other && value) {} };\n  return inner;\n};");
  assert.equal(actual.metric("function_count"), 2);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 3);
});

test("TypeScript: regex literals cannot close a function or add decisions", async (t) => {
  const actual = await measure(t, "ts", "function example() {\n  const pattern = /[}]/;\n  return /if|for|while|catch|case|\\?/;\n}");
  assert.equal(actual.metric("function_count"), 1);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 1);
  assert.equal(actual.file.maxFunctionLength, 4);
});

test("TypeScript: generic declarations still have function-level measurements", async (t) => {
  const actual = await measure(t, "ts", "function example<T>(value: T): T { if (value) return value; return value; }");
  assert.equal(actual.metric("function_count"), 1);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 2);
});

test("TypeScript: function types returning object types are not executable functions", async (t) => {
  const actual = await measure(t, "ts", "type Callback = (value?: number) => { result: number };\ninterface Factory { build(value: number): { result: number }; }");
  assert.equal(actual.metric("function_count"), 0);
  assert.equal(actual.metric("max_cyclomatic_complexity"), 0);
});
