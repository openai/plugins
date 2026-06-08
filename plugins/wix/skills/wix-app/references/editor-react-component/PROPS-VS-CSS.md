# Props vs CSS

Rules and patterns for handling visual/layout properties that vary by breakpoint.

---

## Should This Be a React Prop or CSS?

```
Is this a content/data property?
│
├─ YES → Can it be derived from other props / internal state?
│   │
│   ├─ YES (subtotal = price × qty, fullName = first + last, etc.)
│   │   └─ ❌ NOT a prop → compute internally
│   │
│   └─ NO (label, items, imageSrc, link, title, etc.)
│       └─ ✅ React prop
│
└─ NO → Would a user want this to vary per breakpoint?
    │
    ├─ YES (showLabel, orientation, displayMode, iconPosition)
    │   └─ ❌ NOT a prop → CSS only
    │
    └─ NO → Is it direction (RTL/LTR)?
        │
        ├─ YES
        │   └─ ✅ React prop (internationalization)
        │
        └─ NO → Is it behavior (disabled, required)?
            │
            ├─ YES
            │   └─ ✅ React prop
            │
            └─ NO
                └─ ❌ NOT a prop → CSS only
```

---

## Rules

Components must distinguish between content/data and visual/layout properties:

- **Content/Data** (same across all breakpoints) → React props ✅
- **Visual/Layout** (vary by breakpoint) → CSS only, NOT props ❌

### What CAN be props

- Content data that stays the same: `label`, `items`, `imageSrc`, `link`, `title`
- Behavior that's consistent: `disabled`, `required`, `searchable`, `multiple`

### What CANNOT be props (must be CSS)

- Visual display decisions: `showLabel`, `showIcon`, `displayMode`, `iconOnly`
- Layout decisions: `orientation`, `alignment`, `compact`
- Visibility toggles: `hideOnMobile`, `showOnDesktop`, `mobileView`

### Critical: ALL Show/Hide Toggles Are Visual/Layout Properties

Props like `showProgressBar`, `showVolumeControls`, `showTimeDisplay`, `showNavigation`, `showControls` are visual display decisions that CANNOT be props.

**Why:** Show/hide decisions affect layout and users need breakpoint control:

- Show progress bar on desktop, hide on mobile
- Show cover art on desktop, hide on tablet
- Show full controls on large screens, minimal on small screens

**Pattern:** These look like "feature toggles" but they're actually "layout modes".

**Exception:** `direction` (RTL/LTR) is a mandatory prop for internationalization, not a breakpoint-responsive property.

**Critical Rule:** If a property should be customizable per breakpoint, it CANNOT be a React prop.

### How to Implement

Visibility/display properties can be overridden per breakpoint by the user via the editor — but, just like background colors, the component still authors the resting defaults in CSS:

1. **Always render all elements** — No conditional rendering with props
2. **Do NOT hardcode visibility-toggling display in CSS** (e.g. `display: none` to hide an element by default) — visibility is user-controlled per breakpoint. Layout `display` (`flex`, `grid`, etc.) on layout containers is fine and expected. Resting visual properties (background, color, border-radius, padding, font) DO belong in CSS — see `CSS-GUIDELINES.md`.
3. **Visibility is user-controlled** — Users control what shows/hides per breakpoint via the editor

```tsx
// ✅ CORRECT: Always render
<div className={styles.progressBar}>...</div>
<div className={styles.volumeControls}>...</div>
<div className={styles.trackInfo}>...</div>

// SCSS: no `display: none` default — visibility is user-controlled per breakpoint
.progressBar {
  position: relative;
}
```

### How to Identify

Ask these questions in order:

1. **"Would a user want this to vary per breakpoint?"** (mobile vs desktop vs tablet)
   - If YES → CSS only, NOT a prop

2. **"Does this control WHAT is displayed vs WHICH content to display?"**
   - `showProgressBar` → Controls WHAT (layout decision) → CSS only
   - `audioUrl` → Specifies WHICH audio file (content) → Prop is OK

3. **"Does it change the visual appearance or layout?"**
   - `showControls`, `orientation`, `alignment` → Visual/layout → CSS only
   - `disabled`, `required`, `autoPlay` → Behavior (not visual) → Props are OK

**Rule of thumb:** If the prop name starts with `show*`, `hide*`, `display*` → It's CSS-only.

**Examples:**

- ✅ **Visual properties:** Show/hide elements, display modes → CSS only
- ✅ **Layout properties:** Orientation, alignment, spacing variations, flex/grid directions → CSS only
- ❌ **Content properties:** Text, media URLs, links, data → Props are OK
- ❌ **Internationalization:** RTL/LTR (`direction` prop) → Props are OK (not breakpoint-responsive)

---

## Patterns

### Correct: Only Data as Props

**❌ Wrong — visual properties as props:**

```typescript
interface ButtonProps {
  showLabel?: boolean; // ❌ Breakpoint-customizable
  showIcon?: boolean; // ❌ Breakpoint-customizable
  displayMode?: 'icon-only' | 'label-only' | 'both'; // ❌
  iconPosition?: 'left' | 'right'; // ❌ Layout
  orientation?: 'horizontal' | 'vertical'; // ❌ Layout
}
```

**✅ Correct — only data as props:**

```typescript
interface ButtonProps {
  label: string; // ✅ Content data
  icon: VectorArt; // ✅ Content data
}
```

### Correct: Always Render, Users Control Visibility

**❌ Wrong — show/hide as props:**

```typescript
interface AudioPlayerProps {
  showProgressBar?: boolean;      // ❌ Layout decision
  showVolumeControls?: boolean;   // ❌ Layout decision
  showTimeDisplay?: boolean;      // ❌ Layout decision
  showTrackInfo?: boolean;        // ❌ Layout decision
}

// Conditional rendering
{showProgressBar && <div className={styles.progressBar}>...</div>}
```

**✅ Correct — always render, users control visibility:**

```typescript
interface AudioPlayerProps {
  audioUrl: string;     // ✅ Content data only
  title?: string;       // ✅ Content data
  artist?: string;      // ✅ Content data
}

// Always render all elements
<div className={styles.progressBar}>...</div>
<div className={styles.volumeControls}>...</div>
<div className={styles.trackInfo}>...</div>

// SCSS: no `display: none` default — visibility is user-controlled per breakpoint
.progressBar {
  position: relative;
}
```

---

## Common Mistake: Adding Visual Toggle Props

**❌ Wrong:**

```typescript
export interface ButtonProps {
  showIcon?: boolean; // ❌ Breakpoint-customizable
  iconPosition?: 'left' | 'right'; // ❌ Layout
}
```

**✅ Correct:**

```typescript
export interface ButtonProps {
  label: string;
  icon: VectorArt;
  // Visual variations via CSS
}
```
