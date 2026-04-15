---
name: shadcn
description: shadcn/ui expert guidance — CLI, component installation, composition patterns, custom registries, theming, Tailwind CSS integration, and high-quality interface design. Use when initializing shadcn, adding components, composing product UI, building custom registries, configuring themes, or troubleshooting component issues.
metadata:
  priority: 6
  docs:
    - "https://ui.shadcn.com/docs"
    - "https://ui.shadcn.com/docs/components"
  pathPatterns:
    - 'components.json'
    - 'components/ui/**'
    - 'src/components/ui/**'
    - 'apps/*/components/ui/**'
    - 'apps/*/src/components/ui/**'
    - 'packages/*/components/ui/**'
    - 'packages/*/src/components/ui/**'
  bashPatterns:
    - '\bnpx\s+shadcn\b'
    - '\bnpx\s+shadcn@latest\s+(init|add|build|search|list|migrate|info|docs|view)\b'
    - '\bnpx\s+create-next-app\b'
    - '\bbunx\s+create-next-app\b'
    - '\bpnpm\s+create\s+next-app\b'
    - '\bnpm\s+create\s+next-app\b'
---

# shadcn/ui

You are an expert in shadcn/ui — a collection of beautifully designed, accessible, and customizable React components built on Radix UI primitives and Tailwind CSS. Components are added directly to your codebase as source code, not installed as a dependency.

## Key Concept

shadcn/ui is **not a component library** in the traditional sense. You don't install it as a package. Instead, the CLI copies component source code into your project, giving you full ownership and customization ability.

## CLI Commands

### Initialize (non-interactive — ALWAYS use this)

**IMPORTANT**: `shadcn init` is interactive by default. Always use `-d` (defaults) for non-interactive initialization:

```bash
# Non-interactive init with defaults — USE THIS
npx shadcn@latest init -d

# Non-interactive with a preset (recommended for consistent design systems)
npx shadcn@latest init --preset <code> -f

# Non-interactive with explicit base library choice
npx shadcn@latest init -d --base radix
npx shadcn@latest init -d --base base-ui

# Scaffold a full project template (CLI v4)
```

> **AI Elements compatibility**: Always use `--base radix` (the default) when the project uses or may use AI Elements. AI Elements components rely on Radix APIs and have type errors with Base UI.

```bash
npx shadcn@latest init --template next -d
npx shadcn@latest init --template vite -d
```

Options:
- `-d, --defaults` — **Use default configuration, skip all interactive prompts** (REQUIRED for CI/agent use)
- `-y, --yes` — Skip confirmation prompts (does NOT skip library selection — use `-d` instead)
- `-f, --force` — Force overwrite existing configuration
- `-t, --template` — Scaffold full project template (`next`, `vite`, `react-router`, `astro`, `laravel`, `tanstack-start`)
- `--preset` — Apply a design system preset (colors, theme, icons, fonts, radius) as a single shareable code
- `--base` — Choose primitive library: `radix` (default) or `base-ui`
- `--monorepo` — Set up a monorepo structure

> **WARNING**: `-y`/`--yes` alone does NOT make init fully non-interactive — it still prompts for component library selection. Always use `-d` to skip ALL prompts.

> **Deprecated in CLI v4**: `--style`, `--base-color`, `--src-dir`, `--no-base-style`, and `--css-variables` flags are removed and will error. The `registry:build` and `registry:mcp` registry types are also deprecated. Use `registry:base` and `registry:font` instead.

The init command:
1. Detects your framework (Next.js, Vite, React Router, Astro, Laravel, TanStack Start)
2. Installs required dependencies (Radix UI, tailwind-merge, class-variance-authority)
3. Creates `components.json` configuration
4. Sets up the `cn()` utility function
5. Configures CSS variables for theming

### Add Components

```bash
# Add specific components
npx shadcn@latest add button dialog card

# Add all available components
npx shadcn@latest add --all

# Add from a custom registry
npx shadcn@latest add @v0/dashboard
npx shadcn@latest add @acme/custom-button

# Add from AI Elements registry
npx shadcn@latest add https://elements.ai-sdk.dev/api/registry/all.json
```

Options:
- `-o, --overwrite` — Overwrite existing files
- `-p, --path` — Custom install path
- `-a, --all` — Install all components
- `--dry-run` — Preview what will be added without writing files
- `--diff` — Show diff of changes when updating existing components
- `--view` — Display a registry item's source code inline

### Search & List

```bash
npx shadcn@latest search button
npx shadcn@latest list @v0
```

### Build (Custom Registry)

```bash
npx shadcn@latest build
npx shadcn@latest build ./registry.json -o ./public/r
```

### View, Info & Docs (CLI v4)

