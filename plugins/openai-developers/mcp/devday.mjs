import { readFileSync } from "node:fs";

export const DEVDAY_URI = "ui://openai-developers/devday";
export const DEVDAY_TOOL = {
  name: "open_devday_agenda",
  title: "DevDay agenda",
  description: "Open the DevDay agenda beside this conversation. First verify the public program on devday.openai.com, then pass only published event facts. An empty call opens an empty view; it does not fetch or invent a schedule.",
  inputSchema: {
    type: "object", additionalProperties: false,
    properties: {
      agenda: {
        type: "object", additionalProperties: false,
        required: ["date", "timezone", "location", "checked_on", "source_url", "events"],
        properties: {
          date: { type: "string", format: "date" },
          timezone: { type: "string", description: "Published IANA event timezone." },
          location: { type: "string", maxLength: 150 },
          checked_on: { type: "string", format: "date" },
          source_url: { type: "string", description: "Public official HTTPS source, without credentials or query parameters." },
          note: { type: "string", maxLength: 600 },
          events: {
            type: "array", minItems: 1, maxItems: 60,
            items: {
              type: "object", additionalProperties: false,
              required: ["id", "title", "start"],
              properties: {
                id: { type: "string", maxLength: 100 },
                title: { type: "string", maxLength: 180 },
                start: { type: "string", format: "date-time" },
                end: { type: ["string", "null"], description: "Published end with UTC offset; null when unknown." },
                detail: { type: "string", maxLength: 600 },
                selected: { type: "boolean" },
              },
            },
          },
        },
      },
    },
  },
  annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  _meta: {
    ui: { resourceUri: DEVDAY_URI, visibility: ["model", "app"] },
    "openai/ui": { entrypoints: [{ type: "thread" }], preferredModelDisplayMode: "fullscreen" },
  },
};

function fields(value, allowed) {
  if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).some(key => !allowed.includes(key))) {
    throw new Error("Unexpected agenda fields. Include only the published program.");
  }
}
function text(value, name, limit = 600) {
  if (typeof value !== "string" || !value.trim() || value.length > limit) throw new Error(`Invalid ${name}.`);
}
function day(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0, 10) !== value) throw new Error("Invalid date.");
}
function instant(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) throw new Error("Times must include a UTC offset.");
  day(value.slice(0, 10));
  return Date.parse(value);
}
export function openDevDay(args = {}) {
  fields(args, ["agenda"]);
  const agenda = args.agenda;
  if (agenda !== undefined) {
    fields(agenda, ["date", "timezone", "location", "checked_on", "source_url", "note", "events"]);
    day(agenda.date); day(agenda.checked_on);
    text(agenda.timezone, "timezone", 100); text(agenda.location, "location", 150);
    const localDay = new Intl.DateTimeFormat("en-CA", { timeZone: agenda.timezone, year: "numeric", month: "2-digit", day: "2-digit" });
    const source = new URL(agenda.source_url);
    if (source.protocol !== "https:" || !["devday.openai.com", "events.openai.com", "openai.com", "www.openai.com"].includes(source.hostname) || source.username || source.password || source.port || source.search) throw new Error("Use a public official HTTPS source without query parameters.");
    if (agenda.note !== undefined) text(agenda.note, "note");
    if (!Array.isArray(agenda.events) || agenda.events.length < 1 || agenda.events.length > 60) throw new Error("Provide 1 to 60 published activities.");
    const ids = new Set();
    for (const event of agenda.events) {
      fields(event, ["id", "title", "start", "end", "detail", "selected"]);
      text(event.id, "id", 100); text(event.title, "title", 180);
      if (ids.has(event.id)) throw new Error("Activity IDs must be unique.");
      ids.add(event.id);
      const start = instant(event.start);
      if (localDay.format(start) !== agenda.date) throw new Error("Activity falls outside the event date in its timezone.");
      if (event.end != null && instant(event.end) <= start) throw new Error("End must follow start; use null if unpublished.");
      if (event.detail !== undefined) text(event.detail, "detail");
      if (event.selected !== undefined && typeof event.selected !== "boolean") throw new Error("selected must be a boolean.");
    }
  }
  return {
    content: [{ type: "text", text: agenda ? `DevDay agenda: ${agenda.date}, ${agenda.timezone}. Public source checked ${agenda.checked_on}: ${agenda.source_url}. The attendee can select activities and attach their plan to chat. No reservations are made.` : "Ask me to check the public DevDay schedule to fill this agenda." }],
    structuredContent: { agenda: agenda ?? null },
  };
}

export function devdayResource() {
  const template = readFileSync(new URL("../skills/devday-guide/assets/agenda.html", import.meta.url), "utf8");
  const bridge = readFileSync(new URL("./devday-client.js", import.meta.url), "utf8");
  const defaults = {
    YEAR: "2026", DATE: "Public event guide", ISO_DATE: "", ZONE: "UTC", ZONE_LABEL: "event time",
    LOCATION: "", STATUS: "Plan your DevDay", CHECKED: "not loaded", SOURCE: "https://devday.openai.com/", ROWS: "",
    NOTE: "Ask me to check the public DevDay schedule to fill this agenda.",
  };
  const html = template.replace(/@@([A-Z_]+)@@/g, (_, key) => defaults[key]).replace("</body>", () => `<script>${bridge}</script></body>`);
  return { contents: [{ uri: DEVDAY_URI, mimeType: "text/html;profile=mcp-app", text: html, _meta: {
    ui: { csp: { connectDomains: [], resourceDomains: [] } },
    "openai/ui": { preferredDisplayMode: "fullscreen" },
  } }] };
}
