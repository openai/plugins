import { dimensionToPoints } from "./normalize.mjs";

const HARD_READABILITY_FLOOR_PT = 8;
const NARRATIVE_TARGET_PT = 12;
const DEFAULT_MAX_ISSUES = 100;

const PROTECTED_PLACEHOLDER_TYPES = new Set([
  "CAPTION",
  "DATE_AND_TIME",
  "FOOTER",
  "HEADER",
  "SLIDE_NUMBER",
]);
const TEXT_PLACEHOLDER_TYPES = new Set(["BODY", "CENTERED_TITLE", "SUBTITLE", "TITLE"]);
const NARRATIVE_PLACEHOLDER_TYPES = new Set(["BODY", "CENTERED_TITLE", "OBJECT", "SUBTITLE", "TITLE"]);

const VISIBLE_BULLET_MARKER =
  /^\s*(?<marker>[\u2022\u2023\u2024\u2027\u2043\u204C\u204D\u2219\u25AA\u25AB\u25CF\u25CB\u25A0\u25A1\u25C6\u25C7\u279C\u27A4\u2192\u21D2])(?=\s)/u;
const DUPLICATE_LIST_MARKER =
  /^\s*(?<marker>(?:[\u2022\u2023\u2024\u2027\u2043\u204C\u204D\u2219\u25AA\u25AB\u25CF\u25CB\u25A0\u25A1\u25C6\u25C7\u279C\u27A4\u2192\u21D2]|-\s*>|->|=>|[-\u2013\u2014]|\d{1,2}[.)]|[A-Za-z][.)]))(?=\s)/u;

const GENERIC_PLACEHOLDER_PATTERNS = [
  /\blorem ipsum\b/i,
  /\bclick to add (?:title|text|subtitle|media|image)\b/i,
  /^\s*(?:sample|placeholder)\s+(?:title|text|copy|name|image|media)\s*$/i,
  /^\s*(?:title|subtitle|speaker name|image|media|demo|chart|table)\s+goes\s+here\s*$/i,
  /^\s*demo\s+can\s+be\s+(?:embedded|inserted|placed)\s+here\s*$/i,
  /^\s*[\[<{].*\b(?:insert|add|replace|paste|upload|drop|embed|place|placeholder|sample|demo|goes\s+here)\b.*[\]}>]\s*$/i,
  /^\s*(?:insert|add|replace|paste|upload|drop|embed|place)\b[^\n]{0,160}\b(?:here|below|above|this)\b/i,
];

function flattenElements(elements) {
  return (elements ?? []).flatMap((element) => [element, ...flattenElements(element.group?.children)]);
}

function textSurfaces(element) {
  const surfaces = [];
  if (element.text) surfaces.push({ key: "shape", text: element.text, cellLocation: null });
  for (const row of element.table?.cells ?? []) {
    for (const cell of row ?? []) {
      if (!cell.text) continue;
      surfaces.push({
        key: `table:${cell.rowIndex}:${cell.columnIndex}`,
        text: cell.text,
        cellLocation: { rowIndex: cell.rowIndex, columnIndex: cell.columnIndex },
      });
    }
  }
  return surfaces;
}

function paragraphRanges(text) {
  const plainText = String(text?.plainText ?? "");
  const markers = [...(text?.paragraphs ?? [])]
    .filter((paragraph) => Number.isInteger(paragraph?.startIndex))
    .sort((left, right) => left.startIndex - right.startIndex);
  if (markers.length > 0) {
    return markers.map((paragraph, index) => {
      const startIndex = paragraph.startIndex;
      const endIndex = Math.max(startIndex, Number(markers[index + 1]?.startIndex ?? plainText.length));
      return {
        startIndex,
        endIndex,
        content: plainText.slice(startIndex, endIndex).replace(/\n+$/g, ""),
        bullet: paragraph.bullet ?? null,
      };
    });
  }

  const ranges = [];
  let startIndex = 0;
  for (const line of plainText.split("\n")) {
    ranges.push({ startIndex, endIndex: startIndex + line.length, content: line, bullet: null });
    startIndex += line.length + 1;
  }
  return ranges;
}

function explicitMinimumFontSize(text, element) {
  const scaleValue = Number(element.shapeProperties?.autofit?.fontScale ?? 1);
  const scale = Number.isFinite(scaleValue) && scaleValue > 0 ? scaleValue : 1;
  const sizes = (text?.runs ?? [])
    .filter((run) => String(run.content ?? "").trim().length > 0)
    .map((run) => dimensionToPoints(run.style?.fontSize))
    .filter(Number.isFinite)
    .map((size) => size * scale);
  return {
    minimumFontSizePt: sizes.length > 0 ? Math.min(...sizes) : null,
    autofitScale: scale,
  };
}

