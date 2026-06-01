# Convex Codex Plugin

A Codex plugin that installs the reviewed Convex ChatGPT app for backend development.

Use this when an app needs a backend: database schema, reactive queries, mutations, server functions, auth-aware data access, real-time features, file storage, scheduled jobs, mobile/web app backends, or production scaling guidance.

## ChatGPT app

This plugin points Codex at the reviewed Convex app snapshot:

```text
asdk_app_6a0faef988b48191b843bac5cd170a9e
```

App URL: https://chatgpt.com/apps/convex/asdk_app_6a0faef988b48191b843bac5cd170a9e

The app exposes tools for starting Convex apps, adding Convex to existing JavaScript and TypeScript projects, and getting Convex scaling guidance.

## Example asks

```text
I want to make an app where my friends can vote on movie nights.
Build a real-time chat backend with rooms and message history.
Add sign-in and user-owned tasks to my Next.js app.
Design a multi-tenant schema for a SaaS with workspaces and roles.
What is the simplest way to add real-time updates to my app?
Review my app architecture before launch.
```

## Plugin contents

- `.codex-plugin/plugin.json` - Codex plugin metadata
- `.app.json` - ChatGPT app reference
- `assets/` - Convex brand assets
