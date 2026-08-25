import {
  assert,
  findFirstRecord,
  firstDefined,
  isRecord,
  redactSensitive,
  sha256Json,
  uniqueSorted,
} from "./common.mjs";
import { buildDesignSystem } from "./design-system.mjs";
import { unwrapCallToolResult } from "./result.mjs";

const EMU_PER_POINT = 12700;

export function dimensionToPoints(dimension) {
  if (dimension === null || dimension === undefined) return null;
  if (typeof dimension === "number") return dimension;
  if (!isRecord(dimension)) return null;

  const magnitude = Number(dimension.magnitude);
  if (!Number.isFinite(magnitude)) return null;
  const unit = String(dimension.unit ?? "PT").toUpperCase();
  if (unit === "PT" || unit === "POINT" || unit === "POINTS") return magnitude;
  if (unit === "EMU") return magnitude / EMU_PER_POINT;
  if (unit === "IN" || unit === "INCH" || unit === "INCHES") return magnitude * 72;
  if (unit === "PX") return magnitude * 0.75;
  return null;
}

function textFromElements(textElements) {
  if (!Array.isArray(textElements)) return "";
  return textElements
    .map((element) => element?.textRun?.content ?? element?.autoText?.content ?? "")
    .join("");
}

function normalizeText(text) {
  if (!isRecord(text)) return null;
  const elements = Array.isArray(text.textElements) ? text.textElements : [];
  const runs = [];
  const paragraphs = [];
  const styleDefaultsByNesting = {};
  const stylePriorityByNesting = {};
  let cursor = 0;
  let nestingLevel = 0;

  for (const element of elements) {
    const content = element?.textRun?.content ?? element?.autoText?.content ?? "";
    const startIndex = Number.isInteger(element?.startIndex) ? element.startIndex : cursor;
    const endIndex = Number.isInteger(element?.endIndex) ? element.endIndex : startIndex + content.length;
    if (element?.paragraphMarker) {
      nestingLevel = Number(element.paragraphMarker.bullet?.nestingLevel ?? 0);
      paragraphs.push({
        startIndex,
        endIndex,
        style: element.paragraphMarker.style ?? null,
        bullet: element.paragraphMarker.bullet ?? null,
      });
    }
    if (element?.textRun || element?.autoText) {
      const style = element.textRun?.style ?? element.autoText?.style ?? null;
      runs.push({
        startIndex,
        endIndex,
        content,
        style,
        kind: element.textRun ? "textRun" : "autoText",
        autoTextType: element.autoText?.type ?? null,
        nestingLevel,
      });
      if (isRecord(style)) {
        const key = String(nestingLevel);
        const priority = content.includes("\n") ? 2 : 1;
        if ((stylePriorityByNesting[key] ?? 0) <= priority) {
          styleDefaultsByNesting[key] = style;
          stylePriorityByNesting[key] = priority;
        }
      }
    }
    cursor = Math.max(cursor, endIndex);
  }

  return {
    plainText: textFromElements(elements),
    runs,
    paragraphs,
    lists: text.lists ?? null,
    styleDefaultsByNesting,
  };
}

function normalizeTable(table) {
  if (!isRecord(table)) return null;
  const rows = Array.isArray(table.tableRows) ? table.tableRows : [];
  return {
    rows: Number(table.rows ?? rows.length),
    columns: Number(table.columns ?? rows[0]?.tableCells?.length ?? 0),
    cells: rows.map((row, rowIndex) =>
      (row.tableCells ?? []).map((cell, columnIndex) => ({
        rowIndex,
        columnIndex,
        text: normalizeText(cell.text),
        rowSpan: cell.rowSpan ?? 1,
        columnSpan: cell.columnSpan ?? 1,
        properties: cell.tableCellProperties ?? null,
      })),
    ),
  };
}

