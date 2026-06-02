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
