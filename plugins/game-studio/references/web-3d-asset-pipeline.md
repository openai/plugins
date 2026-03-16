# Web 3D Asset Pipeline

This is the default 3D asset shipping guidance for the plugin.

## Primary sources

- [Blender glTF exporter manual](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html)
- [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)
- [glTF Transform](https://gltf-transform.dev/)
- [PlayCanvas supported formats](https://developer.playcanvas.com/user-manual/assets/supported-formats/) for a good reference on why GLB is the recommended runtime format in browser engines

## Default output

- Ship GLB when possible.
- Use `.gltf` with external files only when the asset pipeline or delivery strategy genuinely needs that shape.

## Recommended workflow

1. Clean the source asset in the DCC tool.
2. Export to GLB or glTF 2.0.
3. Run glTF Transform for validation, pruning, deduplication, and size reduction.
4. Apply the chosen geometry and texture compression strategy.
5. Verify pivots, scale, collision assumptions, and hierarchy naming.
6. Test the asset in the runtime before treating it as final.

## Compression and optimization

- Use Draco or Meshopt deliberately, not both by default.
- Use KTX2 or BasisU when the runtime stack supports GPU-friendly compressed textures.
- Keep texture resolution aligned with actual on-screen use.
- Reuse materials and avoid unnecessary texture uniqueness.

## Runtime checks

- scale is consistent across assets
- pivots match gameplay expectations
- node names are stable
- collision proxy needs are handled
- animation clips and variants load correctly
- memory and load time are reasonable for the scene

## Starter patterns

- `threejs-vanilla-starter.md`
- `react-three-fiber-starter.md`
- `gltf-loading-starter.md`
- `rapier-integration-starter.md`