```bash
# View a registry item's source before installing
npx shadcn@latest view button

# Show project diagnostics — config, installed components, dependencies
npx shadcn@latest info

# Get docs, code, and examples for any component (agent-friendly output)
npx shadcn@latest docs button
npx shadcn@latest docs dialog
```

> **`shadcn docs`** gives coding agents the context to use primitives correctly — returns code examples, API reference, and usage patterns inline.

### Migrate

```bash
npx shadcn@latest migrate rtl    # RTL support migration
npx shadcn@latest migrate radix  # Migrate to unified radix-ui package
npx shadcn@latest migrate icons  # Icon library changes

# Migrate components outside the default ui directory
npx shadcn@latest migrate radix src/components/custom
```

## shadcn/skills (CLI v4)

shadcn/skills gives coding agents the context they need to work with components and registries correctly. It covers both Radix and Base UI primitives, updated APIs, component patterns, and registry workflows. The skill knows how to use the CLI, when to invoke it, and which flags to pass — so agents produce code that matches your design system.

Install: `pnpm dlx skills add shadcn/ui`

## Unified Radix UI Package (February 2026)

The `new-york` style now uses a single `radix-ui` package instead of individual `@radix-ui/react-*` packages:

```tsx
// OLD — individual packages
import * as DialogPrimitive from "@radix-ui/react-dialog"

// NEW — unified package
import { Dialog as DialogPrimitive } from "radix-ui"
```

To migrate existing projects: `npx shadcn@latest migrate radix`. After migration, remove unused `@radix-ui/react-*` packages from `package.json`.

## Base UI Support (January 2026)

shadcn/ui now supports **Base UI** as an alternative to Radix UI for the underlying primitive library. Components look and behave the same way regardless of which library you choose — only the underlying implementation changes.

Choose during init: `npx shadcn@latest init --base base-ui`

The CLI pulls the correct component variant based on your project configuration automatically.

## Configuration (components.json)

The `components.json` file configures how shadcn/ui works in your project:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "zinc",  // Options: gray, neutral, slate, stone, zinc, mauve, olive, mist, taupe
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {
    "v0": {
      "url": "https://v0.dev/chat/api/registry"
    },
    "ai-elements": {
      "url": "https://elements.ai-sdk.dev/api/registry"
    }
  }
}
```

### Namespaced Registries

Configure multiple registries for your project:

```json
{
  "registries": {
    "acme": {
      "url": "https://acme.com/registry/{name}.json"
    },
    "private": {
      "url": "https://internal.company.com/registry/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}"
      }
    }
  }
}
```

Install using namespace syntax:

```bash
npx shadcn@latest add @acme/header @private/auth-form
```

## Theming

### CSS Variables

shadcn/ui uses CSS custom properties for theming, defined in `globals.css`:

```css
@theme inline {
  --color-background: oklch(0.145 0 0);
  --color-foreground: oklch(0.985 0 0);
  --color-card: oklch(0.205 0 0);
  --color-card-foreground: oklch(0.985 0 0);
  --color-primary: oklch(0.488 0.243 264.376);
  --color-primary-foreground: oklch(0.985 0 0);
  --color-secondary: oklch(0.269 0 0);
  --color-secondary-foreground: oklch(0.985 0 0);
  --color-muted: oklch(0.269 0 0);
  --color-muted-foreground: oklch(0.708 0 0);
  --color-accent: oklch(0.269 0 0);
  --color-accent-foreground: oklch(0.985 0 0);
  --color-destructive: oklch(0.396 0.141 25.723);
  --color-border: oklch(0.269 0 0);
  --color-input: oklch(0.269 0 0);
  --color-ring: oklch(0.488 0.243 264.376);
  --radius: 0.625rem;
  /* CLI v4: radius tokens use multiplicative calc instead of additive */
  --radius-xs: calc(var(--radius) * 0.5);
  --radius-sm: calc(var(--radius) * 0.75);
  --radius-md: calc(var(--radius) * 0.875);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.5);
}
```

### Dark Mode

For dark mode, use the `dark` class on `<html>`:

```tsx
// app/layout.tsx
<html lang="en" className="dark">
```

Or use next-themes for toggling:

```tsx
import { ThemeProvider } from 'next-themes'

<ThemeProvider attribute="class" defaultTheme="dark">
  {children}
