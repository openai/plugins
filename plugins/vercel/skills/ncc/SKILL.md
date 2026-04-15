---
name: ncc
description: 'Expert guidance for @vercel/ncc — a simple CLI for compiling Node.js modules into a single file with all dependencies included. Use when bundling serverless functions, CLI tools, or any Node.js project into a self-contained file.'
metadata:
  priority: 4
  docs:
    - "https://github.com/vercel/ncc"
  pathPatterns: []
  importPatterns:
    - '@vercel/ncc'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/ncc\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/ncc\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/ncc\b'
    - '\byarn\s+add\s+[^\n]*@vercel/ncc\b'
    - '\bncc\s+build\b'
---

# @vercel/ncc — Node.js Compiler Collection

You are an expert in `@vercel/ncc`, Vercel's simple CLI for compiling a Node.js module into a single file, together with all its dependencies.

## Overview

ncc bundles a Node.js application and all of its `node_modules` into a single output file. This is ideal for:
- **Serverless functions** — deploy a single file instead of `node_modules`
- **CLI tools** — distribute a self-contained executable
- **Docker images** — reduce image size by eliminating `node_modules`

## Installation

```bash
npm install -g @vercel/ncc

# Or as a dev dependency
npm install --save-dev @vercel/ncc
```

## Basic Usage

```bash
# Compile index.js into dist/index.js
ncc build input.js -o dist/

# Watch mode for development
ncc build input.js -o dist/ -w

# Run directly without writing to disk
ncc run input.js
```

## CLI Options

| Flag | Description |
|---|---|
| `-o, --out [dir]` | Output directory (default: `dist`) |
| `-m, --minify` | Minify the output |
| `-s, --source-map` | Generate source maps |
| `-a, --asset-builds` | Build nested JS assets recursively |
| `-e, --external [mod]` | Keep module as external (don't bundle) |
| `-w, --watch` | Watch mode — rebuild on changes |
| `-t, --transpile-only` | Skip TypeScript type checking |
| `--license [file]` | Output licenses to a file |
| `-q, --quiet` | Suppress non-error output |
| `--no-cache` | Skip the build cache |
| `--no-asset-builds` | Skip nested JS asset builds |

## package.json Integration

```json
{
  "scripts": {
    "build": "ncc build src/index.ts -o dist/ -m",
    "build:watch": "ncc build src/index.ts -o dist/ -w",
    "start": "node dist/index.js"
  },
  "devDependencies": {
    "@vercel/ncc": "^0.38.0"
  }
}
```

## TypeScript Support

ncc natively supports TypeScript — no separate `tsc` step needed:

```bash
# Compiles TypeScript directly
ncc build src/index.ts -o dist/

# Skip type checking for faster builds
ncc build src/index.ts -o dist/ -t
```

ncc uses the project's `tsconfig.json` automatically.

## Externals

Keep specific modules out of the bundle (useful for native modules or optional dependencies):

```bash
# Single external
ncc build input.js -e aws-sdk

# Multiple externals
ncc build input.js -e aws-sdk -e sharp
```

For serverless environments where the runtime provides certain modules (like AWS Lambda's `aws-sdk`), mark them as external.

## Static Assets

ncc handles non-JS assets (`.json`, `.node`, binary files) by copying them to the output directory alongside the compiled JS file. They are referenced correctly at runtime.

## Common Patterns

### Serverless Function Bundling

```bash
# Build a minimal serverless handler
ncc build api/handler.ts -o .output/ -m --no-cache
```

### CLI Tool Distribution

```json
{
  "bin": "dist/index.js",
  "scripts": {
    "prepublishOnly": "ncc build src/index.ts -o dist/ -m"
  }
}
```

### GitHub Actions

```bash
# Bundle a GitHub Action into a single file
ncc build src/index.ts -o dist/ -m --license licenses.txt
```

GitHub Actions require all dependencies bundled — ncc is the recommended bundler for custom JS/TS actions.

## Key Points

1. **Single-file output** — all dependencies inlined, no `node_modules` needed at runtime
2. **TypeScript native** — compiles `.ts` files directly using the project's `tsconfig.json`
3. **No config file** — entirely driven by CLI flags
4. **Asset handling** — non-JS files are automatically copied to the output directory
5. **Use externals for native modules** — binary `.node` modules often need to be external
6. **Source maps for debugging** — use `-s` flag to generate `.js.map` files
7. **Watch mode for dev** — use `-w` for fast iteration during development

## Official Resources

- [ncc GitHub](https://github.com/vercel/ncc)
- [Vercel Blog — ncc Introduction](https://github.com/vercel/ncc)
