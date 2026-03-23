---
name: turbopack
description: Turbopack expert guidance. Use when configuring the Next.js bundler, optimizing HMR, debugging build issues, or understanding the Turbopack vs Webpack differences.
metadata:
  priority: 4
  docs:
    - "https://turbo.build/pack/docs"
    - "https://nextjs.org/docs/architecture/turbopack"
  sitemap: "https://turbo.build/sitemap.xml"
  pathPatterns: 
    - 'next.config.*'
  bashPatterns: 
    - '\bnext\s+dev\s+--turbo\b'
    - '\bnext\s+dev\s+--turbopack\b'
retrieval:
  aliases:
    - next bundler
    - turbopack
    - fast bundler
    - hmr
  intents:
    - enable turbopack
    - fix build issue
    - speed up dev server
    - configure bundler
  entities:
    - Turbopack
    - HMR
    - bundler
    - next dev --turbopack
chainTo:
  -
    pattern: 'webpack\s*:\s*\(|webpack\s*\(config'
    targetSkill: nextjs
    message: 'Webpack config detected — loading Next.js guidance for migrating webpack customizations to Turbopack top-level config in Next.js 16.'
  -
    pattern: 'turbopack\s*:\s*\{|experimental\.turbopack'
    targetSkill: nextjs
    message: 'Turbopack configuration detected — loading Next.js guidance for top-level turbopack config syntax in Next.js 16 (moved from experimental.turbopack).'

---

# Turbopack

You are an expert in Turbopack — the Rust-powered JavaScript/TypeScript bundler built by Vercel. It is the default bundler in Next.js 16.

## Key Features

- **Instant HMR**: Hot Module Replacement that doesn't degrade with app size
- **File System Caching (Stable)**: Dev server artifacts cached on disk between restarts — up to 14x faster startup on large projects. Enabled by default in Next.js 16.1+, no config needed. Build caching planned next.
- **Multi-environment builds**: Browser, Server, Edge, SSR, React Server Components
- **Native RSC support**: Built for React Server Components from the ground up
- **TypeScript, JSX, CSS, CSS Modules, WebAssembly**: Out of the box
- **Rust-powered**: Incremental computation engine for maximum performance

## Configuration (Next.js 16)

In Next.js 16, Turbopack config is top-level (moved from `experimental.turbopack`):

```js
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  turbopack: {
    // Resolve aliases (like webpack resolve.alias)
    resolveAlias: {
      'old-package': 'new-package',
    },
    // Custom file extensions to resolve
    resolveExtensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
  },
}

export default nextConfig
```

## CSS and CSS Modules Handling

Turbopack handles CSS natively without additional configuration.

### Global CSS

Import global CSS in your root layout:

```tsx
// app/layout.tsx
import './globals.css'
```

### CSS Modules

CSS Modules work out of the box with `.module.css` files:

```tsx
// components/Button.tsx
import styles from './Button.module.css'

export function Button({ children }) {
  return <button className={styles.primary}>{children}</button>
}
```

### PostCSS

Turbopack reads your `postcss.config.js` automatically. Tailwind CSS v4 works with zero config:

```js
// postcss.config.js
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
```

### Sass / SCSS

Install `sass` and import `.scss` files directly — Turbopack compiles them natively:

```bash
npm install sass
```

```tsx
import styles from './Component.module.scss'
```

### Common CSS pitfalls

- **CSS ordering differs from webpack**: Turbopack may load CSS chunks in a different order. Avoid relying on source-order specificity across files — use more specific selectors or CSS Modules.
- **`@import` in global CSS**: Use standard CSS `@import` — Turbopack resolves them, but circular imports cause build failures.
- **CSS-in-JS libraries**: `styled-components` and `emotion` work but require their SWC plugins configured under `compiler` in next.config.

## Tree Shaking

Turbopack performs tree shaking at the module level in production builds. Key behaviors:

- **ES module exports**: Only used exports are included — write `export` on each function/constant rather than barrel `export *`
- **Side-effect-free packages**: Mark packages as side-effect-free in `package.json` to enable aggressive tree shaking:

```json
{
  "name": "my-ui-lib",
  "sideEffects": false
}
```

- **Barrel file optimization**: Turbopack can skip unused re-exports from barrel files (`index.ts`) when the package declares `"sideEffects": false`
- **Dynamic imports**: `import()` expressions create async chunk boundaries — Turbopack splits these into separate chunks automatically

### Diagnosing large bundles

**Built-in analyzer (Next.js 16.1+, experimental)**: Works natively with Turbopack. Offers route-specific filtering, import tracing, and RSC boundary analysis:

```ts
// next.config.ts
const nextConfig: NextConfig = {
  experimental: {
    bundleAnalyzer: true,
  },
}
```

**Legacy `@next/bundle-analyzer`**: Still works as a fallback:

```bash
ANALYZE=true next build
```

```ts
// next.config.ts
import withBundleAnalyzer from '@next/bundle-analyzer'

const nextConfig = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})({
  // your config
})
```

## Custom Loader Migration from Webpack

Turbopack does not support webpack loaders directly. Here is how to migrate common patterns:

