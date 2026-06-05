# Accessibility (ARIA)

Rules and patterns for ARIA accessibility support in Editor React components.

---

## Rules

### All ARIA Attributes Through the `a11y` Prop

- **NEVER** add individual ARIA properties like `ariaLabel?: string`, `ariaDescribedBy?: string`, `role?: string`, etc. to a component's props interface.
- **ALL** accessibility attributes MUST come through the `a11y?: A11y` prop.
- The `A11y` type includes: `ariaLabel`, `ariaDescribedBy`, `ariaLabelledBy`, `role`, `ariaHidden`, `ariaLive`, and all other ARIA attributes.
- Users provide ARIA values through the `a11y` prop: `<Component a11y={{ ariaLabel: "..." }} />`

### ARIA Label Rules

ARIA labels are user-facing content and must NEVER be hardcoded as string literals in JSX.

**Three patterns (in order of preference):**

1. **No aria-label (preferred)** — Visible text content is sufficient:

   ```tsx
   <Button>Play</Button> // Visible text ✅
   ```

2. **User-configurable** — Via a11y prop (for root or element-specific labels, per requirements):

   ```tsx
   // User provides: <ComponentName a11y={{ ariaLabel: "Background music" }} />
   // Component applies to root (using the a11y-to-HTML conversion utility):
   {...(a11y && convertA11yKeysToHtmlFormat(a11y))}

   // Or for inner elements (if requirements specify):
   // elementProps.button.a11y gets passed to the button element
   ```

3. **System-required** — Via constants.ts (when requirements specify non-configurable label):

   ```tsx
   // constants.ts
   export const ARIA_LABELS = {
     playButton: 'Play audio',
     muteButton: 'Mute audio',
   } as const;

   // component.tsx
   import { ARIA_LABELS } from './constants';
   <Button aria-label={ARIA_LABELS.playButton}>▶</Button>;
   ```

**❌ NEVER hardcode string literals:**

```tsx
// ❌ WRONG - hardcoded strings
<Button aria-label="Play">▶</Button>
<Button aria-label={isPlaying ? "Pause" : "Play"}>▶</Button>
<Slider aria-label="Volume" />
```

**Why this matters:**

- Hardcoded strings cannot be translated or customized
- User-provided labels take precedence when available
- Constants allow centralized management and potential future translation

### Detecting Icon-Only Interactive Elements

**Icon-only elements require aria-labels.** Detect with this checklist:

| Element Content       | Needs aria-label? | Example                                   |
| --------------------- | ----------------- | ----------------------------------------- |
| Visible text only     | ❌ No             | `<Button>Play</Button>`                   |
| Icon component + text | ❌ No             | `<Button><PlayIcon />Play</Button>`       |
| Icon/emoji only       | ✅ YES            | `<Button>▶</Button>`                     |
| Image only            | ✅ YES            | `<Button><img src="play.png" /></Button>` |
| SVG only              | ✅ YES            | `<Button><svg>...</svg></Button>`         |

**Critical:** If button/link contains ONLY visual elements (icons, emojis, images, SVG) with NO text node, it MUST have aria-label from constants.

**Pattern for dynamic labels:**

```tsx
// constants.ts
export const ARIA_LABELS = {
  playButton: 'Play audio',
  pauseButton: 'Pause audio',
} as const;

// component.tsx
<Button
  aria-label={isPlaying ? ARIA_LABELS.pauseButton : ARIA_LABELS.playButton}
>
  {isPlaying ? '⏸' : '▶'}
</Button>;
```

---

## Common Mistake: Individual ARIA Properties Instead of A11y Type

**❌ Wrong:**

```typescript
import type { Direction } from '@wix/editor-react-types';

export interface TabsProps {
  id?: string;
  className?: string;
  direction?: Direction;
  ariaLabel?: string; // ❌ Individual ARIA prop
  ariaDescribedBy?: string; // ❌ Individual ARIA prop
  role?: string; // ❌ Individual ARIA prop
}
```

**✅ Correct:**

```typescript
import type { A11y, Direction } from '@wix/editor-react-types';
import { convertA11yKeysToHtmlFormat } from '@wix/react-component-utils';

export interface TabsProps {
  id?: string;
  className?: string;
  direction?: Direction;
  a11y?: A11y;  // ✅ All ARIA attributes through this prop
}

// Usage:
<Tabs a11y={{ ariaLabel: "Navigation", role: "navigation" }} />

// In component:
{...(a11y && convertA11yKeysToHtmlFormat(a11y))}
```

**Why:** The `A11y` type from `@wix/editor-react-types` provides a standardized way to handle ALL ARIA attributes (ariaLabel, ariaDescribedBy, ariaLabelledBy, role, ariaHidden, ariaLive, etc.). Individual ARIA props fragment the API and make it harder to use.
