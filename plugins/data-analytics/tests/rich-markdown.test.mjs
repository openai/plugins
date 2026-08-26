import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { describe, test } from "node:test";
import ts from "typescript";

async function loadRichMarkdown(sourceFile = "RichMarkdown.tsx") {
  const packageRoot = process.cwd();
  const source = await readFile(
    join(packageRoot, "src", "analytics-app", "layout", sourceFile),
    "utf8",
  );
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      jsx: ts.JsxEmit.ReactJSX,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const tempDir = await mkdtemp(join(packageRoot, ".tmp-rich-markdown-"));
  const tempModule = join(tempDir, `${sourceFile}-${Date.now()}-${Math.random()}.mjs`);
  await writeFile(tempModule, outputText);
  const module = await import(`file://${tempModule}`);
  await rm(tempDir, { recursive: true, force: true });
  return module;
}

describe("rich markdown preview", () => {
  test("keeps loose ordered-list items in one ordered list", async () => {
    const React = await import("react");
    const { renderToStaticMarkup } = await import("react-dom/server");
    const { RichMarkdownPreview } = await loadRichMarkdown();
    const markdown = [
      "1. **Make activation the primary metric.** Optimize first-session completion.",
      "",
      "2. **Build opinionated starter paths.** Package top workflows.",
      "",
      "3. **Keep GTM focused on high-fit users.** Target teams with trial usage.",
      "",
      "4. **Use Free/Go as a conversion funnel.** Measure second-task depth.",
      "",
      "5. **Clean up instrumentation.** Standardize task and turn events.",
    ].join("\n");

    const html = renderToStaticMarkup(
      React.createElement(RichMarkdownPreview, { markdown }),
    );

    assert.equal((html.match(/<ol>/g) ?? []).length, 1);
    assert.equal((html.match(/<li>/g) ?? []).length, 5);
    assert.match(html, /Make activation the primary metric/);
    assert.match(html, /Clean up instrumentation/);
  });

  test("portable preview keeps loose ordered-list items in one ordered list", async () => {
    const React = await import("react");
    const { renderToStaticMarkup } = await import("react-dom/server");
    const { RichMarkdownPreview } = await loadRichMarkdown("RichMarkdown.portable.tsx");
    const markdown = [
      "1. First recommendation",
      "",
      "2. Second recommendation",
      "",
      "3. Third recommendation",
    ].join("\n");

    const html = renderToStaticMarkup(
      React.createElement(RichMarkdownPreview, { markdown }),
    );

    assert.equal((html.match(/<ol>/g) ?? []).length, 1);
    assert.equal((html.match(/<li>/g) ?? []).length, 3);
    assert.match(html, /First recommendation/);
    assert.match(html, /Third recommendation/);
  });

  test("portable preview preserves adjacent list and quote runs", async () => {
    const React = await import("react");
    const { renderToStaticMarkup } = await import("react-dom/server");
    const { RichMarkdownPreview } = await loadRichMarkdown("RichMarkdown.portable.tsx");
    const markdown = [
      "- First bullet",
      "- Second bullet",
      "1. First ordered item",
      "2. Second ordered item",
      "> First quote",
      "> Second quote",
      "- Final bullet",
    ].join("\n");

    const html = renderToStaticMarkup(
      React.createElement(RichMarkdownPreview, { markdown }),
    );

    assert.equal((html.match(/<ul>/g) ?? []).length, 2);
    assert.equal((html.match(/<ol>/g) ?? []).length, 1);
    assert.equal((html.match(/<blockquote>/g) ?? []).length, 1);
    for (const text of [
      "First bullet",
      "Second bullet",
      "First ordered item",
      "Second ordered item",
      "First quote",
      "Second quote",
      "Final bullet",
    ]) {
      assert.match(html, new RegExp(text));
    }
  });
});