</ThemeProvider>
```

### Custom Colors

Add application-specific colors alongside shadcn defaults:

```css
@theme inline {
  /* shadcn defaults above... */

  /* Custom app colors */
  --color-priority-urgent: oklch(0.637 0.237 15.163);
  --color-priority-high: oklch(0.705 0.213 47.604);
  --color-status-done: oklch(0.723 0.219 149.579);
}
```

Use in components:

```tsx
<span className="text-[var(--color-priority-urgent)]">Urgent</span>
// Or with Tailwind v4 theme():
<span className="text-priority-urgent">Urgent</span>
```

## Most Common Components

| Component | Use Case |
|-----------|----------|
| `button` | Actions, form submission |
| `card` | Content containers |
| `dialog` | Modals, confirmation prompts |
| `input` / `textarea` | Form fields |
| `select` | Dropdowns |
| `table` | Data display |
| `tabs` | View switching |
| `command` | Command palette (Cmd+K) |
| `dropdown-menu` | Context menus |
| `popover` | Floating content |
| `tooltip` | Hover hints |
| `badge` | Status indicators |
| `avatar` | User profile images |
| `scroll-area` | Scrollable containers |
| `separator` | Visual dividers |
| `label` | Form labels |
| `sheet` | Slide-out panels |
| `skeleton` | Loading placeholders |

## Design Direction for shadcn on Vercel

shadcn/ui is not only a component source generator. In the Vercel stack it is the default interface language. Do not stop at "the component works." Compose pages that feel deliberate, high-signal, and consistent.

### Default aesthetic for product UI

- Prefer style: `new-york` for product, dashboard, AI, and admin surfaces.
- Default to dark mode for dashboards, AI apps, internal tools, settings, and developer-facing products. Use light mode only when the product is clearly content-first or editorial.
- Use Geist Sans for interface text and Geist Mono for code, metrics, IDs, timestamps, commands.
- Prefer zinc, neutral, or slate as the base palette. Use one accent color through `--color-primary`.
- Build core surfaces from tokens: `bg-background`, `bg-card`, `text-foreground`, `text-muted-foreground`, `border-border`, `ring-ring`. Avoid ad-hoc hex values.
- Keep radius consistent. The default `--radius: 0.625rem` is a strong baseline.
- Use one density system per page: comfortable (`gap-6` / `p-6` / `text-sm`) or compact (`gap-4` / `p-4` / `text-sm`).
- Keep icons quiet and consistent. Lucide icons at `h-4 w-4` or `h-5 w-5`.

### Reach for this first

| Use case | Reach for this first | Why |
|----------|----------------------|-----|
| Settings page | `Tabs` + `Card` + `Form` | Clear information grouping with predictable save flows |
| Data dashboard | `Card` + `Badge` + `Table` + `DropdownMenu` | Covers summary, status, dense data, and row actions without custom shells |
| CRUD table | `Table` + `DropdownMenu` + `Sheet` + `AlertDialog` | Supports browse, act, edit, and destructive confirmation in a standard pattern |
| Auth screen | `Card` + `Label` + `Input` + `Button` + `Alert` | Keeps entry flows focused and gives errors a proper treatment |
| Global search | `Command` + `Dialog` | Fast keyboard-first discovery with an established interaction model |
| Mobile nav | `Sheet` + `Button` + `Separator` | Provides a compact navigation shell that adapts cleanly to small screens |
| Detail page | header + `Badge` + `Separator` + `Card` | Balances hierarchy, metadata, and supporting content without over-nesting |
| Filters | `Card` sidebar + `Sheet` + `Select` | Works for persistent desktop filters and collapsible mobile controls |
| Empty/loading/error states | `Card` + `Skeleton` + `Alert` | Gives non-happy paths a designed surface instead of placeholder text |

### Composition recipes

- Settings page: `Tabs` + `Card` per group + `Separator` + save action
- Admin dashboard: summary `Card`s + filter bar + `Table`
- Entity detail: header + status `Badge` + main `Card` + side `Card` + `AlertDialog` for destructive
- Search-heavy: `Command` for quick find, `Popover` for pickers, `Sheet` for mobile filters
- Auth/onboarding: centered `Card` + social `Separator` + inline `Alert` for errors
- Destructive flows: `AlertDialog` (not `Dialog`) for confirmation

### Anti-patterns to avoid

- Raw `button` / `input` / `select` / `div` when shadcn primitives exist
- Repeated `div rounded-xl border p-6` instead of `Tabs` / `Table` / `Sheet` / `Dialog`
- Multiple accent colors fighting each other
- Nested cards inside cards inside cards
- Large gradient backgrounds and glassmorphism on every surface
- Mixing arbitrary spacing and radius values
- Using `Dialog` for destructive confirmation instead of `AlertDialog`
- Shipping empty/loading/error states without design treatment
- Using ad-hoc Tailwind palette classes for foundational surfaces instead of theme tokens

## Building a Custom Registry

Create your own component registry to share across projects:

### Registry Types (CLI v4)

| Type | Purpose |
|------|---------|
| `registry:ui` | Individual UI components |
| `registry:base` | Full design system payload — components, deps, CSS vars, fonts, config |
| `registry:font` | Font configuration as a first-class registry item |

### 1. Define registry.json

```json
[
  {
    "name": "my-component",
    "type": "registry:ui",
    "title": "My Component",
    "description": "A custom component",
    "files": [
      {
        "path": "components/my-component.tsx",
        "type": "registry:ui"
      }
    ],
    "dependencies": ["lucide-react"]
  }
]
```

### 2. Build

```bash
npx shadcn@latest build
# Outputs to public/r/my-component.json
```

### 3. Consume

```bash
npx shadcn@latest add https://your-domain.com/r/my-component.json
```

## Component Gotchas

### `shadcn init` Breaks Geist Font in Next.js (Tailwind v4)

`shadcn init` rewrites `globals.css` and may introduce `--font-sans: var(--font-sans)` — a circular self-reference that breaks font loading. Tailwind v4's `@theme inline` resolves CSS custom properties at **parse time**, not runtime — so even `var(--font-geist-sans)` won't work because Next.js injects that variable via className at runtime.

**The fix**: Use literal font family names in `@theme inline`:

```css
/* In @theme inline — CORRECT (literal names) */
--font-sans: "Geist", "Geist Fallback", ui-sans-serif, system-ui, sans-serif;
--font-mono: "Geist Mono", "Geist Mono Fallback", ui-monospace, monospace;