function elementKind(element) {
  for (const key of [
    "shape",
    "image",
    "table",
    "line",
    "wordArt",
    "sheetsChart",
    "video",
    "speakerSpotlight",
    "elementGroup",
  ]) {
    if (element?.[key] !== undefined) return key;
  }
  return "unknown";
}

function affineMatrix(transform = {}) {
  const translateX = dimensionToPoints({ magnitude: transform.translateX ?? 0, unit: transform.unit ?? "PT" });
  const translateY = dimensionToPoints({ magnitude: transform.translateY ?? 0, unit: transform.unit ?? "PT" });
  const values = [transform.scaleX ?? 1, transform.scaleY ?? 1, transform.shearX ?? 0, transform.shearY ?? 0].map(Number);
  if (translateX === null || translateY === null || values.some((value) => !Number.isFinite(value))) return null;
  const [scaleX, scaleY, shearX, shearY] = values;
  return { a: scaleX, b: shearY, c: shearX, d: scaleY, e: translateX, f: translateY };
}

function multiplyAffine(left, right) {
  return {
    a: left.a * right.a + left.c * right.b,
    b: left.b * right.a + left.d * right.b,
    c: left.a * right.c + left.c * right.d,
    d: left.b * right.c + left.d * right.d,
    e: left.a * right.e + left.c * right.f + left.e,
    f: left.b * right.e + left.d * right.f + left.f,
  };
}

function normalizeGeometry(element, parentMatrix = null) {
  const size = element?.size ?? {};
  const transform = element?.transform ?? {};
  const width = dimensionToPoints(size.width);
  const height = dimensionToPoints(size.height);
  const localMatrix = affineMatrix(transform);
  const absoluteMatrix = parentMatrix && localMatrix ? multiplyAffine(parentMatrix, localMatrix) : localMatrix;
  const serializedMatrix = absoluteMatrix
    ? {
        scaleX: absoluteMatrix.a,
        shearY: absoluteMatrix.b,
        shearX: absoluteMatrix.c,
        scaleY: absoluteMatrix.d,
        translateX: absoluteMatrix.e,
        translateY: absoluteMatrix.f,
        unit: "PT",
      }
    : null;
  if (width === null || height === null || !absoluteMatrix) {
    return { boundsPt: null, absoluteMatrix, absoluteTransform: serializedMatrix };
  }
  const points = [
    [0, 0],
    [width, 0],
    [0, height],
    [width, height],
  ].map(([x, y]) => ({
    x: absoluteMatrix.a * x + absoluteMatrix.c * y + absoluteMatrix.e,
    y: absoluteMatrix.b * x + absoluteMatrix.d * y + absoluteMatrix.f,
  }));
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  return {
    boundsPt: {
      x: Math.min(...xs),
      y: Math.min(...ys),
      width: Math.max(...xs) - Math.min(...xs),
      height: Math.max(...ys) - Math.min(...ys),
      rotatedOrSkewed: Boolean(absoluteMatrix.b || absoluteMatrix.c || absoluteMatrix.a < 0 || absoluteMatrix.d < 0),
    },
    absoluteMatrix,
    absoluteTransform: serializedMatrix,
  };
}

