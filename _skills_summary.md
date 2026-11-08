# Skills Catalog

Source: `E:\PyCharmProject\plugins`
Total skills: **536** across **47** plugins/folders.

## Index

- [.agents](#agents) (1)
- [adobe](#adobe) (6)
- [airtable](#airtable) (3)
- [boltz-api-cli](#boltz-api-cli) (8)
- [build-ios-apps](#build-ios-apps) (9)
- [build-macos-apps](#build-macos-apps) (11)
- [build-web-apps](#build-web-apps) (6)
- [build-web-data-visualization](#build-web-data-visualization) (18)
- [canva](#canva) (8)
- [chatcut](#chatcut) (1)
- [circleci](#circleci) (4)
- [cloudflare](#cloudflare) (9)
- [coderabbit](#coderabbit) (1)
- [codex-security](#codex-security) (15)
- [creative-production](#creative-production) (2)
- [data-analytics](#data-analytics) (18)
- [dropbox](#dropbox) (6)
- [expo](#expo) (13)
- [figma](#figma) (12)
- [game-studio](#game-studio) (9)
- [google-drive](#google-drive) (5)
- [higgsfield](#higgsfield) (3)
- [hyperframes](#hyperframes) (5)
- [life-science-research](#life-science-research) (50)
- [magicpath](#magicpath) (1)
- [mixpanel-headless](#mixpanel-headless) (4)
- [ngs-analysis](#ngs-analysis) (18)
- [notion](#notion) (4)
- [nvidia](#nvidia) (12)
- [openai-ads-conversions](#openai-ads-conversions) (1)
- [openai-developers](#openai-developers) (5)
- [plugin-eval](#plugin-eval) (9)
- [posthog](#posthog) (1)
- [product-design](#product-design) (10)
- [public-equity-investing](#public-equity-investing) (23)
- [remotion](#remotion) (12)
- [sentry](#sentry) (1)
- [shopify](#shopify) (20)
- [stripe](#stripe) (7)
- [supabase](#supabase) (2)
- [superpowers](#superpowers) (14)
- [temporal](#temporal) (4)
- [test-android-apps](#test-android-apps) (2)
- [twilio-developer-kit](#twilio-developer-kit) (55)
- [vercel](#vercel) (54)
- [zoom](#zoom) (53)
- [zotero](#zotero) (1)

## .agents

1 skill(s)

### `plugin-creator`

Create and scaffold plugin directories for Codex with a required `.codex-plugin/plugin.json`, optional plugin folders/files, and baseline placeholders you can edit before publishing or testing. Use when Codex needs to create a new personal plugin, add optional plugin structure, or generate or update personal or repo-root `.agents/plugins/marketplace.json` entries for plugin ordering and availability metadata.

- Path: `.agents/skills/plugin-creator/SKILL.md`

## adobe

6 skill(s)

### `adobe-batch-edit-photos`

Apply consistent photo adjustments across a set of images so they look like they were edited together. Use this skill whenever the user says "make my photos look cohesive", "give all these the same style", "apply a warm and golden feel to all of these", "make this cinematic", "match the look across my photos", "edit all my travel photos the same way", "batch edit these", "make these consistent", "fix my phone photos", or uploads a folder of photos and wants a unified, polished result. Also triggers for requests like "apply a preset to all of these", "make these look professional", or "they were shot in mixed lighting — can you fix them all". Outputs direct final image URLs plus an in-chat preview grid and optional Firefly Board link. Access: 🔐 Signed-In required | Gen AI: ❌

- Path: `plugins/adobe/skills/adobe-batch-edit-photos/SKILL.md`

### `adobe-create-mockups`

Use when a user wants to see their logo, design, or sketch on a product or scene mockup — mugs, t-shirts, business cards, hats, phone screens, posters, billboards, or similar. Triggers on "create mockups", "show my logo on products", or any logo upload with a request to visualize it on items. Access: 🔐 Signed-In required | Gen AI: ✅ Adobe Firefly via `image_generate` used for design creation, sketch polishing, and mockup scene generation

- Path: `plugins/adobe/skills/adobe-create-mockups/SKILL.md`

### `adobe-create-social-variations`

Resize, crop, or export any image or video into platform-ready social media assets using Adobe Creative Cloud tools. Use this skill when a user wants to prepare a photo, image, or video for one or more social platforms — Instagram, TikTok, LinkedIn, Facebook, YouTube, Snapchat, Pinterest, Threads, or X/Twitter. Triggers on: "prepare my image for Instagram", "resize for TikTok", "get this ready to post", "make versions for all platforms", "social media sizes", "crop for stories", "export for LinkedIn", "resize my video for social", "make social media assets", or any request to adapt a photo or video for specific platforms. Handles subject-aware cropping, AI canvas expansion, test previews before full runs, and same-ratio video resizing.

- Path: `plugins/adobe/skills/adobe-create-social-variations/SKILL.md`

### `adobe-design-from-template`

Create any visual design using Adobe Express templates — flyers, posters, social media posts (Instagram, Facebook, LinkedIn), business cards, invitations, greeting cards, resumes, cover letters, brochures, newsletters, certificates, presentations, YouTube thumbnails, email headers, logos, menus, and labels. Use this skill whenever the user wants to make, design, or build any visual — even if they just say "make me a flyer", "design a poster", "I need something for Instagram", "create an event invite", or "make a business card". Also handles browsing templates, editing text, replacing images, changing backgrounds, animating, and exporting designs. Access: 🔐 Signed-In required | Gen AI: ❌ by default — image replacement only where the surface permits generative AI (e.g. Codex); none on Claude

- Path: `plugins/adobe/skills/adobe-design-from-template/SKILL.md`

### `adobe-edit-quick-cut`

Create a punchy sizzle reel from a video using Adobe Quick Cut. Use this skill whenever a user wants to cut, trim, or shorten a video into highlights — including phrases like "make a sizzle reel", "make a highlight reel", "quick cut this", "cut the best parts", "shorten this video", "make a highlight clip", "summarize this video visually", or any request to produce a shorter edited version of a video. Use this skill for Quick Cut requests before suggesting manual editing in Premiere. Requires the user to upload a video file.

- Path: `plugins/adobe/skills/adobe-edit-quick-cut/SKILL.md`

### `adobe-retouch-portraits`

Bulk-retouch a folder of portrait photos using Adobe tools — designed for wedding photographers and event photographers who need fast, walk-away batch processing. Use this skill when the user says "retouch my photos", "batch process these portraits", "process my wedding photos", "clean up this folder of images", "run my headshots through Adobe", or uploads/selects a folder of photos and wants them polished and ready to review. Automatically applies auto-straighten, auto-tone, and auto-light to every image. Outputs a preview grid and download folder. Access: 🔐 Signed-In required | Gen AI: ❌ by default — optional background-only cleanup only where the surface permits generative AI (e.g. Codex); none on Claude

- Path: `plugins/adobe/skills/adobe-retouch-portraits/SKILL.md`

## airtable

3 skill(s)

### `airtable-cli`

Lists bases, reads and writes records, manages tables and fields, filters and searches data in Airtable via the `airtable-mcp` CLI. Use when the task involves Airtable data or the user mentions airtable-mcp, bases, tables, records, or fields.

- Path: `plugins/airtable/skills/airtable-cli/SKILL.md`

### `airtable-filters`

Use this skill when the user wants to find, filter, or narrow down Airtable records by field values, even when they don't explicitly say "filter.

- Path: `plugins/airtable/skills/airtable-filters/SKILL.md`

### `airtable-overview`

Explains what Airtable is and how data is structured — bases, tables, fields, records, views, automations, and interfaces. Use when you need context about the Airtable data model.

- Path: `plugins/airtable/skills/airtable-overview/SKILL.md`

## boltz-api-cli

8 skill(s)

### `boltz-check-status`

Boltz job status and result recovery. Use when listing jobs, checking progress, resuming downloads, recovering results, or downloading an existing job ID. Not for starting new jobs.

- Path: `plugins/boltz-api-cli/skills/boltz-check-status/SKILL.md`

### `boltz-cli-setup`

Boltz CLI setup and auth. Use when installing, updating, verifying, or authenticating `boltz-api`, or fixing missing CLI, PATH, sandbox, browser login, or auth errors.

- Path: `plugins/boltz-api-cli/skills/boltz-cli-setup/SKILL.md`

### `boltz-protein-design`

Design new protein binders with Boltz. Use when generating protein, peptide, antibody, nanobody, or custom binder candidates for a target. Not for screening existing proteins or small molecules.

- Path: `plugins/boltz-api-cli/skills/boltz-protein-design/SKILL.md`

### `boltz-protein-screen`

Screen existing protein binders with Boltz. Use when ranking a supplied protein, peptide, antibody, nanobody, or binder library against a target. Not for designing new proteins or screening small molecules.

- Path: `plugins/boltz-api-cli/skills/boltz-protein-screen/SKILL.md`

### `boltz-small-molecule-adme`

Predict Tier-1 ADME/ADMET for small molecules with Boltz from bare SMILES — no target, no docking. Use when the user wants solubility, permeability, or lipophilicity/logD for a molecule or list of molecules. Not for ranking molecules against a protein target (use boltz-small-molecule-screen, which already returns ADME free).

- Path: `plugins/boltz-api-cli/skills/boltz-small-molecule-adme/SKILL.md`

### `boltz-small-molecule-design`

Design new small-molecule binders with Boltz. Use when generating novel ligands or hits for a target without a fixed compound library. Not for screening existing molecules or one-off docking.

- Path: `plugins/boltz-api-cli/skills/boltz-small-molecule-design/SKILL.md`

### `boltz-small-molecule-screen`

Screen existing small-molecule libraries with Boltz. Use when docking, scoring, or ranking a supplied SMILES or compound library against a target; also returns free Tier-1 ADME/ADMET (solubility, permeability, lipophilicity/logD) per molecule. Not for de novo molecule design, one-off docking, or ADME on bare SMILES with no target (use boltz-small-molecule-adme).

- Path: `plugins/boltz-api-cli/skills/boltz-small-molecule-screen/SKILL.md`

### `boltz-structure-and-binding`

Predict structures and binding for one defined complex with Boltz. Use when folding a protein, RNA, DNA, or ligand complex, docking one ligand, predicting an interface, or scoring binding. Not for screening libraries or design.

- Path: `plugins/boltz-api-cli/skills/boltz-structure-and-binding/SKILL.md`

## build-ios-apps

9 skill(s)

### `ios-app-intents`

Design App Intents, app entities, and App Shortcuts for iOS system surfaces. Use when exposing app actions or content to Shortcuts, Siri, Spotlight, widgets, or controls.

- Path: `plugins/build-ios-apps/skills/ios-app-intents/SKILL.md`

### `ios-debugger-agent`

Build, run, and debug iOS apps on Simulator with XcodeBuildMCP. Use when launching an app, inspecting simulator UI or logs, or diagnosing runtime behavior.

- Path: `plugins/build-ios-apps/skills/ios-debugger-agent/SKILL.md`

### `ios-ettrace-performance`

Capture and interpret iOS Simulator ETTrace profiles. Use when profiling launch or runtime latency, comparing traces, or finding CPU-heavy stacks.

- Path: `plugins/build-ios-apps/skills/ios-ettrace-performance/SKILL.md`

### `ios-memgraph-leaks`

Capture and inspect iOS leaks and memgraphs. Use when debugging leaked objects, retain cycles, memory growth, or before/after leak evidence.

- Path: `plugins/build-ios-apps/skills/ios-memgraph-leaks/SKILL.md`

### `ios-simulator-browser`

Mirror an iOS Simulator into the Codex in-app browser and render SwiftUI previews from importable Swift packages in that simulator with hot reload. Use when a user wants to watch or interact with an iOS app in the browser, see a SwiftUI preview outside Xcode Canvas, iterate live on a preview, or capture browser-visible simulator proof.

- Path: `plugins/build-ios-apps/skills/ios-simulator-browser/SKILL.md`

### `swiftui-liquid-glass`

Implement and review iOS 26+ SwiftUI Liquid Glass UI. Use when adopting Liquid Glass or checking its correctness, performance, and design fit.

- Path: `plugins/build-ios-apps/skills/swiftui-liquid-glass/SKILL.md`

### `swiftui-performance-audit`

Audit SwiftUI runtime performance from code first. Use when diagnosing slow rendering, janky scrolling, expensive updates, or profiling needs.

- Path: `plugins/build-ios-apps/skills/swiftui-performance-audit/SKILL.md`

### `swiftui-ui-patterns`

Build and refactor SwiftUI UI with component patterns and examples. Use when shaping navigation, state, layouts, controls, or screen composition.

- Path: `plugins/build-ios-apps/skills/swiftui-ui-patterns/SKILL.md`

### `swiftui-view-refactor`

Refactor SwiftUI view files into stable, testable structure. Use when splitting large views, tightening data flow, or cleaning Observation ownership.

- Path: `plugins/build-ios-apps/skills/swiftui-view-refactor/SKILL.md`

## build-macos-apps

11 skill(s)

### `appkit-interop`

Bridge macOS SwiftUI into AppKit narrowly. Use when implementing representables, reaching NSWindow or panels, handling menus, or using the responder chain.

- Path: `plugins/build-macos-apps/skills/appkit-interop/SKILL.md`

### `build-run-debug`

Build, run, and debug macOS apps with shell-first Xcode and Swift workflows. Use when launching apps or diagnosing build, startup, or runtime failures.

- Path: `plugins/build-macos-apps/skills/build-run-debug/SKILL.md`

### `liquid-glass`

Implement and review macOS SwiftUI Liquid Glass UI. Use when adopting system glass, removing conflicting custom chrome, or building glass surfaces.

- Path: `plugins/build-macos-apps/skills/liquid-glass/SKILL.md`

### `packaging-notarization`

Prepare macOS packaging and notarization workflows. Use when archiving apps, validating bundles, or explaining distribution-only failures.

- Path: `plugins/build-macos-apps/skills/packaging-notarization/SKILL.md`

### `signing-entitlements`

Inspect macOS signing, entitlements, and Gatekeeper issues. Use when diagnosing code signing, sandbox, hardened runtime, or trust failures.

- Path: `plugins/build-macos-apps/skills/signing-entitlements/SKILL.md`

### `swiftpm-macos`

Build, run, and test SwiftPM macOS packages and executables. Use when the repo is package-first or has no Xcode project.

- Path: `plugins/build-macos-apps/skills/swiftpm-macos/SKILL.md`

### `swiftui-patterns`

Build macOS SwiftUI scenes and components with desktop patterns. Use when shaping windows, commands, toolbars, settings, split views, or inspectors.

- Path: `plugins/build-macos-apps/skills/swiftui-patterns/SKILL.md`

### `telemetry`

Add and verify lightweight macOS runtime telemetry. Use when wiring Logger events or inspecting logs for windows, sidebars, menus, and actions.

- Path: `plugins/build-macos-apps/skills/telemetry/SKILL.md`

### `test-triage`

Triage macOS tests across Xcode and SwiftPM. Use when narrowing failures, explaining assertions or crashes, or separating setup from regressions.

- Path: `plugins/build-macos-apps/skills/test-triage/SKILL.md`

### `view-refactor`

Refactor macOS SwiftUI views and scenes into stable structure. Use when splitting large views, tightening scene state, or narrowing AppKit escapes.

- Path: `plugins/build-macos-apps/skills/view-refactor/SKILL.md`

### `window-management`

Customize macOS SwiftUI windows and scene behavior. Use when tuning window chrome, drag regions, placement, restoration, launch behavior, or borderless windows.

- Path: `plugins/build-macos-apps/skills/window-management/SKILL.md`

## build-web-apps

6 skill(s)

### `frontend-app-builder`

Use for new frontend applications, dashboards, games, creative websites, hero sections, and visually driven UI from scratch, or when the user explicitly asks for a redesign/restyle/modernization. Builds from clean, airy, high-taste, readable image-generated concept design with section-specific references, faithful implementation, and browser testing.

- Path: `plugins/build-web-apps/skills/frontend-app-builder/SKILL.md`

### `frontend-testing-debugging`

Use when testing, debugging, or making targeted improvements to rendered frontend apps through the Build Web Apps or web dev plugin: local dev servers, UI regressions, interaction bugs, console errors, responsive layout, and visual QA. Check whether the Browser plugin is available and use it first when it is; otherwise use regular Playwright with the recorded reason.

- Path: `plugins/build-web-apps/skills/frontend-testing-debugging/SKILL.md`

### `react-best-practices`

React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.

- Path: `plugins/build-web-apps/skills/react-best-practices/SKILL.md`

### `shadcn`

Manages shadcn components and projects — adding, searching, fixing, debugging, styling, and composing UI. Provides project context, component docs, and usage examples. Applies when working with shadcn/ui, component registries, presets, --preset codes, or any project with a components.json file. Also triggers for "shadcn init", "create an app with --preset", or "switch to --preset".

- Path: `plugins/build-web-apps/skills/shadcn-best-practices/SKILL.md`

### `stripe-best-practices`

Guides Stripe integration decisions — API selection (Checkout Sessions vs PaymentIntents), Connect platform setup (Accounts v2, controller properties), billing/subscriptions, Treasury financial accounts, integration surfaces (Checkout, Payment Element), and migrating from deprecated Stripe APIs. Use when building, modifying, or reviewing any Stripe integration — including accepting payments, building marketplaces, integrating Stripe, processing payments, setting up subscriptions, or creating connected accounts.

- Path: `plugins/build-web-apps/skills/stripe-best-practices/SKILL.md`

### `supabase-postgres-best-practices`

Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations.

- Path: `plugins/build-web-apps/skills/supabase-best-practices/SKILL.md`

## build-web-data-visualization

18 skill(s)

### `accessibility-and-inclusive-visualization`

Make data visualizations accessible and inclusive. Use when the user needs chart or diagram accessibility guidance, text alternatives for complex visuals, color and contrast review, keyboard support, reduced-motion behavior for animation or parallax, or an accessibility QA workflow for exported figures, UML-like diagrams, and dashboards.

- Path: `plugins/build-web-data-visualization/skills/accessibility-and-inclusive-visualization/SKILL.md`

### `canvas2d-data-visualization`

Render data visualizations with Canvas2D. Use when the visualization needs high mark counts, fast redraws, immediate-mode rendering, custom hit testing, or a hybrid Canvas plus SVG or HTML architecture.

- Path: `plugins/build-web-data-visualization/skills/canvas2d-data-visualization/SKILL.md`

### `d3-data-visualization`

Build custom data visualizations with D3. Use when the user needs SVG or DOM-based charts, rich annotation, domain-native contextual backgrounds, data joins, custom scales or interactions, scroll-driven SVG scene states, or precise control over browser visualization behavior.

- Path: `plugins/build-web-data-visualization/skills/d3-data-visualization/SKILL.md`

### `dashboards-and-real-time-visualization`

Design dashboards and live visualization systems. Use when the user needs monitoring views, streaming charts, coordinated interactions, downsampling, or performance-aware operational visualization.

- Path: `plugins/build-web-data-visualization/skills/dashboards-and-real-time-visualization/SKILL.md`

### `data-visualization`

Route web data visualization work. Use when the user needs chart choice, visual critique, dashboards, maps or geospatial views, Gantt timelines, UML/software diagrams, scrollytelling, reports or exports, testing, accessibility, browser implementation, or concept-first visual design.

- Path: `plugins/build-web-data-visualization/skills/data-visualization/SKILL.md`

### `gantt-chart-visualization`

Design, critique, route, and implement Gantt charts and schedule visualizations. Use when the user mentions Gantt charts, project schedules, roadmaps with task spans, milestones, dependencies, predecessors, critical path, baselines, WBS, resource plans, capacity timelines, MS Project, Primavera P6, Jira Advanced Roadmaps, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps iterations, or importing/exporting project-management data for a timeline chart.

- Path: `plugins/build-web-data-visualization/skills/gantt-chart-visualization/SKILL.md`

### `geospatial-and-cartographic-visualization`

Design geospatial and cartographic visualizations. Use when the user needs help deciding whether to use a map, choosing projections or basemaps, building choropleths or symbol maps, or implementing thematic maps, slippy maps, or geospatial interactions with D3 geo, Leaflet, MapLibre, Mapbox GL JS, Google Maps, OpenLayers, deck.gl, ArcGIS Maps SDK, Azure Maps, HERE Maps, CesiumJS, or related tools.

- Path: `plugins/build-web-data-visualization/skills/geospatial-and-cartographic-visualization/SKILL.md`

### `grammar-of-graphics-and-declarative-visualization`

Build data visualizations with declarative grammars. Use when the user needs Vega-Lite, Vega, Observable Plot, or grammar-of-graphics reasoning, especially for tabular charts that do not require bespoke rendering.

- Path: `plugins/build-web-data-visualization/skills/grammar-of-graphics-and-declarative-visualization/SKILL.md`

### `node-link-and-diagram-layout`

Choose and apply automatic layout strategies for node-link diagrams and connected-node visuals. Use when the user asks how to auto-arrange nodes, reduce line crossings, route edges, avoid overlaps, stabilize layout, or choose graph-layout algorithms for network diagrams, dependency graphs, database schema diagrams, ERDs, state machines, decision trees, flow diagrams, box-and-line editors, or other line-connected nodes.

- Path: `plugins/build-web-data-visualization/skills/node-link-and-diagram-layout/SKILL.md`

### `react-and-nextjs-data-visualization`

Integrate data visualizations into React and Next.js applications. Use when the user needs chart components, UML-like or architecture diagram components, React integration patterns, Next.js client or server boundaries, hydration-safe rendering, lazy loading, framework-aware performance, scroll-driven visual stories, or export guidance.

- Path: `plugins/build-web-data-visualization/skills/react-and-nextjs-data-visualization/SKILL.md`

### `reports-pdfs-and-slide-automation`

Lay out and export data-rich reports and documents. Use when the user needs report structure, figure packaging, PDFs, PowerPoint or Google Slides automation, or programmatic insertion of visualizations, UML-like diagrams, or architecture diagrams into documents.

- Path: `plugins/build-web-data-visualization/skills/reports-pdfs-and-slide-automation/SKILL.md`

### `scrollytelling-and-parallax-data-visualization`

Design and implement parallax scrolling and scrollytelling data visualizations. Use when the user asks for parallax scrolling, scrollytelling, scroll-driven timelines, sticky graphics, Scrollama, ScrollTrigger, ScrollTimeline, view timelines, rich-media timelines, moviescrollers, scroll-scrubbed charts, staged narrative reveals, or interactive visual stories where scrolling changes a data visualization or media scene.

- Path: `plugins/build-web-data-visualization/skills/scrollytelling-and-parallax-data-visualization/SKILL.md`

### `statistical-and-uncertainty-visualization`

Design statistically honest and uncertainty-aware visualizations. Use when the user needs help showing distributions, intervals, confidence, missingness, sampling effects, or analytical rigor in charts and dashboards.

- Path: `plugins/build-web-data-visualization/skills/statistical-and-uncertainty-visualization/SKILL.md`

### `testing-data-visualizations`

Test data visualizations and dashboards. Use when the user needs chart or diagram test strategy, screenshot or image diff testing, visual regression, mocked or synthetic chart data, component or unit tests, E2E dashboard QA, interactive UML-like diagram verification, scroll-driven story verification, export verification, or guidance on avoiding brittle over-testing.

- Path: `plugins/build-web-data-visualization/skills/testing-data-visualizations/SKILL.md`

### `threejs-data-visualization`

Render WebGL-accelerated data visualizations with Three.js, raw WebGL, deck.gl, luma.gl, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, CesiumJS, Babylon.js, or related GPU libraries. Use when the visualization needs true spatial structure, dense 2D or 3D GPU rendering, particle or flow animation, volumetric views, or interactive exploration that adds real analytical value.

- Path: `plugins/build-web-data-visualization/skills/threejs-data-visualization/SKILL.md`

### `typescript-data-visualization-engineering`

Build typed data visualizations in TypeScript. Use when the user wants TypeScript visualization code, typed data models, browser visualization components, UML-like diagram models, interactive graph or architecture diagram contracts, scroll-driven scene contracts, library selection guidance, or a maintainable visualization architecture beyond React- or Next-specific concerns.

- Path: `plugins/build-web-data-visualization/skills/typescript-data-visualization-engineering/SKILL.md`

### `uml-and-software-architecture-visualization`

Design, critique, read, write, render, and implement UML and UML-like software diagrams. Use when the user mentions UML, sequence diagrams, class diagrams, activity diagrams, state machines, use case diagrams, component diagrams, deployment diagrams, object diagrams, package diagrams, profile diagrams, timing diagrams, communication diagrams, interaction overview diagrams, composite structure diagrams, ERDs, database schema diagrams, C4, BPMN, swimlanes, flowcharts, network diagrams, application architecture diagrams, software architecture diagrams, diagram-as-code, model-as-code, XMI, UMLDI, PlantUML, Mermaid, Graphviz DOT, D2, Structurizr, DBML, diagrams.net/draw.io, Kroki, or interactive diagram editors and explorers.

- Path: `plugins/build-web-data-visualization/skills/uml-and-software-architecture-visualization/SKILL.md`

### `visualization-strategy-and-critique`

Choose, lay out, critique, and explain data visualizations. Use when the user asks what visualization fits a dataset or goal, how a chart, dashboard, operational workspace, UML-like diagram, or software architecture diagram should be composed or interacted with, asks for visual page design, a layout mockup, generated large-screen and mobile concept images, or to be shown what a visualization could look like, when domain-native contextual surfaces or graphical backgrounds may help, when scrollytelling or parallax might be appropriate, wants a critique of an existing visualization, or needs guidance grounded in trusted visualization theory and practice. For advanced visual design or page-layout prompts where composition affects understanding, Codex must generate and show both large-screen and mobile portrait image concepts before implementation or text-only design handoff, plus mobile landscape when needed.

- Path: `plugins/build-web-data-visualization/skills/visualization-strategy-and-critique/SKILL.md`

## canva

8 skill(s)

### `canva-brand-check`

Check a Canva design against a brand kit and report where it diverges — off-palette colors, non-brand fonts, logo misuse, and off-tone copy. Read-only; makes no changes. Use when the user asks "is this on brand", "check this against our brand kit", "do a brand review", "does this match our brand guidelines", or "brand-check my design".

- Path: `plugins/canva/skills/canva-brand-check/SKILL.md`

### `canva-branded-presentation`

Create on-brand Canva presentations from an outline or brief. Use when the user asks to create a branded presentation, make an on-brand deck, turn an outline into slides, or generate a presentation from a brief. Input can be text directly in the message, a Canva design ID, a reference to a Canva doc by name, or a Canva design link (e.g., https://www.canva.com/design/...).

- Path: `plugins/canva/skills/canva-branded-presentation/SKILL.md`

### `canva-bulk-create`

Bulk-create Canva designs from tabular data using a brand template with autofill fields, producing one design per row. Use when users say "bulk create designs from this CSV", "generate one design per row", "create a design for each product", "batch generate from a template", or "autofill a template from a spreadsheet". Accepts any tabular data source — uploaded files, pasted tables, JSON, or URLs.

- Path: `plugins/canva/skills/canva-bulk-create/SKILL.md`

### `canva-design-feedback`

Read a Canva design and return structured, actionable design feedback — visual hierarchy, copy/messaging, layout & spacing, consistency, readability, and accessibility. Read-only; makes no changes to the design. Use when the user asks to "review my design", "give me feedback on this", "critique my deck/poster/flyer", "how can I improve this design", or "what's wrong with this slide".

- Path: `plugins/canva/skills/canva-design-feedback/SKILL.md`

### `canva-edit-design`

Make edits to an existing Canva design — change or fix text, replace/insert/delete images and videos, reformat text (size, weight, style, color, alignment, lists, line height), reposition or resize elements, and update the title. Use when the user wants to change, edit, update, fix, translate, replace, or reformat content in a specific Canva design. This is the safe edit engine that other Canva skills (e.g. implement-feedback) build on.

- Path: `plugins/canva/skills/canva-edit-design/SKILL.md`

### `canva-implement-feedback`

Implement reviewer feedback on a Canva design. Reads all comment threads, synthesises what reviewers want, makes the clear-cut changes directly, and flags anything that needs a human decision. Use when the user asks to "implement feedback on my deck", "address comments on a design", "apply review feedback", "fix the comments on my presentation", or "implement the feedback".

- Path: `plugins/canva/skills/canva-implement-feedback/SKILL.md`

### `canva-resize-for-social-media`

Resize a Canva design into multiple social media formats (Facebook post, Facebook story, Instagram post, Instagram story, LinkedIn post). Use this skill when users want to resize Canva designs specifically for multiple social media platforms in one operation, rather than resizing to a single format manually.

- Path: `plugins/canva/skills/canva-resize-for-social-media/SKILL.md`

### `canva-translate-design`

Translate all text in a Canva design to another language, creating a translated copy. Faster than manually copying and editing each text box in Canva's editor. Use when users say "translate my design to [language]", "make a Spanish/French/etc version", or "localize my Canva design".

- Path: `plugins/canva/skills/canva-translate-design/SKILL.md`

## chatcut

1 skill(s)

### `connect-chatcut-desktop`

Install, open, connect, or repair ChatCut Desktop when the chatcut_desktop MCP tools are missing or unavailable. Do not use from a managed agent already running inside ChatCut Desktop, or when chatcut_desktop tools are already available.

- Path: `plugins/chatcut/skills/connect-chatcut-desktop/SKILL.md`

## circleci

4 skill(s)

### `chunk`

Use CircleCI Chunk for AI-assisted CI/CD work through either the Chunk web UI or the chunk-cli. Trigger this skill when users ask to set up Chunk, troubleshoot or fix failing builds with Chunk, configure Chunk environments, schedule/proactively run Chunk tasks, or use chunk-cli commands such as init, validate, build-prompt, auth, sandbox, task, and skill install.

- Path: `plugins/circleci/skills/chunk/SKILL.md`

### `circleci-builds`

Diagnose and fix failing CircleCI builds quickly and safely. Use when users ask to investigate failed CircleCI jobs, triage flaky pipelines, identify root causes from logs, and implement minimal fixes in configuration, test setup, or build-related code paths.

- Path: `plugins/circleci/skills/builds/SKILL.md`

### `circleci-cli`

Operate and troubleshoot CircleCI using the CircleCI CLI. Use when users ask to authenticate CLI access, inspect pipeline/workflow/job status, validate configuration locally, rerun pipelines/jobs, trigger pipelines, or gather actionable diagnostics from CLI outputs.

- Path: `plugins/circleci/skills/cli/SKILL.md`

### `circleci-config`

Optimize CircleCI configuration for speed, reliability, and maintainability. Use when users ask to improve `.circleci/config.yml`, reduce CI runtime, tune caching/workspaces/parallelism, remove pipeline waste, or fix flaky pipeline behavior caused by configuration choices.

- Path: `plugins/circleci/skills/config/SKILL.md`

## cloudflare

9 skill(s)

### `agents-sdk`

Build AI agents on Cloudflare Workers using the Agents SDK. Load when creating stateful agents, durable workflows, real-time WebSocket apps, scheduled tasks, MCP servers, or chat applications. Covers Agent class, state management, callable RPC, Workflows integration, and React hooks. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/agents-sdk/SKILL.md`

### `building-ai-agent-on-cloudflare`

Builds AI agents on Cloudflare using the Agents SDK with state management, real-time WebSockets, scheduled tasks, tool integration, and chat capabilities. Generates production-ready agent code deployed to Workers.

- Path: `plugins/cloudflare/skills/building-ai-agent-on-cloudflare/SKILL.md`

### `building-mcp-server-on-cloudflare`

Builds remote MCP (Model Context Protocol) servers on Cloudflare Workers with tools, OAuth authentication, and production deployment. Generates server code, configures auth providers, and deploys to Workers.

- Path: `plugins/cloudflare/skills/building-mcp-server-on-cloudflare/SKILL.md`

### `cloudflare`

Comprehensive Cloudflare platform skill covering Workers, Pages, storage (KV, D1, R2), AI (Workers AI, Vectorize, Agents SDK), networking (Tunnel, Spectrum), security (WAF, DDoS), and infrastructure-as-code (Terraform, Pulumi). Use for any Cloudflare development task. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/cloudflare/SKILL.md`

### `durable-objects`

Create and review Cloudflare Durable Objects. Use when building stateful coordination (chat rooms, multiplayer games, booking systems), implementing RPC methods, SQLite storage, alarms, WebSockets, or reviewing DO code for best practices. Covers Workers integration, wrangler config, and testing with Vitest. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/durable-objects/SKILL.md`

### `sandbox-sdk`

Build sandboxed applications for secure code execution. Load when building AI code execution, code interpreters, CI/CD systems, interactive dev environments, or executing untrusted code. Covers Sandbox SDK lifecycle, commands, files, code interpreter, and preview URLs. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/sandbox-sdk/SKILL.md`

### `web-perf`

Analyzes web performance using Chrome DevTools MCP. Measures Core Web Vitals (FCP, LCP, TBT, CLS, Speed Index), identifies render-blocking resources, network dependency chains, layout shifts, caching issues, and accessibility gaps. Use when asked to audit, profile, debug, or optimize page load performance, Lighthouse scores, or site speed. Biases towards retrieval from current documentation over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/web-perf/SKILL.md`

### `workers-best-practices`

Reviews and authors Cloudflare Workers code against production best practices. Load when writing new Workers, reviewing Worker code, configuring wrangler.jsonc, or checking for common Workers anti-patterns (streaming, floating promises, global state, secrets, bindings, observability). Biases towards retrieval from Cloudflare docs over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/workers-best-practices/SKILL.md`

### `wrangler`

Cloudflare Workers CLI for deploying, developing, and managing Workers, KV, R2, D1, Vectorize, Hyperdrive, Workers AI, Containers, Queues, Workflows, Pipelines, and Secrets Store. Load before running wrangler commands to ensure correct syntax and best practices. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.

- Path: `plugins/cloudflare/skills/wrangler/SKILL.md`

## coderabbit

1 skill(s)

### `code-review`

Reviews code changes using CodeRabbit AI. Use when user asks for code review, PR feedback, code quality checks, security issues, or requests fix-review cycles.

- Path: `plugins/coderabbit/skills/coderabbit-review/SKILL.md`

## codex-security

15 skill(s)

### `assess-patch-risk`

Assess an immutable patch artifact's program impact, regression risk, and auto-merge eligibility. Use for generated patch files, provider pull-request diffs, or commit ranges when reviewers need evidence about affected runtime paths, contracts, tests, and recoverability. This skill is read-only and does not generate, edit, apply, push, or merge the patch.

- Path: `plugins/codex-security/skills/assess-patch-risk/SKILL.md`

### `attack-path-analysis`

Use when Codex is already in the attack-path-analysis phase of a security scan or the user explicitly asks to trace a security finding from source to sink and calibrate severity. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.

- Path: `plugins/codex-security/skills/attack-path-analysis/SKILL.md`

### `deep-security-scan`

Use when the user asks for a deep, exhaustive, multi-pass, or variance-reducing repository-wide or scoped-path Codex Security scan. Run repeated complete independent Standard scans with the Codex Security deep-scan tool, which aggregates their validated findings and prepares the canonical artifacts; then complete the same scan once. Do not use for PRs, commits, branch diffs, or working-tree diffs.

- Path: `plugins/codex-security/skills/deep-security-scan/SKILL.md`

### `define-security-policy`

Define, review, or update SECURITY.md guidance for a repository or component. Use when the user wants to clarify what Codex Security should review, what is out of scope, which security properties must hold, or whether existing guidance still matches the code.

- Path: `plugins/codex-security/skills/define-security-policy/SKILL.md`

### `finding-discovery`

Use when Codex is already in the finding-discovery phase of a security scan or the user explicitly asks to discover candidate security findings in a repository or code change. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.

- Path: `plugins/codex-security/skills/finding-discovery/SKILL.md`

### `fix-finding`

Use only when the user explicitly asks to fix and verify a validated or plausible security vulnerability. Do not use for ordinary bug fixes, correctness or design review findings, general validation, or full PR, commit, branch, patch, or repository scans.

- Path: `plugins/codex-security/skills/fix-finding/SKILL.md`

### `propose-security-hardening`

Develop evidence-backed structural and architectural security hardening proposals from vulnerability disclosures, supplied findings, incident or assessment documents, source code, or a completed Codex Security scan. Use when a user asks for systemic improvements, alternatives beyond per-finding patches, before-and-after security architecture views, engineering tradeoff analysis, or an implementation-ready plan for a selected hardening option. Also use automatically after a Codex Security scan with reportable findings when the top-level scan workflow requests final-report hardening guidance.

- Path: `plugins/codex-security/skills/propose-security-hardening/SKILL.md`

### `security-diff-scan`

Review a pull request, commit, branch diff, or working-tree patch for security vulnerabilities.

- Path: `plugins/codex-security/skills/security-diff-scan/SKILL.md`

### `security-scan`

Use for a standard, single-pass security audit of an entire repository or a scoped path, package, folder, or submodule with no diff to review. This is the default repository scan. Do not use for PR, commit, branch, or working-tree diffs, or for deep, multi-pass scans.

- Path: `plugins/codex-security/skills/security-scan/SKILL.md`

### `threat-model`

Use when Codex is already in the threat-modeling phase of a security scan, the user explicitly invokes $threat-model, or the user explicitly asks to create, update, or persist a repository threat model. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.

- Path: `plugins/codex-security/skills/threat-model/SKILL.md`

### `track-findings`

Track validated Codex Security findings in Linear, Jira, GitHub issues, or draft GitHub security advisories. Supports issue batches, duplicate checks, and reviewed writes. Do not use for scans or fixes.

- Path: `plugins/codex-security/skills/track-findings/SKILL.md`

### `triage-finding`

Triage supplied or imported security findings against a repository using its security policy and static code evidence. Accepts scanner reports, advisories, GitHub findings, and Jira or Linear tickets. Do not use for discovery, duplicate triage, runtime validation, or fixes.

- Path: `plugins/codex-security/skills/triage-finding/SKILL.md`

### `validation`

Use when Codex is already in the validation phase of a security scan or the user explicitly asks to determine whether one or more candidate security findings are valid. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.

- Path: `plugins/codex-security/skills/validation/SKILL.md`

### `verify-fix`

Use only when the user explicitly requests verification that a security fix remediates a reported vulnerability. Do not invoke automatically while implementing fixes, reviewing ordinary code changes, or running tests. Do not use for non-security fixes, candidate finding validation, or full repository scans.

- Path: `plugins/codex-security/skills/verify-fix/SKILL.md`

### `vulnerability-writeup`

Turn vulnerability notes, disclosure reports, PoCs, source code, or Codex Security findings into self-contained, sceptically validated, natural-sounding vulnerability reports. Use for one vulnerability or a disclosure campaign; a Codex Security scan is optional.

- Path: `plugins/codex-security/skills/vulnerability-writeup/SKILL.md`

## creative-production

2 skill(s)

### `intake`

Use when Creative Production is explicitly invoked or mentioned without a concrete request, when the user asks what Creative Production can do, or when the user wants help getting started without enough context to choose a workflow.

- Path: `plugins/creative-production/skills/intake/SKILL.md`

### `produce`

Use when the user wants to create, explore, adapt, refine, polish, or review visual creative such as campaigns, ads, social posts, product imagery, scenes, offers, logos, brand systems, styles, charts, decks, or related marketing and design assets.

- Path: `plugins/creative-production/skills/produce/SKILL.md`

## data-analytics

18 skill(s)

### `analyze-data-quality`

Assess whether structured data, query results, dashboards, or analytical evidence are trustworthy enough to use. Use when the task is to check data quality, reconcile conflicting sources or metric definitions, or decide whether evidence is safe to cite.

- Path: `plugins/data-analytics/skills/analyze-data-quality/SKILL.md`

### `build-dashboard`

Build source-backed dashboards for monitoring performance, exploring drivers, or acting on product and business metrics. Use when the task needs a dashboard, scorecard, or monitoring view with clear metrics, filters, source definitions, and QA.

- Path: `plugins/data-analytics/skills/build-dashboard/SKILL.md`

### `build-report`

Build polished analytical reports for executive, product, business, or technical audiences. Use when the task needs a durable answer-first narrative with evidence-backed findings, visuals or tables, caveats, and source context.

- Path: `plugins/data-analytics/skills/build-report/SKILL.md`

### `create-data-context`

Create, update, inspect, or repair Data Analytics semantic layers. Use when the user asks to save data context or create a semantic layer that future Data Analytics work can inspect and cite.

- Path: `plugins/data-analytics/skills/create-data-context/SKILL.md`

### `design-kpis`

Design KPI frameworks, metric definitions, targets, guardrails, and measurement plans for product or business decisions. Use when success metrics, drivers, guardrails, targets, or the measurement approach need to be defined or improved.

- Path: `plugins/data-analytics/skills/design-kpis/SKILL.md`

### `gather-business-context`

Gather business context from connected or provided sources so downstream analysis starts with the right framing. Use when an analytical question depends on missing context, such as what a metric means, what changed recently, or which sources should be checked. If the same prompt asks for diagnosis, recommendation, or a deliverable, gather context first and continue to the focused skill.

- Path: `plugins/data-analytics/skills/gather-business-context/SKILL.md`

### `index`

Route Data Analytics plugin-level requests and broad analytics work to the right focused workflow. Use when Data Analytics is at-mentioned, or for analytics requests involving data, metrics, dashboards, reports, charts, notebooks, spreadsheets, KPIs, market sizing, or semantic layers.

- Path: `plugins/data-analytics/skills/index/SKILL.md`

### `jupyter-notebooks`

Create, edit, or validate reproducible SQL or Python notebooks. Use for notebooks, SQL/Python scratchpads, reproducible exploration, audit trails, or runnable companions where the analysis should be reviewable or rerunnable.

- Path: `plugins/data-analytics/skills/jupyter-notebooks/SKILL.md`

### `kpi-reporting`

Prepare KPI readouts, scorecards, WBR/MBR/QBR updates, and executive summaries from quantitative business or product metrics; use when the task is to report status, compare against targets, explain validated drivers, and state operating implications.

- Path: `plugins/data-analytics/skills/kpi-reporting/SKILL.md`

### `market-sizing`

Estimate market, segment, or opportunity size with transparent assumptions and uncertainty. Use for TAM/SAM/SOM, sizing scenarios, or comparing the scale of possible opportunities.

- Path: `plugins/data-analytics/skills/market-sizing/SKILL.md`

### `metric-diagnostics`

Diagnose why a metric changed or differs from expectation. Use when the task is to identify likely drivers of a metric movement, anomaly, gap, or discrepancy.

- Path: `plugins/data-analytics/skills/metric-diagnostics/SKILL.md`

### `product-business-analysis`

Analyze product or business data to support a decision or recommendation. Use when a decision depends on metric-backed evidence, such as choosing a direction, prioritizing an opportunity, evaluating a change, segmenting users, sizing tradeoffs, or deciding what to do next.

- Path: `plugins/data-analytics/skills/product-business-analysis/SKILL.md`

### `publish-artifact-to-sites`

Publish a validated Data Analytics report or dashboard artifact through Sites. Use automatically for durable artifacts in any positively identified Work Mode when the full Sites lifecycle is callable, or in ChatGPT Desktop outside Work Mode only after an explicit Sites request or acceptance of the optional post-handoff sharing offer.

- Path: `plugins/data-analytics/skills/publish-artifact-to-sites/SKILL.md`

### `report-to-google-doc`

Narrow conversion skill. Invoke only when the user explicitly asks to convert an existing local or blob-hosted HTML analytics report into a Google Doc, DOCX, or shareable document.

- Path: `plugins/data-analytics/skills/build-report/report-to-google-doc/SKILL.md`

### `report-to-google-slides`

Narrow conversion skill. Invoke only when the user explicitly asks to convert an existing HTML analytics report into a native Google Slides deck.

- Path: `plugins/data-analytics/skills/build-report/report-to-google-slides/SKILL.md`

### `report-to-pdf`

Narrow conversion skill. Invoke only when the user explicitly asks to convert an existing Data Analytics report, dashboard, or inline chart export into a PDF artifact.

- Path: `plugins/data-analytics/skills/build-report/report-to-pdf/SKILL.md`

### `validate-data`

Validate whether an analysis is accurate, well-supported, and ready to share or use for a decision. Use when reviewing methodology, calculations, comparisons, visuals, caveats, or conclusions.

- Path: `plugins/data-analytics/skills/validate-data/SKILL.md`

### `visualize-data`

Design, build, revise, or QA quantitative charts and figures. Use when an analytical answer needs visual judgment, whether for an inline answer, report, dashboard, notebook, or artifact.

- Path: `plugins/data-analytics/skills/visualize-data/SKILL.md`

## dropbox

6 skill(s)

### `clean-up-dropbox-content`

Clean up Dropbox content by identifying obsolete, duplicate, temporary, or unwanted files and deleting only after explicit review. Use when the user explicitly asks to delete, remove, or clean up Dropbox files or folders.

- Path: `plugins/dropbox/skills/clean-up-dropbox-content/SKILL.md`

### `collect-files-with-request`

Create, inspect, and manage Dropbox file requests for collecting uploads from other people. Use when the user asks to collect files, request uploads, create an upload portal, check a file request, or list existing file requests.

- Path: `plugins/dropbox/skills/collect-files-with-request/SKILL.md`

### `find-dropbox-content`

Find Dropbox files and folders relevant to a user request. Use when the user asks to search Dropbox, find a document, locate recent files, browse a folder, identify likely source files, or narrow down where content lives before reading, sharing, organizing, or restoring it.

- Path: `plugins/dropbox/skills/find-dropbox-content/SKILL.md`

### `inspect-dropbox-file`

Inspect a Dropbox file or folder by checking metadata, shared links, and file content when needed. Use when the user asks what a file is, whether it is shared, when it changed, what access links exist, or asks to read/analyze a Dropbox file.

- Path: `plugins/dropbox/skills/inspect-dropbox-file/SKILL.md`

### `organize-dropbox-folder`

Organize Dropbox files and folders by creating folders, copying content, or moving content into a cleaner structure. Use when the user asks to organize, archive, consolidate, restructure, copy, or move Dropbox content.

- Path: `plugins/dropbox/skills/organize-dropbox-folder/SKILL.md`

### `share-dropbox-content`

Share Dropbox files or folders by creating shared links, inspecting existing shared links, or explaining current shared-link state. Use only when the user explicitly asks to create a shared link, check access, or inspect a Dropbox shared link.

- Path: `plugins/dropbox/skills/share-dropbox-content/SKILL.md`

## expo

13 skill(s)

### `building-native-ui`

Complete guide for building beautiful apps with Expo Router. Covers fundamentals, styling, components, navigation, animations, patterns, and native tabs.

- Path: `plugins/expo/skills/building-native-ui/SKILL.md`

### `codex-expo-run-actions`

Wire Expo projects into the Codex app with project-local run scripts and .codex/environments/environment.toml actions. Use when the user wants the Codex app Run button, build/run actions, action buttons, or a stable Expo start/run workflow from Codex.

- Path: `plugins/expo/skills/codex-expo-run-actions/SKILL.md`

### `expo-api-routes`

Guidelines for creating API routes in Expo Router with EAS Hosting

- Path: `plugins/expo/skills/expo-api-routes/SKILL.md`

### `expo-cicd-workflows`

Helps understand and write EAS workflow YAML files for Expo projects. Use this skill when the user asks about CI/CD or workflows in an Expo or EAS context, mentions .eas/workflows/, or wants help with EAS build pipelines or deployment automation.

- Path: `plugins/expo/skills/expo-cicd-workflows/SKILL.md`

### `expo-deployment`

Deploying Expo apps to iOS App Store, Android Play Store, web hosting, and API routes

- Path: `plugins/expo/skills/expo-deployment/SKILL.md`

### `expo-dev-client`

Build and distribute Expo development clients locally or via TestFlight

- Path: `plugins/expo/skills/expo-dev-client/SKILL.md`

### `expo-module`

Guide for writing Expo native modules and views using the Expo Modules API (Swift, Kotlin, TypeScript). Covers module definition DSL, native views, shared objects, config plugins, lifecycle hooks, autolinking, and type system. Use when building or modifying native modules for Expo.

- Path: `plugins/expo/skills/expo-module/SKILL.md`

### `expo-tailwind-setup`

Set up Tailwind CSS v4 in Expo with react-native-css and NativeWind v5 for universal styling

- Path: `plugins/expo/skills/expo-tailwind-setup/SKILL.md`

### `expo-ui-jetpack-compose`

`@expo/ui/jetpack-compose` package lets you use Jetpack Compose Views and modifiers in your app.

- Path: `plugins/expo/skills/expo-ui-jetpack-compose/SKILL.md`

### `expo-ui-swift-ui`

`@expo/ui/swift-ui` package lets you use SwiftUI Views and modifiers in your app.

- Path: `plugins/expo/skills/expo-ui-swift-ui/SKILL.md`

### `native-data-fetching`

Use when implementing or debugging ANY network request, API call, or data fetching. Covers fetch API, React Query, SWR, error handling, caching, offline support, and Expo Router data loaders (`useLoaderData`).

- Path: `plugins/expo/skills/native-data-fetching/SKILL.md`

### `upgrading-expo`

Guidelines for upgrading Expo SDK versions and fixing dependency issues

- Path: `plugins/expo/skills/upgrading-expo/SKILL.md`

### `use-dom`

Use Expo DOM components to run web code in a webview on native and as-is on web. Migrate web code to native incrementally.

- Path: `plugins/expo/skills/use-dom/SKILL.md`

## figma

12 skill(s)

### `figma-code-connect`

Creates and maintains Figma Code Connect template files that map Figma components to code snippets. Use when the user mentions Code Connect, Figma component mapping, design-to-code translation, or asks to create/update .figma.ts or .figma.js files.

- Path: `plugins/figma/skills/figma-code-connect/SKILL.md`

### `figma-create-new-file`

**MANDATORY prerequisite** — you MUST invoke this skill BEFORE every `create_new_file` tool call. NEVER call `create_new_file` directly without loading this skill first. Trigger whenever the user wants a new blank Figma file — a new design, FigJam, or Slides file — or when you need a fresh file before calling `use_figma`. Usage — /figma-create-new-file [editorType] [fileName] (e.g. /figma-create-new-file figjam My Whiteboard, /figma-create-new-file slides Q3 Review)

- Path: `plugins/figma/skills/figma-create-new-file/SKILL.md`

### `figma-design-to-code`

**MANDATORY prerequisite** — you MUST invoke this skill BEFORE calling the `get_design_context` Figma MCP tool. You MUST trigger this skill whenever the user wants to implement, build, port, or code up a Figma design as code. Example prompts (not exhaustive) are 'implement this Figma design', 'build this screen from Figma', 'turn this Figma into code', 'design to code'. This skill provides critical instructions and steps to the agent on how to correctly implement Figma designs in code and must NOT be skipped.

- Path: `plugins/figma/skills/figma-design-to-code/SKILL.md`

### `figma-generate-design`

Use this skill alongside figma-use when the task involves translating an application page, view, or multi-section layout into Figma. Triggers: 'write to Figma', 'create in Figma from code', 'push page to Figma', 'take this app/page and build it in Figma', 'create a screen', 'build a landing page in Figma', 'update the Figma screen to match code', 'convert this modal/dialog/drawer/panel to Figma'. This is the preferred workflow skill whenever the user wants to build or update a full page, modal, dialog, drawer, sidebar, panel, or any composed multi-section view in Figma from code or a description. Discovers design system components, variables, and styles from Code Connect files, existing screens, and library search, then imports them and assembles views incrementally section-by-section using design system tokens instead of hardcoded values.

- Path: `plugins/figma/skills/figma-generate-design/SKILL.md`

### `figma-generate-diagram`

MANDATORY prerequisite — load this skill BEFORE every `generate_diagram` tool call. NEVER call `generate_diagram` directly without loading this skill first. Trigger whenever the user asks to create, generate, draw, render, sketch, or build a diagram — flowchart, architecture diagram, sequence diagram, ERD or entity-relationship diagram, state diagram or state machine, gantt chart, or timeline. Also trigger when the user mentions Mermaid syntax or wants a system architecture, decision tree, dependency graph, API call flow, auth handshake, schema, or pipeline visualized in FigJam. Routes to type-specific guidance, sets universal Mermaid constraints, and tells you when to use a different diagram type or skip the tool entirely (mindmaps, pie charts, class diagrams, etc.).

- Path: `plugins/figma/skills/figma-generate-diagram/SKILL.md`

### `figma-generate-library`

Build or update a professional-grade design system in Figma from a codebase. Use when the user wants to create variables/tokens, build component libraries, create individual components with proper variant sets and variable bindings, set up theming (light/dark modes), document foundations, or reconcile gaps between code and Figma. Also use when the user asks to create or generate any component in Figma — even a single one — since components require proper variable foundations, variant states, and design token bindings to be production-quality. This skill teaches WHAT to build and in WHAT ORDER — it complements the `figma-use` skill which teaches HOW to call the Plugin API. Both skills should be loaded together.

- Path: `plugins/figma/skills/figma-generate-library/SKILL.md`

### `figma-implement-motion`

Translates Figma motion and animations into production-ready application code. Use when implementing animation/motion from a Figma design — user mentions "implement this motion", "add animation from Figma", "animate this component", provides a Figma URL whose node is animated, or when `get_design_context` returns motion data or instructs you to call `get_motion_context`.

- Path: `plugins/figma/skills/figma-implement-motion/SKILL.md`

### `figma-swiftui`

SwiftUI ↔ Figma translation. Use whenever the user mentions Swift, SwiftUI, iOS, iPhone, or iPad — in EITHER direction — translating a Figma design into SwiftUI (design → code), or pushing SwiftUI views / screens / tokens back into a Figma file (code → design). Triggers on phrases like 'implement this Figma design in SwiftUI', 'build this screen in Swift', 'push this SwiftUI view to Figma', 'mirror my Swift code in a Figma file', or whenever a Figma URL appears alongside `.swift` files / an `.xcodeproj`. Routes to a direction-specific reference doc; loads alongside `figma-use` for the code → design path.

- Path: `plugins/figma/skills/figma-swiftui/SKILL.md`

### `figma-use`

**MANDATORY prerequisite** — you MUST invoke this skill BEFORE every `use_figma` tool call. NEVER call `use_figma` directly without loading this skill first. Skipping it causes common, hard-to-debug failures. Trigger whenever the user wants to perform a write action or a unique read action that requires JavaScript execution in the Figma file context — e.g. create/edit/delete nodes, set up variables or tokens, build components and variants, modify auto-layout or fills, bind variables to properties, or inspect file structure programmatically.

- Path: `plugins/figma/skills/figma-use/SKILL.md`

### `figma-use-figjam`

This skill helps agents use Figma's use_figma MCP tool in the FigJam context. Can be used alongside figma-use which has foundational context for using the use_figma tool.

- Path: `plugins/figma/skills/figma-use-figjam/SKILL.md`

### `figma-use-motion`

Motion / animation context for the `use_figma` MCP tool — animating Figma nodes via manual keyframes, animation styles, easing, and timeline duration. Load alongside figma-use whenever a task involves adding, editing, or inspecting animation on a node.

- Path: `plugins/figma/skills/figma-use-motion/SKILL.md`

### `figma-use-slides`

This skill helps agents use Figma's use_figma MCP tool in the Slides context. Can be used alongside figma-use which has foundational context for using the use_figma tool.

- Path: `plugins/figma/skills/figma-use-slides/SKILL.md`

## game-studio

9 skill(s)

### `game-playtest`

Run browser-game playtests and frontend QA. Use when the user asks for smoke tests, screenshot-based verification, browser automation, HUD or overlay review, or structured issue-finding in a browser game.

- Path: `plugins/game-studio/skills/game-playtest/SKILL.md`

### `game-studio`

Route early browser-game work. Use when the user needs stack selection and workflow planning across design, implementation, assets, and playtesting before moving to a specialist skill.

- Path: `plugins/game-studio/skills/game-studio/SKILL.md`

### `game-ui-frontend`

Design UI surfaces for browser games. Use when the user asks for HUDs, menus, overlays, responsive layouts, or visual direction that must protect the playfield.

- Path: `plugins/game-studio/skills/game-ui-frontend/SKILL.md`

### `phaser-2d-game`

Implement 2D browser games with Phaser. Use when the user wants a Phaser, TypeScript, and Vite stack for scenes, gameplay systems, cameras, sprite animation, and DOM-overlay HUD patterns.

- Path: `plugins/game-studio/skills/phaser-2d-game/SKILL.md`

### `react-three-fiber-game`

Build React-hosted 3D browser games with React Three Fiber. Use when the user wants pmndrs-based scene composition, shared React state, and 3D HUD integration inside a React app.

- Path: `plugins/game-studio/skills/react-three-fiber-game/SKILL.md`

### `sprite-pipeline`

Generate and normalize 2D sprite animations. Use when the user asks for full-strip generation from approved source frames, consistent anchor and scale normalization, or preview assets for browser-game animation.

- Path: `plugins/game-studio/skills/sprite-pipeline/SKILL.md`

### `three-webgl-game`

Implement browser-game runtimes with plain Three.js. Use when the user wants imperative scene control in TypeScript or Vite with GLB assets, loaders, physics, and low-level WebGL debugging.

- Path: `plugins/game-studio/skills/three-webgl-game/SKILL.md`

### `web-3d-asset-pipeline`

Prepare and optimize browser-game 3D assets. Use when the user asks for GLB or glTF shipping work, including Blender cleanup and export, collision or LOD setup, compression, texture packaging, and runtime validation.

- Path: `plugins/game-studio/skills/web-3d-asset-pipeline/SKILL.md`

### `web-game-foundations`

Set browser-game architecture before implementation. Use when the user needs engine choice, simulation and render boundaries, input model, asset organization, or save/debug/performance strategy.

- Path: `plugins/game-studio/skills/web-game-foundations/SKILL.md`

## google-drive

5 skill(s)

### `google-docs`

Prompt- and template-complete Google Docs creation and editing with explicit-instruction-authoritative structural preservation, including semantic roles, relationships, comparison dimensions, and instructed extensions; full-topology native-copy routing; source-grounded per-tab adaptation for past/example references; style-preserving hyperlink and table edits; canonical smart-chip-first authoring for dates and relevant supported people or Google resources; a file-backed advisory trusted read before existing-document writes; automatic protected-control awareness; direct connector APIs by default; DOCX-first import only when no supplied Google Doc template/reference constrains the output; and checked-in code mode only for exact native dropdown mutation. Use when Codex must create, edit, fill, adapt, redesign, or verify Google Docs without overriding explicit user/template instructions, adding unrequested document scope, or carrying stale reference facts into a new deliverable.

- Path: `plugins/google-drive/skills/google-docs/SKILL.md`

### `google-drive`

Use connected Google Drive as the single entrypoint for Drive, Docs, Sheets, and Slides work. Use when the user wants to find, fetch, organize, share, export, copy, or delete Drive files, or summarize and edit Google Docs, Google Sheets, and Google Slides through one unified Google Drive plugin.

- Path: `plugins/google-drive/skills/google-drive/SKILL.md`

### `google-drive-comments`

Write, reply to, and resolve Google Drive comments on Docs, Sheets, Slides, and Drive files with evidence-backed location context. Use when the user asks to leave comments, review a file with comments, respond to comment threads, or resolve Drive comments.

- Path: `plugins/google-drive/skills/google-drive-comments/SKILL.md`

### `google-sheets`

Analyze and edit connected Google Sheets with range precision. Use when the user wants to create Google Sheets, find a spreadsheet, inspect tabs or ranges, search rows, plan formulas, create or repair charts, clean or restructure tables, write concise summaries, or make explicit cell-range updates.

- Path: `plugins/google-drive/skills/google-sheets/SKILL.md`

### `google-slides`

Route Google Slides authoring requests and derive a design system from a native template or reference deck. Use this skill when the user provides an existing native Google Slides deck as a template, reference, or prior-period source, or asks to edit, update, repair, restyle, or clean up an existing native Google Slides deck. Use the Presentations skill instead for net-new presentation creation when no existing native Google Slides deck must be followed.

- Path: `plugins/google-drive/skills/google-slides/SKILL.md`

## higgsfield

3 skill(s)

### `faceless-channel`

Use only when the user asks to produce a finished multi-scene narrator-led video and explicitly requests a faceless channel, YouTube automation, narrated explainer/story/education, documentary, storybook or myth retelling, or kids song video. Topic alone is never enough: a generic video of/about something, including a historical topic, uses ordinary video generation. Do not use for planning or ideas, single clips, silent animation, image-to-video, footage edits, ads, product demos, or UGC. This workflow requires a consistent non-photoreal style, reusable assets, narrator voiceover, and burned subtitles.

- Path: `plugins/higgsfield/skills/faceless-channel/SKILL.md`

### `narrator`

Activate when the user explicitly names the narrator skill or requests production-ready narration in either case: (1) numbered takes fitted to fixed video windows, or (2) one continuous long-form story read in a locked voice that must be measured and retried for timbre or internal pauses. Collect missing text, voice_id, or voice_type after activation; their absence is not a reason to skip this workflow. Own pacing, speech-duration gates, retries, and ready audio delivery; never time-stretch. Do not use for ordinary TTS, "read this aloud", an unconstrained voiceover, voice browsing, music, SFX, singing, dubbing existing speech, or voice cloning.

- Path: `plugins/higgsfield/skills/narrator/SKILL.md`

### `subtitles`

Burn timed subtitles onto a finished video or configure Whisper-timed caption burning during faceless-video assembly. Takes video/audio generation jobs or a local finished video, optionally with authored narration text, and returns a captioned video or the exact backend subtitle configuration. Timings always come from Whisper on the video's own audio — never estimated. THREE looks: `paper` (torn cream paper label, handwritten ink), `bold` (UGC ALL-CAPS, white with black stroke, platform safe zones), `clean` (slim white CAPS, no plate, tiny at the bottom — no Pillow needed). Use when: adding/burning subtitles or captions to an existing video, restyling captions, or when a production workflow needs its finished cut subtitled. NOT for: generating the video, translating speech, or live/soft subtitle tracks (this burns them into the picture).

- Path: `plugins/higgsfield/skills/subtitles/SKILL.md`

## hyperframes

5 skill(s)

### `gsap`

GSAP animation reference for HyperFrames. Covers gsap.to(), from(), fromTo(), easing, stagger, defaults, timelines (gsap.timeline(), position parameter, labels, nesting, playback), and performance (transforms, will-change, quickTo). Use when writing GSAP animations in HyperFrames compositions.

- Path: `plugins/hyperframes/skills/gsap/SKILL.md`

### `hyperframes`

Create video compositions, animations, title cards, overlays, captions, voiceovers, audio-reactive visuals, and scene transitions in HyperFrames HTML. Use when asked to build any HTML-based video content, add captions or subtitles synced to audio, generate text-to-speech narration, create audio-reactive animation (beat sync, glow, pulse driven by music), add animated text highlighting (marker sweeps, hand-drawn circles, burst lines, scribble, sketchout), or add transitions between scenes (crossfades, wipes, reveals, shader transitions). Covers composition authoring, timing, media, and the full video production workflow. For CLI commands (init, lint, preview, render, transcribe, tts) see the hyperframes-cli skill.

- Path: `plugins/hyperframes/skills/hyperframes/SKILL.md`

### `hyperframes-cli`

HyperFrames CLI tool — hyperframes init, lint, inspect, preview, render, transcribe, tts, doctor, browser, info, upgrade, compositions, docs, benchmark. Use when scaffolding a project, linting, validating, inspecting visual layout in compositions, previewing in the studio, rendering to video, transcribing audio, generating TTS, or troubleshooting the HyperFrames environment.

- Path: `plugins/hyperframes/skills/hyperframes-cli/SKILL.md`

### `hyperframes-registry`

Install and wire registry blocks and components into HyperFrames compositions. Use when running hyperframes add, installing a block or component, wiring an installed item into index.html, or working with hyperframes.json. Covers the add command, install locations, block sub-composition wiring, component snippet merging, and registry discovery.

- Path: `plugins/hyperframes/skills/hyperframes-registry/SKILL.md`

### `website-to-hyperframes`

Capture a website and create a HyperFrames video from it. Use when: (1) a user provides a URL and wants a video, (2) someone says "capture this site", "turn this into a video", "make a promo from my site", (3) the user wants a social ad, product tour, or any video based on an existing website, (4) the user shares a link and asks for any kind of video content. Even if the user just pastes a URL — this is the skill to use.

- Path: `plugins/hyperframes/skills/website-to-hyperframes/SKILL.md`

## life-science-research

50 skill(s)

### `alphafold-skill`

Submit compact AlphaFold Protein Structure Database API requests for prediction, UniProt summary, sequence summary, and annotation lookups. Use when a user wants AlphaFold metadata or concise structure summaries

- Path: `plugins/life-science-research/skills/alphafold-skill/SKILL.md`

### `bgee-skill`

Submit compact Bgee SPARQL requests for healthy wild-type expression metadata and ontology-aware lookup patterns. Use when a user wants concise Bgee summaries; save raw results only on request.

- Path: `plugins/life-science-research/skills/bgee-skill/SKILL.md`

### `bindingdb-skill`

Submit compact BindingDB REST API requests for ligand-target binding lookups by PDB, UniProt, or similarity search. Use when a user wants concise BindingDB summaries; save raw payloads only on request.

- Path: `plugins/life-science-research/skills/bindingdb-skill/SKILL.md`

### `biobankjapan-phewas-skill`

Fetch compact BioBank Japan PheWAS summaries for single variants by accepting rsID, GRCh38, or GRCh37 input and resolving to the required GRCh37 query. Use when a user wants concise BBJ association results for one variant

- Path: `plugins/life-science-research/skills/biobankjapan-phewas-skill/SKILL.md`

### `biorxiv-skill`

Submit compact bioRxiv and medRxiv API requests for details, publication-linkage, and DOI lookups. Use when a user wants concise preprint metadata summaries

- Path: `plugins/life-science-research/skills/biorxiv-skill/SKILL.md`

### `biostudies-arrayexpress-skill`

Submit compact BioStudies and ArrayExpress API requests for free-text search and accession-based study retrieval. Use when a user wants concise BioStudies summaries

- Path: `plugins/life-science-research/skills/biostudies-arrayexpress-skill/SKILL.md`

### `cbioportal-skill`

Submit compact cBioPortal API requests for studies, molecular profiles, mutations, clinical data, and samples. Use when a user wants concise cBioPortal summaries

- Path: `plugins/life-science-research/skills/cbioportal-skill/SKILL.md`

### `cellxgene-skill`

Submit compact CELLxGENE Discover API requests for public collection and dataset metadata. Use when a user wants concise single-cell collection summaries

- Path: `plugins/life-science-research/skills/cellxgene-skill/SKILL.md`

### `chebi-skill`

Submit compact ChEBI 2.0 API requests for chemical search, compound lookup, ontology traversal, and structure metadata. Use when a user wants concise ChEBI summaries

- Path: `plugins/life-science-research/skills/chebi-skill/SKILL.md`

### `chembl-skill`

Submit compact ChEMBL API requests for activity, molecule, target, mechanism, and text-search endpoints. Use when a user wants concise ChEMBL summaries

- Path: `plugins/life-science-research/skills/chembl-skill/SKILL.md`

### `civic-skill`

Submit compact CIViC GraphQL requests for cancer variant interpretation schema inspection and targeted evidence retrieval. Use when a user wants concise CIViC summaries

- Path: `plugins/life-science-research/skills/civic-skill/SKILL.md`

### `clinicaltrials-skill`

Submit compact ClinicalTrials.gov API v2 requests for study search, metadata, enums, search areas, and field statistics. Use when a user wants concise ClinicalTrials.gov summaries

- Path: `plugins/life-science-research/skills/clinicaltrials-skill/SKILL.md`

### `clinvar-variation-skill`

Submit compact ClinVar Clinical Tables and NCBI Variation requests for search, VCV, RCV, SCV, and RefSNP lookups. Use when a user wants variant-level summaries or identifier mapping

- Path: `plugins/life-science-research/skills/clinvar-variation-skill/SKILL.md`

### `efo-ontology-skill`

Submit compact EFO OLS4 requests for search, term lookup, children, and descendants. Use when a user wants concise EFO resolution or ontology-expansion summaries

- Path: `plugins/life-science-research/skills/efo-ontology-skill/SKILL.md`

### `encode-skill`

Submit compact ENCODE REST API requests for object lookups, portal-style search, and metadata retrieval. Use when a user wants concise ENCODE summaries

- Path: `plugins/life-science-research/skills/encode-skill/SKILL.md`

### `ensembl-skill`

Submit compact Ensembl REST API requests for lookup, overlap, cross-reference, and variation endpoints. Use when a user wants concise Ensembl summaries

- Path: `plugins/life-science-research/skills/ensembl-skill/SKILL.md`

### `epigraphdb-skill`

Submit compact EpiGraphDB API requests for ontology, literature, MR, gene-drug, and support-path evidence. Use when a user wants concise EpiGraphDB summaries

- Path: `plugins/life-science-research/skills/epigraphdb-skill/SKILL.md`

### `eqtl-catalogue-skill`

Submit compact eQTL Catalogue API requests for association retrieval and documented metadata endpoints. Use when a user wants concise public eQTL Catalogue summaries

- Path: `plugins/life-science-research/skills/eqtl-catalogue-skill/SKILL.md`

### `eva-skill`

Submit compact EVA REST requests for species metadata and archived variant lookups. Use when a user wants concise European Variation Archive summaries

- Path: `plugins/life-science-research/skills/eva-skill/SKILL.md`

### `finngen-phewas-skill`

Fetch compact FinnGen PheWAS summaries for single variants by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query. Use when a user wants concise FinnGen association results for one variant

- Path: `plugins/life-science-research/skills/finngen-phewas-skill/SKILL.md`

### `genebass-gene-burden-skill`

Submit compact Genebass gene burden requests for one Ensembl gene ID and one burden set. Use when a user wants concise Genebass PheWAS summaries

- Path: `plugins/life-science-research/skills/genebass-gene-burden-skill/SKILL.md`

### `gnomad-graphql-skill`

Submit compact gnomAD GraphQL requests for frequency, gene constraint, and variant context queries. Use when a user wants concise gnomAD summaries

- Path: `plugins/life-science-research/skills/gnomad-graphql-skill/SKILL.md`

### `gtex-eqtl-skill`

Fetch GTEx single-tissue eQTL associations from one variant input by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query for the GTEx v2 API. Use when a user wants eQTL associations returned as JSON.

- Path: `plugins/life-science-research/skills/gtex-eqtl-skill/SKILL.md`

### `gwas-catalog-skill`

Submit compact GWAS Catalog REST API v2 requests for studies, associations, SNPs, EFO traits, genes, publications, loci, and metadata. Use when a user wants concise GWAS Catalog summaries

- Path: `plugins/life-science-research/skills/gwas-catalog-skill/SKILL.md`

### `hmdb-skill`

Submit compact HMDB search requests for metabolites, proteins, diseases, and pathways. Use when a user wants concise HMDB summaries

- Path: `plugins/life-science-research/skills/hmdb-skill/SKILL.md`

### `human-protein-atlas-skill`

Submit compact Human Protein Atlas requests for gene JSON, search downloads, and page-level tissue or cell-line lookups. Use when a user wants concise Human Protein Atlas summaries; save raw JSON or HTML only on request.

- Path: `plugins/life-science-research/skills/human-protein-atlas-skill/SKILL.md`

### `ipd-skill`

Submit compact IPD REST requests for HLA allele and cell-level metadata using the public IPD query API. Use when a user wants concise IPD summaries; save raw JSON or text only on request.

- Path: `plugins/life-science-research/skills/ipd-skill/SKILL.md`

### `locus-to-gene-mapper-skill`

Map GWAS loci to ranked candidate genes using a deterministic multi-skill chain (EFO -> GWAS -> coordinates -> Open Targets L2G/coloc -> eQTL -> burden/coding context), with reproducible tables and optional figures. Use when a user provides a trait/EFO term and/or lead variants and needs locus-to-gene prioritization for downstream biology decisions.

- Path: `plugins/life-science-research/skills/locus-to-gene-mapper-skill/SKILL.md`

### `metabolights-skill`

Submit compact MetaboLights requests for study discovery and study-level metabolomics metadata. Use when a user wants concise MetaboLights summaries

- Path: `plugins/life-science-research/skills/metabolights-skill/SKILL.md`

### `mgnify-skill`

Submit compact MGnify API requests for microbiome studies, samples, and biome metadata. Use when a user wants concise MGnify summaries

- Path: `plugins/life-science-research/skills/mgnify-skill/SKILL.md`

### `ncbi-blast-skill`

Submit, poll, and summarize NCBI BLAST Common URL API jobs (Blast.cgi) for nucleotide or protein sequences. Use when a user wants RID status, BLAST results, or compact top-hit summaries; fetch raw Text/JSON2 only on request.

- Path: `plugins/life-science-research/skills/ncbi-blast-skill/SKILL.md`

### `ncbi-clinicaltables-skill`

Submit compact Clinical Tables NCBI Gene requests for human gene lookup, pagination, and field selection. Use when a user wants concise autocomplete-style human gene search results

- Path: `plugins/life-science-research/skills/ncbi-clinicaltables-skill/SKILL.md`

### `ncbi-datasets-skill`

Submit compact NCBI Datasets v2 requests for assembly, genome, taxonomy, and related metadata endpoints. Use when a user wants concise NCBI Datasets summaries; save raw JSON or text only on request.

- Path: `plugins/life-science-research/skills/ncbi-datasets-skill/SKILL.md`

### `ncbi-entrez-skill`

Submit compact NCBI Entrez E-Utilities requests for PubMed, Gene, Protein, Nucleotide, PMC metadata, and GEO metadata workflows. Use when a user wants concise Entrez search, fetch, summary, or link results; save raw JSON or XML only on request.

- Path: `plugins/life-science-research/skills/ncbi-entrez-skill/SKILL.md`

### `ncbi-pmc-skill`

Submit compact NCBI PMC Open Access requests for article/file availability metadata. Use when a user wants concise PMC Open Access summaries; save raw XML only on request.

- Path: `plugins/life-science-research/skills/ncbi-pmc-skill/SKILL.md`

### `opentargets-skill`

Submit compact Open Targets Platform GraphQL requests for target, disease, drug, variant, study, and search data, including associated-disease datasource heatmap matrices. Use when a user wants concise Open Targets summaries or per-datasource evidence context

- Path: `plugins/life-science-research/skills/opentargets-skill/SKILL.md`

### `pharmgkb-skill`

Submit compact PharmGKB API requests for genes, variants, clinical annotations, dosing guidelines, and search. Use when a user wants concise PharmGKB summaries

- Path: `plugins/life-science-research/skills/pharmgkb-skill/SKILL.md`

### `pride-skill`

Submit compact PRIDE Archive API requests for proteomics project discovery and project-level metadata. Use when a user wants concise PRIDE summaries

- Path: `plugins/life-science-research/skills/pride-skill/SKILL.md`

### `proteomexchange-skill`

Submit compact ProteomeXchange PROXI requests for datasets, libraries, peptidoforms, proteins, PSMs, spectra, and USI examples. Use when a user wants concise PROXI summaries

- Path: `plugins/life-science-research/skills/proteomexchange-skill/SKILL.md`

### `pubchem-pug-skill`

Submit compact PubChem PUG REST requests for compound properties, descriptions, assay summaries, and substance metadata. Use when a user wants concise PubChem summaries

- Path: `plugins/life-science-research/skills/pubchem-pug-skill/SKILL.md`

### `quickgo-skill`

Submit compact QuickGO requests for GO terms, annotations, and ontology traversal. Use when a user wants concise QuickGO summaries

- Path: `plugins/life-science-research/skills/quickgo-skill/SKILL.md`

### `rcsb-pdb-skill`

Submit compact RCSB PDB requests for core metadata, Search API queries, and FASTA downloads. Use when a user wants concise RCSB summaries; save raw JSON or FASTA only on request.

- Path: `plugins/life-science-research/skills/rcsb-pdb-skill/SKILL.md`

### `reactome-skill`

Submit compact Reactome ContentService requests for pathway, event, participant, search, and diagram-related data. Use when a user wants concise Reactome summaries

- Path: `plugins/life-science-research/skills/reactome-skill/SKILL.md`

### `research-router-skill`

Route broad or ambiguous life-sciences research requests to the right skills, normalize core entities, optionally parallelize independent evidence gathering with subagents when available, and synthesize a concise evidence-backed answer. Use when a user asks a general life-sciences question that could span multiple sources or analysis types.

- Path: `plugins/life-science-research/skills/research-router-skill/SKILL.md`

### `rhea-skill`

Submit compact Rhea reaction search requests for biochemical reactions and reaction IDs. Use when a user wants concise Rhea summaries

- Path: `plugins/life-science-research/skills/rhea-skill/SKILL.md`

### `rnacentral-skill`

Submit compact RNAcentral API requests for RNA entry browsing, single-entry lookup, and cross-reference retrieval. Use when a user wants concise RNAcentral summaries

- Path: `plugins/life-science-research/skills/rnacentral-skill/SKILL.md`

### `string-skill`

Submit compact STRING API requests for network, interaction partner, and enrichment endpoints. Use when a user wants concise STRING summaries

- Path: `plugins/life-science-research/skills/string-skill/SKILL.md`

### `tpmi-phewas-skill`

Fetch compact TPMI PheWAS summaries for single variants by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query. Use when a user wants concise TPMI association results for one variant

- Path: `plugins/life-science-research/skills/tpmi-phewas-skill/SKILL.md`

### `ukb-topmed-phewas-skill`

Fetch compact UKB-TOPMed PheWAS summaries for single variants by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query. Use when a user wants concise UKB-TOPMed association results for one variant

- Path: `plugins/life-science-research/skills/ukb-topmed-phewas-skill/SKILL.md`

### `uniprot-skill`

Submit compact UniProt REST API requests for UniProtKB, UniRef, UniParc, and FASTA stream endpoints. Use when a user wants concise UniProt summaries; save raw JSON or FASTA only on request.

- Path: `plugins/life-science-research/skills/uniprot-skill/SKILL.md`

## magicpath

1 skill(s)

### `magicpath`

Use when the user mentions MagicPath, designs, UI components, themes, canvas selections, or repo-to-canvas UI work; run magicpath-ai to search, inspect, install, or author components.

- Path: `plugins/magicpath/skills/magicpath/SKILL.md`

## mixpanel-headless

4 skill(s)

### `dashboard-expert`

Full CRUD and analysis for Mixpanel dashboards. Use when the user asks to build, create, analyze, read, understand, explain, modify, update, enhance, or manage dashboards, or asks about dashboard layout, text cards, or report arrangement. Covers dashboard analysis (read + understand existing), creation (new builds), modification (update existing), and explanation (data-driven annotation).

- Path: `plugins/mixpanel-headless/skills/dashboard-expert/SKILL.md`

### `mixpanel-auth`

Manage Mixpanel Headless authentication: check session state, list/add/use accounts, run OAuth login, switch projects/workspaces, manage targets, and check bridge credentials.

- Path: `plugins/mixpanel-headless/skills/mixpanel-auth/SKILL.md`

### `mixpanel-headless-setup`

This skill installs mixpanel_headless, pandas, numpy, matplotlib, seaborn, networkx, anytree, scipy (and pyarrow on Python 3.11+), then verifies Mixpanel credentials. It should be invoked when setting up a new environment for Mixpanel data analysis, when dependencies are missing, or when configuring service account or OAuth credentials for the first time.

- Path: `plugins/mixpanel-headless/skills/setup/SKILL.md`

### `mixpanelyst`

This skill should be used when the user asks about Mixpanel product analytics, event data, funnel analysis, retention curves, cohort analysis, segmentation queries, user behavior, conversion rates, churn, DAU/MAU, ARPU, revenue metrics, feature adoption, A/B test results, user paths, flow analysis, or any request to query, explore, visualize, or analyze Mixpanel data using Python. Also use when the user asks to read, write, or manage Mixpanel "business context" — the markdown documentation that grounds AI assistants in an organization's structure and goals.

- Path: `plugins/mixpanel-headless/skills/mixpanelyst/SKILL.md`

## ngs-analysis

18 skill(s)

### `ngs-amplicon-microbiome`

Kick off public 16S, 18S, ITS, COI, or other marker-gene amplicon microbiome workflows using nf-core/ampliseq, QIIME2, DADA2, and Cutadapt.

- Path: `plugins/ngs-analysis/skills/ngs-amplicon-microbiome/SKILL.md`

### `ngs-analysis-router`

Route BCL, FASTQ, BAM/CRAM, count-matrix, or VCF sequencing requests to the right public NGS analysis skill and ask only the missing assay-specific setup questions.

- Path: `plugins/ngs-analysis/skills/ngs-analysis-router/SKILL.md`

### `ngs-atacseq-peaks-qc`

Run or plan ATAC-seq QC, alignment, TSS enrichment, fragment-size, blacklist, peak-calling, consensus peak, and differential accessibility workflows.

- Path: `plugins/ngs-analysis/skills/ngs-atacseq-peaks-qc/SKILL.md`

### `ngs-bcl-to-fastq`

Validate Illumina BCL run folders and sample sheets, plan demultiplexing, review index/UMI/lane choices, run BCL-to-FASTQ conversion, and interpret demux metrics while surfacing license/download boundaries.

- Path: `plugins/ngs-analysis/skills/ngs-bcl-to-fastq/SKILL.md`

### `ngs-bulk-rnaseq`

Dispatch bulk RNA-seq requests to FASTQ-to-count QC or count-matrix differential-expression skills using nf-core/rnaseq, STAR, Salmon, featureCounts, MultiQC, and R/Bioconductor workflows.

- Path: `plugins/ngs-analysis/skills/ngs-bulk-rnaseq/SKILL.md`

### `ngs-bulk-rnaseq-counts-qc`

Run or plan bulk RNA-seq FASTQ-to-count processing with sample-sheet, strandedness, genome annotation, alignment or pseudoalignment, MultiQC, and count-matrix QC checks.

- Path: `plugins/ngs-analysis/skills/ngs-bulk-rnaseq-counts-qc/SKILL.md`

### `ngs-bulk-rnaseq-differential-expression`

Run or plan bulk RNA-seq differential-expression analysis from count matrices with replicate, design formula, contrast, batch, normalization, QC plot, and result-table checks.

- Path: `plugins/ngs-analysis/skills/ngs-bulk-rnaseq-differential-expression/SKILL.md`

### `ngs-chip-cutrun-peaks-qc`

Run or plan ChIP-seq, CUT&RUN, or CUT&Tag QC, control handling, spike-in, peak calling, broad-vs-narrow target selection, replicate, bigWig, and differential binding workflows.

- Path: `plugins/ngs-analysis/skills/ngs-chip-cutrun-peaks-qc/SKILL.md`

### `ngs-dna-germline-variants`

Run or plan deep germline WGS, WES, targeted-panel, cohort, or trio variant-calling workflows with reference-build, known-sites, QC, joint-calling, and annotation checks.

- Path: `plugins/ngs-analysis/skills/ngs-dna-germline-variants/SKILL.md`

### `ngs-dna-somatic-variants`

Run or plan tumor-normal, tumor-only, WGS, WES, or cancer-panel somatic variant workflows with pairing, contamination, panel-of-normals, purity, QC, and annotation checks.

- Path: `plugins/ngs-analysis/skills/ngs-dna-somatic-variants/SKILL.md`

### `ngs-dna-umi-panel-variants`

Run or plan targeted DNA panel variant workflows that use UMIs, duplex consensus reads, molecular barcodes, low-frequency calling, target coverage, and panel-specific QC.

- Path: `plugins/ngs-analysis/skills/ngs-dna-umi-panel-variants/SKILL.md`

### `ngs-dna-variant-calling`

Dispatch WGS, WES, or targeted DNA variant requests to germline, somatic, or UMI-panel skills, then plan public nf-core/sarek, GATK4, DeepVariant, samtools, or bcftools workflows.

- Path: `plugins/ngs-analysis/skills/ngs-dna-variant-calling/SKILL.md`

### `ngs-epigenomics-peaks`

Dispatch ATAC-seq, ChIP-seq, CUT&RUN, or CUT&Tag requests to assay-specific QC, alignment, signal-track, peak-calling, consensus, and differential peak workflows.

- Path: `plugins/ngs-analysis/skills/ngs-epigenomics-peaks/SKILL.md`

### `ngs-fastq-qc`

Validate FASTQ inputs, run local FastQC/MultiQC QC, interpret QC signals, and optionally execute fastp or Cutadapt trimming branches without overwriting raw reads.

- Path: `plugins/ngs-analysis/skills/ngs-fastq-qc/SKILL.md`

### `ngs-runtime-env`

Check whether public NGS tools and packages already exist before downloading, installing, or running a sequencing pipeline.

- Path: `plugins/ngs-analysis/skills/ngs-runtime-env/SKILL.md`

### `ngs-scrna-seq`

Route single-cell or single-nucleus RNA-seq FASTQs to public count-generation workflows and defer post-count matrix QC, annotation, clustering, and UMAP analysis to the embedded scrna-seq-qc skill.

- Path: `plugins/ngs-analysis/skills/ngs-scrna-seq/SKILL.md`

### `ngs-shotgun-metagenomics`

Kick off public shotgun metagenomics QC, host-depletion, taxonomic profiling, and functional profiling workflows using nf-core/taxprofiler, Kraken2, Bracken, MetaPhlAn, and HUMAnN.

- Path: `plugins/ngs-analysis/skills/ngs-shotgun-metagenomics/SKILL.md`

### `scrna-seq-qc`

Process, quality-control, annotate, and visualize single-cell or single-nucleus RNA-seq datasets across tissues and species. Use when Codex needs to build, adapt, or review a general scRNA-seq QC pipeline; choose dataset-appropriate cell-level filters from QC distributions; run required scDblFinder-based doublet and ambient-RNA filtering; annotate cells with matched references or marker-based fallbacks; or generate global and per-group UMAP visualizations for large scRNA-seq datasets.

- Path: `plugins/ngs-analysis/skills/scrna-seq-qc/SKILL.md`

## notion

4 skill(s)

### `notion-knowledge-capture`

Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linking.

- Path: `plugins/notion/skills/notion-knowledge-capture/SKILL.md`

### `notion-meeting-intelligence`

Prepare meeting materials with Notion context and supplemental research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees.

- Path: `plugins/notion/skills/notion-meeting-intelligence/SKILL.md`

### `notion-research-documentation`

Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or reports with citations.

- Path: `plugins/notion/skills/notion-research-documentation/SKILL.md`

### `notion-spec-to-implementation`

Turn Notion specs into implementation plans, tasks, and progress tracking; use when implementing PRDs/feature specs and creating Notion plans + tasks from them.

- Path: `plugins/notion/skills/notion-spec-to-implementation/SKILL.md`

## nvidia

12 skill(s)

### `aiq-deploy`

Use when asked to install, deploy, run, validate, troubleshoot, or stop NVIDIA AI-Q Blueprint infrastructure.

- Path: `plugins/nvidia/skills/aiq-deploy/SKILL.md`

### `aiq-research`

Use when asked to run deep research or AI-Q research through a reachable NVIDIA AI-Q Blueprint backend.

- Path: `plugins/nvidia/skills/aiq-research/SKILL.md`

### `cuopt-user-rules`

Base rules for end users calling NVIDIA cuOpt (routing/LP/MILP/QP/install/server). Not for cuOpt internals — use cuopt-developer for those.

- Path: `plugins/nvidia/skills/cuopt-user-rules/SKILL.md`

### `dynamo-interconnect-check`

Validate that a Dynamo deployment's NIXL/UCX/NCCL interconnect is ready for disaggregated serving over RDMA/NVLink. Use after recipe-runner brings a deployment up (especially disagg/multi-node) to confirm the KV transport is correct; use troubleshoot for diagnosing already-failed pods.

- Path: `plugins/nvidia/skills/dynamo-interconnect-check/SKILL.md`

### `dynamo-router-starter`

Start or patch Dynamo router modes and run router endpoint smoke checks. Use for round-robin, KV-aware, least-loaded, or device-aware routing setup; use recipe-runner for recipe deployment and troubleshoot for failure diagnosis.

- Path: `plugins/nvidia/skills/dynamo-router-starter/SKILL.md`

### `nemoclaw-user-get-started`

Installs NemoClaw, launches a sandbox, and runs the first agent prompt. Use when onboarding, installing, or launching a NemoClaw sandbox for the first time. Trigger keywords - nemoclaw quickstart, install nemoclaw openclaw sandbox, nemohermes quickstart, hermes agent nemoclaw, run hermes openshell sandbox, nemoclaw prerequisites, nemoclaw supported platforms, nemoclaw hardware software, nemoclaw windows wsl2 setup, nemoclaw install windows docker desktop.

- Path: `plugins/nvidia/skills/nemoclaw-user-get-started/SKILL.md`

### `nvidia-skill-finder`

Use for NVIDIA-related requests where an NVIDIA skill might help, even if the user did not ask for a skill. Trigger on NVIDIA products, hardware, software, SDKs, GPUs, Jetson/JetPack/L4T/BSP/SDK Manager/driver/flashing/setup, CUDA, NIM, NeMo, Omniverse/OpenUSD/SimReady, RAPIDS/cuDF, cuPyNumeric, cuOpt, Dynamo, Holoscan, TensorRT, DeepStream, VSS, TAO, NGC/NVCF. Do not use for generic non-NVIDIA route, optimize, deploy, AI, video, data, or infrastructure tasks.

- Path: `plugins/nvidia/skills/nvidia-skill-finder/SKILL.md`

### `omniverse-cad-to-simready`

Coordinate the end-to-end CAD/source-asset to SimReady workflow. Use for broad requests such as CAD to SimReady, source asset to simulation-ready USD, or prop packaging that require conversion, material/physics assignment, SimReady conformance, validation, and optional package creation; deploy or verify Content Agents services first when property assignment is enabled; route single-stage work through nested references.

- Path: `plugins/nvidia/skills/omniverse-cad-to-simready/SKILL.md`

### `omniverse-realtime-viewer`

Use as the top-level router for Omniverse Realtime Viewer USD app requests and focused viewer reference documents.

- Path: `plugins/nvidia/skills/omniverse-realtime-viewer/SKILL.md`

### `omniverse-usd-performance-tuning`

Top-level workflow skill for USD performance diagnosis and optimization. Use for slow loading, high memory, low FPS, or 'optimize my scene' requests; delegates auth/runtime setup to Phase 0 owners.

- Path: `plugins/nvidia/skills/omniverse-usd-performance-tuning/SKILL.md`

### `physical-ai-infrastructure-setup-and-resilient-scaling`

Use when the user wants to set up, scale, validate, or harden NVIDIA physical AI infrastructure for synthetic data generation workflows across local MicroK8s or Azure AKS, including Kubernetes clusters, inference endpoint deployment, OSMO deployment, workload submission readiness, and infrastructure failure recovery. Trigger keywords: physical ai infrastructure, resilient scaling, SDG infrastructure, microk8s, azure aks, NVCF deployment, NIM Operator, OSMO deploy, workflow scaling. Don't trigger for: OSMO log summarization or workload-only operations unless infrastructure setup, scaling, validation, or recovery is requested.

- Path: `plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/SKILL.md`

### `physical-ai-neural-reconstruction`

Router for NVIDIA NuRec/NRE: USDZ rendering, NCore conversion, 3DGS, gRPC sensor sim, PhysicalAI HF datasets. Do NOT use for SimReady or infra setup.

- Path: `plugins/nvidia/skills/physical-ai-neural-reconstruction/SKILL.md`

## openai-ads-conversions

1 skill(s)

### `openai-ads-conversions-setup`

Guide Codex through instrumenting or extending repositories with OpenAI Ads Measurement Pixel and optional Conversions API (CAPI). Use when adding Ads conversion tracking, browser pixel events, server-side conversion events, event_id deduplication, CAPI secret placeholders, incremental conversion coverage, or validating Ads conversion setup. Applies to local repositories and PR review contexts; prioritize safe, reviewable diffs and never place API keys or secrets in source code or client bundles.

- Path: `plugins/openai-ads-conversions/skills/openai-ads-conversions-setup/SKILL.md`

## openai-developers

5 skill(s)

### `agents-sdk`

Build, run, deploy, and evaluate OpenAI Agents SDK apps from Codex. Use when the user asks to create or adapt an Agents SDK app, build from a prompt or Codex thread, prepare a runnable agent prototype, add a focused eval harness, or deploy locally through the Agents SDK Deployment Manager.

- Path: `plugins/openai-developers/skills/agents-sdk/SKILL.md`

### `build-chatgpt-app`

Build, scaffold, refactor, and troubleshoot ChatGPT Apps SDK applications that combine an MCP server and widget UI. Use when Codex needs to design tools, register UI resources, wire the MCP Apps bridge or ChatGPT compatibility APIs, apply Apps SDK metadata or CSP or domain settings, or produce a docs-aligned project scaffold. Prefer a docs-first workflow by invoking the openai-docs skill or OpenAI developer docs MCP tools before generating code.

- Path: `plugins/openai-developers/skills/build-chatgpt-app/SKILL.md`

### `chatgpt-app-submission`

Inspect a ChatGPT Apps MCP server codebase and generate chatgpt-app-submission.json with app info suggestions, tool hint justifications, test cases, and negative test cases, then report review-check findings and outputSchema warnings for submission review.

- Path: `plugins/openai-developers/skills/chatgpt-app-submission/SKILL.md`

### `openai-api-troubleshooting`

Use when an OpenAI API request fails and Codex needs to classify the likely cause, explain the next step, and route to the right follow-up. Covers common runtime failures such as blocked outbound network access, invalid credentials, exhausted API quota or credits, rate limits, and model, project, or organization access issues; delegate key provisioning to openai-platform-api-key and current documentation lookups to openai-docs.

- Path: `plugins/openai-developers/skills/openai-api-troubleshooting/SKILL.md`

### `openai-platform-api-key`

Use when Codex is asked to build, run, test, debug, or configure an OpenAI-backed or provider-unspecified AI app, UI, script, CLI, generator, or tool, especially requests phrased only as "using AI" or generators driven by forms/user input; also use for OPENAI_API_KEY or sk-proj setup. Do not gate model or prompt migrations that can proceed with source edits and offline validation. Otherwise treat this as the credential gate: inspect safely, ask reuse-vs-new before API work, and never expose plaintext.

- Path: `plugins/openai-developers/skills/openai-platform-api-key/SKILL.md`

## plugin-eval

9 skill(s)

### `alpha`

Alpha fixture skill. Use when plugin-eval tests need one of two bundled skills.

- Path: `plugins/plugin-eval/fixtures/multi-skill-plugin/skills/alpha/SKILL.md`

### `beta`

Beta fixture skill. Use when plugin-eval tests need the second bundled skill.

- Path: `plugins/plugin-eval/fixtures/multi-skill-plugin/skills/beta/SKILL.md`

### `evaluate-plugin`

Evaluate a local Codex plugin in engineer-friendly language. Use when the user says "evaluate this plugin", "audit this plugin", "why did this score that way", "what should I fix first", "help me benchmark this plugin", or asks for a plugin-wide report before comparing versions.

- Path: `plugins/plugin-eval/skills/evaluate-plugin/SKILL.md`

### `evaluate-skill`

Evaluate a local Codex skill in engineer-friendly terms. Use when the user says "evaluate this skill", "give me an analysis of the game dev skill", "audit this skill", "why did this score that way", "what should I fix first", or asks for a skill-specific report before benchmarking it.

- Path: `plugins/plugin-eval/skills/evaluate-skill/SKILL.md`

### `improve-skill`

Turn plugin-eval findings into a concrete rewrite brief for a Codex skill. Use when the user already evaluated a skill and now wants Codex to improve it, especially after asking what to fix first.

- Path: `plugins/plugin-eval/skills/improve-skill/SKILL.md`

### `metric-pack-designer`

Design custom metric packs for plugin-eval so teams can add local evaluation rubrics that emit schema-compatible checks and metrics. Use when the user wants their own evaluation criteria or visualizations.

- Path: `plugins/plugin-eval/skills/metric-pack-designer/SKILL.md`

### `minimal-plugin-skill`

Minimal plugin skill fixture. Use when a test needs a valid plugin skill.

- Path: `plugins/plugin-eval/fixtures/minimal-plugin/skills/minimal-plugin-skill/SKILL.md`

### `minimal-skill`

Minimal example skill for plugin-eval tests. Use when the user wants a compact demonstration of a well-structured skill.

- Path: `plugins/plugin-eval/fixtures/minimal-skill/SKILL.md`

### `plugin-eval`

Help engineers evaluate a local skill or plugin, explain why it scored that way, show what to fix first, measure real token usage, benchmark starter scenarios, or decide what to run next. Use when the user says things like "evaluate this skill", "give me an analysis of the game dev skill", "why did this score that way", "what should I fix first", "measure the real token usage of this skill", or "what should I run next?".

- Path: `plugins/plugin-eval/skills/plugin-eval/SKILL.md`

## posthog

1 skill(s)

### `posthog`

Analyze product data and manage product tooling in PostHog. Use when the user wants product analytics or insights, HogQL/SQL queries, feature flags, experiments and A/B tests, error tracking, session replay, surveys, LLM analytics, dashboards, data warehouse, or PostHog documentation.

- Path: `plugins/posthog/skills/posthog/SKILL.md`

## product-design

10 skill(s)

### `audit`

Audit or critique a product flow, journey, workflow, funnel, onboarding path, checkout path, settings path, screen, or multi-step product experience by capturing screenshots first, then reporting UX, design, and accessibility findings inline from that evidence. Use Figma only when the user explicitly asks for a board. Use when the user asks to audit, review, critique, inspect, assess, analyze, evaluate, or give feedback on a product experience.

- Path: `plugins/product-design/skills/audit/SKILL.md`

### `design-qa`

Internal prototype QA helper. Use only after a Product Design prototype, URL-to-code build, or image-to-code build has a source visual target and a rendered implementation to compare before handoff. Do not use for broad UX critique, design critique, product audits, or flow reviews; route those user-facing requests to audit.

- Path: `plugins/product-design/skills/design-qa/SKILL.md`

### `get-context`

Mandatory design-brief gate for clarifying the product and outcome. Use before ideation, image-to-code builds, redesigns, or product UI work to clarify missing product information and play back the brief before proceeding.

- Path: `plugins/product-design/skills/get-context/SKILL.md`

### `ideate`

Generate image-based alternatives, remixes, or new design directions from a Product Design brief. Use when the user asks for design variants, visual exploration, remixes, or image-generated approaches from provided context.

- Path: `plugins/product-design/skills/ideate/SKILL.md`

### `image-to-code`

Implement a selected image, screenshot, mockup, or Image Gen reference as a faithful, responsive frontend.

- Path: `plugins/product-design/skills/image-to-code/SKILL.md`

### `index`

Use when Product Design is explicitly invoked, or when the user's main goal is to explore a design, research UX, audit or critique a flow, faithfully clone a visual source, check a built design, or share a prototype. Do not use Product Design for ordinary implementation unless the user explicitly asks for it.

- Path: `plugins/product-design/skills/index/SKILL.md`

### `research`

Run fast, source-grounded UX research on the highest-signal problems users are experiencing with a user-specified digital product. Use when the user asks to research user pain, UX friction, onboarding issues, docs/help problems, developer experience friction, support pain, product workflow issues, or current user complaints for a named product.

- Path: `plugins/product-design/skills/research/SKILL.md`

### `share`

Share a runnable prototype using the user's preferred deployment tool.

- Path: `plugins/product-design/skills/share/SKILL.md`

### `url-to-code`

Clone a live URL as a runnable frontend-only local app.

- Path: `plugins/product-design/skills/url-to-code/SKILL.md`

### `user-context`

Load or manage Product Design's saved user context. Use when the user asks to set up Product Design, get started, onboard, save product or design sources, see what Product Design remembers, update saved context, or remember Product Design preferences. Examples include product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, and general product/design notes.

- Path: `plugins/product-design/skills/user-context/SKILL.md`

## public-equity-investing

23 skill(s)

### `catalyst-calendar`

Use when building public-equity-investing catalyst calendars. Do not use for full event underwriting; use event-driven-analyzer.

- Path: `plugins/public-equity-investing/skills/catalyst-calendar/SKILL.md`

### `company-tearsheet`

Use when creating source-backed public issuer tearsheets. Do not use for private diligence, fund diligence, vendors, or market maps.

- Path: `plugins/public-equity-investing/skills/company-tearsheet/SKILL.md`

### `comps-valuation`

Produce Public Equity Investing comparable-company valuation in report or workbook mode. Use for peer selection, multiple analysis, valuation read-throughs, implied prices, comps dashboards, Excel or Sheets comps, refreshable peer tables, model updates, and comps workbook QA. Do not use for DCF-only, credit-security, or generic market commentary requests.

- Path: `plugins/public-equity-investing/skills/comps-valuation/SKILL.md`

### `dcf-model-builder`

Use when building public-equity DCF valuation workbooks. Default to the banker formula workbook path for new model builds; use deterministic exports only for controlled support calculations or explicit lightweight runs. Do not use for standalone workbook audits; use model-audit-tieout.

- Path: `plugins/public-equity-investing/skills/dcf-model-builder/SKILL.md`

### `deck-report-qc`

Use when running first-pass QC on Public Equity Investing decks or reports. Do not use as external-circulation certification.

- Path: `plugins/public-equity-investing/skills/deck-report-qc/SKILL.md`

### `earnings-deep-dive`

Use when analyzing public-company earnings after results, guidance, transcript, or call commentary. Do not use for pre-print previews.

- Path: `plugins/public-equity-investing/skills/earnings-deep-dive/SKILL.md`

### `earnings-preview`

Use when preparing full pre-earnings preview reports with executive summary, expectation bar, guidance credibility, KPI dashboard, scenarios, and call questions. Do not use after results or for short summaries unless the user explicitly asks for a summary/short version.

- Path: `plugins/public-equity-investing/skills/earnings-preview/SKILL.md`

### `economic-impact-report`

Use when translating a specific event, policy change, macro shock, or industry development into public-equity issuer, sector, earnings, valuation, positioning, and portfolio implications. Do not use for standalone macro strategy, rates, FX, credit, futures, or generic market commentary.

- Path: `plugins/public-equity-investing/skills/economic-impact-report/SKILL.md`

### `equity-model-update`

Safely update public-company Excel model copies from source-to-model maps; emits XLSX as the hero artifact and CSV/log/manifest as support. Do not use for pure earnings notes or broad workbook audits.

- Path: `plugins/public-equity-investing/skills/equity-model-update/SKILL.md`

### `event-driven-analyzer`

Use when analyzing dated public-equity event paths, probabilities, payoffs, and expected returns. Do not use for generic catalyst lists, risk sizing, hedges, capital structure, covenants, or credit recovery.

- Path: `plugins/public-equity-investing/skills/event-driven-analyzer/SKILL.md`

### `financials-normalizer`

Use when normalizing public-company financials from source materials. Do not use for private data rooms or non-financial cleanup.

- Path: `plugins/public-equity-investing/skills/financials-normalizer/SKILL.md`

### `idea-generation`

Use when triaging public-equity idea candidates. Do not use for final trade recommendations, pitches, memos, or models.

- Path: `plugins/public-equity-investing/skills/idea-generation/SKILL.md`

### `initiating-coverage`

Use when building public-equity-investing initiating coverage reports. Do not use for trade pitches, memos, earnings notes, models, or tearsheets.

- Path: `plugins/public-equity-investing/skills/initiating-coverage/SKILL.md`

### `long-short-pitch`

Use when building PM-facing Public Equity Investing trade pitches, including sparse-context or partial-section requests. Do not use for formal memos; use memo-builder.

- Path: `plugins/public-equity-investing/skills/long-short-pitch/SKILL.md`

### `meeting-prep`

Use when creating Public Equity Investing meeting prep briefs. Do not use for private diligence, IB, FP&A, legal, or scheduling-only tasks.

- Path: `plugins/public-equity-investing/skills/meeting-prep/SKILL.md`

### `memo-builder`

Use when drafting or reviewing formal public-equity investment memos. Do not use for live trade construction or credit-first memos; use long-short-pitch or Credit Markets as appropriate.

- Path: `plugins/public-equity-investing/skills/memo-builder/SKILL.md`

### `model-audit-tieout`

Use when auditing existing Public Equity Investing models or spreadsheets. Do not use to build a new model from scratch.

- Path: `plugins/public-equity-investing/skills/model-audit-tieout/SKILL.md`

### `portfolio-risk-management`

Use when sizing Public Equity Investing positions, finding equity hedges, or building an integrated position-and-hedge risk plan from a listed-equity thesis. Do not use for thesis construction, standalone event underwriting, trade execution, personal investment advice, or credit-instrument risk.

- Path: `plugins/public-equity-investing/skills/portfolio-risk-management/SKILL.md`

### `public-equity-investing`

Route Public Equity Investing workflows for listed-company and public-security research, earnings analysis, valuation, model updates, long/short pitches, catalysts, thesis tracking, ETF/index and constituent diligence, position sizing, hedging, dashboards, and investment memos. Use when the user is evaluating a public company, ticker, sector, portfolio position, event, earnings setup, or investment thesis through an investor lens, including what is priced in, what is mispriced, what proves or kills the thesis, and what to watch next. Do not use for private-company diligence, credit-first analysis, personal financial advice, generic company summaries, or generic document drafting with no public-equity investment context.

- Path: `plugins/public-equity-investing/skills/public-equity-investing/SKILL.md`

### `scenario-sensitivity-generator`

Use when turning a public-equity base case, model, thesis, event, or catalyst into scenario skew, sensitivity, breakpoint, and PM action-threshold analysis. Do not use for first-pass model builds, credit-security valuation, or generic planning.

- Path: `plugins/public-equity-investing/skills/scenario-sensitivity-generator/SKILL.md`

### `thesis-tracker`

Use when building or updating Public Equity Investing thesis trackers. Do not use for generic news summaries, trade pitches, or first-pass memos.

- Path: `plugins/public-equity-investing/skills/thesis-tracker/SKILL.md`

### `three-statement-model-builder`

Use when building public-equity three-statement operating model workbooks. Default to the banker formula workbook path for new model builds; use deterministic exports only for controlled support calculations or explicit lightweight runs. Do not use for standalone workbook audits.

- Path: `plugins/public-equity-investing/skills/three-statement-model-builder/SKILL.md`

### `user-context`

Initialize, inspect, save, update, forget, export, or explicitly reset the Public Equity Investing plugin's local user context, source setup, or optional automation setup. Use only when the user explicitly asks to manage Public Equity Investing saved preferences, source pointers, context storage, or recurring automation.

- Path: `plugins/public-equity-investing/skills/user-context/SKILL.md`

## remotion

12 skill(s)

### `remotion-best-practices`

Router for all Remotion skills

- Path: `plugins/remotion/skills/remotion-best-practices/SKILL.md`

### `remotion-captions`

Transcribing, displaying and animating captions

- Path: `plugins/remotion/skills/remotion-captions/SKILL.md`

### `remotion-create`

Create a new Remotion video

- Path: `plugins/remotion/skills/remotion-create/SKILL.md`

### `remotion-docs`

Search Remotion documentation

- Path: `plugins/remotion/skills/remotion-docs/SKILL.md`

### `remotion-interactivity`

Structure Remotion markup for interactivity

- Path: `plugins/remotion/skills/remotion-interactivity/SKILL.md`

### `remotion-maps`

Remotion Map animation knowledge

- Path: `plugins/remotion/skills/remotion-maps/SKILL.md`

### `remotion-markup`

Content, animation and effects best practices

- Path: `plugins/remotion/skills/remotion-markup/SKILL.md`

### `remotion-multimedia`

Interacting with Mediabunny

- Path: `plugins/remotion/skills/remotion-multimedia/SKILL.md`

### `remotion-render`

Export a Remotion video

- Path: `plugins/remotion/skills/remotion-render/SKILL.md`

### `remotion-saas`

Build an app with Remotion

- Path: `plugins/remotion/skills/remotion-saas/SKILL.md`

### `remotion-studio`

Preview a Remotion video

- Path: `plugins/remotion/skills/remotion-studio/SKILL.md`

### `remotion-upgrade`

Upgrade Remotion, and related packages

- Path: `plugins/remotion/skills/remotion-upgrade/SKILL.md`

## sentry

1 skill(s)

### `sentry`

Use when the user asks to inspect Sentry issues or events, summarize recent production errors, or pull basic Sentry health data via the Sentry API; perform read-only queries with the bundled script and require `SENTRY_AUTH_TOKEN`.

- Path: `plugins/sentry/skills/sentry/SKILL.md`

## shopify

20 skill(s)

### `shopify-admin`

Write or explain **Admin GraphQL** queries and mutations for apps and integrations that extend the Shopify admin. Use when the user wants to **understand, design, or generate** the operation itself—even before deciding how to run it. Do **not** choose `admin` first for **app or extension config validation** —use **`use-shopify-cli`**. Do **not** choose `admin` first to **execute** Admin GraphQL **now via Shopify CLI** or for CLI setup/troubleshooting on store workflows—use **`use-shopify-cli`** (store auth/execute, handle/SKU/location lookups, inventory changes).

- Path: `plugins/shopify/skills/shopify-admin/SKILL.md`

### `shopify-app-store-review`

Run a pre-submission compliance check against your Shopify app's codebase. Reviews App Store requirements and surfaces likely issues before you submit for official review.

- Path: `plugins/shopify/skills/shopify-app-store-review/SKILL.md`

### `shopify-custom-data`

MUST be used first when prompts mention Metafields or Metaobjects. Use Metafields and Metaobjects to model and store custom data for your app. Metafields extend built-in Shopify data types like products or customers, Metaobjects are custom data types that can be used to store bespoke data structures. Metafield and Metaobject definitions provide a schema and configuration for values to follow.

- Path: `plugins/shopify/skills/shopify-custom-data/SKILL.md`

### `shopify-customer`

The Customer Account API allows customers to access their own data including orders, payment methods, and addresses.

- Path: `plugins/shopify/skills/shopify-customer/SKILL.md`

### `shopify-dev`

Search Shopify developer documentation across all APIs. Use only when no API-specific skill applies.

- Path: `plugins/shopify/skills/shopify-dev/SKILL.md`

### `shopify-functions`

Shopify Functions allow developers to customize the backend logic that powers parts of Shopify. Available APIs: Discount, Cart and Checkout Validation, Cart Transform, Pickup Point Delivery Option Generator, Delivery Customization, Fulfillment Constraints, Local Pickup Delivery Option Generator, Order Routing Location Rule, Payment Customization

- Path: `plugins/shopify/skills/shopify-functions/SKILL.md`

### `shopify-hydrogen`

Hydrogen storefront implementation cookbooks. Some of the available recipes are: B2B Commerce, Bundles, Combined Listings, Custom Cart Method, Dynamic Content with Metaobjects, Express Server, Google Tag Manager Integration, Infinite Scroll, Legacy Customer Account Flow, Markets, Partytown + Google Tag Manager, Subscriptions, Third-party API Queries and Caching. MANDATORY: Use this API for ANY Hydrogen storefront question - do NOT use Storefront GraphQL when 'Hydrogen' is mentioned.

- Path: `plugins/shopify/skills/shopify-hydrogen/SKILL.md`

### `shopify-liquid`

Liquid is an open-source templating language created by Shopify. It is the backbone of Shopify themes and is used to load dynamic content on storefronts. Keywords: liquid, theme, shopify-theme, liquid-component, liquid-block, liquid-section, liquid-snippet, liquid-schemas, shopify-theme-schemas

- Path: `plugins/shopify/skills/shopify-liquid/SKILL.md`

### `shopify-onboarding-dev`

Get started building on Shopify. Use when a developer asks to build an app, build a theme, create a dev store, set up a partner account, scaffold a project, or get started developing for Shopify. NOT for merchants managing stores.

- Path: `plugins/shopify/skills/shopify-onboarding-dev/SKILL.md`

### `shopify-onboarding-merchant`

Set up and connect a Shopify store from your AI assistant. Use when the user wants to: set up my Shopify store, connect my store, install Shopify plugin, get started with Shopify, manage my store, add products to my store, merchant onboarding, start selling online, Shopify setup help, create my first store, how do I set up an online store, import products, migrate from Square, migrate from WooCommerce, migrate from Etsy, migrate from Amazon, migrate from eBay, migrate from Wix, import from Google Merchant Center, migrate from Clover, migrate from Lightspeed, move products to Shopify, import catalog, replatform to Shopify. This is for store owners — not developers.

- Path: `plugins/shopify/skills/shopify-onboarding-merchant/SKILL.md`

### `shopify-partner`

The Partner API lets you programmatically access data about your Partner Dashboard, including your apps, themes, and affiliate referrals.

- Path: `plugins/shopify/skills/shopify-partner/SKILL.md`

### `shopify-payments-apps`

The Payments Apps API enables payment providers to integrate their payment solutions with Shopify's checkout.

- Path: `plugins/shopify/skills/shopify-payments-apps/SKILL.md`

### `shopify-polaris-admin-extensions`

Add custom actions and blocks from your app at contextually relevant spots throughout the Shopify Admin. Admin UI Extensions also supports scaffolding new adminextensions using Shopify CLI commands.

- Path: `plugins/shopify/skills/shopify-polaris-admin-extensions/SKILL.md`

### `shopify-polaris-app-home`

Build your app's primary user interface embedded in the Shopify admin. If the prompt just mentions `Polaris` and you can't tell based off of the context what API they meant, assume they meant this API.

- Path: `plugins/shopify/skills/shopify-polaris-app-home/SKILL.md`

### `shopify-polaris-checkout-extensions`

Build custom functionality that merchants can install at defined points in the checkout flow, including product information, shipping, payment, order summary, and Shop Pay. Checkout UI Extensions also supports scaffolding new checkout extensions using Shopify CLI commands.

- Path: `plugins/shopify/skills/shopify-polaris-checkout-extensions/SKILL.md`

### `shopify-polaris-customer-account-extensions`

Build custom functionality that merchants can install at defined points on the Order index, Order status, and Profile pages in customer accounts. Customer Account UI Extensions also supports scaffolding new customer account extensions using Shopify CLI commands.

- Path: `plugins/shopify/skills/shopify-polaris-customer-account-extensions/SKILL.md`

### `shopify-pos-ui`

Build retail point-of-sale applications using Shopify's POS UI components. These components provide a consistent and familiar interface for POS applications. POS UI Extensions also supports scaffolding new POS extensions using Shopify CLI commands. Keywords: POS, Retail, smart grid

- Path: `plugins/shopify/skills/shopify-pos-ui/SKILL.md`

### `shopify-storefront-graphql`

Use for custom storefronts requiring direct GraphQL queries/mutations for data fetching and cart operations. Choose this when you need full control over data fetching and rendering your own UI. NOT for Web Components - if the prompt mentions HTML tags like <shopify-store>, <shopify-cart>, use storefront-web-components instead.

- Path: `plugins/shopify/skills/shopify-storefront-graphql/SKILL.md`

### `shopify-use-shopify-cli`

Choose when the user needs **Shopify CLI** to run or fix something now: validate app or extension config on disk (`shopify.app.toml`, `shopify.app.<name>.toml`, `shopify.extension.toml`); run or troubleshoot store workflows (`shopify store auth`, `shopify store execute`); inventory or product changes by handle, SKU, or location name; or CLI setup, auth, upgrade issues. Emphasize **commands and operational steps**, not only authoring GraphQL. Skip for API-only understanding or codegen with no CLI execution. Examples: validate configuration before deploy; run an existing query via CLI; list products; missing `shopify store execute`.

- Path: `plugins/shopify/skills/shopify-use-shopify-cli/SKILL.md`

### `ucp`

Use when the user wants to use the UCP CLI to find, compare, buy, or track products from online merchants, or to set up and troubleshoot the local UCP profile required for merchant-scoped operations. Covers global catalog search (\"find me X under $Y\"), named-merchant transactions (\"buy this from Z.com\"), order tracking, `ucp profile init`, `ucp doctor`, carts, checkout, orders, and UCP setup/help. Falls back to merchant-hosted handoff when direct in-protocol checkout isn't available.

- Path: `plugins/shopify/skills/ucp/SKILL.md`

## stripe

7 skill(s)

### `connect-recommend`

Use this skill when the user asks about Stripe Connect configuration, charge patterns, Dashboard access, or how to get started with Connect, is building a marketplace, platform, multi-vendor store, gig platform, or subscription platform, needs to pay out sellers, vendors, or providers, mentions split payments, revenue sharing, multi-party payments, or similar payment distribution concepts, provides a company URL or business description for a recommendation, builds SaaS that routes money between parties (for example, POS, booking, invoicing — not operational SaaS without payment routing), asks about onboarding or KYC for merchants, sellers, and vendors, mentions connected account Dashboard or responsibility configurations, or asks about payment flows, white-label payments, or embedded payments.

- Path: `plugins/stripe/skills/connect-recommend/SKILL.md`

### `stripe-apps`

Use when building, modifying, or reviewing a Stripe App — or when the user describes something that implies one (e.g. "add a panel to the customer page", "customize my Stripe Dashboard", "react to Stripe events from my app", "connect my service to Stripe without sharing API keys"). Covers the full app development workflow (scaffold, preview, upload, versioning), UI extension architecture (sandboxed iframe, Stripe UI toolkit, viewports), extension types (UI extensions, backend-only, extension interfaces, embedded apps), authentication (platform keys, OAuth, restricted API keys), stripe-app.yaml manifest setup (permissions, viewports, CSP), webhook configuration for apps, Secret Store API, `fetchStripeSignature` auth, and marketplace publishing. Use when the user mentions Stripe Apps, UI extensions, @stripe/ui-extension-sdk, stripe-app.yaml, Dashboard extensions, or customizing the Stripe Dashboard.

- Path: `plugins/stripe/skills/stripe-apps/SKILL.md`

### `stripe-best-practices`

Guides Stripe integration decisions across API selection (Checkout Sessions vs PaymentIntents), Connect platform setup (Accounts v2, controller properties), billing/subscriptions, tax and registrations (Stripe Tax, automatic_tax, product tax codes), Treasury financial accounts, integration options (Checkout, Payment Element), migrating from deprecated Stripe APIs, and security best practices (API key management, restricted keys, webhooks, OAuth). Use when building, modifying, or reviewing any Stripe integration, including accepting payments, building marketplaces, integrating Stripe, processing payments, setting up subscriptions, collecting sales tax, VAT, or GST, creating connected accounts, or implementing secure key handling.

- Path: `plugins/stripe/skills/stripe-best-practices/SKILL.md`

### `stripe-directory`

Use when the user wants to find businesses, software, service providers, or partners for a specific industry, workflow, pain point, capability, or job to be done. Also use when the agent needs to programmatically purchase or consume a service. Use Stripe Directory to build a short relevant shortlist, even if the user does not mention Stripe Directory explicitly.

- Path: `plugins/stripe/skills/stripe-directory/SKILL.md`

### `stripe-docs`

Use when the user or agent needs to read, search, or look up Stripe documentation or API reference. Prefer this over curl or WebFetch for any docs.stripe.com content.

- Path: `plugins/stripe/skills/stripe-docs/SKILL.md`

### `stripe-projects`

Use when the user wants to provision infrastructure or third-party services using Stripe Projects. Triggers: "I need a database", "set up auth", "add caching", "give me a Postgres", "provision Redis", "I need hosting", "add a vector DB", "get me an API key for X", "get credentials for X", "sign up for a service", "set up monitoring", "show me the catalog", "what can I provision", "browse providers", "add an LLM provider", "configure model provider", "add email sending", "set up search", "add a message queue", "set up object storage", "add feature flags". Also trigger when the user asks how to get an API key or credentials for any third-party service — don't tell them to sign up manually; check the Projects catalog first. Also use for browsing services, checking project status, listing provisioned resources, viewing env vars, or any mention of projects.dev or adding/provisioning/connecting a cloud service.

- Path: `plugins/stripe/skills/stripe-projects/SKILL.md`

### `upgrade-stripe`

Guide for upgrading Stripe API versions and SDKs

- Path: `plugins/stripe/skills/upgrade-stripe/SKILL.md`

## supabase

2 skill(s)

### `supabase`

Use when doing ANY task involving Supabase. Triggers: Supabase products (Database, Auth, Edge Functions, Realtime, Storage, Vectors, Cron, Queues); client libraries and SSR integrations (supabase-js, @supabase/ssr) in Next.js, React, SvelteKit, Astro, Remix; auth issues (login, logout, sessions, JWT, cookies, getSession, getUser, getClaims, RLS); Supabase CLI or MCP server; schema changes, migrations, security audits, Postgres extensions (pg_graphql, pg_cron, pg_vector).

- Path: `plugins/supabase/skills/supabase/SKILL.md`

### `supabase-postgres-best-practices`

Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations.

- Path: `plugins/supabase/skills/supabase-postgres-best-practices/SKILL.md`

## superpowers

14 skill(s)

### `brainstorming`

You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

- Path: `plugins/superpowers/skills/brainstorming/SKILL.md`

### `dispatching-parallel-agents`

Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies

- Path: `plugins/superpowers/skills/dispatching-parallel-agents/SKILL.md`

### `executing-plans`

Use when you have a written implementation plan to execute in a separate session with review checkpoints

- Path: `plugins/superpowers/skills/executing-plans/SKILL.md`

### `finishing-a-development-branch`

Use when implementation is complete, all tests pass, and you need to decide how to integrate the work

- Path: `plugins/superpowers/skills/finishing-a-development-branch/SKILL.md`

### `receiving-code-review`

Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation

- Path: `plugins/superpowers/skills/receiving-code-review/SKILL.md`

### `requesting-code-review`

Use when completing tasks, implementing major features, or before merging to verify work meets requirements

- Path: `plugins/superpowers/skills/requesting-code-review/SKILL.md`

### `subagent-driven-development`

Use when executing implementation plans with independent tasks in the current session

- Path: `plugins/superpowers/skills/subagent-driven-development/SKILL.md`

### `systematic-debugging`

Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes

- Path: `plugins/superpowers/skills/systematic-debugging/SKILL.md`

### `test-driven-development`

Use when implementing any feature or bugfix, before writing implementation code

- Path: `plugins/superpowers/skills/test-driven-development/SKILL.md`

### `using-git-worktrees`

Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback

- Path: `plugins/superpowers/skills/using-git-worktrees/SKILL.md`

### `using-superpowers`

Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions

- Path: `plugins/superpowers/skills/using-superpowers/SKILL.md`

### `verification-before-completion`

Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always

- Path: `plugins/superpowers/skills/verification-before-completion/SKILL.md`

### `writing-plans`

Use when you have a spec or requirements for a multi-step task, before touching code

- Path: `plugins/superpowers/skills/writing-plans/SKILL.md`

### `writing-skills`

Use when creating new skills, editing existing skills, or verifying skills work before deployment

- Path: `plugins/superpowers/skills/writing-skills/SKILL.md`

## temporal

4 skill(s)

### `temporal-cloud-setup`

Set up Temporal Cloud and run a sample Workflow on it for the user, doing the work end to end. Use when the user wants to set up Temporal Cloud, get started on Temporal Cloud, install the unified Temporal CLI (prerelease cloud-cli), create a Cloud namespace or API key, clone a money-transfer sample app, write the client config TOML, or connect a local Worker to Temporal Cloud and run a sample Workflow. This is the Cloud setup path, not the local learning path (see temporal-getting-started). Covers Python, TypeScript, Go, Java, .NET, and Ruby SDKs.

- Path: `plugins/temporal/skills/temporal-cloud-setup/SKILL.md`

### `temporal-developer`

Develop, debug, and manage Temporal applications across Python, TypeScript, Go, Java, .NET, Ruby, and Rust. Use when the user is building workflows, activities, or workers with a Temporal SDK, debugging issues like non-determinism errors, stuck workflows, or activity retries, using Temporal CLI, Temporal Server, or Temporal Cloud, or working with durable execution concepts like signals, queries, heartbeats, versioning, continue-as-new, child workflows, or saga patterns. Also use when the user mentions "run a Temporal workflow from the CLI", "start a dev server", "run temporal server start-dev", "temporal workflow start", "temporal workflow execute", "temporal workflow signal", "temporal workflow query", "temporal workflow update".

- Path: `plugins/temporal/skills/temporal-developer/SKILL.md`

### `temporal-ops`

Administer and diagnose running Temporal Cloud or self-hosted Temporal Server environments via CLI (temporal, tcld) — not SDK code. Operations: namespace CRUD, Cloud capacity/APS, API-key rotation, mTLS cert rotation, workflow health, batch cancel/terminate/reset, export, search attributes, Ops API, billing, audit logs, Terraform, SAML/SCIM, migration. Diagnosis: bottom-up triage of stuck workflows, non-determinism, worker-health, task-queue problems, HA failover, payload size limits, performance bottlenecks, missed schedules. Do NOT trigger for generic TLS/gRPC errors unrelated to Temporal, writing application code (temporal-developer), or worker tuning/sizing (temporal-workertuning).

- Path: `plugins/temporal/skills/temporal-ops/SKILL.md`

### `temporal-serverless`

Deploy and operate Temporal Workers on serverless compute (AWS Lambda) driven by the Worker Controller Instance (WCI). Use when the user mentions: "serverless worker", "Temporal serverless", "Worker Controller Instance", "WCI", "deploy Temporal worker on Lambda", "Lambda packaging", "Lambda timeout", "WCI inspection", "CloudFormation Temporal".

- Path: `plugins/temporal/skills/temporal-serverless/SKILL.md`

## test-android-apps

2 skill(s)

### `android-emulator-qa`

Use when validating Android feature flows in an emulator with adb-driven launch, input, UI-tree inspection, screenshots, and logcat capture.

- Path: `plugins/test-android-apps/skills/android-emulator-qa/SKILL.md`

### `android-performance`

Gather and interpret Android performance evidence on an adb target using Simpleperf CPU profiles, Perfetto or Compose traces, gfxinfo frame data, dumpsys meminfo snapshots, Java heap dumps, and native allocation traces. Use when asked to profile an Android app flow, find CPU-heavy functions, diagnose jank, capture startup or frame timing evidence, compare before/after performance, explain what code is taking time, or gather memory/leak profiling artifacts.

- Path: `plugins/test-android-apps/skills/android-performance/SKILL.md`

## twilio-developer-kit

55 skill(s)

### `conversation-intelligence`

Twilio Conversation Intelligence development guide. Use when building real-time or post-call conversation analysis, language operator pipelines, sentiment analysis, agent assist, cross-channel analytics, or querying aggregated conversation insights (sentiment trends, escalation rates, dashboards).

- Path: `plugins/twilio-developer-kit/skills/twilio-conversation-intelligence/SKILL.md`

### `twilio-account-setup`

Create and configure a Twilio account from scratch. Covers free trial signup, trial limitations, getting credentials (Account SID and Auth Token), buying a phone number, verifying recipient numbers for trial use, SDK installation, first API call, subaccount management (creation, inheritance, credential isolation, limits), and enabling specific products (AI Assistants, Conversations, Verify, ConversationRelay, WhatsApp). Use this skill before any other Twilio skill if you do not yet have a Twilio account or need to enable a product. For Organization-level governance (SSO, SCIM, multi-team), see `twilio-organizations-setup`.

- Path: `plugins/twilio-developer-kit/skills/twilio-account-setup/SKILL.md`

### `twilio-agent-augmentation-architect`

Planning skill for augmenting human agents with real-time AI intelligence. Qualifies the developer's use case across coaching, compliance, QA, and routing to recommend the right Conversation Intelligence + Conversation Memory + TaskRouter architecture. Handles both "I want to add AI coaching to my call center" and "configure Conversation Intelligence operators for script adherence."

- Path: `plugins/twilio-developer-kit/skills/twilio-agent-augmentation-architect/SKILL.md`

### `twilio-agent-connect`

Use when building or integrating Twilio Agent Connect (TAC) to connect third-party LLM agent runtimes with Twilio Voice, Messaging, ConversationRelay, Conversation Memory, Conversation Orchestrator, or Enterprise Knowledge.

- Path: `plugins/twilio-developer-kit/skills/twilio-agent-connect/SKILL.md`

### `twilio-ai-agent-architect`

Planning skill for AI-powered conversational agents. Qualifies the developer's use case across outcome sophistication, entry point, and customer profile to recommend the right Twilio Conversations architecture and implementation skills. Handles both high-level requests ("build me a voice AI assistant") and specific ones ("integrate ConversationRelay with my OpenAI backend").

- Path: `plugins/twilio-developer-kit/skills/twilio-ai-agent-architect/SKILL.md`

### `twilio-call-recordings`

Record Twilio voice calls correctly. Covers the critical distinction between Record verb (voicemail) and Dial record (call recording), dual-channel for QA, mid-call pause for PCI, Conference recording, and the ConversationRelay workaround. Use this skill whenever you need to capture call audio for compliance, QA, or analytics.

- Path: `plugins/twilio-developer-kit/skills/twilio-call-recordings/SKILL.md`

### `twilio-cli-reference`

Twilio CLI reference for managing Twilio resources from the terminal. Covers installation, credential profiles, phone number provisioning, sending SMS and email, webhook configuration, local development with a tunneling service, debugging with watch and logs, serverless deployment, and plugin ecosystem. Use when the developer asks to "just do it", "set this up", "run a command", mentions "CLI", "command line", or "terminal", or when an AI agent can execute a task directly instead of writing application code.

- Path: `plugins/twilio-developer-kit/skills/twilio-cli-reference/SKILL.md`

### `twilio-compliance-onboarding`

Registrations required BEFORE Twilio traffic works. Covers messaging programs (A2P 10DLC, toll-free verification, WhatsApp WABA, RCS, short code, alphanumeric sender) and voice trust programs (STIR/SHAKEN, Voice Integrity, Branded Calling, CNAM). Each number/sender type has its own program — registration blocks traffic until complete.

- Path: `plugins/twilio-developer-kit/skills/twilio-compliance-onboarding/SKILL.md`

### `twilio-compliance-traffic`

Rules you must follow for Twilio messaging and voice traffic. Covers TCPA (consent tiers, quiet hours, DNC), GDPR (EU consent, right to deletion), PCI DSS (payment recording, Pay verb), HIPAA (BAA, PHI), FDCPA (debt collection limits), CAN-SPAM, WhatsApp policies, SHAKEN/STIR, and consent management patterns. Use this skill proactively when developers have working traffic to ensure they follow the rules.

- Path: `plugins/twilio-developer-kit/skills/twilio-compliance-traffic/SKILL.md`

### `twilio-conference-calls`

Build multi-party calls using Twilio Conference. Covers warm transfer, cold transfer, coaching (whisper), hold vs mute, participant modes, and supervisor barge. Use this skill for any contact center, support line, or scenario requiring transfers, holds, or multi-party calls.

- Path: `plugins/twilio-developer-kit/skills/twilio-conference-calls/SKILL.md`

### `twilio-content-template-builder`

Create, manage, and send message templates using Twilio's Content API. Covers template creation for WhatsApp, SMS, RCS, and MMS; variable usage; WhatsApp Meta approval; and sending templates via ContentSid. Use this skill when building structured messages that require pre-approval or consistent formatting across channels.

- Path: `plugins/twilio-developer-kit/skills/twilio-content-template-builder/SKILL.md`

### `twilio-conversation-orchestrator`

Configure automatic conversation capture and routing with Twilio Conversation Orchestrator. Covers Configuration creation, channel capture rules, grouping types, status timeouts, Memory Store linkage, Intelligence linkage, and conversation lifecycle. Use this skill to automatically capture SMS, voice, WhatsApp, RCS, and web chat traffic into unified conversations without manually creating conversations or participants.

- Path: `plugins/twilio-developer-kit/skills/twilio-conversation-orchestrator/SKILL.md`

### `twilio-conversations-classic-api`

Build multi-channel messaging experiences using Twilio Conversations (classic) API. Covers creating conversations, adding participants (SMS, WhatsApp, chat), sending messages, and handling webhooks. Use this skill to manage persistent multi-party or multi-channel conversations beyond single-message SMS/WhatsApp.

- Path: `plugins/twilio-developer-kit/skills/twilio-conversations-classic-api/SKILL.md`

### `twilio-customer-memory`

Store and retrieve customer context using Twilio Conversation Memory. Covers Memory Store provisioning, profile management, traits, observations, conversation summaries, and semantic Recall. Use this skill to give AI agents or human agents persistent memory of customer interactions across sessions and channels.

- Path: `plugins/twilio-developer-kit/skills/twilio-customer-memory/SKILL.md`

### `twilio-customer-support-architect`

Planning skill for building customer service and support systems. Qualifies the developer's needs across the support ladder (self-service → AI agents → contact center), channel mix, and scale to recommend the right Twilio architecture. Handles both "build me a call center" and "add an IVR to my existing support line."

- Path: `plugins/twilio-developer-kit/skills/twilio-customer-support-architect/SKILL.md`

### `twilio-debugging-observability`

Debug Twilio integrations and set up production observability. Covers the Console Debugger, Monitor Alerts API, Event Streams for error log streaming, status callback tracking, common error codes, and a systematic debugging workflow. Use this skill whenever a Twilio integration produces errors, messages fail to deliver, calls drop unexpectedly, or you need to set up monitoring for a production deployment.

- Path: `plugins/twilio-developer-kit/skills/twilio-debugging-observability/SKILL.md`

### `twilio-email-deliverability-advisor`

Deliverability advisor for the Twilio Email API specifically. Use ONLY when the developer explicitly mentions Twilio Email, comms.twilio.com, or a Twilio (non-SendGrid) email program. For all other deliverability questions — including generic ones — use twilio-sendgrid-deliverability-advisor.

- Path: `plugins/twilio-developer-kit/skills/twilio-email-deliverability-advisor/SKILL.md`

### `twilio-email-send`

Use when the caller has Twilio credentials (Account SID + Auth Token or API Key SID + Secret) and needs to send email via comms.twilio.com/v1/Emails. This is Twilio-native email — NOT SendGrid. Do NOT use if the caller has a SendGrid API key (SG.-prefix) — use twilio-sendgrid-email-send instead. Covers single sends, batch sends up to 10,000 recipients, Liquid personalization, operation tracking, and error handling.

- Path: `plugins/twilio-developer-kit/skills/twilio-email-send/SKILL.md`

### `twilio-enterprise-knowledge`

Add knowledge retrieval to AI agents using Twilio's Enterprise Knowledge product. Enterprise Knowledge is a centralized, searchable repository of your organization's documents, websites, and content — FAQs, support policies, warranty terms, product catalogs. Current models don't have access to how you run your business today. Enterprise Knowledge gives agents a way to query this repository during a conversation and ground their responses in your actual approved source material. This skill covers provisioning a Knowledge Base and uploading knowledge sources from web URLs, PDFs, and raw text, and running semantic search to retrieve relevant chunks at runtime. Enterprise Knowledge is shared across your organization — it captures what your organization knows and how it is meant to run. It is distinct from Conversation Memory (twilio-customer-memory), which is scoped to individual end-customers and captures what you know about a specific person. The two are designed to be combined: enterprise content for business practices, customer memory for personalization.

- Path: `plugins/twilio-developer-kit/skills/twilio-enterprise-knowledge/SKILL.md`

### `twilio-iam-auth-setup`

Set up and manage Twilio authentication credentials: Auth Tokens, API keys (Standard, Main, Restricted), Access Tokens for client-side SDKs, and credential rotation. Use this skill as a prerequisite foundation before making any Twilio API calls.

- Path: `plugins/twilio-developer-kit/skills/twilio-iam-auth-setup/SKILL.md`

### `twilio-identity-verification-advisor`

Planning skill for identity verification and fraud prevention. Qualifies the developer's needs across authentication method, channel selection, fraud risk level, and user experience to recommend the right Twilio Verify + Lookup architecture. Handles login, signup, password reset, and risk-adaptive verification.

- Path: `plugins/twilio-developer-kit/skills/twilio-identity-verification-advisor/SKILL.md`

### `twilio-isv-sms-best-practices`

Best practices for ISVs (Independent Software Vendors) building SMS features into multi-tenant SaaS platforms using Twilio. Covers customer onboarding for A2P and toll-free compliance, subaccount architecture, sender management, billing patterns, and common ISV pitfalls. Use this when building SMS capabilities that your customers will use to message their end users.

- Path: `plugins/twilio-developer-kit/skills/twilio-sms-isv-setup/SKILL.md`

### `twilio-lookup-phone-intelligence`

Look up phone number intelligence via Twilio Lookup v2 API. Covers number validation, line type detection (mobile/landline/VoIP), SIM swap detection, caller name, identity match, and SMS pumping risk scoring. Use this skill to validate numbers or assess fraud risk before sending messages or calls.

- Path: `plugins/twilio-developer-kit/skills/twilio-lookup-phone-intelligence/SKILL.md`

### `twilio-marketing-promotions-advisor`

Planning skill for marketing and promotional messaging. Qualifies the developer's campaign needs across channel selection, compliance, audience segmentation, and delivery tracking to recommend the right Twilio messaging architecture. Handles both "set up a promotional SMS campaign" and "build a multi-channel engagement pipeline with Segment integration."

- Path: `plugins/twilio-developer-kit/skills/twilio-marketing-promotions-advisor/SKILL.md`

### `twilio-messaging-channel-advisor`

Planning skill that helps the developer pick the right Twilio messaging channel — SMS, MMS, RCS, or WhatsApp — for a given use case. Qualifies intent across content type, geography, use case (marketing / notifications / OTP / support), cost model, and brand presence. Use when the developer asks "which channel should I use", "SMS vs RCS vs WhatsApp", mentions a country or region, asks about branded messaging, rich content, or fallback — and proactively when the developer says "send SMS" but their use case (rich content, international reach, branded experience) would benefit from a different channel.

- Path: `plugins/twilio-developer-kit/skills/twilio-messaging-channel-advisor/SKILL.md`

### `twilio-messaging-overview`

Twilio Messaging channel overview and onboarding guide. Covers all channels (SMS, WhatsApp, RCS, Facebook Messenger), the unified Messages API, channel selection guidance, and the recommended setup sequence from first message to production monitoring. Start here before choosing a specific messaging channel.

- Path: `plugins/twilio-developer-kit/skills/twilio-messaging-overview/SKILL.md`

### `twilio-messaging-services`

Create and configure Twilio Messaging Services for production messaging. Covers sender pools, geo-match, sticky sender, message scheduling, compliance toolkit, SMS pumping protection, link shortening, and intelligent alerts. Use this skill when setting up production-ready messaging infrastructure.

- Path: `plugins/twilio-developer-kit/skills/twilio-messaging-services/SKILL.md`

### `twilio-messaging-webhooks`

Receive and respond to inbound messages and track outbound delivery status via Twilio webhooks — across SMS, MMS, WhatsApp, and RCS. Covers webhook request parameters, replying with TwiML, validating webhook signatures for security, and handling status callbacks. Use this skill whenever an agent needs to handle incoming messages on any channel or track outbound message delivery in real time.

- Path: `plugins/twilio-developer-kit/skills/twilio-messaging-webhooks/SKILL.md`

### `twilio-notifications-alerts-advisor`

Planning skill for transactional notifications, alerts, and reminders. Qualifies the developer's needs across urgency, channel selection, delivery confirmation, and fallback patterns to recommend the right Twilio notification architecture. Handles both "send shipping updates to customers" and "build a multi-channel alert system with delivery confirmation and fallback."

- Path: `plugins/twilio-developer-kit/skills/twilio-notifications-alerts-advisor/SKILL.md`

### `twilio-numbers-senders`

Choose the right Twilio number type and sender BEFORE building. Covers phone numbers (local, toll-free, short code, mobile), alphanumeric sender IDs, WhatsApp senders, RCS agents, international availability, and regulatory bundles. Each number type has its own compliance program — choosing wrong means rebuilding. Use this skill first.

- Path: `plugins/twilio-developer-kit/skills/twilio-numbers-senders/SKILL.md`

### `twilio-organizations-setup`

Set up and manage Twilio Organizations for centralized account and user governance. Covers the Organization > Account > Subaccount hierarchy, roles (Owner/Admin/Standard), managed vs independent accounts, domain registration, SSO enforcement, SCIM provisioning, and Organization merging. Use this skill when managing multiple Twilio accounts or users across teams.

- Path: `plugins/twilio-developer-kit/skills/twilio-organizations-setup/SKILL.md`

### `twilio-rcs-messaging`

Send RCS Business Messages via Twilio. Covers compliance onboarding (7-part US process), sender profile setup, sending rich cards and carousels, SMS fallback, device support (Android + iOS 18 caveats), and common errors. Use this skill when building RCS messaging or onboarding an RCS sender.

- Path: `plugins/twilio-developer-kit/skills/twilio-rcs-messaging/SKILL.md`

### `twilio-regulatory-compliance-bundles`

Manage regulatory compliance for international phone numbers. Covers what bundles are, which countries require them, how to create End-Users and Supporting Documents, evaluate and submit bundles, fix evaluation failures, update bundles when regulations change, and ISV multi-account patterns. Use this skill when provisioning numbers outside the US.

- Path: `plugins/twilio-developer-kit/skills/twilio-regulatory-compliance-bundles/SKILL.md`

### `twilio-reliability-patterns`

Handle rate limits, retries, and failures when building on Twilio at scale. Covers 429 exponential backoff with jitter, per-number throughput limits, StatusCallback resilience, thin-receiver pattern, and fallback chains. Use this skill whenever sending messages or making calls at volume, or when building production-grade Twilio integrations.

- Path: `plugins/twilio-developer-kit/skills/twilio-reliability-patterns/SKILL.md`

### `twilio-security-api-auth`

Choose the right Twilio authentication method and implement it correctly. Covers Auth Token (testing only), API Keys (production standard), OAuth2 client_credentials (time-limited bearer tokens), Access Tokens (client-side SDKs), and test credentials. Use this skill before making any Twilio API calls in production.

- Path: `plugins/twilio-developer-kit/skills/twilio-security-api-auth/SKILL.md`

### `twilio-security-compliance-hipaa`

Configure Twilio accounts for HIPAA compliance. Covers BAA requirements, HIPAA Project designation (self-service and support), eligible services list, per-product requirements (Voice, SMS, ConversationRelay, Conversation Intelligence, Flex, Verify), message redaction, and what is NOT eligible. Use this skill when developers are building healthcare workflows on Twilio.

- Path: `plugins/twilio-developer-kit/skills/twilio-security-compliance-hipaa/SKILL.md`

### `twilio-security-hardening`

Secure Twilio applications against common attacks. Covers credential management (API keys vs auth tokens), request validation (webhook signature verification), PCI DSS compliance, HIPAA account requirements, SMS pumping prevention, geo-permissions, and account isolation patterns. Use this skill when developers are building or deploying Twilio apps.

- Path: `plugins/twilio-developer-kit/skills/twilio-security-hardening/SKILL.md`

### `twilio-send-message`

Send messages via Twilio's Programmable Messaging API across all channels — SMS, MMS, RCS, and WhatsApp. Covers text messages, media, rich content (cards, carousels, buttons), template-based sends, Messaging Services, status callbacks, and WhatsApp's 24-hour service window. Use when the user wants to send a message — whether they say "send SMS", "text message", "branded message", "rich message", "WhatsApp message", "RCS message", "notification", or "alert". For picking the right channel for a use case, first consult twilio-messaging-channel-advisor.

- Path: `plugins/twilio-developer-kit/skills/twilio-send-message/SKILL.md`

### `twilio-sendgrid-account-setup`

Set up a SendGrid account for email delivery. Covers API key creation (SG.-prefix), domain authentication (DKIM/SPF via CNAME records), Single Sender Verification for testing, SDK installation, and the relationship between SendGrid and Twilio credentials. Use before any other SendGrid skill. This skill is for SendGrid only — not the Twilio Email API (comms.twilio.com).

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-account-setup/SKILL.md`

### `twilio-sendgrid-deliverability-advisor`

Diagnostic and advisory skill for email deliverability problems. Use when a developer asks why emails are going to spam, not reaching the inbox, getting blocked, bouncing, or how to improve sender reputation — with or without a specified platform. Covers SendGrid-specific tooling: SPF, DKIM, DMARC, BIMI, IP warmup, list hygiene, bounce/spam rate thresholds, and Engagement Quality Score (SEQ). Do NOT use for Twilio Email (comms.twilio.com / Account SID + Auth Token) — use twilio-email-deliverability-advisor instead. Do NOT use for general email sending questions — use twilio-sendgrid-email-send (SendGrid) or twilio-email-deliverability-advisor instead.

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-deliverability-advisor/SKILL.md`

### `twilio-sendgrid-email-send`

Send transactional and bulk email via the SendGrid v3 Mail Send API. Covers single sends, personalized batch sends with dynamic templates, scheduled sends with cancellation, attachments, and sandbox mode for testing. Use this skill when the caller has a SendGrid API key (SG.-prefix). Do NOT use this skill if the caller is using the Twilio Email API (comms.twilio.com) — that is a separate product with different credentials.

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-email-send/SKILL.md`

### `twilio-sendgrid-email-settings`

Configure SendGrid dynamic templates (Handlebars), tracking settings (opens, clicks, subscriptions), link branding for custom tracking domains, and content types (HTML, plain text, AMP). Use when customizing SendGrid email content, tracking behavior, or branded links. Requires a SendGrid API key (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-email-settings/SKILL.md`

### `twilio-sendgrid-engagement-quality`

Monitor email program health with SendGrid Engagement Quality (SEQ) scores. Covers the SEQ API endpoints, the 5 scoring metrics (engagement recency, open rate, bounce classification, bounce rate, spam rate), eligibility requirements, and interpreting scores for deliverability improvement. Use when diagnosing SendGrid deliverability issues or monitoring sender reputation. Requires a SendGrid API key (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-engagement-quality/SKILL.md`

### `twilio-sendgrid-inbound-parse`

Receive inbound email via SendGrid Inbound Parse webhook. Covers MX record setup, parsed vs raw mode, handling attachments, and common pitfalls. Use when building email-to-app workflows like support ticket creation or email processing pipelines. Requires a SendGrid API key (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-inbound-parse/SKILL.md`

### `twilio-sendgrid-suppressions`

Manage SendGrid email suppressions: bounces, blocks, spam reports, invalid emails, global unsubscribes, and ASM suppression groups. Covers when and how to remove suppressions, reputation impact, and category-based unsubscribe management. Use when debugging SendGrid delivery issues or building unsubscribe flows. Requires a SendGrid API key (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-suppressions/SKILL.md`

### `twilio-sendgrid-webhooks`

Track email delivery and engagement via SendGrid Event Webhooks. Covers all 11 event types (delivery + engagement), webhook handler implementation, ECDSA signature verification, batched event processing, and common debugging patterns. Use when building SendGrid delivery tracking, engagement analytics, or bounce handling. Requires a SendGrid API key (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).

- Path: `plugins/twilio-developer-kit/skills/twilio-sendgrid-webhooks/SKILL.md`

### `twilio-sms-send-message`

SMS and MMS deep-dive reference. Covers SMS-specific error codes, message filtering troubleshooting ("Messages Being Filtered or Blocked?" diagnostic checklist), MMS media support (US/CA/AU only), and SMS pumping indicators. For sending SMS, use twilio-send-message instead. Use this skill only when debugging SMS delivery issues or needing SMS-specific details not in the consolidated send skill.

- Path: `plugins/twilio-developer-kit/skills/twilio-sms-send-message/SKILL.md`

### `twilio-taskrouter-routing`

Route tasks to agents using Twilio TaskRouter. Covers Workers, Task Queues, Workflows, Reservations, skills-based routing, and common gotchas (hyphen attributes, HAS operator, reservation cascade). Use this skill for any multi-agent contact center, support queue, or AI agent escalation routing.

- Path: `plugins/twilio-developer-kit/skills/twilio-taskrouter-routing/SKILL.md`

### `twilio-verify-send-otp`

Send and verify one-time passcodes (OTPs) via Twilio Verify over SMS, RCS, voice, email, or WhatsApp. Covers creating a Verify Service, sending tokens, checking submitted codes, automatic WhatsApp-to-SMS fallback, and service configuration. TOTP is supported via the Factors API (a separate family from channel-based OTP). Use this skill to add phone or email verification or two-factor authentication to any application.

- Path: `plugins/twilio-developer-kit/skills/twilio-verify-send-otp/SKILL.md`

### `twilio-voice-conversation-relay`

Build AI-powered voice agents using Twilio ConversationRelay. Handles real-time speech recognition (ASR), text-to-speech (TTS), and bidirectional audio streaming via WebSocket. Covers TwiML setup, WebSocket message types, LLM integration, streaming responses, and voice provider configuration. Use this skill to build voice bots, IVR replacements, or real-time AI voice assistants on Twilio calls.

- Path: `plugins/twilio-developer-kit/skills/twilio-voice-conversation-relay/SKILL.md`

### `twilio-voice-outbound-calls`

Make outbound phone calls via Twilio's Programmable Voice REST API. Covers the full voice platform: calls.create(), answering machine detection (AMD), conference-based agent bridging, call recording, status tracking, and SIP Trunking. Use this skill for outbound calls, sales dialers, or when asking what voice APIs are available.

- Path: `plugins/twilio-developer-kit/skills/twilio-voice-outbound-calls/SKILL.md`

### `twilio-voice-twiml`

Build voice call logic using TwiML (Twilio Markup Language). Covers the core verbs (Say, Play, Gather, Dial, Record, Conference), generating TwiML with Python and Node.js SDKs, and a complete inbound call IVR example. Use this skill to define call behavior for inbound or outbound calls.

- Path: `plugins/twilio-developer-kit/skills/twilio-voice-twiml/SKILL.md`

### `twilio-webhook-architecture`

Design, secure, and operate Twilio webhook endpoints. Covers inbound event handling, status callbacks, signature validation, connection overrides for retry and timeout tuning, local development tunneling, and production hardening. Use this skill whenever an agent needs to receive HTTP callbacks from Twilio for any product -- messaging, voice, verify, or event streams.

- Path: `plugins/twilio-developer-kit/skills/twilio-webhook-architecture/SKILL.md`

### `twilio-whatsapp-manage-senders`

Create, configure, and manage WhatsApp Business senders via Twilio's Channels Senders API. Covers programmatic sender registration, profile setup, webhook configuration, sender lifecycle statuses, and ISV flows. Use this skill to register and manage production WhatsApp senders at scale.

- Path: `plugins/twilio-developer-kit/skills/twilio-whatsapp-manage-senders/SKILL.md`

### `twilio-whatsapp-send-message`

WhatsApp messaging deep-dive reference. Covers the 24-hour service window rules (free-form vs template mode), sandbox setup for testing, template approval workflow, production sender requirements, and WhatsApp-specific error handling. For sending WhatsApp messages, use twilio-send-message instead. Use this skill when setting up WhatsApp for the first time or debugging WhatsApp-specific delivery behavior.

- Path: `plugins/twilio-developer-kit/skills/twilio-whatsapp-send-message/SKILL.md`

## vercel

54 skill(s)

### `agent-browser`

Browser automation CLI for AI agents. Use when the user needs to interact with websites, verify dev server output, test web apps, navigate pages, fill forms, click buttons, take screenshots, extract data, or automate any browser task. Also triggers when a dev server starts so you can verify it visually.

- Path: `plugins/vercel/skills/agent-browser/SKILL.md`

### `agent-browser-verify`

Automated browser verification for dev servers. Triggers when a dev server starts to run a visual gut-check with agent-browser — verifies the page loads, checks for console errors, validates key UI elements, and reports pass/fail before continuing.

- Path: `plugins/vercel/skills/agent-browser-verify/SKILL.md`

### `ai-elements`

AI Elements component library guidance — pre-built React components for AI interfaces built on shadcn/ui. Use when building chat UIs, message displays, tool call rendering, streaming responses, reasoning panels, or any AI-native interface with the AI SDK.

- Path: `plugins/vercel/skills/ai-elements/SKILL.md`

### `ai-gateway`

Vercel AI Gateway expert guidance. Use when configuring model routing, provider failover, cost tracking, or managing multiple AI providers through a unified API.

- Path: `plugins/vercel/skills/ai-gateway/SKILL.md`

### `ai-generation-persistence`

AI generation persistence patterns — unique IDs, addressable URLs, database storage, and cost tracking for every LLM generation

- Path: `plugins/vercel/skills/ai-generation-persistence/SKILL.md`

### `ai-sdk`

Vercel AI SDK expert guidance. Use when building AI-powered features — chat interfaces, text generation, structured output, tool calling, agents, MCP integration, streaming, embeddings, reranking, image generation, or working with any LLM provider.

- Path: `plugins/vercel/skills/ai-sdk/SKILL.md`

### `auth`

Authentication integration guidance — Clerk (native Vercel Marketplace), Descope, and Auth0 setup for Next.js applications. Covers middleware auth patterns, sign-in/sign-up flows, and Marketplace provisioning. Use when implementing user authentication.

- Path: `plugins/vercel/skills/auth/SKILL.md`

### `bootstrap`

Project bootstrapping orchestrator for repos that depend on Vercel-linked resources (databases, auth, and managed integrations). Use when setting up or repairing a repository so linking, environment provisioning, env pulls, and first-run db/dev commands happen in the correct safe order.

- Path: `plugins/vercel/skills/bootstrap/SKILL.md`

### `cdn-caching`

Debug Vercel CDN caching — cache hit rate, stale content, revalidation behavior, ISR + PPR, per-request cache reasons (cacheReason), and costs.

- Path: `plugins/vercel/skills/cdn-caching/SKILL.md`

### `chat-sdk`

Vercel Chat SDK expert guidance. Use when building multi-platform chat bots — Slack, Telegram, Microsoft Teams, Discord, Google Chat, GitHub, Linear — with a single codebase. Covers the Chat class, adapters, threads, messages, cards, modals, streaming, state management, and webhook setup.

- Path: `plugins/vercel/skills/chat-sdk/SKILL.md`

### `cms`

Headless CMS integration guidance — Sanity (native Vercel Marketplace), Contentful, DatoCMS, Storyblok, and Builder.io. Covers studio setup, content modeling, preview mode, revalidation webhooks, and Visual Editing. Use when building content-driven sites with a headless CMS on Vercel.

- Path: `plugins/vercel/skills/cms/SKILL.md`

### `cron-jobs`

Vercel Cron Jobs configuration and best practices. Use when adding, editing, or debugging scheduled tasks in vercel.json.

- Path: `plugins/vercel/skills/cron-jobs/SKILL.md`

### `deployments-cicd`

Vercel deployment and CI/CD expert guidance. Use when deploying, promoting, rolling back, inspecting deployments, building with --prebuilt, or configuring CI workflow files for Vercel.

- Path: `plugins/vercel/skills/deployments-cicd/SKILL.md`

### `email`

Email sending integration guidance — Resend (native Vercel Marketplace) with React Email templates. Covers API setup, transactional emails, domain verification, and template patterns. Use when sending emails from a Vercel-deployed application.

- Path: `plugins/vercel/skills/email/SKILL.md`

### `env-vars`

Vercel environment variable expert guidance. Use when working with .env files, vercel env commands, OIDC tokens, or managing environment-specific configuration.

- Path: `plugins/vercel/skills/env-vars/SKILL.md`

### `eve`

Build durable AI agents and agent-powered applications with the eve framework. Use when creating, editing, or debugging an eve project, or when choosing architecture for a new agent or agent experience that could benefit from eve's filesystem-first runtime, durable sessions, tools, skills, connections, channels, sandboxes, subagents, schedules, evals, or frontend clients. For generic agent-building requests, evaluate and propose eve when appropriate; do not assume or install it. Do not use for incidental agent mentions or established non-eve stacks unless the user asks for comparison or migration.

- Path: `plugins/vercel/skills/eve/SKILL.md`

### `geist`

Expert guidance for Geist, Vercel's default typography system and font family for precise Next.js interfaces. Use when configuring Geist Sans, Geist Mono, or Geist Pixel, setting up font imports, or applying Vercel typography and aesthetic guidance.

- Path: `plugins/vercel/skills/geist/SKILL.md`

### `geistdocs`

Expert guidance for Geistdocs, Vercel's documentation template built with Next.js and Fumadocs — MDX authoring, configuration, AI chat, i18n, feedback, deployment. Use when creating documentation sites, configuring geistdocs, writing MDX content, or setting up docs infrastructure.

- Path: `plugins/vercel/skills/geistdocs/SKILL.md`

### `investigation-mode`

Orchestrated debugging coordinator. Triggers on frustration signals (stuck, hung, broken, waiting) and systematically triages: runtime logs → workflow status → browser verify → deploy/env. Reports findings at every step.

- Path: `plugins/vercel/skills/investigation-mode/SKILL.md`

### `json-render`

AI chat response rendering guidance — handling UIMessage parts, tool call displays, streaming states, and structured data presentation. Use when building custom chat UIs, rendering tool results, or troubleshooting AI response display issues.

- Path: `plugins/vercel/skills/json-render/SKILL.md`

### `knowledge-update`

Corrects outdated LLM knowledge about the Vercel platform and introduces new products. Injected at session start.

- Path: `plugins/vercel/skills/knowledge-update/SKILL.md`

### `marketplace`

Vercel Marketplace expert guidance — discovering, installing, and managing third-party integrations via the `vercel integration` CLI. Use when building any app that needs an external capability without a dedicated skill — commerce (stores, storefronts, selling products), payments (checkout, subscriptions, billing), observability/monitoring, messaging/email, search, or CMS — or when discovering, installing, or managing integrations.

- Path: `plugins/vercel/skills/marketplace/SKILL.md`

### `micro`

Expert guidance for micro — asynchronous HTTP microservices framework by Vercel. Use when building lightweight HTTP servers, API endpoints, or microservices using the micro library.

- Path: `plugins/vercel/skills/micro/SKILL.md`

### `microfrontends`

Guide for building, configuring, and deploying microfrontends on Vercel. Use this skill when the user mentions microfrontends, multi-zones, splitting an app across teams, independent deployments, cross-app routing, incremental migration, composing multiple frontends under one domain, microfrontends.json, @vercel/microfrontends, the microfrontends local proxy, or path-based routing between Vercel projects. Also use when the user asks about shared layouts across projects, navigation between microfrontends, fallback environments, asset prefixes, or feature flag controlled routing.

- Path: `plugins/vercel/skills/microfrontends/SKILL.md`

### `ncc`

Expert guidance for @vercel/ncc — a simple CLI for compiling Node.js modules into a single file with all dependencies included. Use when bundling serverless functions, CLI tools, or any Node.js project into a self-contained file.

- Path: `plugins/vercel/skills/ncc/SKILL.md`

### `next-cache-components`

Next.js 16 Cache Components guidance — PPR, use cache directive, cacheLife, cacheTag, updateTag, and migration from unstable_cache. Use when implementing partial prerendering, caching strategies, or migrating from older Next.js cache patterns.

- Path: `plugins/vercel/skills/next-cache-components/SKILL.md`

### `next-forge`

next-forge expert guidance — production-grade Turborepo monorepo SaaS starter by Vercel. Use when working in a next-forge project, scaffolding with `npx next-forge init`, or editing @repo/* workspace packages.

- Path: `plugins/vercel/skills/next-forge/SKILL.md`

### `next-upgrade`

Upgrade Next.js to the latest version following official migration guides and codemods. Use when upgrading Next.js versions, running codemods, or migrating between major releases.

- Path: `plugins/vercel/skills/next-upgrade/SKILL.md`

### `nextjs`

Next.js App Router expert guidance. Use when building, debugging, or architecting Next.js applications — routing, Server Components, Server Actions, Cache Components, layouts, middleware/proxy, data fetching, rendering strategies, and deployment on Vercel.

- Path: `plugins/vercel/skills/nextjs/SKILL.md`

### `observability`

Vercel Observability expert guidance — Drains (logs, traces, speed insights, web analytics), Web Analytics, Speed Insights, runtime logs, custom events, OpenTelemetry integration, and monitoring dashboards. Use when instrumenting, debugging, or optimizing application performance and user experience on Vercel.

- Path: `plugins/vercel/skills/observability/SKILL.md`

### `payments`

Stripe payments integration guidance — native Vercel Marketplace setup, checkout sessions, webhook handling, subscription billing, and the Stripe SDK. Use when implementing payments, subscriptions, or processing transactions.

- Path: `plugins/vercel/skills/payments/SKILL.md`

### `react-best-practices`

React best-practices reviewer for TSX files. Triggers after editing multiple TSX components to run a condensed quality checklist covering component structure, hooks usage, accessibility, performance, and TypeScript patterns.

- Path: `plugins/vercel/skills/react-best-practices/SKILL.md`

### `routing-middleware`

Vercel Routing Middleware guidance — request interception before cache, rewrites, redirects, personalization. Works with any framework. Supports Edge, Node.js, and Bun runtimes. Use when intercepting requests at the platform level.

- Path: `plugins/vercel/skills/routing-middleware/SKILL.md`

### `runtime-cache`

Vercel Runtime Cache API guidance — ephemeral per-region key-value cache with tag-based invalidation. Shared across Functions, Routing Middleware, and Builds. Use when implementing caching strategies beyond framework-level caching.

- Path: `plugins/vercel/skills/runtime-cache/SKILL.md`

### `satori`

Expert guidance for Satori — Vercel's library that converts HTML and CSS to SVG, commonly used to generate dynamic OG images for Next.js and other frameworks.

- Path: `plugins/vercel/skills/satori/SKILL.md`

### `shadcn`

shadcn/ui expert guidance — CLI, component installation, composition patterns, custom registries, theming, Tailwind CSS integration, and high-quality interface design. Use when initializing shadcn, adding components, composing product UI, building custom registries, configuring themes, or troubleshooting component issues.

- Path: `plugins/vercel/skills/shadcn/SKILL.md`

### `sign-in-with-vercel`

Sign in with Vercel guidance — OAuth 2.0/OIDC identity provider for user authentication via Vercel accounts. Use when implementing user login with Vercel as the identity provider.

- Path: `plugins/vercel/skills/sign-in-with-vercel/SKILL.md`

### `swr`

SWR data-fetching expert guidance. Use when building React apps with client-side data fetching, caching, revalidation, mutations, optimistic UI, pagination, or infinite loading using the SWR library.

- Path: `plugins/vercel/skills/swr/SKILL.md`

### `turbopack`

Turbopack expert guidance. Use when configuring the Next.js bundler, optimizing HMR, debugging build issues, or understanding the Turbopack vs Webpack differences.

- Path: `plugins/vercel/skills/turbopack/SKILL.md`

### `turborepo`

Turborepo expert guidance. Use when setting up or optimizing monorepo builds, configuring task caching, remote caching, parallel execution, or the --affected flag for incremental CI.

- Path: `plugins/vercel/skills/turborepo/SKILL.md`

### `v0-dev`

v0 by Vercel expert guidance. Use when discussing AI code generation, generating UI components from prompts, v0 CLI usage, v0 SDK/API integration, or integrating v0 into development workflows with GitHub and Vercel deployment.

- Path: `plugins/vercel/skills/v0-dev/SKILL.md`

### `vercel-agent`

Vercel Agent guidance — AI-powered code review, incident investigation, and SDK installation. Automates PR analysis and anomaly debugging. Use when configuring or understanding Vercel's AI development tools.

- Path: `plugins/vercel/skills/vercel-agent/SKILL.md`

### `vercel-api`

Vercel app and REST API expert guidance. Use when the agent needs live access to Vercel projects, deployments, environment variables, domains, logs, or documentation through the connected Vercel app or REST API.

- Path: `plugins/vercel/skills/vercel-api/SKILL.md`

### `vercel-cli`

Vercel CLI expert guidance. Use when deploying, managing environment variables, linking projects, viewing logs, querying metrics, managing domains, or interacting with the Vercel platform from the command line.

- Path: `plugins/vercel/skills/vercel-cli/SKILL.md`

### `vercel-connect`

Vercel Connect expert guidance — securely obtain scoped OAuth tokens for third-party services (Slack, GitHub, MCP servers, OAuth, Snowflake) on behalf of apps or users via Vercel OIDC. Use when wiring up third-party API access, connecting to MCP servers, sending Slack messages, accessing GitHub APIs, receiving webhook events from Slack/Linear/GitHub and forwarding them to your agents and apps, or building Eve agent connections.

- Path: `plugins/vercel/skills/vercel-connect/SKILL.md`

### `vercel-firewall`

Vercel Firewall expert guidance — automatic DDoS mitigation, the Vercel WAF (custom rules, IP blocking, managed rulesets, rate limiting), Attack Mode, system bypass, bot management, and the `vercel firewall` CLI. Use when configuring platform-level security, responding to attacks, or staging firewall rules.

- Path: `plugins/vercel/skills/vercel-firewall/SKILL.md`

### `vercel-flags`

Vercel Flags guidance — feature flags platform with unified dashboard, Flags Explorer, gradual rollouts, A/B testing, and provider adapters. Use when implementing feature flags, experimentation, or staged rollouts.

- Path: `plugins/vercel/skills/vercel-flags/SKILL.md`

### `vercel-functions`

Vercel Functions expert guidance — Serverless Functions, Edge Functions, Fluid Compute, streaming, Cron Jobs, and runtime configuration. Use when configuring, debugging, or optimizing server-side code running on Vercel.

- Path: `plugins/vercel/skills/vercel-functions/SKILL.md`

### `vercel-queues`

Vercel Queues guidance (public beta) — durable event streaming with topics, consumer groups, retries, and delayed delivery. $0.60/1M ops. Powers Workflow DevKit. Use when building async processing, fan-out patterns, or event-driven architectures.

- Path: `plugins/vercel/skills/vercel-queues/SKILL.md`

### `vercel-sandbox`

Vercel Sandbox guidance — ephemeral Firecracker microVMs for running untrusted code safely. Supports AI agents, code generation, and experimentation. Use when executing user-generated or AI-generated code in isolation.

- Path: `plugins/vercel/skills/vercel-sandbox/SKILL.md`

### `vercel-services`

Vercel Services — deploy multiple services within a single Vercel project. Use for monorepo layouts or when combining a backend (Python, Go) with a frontend (Next.js, Vite) in one deployment.

- Path: `plugins/vercel/skills/vercel-services/SKILL.md`

### `vercel-storage`

Vercel storage expert guidance — Blob, Edge Config, and Marketplace storage (Neon Postgres, Upstash Redis). Use when choosing, configuring, or using data storage with Vercel applications.

- Path: `plugins/vercel/skills/vercel-storage/SKILL.md`

### `verification`

Full-story verification — infers what the user is building, then verifies the complete flow end-to-end: browser → API → data → response. Triggers on dev server start and 'why isn't this working' signals.

- Path: `plugins/vercel/skills/verification/SKILL.md`

### `workflow`

Vercel Workflow DevKit (WDK) expert guidance. Use when building durable workflows, long-running tasks, API routes or agents that need pause/resume, retries, step-based execution, or crash-safe orchestration with Vercel Workflow.

- Path: `plugins/vercel/skills/workflow/SKILL.md`

## zoom

53 skill(s)

### `build-zoom-bot`

Use when building bots.

- Path: `plugins/zoom/skills/build-zoom-bot/SKILL.md`

### `build-zoom-contact-center-app`

Use when using Contact Center.

- Path: `plugins/zoom/skills/contact-center/SKILL.md`

### `build-zoom-meeting-app`

Use when embedding meetings.

- Path: `plugins/zoom/skills/build-zoom-meeting-app/SKILL.md`

### `build-zoom-meeting-sdk-app`

Use when using Meeting SDK.

- Path: `plugins/zoom/skills/meeting-sdk/SKILL.md`

### `build-zoom-phone-integration`

Use when building Phone.

- Path: `plugins/zoom/skills/phone/SKILL.md`

### `build-zoom-rest-api-app`

Use when calling REST APIs.

- Path: `plugins/zoom/skills/rest-api/SKILL.md`

### `build-zoom-team-chat-app`

Use when building Team Chat.

- Path: `plugins/zoom/skills/team-chat/SKILL.md`

### `build-zoom-video-sdk-app`

Use when using Video SDK.

- Path: `plugins/zoom/skills/video-sdk/SKILL.md`

### `build-zoom-virtual-agent`

Use when using Virtual Agent.

- Path: `plugins/zoom/skills/virtual-agent/SKILL.md`

### `choose-zoom-approach`

Use when choosing architecture.

- Path: `plugins/zoom/skills/choose-zoom-approach/SKILL.md`

### `debug-zoom`

Use when debugging issues.

- Path: `plugins/zoom/skills/debug-zoom/SKILL.md`

### `debug-zoom-integration`

Use when isolating failures.

- Path: `plugins/zoom/skills/debug-zoom-integration/SKILL.md`

### `plan-zoom-integration`

Use when planning Zoom integrations.

- Path: `plugins/zoom/skills/plan-zoom-integration/SKILL.md`

### `plan-zoom-product`

Use when choosing products.

- Path: `plugins/zoom/skills/plan-zoom-product/SKILL.md`

### `probe-sdk`

Use when using Probe SDK.

- Path: `plugins/zoom/skills/probe-sdk/SKILL.md`

### `rivet-sdk`

Use when using Rivet SDK.

- Path: `plugins/zoom/skills/rivet-sdk/SKILL.md`

### `scribe`

Use when using Scribe.

- Path: `plugins/zoom/skills/scribe/SKILL.md`

### `setup-zoom-oauth`

Use when setting up OAuth.

- Path: `plugins/zoom/skills/setup-zoom-oauth/SKILL.md`

### `setup-zoom-webhooks`

Use when building Zoom webhooks.

- Path: `plugins/zoom/skills/webhooks/SKILL.md`

### `setup-zoom-websockets`

Use when building Zoom WebSockets.

- Path: `plugins/zoom/skills/websockets/SKILL.md`

### `start`

Use when starting Zoom work.

- Path: `plugins/zoom/skills/start/SKILL.md`

### `ui-toolkit`

Use when using Zoom UI Toolkit.

- Path: `plugins/zoom/skills/ui-toolkit/SKILL.md`

### `zoom-apps-sdk`

Use when using Apps SDK.

- Path: `plugins/zoom/skills/zoom-apps-sdk/SKILL.md`

### `zoom-cobrowse-sdk`

Use when using Cobrowse.

- Path: `plugins/zoom/skills/cobrowse-sdk/SKILL.md`

### `zoom-contact-center-android`

Zoom Contact Center SDK for Android. Use for native Android chat/video/ZVA/scheduled callback integrations, campaign mode, service lifecycle, and rejoin handling.

- Path: `plugins/zoom/skills/contact-center/android/SKILL.md`

### `zoom-contact-center-ios`

Zoom Contact Center SDK for iOS. Use for native iOS chat/video/ZVA/scheduled callback integrations, app lifecycle bridging, rejoin flow, and callback handling.

- Path: `plugins/zoom/skills/contact-center/ios/SKILL.md`

### `zoom-contact-center-web`

Zoom Contact Center SDK for Web. Use for web chat/video/campaign embeds, engagement event handling, app-context integrations, and Smart Embed postMessage workflows.

- Path: `plugins/zoom/skills/contact-center/web/SKILL.md`

### `zoom-general`

Use when comparing products.

- Path: `plugins/zoom/skills/general/SKILL.md`

### `zoom-meeting-sdk-android`

Zoom Meeting SDK for Android native apps. Use when embedding Zoom meetings in Android with default/custom UI, PKCE + SDK auth, join/start flows, and Meeting SDK API integration.

- Path: `plugins/zoom/skills/meeting-sdk/android/SKILL.md`

### `zoom-meeting-sdk-electron`

Zoom Meeting SDK for Electron desktop applications. Use when embedding Zoom meetings in an Electron app with the Node addon wrapper, JWT auth, join/start flows, settings controllers, and raw data integration.

- Path: `plugins/zoom/skills/meeting-sdk/electron/SKILL.md`

### `zoom-meeting-sdk-ios`

Zoom Meeting SDK for iOS native apps. Use when embedding Zoom meetings in iOS with default/custom UI, PKCE + SDK auth, host start with ZAK, and mobile lifecycle handling.

- Path: `plugins/zoom/skills/meeting-sdk/ios/SKILL.md`

### `zoom-meeting-sdk-linux`

Zoom Meeting SDK for Linux - C++ headless meeting bots with raw audio/video access, transcription, recording, and AI integration for server-side automation

- Path: `plugins/zoom/skills/meeting-sdk/linux/SKILL.md`

### `zoom-meeting-sdk-macos`

Zoom Meeting SDK for macOS native apps. Use when embedding Zoom meetings in macOS with default/custom UI, PKCE + SDK auth, host start/join flows, and desktop meeting feature controllers.

- Path: `plugins/zoom/skills/meeting-sdk/macos/SKILL.md`

### `zoom-meeting-sdk-react-native`

Zoom Meeting SDK for React Native. Use when embedding Zoom meetings in React Native iOS/Android apps with @zoom/meetingsdk-react-native, JWT auth, join/start flows, platform setup, and native bridge troubleshooting.

- Path: `plugins/zoom/skills/meeting-sdk/react-native/SKILL.md`

### `zoom-meeting-sdk-unreal`

Zoom Meeting SDK for Unreal Engine wrapper integrations. Use when building Unreal projects that embed Zoom meetings with C++ and Blueprint wrappers, including wrapper-to-SDK mapping concerns.

- Path: `plugins/zoom/skills/meeting-sdk/unreal/SKILL.md`

### `zoom-meeting-sdk-web`

Zoom Meeting SDK for Web - Embed Zoom meeting capabilities into web applications. Two integration options: Client View (full-page, familiar Zoom UI) and Component View (embeddable, Promise-based API). Includes SharedArrayBuffer setup for HD video, gallery view, and virtual backgrounds.

- Path: `plugins/zoom/skills/meeting-sdk/web/SKILL.md`

### `zoom-meeting-sdk-web-client-view`

Zoom Meeting SDK Web - Client View. Full-page Zoom meeting experience with the familiar Zoom interface. Uses ZoomMtg global singleton with callback-based API. Ideal for quick integration with minimal customization. Provides the same UI as Zoom Web Client.

- Path: `plugins/zoom/skills/meeting-sdk/web/client-view/SKILL.md`

### `zoom-meeting-sdk-web-component-view`

Zoom Meeting SDK Web - Component View. Embeddable Zoom meeting components with Promise-based API for flexible integration. Ideal for React/Vue/Angular apps and custom layouts. Uses ZoomMtgEmbedded with async/await patterns and embeddable UI containers.

- Path: `plugins/zoom/skills/meeting-sdk/web/component-view/SKILL.md`

### `zoom-meeting-sdk-windows`

Zoom Meeting SDK for Windows - Native C++ SDK for embedding Zoom meetings into Windows desktop applications. Supports custom UI architecture with raw video/audio data, headless bots, and deep integration with meeting features. Includes SDK architecture patterns and Windows message loop handling.

- Path: `plugins/zoom/skills/meeting-sdk/windows/SKILL.md`

### `zoom-oauth`

Use when implementing OAuth.

- Path: `plugins/zoom/skills/oauth/SKILL.md`

### `zoom-rtms`

Use when using RTMS.

- Path: `plugins/zoom/skills/rtms/SKILL.md`

### `zoom-video-sdk-android`

Zoom Video SDK for Android native apps. Use when building custom Android video experiences with full UI control, session tokens, raw media options, and event-driven participant state.

- Path: `plugins/zoom/skills/video-sdk/android/SKILL.md`

### `zoom-video-sdk-flutter`

Zoom Video SDK for Flutter. Use when building custom video session apps in Flutter with flutter_zoom_videosdk, event-driven architecture, session lifecycle handling, and mobile platform integration patterns.

- Path: `plugins/zoom/skills/video-sdk/flutter/SKILL.md`

### `zoom-video-sdk-ios`

Zoom Video SDK for iOS native apps. Use when building custom iOS video sessions with full UI control, token-based session auth, and event-driven media/participant flows.

- Path: `plugins/zoom/skills/video-sdk/ios/SKILL.md`

### `zoom-video-sdk-linux`

Zoom Video SDK for Linux - C++ headless bots, raw audio/video capture/injection, Qt/GTK integration, Docker support

- Path: `plugins/zoom/skills/video-sdk/linux/SKILL.md`

### `zoom-video-sdk-macos`

Zoom Video SDK for macOS native desktop apps. Use when building custom macOS video sessions with native UI control, tokenized join, and desktop-oriented media/device workflows.

- Path: `plugins/zoom/skills/video-sdk/macos/SKILL.md`

### `zoom-video-sdk-react-native`

Zoom Video SDK for React Native. Use when building custom mobile video session experiences with @zoom/react-native-videosdk, event listeners, helper-based APIs, and backend JWT token flows.

- Path: `plugins/zoom/skills/video-sdk/react-native/SKILL.md`

### `zoom-video-sdk-unity`

Zoom Video SDK for Unity wrapper integrations. Use when building custom Unity-based video session experiences and mapping Unity scene/UI state to Video SDK events.

- Path: `plugins/zoom/skills/video-sdk/unity/SKILL.md`

### `zoom-video-sdk-web`

Zoom Video SDK for Web - JavaScript/TypeScript integration for browser-based video sessions, real-time communication, screen sharing, recording, and live transcription

- Path: `plugins/zoom/skills/video-sdk/web/SKILL.md`

### `zoom-video-sdk-windows`

Zoom Video SDK for Windows - C++ integration for video sessions, raw audio/video capture, screen sharing, recording, and real-time communication

- Path: `plugins/zoom/skills/video-sdk/windows/SKILL.md`

### `zoom-virtual-agent-android`

Zoom Virtual Agent Android integration via WebView. Use for Java/Kotlin bridge callbacks, native URL handling, support_handoff relay, and lifecycle-safe embedding.

- Path: `plugins/zoom/skills/virtual-agent/android/SKILL.md`

### `zoom-virtual-agent-ios`

Zoom Virtual Agent iOS integration via WKWebView. Use for Swift/Objective-C script injection, message handlers, support_handoff relay, and URL routing policies.

- Path: `plugins/zoom/skills/virtual-agent/ios/SKILL.md`

### `zoom-virtual-agent-web`

Zoom Virtual Agent SDK for web embeds. Use for campaign or entry ID chat launch, event-driven controls, user context updates, and CSP-safe deployment.

- Path: `plugins/zoom/skills/virtual-agent/web/SKILL.md`

## zotero

1 skill(s)

### `Zotero`

Use Zotero Desktop from Codex to enable/probe the local API, search a local Zotero library, list items/collections/tags, export BibTeX, insert citation keys into LaTeX or Markdown drafts, read indexed full text when requested, and import BibTeX/RIS records into Zotero through the connector server. Use when the user mentions Zotero, citations, references.bib, BibTeX export, local Zotero API, localhost:23119, or adding citations from a Zotero library.

- Path: `plugins/zotero/skills/zotero/SKILL.md`
