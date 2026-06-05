import { media } from "@wix/sdk";

export type WixImage = {
  url: string;
  altText?: string;
  width?: number;
  height?: number;
};

export function resolveWixImage(
  image: string | { id?: string; url?: string } | undefined
): WixImage | null {
  if (!image) return null;

  if (typeof image === "string") {
    if (image.startsWith("wix:image://")) {
      const resolved = media.getImageUrl(image);
      return { url: resolved.url, width: resolved.width, height: resolved.height };
    }
    return { url: image };
  }

  if (image.url) {
    return { url: image.url };
  }

  if (image.id) {
    const resolved = media.getImageUrl(image.id);
    return { url: resolved.url, width: resolved.width, height: resolved.height };
  }

  return null;
}

export function scaledSrc(img: WixImage, width: number): string {
  const url = new URL(img.url);
  url.searchParams.set("w", String(width));
  return url.toString();
}

export function srcSet(img: WixImage, widths: number[]): string {
  return widths.map((w) => `${scaledSrc(img, w)} ${w}w`).join(", ");
}

// Consumed by every vertical that renders a Wix image at a specific size
// (stores ProductCard + detail page, blog post hero, cms list thumbnails).
// Kept alongside resolveWixImage so verticals do not ship their own copy.
export function resolveWixImageUrl(
  image: string | { id?: string; url?: string } | undefined,
  width?: number,
  height?: number,
): string | null {
  if (!image) return null;

  if (
    typeof image === "string" &&
    image.startsWith("wix:image://") &&
    width != null &&
    height != null
  ) {
    return media.getScaledToFillImageUrl(image, width, height, {});
  }

  const resolved = resolveWixImage(image);
  if (!resolved) return null;
  if (width == null && height == null) return resolved.url;

  const url = new URL(resolved.url);
  if (width != null) url.searchParams.set("w", String(width));
  if (height != null) url.searchParams.set("h", String(height));
  return url.toString();
}
