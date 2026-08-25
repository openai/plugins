# Testing & Troubleshooting Reference

## Testing Utilities

The `@vercel/microfrontends` package includes test utilities imported from `@vercel/microfrontends/next/testing`. All utilities throw exceptions on failure, so they work with any test framework.

### validateMiddlewareConfig

Validates that Next.js middleware is configured correctly for microfrontends. Run only on the **default application**.

Checks:

- Middleware matches `/.well-known/vercel/microfrontends/client-config`
- Middleware does **not** match paths routed to child microfrontends (those requests never reach the default app's middleware)
- Middleware **does** match all flagged paths

```ts
// tests/middleware.test.ts
/* @jest-environment node */
import { validateMiddlewareConfig } from "@vercel/microfrontends/next/testing";
import { config } from "../middleware";

describe("middleware", () => {
  test("matches microfrontends paths", () => {
    expect(() =>
      validateMiddlewareConfig(config, "./microfrontends.json"),
    ).not.toThrow();
  });
});
```

**Signature:**

```ts
function validateMiddlewareConfig(
  middlewareConfig: MiddlewareConfig,
  microfrontendConfigOrPath: string | MicrofrontendConfigIsomorphic,
  extraProductionMatches?: string[],
): void;
```

- `middlewareConfig`: The exported `config` from your `middleware.ts`
- `microfrontendConfigOrPath`: Path to `microfrontends.json` or a parsed config object
- `extraProductionMatches`: Optional paths that middleware intentionally matches despite being child app paths

### validateMiddlewareOnFlaggedPaths

Validates that middleware correctly rewrites flagged paths to the right microfrontend. **All flags must be enabled** before calling this function.

```ts
// tests/middleware.test.ts
/* @jest-environment node */
import { validateMiddlewareOnFlaggedPaths } from "@vercel/microfrontends/next/testing";
import { middleware } from "../middleware";

// Enable all flags before testing.
// This mock is specific to the Flags SDK; adapt if using a custom flag implementation.
jest.mock("flags/next", () => ({
  flag: jest.fn().mockReturnValue(jest.fn().mockResolvedValue(true)),
}));

describe("middleware", () => {
  test("rewrites for flagged paths", async () => {
    await expect(
      validateMiddlewareOnFlaggedPaths("./microfrontends.json", middleware),
    ).resolves.not.toThrow();
  });
});
```

**Signature:**

```ts
async function validateMiddlewareOnFlaggedPaths(
  microfrontendConfigOrPath: string | MicrofrontendConfigIsomorphic,
  middleware: (
    request: NextRequest,
    event: NextFetchEvent,
  ) => Promise<Response | undefined>,
): Promise<void>;
```

### validateRouting

Validates that specific paths route to the correct microfrontend application. Run only on the **default application** where `microfrontends.json` is defined.

```ts
// tests/microfrontends.test.ts
import { validateRouting } from "@vercel/microfrontends/next/testing";

describe("microfrontends", () => {
  test("routing", () => {
    expect(() => {
      validateRouting("./microfrontends.json", {
        marketing: ["/", "/products"],
        docs: ["/docs", "/docs/api"],
        dashboard: [
          "/dashboard",
          { path: "/new-dashboard", flag: "enable-new-dashboard" },
        ],
      });
    }).not.toThrow();
  });
});
```

**Signature:**

```ts
function validateRouting(
  microfrontendConfigOrPath: string | MicrofrontendConfigIsomorphic,
  routesToTest: Record<string, (string | { path: string; flag: string })[]>,
): void;
```

The `routesToTest` maps application names to arrays of paths. Each path can be:

- A string: `'/docs'` — asserts this path routes to the named app
- An object: `{ path: '/new-docs', flag: 'my-flag' }` — asserts this path routes to the named app when the flag is enabled

## Debug Headers

Enable debug headers to inspect routing decisions on deployed environments.

### Enabling

- Use the **Vercel Toolbar** → enable Routing Debug Mode, **or**
- Set browser cookie `VERCEL_MFE_DEBUG=1`

### Response headers

| Header                                   | Description                                                 |
| ---------------------------------------- | ----------------------------------------------------------- |
| `x-vercel-mfe-app`                       | Microfrontend project that handled the request              |
| `x-vercel-mfe-target-deployment-id`      | Deployment ID that handled the request                      |
| `x-vercel-mfe-default-app-deployment-id` | Default app deployment ID (source of `microfrontends.json`) |
| `x-vercel-mfe-zone-from-middleware`      | For flagged paths: which microfrontend middleware selected  |
| `x-vercel-mfe-matched-path`              | Path pattern from `microfrontends.json` that matched        |
| `x-vercel-mfe-response-reason`           | Internal reason for the routing decision                    |

## Debug Routing Locally

Enable debug logging for the local proxy:

1. Set `MFE_DEBUG=1` environment variable, **or**
2. Pass `debug: true` to `withMicrofrontends`:

```ts
export default withMicrofrontends(nextConfig, { debug: true });
```

The proxy logs show:

- Which path matched which routing rule
- Whether the request went to a local app or fallback
- Environment variable and rewrite changes

## Observability & Tracing

### Observability dashboard

Microfrontend routing data appears in the **Observability** tab under the CDN section → Microfrontends.

### Session tracing

Routing is captured in [Session Tracing](https://vercel.com/docs/tracing/session-tracing). The Microfrontends span includes:

| Attribute                              | Description                                          |
| -------------------------------------- | ---------------------------------------------------- |
| `vercel.mfe.app`                       | Microfrontend that handled the request               |
| `vercel.mfe.target_deployment_id`      | Target deployment ID                                 |
| `vercel.mfe.default_app_deployment_id` | Default app deployment ID                            |
| `vercel.mfe.app_from_middleware`       | Microfrontend selected by middleware (flagged paths) |
| `vercel.mfe.matched_path`              | Matched path pattern                                 |

## Common Issues

### Microfrontends aren't working in local development

1. Enable debug logging (`MFE_DEBUG=1`) to see routing decisions
2. Verify the proxy is running and you're accessing the proxy URL (not the app's direct port)
3. Check that `--local-apps` includes the correct app name
4. Verify `microfrontends.json` is accessible (auto-detected in monorepos, needs manual config in polyrepos)

### Requests not routed to the correct microfrontend in production

1. Verify the path is covered by the routing config using the [Deployment Summary](https://vercel.com/docs/deployments#resources-tab-and-deployment-summary) or Vercel Toolbar
2. Enable [debug headers](#debug-headers) and inspect `x-vercel-mfe-matched-path` and `x-vercel-mfe-app`
3. Check [session traces](#session-tracing) for detailed routing information

### Middleware not running for flagged paths

- Ensure flagged paths are listed in the middleware `matcher` config
- Verify `/.well-known/vercel/microfrontends/client-config` is in the matcher
- Use `validateMiddlewareConfig` and `validateMiddlewareOnFlaggedPaths` tests to catch misconfigurations

### Asset 404 errors

- Verify the asset prefix is correctly configured and routed in `microfrontends.json`
- For Next.js `public/` directory files, move them to a subdirectory matching the asset prefix
- Check that `withMicrofrontends` (or the Vite plugin) is applied to the framework config

### Deployment protection blocking fallbacks locally

- The default app's `VERCEL_AUTOMATION_BYPASS_SECRET` is used to bypass protection on child projects — ensure that secret is also added as a [Protection Bypass for Automation](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation) secret in each protected child project
- Add `VERCEL_AUTOMATION_BYPASS_SECRET=<secret>` to the default app's local environment file (e.g. `.env.local`)
