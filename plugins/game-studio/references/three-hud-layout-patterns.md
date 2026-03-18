# 3D HUD Layout Patterns

Use these defaults for initial 3D browser-game scaffolds. The first screen should be playable before it is informational.

## Layout Budget

- Keep the center of the screen clear during normal play.
- On desktop, prefer one primary persistent cluster and one small secondary cluster.
- On mobile, prefer one compact persistent cluster and transient prompts.
- Secondary information belongs in drawers, toggles, pause menus, or contextual popovers.

## Good Default Patterns

### Objective chip

- One short objective in a compact top-corner chip.
- One optional sublabel for location or mode.
- No giant hero banner over the live scene.

### Contextual interaction prompt

- Bottom-center or lower-corner pill.
- Appears only near interactables or during onboarding.
- Dismisses after first use or fades once the player is moving confidently.

### Small status strip

- Health, energy, party count, or beacon progress in a narrow edge-aligned strip.
- Use icons, short labels, and compact meters instead of stacked cards.

### Collapsible journal or quest log

- Closed by default.
- Opened by a hotkey, button, or pause state.
- Holds longer prose, lore, map notes, and multi-step objective details.

### Pause and settings modal

- Explicit modal state.
- Suspends pointer-lock, drag-look, or camera input while active.

## Anti-Patterns

- four to six glass cards permanently framing the viewport
- large lore or field-notes panels open during normal movement
- controls lists permanently pinned to the screen
- symmetric dashboard composition that competes with the scene
- oversized title panels staying visible after the first second of play

## Example UI Budget

- top-left: objective chip
- top-right: compact status strip
- bottom-center: transient interaction or controls hint
- pause menu or drawer: map, notes, inventory, settings

## Prompt Add-On

```text
Default to a low-chrome playable HUD. Keep the central playfield clear. Use one compact objective chip, one small status surface, and transient prompts. Put lore, field notes, full controls, and long checklists behind a drawer or pause menu. Avoid equal-weight boxed panels in every corner.
```
