# React Component Patterns

Code patterns and common mistakes for Editor React components.

# Part 1: Implementation Patterns

## 1.1 SSR-Safe Implementation

Avoid browser-only APIs at module scope or during render; use them inside `useEffect` with `typeof window !== 'undefined'`.

**❌ Wrong:**

```typescript
const userAgent = window.navigator.userAgent;
```

**✅ Correct:**

```typescript
useEffect(() => {
  if (typeof window !== "undefined") {
    const userAgent = window.navigator.userAgent;
  }
}, []);
```

## 1.2 Element Visibility (Platform-Managed)

See [`PROPS-VS-CSS.md`](PROPS-VS-CSS.md) — element visibility is platform-managed; always render all elements, no conditional rendering.

---

# Part 2: CSS/SCSS Rules

Authoritative SCSS rules: `REACT-GUIDELINES.md` Part 2. For RTL/logical CSS patterns, see [`DIRECTIONALITY.md`](DIRECTIONALITY.md).

## 2.1 What NOT to Include

```scss
// ❌ NEVER include:

// State CSS
&:hover { ... }              // ❌
&:focus { ... }              // ❌
&:disabled { ... }           // ❌
&[data-state='open'] { ... } // ❌

// Transitions/Animations
transition: all 0.3s;        // ❌
animation: fadeIn 0.5s;      // ❌
```

---

# Part 3: Common Mistakes

## 3.1 Adding interaction-state CSS to parts

The resting visual (background, color, border-radius, padding, font)
belongs in the component's CSS — see `CSS-GUIDELINES.md` §"Keep all
styling in CSS". What does NOT belong is **interaction-state CSS**
(`:hover`, `:focus`, `:focus-visible`, `:active`, `:disabled`,
`[data-state]`, `[aria-selected]`) — the platform owns those.
Selection / mode variants (`selected`, `active`, `open`) are
different — they go through a JS-toggled modifier class; see
`CSS-GUIDELINES.md` §"Express selection / mode variants".

**❌ Wrong — pseudo-class rules must be removed:**

```scss
.button {
  background-color: #ffffff;
  color: #0f172a;
  border-radius: 8px;
  padding-block: 8px;
  padding-inline: 16px;
}

.button:hover { /* ❌ Interaction state — platform owns this */
  background-color: #f0f0f0;
}

.button:disabled { /* ❌ Interaction state — platform owns this */
  opacity: 0.5;
}
```

**✅ Correct — keep the resting visual; drop the pseudo-class rules:**

```scss
.button {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  color: #0f172a;
  border-radius: 8px;
  padding-block: 8px;
  padding-inline: 16px;
  box-sizing: border-box;
}
```

## 3.2 Browser APIs at module scope

**❌ Wrong:**

```typescript
const isMobile = window.innerWidth < 768; // ❌ SSR breaks
```

**✅ Correct:**

```typescript
useEffect(() => {
  if (typeof window !== "undefined") {
    setIsMobile(window.innerWidth < 768);
  }
}, []);
```

## 3.3 Use semantic HTML for collection-style UI

For lists, breadcrumbs, tabs, menus, and similar collection-style UI, render the underlying semantic HTML directly (`<ol>`/`<ul>` + `<li>`, `<nav>`, `<button role="tab">`, etc.) and own the keyboard / ARIA wiring in your own React code.

```tsx
<ol className="breadcrumbs">
  <li>
    <a href="/">Home</a>
  </li>
  <li>
    <span aria-hidden="true">/</span>
    <a href="/products">Products</a>
  </li>
</ol>
```

Handle separators with CSS pseudo-elements or inside each item.
