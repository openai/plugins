---
name: figma-copy-paste
description: Copy exact, editable Figma screens, frames, components, or layers from one file to another with Figma's native clipboard, then verify the pasted result. Use when the user asks to copy, paste, transfer, or duplicate existing Figma content between files without recreating or flattening it.
---

# Figma Copy Paste

Use Figma's native clipboard. Use Figma MCP to identify and verify content; never reconstruct an exact-copy request.

Computer Use is required to send the native OS-level Copy and Paste events that make exact cross-file Figma transfer reliable on macOS and Windows.

## Workflow

1. Identify the smallest complete source node that satisfies the request. For a vague request or oversized source canvas, follow [references/selection.md](references/selection.md). Prefer a full screen over an inner layer or surrounding multi-screen canvas. When the user supplies an exact node ID and metadata confirms it is already the requested complete node, do not substitute an ancestor. Record its file key, node ID, name, type, dimensions, metadata counts, variables, and screenshot. Name similar frames excluded from the copy.
2. Keep the source read-only. Never cut, detach, flatten, move, or republish it. For view-only sources, use MCP read tools rather than `use_figma`.
3. Inspect the destination page and record its existing top-level nodes and local assets.
4. Follow [references/clipboard.md](references/clipboard.md) to select the exact node, validate the native Figma clipboard payload, paste, and handle the watchdog and variable prompt.
5. Do not copy every main component set preemptively. Preserve linked instances; localize only components the user later chooses to edit independently.
6. Follow [references/verification.md](references/verification.md) to compare structure, bindings, and isolated renders.
7. Report the source and destination node IDs, clipboard path, variable behavior, fidelity classification, discrepancies, and optional follow-up work.

Ask only when two materially different complete source nodes remain equally plausible. Never substitute an image, generated nodes, or a flattened export for a failed native transfer.