| Webpack Loader | Turbopack Equivalent |
|----------------|---------------------|
| `css-loader` + `style-loader` | Built-in CSS support — remove loaders |
| `sass-loader` | Built-in — install `sass` package |
| `postcss-loader` | Built-in — reads `postcss.config.js` |
| `file-loader` / `url-loader` | Built-in static asset handling |
| `svgr` / `@svgr/webpack` | Use `@svgr/webpack` via `turbopack.rules` |
| `raw-loader` | Use `import x from './file?raw'` |
| `graphql-tag/loader` | Use a build-time codegen step instead |
| `worker-loader` | Use native `new Worker(new URL(...))` syntax |

### Configuring custom rules (loader replacement)

For loaders that have no built-in equivalent, use `turbopack.rules`:

```js
// next.config.ts
const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
}
```

### When migration isn't possible

If a webpack loader has no Turbopack equivalent and no workaround, fall back to webpack:

```js
const nextConfig: NextConfig = {
  bundler: 'webpack',
}
```

File an issue at [github.com/vercel/next.js](https://github.com/vercel/next.js) — the Turbopack team tracks loader parity requests.

## Production Build Diagnostics

### Build failing with Turbopack

1. **Check for unsupported config**: Remove any `webpack()` function from next.config — it's ignored by Turbopack and may mask the real config
2. **Verify `turbopack.rules`**: Ensure custom rules reference valid loaders that are installed
3. **Check for Node.js built-in usage in edge/client**: Turbopack enforces environment boundaries — `fs`, `path`, etc. cannot be imported in client or edge bundles
4. **Module not found errors**: Ensure `turbopack.resolveAlias` covers any custom resolution that was previously in webpack config

### Build output too large

- Audit `"use client"` directives — each client component boundary creates a new chunk
- Check for accidentally bundled server-only packages in client components
- Use `server-only` package to enforce server/client boundaries at import time:

```bash
npm install server-only
```

```ts
// lib/db.ts
import 'server-only' // Build fails if imported in a client component
```

### Comparing webpack vs Turbopack output

Run both bundlers and compare:

```bash
# Turbopack build (default in Next.js 16)
next build

# Webpack build
BUNDLER=webpack next build
```

Compare `.next/` output sizes and page-level chunks.

## Performance Profiling

### HMR profiling

Enable verbose HMR timing in development:

```bash
NEXT_TURBOPACK_TRACING=1 next dev
```

This writes a `trace.json` to the project root — open it in `chrome://tracing` or [Perfetto](https://ui.perfetto.dev/) to see module-level timing.

### Build profiling

Profile production builds:

```bash
NEXT_TURBOPACK_TRACING=1 next build
```

Look for:
- **Long-running transforms**: Indicates a slow SWC plugin or heavy PostCSS config
- **Large module graphs**: Reduce barrel file re-exports
- **Cache misses**: If incremental builds aren't hitting cache, check for files that change every build (e.g., generated timestamps)

### Memory usage

Turbopack's Rust core manages its own memory. If builds OOM:
- Increase Node.js heap: `NODE_OPTIONS='--max-old-space-size=8192' next build`
- Reduce concurrent tasks if running inside Turborepo: `turbo build --concurrency=2`

## Turbopack vs Webpack

| Feature | Turbopack | Webpack |
|---------|-----------|---------|
| Language | Rust | JavaScript |
| HMR speed | Constant (O(1)) | Degrades with app size |
| RSC support | Native | Plugin-based |
| Cold start | Fast | Slower |
| Ecosystem | Growing | Massive (loaders, plugins) |
| Status in Next.js 16 | Default | Still supported |
| Tree shaking | Module-level | Module-level |
| CSS handling | Built-in | Requires loaders |
| Production builds | Supported | Supported |

## When You Might Need Webpack

- Custom webpack loaders with no Turbopack equivalent
- Complex webpack plugin configurations (e.g., `ModuleFederationPlugin`)
- Specific webpack features not yet in Turbopack (e.g., custom `externals` functions)

To use webpack instead:
```js
// next.config.ts
const nextConfig: NextConfig = {
  bundler: 'webpack', // Opt out of Turbopack
}
```

## Development vs Production

- **Development**: Turbopack provides instant HMR and fast refresh
- **Production**: Turbopack handles the production build (replaces webpack in Next.js 16)

## Common Issues

1. **Missing loader equivalent**: Some webpack loaders don't have Turbopack equivalents yet. Check Turbopack docs for supported transformations.
2. **Config migration**: Move `experimental.turbopack` to top-level `turbopack` in next.config.
3. **Custom aliases**: Use `turbopack.resolveAlias` instead of `webpack.resolve.alias`.
4. **CSS ordering changes**: Test visual regressions when migrating — CSS chunk order may differ.
5. **Environment boundary errors**: Server-only modules imported in client components fail at build time — use `server-only` package.

## Official Documentation

- [Turbopack](https://turborepo.dev/pack)
- [Turbopack Documentation](https://turborepo.dev/pack/docs)
- [Next.js Turbopack Config](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack)
- [GitHub: Turbopack](https://github.com/vercel/turborepo)
