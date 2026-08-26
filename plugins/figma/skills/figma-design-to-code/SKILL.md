---
name: figma-design-to-code
description: "Use this skill when implementing a Figma design as code (design → code) — the read-FROM-Figma direction. Triggers: 'implement this Figma design', 'build this screen from Figma', 'turn this Figma into code', 'code this up from Figma', 'design to code', or a figma.com design URL provided alongside a codebase. Encodes the workflow for reading a node out of Figma with get_design_context and adapting its reference output to the target project — reusing existing components, tokens, and conventions, and honoring Code Connect mappings, component docs, design annotations, and design tokens by priority. Complements figma-code-connect (component mapping) and figma-generate-design / figma-use (the reverse, code → design direction)."
disable-model-invocation: false
---

# Implement a Figma Design as Code (Design → Code)

Use this skill to turn a Figma design into code in a target codebase. This is the **read-FROM-Figma** direction: pull design context out of Figma with `get_design_context`, then adapt it into the project's real stack. For the reverse direction — building or updating a design *in* Figma from code — use [figma-generate-design](../figma-generate-design/SKILL.md) instead.

This skill owns the **workflow** for design-to-code. Parameter mechanics (nodeId / fileKey / branchKey extraction, URL parsing, `format`/`query` options, response shape) live on the `get_design_context` tool description itself — follow them there.

## Direction and Scope

- You MUST use this skill for design → code: implementing, translating, or porting a Figma node into code.
- You MUST NOT use this skill to write to Figma.

## Workflow

### 1. Call get_design_context first

- You MUST call `get_design_context` on the target node before writing any code. It is your primary tool — a single call returns reference code, a screenshot, and contextual hints.
- You MUST NOT reach for `get_metadata` or `get_screenshot` as a substitute. Use them only to orient (e.g. picking a node) or to validate, not in place of `get_design_context`.

### 2. Treat the output as a reference, not final code

- The returned code is React + Tailwind enriched with hints. You MUST treat it as a REFERENCE, not as final code to paste verbatim.
- You MUST adapt it to the target project's language, framework, component library, styling system, and conventions. Match the surrounding code.

### 3. Reuse what the project already has

- Before writing new code, You MUST check the target project for existing components, layout patterns, and design tokens that match the design intent.
- You MUST reuse the project's existing components and tokens instead of generating new equivalents from scratch.

### 4. Honor the response hints by priority

Apply the hints in this order — earlier sources override later ones:

1. **Code Connect snippets** → use the mapped codebase component directly.
2. **Component documentation links** → follow them for usage and guidelines.
3. **Design annotations** → follow any designer notes or constraints.
4. **Design tokens (CSS variables)** → map them to the project's token system.
5. **Raw hex / absolute positioning** → loosely structured; lean on the screenshot for intent.

## Error Recovery

- On a `get_design_context` error, STOP and read the message before retrying.
- If the design URL has no `node-id` (a file-only URL), ask the user for a node-specific URL — You MUST NOT guess or pass an empty `nodeId`.
- On a timeout, retry against a smaller node or selection.
- You MUST NOT silently fall back to hand-writing the screen from the screenshot alone when `get_design_context` can still provide context.
