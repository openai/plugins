import { isRecord, uniqueSorted, verifySnapshotHash } from "./common.mjs";
import { aspectRatio, mediaGeometry, panelGeometry } from "./media-geometry.mjs";

const EMU_PER_POINT = 12700;
const TEXT_PLACEHOLDER_TYPES = new Set([
  "BODY", "CENTERED_TITLE", "DATE_AND_TIME", "FOOTER", "HEADER", "SLIDE_NUMBER", "SUBTITLE", "TITLE",
]);
const MEDIA_PLACEHOLDER_TYPES = new Set(["CHART", "CLIP_ART", "DIAGRAM", "MEDIA", "OBJECT", "PICTURE", "SLIDE_IMAGE", "TABLE"]);
const PROTECTED_PLACEHOLDER_TYPES = new Set(["DATE_AND_TIME", "FOOTER", "HEADER", "SLIDE_NUMBER"]);
const CONTENT_KINDS = new Set(["image", "table", "sheetsChart", "video", "wordArt", "speakerSpotlight"]);
const CHROME_PATTERN = /\b(?:brand|chrome|footer|header|logo|navigation|page number|slide number)\b/i;

function clone(value) {
  if (value === undefined) return undefined;
  return structuredClone(value);
}

function dimensionToPoints(dimension) {
  if (dimension === null || dimension === undefined) return null;
  if (typeof dimension === "number") return Number.isFinite(dimension) ? dimension : null;
  if (!isRecord(dimension)) return null;
  const magnitude = Number(dimension.magnitude);
  if (!Number.isFinite(magnitude)) return null;
  const unit = String(dimension.unit ?? "PT").toUpperCase();
  if (["PT", "POINT", "POINTS"].includes(unit)) return magnitude;
  if (unit === "EMU") return magnitude / EMU_PER_POINT;
  if (["IN", "INCH", "INCHES"].includes(unit)) return magnitude * 72;
  if (unit === "PX") return magnitude * 0.75;
  return null;
}

function mergeInherited(parent, child) {
  if (child === null || child === undefined) return clone(parent) ?? null;
  if (!isRecord(child)) return clone(child);
  if (child.propertyState === "INHERIT") return clone(parent) ?? clone(child);
  if (child.propertyState === "NOT_RENDERED") return clone(child);
  const output = isRecord(parent) ? clone(parent) : {};
  for (const [key, value] of Object.entries(child)) {
    if (value === undefined) continue;
    output[key] = isRecord(value) ? mergeInherited(output[key], value) : clone(value);
  }
  return output;
}

export function flattenPageElements(elements) {
  return (elements ?? []).flatMap((element) => [element, ...flattenPageElements(element.group?.children)]);
}

function elementText(element) {
  const values = [];
  if (element?.text?.plainText) values.push(element.text.plainText);
  if (element?.wordArt?.renderedText) values.push(element.wordArt.renderedText);
  for (const row of element?.table?.cells ?? []) {
    for (const cell of row ?? []) if (cell.text?.plainText) values.push(cell.text.plainText);
  }
  return values.join("\n").trim();
}

function elementKinds(elements) {
  const counts = {};
  for (const element of flattenPageElements(elements)) counts[element.kind] = (counts[element.kind] ?? 0) + 1;
  return counts;
}

function boundsAreaRatio(bounds, pageSize) {
  if (!bounds || !Number.isFinite(pageSize?.width) || !Number.isFinite(pageSize?.height)) return null;
  const pageArea = pageSize.width * pageSize.height;
  if (!(pageArea > 0)) return null;
  return Math.max(0, bounds.width) * Math.max(0, bounds.height) / pageArea;
}

function edgeRegion(bounds, pageSize) {
  if (!bounds || !Number.isFinite(pageSize?.width) || !Number.isFinite(pageSize?.height)) return false;
  const edgeX = pageSize.width * 0.08;
  const edgeY = pageSize.height * 0.08;
  return bounds.x <= edgeX || bounds.y <= edgeY ||
    bounds.x + bounds.width >= pageSize.width - edgeX ||
    bounds.y + bounds.height >= pageSize.height - edgeY;
}

