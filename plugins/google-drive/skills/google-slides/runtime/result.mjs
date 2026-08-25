import { isRecord, redactSensitive } from "./common.mjs";

export class ToolCallError extends Error {
  constructor(message, { raw = null } = {}) {
    super(redactSensitive(message));
    this.name = "ToolCallError";
    this.raw = redactSensitive(raw);
  }
}

export function extractToolText(raw) {
  if (typeof raw === "string") return raw;
  if (!raw) return "Unknown connector error";

  if (Array.isArray(raw.content)) {
    const text = raw.content
      .filter((item) => item?.type === "text" && typeof item.text === "string")
      .map((item) => item.text)
      .join("\n")
      .trim();
    if (text) return text;
  }

  for (const key of ["message", "error", "detail"]) {
    if (typeof raw[key] === "string" && raw[key]) return raw[key];
    if (isRecord(raw[key]) && typeof raw[key].message === "string") return raw[key].message;
  }
  return "Connector returned an error result";
}

function parseJsonText(text) {
  try {
    return JSON.parse(text);
  } catch {
    return { text };
  }
}

function returnOrThrow(value, raw) {
  if (value?.isError === true) {
    throw new ToolCallError(extractToolText(value), { raw });
  }
  return value;
}

export function unwrapCallToolResult(raw) {
  if (raw?.isError === true) {
    throw new ToolCallError(extractToolText(raw), { raw });
  }

  if (raw?.structuredContent?.result !== undefined) return returnOrThrow(raw.structuredContent.result, raw);
  if (raw?.structuredContent !== undefined) return returnOrThrow(raw.structuredContent, raw);

  const textItem = Array.isArray(raw?.content)
    ? raw.content.find((item) => item?.type === "text" && typeof item.text === "string")
    : null;
  if (textItem) {
    const parsed = parseJsonText(textItem.text);
    if (parsed?.isError === true) {
      throw new ToolCallError(extractToolText(parsed), { raw });
    }
    if (parsed?.structuredContent?.result !== undefined) return returnOrThrow(parsed.structuredContent.result, raw);
    if (parsed?.structuredContent !== undefined) return returnOrThrow(parsed.structuredContent, raw);
    return returnOrThrow(parsed, raw);
  }

  return returnOrThrow(raw, raw);
}
