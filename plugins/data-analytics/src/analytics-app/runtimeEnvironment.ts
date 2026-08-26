type HostPromptResult = boolean | null;

type OpenAIHostBridge = {
  sendFollowUpMessage?: (payload: { prompt: string; title?: string }) => Promise<{ isError?: boolean }>;
  sendMessage?: (payload: {
    role: "user";
    content: Array<{ type: "text"; text: string }>;
  }) => Promise<{ isError?: boolean }>;
};

type CodexPromptPackageInfo = {
  originUrl?: unknown;
  root?: unknown;
} | null | undefined;

declare global {
  interface Window {
    openai?: OpenAIHostBridge;
  }
}

async function requestJson(path: string, init?: RequestInit): Promise<unknown> {
  const response = await fetch(path, { cache: "no-store", ...init });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const message = typeof payload?.error === "string"
      ? payload.error
      : `Request failed: ${response.status}`;
    throw new Error(message);
  }
  return payload;
}

async function requestOptionalJson(path: string, init?: RequestInit): Promise<unknown | null> {
  try {
    return await requestJson(path, init);
  } catch {
    return null;
  }
}

export async function loadArtifactFromApi() {
  const [manifest, snapshot, packageInfo] = await Promise.all([
    requestJson("/api/manifest"),
    requestJson("/api/snapshot"),
    requestOptionalJson("/api/package")
  ]);
  return { manifest, packageInfo, snapshot };
}

export async function loadHostedPresentation(): Promise<unknown | null> {
  return requestOptionalJson("/api/presentation");
}

export async function saveHostedPresentation(payload: unknown): Promise<unknown> {
  return requestJson("/api/presentation", {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function loadInlineChartWidgetHtml(widgetInstanceId: string): Promise<string> {
  const response = await fetch(
    `/api/inline-chart-widget?displayMode=modal&widgetInstanceId=${encodeURIComponent(widgetInstanceId)}`
  );
  if (!response.ok) {
    throw new Error(`Shared chart detail failed to load (${response.status}).`);
  }
  const html = await response.text();
  const serializedWidgetInstanceId = JSON.stringify(widgetInstanceId).replace(/</g, "\\u003c");
  const bridge = `<script>
window.openai = {
  ...(window.openai || {}),
  availableDisplayModes: ["modal"],
  displayMode: "modal",
  widgetInstanceId: ${serializedWidgetInstanceId},
  requestDisplayMode(request) {
    const mode = typeof request === "string" ? request : request && request.mode;
    window.parent.postMessage({ type: "datascience-chart-widget-display-mode", mode }, "*");
    return Promise.resolve({ mode });
  },
  sendFollowUpMessage(payload) {
    window.parent.postMessage(
      {
        originUrl: payload && payload.originUrl,
        prompt: payload && payload.prompt,
        type: "datascience-chart-widget-codex-prompt"
      },
      "*"
    );
    return Promise.resolve({ ok: true });
  },
  openCodexPrompt(payload) {
    return this.sendFollowUpMessage(payload);
  }
};
</script>`;
  return html.includes("</head>") ? html.replace("</head>", `${bridge}</head>`) : `${bridge}${html}`;
}

export async function loadSourceText(path: string, timeoutMs = 10_000): Promise<string | null> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`/api/source-file?path=${encodeURIComponent(path)}`, {
      cache: "no-store",
      headers: { Accept: "text/plain" },
      signal: controller.signal
    });
    const text = await response.text();
    if (!response.ok) {
      throw new Error(text || `Request failed: ${response.status}`);
    }
    return text;
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function sendPromptToHost(prompt: string, title?: string): Promise<HostPromptResult> {
  const hostApi = window.openai;
  if (typeof hostApi?.sendFollowUpMessage === "function") {
    try {
      const result = await hostApi.sendFollowUpMessage(title ? { prompt, title } : { prompt });
      return result?.isError !== true;
    } catch {
      return false;
    }
  }
  if (typeof hostApi?.sendMessage === "function") {
    try {
      const result = await hostApi.sendMessage({
        role: "user",
        content: [{ type: "text", text: prompt }]
      });
      return result?.isError !== true;
    } catch {
      return false;
    }
  }
  return null;
}

export function readPersistedValue(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writePersistedValue(key: string, value: string): void {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Persistence is best effort when browser storage is unavailable.
  }
}

function setOptionalCodexSearchParam(url: URL, name: string, value: unknown): void {
  if (typeof value !== "string" || !value.trim()) return;
  url.searchParams.set(name, value.trim());
}

function codexPromptUrl(prompt: string, packageInfo: CodexPromptPackageInfo): string {
  const url = new URL("codex://threads/new");
  setOptionalCodexSearchParam(url, "prompt", prompt);
  setOptionalCodexSearchParam(url, "originUrl", packageInfo?.originUrl);
  setOptionalCodexSearchParam(url, "path", packageInfo?.root);
  return url.toString();
}

function isLocalPreviewHost(): boolean {
  return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
}

export function launchCodexPromptFallback(
  prompt: string,
  packageInfo: CodexPromptPackageInfo,
): boolean {
  if (isLocalPreviewHost()) return false;
  const url = codexPromptUrl(prompt, packageInfo);
  let linkClicked = false;
  try {
    const link = document.createElement("a");
    link.href = url;
    link.target = "_top";
    link.rel = "noopener noreferrer";
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    link.remove();
    linkClicked = true;
  } catch {
    // Fall through to direct top-level navigation when it is available.
  }
  try {
    if (window.top === window) {
      window.location.assign(url);
      return true;
    }
  } catch {
    // Cross-origin frames can reject access to window.top.
  }
  return linkClicked;
}

export function sitePublishingInstructions(surface: string): string {
  return `Use the current Data Analytics artifact as the source of truth. Create or reuse a Site Creator project for this ${surface}, materialize a Cloudflare Worker-compatible app that serves the current manifest, bounded snapshot, package metadata, and inline-safe source text through /api/manifest, /api/snapshot, /api/package, and /api/source-file, then deploy it through Site Creator. Preserve the rendered layout, charts, tables, source details, and narrative. Default access to workspace_all unless I explicitly ask for narrower access, and report the production URL plus the access mode.`;
}
