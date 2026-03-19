---
name: satori
description: Expert guidance for Satori — Vercel's library that converts HTML and CSS to SVG, commonly used to generate dynamic OG images for Next.js and other frameworks.
metadata:
  priority: 4
  docs:
    - "https://github.com/vercel/satori"
    - "https://nextjs.org/docs/app/api-reference/file-conventions/metadata/opengraph-image"
  sitemap: "https://nextjs.org/sitemap.xml"
  pathPatterns:
    - 'app/**/og/**'
    - 'app/**/og.*'
    - 'app/**/opengraph-image.*'
    - 'app/**/twitter-image.*'
    - 'src/app/**/og/**'
    - 'src/app/**/og.*'
    - 'src/app/**/opengraph-image.*'
    - 'src/app/**/twitter-image.*'
    - 'pages/api/og.*'
    - 'pages/api/og/**'
    - 'src/pages/api/og.*'
    - 'src/pages/api/og/**'
    - 'apps/*/app/**/og/**'
    - 'apps/*/app/**/og.*'
    - 'apps/*/app/**/opengraph-image.*'
    - 'apps/*/app/**/twitter-image.*'
  importPatterns:
    - 'satori'
    - 'satori/wasm'
    - '@vercel/og'
    - 'next/og'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bsatori\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bsatori\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bsatori\b'
    - '\byarn\s+add\s+[^\n]*\bsatori\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/og\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/og\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/og\b'
    - '\byarn\s+add\s+[^\n]*@vercel/og\b'
retrieval:
  aliases:
    - og image
    - social image
    - html to svg
    - open graph
  intents:
    - generate og image
    - create social image
    - convert html to svg
    - dynamic og
  entities:
    - Satori
    - OG image
    - SVG
    - open graph
chainTo:
  -
    pattern: 'from\s+[''""]puppeteer[''""]|from\s+[''""]playwright[''""]|launch\(\s*\{.*headless'
    targetSkill: vercel-functions
    message: 'Headless browser for OG image generation detected — Satori generates OG images without a browser. Loading Functions guidance for lightweight serverless deployment.'
  -
    pattern: 'from\s+[''""]canvas[''""]|createCanvas\('
    targetSkill: vercel-functions
    message: 'Node canvas for image generation detected — Satori uses JSX-to-SVG without native dependencies. Loading Functions guidance for serverless-compatible OG images.'

---

# Satori — HTML/CSS to SVG for OG Images

You are an expert in Satori and `@vercel/og` for generating dynamic Open Graph images.

## Overview

**Satori** converts JSX-like HTML and CSS into SVG. **`@vercel/og`** wraps Satori with an `ImageResponse` class that renders the SVG to PNG, designed to run in Vercel Edge Functions and other edge runtimes.

## Installation

```bash
# For Next.js projects (recommended — includes Satori + PNG rendering)
npm install @vercel/og

# Standalone Satori (SVG output only)
npm install satori
```

## Next.js App Router — OG Image Route (Recommended)

Next.js has built-in OG image support via the `ImageResponse` re-exported from `next/og`:

```tsx
// app/og/route.tsx  OR  app/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const runtime = 'edge'

export async function GET(request: Request) {
  return new ImageResponse(
    (
      <div
        style={{
          display: 'flex',
          fontSize: 60,
          color: 'white',
          background: 'linear-gradient(to bottom, #1a1a2e, #16213e)',
          width: '100%',
          height: '100%',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        Hello, OG Image!
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

## Convention-Based OG Images (Next.js 13.3+)

Place an `opengraph-image.tsx` or `twitter-image.tsx` file in any route segment:

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const alt = 'Blog post image'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const runtime = 'edge'

export default async function Image({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)

  return new ImageResponse(
    (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          height: '100%',
          background: '#000',
          color: '#fff',
          fontSize: 48,
        }}
      >
        <div>{post.title}</div>
      </div>
    ),
    { ...size }
  )
}
```

