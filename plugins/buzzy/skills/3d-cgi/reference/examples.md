# 3D CGI — Example Prompts

形状参考，禁止原文照抄到无关 brief。样例里的配乐句**不要**写进 `generate_video.prompt`。每份词末尾 `no background music`。分辨率 / fps 不要写死。

---

## EXAMPLE 1: Pixar Character Reveal

```
OPENING HOOK: A crystalline cube materializes from swirling golden particles
and rotates to reveal a character inside.

Camera: Slow orbital (~45°/sec) around the floating cube, mid-distance,
ease-in/out.

Render Style: Pixar-style 3D, warm saturated palette, soft shading.

Lighting: Golden-hour HDRI, 3200K key upper-left, cool blue fill right,
rim from back. Volumetric god rays through particles.

Subject: Anthropomorphic fox, large eyes, orange fur, white chest, blue vest,
slight confident posture. Starts translucent, solidifies as particles settle.

Materials: Fur SSS in backlight especially ears. Woven vest wrinkles.
Glossy amber irises, sharp spec.

Animation: Coalesce over ~2s, then blink and look at camera, slight smile.
Eyes track the orbit.

Particles: Golden swirl onto the form; trails linger then settle.

Color: Warm golds/oranges against a cool pale-blue to lavender background.

Duration: VIDEO_DURATION seconds.
Composition: Character centered, cube slightly above midline; sparkles in FG.

no background music
```

---

## EXAMPLE 2: Photoreal Luxury Watch

```
OPENING HOOK: A water droplet on polished metal refracts a hidden product
in the background.

Camera: Dolly-in over the first two-thirds of VIDEO_DURATION. Shallow DOF
starts soft, racks onto the watch at the midpoint. Subtle edge chromatic
look, not a resolution promise.

Render Style: Photorealistic product visualization.

Lighting: 3100K key upper-left, 7500K cool fill on metal edge, warm rim.
Studio HDRI. Soft penumbra, no hard shadows.

Subject: Rose-gold watch, black dial, droplet on the bezel, frosted-glass
plinth.

Materials: 18k rose gold mirror polish, zero distortion. Sapphire crystal
sharp Fresnel. Cognac leather grain with slight SSS.

Motion: Watch locked. Droplet rolls a few millimeters under gravity as the
camera approaches. Highlights bloom as focus lands.

Details: Micro-scratches on the crown, warm metallic hour indices,
thread-level strap.

Duration: VIDEO_DURATION seconds.
Composition: Droplet off-center first; watch revealed into a thirds lock.

<<<image_1>>> if a product still is bound: match case shape and dial, not a
new SKU.

no background music
```

---

## EXAMPLE 3: Isometric Sci-Fi City

```
OPENING HOOK: An isometric futuristic city builds from cyan blueprint
wireframe, color and materials flooding in layer by layer.

Camera: Locked 45° isometric. Slow track down and forward through layers.

Render Style: Isometric 3D, crisp geo, photoreal textures, no perspective
drift.

Lighting: Dual-sun — cyan UL, warm UR. 45° shadows matching the iso grid.
GI color bleed. Depth haze.

Subject: Curved glass towers, hover traffic, terraced gardens, canals,
plazas, ad holograms.

Materials: Glass refraction + Fresnel. Brushed steel. Lush vegetation.
Water caustics. Magenta/cyan/yellow neon.

Animation: Wireframe → glass/metal/green. Vehicles on paths. Soft building
lights. Gentle water ripple.

Duration: VIDEO_DURATION seconds.
Composition: City fills frame; FG sharp, BG hazed.

no background music
```

---

## EXAMPLE 4: Creature Transformation

```
OPENING HOOK: A humanoid silhouette turns transparent, shatters into
geometric shards, then snaps into an insectoid form.

Camera: Slow orbit (~30°/sec). Pulls back slightly as the form expands.
Rack to environment only at the end.

Render Style: Photoreal materials on surreal anatomy.

Lighting: 8000K key UL, 3000K fill LR, cyan rear rim, amber opposite rim.
Faint violet bioluminescence. Blue-hour HDRI.

Subject: Start: translucent humanoid with inner crystal. Mid: fractures,
zero-g shards. End: chitin, compound eyes, wet skin under carapace,
veined translucent wings.

Animation (scale to VIDEO_DURATION):
- First third: transparency + inner fractals
- Middle: shards separate and hover
- Last third: snap together bottom-up (legs, torso, head last), then a
  breath and antenna twitch

Particles: Cyan motes on fracture; bioluminescent dust on reassembly.

Duration: VIDEO_DURATION seconds.

no background music
```

---

## EXAMPLE 5: Architectural Flythrough

```
OPENING HOOK: Camera glides into an atrium where the glass ceiling
refracts sunlight into moving fractal caustics.

Camera: One continuous track — atrium, past surfaces, down a spiral stair,
out to a plaza. Slow, meditative, slight tilt-up at the end.

Render Style: Photoreal architectural visualization.

Lighting: 3100K late-afternoon skylight, cool sky bounce, animated ceiling
caustics, GI between wood and stone, volumetric motes in the shafts.

Subject: Multi-pane glass roof, cream limestone, blonde oak plank floors,
brushed stainless structure, reflecting pool, curved walls, living walls.

Materials: Crystal roof with edge dispersion. Fossil limestone. Honey oak
grain, matte sheen. Brushed steel. Clear pool with floor caustics.

Animation: Continuous camera. Gentle pool ripple. Leaves barely move.
Caustics drift as if clouds pass.

Duration: VIDEO_DURATION seconds.
Composition: Leading lines of walls/stairs; depth layers always readable.

<<<image_1>>> if a still of the space is bound: match materials and plan,
do not invent a different building.

no background music
```
