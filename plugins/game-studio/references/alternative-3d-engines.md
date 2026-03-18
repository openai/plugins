# Alternative 3D Engines

This plugin defaults to Three.js and React Three Fiber for code generation. Babylon.js and PlayCanvas still matter, but they are reference-only alternatives in the current plugin shape.

## Babylon.js

Useful sources:

- [Babylon.js home](https://babylonjs.com/)
- [Engine specifications](https://www.babylonjs.com/specifications/)
- [Babylon.js Editor](https://editor.babylonjs.com/)

Choose Babylon.js when:

- the user explicitly wants Babylon.js
- the team wants a more engine-heavy stack with scene, material, viewer, and editor tooling built around one ecosystem
- WebGPU, Havok, node-based rendering or material tooling, or Babylon-specific runtime features are part of the reason for the choice

What Babylon.js is good at:

- full-engine 3D workflows
- strong built-in tooling and editor surfaces
- WebGL and WebGPU support inside one ecosystem
- integrated viewer and inspection-oriented workflows

## PlayCanvas

Useful sources:

- [PlayCanvas graphics overview](https://developer.playcanvas.com/user-manual/graphics/)
- [Supported formats](https://developer.playcanvas.com/user-manual/assets/supported-formats/)
- [PlayCanvas React GLTF API](https://developer.playcanvas.com/user-manual/react/api/gltf/)
- [PlayCanvas Web Components](https://developer.playcanvas.com/user-manual/web-components/)

Choose PlayCanvas when:

- the user explicitly wants PlayCanvas
- the team prefers an editor-centric browser engine workflow
- GLB import, runtime tooling, React bindings, or web-component-based embedding are central to the project

What PlayCanvas is good at:

- editor and engine working together
- GLB-centric browser asset workflows
- strong web embedding patterns
- WebGL and WebGPU support with browser-focused runtime tooling

## Default recommendation

If the user has not already chosen Babylon.js or PlayCanvas, prefer Three.js or React Three Fiber in this plugin because they give the best balance of portability, ecosystem depth, and predictable code generation across normal browser-game repos.
