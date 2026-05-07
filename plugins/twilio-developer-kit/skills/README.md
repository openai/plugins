# Twilio Skills

Procedural knowledge for AI coding agents building on Twilio. Each skill is a `SKILL.md` file following the open [Agent Skills](https://agentskills.io) standard — compatible with Claude Code, Cursor, Codex, GitHub Copilot, Gemini CLI, and 30+ other tools.

## Skill Types

| Type | Purpose | When your agent uses it |
|------|---------|------------------------|
| **Setup** | Account, auth, and number configuration | First-time Twilio setup, credential rotation, adding senders |
| **Planner** | Use-case qualification and product selection | "I need to build X" — before any code gets written |
| **Product** | How to use one Twilio product correctly | Implementation phase — API patterns, code examples, edge cases |
| **Guardrail** | Operational patterns preventing failures | Production readiness — rate limiting, security, compliance |

## Products Covered

SMS, MMS, WhatsApp, RCS, Voice, Verify, SendGrid, Conversations, TaskRouter, Messaging Services, Compliance (A2P 10DLC, Toll-Free, STIR/SHAKEN), and more.

## Format

Each skill is a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name
description: >
  What this skill does and when to use it.
---

## Overview
## Prerequisites
## Quickstart
## Key Patterns
## CANNOT
## Next Steps
```

## Install

See the [main README](../README.md#install-twilio-skills) for per-platform installation instructions.
