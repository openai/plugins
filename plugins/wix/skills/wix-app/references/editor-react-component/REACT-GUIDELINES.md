# React Component Implementation Guide

This guide defines rules and guidance on **how to implement** production-quality Editor React components for Wix CLI applications. Editor React components are React components that integrate with the Wix Editor, allowing site owners to customize content, styling, and behavior through a visual interface.

**Topic reference files:**
- [`PARTS.md`](PARTS.md) — What qualifies as a named part (mandatory filter)
- [`ACCESSIBILITY.md`](ACCESSIBILITY.md) — ARIA/a11y rules and patterns
- [`DIRECTIONALITY.md`](DIRECTIONALITY.md) — RTL/LTR rules and patterns
- [`PROPS-VS-CSS.md`](PROPS-VS-CSS.md) — What should be a React prop vs CSS
- [`COMPONENT-API.md`](COMPONENT-API.md) — Props structure, elementProps, data types, file splitting, containers, array props
- [`REACT-PATTERNS.md`](REACT-PATTERNS.md) — SSR-safe patterns, CSS rules, common mistakes

## React 18 features are not supported

The Wix runtime does not currently support React 18 features. Stick
to React 17-compatible APIs and avoid libraries that depend on
React 18 features.

# Part 0: Component Behavior Guide

Understand the component and infer its behavior. Extract what is provided; use reasonable defaults for anything not specified.

1. **Identity** — Component name.
2. **Structure** — Identify named parts by applying the mandatory filter in [`PARTS.md`](PARTS.md) to every candidate element before accepting it as a part. Include content/data props (labels, items, types, required vs optional) and configuration (toggles, choices, ranges, modes).
3. **Interactions** — Clicks, hover/focus; what is exposed as event props vs handled internally.

**Understanding → implementation (checklist):** For every part, decide `elementProps` vs CSS-only; build the props interface (data + behavior); wire interaction in React (`useState`, `useEffect`, refs, native event handlers); generate TS + CSS. Infer reasonable defaults where anything is unspecified.

# Part 1: Standards & Conventions

These are the mandatory patterns and conventions for all components.

## 1.1 Mandatory Features

Every component MUST include:

### Direction Support (RTL/LTR)

Direction support is mandatory — see [`DIRECTIONALITY.md`](DIRECTIONALITY.md).

### Accessibility ARIA Support

See [`ACCESSIBILITY.md`](ACCESSIBILITY.md) for full rules and patterns.

### TypeScript

- All components must be fully typed
- NO `any` types
- Export all prop interfaces
- Use proper React types (`React.FC`, `React.ReactNode`, etc.)
- **Array type syntax:** Use `Array<T>` instead of `T[]` (e.g., `Array<Item>` not `Item[]`)
- **Array element types:** `T` must be an object with named keys — `Array<{ key: ValueType, ... }>` or a named interface that is itself a keyed object. Never `Array<string>`, `Array<number>`, `Array<boolean>`, or `Array<DataType>` (`Image`, `Link`, `Video`, `Audio`, `VectorArt`, `RichText`, etc.). See [`COMPONENT-API.md`](COMPONENT-API.md) for full rules.
- **Component function pattern:**
  - Use inline arrow functions with `export const`
  - Accept `props` as the argument (do NOT destructure in function signature)
  - Destructure props inside the component body

## 1.2 Implementation Standards

### When to Use elementProps

See [`COMPONENT-API.md`](COMPONENT-API.md) for full elementProps rules and the decision tree.

### React & Runtime Standards

All components MUST follow these patterns:

**1. SSR-Safe Implementation**

- NO browser APIs at module scope (window, document, navigator, etc.)
- Guard browser APIs with typeof checks or useEffect
- All browser-dependent logic must run client-side only

See [`REACT-PATTERNS.md`](REACT-PATTERNS.md) §1.1 for code examples.

**2. Clean Code**

- NO TypeScript errors
- NO unused variables or imports
- NO comments in React component files — code should be self-documenting through clear naming
- NO TODO comments in generated code
- **Remove ALL comments from the final component** — including any comments from templates/examples

**3. Data-Driven Components (NO children in exported props)**

See [`COMPONENT-API.md`](COMPONENT-API.md) for full rules and patterns.

**4. Breakpoint-Responsive Properties (NO props for visual variations)**

See [`PROPS-VS-CSS.md`](PROPS-VS-CSS.md) for full rules and patterns.

**5. Reactive to Prop Changes**

- Components MUST react to prop changes
- If state is derived from props, use `useEffect` with prop dependencies
- State initialized from props should update when props change

**6. Event Handler Scope (Internal by Default)**

Unless explicitly specified as a component capability/API in the specification, all event handlers are **internal** and NOT exposed as props.

**Internal handlers (default):**

- Used for component behavior (autoplay, animations, state management)
- NOT exposed in the component's props interface

**External handlers (only when specified):**

- Only expose handlers that are explicitly listed as component capabilities
- Example: If specification says "onClick callback for external control", then add `onClick?: () => void` to props

**Child component handlers:**

- Internal sub-components receive handlers from parent via props
- These are still internal to the main component

## 1.3 Implementation Workflow

### Step 1: Analyze Component Parts

For each part of the component, decide:

**CSS class only if**:

- ✅ Purely visual/decorative
- ✅ No data or configuration needed
- ✅ No direction override needed
- ✅ No custom behavior needed

**Use elementProps if**:

- ✅ Needs data/content
- ✅ Needs direction override
- ✅ Has state or behavior
- ✅ Needs event handlers

See [`COMPONENT-API.md`](COMPONENT-API.md) and [`PROPS-VS-CSS.md`](PROPS-VS-CSS.md) for the decision trees.

### Step 2: Build Props Interface

Combine:

1. Data/content props (from specification)
2. Behavior props (from specification)
3. Mandatory React props (direction, a11y, className, id)
4. elementProps (only for parts that need it)

### Step 3: Implement

Follow Part 2 templates with mandatory patterns applied.

# Part 2: CSS Rules

All CSS authoring rules — root layout, naming, RTL, state styles,
transitions, etc. — live in [`CSS-GUIDELINES.md`](CSS-GUIDELINES.md).

See [`PROPS-VS-CSS.md`](PROPS-VS-CSS.md) and [`COMPONENT-API.md`](COMPONENT-API.md) for the prop vs CSS vs `elementProps` decision trees.

# Part 3: Examples & Reference

## 3.1 Implementation Checklist

**Phase 1: Analysis** — Parse information, map component structure (see Part 0)

**Phase 2: Component File** — Apply all §1.1 mandatory features and §1.2 implementation standards

**Phase 3: Styles** — Apply Part 2 SCSS rules