function themeColors(pageProperties) {
  return Object.fromEntries((pageProperties?.colorScheme?.colors ?? [])
    .filter((entry) => entry?.type && entry?.color)
    .map((entry) => [entry.type, entry.color]));
}

function stylesByNesting(element) {
  return element?.text?.styleDefaultsByNesting ?? {};
}

function mergeStyleMaps(parent, child) {
  const output = {};
  for (const key of uniqueSorted([...Object.keys(parent ?? {}), ...Object.keys(child ?? {})])) {
    output[key] = mergeInherited(parent?.[key], child?.[key]);
  }
  return output;
}

function renderedFontSizes(styles, shapeProperties) {
  const fontScale = Number(shapeProperties?.autofit?.fontScale ?? 1);
  const scale = Number.isFinite(fontScale) && fontScale > 0 ? fontScale : 1;
  return Object.fromEntries(Object.entries(styles ?? {}).flatMap(([level, style]) => {
    const size = dimensionToPoints(style?.fontSize);
    return Number.isFinite(size) ? [[level, size * scale]] : [];
  }));
}

function semanticHints(slot, layoutLabel) {
  const type = slot.type;
  const hints = [];
  const add = (role, confidence, reason) => hints.push({ role, confidence, reason });
  const standard = {
    BODY: "body", CENTERED_TITLE: "title", DATE_AND_TIME: "date", FOOTER: "footer",
    HEADER: "header", SLIDE_NUMBER: "slide-number", SUBTITLE: "subtitle", TITLE: "title",
    CHART: "chart", CLIP_ART: "image", DIAGRAM: "diagram", MEDIA: "media", OBJECT: "evidence",
    PICTURE: "image", SLIDE_IMAGE: "slide-image", TABLE: "table",
  }[type];
  if (standard) add(standard, "high", `Google placeholder type ${type}`);
  if (/speaker/i.test(layoutLabel)) {
    if (["TITLE", "CENTERED_TITLE"].includes(type)) add("talk-title", "medium", "speaker layout title region");
    if (type === "PICTURE") add("speaker-portrait", "medium", "speaker layout picture region");
    if (["SUBTITLE", "BODY"].includes(type)) add("speaker-name", "low", "speaker layout secondary text region; confirm from exemplar labels");
  }
  if (/quote|testimonial/i.test(layoutLabel)) {
    if (["TITLE", "BODY"].includes(type)) add("quote", "low", "quote-oriented layout text region; confirm from exemplar labels");
    if (type === "SUBTITLE") add("attribution", "medium", "quote-oriented layout subtitle region");
  }
  return hints;
}

function protectedRegionsForPage(page, origin, pageSize) {
  return flattenPageElements(page?.elements).flatMap((element) => {
    if (!element.boundsPt) return [];
    const placeholderProtected = PROTECTED_PLACEHOLDER_TYPES.has(element.placeholderType);
    const label = `${element.title ?? ""} ${element.description ?? ""} ${elementText(element)}`;
    const namedChrome = CHROME_PATTERN.test(label);
    const areaRatio = boundsAreaRatio(element.boundsPt, pageSize);
    const edgeChrome = !element.placeholder && areaRatio !== null && areaRatio <= 0.12 && edgeRegion(element.boundsPt, pageSize);
    if (!placeholderProtected && !namedChrome && !edgeChrome) return [];
    return [{
      objectId: element.objectId,
      origin,
      kind: element.kind,
      placeholderType: element.placeholderType ?? null,
      boundsPt: element.boundsPt,
      reason: placeholderProtected ? "reserved-placeholder" : namedChrome ? "named-brand-chrome" : "edge-chrome",
    }];
  });
}

