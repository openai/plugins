---
name: higgsfield-marketing-studio
description: Create Higgsfield Marketing Studio ads. Use when the user asks for UGC, product demos, unboxing/review videos, presenters, branded ad images, avatars, hooks/settings, or brand kits.
---

# Higgsfield Marketing Studio

Use this skill for campaign-shaped creative work. Marketing Studio is different from generic generation because it can select or create products, avatars, hooks, settings, ad formats, and brand kits before calling `generate_image` or `generate_video`.

## Workflow

1. Identify the ad shape: video or image, product involved or not, avatar/presenter needed or not, brand-kit constraints, and aspect ratio/platform.
2. Discover existing assets before creating new ones:
   - `marketing_list_video_presets`
   - `marketing_list_avatars`
   - `marketing_list_products`
   - `marketing_list_webproducts`
   - `marketing_list_hooks`
   - `marketing_list_settings`
   - `marketing_list_ad_formats`
   - `marketing_list_brand_kits`
3. If the user supplies product images, upload them with `media_upload_and_confirm` using `type: "image"`, then call `marketing_create_product_from_media` with the returned media IDs.
4. If the user supplies brand data, call `marketing_create_brand_kit` only from user-provided values. Use `marketing_get_brand_kit` for inspection.
5. Generate:
   - Use `generate_video` with `model: "marketing_studio_video"` for UGC, product demo, unboxing, product review, presenter, and social ad videos.
   - Use `generate_image` with a Marketing Studio image model for branded ad images, DTC creatives, and product/social campaign stills.
   - Pass `product_ids`, `avatars`, `hook_id`, `setting_id`, `brand_kit_id`, mode, duration, aspect ratio, and resolution only when supported by `models_get`.
6. Poll with `job_status`. Use `show_marketing_studio_generations` when the user asks to browse prior Marketing Studio output.

## Asset Rules

- If the user gives a product URL, ask for product images or manual product details.
- `marketing_create_product_from_media` needs confirmed uploaded image media IDs.
- Create or update brand kits from supplied brand data.
- Use `marketing_update_brand_kit` and `marketing_delete_brand_kit` only after explicit user intent.

## Creative Defaults

- For UGC-style ads, start by listing video presets, avatars, products, hooks, and settings; choose a coherent combination instead of asking for everything up front.
- Use hooks/settings only after listing or when the user provides exact IDs.
- Prefer one question per phase: product, then avatar, then style/mode. If defaults are obvious, proceed.
- For ad images, list ad formats and brand kits when brand consistency matters.
- Keep user-facing language simple: product, avatar, hook, setting, brand kit, ad format. Do not expose internal job-set wording.

## Notes

- Create products, brand kits, and brand-kit edits only when the user asks for that operation.
- Keep each ad focused on one product, one campaign angle, and one primary output unless the user asks for a set.
- If an error includes `request_id`, include it in the user-facing failure summary.
