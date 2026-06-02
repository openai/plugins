# Component Configuration

After scaffolding the component and running `npx wix build && npx wix generate manifest`,
configure the component's behavior in the editor by writing **partial
manifest overrides** in the component's hand-edited extension file
(`<ComponentName>.extension.ts`). That file imports the auto-generated
manifest and spreads it; specific fields are overridden inline. Re-running
this command regenerates each `<ComponentName>.generated.ts`
companion but never touches the overrides authored in the extension file.

---

## 1. Verifying that height sizing type meets user needs

Set `installation.initialSize.height.sizingType` based on whether the
component's own content decides how tall it is.

### Heuristic — one question

**Does the component's own content decide how tall it is?**

- **Yes — height should grow with text the user types or children they drop inside** → `LAYOUT.SIZING_TYPE.content`. Omit `pixels`.
- **No — the component is a framed visual** (a graphic, an embedded media surface, a form control with a standard height, an empty placeholder) → `LAYOUT.SIZING_TYPE.pixels`. Provide a `pixels` default that matches its natural visual size.

**Tiebreaker:** if a designer would drag a handle to set the height, it's `pixels`. If the height should just fit whatever is inside, it's `content`.

### Where to write the override

```ts
import { extensions } from '@wix/astro/builders';
import { LAYOUT } from '@wix/react-component-schema';
import { manifest } from './ComponentName.generated';

const componentExtension = extensions.editorReactComponent({
  // …other fields…
  installation: {
    initialSize: {
      width: {
        sizingType: LAYOUT.SIZING_TYPE.pixels,
        pixels: 250,
      },
      height: {
        sizingType: LAYOUT.SIZING_TYPE.updateMe,
      },
    },
  },
});
```

### Examples

**Content-driven** (`LAYOUT.SIZING_TYPE.content`) — testimonial card,
FAQ accordion, pricing tier, blog-post body, list/grid of arbitrary
children:

```ts
height: {
  sizingType: LAYOUT.SIZING_TYPE.content,
}
```

**Framed visual** (`LAYOUT.SIZING_TYPE.pixels`) — hero banner with a
fixed image, video embed, color-picker swatch grid, OTP input, empty
placeholder slot:

```ts
height: {
  sizingType: LAYOUT.SIZING_TYPE.pixels,
  pixels: 320,
}
```

---

## 2. Verifying that resize direction meets user needs

Set `editorElement.layout.resizeDirection` based on which axes the
designer should be able to control with a drag handle. Allow an axis
if dragging it produces a meaningful, intended change. Disallow it if
dragging would do nothing visible or would break the component's
identity.

### Heuristic — which axes are meaningful?

| Choice | When to use |
|--------|-------------|
| `horizontalAndVertical` | Content fills or stretches in both axes. Hero, carousel, gallery, card grid, embed, form control, any framed visual. **Default for most components.** |
| `horizontal` | Height is rigid/intrinsic — cannot meaningfully stretch. Breadcrumb, tag row, nav bar, single-line input, slider rail. |
| `vertical` | Width is rigid/intrinsic. Vertical stack, ribbon, sidebar rail. |
| `aspectRatio` | Distortion breaks identity — logo, illustration, animation. |
| `none` | Size fully owned by a parent layout. Never for top-level components. |

**Tiebreaker:** if a drag handle on an axis would feel inert or wrong
to a designer, take it away.

### Where to write the override

```ts
import { extensions } from '@wix/astro/builders';
import { LAYOUT } from '@wix/react-component-schema';
import { manifest } from './ComponentName.generated';

const componentExtension = extensions.editorReactComponent({
  // …other fields…
  editorElement: {
    ...manifest.editorElement,
    layout: {
      resizeDirection: LAYOUT.RESIZE_DIRECTION._selectedResizeDirection_,
    },
  },
});
```

### Examples

```ts
// hero, carousel, gallery, card grid, embed, form
resizeDirection: LAYOUT.RESIZE_DIRECTION.horizontalAndVertical,

// breadcrumb, tag row, nav bar, slider rail
resizeDirection: LAYOUT.RESIZE_DIRECTION.horizontal,

// logo, illustration, animation
resizeDirection: LAYOUT.RESIZE_DIRECTION.aspectRatio,
```

---

## 3. Wiring defaults into the manifest

1. **Export `defaultProps` from `component.tsx`** so the extension file can import it.
2. **Import `componentUrl` from `'./component.tsx?url'`** (the wrapped component), not from `'./ComponentName.tsx?url'` (the raw component).
3. **Wrap `editorElement` with `withEditorElementDefaults`** using the same `defaultProps`.

```ts
import { withEditorElementDefaults } from '@wix/react-component-utils';
import componentUrl from './component.tsx?url';
import { defaultProps } from './component';

// in the extension:
editorElement: withEditorElementDefaults({
  ...manifest.editorElement,
}, defaultProps),
resources: {
  ...manifest.resources,
  client: { componentUrl },
},
```

---

## 4. Enabling automatic installation on Harmony editor

**Always include `"staticContainer": "HOMEPAGE"`** in `installation` so the
component is automatically installed on the Harmony editor.

```ts
const componentExtension = extensions.editorReactComponent({
  // …other fields…
  installation: {
    // …other fields…
    staticContainer: 'HOMEPAGE',
  },
});
```
