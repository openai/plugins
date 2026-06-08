# Code Quality Requirements

Applies to all generated code across every Wix CLI app extension type. Each per-extension reference links here instead of restating these rules.

## TypeScript Quality Guidelines

- Generated code MUST compile with zero TypeScript errors under strict settings: `strict`, `noImplicitAny`, `strictNullChecks`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`.
- Prefer type-narrowing and exhaustive logic over assertions; avoid non-null assertions (`!`) and unsafe casts (`as any`).
- Treat optional values, refs, and array indexing results as possibly undefined and handle them explicitly.
- Use exhaustive checks for unions (e.g., `switch` with a `never` check) and return total values (no implicit `undefined`).
- Do NOT use `// @ts-ignore` or `// @ts-expect-error`; fix the types or add guards instead.

## Core Principles

- Do NOT invent or assume new types, modules, functions, props, events, or imports. Use only entities present in the provided references or standard libraries already used in this project.
- NEVER use mocks, placeholders, or TODOs in shipped code. ALWAYS implement complete, production-ready functionality.
- If a required API, type, or module is missing, surface it to the user explicitly rather than inserting placeholder code.
- Do NOT create README.md, CHANGELOG.md, or other unprompted markdown documentation — only output the files the task actually requires.

## Code Quality Standards

- Add documentation only for complex or non-obvious logic — well-named identifiers should carry the rest.
- Prefer `async`/`await` for asynchronous operations.

## Modular Code

- If a generated file would exceed ~300 lines, split it into multiple smaller files with imports. Each component or function should stay ~50–100 lines.
- Extract utilities/helpers into separate files; put types/interfaces into dedicated type files.

## Error Handling

- Log errors with `console.error` for debugging.
- Handle network timeouts and external service failures.
