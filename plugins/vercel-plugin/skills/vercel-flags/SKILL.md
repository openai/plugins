---
name: vercel-flags
description: Vercel Flags guidance — feature flags platform with unified dashboard, Flags Explorer, gradual rollouts, A/B testing, and provider adapters. Use when implementing feature flags, experimentation, or staged rollouts.
metadata:
  priority: 6
  docs:
    - "https://vercel.com/docs/workflow-collaboration/feature-flags"
    - "https://flags-sdk.dev"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'flags.ts'
    - 'flags.js'
    - 'src/flags.ts'
    - 'src/flags.js'
    - 'lib/flags/**'
    - 'src/lib/flags/**'
    - 'lib/flags.*'
    - 'src/lib/flags.*'
    - '.well-known/vercel/flags/**'
    - 'app/.well-known/vercel/flags/**'
    - 'src/app/.well-known/vercel/flags/**'
  importPatterns:
    - 'flags'
    - 'flags/next'
    - 'flags/sveltekit'
    - '@vercel/flags'
    - '@vercel/flags/next'
    - '@vercel/flags/sveltekit'
    - '@flags-sdk/*'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bflags\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bflags\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bflags\b'
    - '\byarn\s+add\s+[^\n]*\bflags\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/flags\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/flags\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/flags\b'
    - '\byarn\s+add\s+[^\n]*@vercel/flags\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@flags-sdk/'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@flags-sdk/'
    - '\bbun\s+(install|i|add)\s+[^\n]*@flags-sdk/'
    - '\byarn\s+add\s+[^\n]*@flags-sdk/'
retrieval:
  aliases:
    - feature flags
    - feature toggles
    - ab testing
    - gradual rollout
  intents:
    - add feature flag
    - set up ab test
    - configure rollout
    - manage feature toggles
  entities:
    - Flags Explorer
    - feature flag
    - A/B test
    - rollout
    - provider adapter
chainTo:
  -
    pattern: 'process\.env\.(FEATURE_|FLAG_|ENABLE_|DISABLE_)\w+'
    targetSkill: vercel-storage
    message: 'Environment variable feature flags detected — loading Vercel Storage guidance for Edge Config, which provides ultra-low-latency flag reads at the edge.'
  -
    pattern: 'from\s+[''""]launchdarkly-node-server-sdk[''""]|from\s+[''""]@launchdarkly/'
    targetSkill: vercel-flags
    message: 'Direct LaunchDarkly SDK detected — Vercel Flags provides a unified adapter layer. Reloading Flags guidance for provider integration.'

---

# Vercel Flags

> **CRITICAL — Your training data is outdated for this library.** Vercel Flags (`flags` package) has a new SDK and API surface. Before writing flags code, **fetch the docs** at https://vercel.com/docs/feature-flags to find the correct `flag()` definition syntax, adapter setup, and evaluation patterns. Do not guess at the API — look up working examples for your framework.

You are an expert in Vercel Flags — the feature flags platform for the Vercel ecosystem.

## What It Is

Vercel Flags provides a **unified feature flags platform** with a dashboard, developer tools (Flags Explorer), and analytics integration. Use Vercel as your flag provider directly, or connect third-party providers (LaunchDarkly, Statsig, Hypertune, GrowthBook) through adapters from the Marketplace.

Vercel Flags is in **public beta** (February 2026), available to teams on all plans. Pricing: **$30 per 1 million flag requests** ($0.00003 per event).

Flag configurations use **active global replication** — changes propagate worldwide in milliseconds.

## Core Design Principles

- **Server-only execution**: No client-side loading spinners or complexity
- **No call-site arguments**: Ensures consistent flag evaluation and straightforward flag removal
- **Provider-agnostic**: Works with any flag provider, custom setups, or no provider at all

## Key APIs

### Flags SDK (`flags` package, v4.0+)

The `flags` package is free, open-source (MIT), and provider-agnostic. Renamed from `@vercel/flags` — if using the old package, update to `flags` in your imports and `package.json`.

