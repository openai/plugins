# base44 site deploy

Deploy built site files to Base44 hosting.

## Table of Contents

- [Syntax](#syntax)
- [Authentication](#authentication)
- [Prerequisites](#prerequisites)
- [How It Works](#how-it-works)
- [Interactive Flow](#interactive-flow)
- [Typical Workflow](#typical-workflow)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Use Cases](#use-cases)
- [Notes](#notes)

## Syntax

```bash
npx base44 site deploy [options]
```

## Options

| Option       | Description               |
| ------------ | ------------------------- |
| `-y, --yes`  | Skip confirmation prompt  |

Use `-y` flag for non-interactive/automated deployments:

```bash
npx base44 site deploy -y
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## Prerequisites

- Must be run from a Base44 project directory
- Project must have `site.outputDirectory` configured in project config
- Site must be built before deploying (run your build command first)
- **SPA only**: Base44 hosting supports Single Page Applications with a single `index.html` entry point. All routes are served from `index.html` (client-side routing).

## How It Works

1. Reads project configuration
2. Validates that site configuration exists
3. Prompts for deployment confirmation showing the output directory
4. Creates an archive of site files from the output directory
5. Deploys to Base44 hosting
6. Returns the app URL

## Interactive Flow

```bash
$ npx base44 site deploy

Deploy site from ./dist? (yes/no) yes

Creating archive...
Uploading to Base44...
Deploying...

✓ Deployment successful!

Visit your site at: https://my-app.base44.app
```

## Typical Workflow

```bash
# 1. Build your site using your framework's build command
npm run build

# 2. Deploy to Base44
npx base44 site deploy
```

## Configuration

The `site.outputDirectory` in your project configuration should point to where your framework outputs built files:

- Vite: typically `./dist`
- Next.js: typically `./.next` or `./out`
- Create React App: typically `./build`
- Custom: whatever your build tool outputs to

## Error Handling

If site configuration is missing:
```bash
$ npx base44 site deploy
Error: No site configuration found in project
```

If you cancel the deployment:
```bash
Deploy site from ./dist? (yes/no) no
Deployment cancelled
```

## Use Cases

- Deploy your site after making changes
- Push new versions of your application
- Deploy after updating content or functionality
- Part of your CI/CD pipeline

## Notes

- Always build your site before deploying
- The command deploys whatever is in your output directory
- Make sure your build completed successfully before deploying
- Previous deployments are preserved (versioned) in Base44
- Deployment is immediate and updates your live site
