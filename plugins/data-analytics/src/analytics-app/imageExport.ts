import { useRef, useState } from "react";

type PreparedImageExportStatus = "idle" | "pending" | "ready" | "error";

type PreparedImageExport = {
  blob?: Blob;
  element: HTMLElement;
  error?: Error;
  promise: Promise<Blob>;
  startedAt: number;
  status: Exclude<PreparedImageExportStatus, "idle">;
};

export type ImageClipboardWriteResult = "native" | "html-fallback";

const IMAGE_EXPORT_PREPARE_TTL_MS = 30_000;

function shouldIncludeNodeInImageExport(node: unknown): boolean {
  const closest = (node as { closest?: unknown } | null)?.closest;
  if (typeof closest !== "function") return true;
  return closest.call(node, "[data-image-export-exclude='true']") === null;
}

function isVisibleColor(value: string): boolean {
  const color = value.trim().toLowerCase();
  if (!color || color === "transparent") return false;
  if (color.startsWith("rgba(") && /,\s*0(?:\.0+)?\s*\)$/.test(color)) return false;
  return color !== "rgba(0, 0, 0, 0)";
}

function resolvedImageExportBackground(element: HTMLElement): string {
  let current: HTMLElement | null = element;
  while (current) {
    const backgroundColor = getComputedStyle(current).backgroundColor;
    if (isVisibleColor(backgroundColor)) return backgroundColor;
    current = current.parentElement;
  }

  const bodyBackground = getComputedStyle(document.body).backgroundColor;
  return isVisibleColor(bodyBackground) ? bodyBackground : "#ffffff";
}

function scrubImageExportClone(clone: HTMLElement) {
  clone
    .querySelectorAll<HTMLElement>(
      [
        "[data-image-export-exclude='true']",
        ".analytics-layout-drop-indicator",
        ".analytics-layout-grab-handle",
        ".copy-toast",
        ".menu-surface",
        ".viz-card-menu",
        ".viz-card-menu-button",
        ".viz-card-submenu-list"
      ].join(", ")
    )
    .forEach((node) => node.remove());

  clone
    .querySelectorAll<HTMLElement>("[aria-expanded='true']")
    .forEach((node) => node.setAttribute("aria-expanded", "false"));

  clone.classList.remove(
    "intent-zone-after",
    "intent-zone-before",
    "intent-zone-end",
    "intent-zone-pair-after",
    "intent-zone-pair-before",
    "is-dragging",
    "is-drop-target"
  );
}

function createImageExportTarget(element: HTMLElement) {
  const rect = element.getBoundingClientRect();
  const width = Math.max(1, Math.ceil(rect.width || element.offsetWidth || element.scrollWidth));
  const backgroundColor = resolvedImageExportBackground(element);
  const sandbox = document.createElement("div");
  sandbox.setAttribute("data-image-export-sandbox", "true");
  sandbox.style.position = "fixed";
  sandbox.style.top = "0";
  sandbox.style.left = "-100000px";
  sandbox.style.width = `${width}px`;
  sandbox.style.pointerEvents = "none";
  sandbox.style.backgroundColor = backgroundColor;
  sandbox.style.colorScheme = getComputedStyle(document.documentElement).colorScheme;

  const clone = element.cloneNode(true) as HTMLElement;
  clone.setAttribute("data-image-export-root", "true");
  clone.style.width = `${width}px`;
  clone.style.maxWidth = `${width}px`;
  clone.style.margin = "0";
  clone.style.transform = "none";
  clone.style.pointerEvents = "none";
  scrubImageExportClone(clone);

  sandbox.appendChild(clone);
  document.body.appendChild(sandbox);

  return {
    backgroundColor,
    cleanup: () => sandbox.remove(),
    node: clone,
    width
  };
}

function nextAnimationFrame(): Promise<void> {
  return new Promise((resolve) => {
    window.requestAnimationFrame(() => resolve());
  });
}

function normalizePngBlob(blob: Blob): Blob {
  if (blob.type === "image/png") return blob;
  return new Blob([blob], { type: "image/png" });
}

