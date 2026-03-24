---
name: vercel-services
description: "Vercel Services — deploy multiple services within a single Vercel project. Use for monorepo layouts or when combining a backend (Python, Go) with a frontend (Next.js, Vite) in one deployment."
summary: "Deploy multiple services in one Vercel project — e.g. a Python backend alongside a JS frontend"
metadata:
  priority: 7
  docs:
    - "https://vercel.com/docs/services"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'backend/**'
    - 'backend/main.py'
    - 'backend/main.go'
    - 'backend/go.mod'
    - 'backend/pyproject.toml'
    - 'backend/requirements.txt'
    - 'frontend/**'
    - 'apps/*/backend/**'
    - 'apps/*/frontend/**'
    - 'services/*/vercel.json'
    - '*/pyproject.toml'
    - '*/go.mod'
  bashPatterns:
    - '\bvercel\s+dev\b.*-L'
    - '\bpip\s+install\b.*fastapi'
    - '\buv\s+(sync|pip|run)\b'
    - '\bgo\s+(run|build|mod)\b'
    - '\bpython\s+-m\s+uvicorn\b'
    - '\buvicorn\b'
  importPatterns:
    - "fastapi"
  promptSignals:
    phrases:
      - "services api"
      - "vercel services"
      - "multi-service"
      - "python backend"
      - "go backend"
      - "fastapi"
      - "deploy backend"
      - "backend and frontend"
      - "multiple services"
    allOf:
      - [backend, frontend]
      - [python, vercel]
      - [go, vercel]
      - [backend, deploy]
      - [service, monorepo]
      - [fastapi, deploy]
    anyOf:
      - "backend"
      - "monorepo"
      - "service"
      - "python"
      - "golang"
    noneOf:
      - "turborepo cache"
      - "turbo.json"
      - "aws lambda"
      - "docker compose"
    minScore: 6
validate:
  -
    pattern: '@app\.(get|post|put|delete|patch)\s*\(\s*[''"]\/api\/'
    message: 'Do not include routePrefix in backend routes — Vercel strips the prefix before forwarding. Use @app.get("/health") not @app.get("/api/health")'
    severity: error
  -
    pattern: 'http\.HandleFunc\s*\(\s*[''"]\/api\/'
    message: 'Do not include routePrefix in Go handlers — Vercel strips the prefix. Use "/health" not "/api/health"'
    severity: error
retrieval:
  aliases:
    - multi-service
    - backend service
    - services api
    - monorepo deploy
    - monorepo services
  intents:
    - deploy backend and frontend together on vercel
    - set up python backend alongside next.js frontend
    - configure multi-service vercel project
    - add go backend to vercel project
  entities:
    - experimentalServices
    - routePrefix
    - entrypoint
    - Services API
    - vercel.json services
  examples:
    - deploy a fastapi backend with a react frontend
    - add a go api service to my vercel project
    - set up a multi-service monorepo on vercel
---

# Deploy multi-service projects with Vercel

Services let you deploy multiple independently-built units within a single Vercel project. The typical use case is combining different runtimes (e.g. Python + JavaScript) in one deployment with shared routing and environment variables, but services work for any combination — multiple services of the same runtime, different frameworks, or a mix.

This skill covers **project structure and configuration**. For the actual deployment, defer to the **deployments-cicd** skill.

## How It Works

A service is an independently built unit within your project, deployed to the same domain under a unique subpath. At build time, Vercel builds each service separately. At request time, Vercel routes incoming requests to the correct service based on the URL path prefix (longest prefix wins).

- Services are enabled via the `experimentalServices` field in `vercel.json` (see reference project).
- `vercel dev -L` auto-detects frameworks and runs all services locally as one application, handling routing automatically. The `-L` flag (short for `--local`) runs without authenticating with Vercel Cloud.
- Only `vercel.json` lives at the root. Each service manages its own dependencies independently.

## Configuration

Define services in `vercel.json`:

