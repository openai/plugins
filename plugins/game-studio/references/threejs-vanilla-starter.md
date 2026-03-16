# Three.js Vanilla Starter

Use this as the smallest canonical starting point for a plain TypeScript or Vite Three.js app.

## Files

```text
src/
  main.ts
```

## `src/main.ts`

```ts
import * as THREE from "three";

const scene = new THREE.Scene();
scene.background = new THREE.Color("#101418");

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 1.5, 4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(4, 6, 3);
scene.add(light);

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: "#3dd9b8" }),
);
scene.add(mesh);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

renderer.setAnimationLoop(() => {
  mesh.rotation.y += 0.01;
  renderer.render(scene, camera);
});
```

## Notes

- Start here for direct loop and renderer control.
- If the scaffold needs UI, start with one compact objective chip and one transient controls hint rather than multiple permanent cards.
- Keep notes, codex, maps, and settings behind on-demand surfaces. The starter scene should stay readable while moving the camera.
- Add GLB loading with `gltf-loading-starter.md`.
- Add physics sync with `rapier-integration-starter.md`.
- Use `three-hud-layout-patterns.md` for low-chrome 3D overlay defaults.
