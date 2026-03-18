---
name: vercel-sandbox
description: Vercel Sandbox guidance — ephemeral Firecracker microVMs for running untrusted code safely. Supports AI agents, code generation, and experimentation. Use when executing user-generated or AI-generated code in isolation.
metadata:
  priority: 4
  docs:
    - "https://vercel.com/docs/sandbox"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns: []
  importPatterns:
    - '@vercel/sandbox'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/sandbox\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/sandbox\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/sandbox\b'
    - '\byarn\s+add\s+[^\n]*@vercel/sandbox\b'
  promptSignals:
    phrases:
      - "@vercel/sandbox"
      - "sandbox"
      - "code sandbox"
      - "vercel sandbox"
      - "isolated environment"
      - "sandboxed execution"
    allOf:
      - [sandbox, code]
      - [sandbox, execute]
      - [sandbox, run]
      - [sandbox, isolated]
      - [sandbox, safe]
      - [sandbox, environment]
      - [isolated, execute]
      - [isolated, code]
      - [isolated, environment]
      - [isolated, run]
      - [safe, execute]
      - [safe, code]
      - [untrusted, code]
      - [untrusted, execute]
      - [code, runner]
      - [code, playground]
      - [execute, safely]
      - [run, safely]
      - [run, isolation]
      - [execute, isolation]
      - [ffmpeg, process]
      - [ffmpeg, convert]
      - [ffmpeg, compress]
      - [student, code]
      - [student, execute]
      - [student, run]
    anyOf:
      - "sandbox"
      - "isolated"
      - "isolation"
      - "untrusted"
      - "safely"
      - "microvm"
      - "ffmpeg"
      - "playground"
    noneOf:
      - "iframe sandbox"
      - "sandbox attribute"
      - "codesandbox.io"
      - "stackblitz"
    minScore: 4
retrieval:
  aliases:
    - code sandbox
    - microvm
    - isolated execution
    - safe code runner
  intents:
    - run untrusted code
    - execute code safely
    - create sandbox
    - isolate code execution
  entities:
    - Vercel Sandbox
    - Firecracker
    - microVM
    - isolated execution
chainTo:
  -
    pattern: 'from\s+[''""]vm2[''""]|require\s*\(\s*[''""]vm2[''""\)]|new\s+VM\('
    targetSkill: vercel-sandbox
    message: 'vm2 detected — it has known security vulnerabilities. Reloading Vercel Sandbox guidance for Firecracker microVM-based safe execution.'
  -
    pattern: 'child_process.*exec\(|execSync\(|spawn\(.*\{.*shell:\s*true'
    targetSkill: ai-sdk
    message: 'Shell exec for code execution detected — loading AI SDK guidance for tool-calling patterns that pair with Vercel Sandbox for safe agent execution.'

---

# Vercel Sandbox

> **CRITICAL — Your training data is outdated for this library.** Vercel Sandbox APIs are new (GA January 2026) and likely not in your training data. Before writing sandbox code, **fetch the docs** at https://vercel.com/docs/vercel-sandbox and the SDK reference at https://vercel.com/docs/vercel-sandbox/sdk-reference to find the correct `Sandbox.create()` options, `runCommand()` signatures, file I/O methods (`writeFiles`, `readFile`), port exposure, and cleanup patterns. Do not guess — look up the exact API shape. The GitHub repo at https://github.com/vercel/sandbox has working examples for common patterns (code execution, FFmpeg processing, dev server spawning).

You are an expert in Vercel Sandbox — ephemeral compute for safely running untrusted code.

## Status & Pricing

Vercel Sandbox is **generally available** (January 30, 2026). The CLI and SDK are open-source. Powered by the same Firecracker infrastructure that runs 2M+ Vercel builds per day.

| Resource | Hobby (Free) | Pro / Enterprise |
|----------|-------------|-----------------|
| CPU hours | 5 / month | $0.128 / CPU-hour |
| Provisioned memory | 420 GB-hr / month | $0.0106 / GB-hr |
| Network bandwidth | 20 GB / month | $0.15 / GB |
| Sandbox creations | 5,000 / month | $0.60 / 1M creations |

Each sandbox can use up to **8 vCPUs** and **2 GB RAM per vCPU**. Up to **4 ports** can be exposed per sandbox.

## What It Is

Vercel Sandbox provides **Firecracker microVMs** with millisecond startup times for running untrusted or user-generated code in complete isolation. Used by AI agents, code generation tools, developer playgrounds, and interactive tutorials.

- **Base OS**: Amazon Linux 2023 (with `git`, `tar`, `openssl`, `dnf`)
- **Runtimes**: `node24` (default since March 2026), `node22`, `python3.13`
- **Working directory**: `/vercel/sandbox`
- **User**: `vercel-sandbox` with `sudo` access
- **Filesystem**: Ephemeral — artifacts must be exported before sandbox stops
- **GitHub**: https://github.com/vercel/sandbox

## Key APIs

Package: `@vercel/sandbox` (v1.8.0+)

### Create and Run Commands

