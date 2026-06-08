# Component Directionality (RTL/LTR)

Rules and patterns for direction support in Editor React components.

---

## Rules

Direction support is mandatory for every component. The pattern uses native HTML `dir` attributes for standards-compliant, accessible directionality support, with mandatory fallback classes on root components.

### Direction Resolution

```typescript
const subComponentDirection = elementProps?.subComponent?.direction;
```

- Sub-component directions only applied when explicitly set (to override inherited direction)
- When undefined: inherits direction from parent via CSS inheritance
- Root component always gets fallback class

### Direction Anti-Patterns

```scss
/* ❌ Don't use CSS variables for direction */
.component { direction: var(--component-direction, ltr); }
```

```tsx
/* ❌ Don't use conditional logic for fallback class */
className={classNames({
  [styles.fallbackDirection]: !direction
})}
```

### RTL in SCSS

Use logical CSS properties — never physical `left`/`right`-only layouts. See §2.1 below.

---

## Patterns

### Root Element Pattern

Apply on main component only:

```typescript
<div
  dir={direction}
  className={classNames(
    styles.root,
    className,
    styles.fallbackDirection,
  )}
>
```

```scss
.fallbackDirection:not([dir]) {
  direction: var(--wix-opt-in-direction);
}
```

**Imports:**

```typescript
import type { Direction } from '@wix/editor-react-types';
```

### Child Element Direction

Only when explicitly specified:

```typescript
const labelDirection = elementProps?.label?.direction;

<span
  dir={labelDirection}
>
```

### Runtime Direction Checking

**Environment Service (for site direction):**

Use service when direction drives JavaScript behavior (keyboard navigation, animation logic, conditional rendering).

```typescript
import { useService } from '@wix/services-manager-react';
import { EnvironmentDefinition } from '@wix/environment-service/definition';

const environmentService = useService(EnvironmentDefinition);
const siteDirection = environmentService.getLanguageDirection();
const isRTL = siteDirection === 'rtl';
```

**Fallback chain (for child components):**

```typescript
const isRTL = (direction || parentDirection || siteDirection) === 'rtl';
```

**CSS Variable**

Use css variable `--wix-opt-in-direction-multiplier` when direction only affects visual appearance (transforms, spacing, layout):

```scss
.scrollButton {
  scale: var(--wix-opt-in-direction-multiplier, 1) 1;
}
```

### RTL Support — Use Logical CSS Properties

**✅ Correct:**

```scss
.element {
  inset-inline-start: 0; // Instead of left
  inset-inline-end: 0; // Instead of right
  padding-inline-start: 8px; // Instead of padding-left
  margin-inline-end: 4px; // Instead of margin-right
}
```

**❌ Wrong:**

```scss
.element {
  padding-left: 8px;
  [dir='rtl'] & {
    padding-right: 8px; // Manual RTL - avoid
  }
}
```

Use logical CSS properties (e.g., `margin-inline-start` not `margin-left`) for RTL support.

---

## Common Mistake: Manual RTL Handling

**❌ Wrong:**

```scss
.element {
  padding-left: 8px;
  [dir='rtl'] & {
    padding-right: 8px; // Manual overrides
  }
}
```

**✅ Correct:**

```scss
.element {
  padding-inline-start: 8px; // Auto RTL/LTR
}
```

## Container Components and RTL Inheritance

Elements that render `React.ReactNode` content MUST have `dir="ltr"` to prevent RTL inheritance from the parent component:

```tsx
<Accordion.Content dir="ltr">
  {item.content} {/* React.ReactNode */}
</Accordion.Content>
```
