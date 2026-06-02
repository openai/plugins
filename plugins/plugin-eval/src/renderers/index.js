import { renderHtml } from "./html.js";
import { renderMarkdown } from "./markdown.js";

export function renderPayload(payload, format) {
  if (format === "json") {
    return `${JSON.stringify(payload, null, 2)}\n`;
  }
  if (format === "markdown" || format === "md") {
    return `${renderMarkdown(payload)}\n`;
  }
  if (format === "html") {
    return renderHtml(payload);
  }
  throw new Error(`Unsupported format: ${format}`);
}
