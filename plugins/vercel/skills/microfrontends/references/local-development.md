# Local Development Reference

## Overview

The `@vercel/microfrontends` local development proxy routes requests between locally running microfrontends and production fallbacks. This allows developers to run only the microfrontend they're working on while still being able to navigate the full application.

**How it works:**

- The proxy listens on a single port (default `3024`)
- Requests matching a child app's routing paths are sent to the local dev server (if running) or to the production fallback
- Requests not matching any child app go to the default app

> **Warning (Next.js):** Traffic a child application receives directly will be redirected to the local proxy. Set `MFE_DISABLE_LOCAL_PROXY_REWRITE=1` to disable this.

## Application Setup

Configure each app's dev server to use the auto-assigned port so the proxy knows where to route:

```json
{
  "name": "web",
  "scripts": {
    "dev": "next dev --port $(microfrontends port)"
  },
  "dependencies": {
    "@vercel/microfrontends": "latest"
  }
}
```

### Custom ports

Set a specific port in `microfrontends.json`:

```json
{
  "applications": {
    "docs": {
      "routing": [{ "paths": ["/docs/:path*"] }],
      "development": {
        "local": 3001
      }
    }
  }
}
```

The `local` field accepts:

- A port number: `3001`
- A host: `my.localhost.me:3001`
- A full URL: `https://my.localhost.me:3030`

### packageName mapping

If the Vercel project name differs from `package.json` `name`:

```json
{
  "applications": {
    "docs": {
      "packageName": "my-docs-package",
      "routing": [{ "paths": ["/docs/:path*"] }]
    }
  }
}
```

## Starting the Local Proxy

### Monorepo with Turborepo

The proxy starts automatically when running a dev task with `turbo`:

```bash
turbo run dev --filter=web
```

This starts the `web` dev server and a proxy routing other microfrontends to production fallbacks.

> Requires `turbo` version `2.3.6` or `2.4.2` or newer.

Turborepo infers configuration from `microfrontends.json`, so no additional Turbo config is needed for microfrontends.

### Without Turborepo

Start the proxy manually:

```json
{
  "scripts": {
    "dev": "next dev --port $(microfrontends port)",
    "proxy": "microfrontends proxy microfrontends.json --local-apps web"
  }
}
```

Run both `dev` and `proxy` scripts simultaneously.

### Accessing the proxy

Visit the proxy URL shown in terminal output (default `http://localhost:3024`).

Change the port in `microfrontends.json`:

```json
{
  "options": {
    "localProxyPort": 4001
  }
}
```

## Polyrepo Setup

For separate repositories, the `microfrontends.json` file won't be auto-detected. You need to make it available to each repo.

### Option 1: Vercel CLI

```bash
vercel microfrontends pull
```

Downloads `microfrontends.json` from your default application. Requires Vercel CLI 44.2.2+.

### Option 2: Environment variable

```bash
export VC_MICROFRONTENDS_CONFIG=/path/to/microfrontends.json
```

Or in `.env`:

```
VC_MICROFRONTENDS_CONFIG=/path/to/microfrontends.json
```

### Running in polyrepo

1. Start your local microfrontend dev server (e.g., `next dev --port $(microfrontends port)`)
2. In the same or separate terminal, start the proxy:

```bash
microfrontends proxy --local-apps your-app-name
```

3. Visit the proxy URL (default `http://localhost:3024`)

## Proxy Command Reference

```
microfrontends proxy [configPath] --local-apps <names...> [--port <port>]
```

| Argument/Flag             | Description                                                           |
| ------------------------- | --------------------------------------------------------------------- |
| `[configPath]`            | Path to `microfrontends.json`. Optional in monorepos (auto-detected). |
| `--local-apps <names...>` | Space-separated list of locally running app names.                    |
| `--port <port>`           | Override the proxy port.                                              |

Example with multiple local apps:

```bash
microfrontends proxy microfrontends.json --local-apps web docs
```

## Port Configuration

```
microfrontends port
```

Prints the auto-assigned development port for the current application. The port is deterministic based on the application name and the microfrontends configuration.

Use in `package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev --port $(microfrontends port)"
  }
}
```

## Debug Routing

Enable debug logs to see where and why the proxy routed each request:

1. Set environment variable `MFE_DEBUG=1`, **or**
2. Pass `debug: true` to `withMicrofrontends`:

```ts
export default withMicrofrontends(nextConfig, { debug: true });
```

Debug output shows:

- Environment variables set by microfrontends
- Rewrites configured
- For each request: matched path, target application, local vs fallback

## Protected Deployment Fallbacks

To fall back to deployments with [Deployment Protection](https://vercel.com/docs/deployment-protection), set a bypass environment variable.

The local proxy reads `VERCEL_AUTOMATION_BYPASS_SECRET` from the default app's environment (Vercel sets this automatically as a system environment variable) and sends its value as the `x-vercel-protection-bypass` header when proxying to protected child project deployments.

### Setup steps

1. **Find the default app's secret**: in the default app's Vercel project, go to Settings → Deployment Protection → Protection Bypass for Automation → copy the secret (this is what Vercel exposes as `VERCEL_AUTOMATION_BYPASS_SECRET`)
2. **Add that secret to each child project**: in each child project's Vercel project, go to Settings → Deployment Protection → add a Protection Bypass for Automation secret using the same value
3. **Set locally**: add `VERCEL_AUTOMATION_BYPASS_SECRET=<secret>` to the default app's local environment file (e.g. `.env.local`)
