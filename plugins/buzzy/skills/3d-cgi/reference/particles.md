# 3D CGI — Particles & Effects

粒子必须量化：密度、颜色、速度、时长。不要写 "lots of cool particles"。

1. **Dust in god rays** — millions of motes, gravity settle, size variation, golden-orange, never homogeneous.
2. **Swirling smoke** — turbulent then layered, warm-gray → transparent, interior caustics.
3. **Coalescing swarm** — thousands of cyan motes form a figure; parts delay (hands first); soft emissive.
4. **Sparks / glitter** — sparse gold/white points, gravity arcs, short trails, light nearby surfaces.
5. **Water splash** — sheets + droplets, refraction, surface tension, caustics, ~1.5s burst.
6. **Fire & embers** — blue base / yellow mid / orange top, buoyancy, no looping cycle.
7. **Data / tech** — cubes/spheres/lines on splines, neon cyan/magenta, fade in/out.
8. **Rain or mist** — streaks vs hanging spheres; rain + wind; mist almost still.
9. **Leaves / paper / feathers** — tumble, air drag, color variation, slow.
10. **Explosion debris** — rocks + dust + embers, parabolic gravity, 2s burst + settle.
11. **Bioluminescent trail** — spawn along motion, fade ~1s, light the set.
12. **Fog / haze layer** — density vs distance, glows in light / silhouettes in shadow.

没有特效需要就整段省略，不要为「看起来 3D」硬加粒子。
