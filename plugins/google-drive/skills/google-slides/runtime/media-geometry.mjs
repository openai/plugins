import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { assert, isRecord } from "./common.mjs";
import { dimensionToPoints } from "./normalize.mjs";

const VERSION = "1.18";
const RATIO_TOLERANCE = 0.01;

function finitePositive(value) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : null;
}

export function aspectRatio(width, height) {
  const safeWidth = finitePositive(width);
  const safeHeight = finitePositive(height);
  return safeWidth && safeHeight ? safeWidth / safeHeight : null;
}

export function ratioDrift(left, right) {
  const a = finitePositive(left);
  const b = finitePositive(right);
  return a && b ? Math.abs(a / b - 1) : null;
}

export function panelGeometry(bounds, pageSize) {
  if (!bounds || !Number.isFinite(pageSize?.width) || !Number.isFinite(pageSize?.height)) return null;
  const centerX = bounds.x + bounds.width / 2;
  const centerY = bounds.y + bounds.height / 2;
  const areaRatio = bounds.width * bounds.height / (pageSize.width * pageSize.height);
  const horizontal = centerX < pageSize.width * 0.4 ? "left" : centerX > pageSize.width * 0.6 ? "right" : "center";
  const vertical = centerY < pageSize.height * 0.4 ? "top" : centerY > pageSize.height * 0.6 ? "bottom" : "middle";
  const fullWidth = bounds.width >= pageSize.width * 0.9;
  const fullHeight = bounds.height >= pageSize.height * 0.9;
  return {
    horizontal,
    vertical,
    classification: fullWidth && fullHeight ? "full-canvas" : fullWidth ? "horizontal-band" : fullHeight ? "vertical-band" : `${horizontal}-${vertical}`,
    areaRatio,
  };
}

export function cropGeometry(element) {
  const crop = element?.image?.properties?.cropProperties ?? element?.image?.imageProperties?.cropProperties ?? {};
  const left = Math.max(0, Number(crop.leftOffset ?? 0));
  const right = Math.max(0, Number(crop.rightOffset ?? 0));
  const top = Math.max(0, Number(crop.topOffset ?? 0));
  const bottom = Math.max(0, Number(crop.bottomOffset ?? 0));
  const visibleWidthFraction = Math.max(0, 1 - left - right);
  const visibleHeightFraction = Math.max(0, 1 - top - bottom);
  return {
    left,
    right,
    top,
    bottom,
    visibleWidthFraction,
    visibleHeightFraction,
    visibleAreaFraction: visibleWidthFraction * visibleHeightFraction,
  };
}

function transformedEdgeLengths(element) {
  const width = dimensionToPoints(element?.size?.width);
  const height = dimensionToPoints(element?.size?.height);
  const transform = element?.absoluteTransform ?? element?.transform ?? {};
  if (!finitePositive(width) || !finitePositive(height)) return null;
  const scaleX = Number(transform.scaleX ?? 1);
  const scaleY = Number(transform.scaleY ?? 1);
  const shearX = Number(transform.shearX ?? 0);
  const shearY = Number(transform.shearY ?? 0);
  if (![scaleX, scaleY, shearX, shearY].every(Number.isFinite)) return null;
  return {
    width: width * Math.hypot(scaleX, shearY),
    height: height * Math.hypot(shearX, scaleY),
  };
}

export function frameAspectRatio(element) {
  const edges = transformedEdgeLengths(element);
  return edges ? aspectRatio(edges.width, edges.height) : aspectRatio(element?.boundsPt?.width, element?.boundsPt?.height);
}

export function estimatedContentAspectRatio(element) {
  const frameRatio = frameAspectRatio(element);
  if (!frameRatio) return null;
  if (!element?.image) return frameRatio;
  const crop = cropGeometry(element);
  if (!(crop.visibleWidthFraction > 0) || !(crop.visibleHeightFraction > 0)) return null;
  return frameRatio * crop.visibleHeightFraction / crop.visibleWidthFraction;
}

export function mediaGeometry(element, pageSize) {
  const bounds = element?.boundsPt ?? null;
  const crop = element?.image ? cropGeometry(element) : null;
  return {
    mediaType: element?.kind ?? null,
    boundsPt: bounds,
    frameAspectRatio: frameAspectRatio(element),
    contentAspectRatioEstimate: estimatedContentAspectRatio(element),
    occupiedAreaRatio: bounds && Number.isFinite(pageSize?.width) && Number.isFinite(pageSize?.height)
      ? bounds.width * bounds.height / (pageSize.width * pageSize.height)
      : null,
    panel: panelGeometry(bounds, pageSize),
    crop,
  };
}

export function fitRect({ sourceAspectRatio, targetBounds, fit = "contain", alignX = 0.5, alignY = 0.5 } = {}) {
  const ratio = finitePositive(sourceAspectRatio);
  assert(ratio, "sourceAspectRatio must be positive", "sourceAspectRatio");
  assert(targetBounds && finitePositive(targetBounds.width) && finitePositive(targetBounds.height), "targetBounds must have positive width and height", "targetBounds");
  assert(["contain", "cover"].includes(fit), "fit must be contain or cover", "fit");
  assert(Number.isFinite(alignX) && alignX >= 0 && alignX <= 1, "alignX must be between 0 and 1", "alignX");
  assert(Number.isFinite(alignY) && alignY >= 0 && alignY <= 1, "alignY must be between 0 and 1", "alignY");
  const targetRatio = targetBounds.width / targetBounds.height;
  let width;
  let height;
  if ((fit === "contain" && ratio >= targetRatio) || (fit === "cover" && ratio < targetRatio)) {
    width = targetBounds.width;
    height = width / ratio;
  } else {
    height = targetBounds.height;
    width = height * ratio;
  }
  return {
    x: targetBounds.x + (targetBounds.width - width) * alignX,
    y: targetBounds.y + (targetBounds.height - height) * alignY,
    width,
    height,
    sourceAspectRatio: ratio,
    targetAspectRatio: targetRatio,
    fit,
  };
}