function localComposition(slide, pageSize) {
  const objects = flattenPageElements(slide.elements).map((element) => {
    const text = elementText(element);
    const areaRatio = boundsAreaRatio(element.boundsPt, pageSize);
    const placeholder = Boolean(element.placeholder);
    const contentBearing = Boolean(text || CONTENT_KINDS.has(element.kind));
    return {
      objectId: element.objectId,
      kind: element.kind,
      placeholder: placeholder ? {
        type: element.placeholder.type,
        index: element.placeholder.index,
        parentObjectId: element.placeholder.parentObjectId,
      } : null,
      classification: placeholder ? "placeholder-slot" : contentBearing ? "slide-local-content" : "slide-local-decoration",
      contentBearing,
      boundsPt: element.boundsPt ?? null,
      areaRatio,
      aspectRatio: aspectRatio(element.boundsPt?.width, element.boundsPt?.height),
      panel: panelGeometry(element.boundsPt, pageSize),
      mediaGeometry: ["image", "video", "sheetsChart", "table"].includes(element.kind)
        ? mediaGeometry(element, pageSize)
        : null,
      textPreview: text ? text.replace(/\s+/g, " ").slice(0, 120) : null,
      mediaIdentity: element.image?.sourceUrl ?? element.video?.id ?? element.sheetsChart?.chartId ?? null,
    };
  });
  return {
    objects,
    contentBearingObjectIds: objects.filter((entry) => entry.contentBearing).map((entry) => entry.objectId),
    slideLocalContentObjectIds: objects.filter((entry) => entry.classification === "slide-local-content").map((entry) => entry.objectId),
    slideLocalDecorationObjectIds: objects.filter((entry) => entry.classification === "slide-local-decoration").map((entry) => entry.objectId),
  };
}

function titlePreview(slide) {
  const elements = flattenPageElements(slide.elements);
  const title = elements.find((element) => ["TITLE", "CENTERED_TITLE"].includes(element.placeholderType) && elementText(element));
  const fallback = elements.find((element) => elementText(element));
  return elementText(title ?? fallback ?? {}).replace(/\s+/g, " ").slice(0, 140) || null;
}

