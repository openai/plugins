import { useState } from "react";

export type ImageClipboardWriteResult = "native" | "html-fallback";

export function shouldOfferImageClipboardCopy(): boolean {
  return false;
}
export function usePreparedImageExport() {
  const [preparedImageExportStatus] = useState<"idle">("idle");
  return {
    getPreparedImageBlob: () => null,
    preparedImageExportStatus,
    prepareImageExport: () => null,
    resetPreparedImageExport: () => undefined
  };
}

export async function copyElementAsImage(): Promise<never> {
  throw new Error("Image copy is unavailable in a portable artifact.");
}

export function imageCopySuccessMessage(nativeMessage: string): string {
  return nativeMessage;
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
  textarea.remove();
  return copied;
}

export async function copyTextToClipboard(text: string): Promise<void> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
  } catch {
    // Fall through to the selection-based fallback for file URLs and restrictive browsers.
  }
  if (!copyTextWithSelection(text)) throw new Error("Copy is blocked by this browser.");
}
