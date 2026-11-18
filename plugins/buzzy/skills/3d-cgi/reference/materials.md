# 3D CGI — Material & Surface Library

材质必须服从物理。velvet 不能 mirror；玻璃要写 Fresnel / 折射，不要只写 "shiny"。

## Language

- **SSS**: "Fine facial SSS showing blood flow," "marble with warm SSS in backlight," "translucent jade internal diffusion."
- **PBR**: "Physically accurate PBR, accurate Fresnel on wetted surfaces."
- **Metal**: polished / brushed / oxidized / anodized — pick one finish.
- **Glass / crystal**: clear, frosted, tinted, optical, faceted.
- **Fabric**: velvet SSS vs silk specular vs linen weave.
- **Fur / hair**: strand detail, color variation, backlight SSS.
- **Water**: caustics, surface tension, viscosity, foam.
- **Skin**: pores, thin-area SSS, oil sheen, freckles.
- **Wood / ceramic / organic**: grain, glaze chips, scales, iridescence.

## Production phrases

**Metals**
- Mirror steel: "Near-perfect Fresnel, minimal orange-peel, slight blue cast, hard lit/shadow contrast."
- Brushed aluminum: "Horizontal micro-scratches, soft diffuse spec, warm silver, slight wear."
- Verdigris copper: "Green patina on orange-red recesses, no spec, crusty centuries-old texture."
- 24k gold: "Warm saturated yellow, mirror polish, warm-tinted highlights, soft reflection edges."
- Gunmetal: "Matte cool gray, tool marks, spec only in rim, worn contact zones."

**Organic**
- Skin: "Pores, cheek/ear redness, SSS in ears/lips, oil sheen, vein visibility."
- Aged oak: "Honey-brown rings, dents, matte, weathered corners."
- Leaf: "Adaxial smooth, abaxial stomata, amber-green SSS in backlight, dew refraction."
- Reptile scale: "Overlapping iridescent scales, convex micro-wrinkles, moist refraction."
- Fur: "Strand-level guard hairs, deep SSS at tips, never uniform color."

**Glass**
- Clear: "Sharp Fresnel, strong refraction, edge chromatic fringe, interior secondary reflections."
- Frosted: "Diffuse transmission, no clear refraction, sandblasted microstructure."
- Emerald: "Green-tinted refraction, thicker volumes darker, polished edges."

**Fabrics**
- Black velvet: "Near-zero spec, nap-direction color shift, faint SSS at thin edges."
- Ivory silk: "Warm-tinted sharp spec, soft falloff, elegant drape, no pilling."
- Cream linen: "Yarn-level weave, matte, anisotropic from yarn direction."

**Complex**
- Shallow ocean: "Sky Fresnel, dancing caustics on sand, surface-tension edges, slight green tint."
- White marble: "Gray veins, warm SSS, soft spec, micro-fractures."
- Weathered concrete: "Visible aggregate, stains, algae in crevices, no spec except wet."
- Bioluminescent: "Emissive violet/cyan/amber, illuminates nearby GI, not environment spec."

写完自检：specularity、finish、SSS、refraction、metallic、anisotropy、色变、磨损是否都说清了该说的。
