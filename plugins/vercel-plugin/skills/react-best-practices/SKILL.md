---
name: react-best-practices
description: React best-practices reviewer for TSX files. Triggers after editing multiple TSX components to run a condensed quality checklist covering component structure, hooks usage, accessibility, performance, and TypeScript patterns.
metadata:
  priority: 4
  docs:
    - "https://react.dev/reference/react"
    - "https://react.dev/learn"
  pathPatterns:
    - 'src/components/**/*.tsx'
    - 'src/components/**/*.jsx'
    - 'app/components/**/*.tsx'
    - 'app/components/**/*.jsx'
    - 'components/**/*.tsx'
    - 'components/**/*.jsx'
    - 'src/ui/**/*.tsx'
    - 'lib/components/**/*.tsx'
  bashPatterns: []
  importPatterns:
    - 'react'
    - 'react-dom'
validate:
  -
    pattern: 'from\s+[''"](axios)[''"]|axios\.(get|post|put|delete)\('
    message: 'Client-side axios detected. Use SWR for React data fetching with caching, revalidation, and deduplication.'
    severity: recommended
    upgradeToSkill: swr
    upgradeWhy: 'Replace manual fetch/axios with SWR for automatic caching, revalidation, and optimistic UI.'
    skipIfFileContains: 'useSWR|from\s+[''"](swr)[''"]|@tanstack/react-query'
  -
    pattern: 'from\s+[''"](styled-components|@emotion/styled|@emotion/react|@mui/material|@chakra-ui/react)[''"]|styled\.'
    message: 'Legacy CSS-in-JS or component library detected. Consider shadcn/ui + Tailwind for modern Vercel-native UI.'
    severity: warn
    upgradeToSkill: shadcn
    upgradeWhy: 'Migrate from CSS-in-JS/MUI/Chakra to shadcn/ui + Tailwind CSS for better SSR performance and Vercel ecosystem alignment.'
    skipIfFileContains: '@/components/ui|shadcn|tailwindcss'
retrieval:
  aliases:
    - react review
    - component quality
    - tsx linter
    - react patterns
  intents:
    - review react code
    - improve component quality
    - check accessibility
    - optimize react
  entities:
    - hooks
    - accessibility
    - React
    - TSX
    - component
chainTo:
  -
    pattern: 'from\s+[''\"](axios)[''"]|axios\.(get|post|put|delete)\('
    targetSkill: swr
    message: 'Client-side axios detected — loading SWR guidance for React data fetching with caching and revalidation.'
  -
    pattern: 'from\s+[''\"](styled-components|@emotion/styled|@emotion/react|@mui/material|@chakra-ui/react)[''"]|styled\.'
    targetSkill: shadcn
    message: 'Legacy CSS-in-JS or component library detected — loading shadcn/ui guidance for modern Vercel-native UI.'
  -
    pattern: 'fetch\s*\([^)]*\)\s*\.then\s*\(|\.then\s*\(\s*(res|response)\s*=>'
    targetSkill: swr
    message: 'Manual fetch().then() in component — loading SWR guidance for declarative data fetching with caching and revalidation.'
    skipIfFileContains: 'useSWR|from\s+[''""](swr)[''""]|useQuery|@tanstack/react-query'

---

# React Best-Practices Review

After editing several TSX/JSX files, run through this condensed checklist to catch common issues before they compound.

## Component Structure

- **One component per file** — colocate helpers only if they are private to that component
- **Named exports** over default exports for better refactoring and tree-shaking
- **Props interface** defined inline or colocated, not in a separate `types.ts` unless shared
- **Destructure props** in the function signature: `function Card({ title, children }: CardProps)`
- **Avoid barrel files** (`index.ts` re-exports) in large projects — they hurt tree-shaking

## Hooks

- **Rules of Hooks** — never call hooks conditionally or inside loops
- **Custom hooks** — extract reusable logic into `use*` functions when two or more components share it
- **Dependency arrays** — list every reactive value; lint with `react-hooks/exhaustive-deps`
- **`useCallback` / `useMemo`** — use only when passing to memoized children or expensive computations, not by default
- **`useEffect` cleanup** — return a cleanup function for subscriptions, timers, and abort controllers

## State Management

- **Colocate state** — keep state as close as possible to where it is consumed
- **Derive, don't sync** — compute values from existing state instead of adding `useEffect` to mirror state
- **Avoid prop drilling** past 2–3 levels — use context or composition (render props / children)
- **Server state** — use React Query, SWR, or Server Components instead of manual fetch-in-effect

## Accessibility (a11y)

- **Semantic HTML first** — use `<button>`, `<a>`, `<nav>`, `<main>`, etc. before reaching for `<div onClick>`
- **`alt` on every `<img>`** — decorative images get `alt=""`
- **Keyboard navigation** — interactive elements must be focusable and operable via keyboard
- **`aria-*` attributes** — only when native semantics are insufficient; don't redundantly label

## Performance

- **`React.memo`** — wrap pure display components that re-render due to parent changes
- **Lazy loading** — use `React.lazy` + `Suspense` for route-level code splitting
- **List keys** — use stable, unique IDs; never use array index as key for reorderable lists
- **Avoid inline object/array literals** in JSX props — they create new references every render
- **Image optimization** — use `next/image` or responsive `srcSet`; avoid unoptimized `<img>` in Next.js

## TypeScript Patterns

- **`React.FC` is optional** — prefer plain function declarations with explicit return types
- **`PropsWithChildren`** — use when the component accepts `children` but has no other custom props
- **Event handlers** — type as `React.MouseEvent<HTMLButtonElement>`, not `any`
- **Generics for reusable components** — e.g., `function List<T>({ items, renderItem }: ListProps<T>)`
- **`as const` for config objects** — ensures literal types for discriminated unions and enums

## Design System Consistency

- Prefer shadcn primitives in Vercel-stack apps: Button, Input, Tabs, Dialog, AlertDialog, Sheet, Table, Card before building ad-hoc equivalents.
- Reject container soup: repeated `div rounded-xl border p-6` blocks usually mean stronger composition primitives are missing.
- Typography consistency: use Geist Sans and Geist Mono consistently; reserve monospace for code, metrics, IDs, and timestamps.

## Review Workflow

1. Scan recent TSX edits for the patterns above
2. Flag any violations with file path and line reference
3. Suggest minimal fixes — do not refactor beyond what is needed
4. If multiple issues exist in one file, batch them into a single edit