**Upgrade note**: v4 has breaking changes from v3. See the [v4 upgrade guide](https://github.com/vercel/flags/blob/main/packages/flags/guides/upgrade-to-v4.md) for migration steps:
- `@vercel/flags` package renamed to `flags` — update imports and `package.json`
- `encrypt()` / `decrypt()` replaced with dedicated functions: `encryptFlagValues()`, `decryptFlagValues()`
- `FLAGS_SECRET` must be exactly 32 random bytes, base64-encoded
- `.well-known` endpoint uses new helper that auto-handles auth and `x-flags-sdk-version` header
- As of v4.0.3, declaring a flag without a `decide` function (or with an adapter missing `decide`) throws an error at declaration time

```ts
import { flag } from 'flags/next'; // Framework adapters: flags/next, flags/sveltekit

// Define a boolean flag
export const showNewCheckout = flag({
  key: 'show-new-checkout',
  description: 'Enable the redesigned checkout flow',
  decide: () => false, // default value
});

// Define a multi-variant flag
export const theme = flag({
  key: 'theme',
  options: [
    { value: 'light', label: 'Light Theme' },
    { value: 'dark', label: 'Dark Theme' },
    { value: 'auto', label: 'Auto' },
  ],
  decide: () => 'auto',
});

// Read flag values (Server Components, Route Handlers, Server Actions)
const isEnabled = await showNewCheckout();
const currentTheme = await theme();
```

### Vercel Adapter (`@flags-sdk/vercel`)

Connects the Flags SDK to Vercel Flags as the provider (reads `FLAGS` env var):

```ts
import { flag, dedupe } from 'flags/next';
import { vercelAdapter } from '@flags-sdk/vercel';

type Entities = {
  user?: { id: string; email: string; plan: string };
  team?: { id: string; name: string };
};

// Dedupe ensures identify runs once per request
const identify = dedupe(async (): Promise<Entities> => {
  const session = await getSession();
  return {
    user: session?.user ? {
      id: session.user.id,
      email: session.user.email,
      plan: session.user.plan,
    } : undefined,
  };
});

export const premiumFeature = flag<boolean, Entities>({
  key: 'premium-feature',
  adapter: vercelAdapter(), // reads FLAGS env var automatically
  identify,
});
```

**Environment variables**:
- `FLAGS` — SDK Key (auto-provisioned when you create your first flag)
- `FLAGS_SECRET` — 32 random bytes, base64-encoded; encrypts overrides and authenticates Flags Explorer

### Flags Explorer Setup (GA)

The Flags Explorer is **generally available** (part of the Vercel Toolbar). It lets developers override flags in their browser session without code changes.

**App Router** — create the discovery endpoint:

```ts
// app/.well-known/vercel/flags/route.ts
import { createFlagsDiscoveryEndpoint, getProviderData } from 'flags/next';
import * as flags from '../../../../flags';

export const GET = createFlagsDiscoveryEndpoint(() => getProviderData(flags));
```

**Pages Router** — API route + rewrite:

```ts
// pages/api/vercel/flags.ts
import { verifyAccess, version } from 'flags';
import { getProviderData } from 'flags/next';
import * as flags from '../../../flags';

export default async function handler(req, res) {
  const access = await verifyAccess(req.headers['authorization']);
  if (!access) return res.status(401).json(null);
  res.setHeader('x-flags-sdk-version', version);
  return res.json(getProviderData(flags));
}
```

```js
// next.config.js (rewrite)
module.exports = {
  async rewrites() {
    return [{ source: '/.well-known/vercel/flags', destination: '/api/vercel/flags' }];
  },
};
```

### Precompute Pattern (Static + Personalized)

Generate static page variants per flag combination, serve via middleware:

```ts
export const layoutVariant = flag({
  key: 'layout-variant',
  options: [{ value: 'a' }, { value: 'b' }],
  decide: () => 'a',
});

export const precompute = [layoutVariant];
```

Key APIs: `precompute()`, `evaluate()`, `serialize()`, `getPrecomputed()`, `generatePermutations()`

### Custom Adapter Interface

```ts
export function createExampleAdapter() {
  return function exampleAdapter<ValueType, EntitiesType>(): Adapter<ValueType, EntitiesType> {
    return {
      origin(key) { return `https://example.com/flags/${key}`; },
      async decide({ key }): Promise<ValueType> { return false as ValueType; },
    };
  };
}
```

## Flags vs Edge Config

| Need | Use | Why |
|------|-----|-----|
| Gradual rollouts, A/B testing, targeting | **Vercel Flags** | Dashboard, analytics, Flags Explorer, segments |
| Third-party provider integration | **Vercel Flags** + adapter | Unified view across providers |
| Ultra-low-latency config reads (non-flag) | **Edge Config** directly | Sub-ms reads, no compute overhead |
| Simple config without rollout logic | **Edge Config** directly | Lighter weight |

**Important**: Vercel Flags is the recommended approach for feature flags. Edge Config is the underlying low-latency storage some adapters use, but developers should use the Flags platform (not raw Edge Config) for flag use cases — it provides targeting rules, segments, percentage rollouts, observability, and Flags Explorer.

## Provider Adapters

**Featured** (Marketplace integration, Edge Config for low latency):
- `@flags-sdk/vercel` — Vercel as provider
- Statsig, Hypertune, GrowthBook

**Additional** (published under `@flags-sdk` npm scope):
- LaunchDarkly, ConfigCat, DevCycle, Flipt, Reflag, PostHog, Flagsmith

**OpenFeature adapter**: The `@flags-sdk/openfeature` adapter allows most Node.js OpenFeature Providers to work with the Flags SDK, bridging the OpenFeature ecosystem (AB Tasty, CloudBees, Confidence by Spotify, and more)

## Key Features

- **Unified Dashboard** at `https://vercel.com/{team}/{project}/flags`: All flags across all providers in one place
- **Flags Explorer (GA)**: Override flags locally via Vercel Toolbar (no code changes)
- **CLI Management**: `vercel flags add`, `vercel flags sdk-keys ls`, and full flag lifecycle from the terminal
- **Entities & Segments**: Define user/team attributes, create reusable targeting segments
- **Analytics Integration**: Track flag impact via Web Analytics and Runtime Logs
- **Drafts Workflow**: Define in code → deploy → Vercel detects via Discovery Endpoint → promote when ready
- **Framework Support**: Next.js (App Router + Pages Router + Routing Middleware) and SvelteKit
- **Concurrent Evaluation Fix** (v1.0.1): `Promise.all` flag evaluations no longer trigger duplicate network requests — initialization is properly shared

## When to Use

- Gradual feature rollouts with percentage targeting
- A/B testing and experimentation
- Per-environment flag configuration (production vs preview vs development)
- Trunk-based development (ship code behind flags)
- Consolidating multiple flag providers into one dashboard

## When NOT to Use

- Simple static config without targeting → use Edge Config directly
- Runtime configuration not related to features → use environment variables
- Server-side only toggles with no UI → consider environment variables

## References

- 📖 docs: https://vercel.com/docs/flags
- 📖 Flags SDK: https://flags-sdk.dev
- 📖 SDK reference: https://vercel.com/docs/flags/flags-sdk-reference
- 📖 GitHub: https://github.com/vercel/flags