async function renderElementAsImageBlob(element: HTMLElement): Promise<Blob> {
  const exportTarget = createImageExportTarget(element);
  try {
    await document.fonts?.ready;
    await nextAnimationFrame();
    const { getFontEmbedCSS, toBlob } = await import("html-to-image");
    const fontEmbedCSS = await getFontEmbedCSS(document.documentElement, {
      cacheBust: true,
      preferredFontFormat: "woff2"
    }).catch(() => "");
    const height = Math.max(
      1,
      Math.ceil(exportTarget.node.getBoundingClientRect().height || exportTarget.node.scrollHeight)
    );
    const blob = await toBlob(exportTarget.node, {
      backgroundColor: exportTarget.backgroundColor,
      cacheBust: true,
      filter: shouldIncludeNodeInImageExport,
      fontEmbedCSS: fontEmbedCSS || undefined,
      height,
      pixelRatio: Math.min(2, window.devicePixelRatio || 1),
      preferredFontFormat: "woff2",
      width: exportTarget.width
    });
    if (!blob) throw new Error("Failed to create image.");
    return normalizePngBlob(blob);
  } finally {
    exportTarget.cleanup();
  }
}

function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => resolve(String(reader.result)));
    reader.addEventListener("error", () => reject(reader.error ?? new Error("Failed to encode image.")));
    reader.readAsDataURL(blob);
  });
}

function copyRichImageToClipboard(dataUrl: string): boolean {
  const container = document.createElement("div");
  container.contentEditable = "true";
  container.style.position = "fixed";
  container.style.left = "-10000px";
  container.style.top = "0";
  container.innerHTML = `<img src="${dataUrl}" alt="Analytics app card" style="display:block;border:0;outline:0;box-shadow:none;max-width:100%;" />`;
  document.body.appendChild(container);

  const range = document.createRange();
  range.selectNodeContents(container);
  const selection = window.getSelection();
  selection?.removeAllRanges();
  selection?.addRange(range);
  const copied = document.execCommand("copy");
  selection?.removeAllRanges();
  document.body.removeChild(container);
  return copied;
}

function imageClipboardFallbackBlockedMessage(): string {
  return "Native image copy is blocked in this MCP app surface, and the browser fallback cannot reliably paste into apps like Slack or ChatGPT Desktop.";
}


function canUseRichImageClipboardFallback(): boolean {
  return typeof window === "undefined" || !window.openai;
}

export function shouldOfferImageClipboardCopy(): boolean {
  // The MCP host bridge blocks image clipboard writes, so the HTML fallback is
  // intentionally limited to standalone browser previews.
  return canUseRichImageClipboardFallback();
}

function copyImageWithFallback(dataUrl: string): ImageClipboardWriteResult {
  if (!canUseRichImageClipboardFallback()) {
    throw new Error(imageClipboardFallbackBlockedMessage());
  }
  if (copyRichImageToClipboard(dataUrl)) {
    return "html-fallback";
  }
  throw new Error("Copy is blocked by this browser.");
}

async function writeNativeImageToClipboard(blob: Blob): Promise<void> {
  if (typeof ClipboardItem === "undefined" || !navigator.clipboard?.write) {
    throw new Error("Clipboard image write is unavailable.");
  }
  await navigator.clipboard.write([new ClipboardItem({ "image/png": normalizePngBlob(blob) })]);
}

async function writeNativeImagePromiseToClipboard(blobPromise: Promise<Blob>): Promise<void> {
  if (typeof ClipboardItem === "undefined" || !navigator.clipboard?.write) {
    throw new Error("Clipboard image write is unavailable.");
  }
  await navigator.clipboard.write([
    new ClipboardItem({
      "image/png": blobPromise.then(normalizePngBlob)
    })
  ]);
}

async function copyImageBlob(blob: Blob, dataUrl: string): Promise<ImageClipboardWriteResult> {
  try {
    await writeNativeImageToClipboard(blob);
    return "native";
  } catch {
    return copyImageWithFallback(dataUrl);
  }
}