export function buildDesignSystem(snapshot) {
  const pageSize = snapshot.presentation?.pageSizePt ?? {};
  const masters = new Map((snapshot.masters ?? []).map((page) => [page.objectId, page]));
  const layouts = new Map((snapshot.layouts ?? []).map((page) => [page.objectId, page]));
  const pages = [...(snapshot.masters ?? []), ...(snapshot.layouts ?? []), ...(snapshot.slides ?? [])];
  const elements = new Map();
  for (const page of pages) {
    for (const element of flattenPageElements(page.elements)) {
      if (element.objectId) elements.set(element.objectId, { page, element });
    }
  }

  const effectivePageProperties = new Map();
  for (const master of snapshot.masters ?? []) effectivePageProperties.set(master.objectId, mergeInherited(null, master.pageProperties));
  for (const layout of snapshot.layouts ?? []) {
    effectivePageProperties.set(layout.objectId, mergeInherited(effectivePageProperties.get(layout.masterId), layout.pageProperties));
  }
  for (const slide of snapshot.slides ?? []) {
    const layout = layouts.get(slide.layoutId);
    const masterId = slide.masterId ?? layout?.masterId ?? null;
    const parent = layout ? effectivePageProperties.get(layout.objectId) : effectivePageProperties.get(masterId);
    effectivePageProperties.set(slide.objectId, mergeInherited(parent, slide.pageProperties));
  }

  const placeholderCache = new Map();
  const resolvePlaceholder = (objectId, stack = new Set()) => {
    if (placeholderCache.has(objectId)) return placeholderCache.get(objectId);
    const located = elements.get(objectId);
    if (!located?.element?.placeholder) return null;
    const element = located.element;
    const parentObjectId = element.placeholder.parentObjectId ?? null;
    if (stack.has(objectId)) {
      const cycle = { objectId, pageId: located.page.objectId, lineage: [objectId], cycle: true };
      placeholderCache.set(objectId, cycle);
      return cycle;
    }
    const nextStack = new Set(stack).add(objectId);
    const parent = parentObjectId ? resolvePlaceholder(parentObjectId, nextStack) : null;
    const effectiveShapeProperties = mergeInherited(parent?.effectiveShapeProperties, element.shapeProperties);
    const effectiveTextStylesByNesting = mergeStyleMaps(parent?.effectiveTextStylesByNesting, stylesByNesting(element));
    const record = {
      objectId,
      pageId: located.page.objectId,
      pageKind: located.page.kind,
      type: element.placeholder.type,
      index: element.placeholder.index,
      parentObjectId,
      missingParentObjectId: parentObjectId && !parent ? parentObjectId : null,
      lineage: [...(parent?.lineage ?? []), objectId],
      cycle: Boolean(parent?.cycle),
      boundsPt: element.boundsPt ?? null,
      effectiveShapeProperties,
      effectiveTextStylesByNesting,
      renderedFontSizePtByNesting: renderedFontSizes(effectiveTextStylesByNesting, effectiveShapeProperties),
    };
    placeholderCache.set(objectId, record);
    return record;
  };
  for (const objectId of elements.keys()) resolvePlaceholder(objectId);

  const slideIdsByLayout = new Map();
  for (const slide of snapshot.slides ?? []) {
    if (!slideIdsByLayout.has(slide.layoutId)) slideIdsByLayout.set(slide.layoutId, []);
    slideIdsByLayout.get(slide.layoutId).push(slide.objectId);
  }

  const masterCatalog = (snapshot.masters ?? []).map((master) => ({
    masterId: master.objectId,
    displayName: master.displayName ?? master.name ?? null,
    effectivePageProperties: effectivePageProperties.get(master.objectId) ?? null,
    themeColors: themeColors(effectivePageProperties.get(master.objectId)),
    elementKinds: elementKinds(master.elements),
    placeholderObjectIds: flattenPageElements(master.elements).filter((element) => element.placeholder).map((element) => element.objectId),
    protectedRegions: protectedRegionsForPage(master, "master", pageSize),
  }));

  const layoutCatalog = (snapshot.layouts ?? []).map((layout) => {
    const layoutLabel = `${layout.displayName ?? ""} ${layout.name ?? ""}`.trim();
    const slots = flattenPageElements(layout.elements).filter((element) => element.placeholder).map((element) => {
      const lineage = placeholderCache.get(element.objectId);
      const areaRatio = boundsAreaRatio(element.boundsPt, pageSize);
      return {
        objectId: element.objectId,
        type: element.placeholder.type,
        index: element.placeholder.index,
        parentObjectId: element.placeholder.parentObjectId,
        boundsPt: element.boundsPt ?? null,
        areaRatio,
        aspectRatio: aspectRatio(element.boundsPt?.width, element.boundsPt?.height),
        panel: panelGeometry(element.boundsPt, pageSize),
        semanticHints: semanticHints(element.placeholder, layoutLabel),
        renderedFontSizePtByNesting: lineage?.renderedFontSizePtByNesting ?? {},
      };
    });
    const placeholderCounts = {};
    for (const slot of slots) placeholderCounts[slot.type] = (placeholderCounts[slot.type] ?? 0) + 1;
    const previewSlideIds = slideIdsByLayout.get(layout.objectId) ?? [];
    const textSlots = slots.filter((slot) => TEXT_PLACEHOLDER_TYPES.has(slot.type));
    const mediaSlots = slots.filter((slot) => MEDIA_PLACEHOLDER_TYPES.has(slot.type));
    const dominantMediaSlot = [...mediaSlots].sort((left, right) => (right.areaRatio ?? 0) - (left.areaRatio ?? 0))[0] ?? null;
    return {
      layoutId: layout.objectId,
      masterId: layout.masterId,
      name: layout.name ?? null,
      displayName: layout.displayName ?? layout.name ?? null,
      effectivePageProperties: effectivePageProperties.get(layout.objectId) ?? null,
      themeColors: themeColors(effectivePageProperties.get(layout.objectId)),
      elementKinds: elementKinds(layout.elements),
      placeholderSlots: slots,
      signature: {
        placeholderCounts,
        placeholderTypes: uniqueSorted(slots.map((slot) => slot.type)),
        textSlotCount: textSlots.length,
        mediaSlotCount: mediaSlots.length,
        textAreaRatio: textSlots.reduce((sum, slot) => sum + (slot.areaRatio ?? 0), 0),
        mediaAreaRatio: mediaSlots.reduce((sum, slot) => sum + (slot.areaRatio ?? 0), 0),
        dominantMediaAspectRatio: dominantMediaSlot?.aspectRatio ?? null,
        dominantMediaAreaRatio: dominantMediaSlot?.areaRatio ?? null,
        dominantMediaPanel: dominantMediaSlot?.panel ?? null,
      },
      previewSlideIds,
      usageCount: previewSlideIds.length,
      protectedRegions: [
        ...protectedRegionsForPage(masters.get(layout.masterId), "master", pageSize),
        ...protectedRegionsForPage(layout, "layout", pageSize),
      ],
    };
  });

  const slideCatalog = (snapshot.slides ?? []).map((slide) => {
    const layout = layouts.get(slide.layoutId);
    const masterId = slide.masterId ?? layout?.masterId ?? null;
    const master = masters.get(masterId);
    const placeholderObjectIds = flattenPageElements(slide.elements).filter((element) => element.placeholder).map((element) => element.objectId);
    const placeholderLineage = placeholderObjectIds.map((objectId) => placeholderCache.get(objectId)).filter(Boolean);
    const inheritedVisualObjectIds = [master, layout].filter(Boolean).flatMap((page) =>
      flattenPageElements(page.elements).filter((element) => !element.placeholder).map((element) => element.objectId));
    const composition = localComposition(slide, pageSize);
    const localMedia = composition.objects.filter((entry) => entry.mediaGeometry);
    const dominantMedia = [...localMedia].sort((left, right) => (right.areaRatio ?? 0) - (left.areaRatio ?? 0))[0] ?? null;
    const attentionReasons = [];
    if (slide.isSkipped) attentionReasons.push("DELIVERED_SLIDE_SKIPPED");
    if (!layout) attentionReasons.push("LAYOUT_REFERENCE_MISSING");
    if (layout && !master) attentionReasons.push("MASTER_REFERENCE_MISSING");
    if (placeholderLineage.some((entry) => entry.missingParentObjectId || entry.cycle)) attentionReasons.push("PLACEHOLDER_LINEAGE_INVALID");
    if (placeholderLineage.some((entry) => Object.values(entry.renderedFontSizePtByNesting ?? {}).some((size) => size < 12))) attentionReasons.push("SMALL_EFFECTIVE_PLACEHOLDER_TEXT");
    if (composition.objects.some((entry) => ["image", "video", "sheetsChart", "table"].includes(entry.kind))) attentionReasons.push("MEDIA_OR_EVIDENCE");
    return {
      slideId: slide.objectId,
      index: slide.index,
      layoutId: slide.layoutId,
      masterId,
      isSkipped: slide.isSkipped === true,
      titlePreview: titlePreview(slide),
      effectivePageProperties: effectivePageProperties.get(slide.objectId) ?? null,
      placeholderLineage,
      effectiveContent: {
        directContentObjectIds: composition.contentBearingObjectIds,
        inheritedVisualObjectIds,
        hasDirectContent: composition.contentBearingObjectIds.length > 0,
        hasInheritedVisual: inheritedVisualObjectIds.length > 0,
      },
      localComposition: composition,
      mediaSignature: {
        mediaObjectCount: localMedia.length,
        occupiedAreaRatio: localMedia.reduce((sum, entry) => sum + (entry.areaRatio ?? 0), 0),
        dominantObjectId: dominantMedia?.objectId ?? null,
        dominantAspectRatio: dominantMedia?.mediaGeometry?.contentAspectRatioEstimate ?? dominantMedia?.aspectRatio ?? null,
        dominantAreaRatio: dominantMedia?.areaRatio ?? null,
        dominantPanel: dominantMedia?.panel ?? null,
      },
      protectedRegions: [
        ...protectedRegionsForPage(master, "master", pageSize),
        ...protectedRegionsForPage(layout, "layout", pageSize),
      ],
      attentionReasons: uniqueSorted(attentionReasons),
    };
  });

  return {
    version: 1,
    kind: "slides-derived-design-system",
    pageSizePt: clone(pageSize),
    multiMaster: masterCatalog.length > 1,
    masters: masterCatalog,
    layouts: layoutCatalog,
    slides: slideCatalog,
    placeholders: Object.fromEntries([...placeholderCache.entries()].sort(([left], [right]) => left.localeCompare(right))),
  };
}