function isSupportingText(element, text, pageHeightPt) {
  if (PROTECTED_PLACEHOLDER_TYPES.has(element.placeholderType)) return true;
  const value = String(text?.plainText ?? "").trim();
  const bounds = element.boundsPt;
  const bottomBand = Number.isFinite(pageHeightPt) && bounds &&
    bounds.y >= pageHeightPt * 0.8 && bounds.height <= pageHeightPt * 0.2;
  const supportingLabel = /^(?:source|sources|note|notes|footnote|confidential|internal use|©)\b/i.test(value);
  return value.length <= 240 && (bottomBand || supportingLabel);
}

function isLikelyNarrative(element, text) {
  if (NARRATIVE_PLACEHOLDER_TYPES.has(element.placeholderType)) return true;
  if ((text?.paragraphs ?? []).some((paragraph) => Boolean(paragraph.bullet))) return true;
  const value = String(text?.plainText ?? "").trim();
  if (element.kind === "table") return value.length >= 40;
  return value.length >= 80;
}

function isGenericPlaceholder(value) {
  const text = String(value ?? "").trim();
  return text.length > 0 && GENERIC_PLACEHOLDER_PATTERNS.some((pattern) => pattern.test(text));
}

function issueId(issue) {
  const location = issue.cellLocation
    ? `${issue.cellLocation.rowIndex}-${issue.cellLocation.columnIndex}`
    : issue.surface ?? "slide";
  const startIndex = issue.range?.startIndex ?? "all";
  return [issue.code, issue.slideId, issue.objectId ?? issue.slideId, location, startIndex]
    .map((part) => String(part ?? "unknown").replace(/[^A-Za-z0-9_-]+/g, "-"))
    .join(":");
}

function compareIssues(left, right) {
  return left.slideIndex - right.slideIndex ||
    (left.severity === right.severity ? 0 : left.severity === "error" ? -1 : 1) ||
    left.code.localeCompare(right.code) ||
    String(left.objectId ?? "").localeCompare(String(right.objectId ?? "")) ||
    Number(left.range?.startIndex ?? 0) - Number(right.range?.startIndex ?? 0);
}

function countBy(items, key) {
  return Object.fromEntries(
    [...new Set(items.map((item) => item[key]))]
      .sort()
      .map((value) => [value, items.filter((item) => item[key] === value).length]),
  );
}

