---
name: vercel-agent
description: Vercel Agent guidance — AI-powered code review, incident investigation, and SDK installation. Automates PR analysis and anomaly debugging. Use when configuring or understanding Vercel's AI development tools.
metadata:
  priority: 4
  docs:
    - "https://vercel.com/docs"
    - "https://sdk.vercel.ai/docs"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns: 
    - '.github/workflows/vercel*.yml'
    - '.github/workflows/vercel*.yaml'
    - '.github/workflows/deploy*.yml'
    - '.github/workflows/deploy*.yaml'
    - '.github/workflows/preview*.yml'
    - '.github/workflows/preview*.yaml'
  bashPatterns: 
    - '\bvercel\s+agent\b'
retrieval:
  aliases:
    - ai code review
    - incident debugger
    - vercel ai tools
    - pr analyzer
  intents:
    - set up vercel agent
    - automate code review
    - investigate incident
    - configure ai tools
  entities:
    - Vercel Agent
    - code review
    - incident investigation
    - SDK
chainTo:
  -
    pattern: 'uses:\s*vercel/|vercel-action|VERCEL_TOKEN.*github'
    targetSkill: deployments-cicd
    message: 'GitHub Actions with Vercel detected — loading CI/CD guidance for deployment workflows, preview URLs, and production promotions.'
  -
    pattern: '@vercel/sdk|vercel\.deployments|vercel\.projects'
    targetSkill: vercel-api
    message: 'Vercel SDK usage detected — loading API guidance for programmatic deployment management, project configuration, and MCP server integration.'

---

# Vercel Agent

You are an expert in Vercel Agent — AI-powered development tools built into the Vercel platform.

## What It Is

Vercel Agent is a suite of **AI-powered development tools** that leverage deep context about your codebase, deployment history, and runtime behavior. It provides automated code review, incident investigation, and SDK installation assistance.

## Capabilities

### Code Review
- Automatic PR analysis triggered on push or via `@vercel` mention in PR comments
- Multi-step reasoning: identifies security vulnerabilities, logic errors, performance issues
- Generates and validates patches in **Vercel Sandbox** (secure execution)
- Supports inline suggestions and full patch proposals

### Investigation
- Analyzes anomaly alerts by querying logs and metrics
- Finds patterns and correlations across deployment data
- Provides root cause insights
- **Requires Observability Plus** subscription

### Installation
- Auto-installs Web Analytics and Speed Insights SDKs
- Analyzes repo structure, installs dependencies, writes integration code
- Creates PRs with the changes
- **Free** (no credit cost)

## Pricing

- $0.30 per Code Review or Investigation + token costs
- $100 promotional credit for Pro teams
- Installation is free

## Configuration

Vercel Agent is configured at `https://vercel.com/{team}/{project}/settings` → **AI** section. No npm package required — it is a platform-level service.

## When to Use

- Automated security and quality checks on every PR
- Root-cause analysis when anomaly alerts fire
- Quick SDK installation for analytics/monitoring

## References

- 📖 docs: https://vercel.com/docs/agent
