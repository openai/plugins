---
name: reports-pdfs-and-slide-automation
description: Lay out and export data-rich reports and documents. Use when the user needs report structure, figure packaging, PDFs, PowerPoint or Google Slides automation, or programmatic insertion of visualizations, UML-like diagrams, or architecture diagrams into documents.
---

# Reports, PDFs, and Slide Automation

## Overview

Use this skill when the output is a deliverable rather than a standalone chart. That includes reports, briefing decks, PDFs, slide exports, document embeds, and reusable figure assets that other systems can place into files.

Default assumption: build figures as durable assets first, then compose them into documents. Do not rely on screenshots unless the workflow truly has no better option.

For editorial reports and infographic packages, use `../../references/foundations/editorial-infographic-system.md` before layout. For visual stories that include animation, generated imagery, illustrated substrates, WebGL, particles, 3D, or scrollytelling, also use `../../references/foundations/art-directed-interactive-visual-stories.md`. When page, slide, or figure composition materially affects interpretation, use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md` for concept generation, user approval, mobile variants, and semantic design contracts. The deliverable should read as a sequence of claims supported by figures, not as a dashboard export.

For reports, decks, PDFs, and documents with multiple meaningful figures, use `../../references/foundations/embedded-visualization-self-use.md` before page or slide composition. Each chart, map, table-graphic, inset, flow layer, static fallback, and export-only frame needs a specialist owner and mini-brief before it becomes a placed asset.

## Common Targets

- HTML reports
- PDF reports generated from HTML or direct PDF libraries
- PowerPoint decks
- Google Slides decks
- Word or Docs-style narrative documents
- Markdown and static-site reports
- Technical documentation with UML, ERD, C4, BPMN, flow, state machine, dependency, schema, or architecture diagram assets

## Figure Packaging Rules

1. Inventory every meaningful embedded figure or visual layer before layout, assign a primary specialist owner, and write a mini-brief covering job, data shape, encoding, interaction or static fallback, accessibility, QA, and fresh-pass status.
2. Use an authorized delegated specialist or explicit local specialist pass for substantial figures before composition. The report or deck owner integrates the results, keeps shared encodings consistent, and performs final editorial QA.
3. For advanced report, deck, or page compositions, create a visual design contract before implementation, but only after the user approves the generated layout concept set or requests a revised concept. Do not make project changes, finalize assets, or generate implementation code while approval is pending. If the user requests changes, revise or regenerate the concept set and repeat the concise bullet review until the user agrees on the design. The contract should map the approved concepts to figure slots, locked layout elements, flexible production details, data-bound layers, source/caveat placement, export frames, mobile/landscape or print adaptations, and approved deviations.
4. Export each figure in the format the medium needs:
   - SVG for vector and print
   - PNG for slides and office documents
   - PDF when downstream systems preserve vector PDF pages well
5. Keep chart dimensions intentional for page or slide slots.
6. Preserve consistent theming, typography, and color semantics across all assets.
7. Keep annotations readable at final output size.
8. Include source, caveat, and alternative text metadata with each exported figure.
9. For animated or interactive stories, export first frame, key frames, and final frame so the argument survives in PDF, slides, and reduced-motion contexts.
10. For WebGL or particle scenes, export a static fallback that preserves the data claim: final frame, key frames, arrows, path widths, selected focus state, or a panel sequence.
11. For generated imagery, keep image assets, data overlays, captions, and source notes as separate layers whenever the target medium permits.
12. For UML-like, ERD, C4, BPMN, flow, dependency, or architecture diagrams, use `../uml-and-software-architecture-visualization/SKILL.md` first and export both the diagram source and the rendered asset when the target workflow permits.

## Programmatic PDF Approaches

- Browser or HTML-first:
   - render semantic HTML and CSS
   - print with Playwright or Puppeteer
- JavaScript-first:
   - pdf-lib for PDF manipulation
   - PDFKit or jsPDF for direct generation

For Codex-driven workflows, the most reliable pattern is often: generate charts as SVG or PNG, compose an HTML report, then render to PDF with a browser engine.

## Slide Deck Approaches

- PowerPoint:
   - `pptxgenjs` in JavaScript or TypeScript
- Google Slides:
   - generate assets first
   - place them via the Google Slides API with explicit page geometry

## Document Embedding Patterns

- Word or DOCX: insert exported PNG or SVG where supported and keep captions separate from the image raster.
- Markdown or static docs: prefer SVG for crisp web rendering.
- PDFs: either compose from exported assets or print from HTML layouts.
- Spreadsheets and office docs: use fixed-aspect PNG exports when office rendering of SVG is inconsistent.

## Report Layout Principles

- Start with the question, not the chart inventory.
- Lead with the strongest claim and the view that supports it.
- Use supporting small multiples instead of giant dashboard mosaics.
- Integrate explanatory text near the figure it explains.
- Use insight titles, direct labels, and annotations in the figure asset itself so it survives being moved into slides, PDFs, or article embeds.
- When an interactive story has to become static, package it as a paced panel sequence instead of a single unexplained screenshot.
- Reserve appendix sections for dense tables and methodological detail.

## Output Expectations

- Name the target medium.
- Provide the embedded visualization inventory with specialist owners, mini-brief summaries, QA checks, and delegated or local fresh-pass status.
- For concepted report, deck, or page layouts, use the shared design workflow for required concept images, approval status, approved references, binding visual design contract, locked and flexible elements, data-bound layers, mobile/landscape or print continuation, approved deviations, and semantic fidelity QA.
- Define the export asset set.
- Make page or slide layout explicit.
- For art-directed visual stories, identify which key frames, generated assets, and data overlays should be exported.
- Preserve a clean path for regeneration when the data changes.

## References

- Shared theory:
  - `../../references/foundations/editorial-infographic-system.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/meaning-preserving-visual-design-workflow.md`
  - `../../references/foundations/embedded-visualization-self-use.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/storytelling-annotation-and-critique.md`
- Skill references:
  - `./references/report-structure-and-figure-packaging.md`
  - `./references/pdf-generation-paths.md`
  - `./references/powerpoint-and-google-slides.md`
  - `./references/document-embedding-and-regeneration.md`
  - `../uml-and-software-architecture-visualization/SKILL.md`

## Representative Prompts

- "Turn this dashboard into an executive PDF report."
- "Generate a PowerPoint deck with chart assets and commentary."
- "Programmatically add these visualizations to a report."
- "Create an HTML report and render it to PDF with Playwright."
- "Automate Google Slides or PowerPoint creation from chart assets."
- "Package UML, ERD, C4, BPMN, flow, state machine, dependency, or architecture diagrams into a report, PDF, or deck."