/* WRONG — circular, resolves to nothing */
--font-sans: var(--font-sans);

/* ALSO WRONG — @theme inline can't resolve runtime CSS variables */
--font-sans: var(--font-geist-sans);
```

**After running `shadcn init`**, always:
1. Replace font declarations in `@theme inline` with literal Geist font names (as shown above)
2. Move the font variable classNames from `<body>` to `<html>` in `layout.tsx`:

```tsx
// layout.tsx — font variables on <html>, not <body>
<html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
  <body className="antialiased">
```

### Avatar Has No `size` Prop

The shadcn Avatar component does **not** accept a `size` variant prop. Control size with Tailwind classes:

```tsx
// WRONG — no size variant exists
<Avatar size="lg" />  // ❌ TypeScript error / silently ignored

// CORRECT — use Tailwind
<Avatar className="h-12 w-12">
  <AvatarImage src={user.image} />
  <AvatarFallback>JD</AvatarFallback>
</Avatar>

// Small avatar
<Avatar className="h-6 w-6"> ... </Avatar>
```

This applies to most shadcn components — they use Tailwind classes for sizing, not variant props. If you need reusable size variants, add them yourself via `cva` in the component source.

## Common Patterns

### cn() Utility

All shadcn components use the `cn()` utility for conditional class merging:

```ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Extending Components

Since you own the source code, extend components directly:

```tsx
// components/ui/button.tsx — add your custom variant
const buttonVariants = cva('...', {
  variants: {
    variant: {
      default: '...',
      destructive: '...',
      // Add custom variants
      success: 'bg-green-600 text-white hover:bg-green-700',
      premium: 'bg-gradient-to-r from-purple-500 to-pink-500 text-white',
    },
  },
})
```

### Wrapping with TooltipProvider

Many components require `TooltipProvider` at the root:

```tsx
// app/layout.tsx
import { TooltipProvider } from '@/components/ui/tooltip'

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body>
        <TooltipProvider>{children}</TooltipProvider>
      </body>
    </html>
  )
}
```

## Framework Support

- **Next.js** — Full support (App Router + Pages Router)
- **Vite** — Full support
- **React Router** — Full support
- **Astro** — Full support
- **Laravel** — Full support (via Inertia)
- **TanStack Start** — Full support

## Presets (CLI v4)

Presets bundle your entire design system config (colors, theme, icon library, fonts, radius) into a single shareable code. One string configures everything:

```bash
# Apply a preset during init
npx shadcn@latest init --preset <code>

# Switch presets in an existing project (reconfigures everything including components)
npx shadcn@latest init --preset <code>
```

Build custom presets on `shadcn/create` — preview how colors, fonts, and radius apply to real components before publishing.

## RTL Support (2026)

The CLI handles RTL transformation at install time:

```bash
npx shadcn@latest migrate rtl
```

Converts directional classes (`ml-4`, `left-2`) to logical properties (`ms-4`, `start-2`) automatically.

## Official Documentation

- [shadcn/ui](https://ui.shadcn.com)
- [Components](https://ui.shadcn.com/docs/components)
- [CLI](https://ui.shadcn.com/docs/cli)
- [Theming](https://ui.shadcn.com/docs/theming)
- [Custom Registry](https://ui.shadcn.com/docs/registry)
- [Registry Directory](https://ui.shadcn.com/docs/directory)
- [GitHub: shadcn/ui](https://github.com/shadcn-ui/ui)
