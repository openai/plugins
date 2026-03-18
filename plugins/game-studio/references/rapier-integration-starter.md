# Rapier Integration Starter

Use this as the smallest canonical pattern for adding physics without letting it take over the whole runtime.

## Vanilla Three.js

```ts
import RAPIER from "@dimforge/rapier3d-compat";

await RAPIER.init();

const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setTranslation(0, 2, 0));
world.createCollider(RAPIER.ColliderDesc.cuboid(0.5, 0.5, 0.5), body);

renderer.setAnimationLoop(() => {
  world.step();
  const p = body.translation();
  mesh.position.set(p.x, p.y, p.z);
  renderer.render(scene, camera);
});
```

## React Three Fiber

```tsx
import { Physics, RigidBody } from "@react-three/rapier";

<Physics gravity={[0, -9.81, 0]}>
  <RigidBody colliders="cuboid">
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#3dd9b8" />
    </mesh>
  </RigidBody>
</Physics>;
```

## Notes

- Keep physics state synchronized through an explicit bridge.
- Do not bury gameplay rules inside render or physics callbacks.
