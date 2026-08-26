import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const input = process.env.INPUT ?? "datascience-chart-widget.html";
const isArtifactWidget = input.includes("datascience-artifact-widget");
const isPortableArtifactReader = input.includes("portable-artifact-reader");
const usesReactApp = isArtifactWidget || isPortableArtifactReader;
const pluginRoot = fileURLToPath(new URL(".", import.meta.url));
const portableTokenTransform = {
  name: "data-analytics-portable-token-transform",
  enforce: "pre" as const,
  transform(source: string, id: string) {
    if (!isPortableArtifactReader || !/analytics-app\/tokens\.css(?:\?|$)/.test(id)) return null;
    return source.replace(/^@font-face\s*\{[\s\S]*?\}\s*/, "");
  },
};
const appAliases = usesReactApp
  ? [
      { find: /^react$/, replacement: path.join(pluginRoot, "node_modules/react/index.js") },
      {
        find: /^react\/jsx-runtime$/,
        replacement: path.join(pluginRoot, "node_modules/react/jsx-runtime.js"),
      },
      {
        find: /^react\/jsx-dev-runtime$/,
        replacement: path.join(pluginRoot, "node_modules/react/jsx-dev-runtime.js"),
      },
      { find: /^react-dom$/, replacement: path.join(pluginRoot, "node_modules/react-dom/index.js") },
      {
        find: /^react-dom\/client$/,
        replacement: path.join(pluginRoot, "node_modules/react-dom/client.js"),
      },
      ...(isPortableArtifactReader
        ? [
            {
              find: "./layout/RichMarkdown",
              replacement: path.join(
                pluginRoot,
                "src/analytics-app/layout/RichMarkdown.portable.tsx",
              ),
            },
            {
              find: "./imageExport",
              replacement: path.join(pluginRoot, "src/analytics-app/imageExport.portable.ts"),
            },
            {
              find: /^(?:\.\/|\.\.\/)runtimeEnvironment$/,
              replacement: path.join(
                pluginRoot,
                "src/analytics-app/runtimeEnvironment.portable.ts",
              ),
            },
          ]
        : []),
    ]
  : [];

export default defineConfig({
  root: "src",
  plugins: [portableTokenTransform, viteSingleFile()],
  resolve: {
    alias: appAliases,
    dedupe: ["react", "react-dom"],
    preserveSymlinks: true
  },
  build: {
    outDir: "../assets",
    emptyOutDir: false,
    modulePreload: isPortableArtifactReader ? false : undefined,
    minify: usesReactApp ? "oxc" : false,
    cssMinify: false,
    rollupOptions: {
      input
    }
  }
});
