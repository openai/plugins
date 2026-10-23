# Task Group: Small Node.js CLI utilities

scope: Node.js command-line tools in personal projects
applies_to: cwd=/home/user/proj

## Task 1: Fix add() in math.js and verify it with node -e

outcome: success

## Task 2: Add a slugify helper with node:test coverage

outcome: success

## User preferences

- “I always want node:test, zero dependencies and no semicolons.” -> prefer node:test with no runtime dependencies [Task 2]
- When a fix is small, verify it with a one-line `node -e` check -> keep verification lightweight [Task 1]

## Reusable knowledge

- `node --test` discovers `*.test.js` files without extra configuration [Task 2]
- The project is plain ESM; use `export function` rather than `module.exports` [Task 1]