export function inspectOutputIssues(snapshot, { maxIssues = DEFAULT_MAX_ISSUES } = {}) {
  const limit = Number(maxIssues);
  if (!Number.isInteger(limit) || limit < 1 || limit > 1000) {
    throw new Error("maxIssues must be an integer between 1 and 1000");
  }

  const issues = [];
  const add = (issue) => issues.push({ id: issueId(issue), ...issue });
  const pageHeightPt = Number(snapshot?.presentation?.pageSizePt?.height);

  for (const slide of snapshot.slides ?? []) {
    const slideId = slide.objectId;
    const slideIndex = slide.index;
    if ((slide.elements ?? []).length === 0) {
      add({
        code: "BLANK_SLIDE",
        severity: "warning",
        slideId,
        slideIndex,
        objectId: slideId,
        surface: "slide",
        message: "The slide has no slide-local page elements.",
        remediation: "Confirm the slide is intentionally blank; otherwise populate it from its selected exemplar.",
      });
    }

    for (const element of flattenElements(slide.elements)) {
      const objectId = element.objectId;
      const plainShapeText = String(element.text?.plainText ?? "").trim();
      if (element.kind === "shape" && TEXT_PLACEHOLDER_TYPES.has(element.placeholderType) && !plainShapeText) {
        add({
          code: "EMPTY_TEXT_PLACEHOLDER",
          severity: "warning",
          slideId,
          slideIndex,
          objectId,
          surface: "shape",
          message: `An empty ${element.placeholderType} placeholder remains on the slide.`,
          remediation: "Populate it or delete it when the selected exemplar does not need that slot.",
        });
      }

      for (const surface of textSurfaces(element)) {
        const value = String(surface.text?.plainText ?? "").trim();
        const location = {
          slideId,
          slideIndex,
          objectId,
          surface: surface.key,
          ...(surface.cellLocation ? { cellLocation: surface.cellLocation } : {}),
        };

        if (isGenericPlaceholder(value)) {
          add({
            code: "GENERIC_PLACEHOLDER_TEXT",
            severity: "error",
            ...location,
            message: "Visible editor instruction or generic placeholder text remains.",
            remediation: "Replace it with final content or remove the underlying template object.",
            evidence: { textPreview: value.slice(0, 160) },
          });
        }

        for (const paragraph of paragraphRanges(surface.text)) {
          if (paragraph.bullet && paragraph.content.trim().length === 0 && paragraph.endIndex > paragraph.startIndex) {
            add({
              code: "EMPTY_BULLET_PARAGRAPH",
              severity: "error",
              ...location,
              range: { startIndex: paragraph.startIndex, endIndex: paragraph.endIndex },
              message: "A whitespace-only native bullet paragraph can render a stray bullet.",
              remediation: "Delete the empty paragraph range or remove its bullet formatting.",
            });
            continue;
          }

          const duplicate = paragraph.bullet ? DUPLICATE_LIST_MARKER.exec(paragraph.content) : null;
          if (duplicate) {
            add({
              code: "DUPLICATE_LIST_MARKER",
              severity: "error",
              ...location,
              range: { startIndex: paragraph.startIndex, endIndex: paragraph.endIndex },
              message: "A native bulleted paragraph also begins with a typed list marker.",
              remediation: "Remove the typed marker and preserve the paragraph's native bullet formatting.",
              evidence: {
                marker: duplicate.groups?.marker ?? duplicate[0].trim(),
                textPreview: paragraph.content.trim().slice(0, 120),
              },
            });
            continue;
          }

          const literal = paragraph.bullet ? null : VISIBLE_BULLET_MARKER.exec(paragraph.content);
          if (literal) {
            add({
              code: "LITERAL_BULLET_CHARACTER",
              severity: "warning",
              ...location,
              range: { startIndex: paragraph.startIndex, endIndex: paragraph.endIndex },
              message: "A paragraph begins with a typed bullet character instead of native list formatting.",
              remediation: "Use a native bullet unless this character is an intentional template-native decorative element.",
              evidence: {
                marker: literal.groups?.marker ?? literal[0].trim(),
                textPreview: paragraph.content.trim().slice(0, 120),
              },
            });
          }
        }

        if (!value || isSupportingText(element, surface.text, pageHeightPt) || !isLikelyNarrative(element, surface.text)) continue;
        const { minimumFontSizePt, autofitScale } = explicitMinimumFontSize(surface.text, element);
        if (!Number.isFinite(minimumFontSizePt)) continue;
        const roundedSize = Math.round(minimumFontSizePt * 10) / 10;
        if (minimumFontSizePt < HARD_READABILITY_FLOOR_PT) {
          add({
            code: "TEXT_EFFECTIVELY_UNREADABLE",
            severity: "error",
            ...location,
            message: `Narrative text explicitly renders at ${roundedSize} pt, below the ${HARD_READABILITY_FLOOR_PT} pt hard floor.`,
            remediation: "Restore a readable template size, then shorten the copy or select a denser appropriate exemplar.",
            evidence: { minimumFontSizePt: roundedSize, autofitScale, textPreview: value.slice(0, 160) },
          });
        } else if (minimumFontSizePt < NARRATIVE_TARGET_PT) {
          add({
            code: "TEXT_BELOW_NARRATIVE_TARGET",
            severity: "warning",
            ...location,
            message: `Narrative text explicitly renders at ${roundedSize} pt, below the ${NARRATIVE_TARGET_PT} pt target.`,
            remediation: "Preserve the template size when possible; otherwise shorten the copy or choose a denser exemplar instead of shrinking further.",
            evidence: { minimumFontSizePt: roundedSize, autofitScale, textPreview: value.slice(0, 160) },
          });
        }
      }
    }
  }

  issues.sort(compareIssues);
  const reported = issues.slice(0, limit);
  return {
    schemaVersion: 1,
    presentation: {
      id: snapshot.presentation?.id ?? null,
      title: snapshot.presentation?.title ?? null,
      revisionId: snapshot.presentation?.revisionId ?? null,
      slideCount: snapshot.presentation?.slideCount ?? snapshot.slides?.length ?? 0,
    },
    snapshotSha256: snapshot.sha256 ?? null,
    summary: {
      totalIssues: issues.length,
      reportedIssues: reported.length,
      truncated: reported.length < issues.length,
      bySeverity: countBy(issues, "severity"),
      byCode: countBy(issues, "code"),
    },
    issues: reported,
  };
}