export function designSystemSlide(snapshot, slideId) {
  return snapshot.designSystem?.slides?.find((slide) => slide.slideId === slideId) ?? null;
}

export function designSystemPlaceholder(snapshot, objectId) {
  return snapshot.designSystem?.placeholders?.[objectId] ?? null;
}

function formatRatio(value) {
  return Number.isFinite(value) ? `${(value * 100).toFixed(0)}%` : "unknown";
}

function oneLine(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

export function renderDesignCatalog(snapshot) {
  verifySnapshotHash(snapshot);
  const design = snapshot.designSystem;
  const lines = [
    "# Generated Slides Design Catalog",
    "",
    `- Presentation: ${oneLine(snapshot.presentation.title) || "(untitled)"}`,
    `- Presentation ID: \`${snapshot.presentation.id}\``,
    `- Snapshot SHA-256: \`${snapshot.sha256}\``,
    `- Masters: ${design.masters.length}`,
    `- Layouts: ${design.layouts.length}`,
    `- Slides available as exemplars: ${design.slides.length}`,
    "",
    "This is derived evidence, not a model-authored contract. Confirm semantic roles from rendered exemplars.",
    "",
    "## Masters",
    "",
    "| Master ID | Name | Layouts | Theme colors | Protected regions |",
    "| --- | --- | ---: | ---: | ---: |",
  ];
  for (const master of design.masters) {
    const layoutCount = design.layouts.filter((layout) => layout.masterId === master.masterId).length;
    lines.push(`| \`${master.masterId}\` | ${oneLine(master.displayName) || "(unnamed)"} | ${layoutCount} | ${Object.keys(master.themeColors).length} | ${master.protectedRegions.length} |`);
  }
  lines.push("", "## Layouts", "");
  for (const layout of design.layouts) {
    lines.push(
      `### ${oneLine(layout.displayName) || layout.layoutId}`,
      "",
      `- Layout ID: \`${layout.layoutId}\``,
      `- Master ID: \`${layout.masterId ?? "missing"}\``,
      `- Preview slides: ${layout.previewSlideIds.map((id) => `\`${id}\``).join(", ") || "none"}`,
      `- Text capacity signals: ${layout.signature.textSlotCount} slots covering ${formatRatio(layout.signature.textAreaRatio)} of the canvas`,
      `- Media/evidence signals: ${layout.signature.mediaSlotCount} slots covering ${formatRatio(layout.signature.mediaAreaRatio)} of the canvas`,
      `- Inherited protected regions: ${layout.protectedRegions.length}`,
      "",
      "| Placeholder ID | Type | Index | Area | Ratio | Panel | Suggested semantic roles |",
      "| --- | --- | ---: | ---: | ---: | --- | --- |",
    );
    for (const slot of layout.placeholderSlots) {
      const hints = slot.semanticHints.map((hint) => `${hint.role} (${hint.confidence})`).join(", ");
      const ratio = Number.isFinite(slot.aspectRatio) ? slot.aspectRatio.toFixed(2) : "unknown";
      lines.push(`| \`${slot.objectId}\` | ${slot.type} | ${slot.index ?? 0} | ${formatRatio(slot.areaRatio)} | ${ratio} | ${slot.panel?.classification ?? "unknown"} | ${hints || "none"} |`);
    }
    if (layout.placeholderSlots.length === 0) lines.push("| (none) | | | | | | |");
    lines.push("");
  }
  lines.push(
    "## Exemplar Slides",
    "",
    "| # | Slide ID | Layout | Title/content preview | Local content objects | Dominant media | Attention |",
    "| ---: | --- | --- | --- | ---: | --- | --- |",
  );
  for (const slide of design.slides) {
    const media = slide.mediaSignature;
    const mediaSummary = media?.dominantObjectId
      ? `${Number.isFinite(media.dominantAspectRatio) ? media.dominantAspectRatio.toFixed(2) : "?"} ratio; ${formatRatio(media.dominantAreaRatio)} area; ${media.dominantPanel?.classification ?? "unknown"}`
      : "none";
    lines.push(`| ${slide.index + 1} | \`${slide.slideId}\` | \`${slide.layoutId ?? "missing"}\` | ${oneLine(slide.titlePreview) || "(none)"} | ${slide.localComposition.slideLocalContentObjectIds.length} | ${mediaSummary} | ${slide.attentionReasons.join(", ") || "none"} |`);
  }
  lines.push("");
  return `${lines.join("\n")}\n`;
}
