#!/usr/bin/env node

/**
 * PostToolUse hook: Fix shadcn init breaking Geist fonts
 *
 * After `npx shadcn init` runs, globals.css gets rewritten with
 * `--font-sans: var(--font-sans)` — a circular self-reference that resolves
 * to nothing, causing fonts to fall back to Times/serif.
 *
 * Tailwind v4's `@theme inline` resolves CSS custom properties at parse time,
 * NOT at runtime. So `var(--font-geist-sans)` also doesn't work because the
 * Next.js font variable is injected via className at runtime.
 *
 * The fix: use literal font family names in @theme inline.
 *
 * This hook also reminds to move font variable classNames from <body> to <html>.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

function detectPlatform(input) {
  if ("conversation_id" in input || "cursor_version" in input) {
    return "cursor";
  }
  return "claude-code";
}

function resolveWorkspaceRoot(input) {
  if (!Array.isArray(input.workspace_roots)) {
    return null;
  }

  for (const root of input.workspace_roots) {
    if (typeof root === "string" && root.trim() !== "") {
      return root;
    }
  }

  return null;
}

function resolveCwd(input) {
  const candidate = input.cwd
    ?? input.working_directory
    ?? resolveWorkspaceRoot(input)
    ?? process.env.CURSOR_PROJECT_DIR
    ?? process.env.CLAUDE_WORKING_DIRECTORY
    ?? process.cwd();

  return typeof candidate === "string" && candidate.trim() !== "" ? candidate : process.cwd();
}

// Read hook input from stdin
let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let parsed;
try {
  parsed = JSON.parse(input);
} catch {
  process.exit(0);
}

const platform = detectPlatform(parsed);

const toolName = parsed.tool_name;
const toolInput = parsed.tool_input || {};

// Only trigger after Bash commands that look like shadcn init/add
if (toolName !== "Bash") process.exit(0);

const command = toolInput.command || "";
if (!command.match(/\bnpx\s+shadcn(@latest)?\s+(init|add)\b/)) process.exit(0);

// Find globals.css — check common locations
const cwd = resolveCwd(parsed);
const candidates = [
  join(cwd, "app/globals.css"),
  join(cwd, "src/app/globals.css"),
];

let globalsPath = null;
for (const candidate of candidates) {
  if (existsSync(candidate)) {
    globalsPath = candidate;
    break;
  }
}

if (!globalsPath) process.exit(0);

const content = readFileSync(globalsPath, "utf-8");

// Check for the broken patterns:
// 1. Circular: --font-sans: var(--font-sans)
// 2. Runtime var that @theme can't resolve: --font-sans: var(--font-geist-sans)
const hasBrokenFont =
  content.includes("--font-sans: var(--font-sans)") ||
  content.includes("--font-sans: var(--font-geist-sans)");

if (!hasBrokenFont) process.exit(0);

// Fix with literal font names that @theme inline can resolve at parse time
let fixed = content.replace(
  /--font-sans:\s*var\(--font-(?:sans|geist-sans)\)/g,
  '--font-sans: "Geist", "Geist Fallback", ui-sans-serif, system-ui, sans-serif'
);

// Also fix mono if present
fixed = fixed.replace(
  /--font-mono:\s*var\(--font-(?:mono|geist-mono)\)/g,
  '--font-mono: "Geist Mono", "Geist Mono Fallback", ui-monospace, monospace'
);

writeFileSync(globalsPath, fixed, "utf-8");

const relPath = globalsPath.replace(cwd + "/", "");

// Output a detailed explanation to the conversation
const message = `<!-- shadcn-font-fix -->
**Auto-fix applied to \`${relPath}\`**: Replaced CSS variable font references with literal Geist font family names.

### Why this fix was needed

\`shadcn init\` rewrites \`globals.css\` and sets \`--font-sans: var(--font-sans)\` inside \`@theme inline\` — a circular self-reference that resolves to nothing, causing all text to fall back to Times/serif.

**Why \`var(--font-geist-sans)\` also doesn't work**: Tailwind v4's \`@theme inline\` block resolves CSS custom properties at **CSS parse time** (build time), not at runtime. Next.js \`next/font\` injects \`--font-geist-sans\` via a className on \`<html>\` at **runtime**, so it doesn't exist when \`@theme inline\` evaluates. The variable resolves to empty, and fonts fall back to the browser default serif.

**The correct fix** (applied automatically):
\`\`\`css
@theme inline {
  --font-sans: "Geist", "Geist Fallback", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "Geist Mono", "Geist Mono Fallback", ui-monospace, monospace;
}
\`\`\`

### Second required fix (manual)

You MUST also move the font variable classNames from \`<body>\` to \`<html>\` in \`layout.tsx\`. The default \`create-next-app\` scaffold puts them on \`<body>\`, but they need to be on \`<html>\` so the \`@font-face\` declarations are scoped to the document root:

\`\`\`tsx
// CORRECT — font variables on <html>
<html lang="en" className={\`\${geistSans.variable} \${geistMono.variable}\`}>
  <body className="antialiased">

// WRONG — default scaffold puts them on <body>
<html lang="en">
  <body className={\`\${geistSans.variable} \${geistMono.variable} antialiased\`}>
\`\`\`
<!-- /shadcn-font-fix -->`;

const result = platform === "cursor"
  ? { additional_context: message }
  : { additionalContext: message };

console.log(JSON.stringify(result));
