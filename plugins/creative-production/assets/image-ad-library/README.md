# Image Ad Library

Reusable Creative Production image-ad packs live here.

Image-ad packs define high-level advertising formats and visual grammars for placing a supplied product, service, venue, offer, or business asset into campaign-ready image directions. They are broader than product-context archetypes: some are UGC thumbnails, some are surreal 3D renders, some are OOH posters, some are ecommerce modules, and some are proof-led or demo-led ad systems.

Use this library when the user wants a diverse ad exploration before selecting scenes, styles, layouts, or final production polish. For app, SaaS, AI, marketplace, commerce, dev-tool, or other software-product ads, use the digital product pack so the UI remains the central product proof.

Current packs:

- `packs/diverse-image-ad-archetypes.json`: 25 reusable ad families spanning UGC, surreal 3D, premium still life, demo, comparison, OOH, retail, ecommerce, proof, launch, editorial, meme-native, and immersive ad formats.
- `packs/digital-product-core-ad-prompts.json`: 12 screen-first routes for apps, SaaS, AI products, developer products, and other digital products where the UI itself is the product proof.

Example from the workspace root:

```bash
python3 plugins/creative-production/skills/produce/helpers/offers/scripts/build_offer_explorer.py \
  --offer-name "<subject name>" \
  --subject-kind product \
  --offer-brief "<facts to preserve, supplied copy, audience, palette, and avoid list>" \
  --expansion-map plugins/creative-production/assets/image-ad-library/packs/diverse-image-ad-archetypes.json \
  --pack diverse-image-ad-archetypes \
  --scale family \
  --out-dir outputs/imagegen/<subject-slug>-diverse-image-ads
```

Digital product example from the workspace root:

```bash
python3 plugins/creative-production/skills/produce/helpers/ads/scripts/build_ads_explorer.py \
  --ad-name "<app or digital product name>" \
  --subject-kind product \
  --pack digital-product-core-ad-prompts \
  --ad-brief "<product category, core UI surface, mechanic, device policy, allowed readable text, exact exterior copy or NONE, audience, palette, privacy/legal avoid list, and UI reference policy>" \
  --out-dir outputs/imagegen/<subject-slug>-digital-product-ads
```

Text handling:

- Use exact supplied copy only.
- Keep generated readable text short.
- For long copy, create clear placement zones or placeholder blocks for deterministic layout later.
- Treat logos, labels, packaging text, claims, contact details, and prices as high-risk fidelity areas.
