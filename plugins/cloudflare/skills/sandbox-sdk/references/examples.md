# Sandbox SDK Examples

All examples: https://github.com/cloudflare/sandbox-sdk/tree/main/examples

## Example Index

| Example | Use Case | Key File |
|---------|----------|----------|
| `minimal` | Basic setup, exec, file ops | `src/index.ts` |
| `code-interpreter` | AI code execution with Workers AI | `src/index.ts` |
| `openai-agents` | OpenAI Agents SDK integration | `src/index.ts` |
| `opencode` | OpenCode agent integration | `src/index.ts` |
| `claude-code` | Claude Code agent integration | `src/index.ts` |
| `typescript-validator` | TypeScript compilation/validation | `src/index.ts` |
| `authentication` | Auth patterns for sandboxes | `src/index.ts` |

## When to Use Which Example

| Building | Start With |
|----------|------------|
| AI code execution | `code-interpreter` |
| Agent with shell + file editing | `openai-agents` |
| Basic command execution | `minimal` |
| Code validation service | `typescript-validator` |
| Multi-user sandboxes | `authentication` |

## Common Patterns from Examples

**Sandbox per user/session** (from `openai-agents`):
```typescript
const sandbox = getSandbox(env.Sandbox, `session-${sessionId}`);
```

**Code context reuse** (from `code-interpreter`):
```typescript
const pythonCtx = await sandbox.createCodeContext({ language: 'python' });
const result = await sandbox.runCode(code, { context: pythonCtx });
```

**Resource cleanup** (from `code-interpreter`):
```typescript
try {
  // ... use sandbox
} finally {
  await sandbox.destroy();
}
```

Fetch the full example source when implementing similar patterns.