```json
{
  "experimentalServices": {
    "web": {
      "entrypoint": "apps/web",
      "routePrefix": "/"
    },
    "api": {
      "entrypoint": "backend/main.py",
      "routePrefix": "/server"
    }
  }
}
```

The project's Framework Preset must be set to **Services** in the Vercel dashboard.

### Configuration fields

| Field          | Required | Description                                                |
|----------------|----------|------------------------------------------------------------|
| `entrypoint`   | Yes      | Path to the service entrypoint file or directory.          |
| `routePrefix`  | Yes      | URL path prefix for routing (e.g. `/`, `/api`, `/svc/go`). |
| `framework`    | No       | Framework slug. Pins detection; auto-detected if unset.    |
| `memory`       | No       | Max available RAM in MB (128–10,240).                      |
| `maxDuration`  | No       | Execution timeout in seconds (1–900).                      |
| `includeFiles` | No       | Glob patterns for files to include in the deployment.      |
| `excludeFiles` | No       | Glob patterns for files to exclude from the deployment.    |

Do not add unknown fields — they will cause the build to fail.

## Supported runtimes and frameworks

Services is in beta. **Python** and **Go** are tested and production-ready. Other runtimes may work but are not yet validated.

### Python

Works with FastAPI, Flask, Django, or any ASGI/WSGI application. Framework is auto-detected. Set `entrypoint` to the application file (e.g. `"backend/main.py"`). Dependencies go in `pyproject.toml` in the service directory.

### Go

Set `entrypoint` to the service **directory** (e.g. `"backend"`), not a file. **Must** set `"framework": "go"` explicitly in `vercel.json` — auto-detection does not work for Go services. Dependencies in `go.mod` in the service directory.

### Other runtimes (untested)

Vercel supports Node.js, Bun, Rust, Ruby, Wasm, and Edge runtimes for functions. These can theoretically be used as services but are not yet validated.

## Routing

Vercel evaluates route prefixes from longest to shortest (most specific first), with the primary service (`/`) as the catch-all. Vercel automatically mounts services at their `routePrefix`, so service handlers should **not** include the prefix in their routes.

For frontend frameworks mounted on a subpath (not `/`), configure the framework's own base path (e.g. `basePath` in `next.config.js`) to match `routePrefix`.

## Environment variables

Vercel auto-generates URL variables so services can find each other:

| Variable                        | Example value                            | Availability | Use case                              |
|---------------------------------|------------------------------------------|--------------|---------------------------------------|
| `{SERVICENAME}_URL`             | `https://your-deploy.vercel.app/svc/api` | Server-side  | Server-to-server requests             |
| `NEXT_PUBLIC_{SERVICENAME}_URL` | `/svc/api`                               | Client-side  | Browser requests (relative, no CORS)  |

`SERVICENAME` is the key name from `experimentalServices`, uppercased. If you define an env var with the same name in project settings, your value takes precedence.

## Usage

1. Read `references/fastapi-vite/` for the canonical project layout.
2. Adapt the structure to the user's chosen runtimes — services can use any supported runtime, not just the ones in the reference.
3. Define service routes **without** the route prefix — Vercel strips the prefix before forwarding.
4. Validate that each service in `vercel.json` has `entrypoint` and `routePrefix`. Only set `framework` when auto-detection fails (required for Go).

## Output

After scaffolding, present the created file structure to the user. After deployment, present the deployment URL (refer to the **deployments-cicd** skill for details).

## Troubleshooting

### 404 on routes after deployment

The project needs the Services framework preset:

1. Go to Project Settings → Build & Deployment → Framework Preset
2. Select **Services** from the dropdown
3. Redeploy

### Routes return unexpected results

1. Ensure all services are picked up by `vercel dev` — check logs. If a service is missing, verify `vercel.json`. Try setting `framework` explicitly.
2. Validate route prefix behavior: handlers declare routes without `routePrefix` (e.g. `/health`), but requests from other services use the full prefix (e.g. `/api/health`).
3. For frontend services on a subpath, confirm the framework's base path config matches `routePrefix`.