async function copyPreparedImageBlob(blob: Blob): Promise<ImageClipboardWriteResult> {
  try {
    await writeNativeImageToClipboard(blob);
    return "native";
  } catch {
    const dataUrl = await blobToDataUrl(blob);
    return copyImageWithFallback(dataUrl);
  }
}

export function usePreparedImageExport(elementRef: { current: HTMLElement | null }) {
  const preparedRef = useRef<PreparedImageExport | null>(null);
  const [preparedImageExportStatus, setPreparedImageExportStatus] = useState<PreparedImageExportStatus>("idle");

  function resetPreparedImageExport() {
    preparedRef.current = null;
    setPreparedImageExportStatus("idle");
  }

  function prepareImageExport(options: { force?: boolean } = {}): PreparedImageExport | null {
    const element = elementRef.current;
    if (!element) return null;

    const current = preparedRef.current;
    const now = Date.now();
    const currentIsFresh =
      current &&
      current.element === element &&
      current.status !== "error" &&
      now - current.startedAt < IMAGE_EXPORT_PREPARE_TTL_MS;
    if (current && currentIsFresh && (current.status === "pending" || !options.force)) {
      setPreparedImageExportStatus(current.status);
      return current;
    }

    const prepared: PreparedImageExport = {
      element,
      promise: Promise.resolve().then(() => renderElementAsImageBlob(element)),
      startedAt: now,
      status: "pending"
    };
    prepared.promise = prepared.promise
      .then((blob) => {
        prepared.blob = blob;
        prepared.status = "ready";
        if (preparedRef.current === prepared) setPreparedImageExportStatus("ready");
        return blob;
      })
      .catch((error) => {
        prepared.error = error instanceof Error ? error : new Error("Failed to prepare image.");
        prepared.status = "error";
        if (preparedRef.current === prepared) {
          preparedRef.current = null;
          setPreparedImageExportStatus("error");
        }
        throw prepared.error;
      });

    preparedRef.current = prepared;
    setPreparedImageExportStatus("pending");
    return prepared;
  }

  function getPreparedImageBlob(): Blob | null {
    const prepared = preparedRef.current;
    if (
      !prepared ||
      prepared.element !== elementRef.current ||
      prepared.status !== "ready" ||
      !prepared.blob ||
      Date.now() - prepared.startedAt >= IMAGE_EXPORT_PREPARE_TTL_MS
    ) {
      return null;
    }
    return prepared.blob;
  }

  return {
    getPreparedImageBlob,
    preparedImageExportStatus,
    prepareImageExport,
    resetPreparedImageExport
  };
}

export async function copyElementAsImage(
  element: HTMLElement,
  preparedBlob?: Blob | null
): Promise<ImageClipboardWriteResult> {
  if (preparedBlob) return copyPreparedImageBlob(preparedBlob);
  const blobPromise = renderElementAsImageBlob(element);
  try {
    await writeNativeImagePromiseToClipboard(blobPromise);
    return "native";
  } catch {
    const blob = await blobPromise;
    const dataUrl = await blobToDataUrl(blob);
    return copyImageBlob(blob, dataUrl);
  }
}

export function imageCopySuccessMessage(nativeMessage: string, result: ImageClipboardWriteResult): string {
  if (result === "native") return nativeMessage;
  return `${nativeMessage} Native image copy was blocked, so this browser fallback may not paste into apps like Slack or ChatGPT Desktop.`;
}

function copyTextWithSelection(text: string): boolean {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "true");
  textarea.style.position = "fixed";
  textarea.style.left = "-10000px";
  textarea.style.top = "0";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.focus({ preventScroll: true });
  textarea.select();
  textarea.setSelectionRange(0, text.length);
  let copied = false;
  try {
    copied = document.execCommand("copy");
  } catch {
    copied = false;
  }
  document.body.removeChild(textarea);
  return copied;
}

export async function copyTextToClipboard(text: string): Promise<void> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
  } catch {
    // Fall through to the selection-based fallback.
  }
  if (copyTextWithSelection(text)) return;
  throw new Error("Copy is blocked by this browser.");
}
