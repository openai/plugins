# React Three Fiber Stack

This is the default React-native 3D stack for the plugin.

## Primary components

- [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction) for declarative Three.js rendering in React.
- [Drei](https://drei.docs.pmnd.rs/controls/introduction) for controls, loaders, helpers, environments, and common scene utilities.
- [React Postprocessing](https://react-postprocessing.docs.pmnd.rs/introduction) for effect composition in React-hosted scenes.
- [React Three Rapier](https://pmndrs.github.io/react-three-rapier/) for physics integration.
- [React Three A11y](https://a11y.docs.pmnd.rs/introduction) when scene interaction benefits from accessibility-aware patterns.
- [glTF Transform](https://gltf-transform.dev/) and the [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) for shipped assets.

## Default stack choices

- Runtime: `@react-three/fiber` + `three`
- Helper ecosystem: `@react-three/drei`
- Physics: `@react-three/rapier`
- Effects: `@react-three/postprocessing`
- Accessibility: `@react-three/a11y` when appropriate
- Assets: GLB or glTF 2.0

## Choose this stack when

- the 3D scene lives inside a React app
- the UI shell, settings, or product flow already uses React
- the team benefits from declarative scene composition
- the scene must share app state with non-canvas UI

## Avoid this stack when

- the project wants a cleaner imperative loop with minimal React coordination
- the whole game runtime would be easier to reason about in plain TypeScript

## Companion references

- `threejs-stack.md`
- `react-three-fiber-starter.md`
- `gltf-loading-starter.md`
- `rapier-integration-starter.md`
- `web-3d-asset-pipeline.md`
- `webgl-debugging-and-performance.md`
