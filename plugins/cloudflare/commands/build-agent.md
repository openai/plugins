---
description: Build an AI agent on Cloudflare using the Agents SDK
argument-hint: [agent-description]
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, WebFetch]
---

# Build AI Agent on Cloudflare

This command helps you build AI agents using the Cloudflare Agents SDK with state management, real-time WebSockets, scheduled tasks, and tool integration.

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

When this command is invoked:

1. Read the skill file at `building-ai-agent-on-cloudflare/SKILL.md` for core guidance
2. Reference `building-ai-agent-on-cloudflare/references/examples.md` for templates
3. Use `building-ai-agent-on-cloudflare/references/agent-patterns.md` for tool calling and patterns
4. Use `building-ai-agent-on-cloudflare/references/state-patterns.md` for state management
5. Consult `building-ai-agent-on-cloudflare/references/troubleshooting.md` for common issues

## Capabilities

- Stateful AI agents with persistent memory
- Real-time WebSocket communication
- Scheduled tasks and cron jobs
- Tool integration and function calling
- Multi-agent orchestration
- RAG (Retrieval Augmented Generation) patterns

## Example Usage

```
/build-agent a customer support chatbot
/build-agent real-time coding assistant with WebSocket
/build-agent multi-agent workflow orchestrator
```
