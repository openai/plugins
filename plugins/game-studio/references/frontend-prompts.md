# Frontend Prompts

Use these prompt shapes to keep browser-game UI intentional instead of generic.

## Prompt ingredients

- game genre and fantasy
- camera or viewpoint
- player verbs
- HUD zones
- menu surfaces
- motion tone
- desktop and mobile expectations
- playfield protection and disclosure strategy
- anti-patterns to avoid

## HUD implementation prompt

```text
Design and implement the HUD for a browser game.

Game fantasy: <genre and world>
Viewpoint: <top-down, side-view, tactical grid, third-person, first-person>
Primary verbs: <attack, move, cast, build, dodge, inspect>
HUD zones: <top status, bottom command bar, side objectives, modal panels>
Tone: <ornate, rugged, clean sci-fi, painterly, arcade>
Motion: <restrained, snappy, dramatic only on important state changes>
Platforms: desktop and mobile
Constraints: readable over active gameplay, DOM-based overlays, CSS variables, no generic dashboard look
Playfield protection: keep the central play area clear during normal play, prefer one primary persistent HUD cluster, and move long-form notes or controls behind menus
Avoid: flat admin UI, default font stack, cluttered overlays, constant micro-animation, equal-weight cards around every edge, broad always-on panels that cover the world
```

## Menu implementation prompt

```text
Build the shell UI for a browser game with the following surfaces:
- title screen
- pause menu
- settings panel
- game-over or victory screen

Keep the menus visually tied to the game world, not to a SaaS app aesthetic. Use strong hierarchy, intentional typography, meaningful motion, and responsive layout.
```

## Low-chrome 3D starter prompt

```text
Design the initial playable HUD for a browser 3D game.

Goal: the first screen should feel playable in under 3 seconds, not like a dashboard.
Camera mode: <third-person, first-person, orbit, rail>
Primary verbs: <move, inspect, interact, attack, build>
Persistent UI budget:
- one compact objective chip or status cluster
- one optional small secondary surface
- one transient controls or interaction hint

Interaction rules:
- keep the center of the playfield clear
- keep the lower-middle playfield mostly clear during normal play
- lore, notes, quest details, and long control lists live behind a drawer, pause menu, or toggle
- modal and pause states must gate camera input correctly

Avoid:
- giant title cards over live gameplay
- field notes, controls, and objectives all open at once
- equally weighted glass panels in every corner
- full-screen overlay chrome during normal movement
```

## 3D overlay prompt

```text
Design and implement the HUD and menu overlays for a browser 3D game.

Engine context: <vanilla Three.js or React Three Fiber>
Camera mode: <third-person, first-person, orbit, rail>
Primary verbs: <move, inspect, interact, attack, build>
Overlay surfaces: <reticle, quest log, inventory, pause menu, settings>
Interaction constraints:
- DOM overlays, not in-scene UI by default
- modal and menu states must suspend or gate camera input correctly
- keyboard and pointer states must be explicit
- reduced-motion support for non-essential transitions
- keep the center of the screen clear during normal play
- keep the lower-middle playfield mostly clear during normal play
- start with one compact objective surface and transient hints rather than multiple permanent cards
- secondary content such as notes, lore, and full control references should be collapsed by default
Avoid:
- dashboard UI
- cluttered full-screen overlays
- boxed panels around every edge of the viewport
- full-width top-and-bottom panel stacks
- permanent text-heavy cards competing with the scene
- camera movement continuing under active menus
```