export function buildAspectSafeImageRequests({
  imageObjectId,
  url,
  targetElement,
  sourceAspectRatio,
  targetBounds = targetElement?.boundsPt,
  fit = "contain",
  alignX = 0.5,
  alignY = 0.5,
} = {}) {
  assert(typeof imageObjectId === "string" && imageObjectId.length > 0, "imageObjectId is required", "imageObjectId");
  assert(typeof url === "string" && url.length > 0, "url is required", "url");
  assert(targetElement?.kind === "image", "targetElement must be an image", "targetElement");
  const sourceRatio = finitePositive(sourceAspectRatio);
  assert(sourceRatio, "sourceAspectRatio must be positive", "sourceAspectRatio");
  const targetRatio = aspectRatio(targetBounds?.width, targetBounds?.height);
  assert(targetRatio, "targetBounds must have positive width and height", "targetBounds");
  assert(["contain", "cover"].includes(fit), "fit must be contain or cover", "fit");
  if (fit === "cover") {
    const visibleAreaFraction = Math.min(sourceRatio / targetRatio, targetRatio / sourceRatio);
    return {
      requests: [{ replaceImage: { imageObjectId, url, imageReplaceMethod: "CENTER_CROP" } }],
      analysis: { fit, sourceAspectRatio: sourceRatio, targetAspectRatio: targetRatio, visibleAreaFraction, expectedCropFraction: 1 - visibleAreaFraction },
    };
  }
  const rect = fitRect({ sourceAspectRatio: sourceRatio, targetBounds, fit: "contain", alignX, alignY });
  return {
    requests: [{ replaceImage: { imageObjectId, url, imageReplaceMethod: "CENTER_INSIDE" } }],
    analysis: { ...rect, expectedCropFraction: 0 },
  };
}

export function buildAspectSafeVideoRequest({ objectId, source, id, pageObjectId, sourceAspectRatio, targetBounds, alignX = 0.5, alignY = 0.5 } = {}) {
  const rect = fitRect({ sourceAspectRatio, targetBounds, fit: "contain", alignX, alignY });
  return {
    createVideo: {
      objectId,
      source,
      id,
      elementProperties: {
        pageObjectId,
        size: {
          width: { magnitude: rect.width, unit: "PT" },
          height: { magnitude: rect.height, unit: "PT" },
        },
        transform: { scaleX: 1, scaleY: 1, translateX: rect.x, translateY: rect.y, unit: "PT" },
      },
    },
  };
}

function pngDimensions(bytes) {
  if (bytes.length < 24 || bytes.toString("hex", 0, 8) !== "89504e470d0a1a0a") return null;
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), mimeType: "image/png", animated: false };
}

function gifDimensions(bytes) {
  if (bytes.length < 10 || !["GIF87a", "GIF89a"].includes(bytes.toString("ascii", 0, 6))) return null;
  return { width: bytes.readUInt16LE(6), height: bytes.readUInt16LE(8), mimeType: "image/gif", animated: true };
}

function jpegDimensions(bytes) {
  if (bytes.length < 4 || bytes[0] !== 0xff || bytes[1] !== 0xd8) return null;
  let offset = 2;
  while (offset + 9 < bytes.length) {
    if (bytes[offset] !== 0xff) { offset += 1; continue; }
    const marker = bytes[offset + 1];
    if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
      return { width: bytes.readUInt16BE(offset + 7), height: bytes.readUInt16BE(offset + 5), mimeType: "image/jpeg", animated: false };
    }
    const length = bytes.readUInt16BE(offset + 2);
    if (!Number.isInteger(length) || length < 2) break;
    offset += 2 + length;
  }
  return null;
}

export function imageMetadataFromBytes(bytes) {
  assert(Buffer.isBuffer(bytes), "image bytes must be a Buffer", "bytes");
  const metadata = pngDimensions(bytes) ?? gifDimensions(bytes) ?? jpegDimensions(bytes);
  assert(metadata && finitePositive(metadata.width) && finitePositive(metadata.height), "unsupported or invalid PNG, JPEG, or GIF", "bytes");
  return {
    ...metadata,
    aspectRatio: metadata.width / metadata.height,
    bytes: bytes.length,
    sha256: createHash("sha256").update(bytes).digest("hex"),
  };
}

export async function inspectImageFiles(paths = []) {
  const assets = [];
  for (const path of paths) {
    assert(typeof path === "string" && path.length > 0, "image path must be a non-empty string", "paths");
    const bytes = await readFile(path);
    assets.push({ path, ...imageMetadataFromBytes(bytes) });
  }
  return { version: VERSION, kind: "slides-media-assets", assets };
}

export function mediaAssetMap(manifest) {
  if (!isRecord(manifest) || manifest.kind !== "slides-media-assets" || !Array.isArray(manifest.assets)) return new Map();
  return new Map(manifest.assets.map((asset) => [asset.path, asset]));
}

export { RATIO_TOLERANCE };