function normalizeElement(element, pageId, parentMatrix = null, groupChild = false) {
  const kind = elementKind(element);
  const shape = element?.shape ?? null;
  const objectId = element?.objectId ?? element?.id ?? null;
  const geometry = normalizeGeometry(element, parentMatrix);
  return {
    objectId,
    pageId,
    kind,
    placeholderType: shape?.placeholder?.type ?? null,
    placeholder: shape?.placeholder
      ? {
          type: shape.placeholder.type ?? null,
          index: Number.isInteger(shape.placeholder.index) ? shape.placeholder.index : 0,
          parentObjectId: shape.placeholder.parentObjectId ?? null,
        }
      : null,
    shapeType: shape?.shapeType ?? null,
    shapeProperties: shape?.shapeProperties ?? null,
    boundsPt: geometry.boundsPt,
    transform: element?.transform ?? null,
    absoluteTransform: geometry.absoluteTransform,
    groupChild,
    size: element?.size ?? null,
    text: normalizeText(shape?.text),
    table: normalizeTable(element?.table),
    wordArt: element?.wordArt
      ? { renderedText: element.wordArt.renderedText ?? "" }
      : null,
    image: element?.image
      ? {
          contentUrl: element.image.contentUrl ? "[EPHEMERAL_URL]" : null,
          sourceUrl: element.image.sourceUrl ?? null,
          properties: element.image.imageProperties ?? null,
        }
      : null,
    sheetsChart: element?.sheetsChart ?? null,
    video: element?.video ?? null,
    speakerSpotlight: element?.speakerSpotlight ?? null,
    line: element?.line ?? null,
    group: element?.elementGroup
      ? {
          children: (element.elementGroup.children ?? []).map((child) =>
            normalizeElement(child, pageId, geometry.absoluteMatrix, true)),
        }
      : null,
    description: element?.description ?? null,
    title: element?.title ?? null,
  };
}

function normalizeNotes(slide) {
  const notesPage = slide?.notesPage ?? slide?.slideProperties?.notesPage;
  if (!isRecord(notesPage)) return { objectId: null, text: "", elements: [] };
  const notesObjectId = notesPage?.notesProperties?.speakerNotesObjectId ?? null;
  const elements = (notesPage.pageElements ?? []).map((element) => normalizeElement(element, notesPage.objectId));
  const notesElement = elements.find((element) => element.objectId === notesObjectId);
  return {
    objectId: notesObjectId,
    text: notesElement?.text?.plainText ?? "",
    elements,
  };
}

function normalizePage(page, index, kind) {
  const objectId = page?.objectId ?? page?.id ?? null;
  const properties =
    kind === "slide"
      ? page?.slideProperties
      : kind === "layout"
        ? page?.layoutProperties
        : page?.masterProperties;
  return {
    objectId,
    index,
    kind,
    layoutId: page?.slideProperties?.layoutObjectId ?? null,
    masterId: properties?.masterObjectId ?? null,
    name: properties?.name ?? properties?.displayName ?? null,
    displayName: properties?.displayName ?? properties?.name ?? null,
    revisionId: page?.revisionId ?? null,
    isSkipped: kind === "slide" ? page?.slideProperties?.isSkipped === true : false,
    pageProperties: page?.pageProperties ?? null,
    elements: (page?.pageElements ?? []).map((element) => normalizeElement(element, objectId)),
    notes: kind === "slide" ? normalizeNotes(page) : null,
    properties: properties ?? null,
  };
}

function locatePresentation(value) {
  const directCandidates = [
    value?.presentation,
    value?.result?.presentation,
    value?.data?.presentation,
    value?.result,
    value?.data,
    value,
  ];
  for (const candidate of directCandidates) {
    if (isRecord(candidate) && (Array.isArray(candidate.slides) || candidate.presentationId || candidate.pageSize)) {
      return candidate;
    }
  }
  return findFirstRecord(
    value,
    (candidate) => Array.isArray(candidate.slides) && (candidate.presentationId || candidate.title || candidate.pageSize),
  );
}

function indexPages(pages) {
  const objectIndex = {};
  const visitElement = (element, pageId) => {
    if (element.objectId) objectIndex[element.objectId] = { pageId, kind: element.kind };
    for (const child of element.group?.children ?? []) visitElement(child, pageId);
  };
  for (const page of pages) {
    if (page.objectId) objectIndex[page.objectId] = { pageId: page.objectId, kind: page.kind };
    for (const element of page.elements) visitElement(element, page.objectId);
    for (const element of page.notes?.elements ?? []) {
      visitElement({ ...element, kind: "notes" }, page.objectId);
    }
  }
  return objectIndex;
}

