# Engine Selection

Use this table to choose the default implementation path for browser games in this plugin.

## Default choices

- Choose Phaser for 2D games unless the user explicitly asks for another stack.
- Choose vanilla Three.js for explicit 3D or WebGL-first experiences in plain TypeScript or Vite apps.
- Choose React Three Fiber when the 3D scene is part of a React application and shared app state or declarative composition matters.
- Choose raw WebGL only when engine abstractions are the problem, not because WebGL sounds more advanced.
- Treat Babylon.js and PlayCanvas as alternative ecosystems, not the default path in this plugin.

## Phaser is the best fit when

- the game is sprite- or tile-based
- the game is top-down, side-view, or grid tactics
- you need camera, sprite, and scene primitives quickly
- the UI will mostly live in DOM overlays
- the game loop is gameplay-first rather than renderer-first

## Three.js is the best fit when

- the game is genuinely 3D
- camera movement and depth are central to play
- materials, lighting, or scene composition matter more than sprite tooling
- the user explicitly asks for Three.js or WebGL-based 3D work
- the team wants direct control over scene setup, loaders, physics integration, and the game loop

## React Three Fiber is the best fit when

- the project already lives in React
- the 3D scene needs to share app state with the rest of the product
- declarative scene composition is more valuable than a fully imperative loop
- the team benefits from pmndrs tooling such as Drei, React Postprocessing, or `@react-three/rapier`

## Babylon.js or PlayCanvas are the best fit when

- the user explicitly asks for those engines
- the team already has engine-specific tooling or editor workflows in those ecosystems
- the project wants engine-heavy runtime features, editor-first workflows, or platform-specific tooling that Three.js does not provide by default

## Raw WebGL is the best fit when

- the project is shader-heavy
- you need a custom renderer or post-processing pipeline
- the user explicitly wants low-level rendering control

## Avoid these mismatches

- Do not choose a 3D stack for a normal 2D tactics or platformer game.
- Do not choose raw WebGL for a game that mostly needs engine conveniences.
- Do not force HUD and menus into canvas or WebGL when DOM would be clearer.
- Do not default to Babylon.js or PlayCanvas when the user mainly wants portable TypeScript code generation across browser-game repos.
