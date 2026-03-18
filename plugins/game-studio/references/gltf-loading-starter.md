# GLB Loading Starter

Use this as the canonical minimal pattern for loading shipped 3D content.

## Vanilla Three.js

```ts
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader.js";

const draco = new DRACOLoader();
draco.setDecoderPath("/draco/");

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(draco);

gltfLoader.load("/assets/hero.glb", (gltf) => {
  const root = gltf.scene;
  root.traverse((node) => {
    if ("castShadow" in node) {
      node.castShadow = true;
      node.receiveShadow = true;
    }
  });
  scene.add(root);
});
```

## React Three Fiber

```tsx
import { useGLTF } from "@react-three/drei";

function HeroModel() {
  const gltf = useGLTF("/assets/hero.glb");
  return <primitive object={gltf.scene} />;
}
```

## Notes

- Default shipping format is GLB or glTF 2.0.
- Keep optimization upstream in the asset pipeline; loader code should stay boring.
