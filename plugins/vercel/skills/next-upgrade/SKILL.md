---
name: next-upgrade
description: Upgrade Next.js to the latest version following official migration guides and codemods. Use when upgrading Next.js versions, running codemods, or migrating between major releases.
metadata:
  priority: 6
  docs:
    - "https://nextjs.org/docs/app/guides/upgrading"
    - "https://nextjs.org/docs/app/guides/upgrading/codemods"
  pathPatterns:
    - 'next.config.*'
    - 'package.json'
  bashPatterns:
    - '\bnpx\s+@next/codemod\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bnext@'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bnext@'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bnext@'
    - '\byarn\s+add\s+[^\n]*\bnext@'
  promptSignals:
    phrases:
      - "upgrade next"
      - "upgrade nextjs"
      - "migrate next"
      - "update next.js"
      - "next.js upgrade"
      - "nextjs migration"
      - "next codemod"
    allOf:
      - [upgrade, next]
      - [migrate, next]
      - [update, nextjs]
    anyOf:
      - "breaking changes"
      - "codemod"
      - "migration guide"
      - "version upgrade"
    noneOf: []
    minScore: 6
---

# Upgrade Next.js

Upgrade the current project to the latest Next.js version following official migration guides.

## Instructions

1. **Detect current version**: Read `package.json` to identify the current Next.js version and related dependencies (React, React DOM, etc.)

2. **Fetch the latest upgrade guide**: Use WebFetch to get the official upgrade documentation:
   - Codemods: https://nextjs.org/docs/app/guides/upgrading/codemods
   - Version-specific guides (adjust version as needed):
     - https://nextjs.org/docs/app/guides/upgrading/version-16
     - https://nextjs.org/docs/app/guides/upgrading/version-15
     - https://nextjs.org/docs/app/guides/upgrading/version-14

3. **Determine upgrade path**: Based on current version, identify which migration steps apply. For major version jumps, upgrade incrementally (e.g., 13 → 14 → 15).

4. **Run codemods first**: Next.js provides codemods to automate breaking changes:
   ```bash
   npx @next/codemod@latest <transform> <path>
   ```
   Common transforms:
   - `next-async-request-api` - Updates async Request APIs (v15)
   - `next-request-geo-ip` - Migrates geo/ip properties (v15)
   - `next-dynamic-access-named-export` - Transforms dynamic imports (v15)

5. **Update dependencies**: Upgrade Next.js and peer dependencies together:
   ```bash
   npm install next@latest react@latest react-dom@latest
   ```

6. **Review breaking changes**: Check the upgrade guide for manual changes needed:
   - API changes (e.g., async params in v15)
   - Configuration changes in `next.config.js`
   - Deprecated features being removed

7. **Update TypeScript types** (if applicable):
   ```bash
   npm install @types/react@latest @types/react-dom@latest
   ```

8. **Test the upgrade**:
   - Run `npm run build` to check for build errors
   - Run `npm run dev` and test key functionality
