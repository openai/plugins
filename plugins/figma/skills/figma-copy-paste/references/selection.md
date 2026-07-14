# Vague Source Selection

Use this only when the user describes a screen or component instead of supplying its exact node, or when the supplied node is an oversized multi-screen canvas.

1. Turn the request into two or three visible cues: distinctive text, selected navigation state, and required region or control.
2. Keep the source read-only. Use Figma's Find through Chrome to locate the rarest visible text cue, then inspect its ancestors in the Layers panel. Do not copy the search result itself unless it is the requested complete object.
3. Promote to the smallest ancestor with a complete visual boundary and plausible screen or component dimensions. Reject page canvases, multi-screen strips, clipped fragments, and frames missing any required cue.
4. Capture isolated screenshots and metadata for at most three plausible candidates. Choose the only candidate that satisfies every cue; record why the others fail.
5. If two candidates remain materially plausible, ask the user. If none match, stop without copying.