Next.js auto-generates the `<meta property="og:image">` tag for these files.

## Standalone Satori (SVG Only)

```ts
import satori from 'satori'
import { readFileSync } from 'fs'

const svg = await satori(
  <div style={{ display: 'flex', color: 'black', fontSize: 40 }}>
    Hello from Satori
  </div>,
  {
    width: 1200,
    height: 630,
    fonts: [
      {
        name: 'Inter',
        data: readFileSync('./fonts/Inter-Regular.ttf'),
        weight: 400,
        style: 'normal',
      },
    ],
  }
)
```

## CSS Support and Limitations

Satori uses a subset of CSS with Flexbox layout (Yoga engine):

**Supported:**
- `display: flex` (default — all elements are flex containers)
- Flexbox properties: `flexDirection`, `alignItems`, `justifyContent`, `flexWrap`, `gap`
- Box model: `width`, `height`, `padding`, `margin`, `border`, `borderRadius`
- Typography: `fontSize`, `fontWeight`, `fontFamily`, `lineHeight`, `letterSpacing`, `textAlign`
- Colors: `color`, `background`, `backgroundColor`, `opacity`
- Backgrounds: `backgroundImage` (linear/radial gradients), `backgroundClip`
- Shadows: `boxShadow`, `textShadow`
- Transforms: `transform` (basic transforms)
- Overflow: `overflow: hidden`
- Position: `absolute`, `relative`
- White space: `whiteSpace`, `wordBreak`, `textOverflow`

**Not supported:**
- `display: grid` — use nested flex containers instead
- CSS animations or transitions
- `position: fixed` or `sticky`
- Pseudo-elements (`::before`, `::after`)
- Media queries
- CSS variables

## Fonts

Fonts must be loaded explicitly — there are no default system fonts:

```tsx
// Load font in edge runtime
const font = fetch(new URL('./Inter-Bold.ttf', import.meta.url)).then(
  (res) => res.arrayBuffer()
)

export async function GET() {
  const fontData = await font

  return new ImageResponse(
    (<div style={{ fontFamily: 'Inter' }}>Hello</div>),
    {
      width: 1200,
      height: 630,
      fonts: [{ name: 'Inter', data: fontData, weight: 700, style: 'normal' }],
    }
  )
}
```

For Google Fonts, fetch directly from the CDN or bundle the `.ttf` file.

## Dynamic Content from URL Parameters

```tsx
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const title = searchParams.get('title') ?? 'Default Title'

  return new ImageResponse(
    (<div style={{ display: 'flex', fontSize: 60 }}>{title}</div>),
    { width: 1200, height: 630 }
  )
}
```

## Images in OG

Use `<img>` with absolute URLs:

```tsx
<img
  src="https://example.com/avatar.png"
  width={100}
  height={100}
  style={{ borderRadius: '50%' }}
/>
```

For local images, convert to base64 or use absolute deployment URLs.

## Key Patterns

1. **Use `next/og` in Next.js projects** — it re-exports `ImageResponse` with built-in optimizations
2. **Always set `runtime = 'edge'`** — Satori and `@vercel/og` are designed for edge runtimes
3. **Use `display: 'flex'` everywhere** — Satori defaults to flex layout, no block or grid support
4. **Load fonts explicitly** — no system fonts are available; bundle `.ttf`/`.woff` files or fetch from CDN
5. **Standard OG dimensions are 1200×630** — this is the most widely supported size
6. **Use convention files for automatic `<meta>` tags** — `opengraph-image.tsx` and `twitter-image.tsx`
7. **Inline styles only** — Satori does not support external CSS or CSS-in-JS libraries

## Official Resources

- [Satori GitHub](https://github.com/vercel/satori)
- [Vercel OG Image Generation](https://vercel.com/docs/functions/og-image-generation)
- [Next.js Metadata — OG Images](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/opengraph-image)
- [Satori Playground](https://og-playground.vercel.app)
