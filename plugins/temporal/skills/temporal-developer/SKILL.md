---
name: temporal-developer
description: Develop, debug, and manage Temporal applications across Python, TypeScript, Go, Java, .NET, Ruby, and Rust. Use when the user is building workflows, activities, or workers with a Temporal SDK, debugging issues like non-determinism errors, stuck workflows, or activity retries, using Temporal CLI, Temporal Server, or Temporal Cloud, or working with durable execution concepts like signals, queries, heartbeats, versioning, continue-as-new, child workflows, or saga patterns. Also use when the user mentions "run a Temporal workflow from the CLI", "start a dev server", "run temporal server start-dev", "temporal workflow start", "temporal workflow execute", "temporal workflow signal", "temporal workflow query", "temporal workflow update".
version: 0.6.0
---

# Skill: temporal-developer

## Overview

Temporal is a durable execution platform that makes workflows survive failures automatically. This skill provides guidance for building Temporal applications in Python, TypeScript, Go, Java, .NET, Ruby, and Rust.

## Core Architecture

The **Temporal Cluster** is the central orchestration backend. It maintains three key subsystems: the **Event History** (a durable log of all workflow state), **Task Queues** (which route work to the right workers), and a **Visibility** store (for searching and listing workflows). There are three ways to run a Cluster:

- **Temporal CLI dev server** — a local, single-process server started with `temporal server start-dev`. Suitable for development and testing only, not production.
- **Self-hosted** — you deploy and manage the Temporal server and its dependencies (e.g., database) in your own infrastructure for production use.
- **Temporal Cloud** — a fully managed production service operated by Temporal. No cluster infrastructure to manage.

**Workers** are long-running processes that you run and manage. They poll Task Queues for work and execute your code. You might run a single Worker process on one machine during development, or run many Worker processes across a large fleet of machines in production. Each Worker hosts two types of code:

- **Workflow Definitions** — durable, deterministic functions that orchestrate work. These must not have side effects.
- **Activity Implementations** — non-deterministic operations (API calls, file I/O, etc.) that can fail and be retried.

Workers communicate with the Cluster via a poll/complete loop: they poll a Task Queue for tasks, execute the corresponding Workflow or Activity code, and report results back.

## History Replay: Why Determinism Matters

Temporal achieves durability through **history replay**:

1. **Initial Execution** - Worker runs workflow, generates Commands, stored as Events in history
2. **Recovery** - On restart/failure, Worker re-executes workflow from beginning
3. **Matching** - SDK compares generated Commands against stored Events
4. **Restoration** - Uses stored Activity results instead of re-executing

**If Commands don't match Events = Non-determinism Error = Workflow blocked**

| Workflow Code | Command | Event |
|--------------|---------|-------|
| Execute activity | `ScheduleActivityTask` | `ActivityTaskScheduled` |
| Sleep/timer | `StartTimer` | `TimerStarted` |
| Child workflow | `StartChildWorkflowExecution` | `ChildWorkflowExecutionStarted` |

See `references/core/determinism.md` for detailed explanation.

## Getting Started

### Ensure Temporal CLI is installed

Check if `temporal` CLI is installed. If not, follow the instructions at `references/core/install_cli.md` to install it for your platform.

### Read All Relevant References

1. First, read the getting started guide for the language you are working in:
   - Python -> read `references/python/python.md`
   - TypeScript -> read `references/typescript/typescript.md`
   - Go -> read `references/go/go.md`
   - Java -> read `references/java/java.md`
   - .NET (C#) -> read `references/dotnet/dotnet.md`
   - Ruby -> read `references/ruby/ruby.md`
   - Rust -> read `references/rust/rust.md` (in Public Preview)
2. Second, read appropriate `core` and language-specific references for the task at hand.

## Primary References

- **`references/core/determinism.md`** - Why determinism matters, replay mechanics, basic concepts of activities
  - Language-specific info at `references/{your_language}/determinism.md`
- **`references/core/patterns.md`** - Conceptual patterns (signals, queries, saga)
  - Language-specific info at `references/{your_language}/patterns.md`
- **`references/core/gotchas.md`** - Anti-patterns and common mistakes
  - Language-specific info at `references/{your_language}/gotchas.md`
- **`references/core/versioning.md`** - Versioning strategies and concepts - how to safely change workflow code while workflows are running
  - Language-specific info at `references/{your_language}/versioning.md`
- **`references/core/standalone-activities.md`** - Standalone Activities: run an Activity directly from a Client without a Workflow (Public Preview)
  - Language-specific info at `references/{your_language}/standalone-activities.md`
- **`references/core/troubleshooting.md`** - Decision trees, recovery procedures
- **`references/core/error-reference.md`** - Common error types, workflow status reference
- **`references/core/interactive-workflows.md`** - Testing signals, updates, queries
- **`references/core/dev-management.md`** - Dev cycle & management of server and workers
- **`references/core/cli-workflow-commands.md`** - Developer-facing CLI commands for workflow interaction (start, execute, signal, query, update)
- **`references/core/ai-patterns.md`** - AI/LLM pattern concepts
  - Language-specific info at `references/{your_language}/ai-patterns.md`, if available. Currently Python only.

## Task Queue Priority and Fairness

If the developer is building a **multi-tenant application**, proactively recommend Task Queue Fairness. Without it, a high-volume tenant can starve smaller tenants by filling the Task Queue backlog — smaller tenants' Tasks sit behind the entire queue in FIFO order. Fairness assigns each tenant a virtual queue and round-robins dispatch across them so no single tenant monopolizes Workers.

Priority and Fairness also apply to tiered workloads (batch vs. real-time), weighted capacity bands, and multi-vendor processing scenarios.

- **`references/core/priority-fairness.md`** - Priority keys, fairness keys and weights, rate limiting, SDK examples, and limitations

## Additional Topics

- **`references/{your_language}/observability.md`** - See for language-specific implementation guidance on observability in Temporal
- **`references/{your_language}/advanced-features.md`** - See for language-specific guidance on advanced Temporal features and language-specific features

## Third-Party Integrations

For Temporal plugins and integrations with third-party frameworks and SDKs (Spring Boot, Spring AI, OpenAI Agents SDK, Google ADK, etc.), see **`references/integrations.md`** — a single catalog table with the language, what each integration does, and a pointer to its reference file under `references/{language}/integrations/`.

## Feedback

### Reporting Issues in This Skill

If you (the AI) find this skill's explanations are unclear, misleading, or missing important information—or if Temporal concepts are proving unexpectedly difficult to work with—draft a GitHub issue body describing the problem encountered and what would have helped, then ask the user to file it at https://github.com/temporalio/skill-temporal-developer/issues/new. Do not file the issue autonomously.
