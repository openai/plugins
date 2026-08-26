(() => {
  const starterDetails = {
    "make-logo-from-scratch": {
      intakeTitle: "First things first, what are we branding?",
      intakeSubtitle: "What's the product? Do you have an existing logo? Any additional art direction you want?",
      instruction: "Explore focused logo directions from the supplied identity and existing assets.",
    },
    "social-ads": {
      intakeSubtitle: "Share a brief or some quick notes on what you're looking for.",
      instruction: "Create distinct social ad directions from the supplied product and art direction.",
    },
    "place-product": {
      intakeSubtitle: "Share a reference for the product and any art direction you have.",
      instruction: "Place the supplied product faithfully into the requested environment.",
    },
    "product-detail-images": {
      intakeSubtitle: "Share a reference for the product and any art direction you have.",
      instruction: "Create polished product shots from the supplied product, angles, and setting.",
    },
    "campaign-ideas": {
      intakeSubtitle: "Share a brief or some quick notes on what you're looking for.",
      instruction: "Develop distinct campaign territories from the supplied subject and goal.",
    },
    "template-assets": {
      intakeSubtitle: "Share the campaign, product, or source asset you want adapted.",
      instruction: "Create channel-ready assets from the supplied campaign, product, or source asset while preserving the core idea, hierarchy, and brand feel.",
    },
    "social-post-series": {
      intakeSubtitle: "Share a brief or some quick notes on what you're looking for.",
      instruction: "Create a cohesive social carousel from the supplied examples and content brief.",
    },
    "place-in-screen": {
      intakeSubtitle: "Share the reference to place and any additional direction.",
      instruction: "Place the supplied reference into a convincing screen context.",
    },
    "images-in-a-style": {
      intakeSubtitle: "Share a template or describe what should stay consistent.",
      instruction: "Create multiple variations that adhere closely to the supplied template while changing the requested content, language, format, or subject.",
    },
  };

  const starterSuggestionExamples = {
    "make-logo-from-scratch": [
      ["Make 10 logos based on the letter R", "Make 10 distinct logo marks based on the letter R. Explore a wide range of styles: geometric, organic, luxury, playful, tech-forward, editorial, heritage, and minimalist."],
      ["Make a wordmark for Kairos, a modern wellness spa", "Create a refined wordmark for Kairos, a modern wellness spa. Make it calm, elevated, spacious, and usable as a real brand mark."],
      ["Create an identity for a sparkling tea brand", "Create an identity for a contemporary sparkling tea brand. Explore logo, color, type, and package-facing directions that feel fresh, crisp, and premium."],
    ],
    "social-ads": [
      ["Square coming-soon teaser for a mini synth", "Make a square coming-soon teaser for a pocket-sized mini synth. Give it 80s nostalgia, crisp product realism, a little weird personality, and the elegance of a modern consumer electronics ad."],
      ["Social ad for software that cleans up launch notes", "Make a bold social ad for Stackgarden, fictional software that turns messy project notes into neat launch plans. Use a clever visual metaphor, crisp UI elements, and slightly quirky startup energy."],
      ["Playful social ad for tiny oat milk cartons", "Make a playful social ad for pocket-sized oat milk cartons called Moo-ish. Use bright studio lighting, exaggerated scale, charming product realism, and deadpan copy energy."],
    ],
    "place-product": [
      ["Place my logo on a t-shirt", "Place this anvil logo on a clean heavyweight cotton t-shirt. Make it feel like a real merch mockup with natural fabric texture, believable folds, and soft studio light.", "starter-assets/suggestion-anvil-logo.svg"],
      ["Place a product on a candy-colored waterslide", "Place this product into a bright, unlikely, candy-colored waterslide scene. Keep the product recognizable and make the whole image feel fun, sunny, and commercially polished.", "starter-assets/suggestion-waterslide-product-phone-photo.svg"],
      ["Place a product in a surreal boutique display", "Place this sculptural perfume bottle in a premium boutique retail display with sculptural shelves, warm color, and a slightly surreal window arrangement.", "starter-assets/suggestion-boutique-product-staged-photo.svg"],
    ],
    "product-detail-images": [
      ["Show this suit in navy, heather, and tan", "Show this suit in navy, heather, and tan. Turn the reference into clean ecommerce-ready product shots with believable fabric, consistent tailoring, and matching lighting across all colorways.", "starter-assets/suggestion-suit-phone-photo.svg"],
      ["Make polished product images for this cowboy hat", "Make polished product shots for this cowboy hat. Show a clean hero angle, side profile, brim detail, and material close-up while keeping the hat shape accurate.", "starter-assets/suggestion-cowboy-hat-phone-photo.svg"],
      ["Make detail images for buttons and ports", "Make product shots that hero buttons, ports, seams, and small controls with crisp macro lighting. Keep the device believable, but make the output much more polished than the reference.", "starter-assets/suggestion-device-staged-photo.svg"],
    ],
    "campaign-ideas": [
      ["Brainstorm a ‘5 tiny reasons’ social campaign", "Brainstorm a simple social campaign built around ‘5 tiny reasons to try it.’ Make the ideas visual, easy to post, and specific enough to turn into images."],
      ["Campaign ideas for sparkling tea shelf moments", "Brainstorm campaign ideas for this sparkling tea retail card. Focus on quick in-store moments, bright shelf visuals, and simple reasons someone would pick it up."],
      ["Brainstorm a simple before/after week campaign", "Brainstorm a campaign based on one small before-and-after change people can feel in a week. Keep it concrete, human, and easy to visualize."],
    ],
    "template-assets": [
      ["Turn a pocket projector launch into channel-ready assets", "Create assets for every channel for the ‘Big Movie. Tiny Box.’ pocket-projector campaign. Preserve the bold red, yellow, and cream palette, oversized typography, and compact projector hero while adapting it for feed, story, short-video cover, web banner, and link-preview placements.", "starter-assets/suggestion-all-social-source-asset.svg"],
      ["Launch the Orbit lamp across every channel", "Create assets for every channel for the Orbit portable lamp campaign. Preserve the ‘Meet Orbit’ and ‘Light, Anywhere’ campaign idea, polished chrome product rendering, and purple visual system while adapting it for feed, story, short-video cover, web banner, and launch communications.", "starter-assets/suggestion-square-launch-graphic.svg"],
      ["Adapt the Wild Day campaign for every channel", "Create assets for every channel for the Wild Day seasonal beverage campaign. Preserve the ‘Sip the Season’ idea, bright citrus imagery, mint-green background, bold typography, and centered can while adapting it for feed, story, short-video cover, email hero, and display placements.", "starter-assets/suggestion-seasonal-social-ad.svg"],
    ],
    "social-post-series": [
      ["Make a 5-slide product story", "Make a realistic 5-slide product carousel from this visual direction. Include a clear hook, feature slide, detail slide, proof or benefit slide, and a final call-to-action slide."],
      ["Create a five-post launch countdown series", "Create a realistic five-post launch countdown series with a visual system, changing daily message, product tease, reveal moment, and launch-day post."],
      ["Make a carousel that tells a founder story", "Make a founder story carousel with realistic pacing: origin, problem, messy middle, product breakthrough, and why it matters now."],
    ],
    "place-in-screen": [
      ["Mock this screen up in a phone", "Place this fictional app screen into a polished phone mockup. The attached reference is the screen only; create the phone context, realistic glass, shadows, and presentation crop.", "starter-assets/suggestion-place-in-screen-phone.svg"],
      ["Mock this up on a laptop with a gradient background", "Mock this up on a laptop with a colorful gradient texture in the background. Make it feel like a polished product-marketing hero image with tasteful reflections and depth.", "starter-assets/suggestion-place-in-screen-laptop.svg"],
      ["Place this asset inside a modern landing-page hero", "Place this fictional product UI inside a modern landing-page hero with browser chrome, realistic spacing, and a clean product-story composition.", "starter-assets/suggestion-place-in-screen-hero.svg"],
    ],
    "images-in-a-style": [
      ["Make the same square ad in multiple languages", "Use this square social ad as a template. Create multiple language variations while preserving the layout, hierarchy, product placement, CTA style, typography feel, and overall brand system.", "starter-assets/suggestion-multilingual-social-ad.svg"],
      ["Create seasonal versions from this same template", "Use the attached social ad as the template and create seasonal versions for spring, summer, fall, and winter. Keep the composition and brand system consistent while changing color, imagery, and headline details.", "starter-assets/suggestion-seasonal-social-ad.svg"],
      ["Swap the product but keep the template system", "Create multiple variations that replace the featured product in this social ad while keeping the same template, spacing, text hierarchy, CTA placement, and overall visual rules.", "starter-assets/suggestion-product-swap-social-ad.svg"],
    ],
  };

  const guidanceByUseCase = {
    "make-logo-from-scratch": "You are a senior graphic designer and branding expert. Your job is to develop sharp, usable identity directions that feel strategically distinct, visually polished, and appropriate for the brand or product.",
    "social-ads": "You are a creative expert in social media marketing. Your job is to develop high-performing paid social ad concepts that are visually arresting, easy to understand quickly, and grounded in the product promise.",
    "campaign-ideas": "You are a creative strategist and campaign conceptor. Your job is to develop memorable campaign territories with clear visual hooks, strong audience appeal, and enough specificity to become real assets.",
    "social-post-series": "You are a social content strategist and art director. Your job is to develop a cohesive carousel or post series with a clear visual rhythm, platform-native pacing, and an immediately legible idea.",
    "product-detail-images": "You are a product art director. Your job is to develop polished product shots that reveal form, material, use, and desirability with crisp visual intent.",
    "place-product": "You are a commercial product photographer and art director. Your job is to place the product into a believable, beautiful scene while preserving the product's recognizable details.",
    "template-assets": "You are a production designer for multi-channel creative. Your job is to adapt the supplied idea or asset into channel-ready creative while preserving the core idea, hierarchy, and brand feel.",
    "place-in-screen": "You are a screen-design and product storytelling expert. Your job is to place the supplied reference into a convincing screen context that makes the product or idea feel real and desirable.",
    "images-in-a-style": "You are a production designer and visual systems art director. Your job is to create multiple polished variations that adhere closely to a supplied template while changing the requested content, language, product, or context.",
  };

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function detailsFor(starter = {}) {
    return { ...(starterDetails[starter.id] || {}), ...starter };
  }

  function title(starter) {
    return starter.intakeTitle || starter.title;
  }

  function subtitle(starter) {
    return starter.intakeSubtitle || "Share a brief or some quick notes on what you're looking for.";
  }

  function suggestionMarkup(starter) {
    const override = window.CREATIVE_PRODUCTION_STARTER_SUGGESTIONS?.[starter.id];
    const suggestions = Array.isArray(override) && override.length
      ? override.map((item) => [item.label, item.text || item.prompt, item.asset])
      : starterSuggestionExamples[starter.id] || [];
    if (!suggestions.length) return "";
    return `
      <div class="starter-intake-suggestions" aria-label="Example use cases">
        ${suggestions.slice(0, 3).map(([label, text, asset]) => `
          <button class="starter-intake-suggestion" type="button" data-suggestion-text="${escapeHtml(text || "")}" data-suggestion-asset="${escapeHtml(asset || "")}">
            ${escapeHtml(label || "Example")}
          </button>
        `).join("")}
      </div>
    `;
  }

  function prompt(starter, notes, files, options = {}) {
    const starterAsset = options.starterAsset || null;
    const attachmentLabels = [starterAsset?.label, ...files.map((file) => file.name)].filter(Boolean);
    const sourceReferenceLines = [];
    if (starterAsset?.path) {
      sourceReferenceLines.push(`- Starter image: ${starterAsset.path} (plugin-relative path; this image is not attached to the follow-up)`);
    }
    files.forEach((file) => {
      sourceReferenceLines.push(`- User file selected in the modal: ${file.name}${file.type ? ` (${file.type})` : ""}${file.size ? `, ${file.size} bytes` : ""}`);
    });
    if (files.length > 0) {
      sourceReferenceLines.push("- Browser file selection does not expose device absolute paths. If the notes include absolute file paths or directories from the user, use those exact paths as the source references.");
    }
    const lines = [
      guidanceByUseCase[starter.id] || "You are an expert creative director. Turn the supplied brief and references into polished, useful creative work.",
      "",
      `Start "${starter.title}" in Creative Production.`,
      starter.instruction,
      "Use the intake notes and source references below. Begin creating immediately; do not ask follow-up questions unless an essential input is genuinely missing.",
      "",
      "Routing:",
      `- use_case: ${starter.id}`,
      "- brief_complete: true",
      "",
    ];
    lines.push(
      "Brief:",
      `- Notes: ${notes || "Not provided"}`,
      `- Source references: ${attachmentLabels.join(", ") || "None"}`,
      ...sourceReferenceLines,
      "",
      "Output expectations:",
      "- Start by creating the requested visual work; do not spend the response asking discovery questions unless a required input is truly missing.",
      "- Make the result feel specific to the brief and supplied references, not generic.",
      "- Prefer a small set of strong, differentiated directions over many slight variations.",
    );
    return lines.join("\n");
  }

  function payload(starter, notes, files, options = {}) {
    return {
      starterId: starter.id,
      brief: {
        notes,
        starterAsset: options.starterAsset || null,
        files: files.map((file) => ({ name: file.name, size: file.size, type: file.type })),
      },
    };
  }

  window.CreativeProductionStarterIntakeRuntime = Object.freeze({
    detailsFor,
    title,
    subtitle,
    suggestionMarkup,
    prompt,
    payload,
  });
})();
