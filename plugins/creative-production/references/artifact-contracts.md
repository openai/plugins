# Creative Production Artifact Contracts

Use this reference before creating, repairing, validating, or reporting Creative Production artifacts.

## Universal Contract

1. Mount at most one Creative Production board per workflow.
2. When there is not enough real context to generate safely, render the zero state once. Do not use a structured intake form.
3. When enough context exists and no board is mounted, generate first and render the populated board once.
4. When a board is already mounted, reuse its `boardId`. Start placeholders only when generation starts and complete those same item IDs after files exist. Never open or remount a replacement board.
5. Every generated image set enters the same mounted board through the canonical import path.
6. Keep local HTML pages, local server URLs, manifests, and debug artifacts out of the primary handoff unless the user explicitly asks to inspect them.

## Board Contract

The Creative Production app is the default visible surface for zero state, image review, selection, remixing, and follow-up work.

The board may render with zero items only for intake. In that state it shows starter prompts, not a fake gallery. Create it once with `creative_production_board action=open`; later actions reuse its `boardId`. When items exist, each visible tile represents one selectable creative asset.

Generated items use bounded previews while preserving full-resolution source assets. The mounted board reconciles revision receipts instead of opening a second board.

## Produce Contract

`produce` owns concrete creative work. It chooses conditional mode references from `skills/produce/references/modes/` and cross-cutting contracts from `skills/produce/references/contracts/`.

Mode references are guidance, not invocable skills. They may describe ads, scenes, offers, shots, logos, styles, positioning, or charts, but they do not create separate review surfaces or routing paths.

## Output Matrix

| Request shape | Conditional guidance | Primary result | Exactness rule |
| --- | --- | --- | --- |
| Broad visual direction | default `produce` behavior | 4-6 distinct image directions in the board | One clean asset per tile; no collage inside a tile |
| Ads or campaigns | `modes/ads.md` | Ad-direction image set in the board | Do not invent claims, endorsements, certifications, or legal copy |
| Product/service scenes | `modes/scenes.md` | Realistic context image set in the board | Preserve supplied subject identity when present |
| Offers or hero directions | `modes/offers.md` | Offer-led image families in the board | Do not invent pricing, product facts, or proof |
| Camera variants | `modes/shots.md` | Angle/crop/detail variants in the board | Source preservation is mandatory |
| Logos or identity | `modes/logos.md` | Distinct identity directions in the board | Do not present placeholder SVGs as finished work |
| Reusable style systems | `modes/styles.md` | Style directions in the board | Vary treatment, not product facts |
| Positioning | `modes/positioning.md` | Image-led positioning directions | Do not default to a text-heavy strategy document |
| Charts | `modes/charts.md` | Chart treatment variants in the board | Preserve all data, labels, values, ordering, and meaning |
| Final exports | `contracts/deterministic-exports.md` | Export previews, files, manifest, and provenance | Exact text, logos, data, dimensions, and safe zones stay deterministic |

## Validation Checklist

- The primary visible surface is the mounted Creative Production board.
- The workflow rendered no more than one board.
- Zero state uses starter prompts and no structured intake.
- Generated sets show the expected number of non-error assets.
- Follow-up work imports into the same board.
- Exact content and source-preservation constraints are applied when relevant.