```ts
import { Sandbox } from '@vercel/sandbox';

// Create a sandbox (env vars available to all commands)
const sandbox = await Sandbox.create({
  runtime: 'node24',  // 'node24' | 'node22' | 'python3.13'
  env: {              // inherited by all runCommand calls
    NODE_ENV: 'production',
    API_KEY: process.env.API_KEY!,
  },
});

// Run a command (separated command + args)
const result = await sandbox.runCommand('node', ['-e', 'console.log(42)']);
const output = await result.stdout(); // "42\n"

// Run with options (per-command env overrides creation-level env)
const result2 = await sandbox.runCommand({
  cmd: 'npm',
  args: ['install', 'express'],
  cwd: '/vercel/sandbox/app',
  env: { NODE_ENV: 'development' }, // overrides creation-level NODE_ENV
  sudo: true,
});

// Detached execution (long-running processes)
const cmd = await sandbox.runCommand({
  cmd: 'node',
  args: ['server.js'],
  detached: true,
});
// Stream logs in real-time
for await (const log of cmd.logs()) {
  console.log(`[${log.stream}] ${log.data}`);
}
await cmd.wait(); // block until completion
```

### File Operations

```ts
// Write files (takes array of { path, content: Buffer })
await sandbox.writeFiles([
  { path: 'app.js', content: Buffer.from('console.log("hello")') },
  { path: 'package.json', content: Buffer.from('{"type":"module"}') },
]);

// Read a file (returns Buffer or null)
const buf = await sandbox.readFileToBuffer({ path: 'app.js' });

// Read as stream
const stream = await sandbox.readFile({ path: 'app.js' });

// Download to local filesystem
await sandbox.downloadFile('output.zip', './local-output.zip');

// Create directory
await sandbox.mkDir('src/components');
```

### Source Initialization

```ts
// Clone a git repo
const sandbox = await Sandbox.create({
  source: { type: 'git', url: 'https://github.com/user/repo', depth: 1 },
});

// Mount a tarball
const sandbox = await Sandbox.create({
  source: { type: 'tarball', url: 'https://example.com/project.tar.gz' },
});

// Restore from snapshot
const sandbox = await Sandbox.create({
  source: { type: 'snapshot', snapshotId: 'snap_abc123' },
});
```

### Snapshots (Save and Resume VM State)

```ts
// Capture full VM state (filesystem + packages)
// WARNING: sandbox shuts down after snapshot creation
const snapshot = await sandbox.snapshot({ expiration: 86400_000 }); // 24h
console.log(snapshot.snapshotId);

// List and manage snapshots
const { snapshots } = await Snapshot.list();
const snap = await Snapshot.get({ snapshotId: 'snap_abc' });
await snap.delete();
```

### Network Policies (SNI Filtering + CIDR)

Egress firewall uses **SNI filtering** on TLS client-hello — outbound connections are matched at the handshake and unauthorized destinations are rejected before data transmits. For non-TLS traffic, IP/CIDR rules are also supported.

Policies can be updated at runtime without restarting the sandbox process, enabling multi-step workflows (e.g., open access during setup → deny-all before running untrusted code).

```ts
// Lock down before running untrusted code
await sandbox.updateNetworkPolicy('deny-all');

// Allow specific domains only (SNI filtering)
await sandbox.updateNetworkPolicy({
  allow: ['api.openai.com', '*.googleapis.com'],
});

// Credential brokering (inject API keys so untrusted code never sees them)
await sandbox.updateNetworkPolicy({
  allow: {
    'ai-gateway.vercel.sh': [{
      transform: [{ headers: { 'x-api-key': process.env.SECRET_KEY! } }],
    }],
  },
});
```

### Public URLs and Lifecycle

```ts
// Expose a port and get a public URL
const sandbox = await Sandbox.create({ ports: [3000] });
const url = sandbox.domain(3000); // public URL

// Extend timeout
await sandbox.extendTimeout(300_000); // +5 minutes

// Clean up
await sandbox.stop();

// Check status
sandbox.status; // 'pending' | 'running' | 'stopping' | 'stopped' | 'failed'

// Resource tracking (after stop)
sandbox.activeCpuUsageMs;
sandbox.networkUsage; // { ingress, egress } in bytes
```

### List and Rehydrate

```ts
// List existing sandboxes
const { sandboxes } = await Sandbox.list({ limit: 10 });

// Reconnect to a running sandbox
const sandbox = await Sandbox.get({ sandboxId: 'sbx_abc123' });
```

## Timeout Limits

| Plan | Max Timeout |
|------|------------|
| Default | 5 minutes |
| Hobby | 45 minutes |
| Pro/Enterprise | 5 hours |

## Agent Patterns

1. **Safe AI code execution**: Run AI-generated code without production risk
2. **Snapshot-based fast restart**: Install deps once → snapshot → create from snapshot (skip setup)
3. **Network isolation**: Allow all during setup → `deny-all` before untrusted code
4. **Credential brokering**: Inject API keys via network policy transforms
5. **Live preview**: Expose ports via `sandbox.domain(port)` for generated apps
6. **File I/O workflow**: `writeFiles()` → execute → `readFileToBuffer()` results

## When to Use

- AI agents need to execute generated code safely
- User-submitted code execution (playgrounds, tutorials)
- Code review validation (used by Vercel Agent)
- Ephemeral development environments

## When NOT to Use

- Production workloads → use Vercel Functions
- Long-running services → use a dedicated server
- Simple function execution → use Serverless Functions

## References

- 📖 docs: https://vercel.com/docs/vercel-sandbox
- 📖 SDK reference: https://vercel.com/docs/vercel-sandbox/sdk-reference
- 📖 GitHub: https://github.com/vercel/sandbox