export function normalizePresentation(raw, { presentationId = null } = {}) {
  const unwrapped = unwrapCallToolResult(raw);
  const presentation = locatePresentation(unwrapped);
  assert(presentation, "Could not locate a presentation object in the connector result");

  const id = firstDefined(presentation, [
    ["presentationId"],
    ["presentation_id"],
    ["id"],
  ]) ?? presentationId;
  const title = firstDefined(presentation, [["title"], ["name"]]) ?? null;
  const revisionId = firstDefined(presentation, [
    ["revisionId"],
    ["revision_id"],
    ["writeControl", "requiredRevisionId"],
    ["write_control", "requiredRevisionId"],
    ["metadata", "revisionId"],
  ]) ?? firstDefined(unwrapped, [
    ["revisionId"],
    ["revision_id"],
    ["writeControl", "requiredRevisionId"],
    ["metadata", "revisionId"],
  ]) ?? null;

  const slides = (presentation.slides ?? []).map((slide, index) => normalizePage(slide, index, "slide"));
  const layouts = (presentation.layouts ?? []).map((layout, index) => normalizePage(layout, index, "layout"));
  const masters = (presentation.masters ?? []).map((master, index) => normalizePage(master, index, "master"));
  const pages = [...slides, ...layouts, ...masters];
  const pageSize = presentation.pageSize ?? {};

  const payload = {
    snapshotVersion: 2,
    presentation: {
      id,
      title,
      revisionId,
      locale: presentation.locale ?? null,
      pageSizePt: {
        width: dimensionToPoints(pageSize.width),
        height: dimensionToPoints(pageSize.height),
      },
      slideCount: slides.length,
      slideIds: slides.map((slide) => slide.objectId),
    },
    slides,
    layouts,
    masters,
    objectIndex: indexPages(pages),
    rawPresentation: redactSensitive(presentation),
  };
  payload.designSystem = buildDesignSystem(payload);

  return { ...payload, sha256: sha256Json(payload) };
}

function oneLine(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

export function renderSlideInventory(snapshot) {
  const lines = [
    "# Slide Inventory",
    "",
    `- Presentation ID: \`${snapshot.presentation.id ?? "missing"}\``,
    `- Title: ${snapshot.presentation.title ?? "(missing)"}`,
    `- Revision ID: \`${snapshot.presentation.revisionId ?? "missing"}\``,
    `- Snapshot SHA-256: \`${snapshot.sha256}\``,
    `- Slide count: ${snapshot.slides.length}`,
    "",
    "| # | Slide ID | Layout ID | Master ID | Skipped | Elements | Title/Text Preview |",
    "| ---: | --- | --- | --- | --- | ---: | --- |",
  ];

  for (const slide of snapshot.slides) {
    const flatten = (elements) => elements.flatMap((element) => [element, ...flatten(element.group?.children ?? [])]);
    const elements = flatten(slide.elements);
    const texts = elements
      .flatMap((element) => [
        element.text?.plainText,
        element.wordArt?.renderedText,
        ...(element.table?.cells ?? []).flatMap((row) => (row ?? []).map((cell) => cell.text?.plainText)),
      ])
      .filter(Boolean)
      .map(oneLine);
    const preview = texts.join(" / ").slice(0, 180).replace(/\|/g, "\\|");
    lines.push(
      `| ${slide.index + 1} | \`${slide.objectId ?? "missing"}\` | \`${slide.layoutId ?? ""}\` | \`${slide.masterId ?? ""}\` | ${slide.isSkipped ? "yes" : "no"} | ${elements.length} | ${preview} |`,
    );
  }

  const kinds = uniqueSorted(
    snapshot.slides.flatMap((slide) => {
      const flatten = (elements) => elements.flatMap((element) => [element, ...flatten(element.group?.children ?? [])]);
      return flatten(slide.elements).map((element) => element.kind);
    }),
  );
  lines.push("", `Element kinds: ${kinds.join(", ") || "none"}`, "");
  return lines.join("\n");
}
