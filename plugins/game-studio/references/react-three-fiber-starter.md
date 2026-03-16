# React Three Fiber Starter

Use this as the smallest canonical starting point for a React-hosted 3D scene.

## Files

```text
src/
  App.tsx
```

## `src/App.tsx`

```tsx
import { Canvas } from "@react-three/fiber";

function Spinner() {
  return (
    <mesh rotation={[0.4, 0.6, 0]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#3dd9b8" />
    </mesh>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <Canvas camera={{ position: [0, 1.5, 4], fov: 60 }}>
        <color attach="background" args={["#101418"]} />
        <ambientLight intensity={0.7} />
        <directionalLight position={[4, 6, 3]} intensity={1.2} />
        <Spinner />
      </Canvas>
      <div className="hud">
        <div className="objective-chip">Reach the lantern bridge.</div>
        <div className="hint-pill">WASD to move. Hold mouse to look.</div>
      </div>
    </div>
  );
}
```

## Notes

- Start here when the 3D scene lives inside an existing React app.
- Keep the initial HUD sparse. One compact objective surface and one transient hint is usually enough for a first playable scaffold.
- Put lore, notes, map, and settings behind drawers or modals instead of opening them all by default.
- Add GLB loading with `gltf-loading-starter.md`.
- Add physics with `rapier-integration-starter.md`.
- Use `three-hud-layout-patterns.md` for low-chrome 3D overlay defaults.
