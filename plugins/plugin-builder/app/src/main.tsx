import {
  AppWindow,
  ChevronLeft,
  ChevronRight,
  Copy,
  FileText,
  FolderClosed,
  Package2,
  Store,
  Upload,
  Workflow,
} from "lucide-react";
import {
  Fragment,
  type ReactElement,
  useEffect,
  useMemo,
  useState,
} from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type PluginSummary = {
  name?: string;
  displayName?: string;
  description?: string;
  viewUrl?: string | null;
  shareUrl?: string | null;
};

type SkillSummary = {
  id: string;
  title?: string;
  summary?: string;
  pathLabel?: string;
  frontmatterSummary?: string;
  headings?: string[];
  preview?: string;
};

type AppSummary = {
  id: string;
  title?: string;
  summary?: string;
  pathLabel?: string;
  appId?: string;
};

type McpSummary = {
  id: string;
  title?: string;
  summary?: string;
  pathLabel?: string;
  commandLabel?: string;
};

type MetaRow = {
  label?: string;
  value?: string;
};

type PluginBuilderModel = {
  plugin: PluginSummary;
  skills: SkillSummary[];
  apps: AppSummary[];
  mcpServers: McpSummary[];
  marketplaces: MetaRow[];
  localDetails: MetaRow[];
};

type DetailSelection =
  | { kind: "skill"; item: SkillSummary }
  | { kind: "app"; item: AppSummary }
  | { kind: "mcp"; item: McpSummary }
  | null;

type PendingRpc = {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
};

type HostMessage = {
  id?: number;
  jsonrpc?: string;
  result?: unknown;
  error?: { message?: string };
};

declare global {
  interface Window {
    openai?: {
      openExternal?: (payload: { href: string }) => void;
      toolOutput?: unknown;
      toolResponseMetadata?: unknown;
    };
  }
}

const fallbackModel: PluginBuilderModel = {
  plugin: {
    displayName: "Loading plugin",
    description: "Codex is preparing the local plugin summary.",
    viewUrl: null,
    shareUrl: null,
  },
  skills: [],
  apps: [],
  mcpServers: [],
  marketplaces: [],
  localDetails: [],
};

const pendingRpc = new Map<number, PendingRpc>();
let nextRpcId = 1;

function safeText(value: unknown, fallback = "Not provided"): string {
  if (value == null || value === "") {
    return fallback;
  }
  return String(value);
}

function decodePayload(raw: unknown): unknown {
  if (raw == null) {
    return null;
  }
  if (typeof raw === "string") {
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }
  return raw;
}

function modelFromPayload(raw: unknown): PluginBuilderModel | null {
  const payload = decodePayload(raw);
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const record = payload as Record<string, unknown>;
  if (
    record.plugin &&
    Array.isArray(record.skills) &&
    Array.isArray(record.apps) &&
    Array.isArray(record.mcpServers)
  ) {
    return record as PluginBuilderModel;
  }

  if ("structuredContent" in record) {
    return modelFromPayload(record.structuredContent);
  }

  if (Array.isArray(record.content)) {
    for (const item of record.content) {
      if (item && typeof item === "object" && "text" in item) {
        const nested = modelFromPayload((item as { text?: unknown }).text);
        if (nested) {
          return nested;
        }
      }
      const nested = modelFromPayload(item);
      if (nested) {
        return nested;
      }
    }
  }

  return null;
}

function readModel(): PluginBuilderModel {
  return (
    modelFromPayload(window.openai?.toolOutput) ??
    modelFromPayload(window.openai?.toolResponseMetadata) ??
    fallbackModel
  );
}

function sendMcpAppMessage(message: unknown): void {
  if (window.parent === window) {
    return;
  }
  window.parent.postMessage(message, "*");
}

function requestMcpApp(method: string, params: unknown): Promise<unknown> {
  const id = nextRpcId;
  nextRpcId += 1;

  const request = new Promise<unknown>((resolve, reject) => {
    pendingRpc.set(id, { reject, resolve });
    window.setTimeout(() => {
      const pending = pendingRpc.get(id);
      if (!pending) {
        return;
      }
      pendingRpc.delete(id);
      reject(new Error(`${method} timed out.`));
    }, 5000);
  });

  sendMcpAppMessage({
    id,
    jsonrpc: "2.0",
    method,
    params,
  });

  return request;
}

function notifyMcpApp(method: string, params: unknown = {}): void {
  sendMcpAppMessage({
    jsonrpc: "2.0",
    method,
    params,
  });
}

async function connectMcpApp(): Promise<void> {
  try {
    await requestMcpApp("ui/initialize", {
      appCapabilities: {
        availableDisplayModes: ["inline", "fullscreen"],
      },
      appInfo: {
        name: "Plugin Builder",
        version: "0.1.0",
      },
      protocolVersion: "2026-01-26",
    });
    notifyMcpApp("ui/notifications/initialized");
    await requestMcpApp("ui/request-display-mode", {
      mode: "fullscreen",
    });
  } catch {
    // The summary remains useful even when the host keeps the app inline.
  }
}

function openCodexLink(href?: string | null): void {
  if (!href) {
    return;
  }
  window.openai?.openExternal?.({ href });
}

async function copyValue(value: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    // The value remains visible and selectable if clipboard access is unavailable.
  }
}

function RowIcon({ kind }: { kind: "skill" | "app" | "mcp" }): ReactElement {
  if (kind === "skill") {
    return <FileText aria-hidden="true" className="h-4 w-4" />;
  }
  if (kind === "app") {
    return <AppWindow aria-hidden="true" className="h-4 w-4" />;
  }
  return <Workflow aria-hidden="true" className="h-4 w-4" />;
}

function SectionHeading({ children }: { children: string }): ReactElement {
  return <h2 className="text-[15px] font-medium text-ink">{children}</h2>;
}

function ResourceSection({
  title,
  kind,
  items,
  onOpen,
}: {
  title: string;
  kind: "skill" | "app" | "mcp";
  items: Array<SkillSummary | AppSummary | McpSummary>;
  onOpen: (selection: DetailSelection) => void;
}): ReactElement | null {
  if (items.length === 0) {
    return null;
  }

  return (
    <section className="space-y-3">
      <SectionHeading>{title}</SectionHeading>
      <div className="divide-y divide-line border-t border-line">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            className="resource-row relative grid min-h-[62px] w-full grid-cols-[20px_minmax(0,1fr)_18px] items-center gap-4 py-3 text-left"
            onClick={() => {
              if (kind === "skill") {
                onOpen({ kind, item: item as SkillSummary });
                return;
              }
              if (kind === "app") {
                onOpen({ kind, item: item as AppSummary });
                return;
              }
              onOpen({ kind, item: item as McpSummary });
            }}
          >
            <span className="text-ink">
              <RowIcon kind={kind} />
            </span>
            <span className="grid min-w-0 gap-1">
              <span className="truncate text-[14px] font-medium text-ink">
                {safeText(item.title, safeText(item.id))}
              </span>
              <span className="line-clamp-2 text-[14px] leading-5 text-muted">
                {safeText(item.summary)}
              </span>
            </span>
            <ChevronRight aria-hidden="true" className="h-4 w-4 text-faint" />
          </button>
        ))}
      </div>
    </section>
  );
}

function MetadataSection({
  title,
  rows,
  icon,
}: {
  title: string;
  rows: MetaRow[];
  icon: ReactElement;
}): ReactElement | null {
  if (rows.length === 0) {
    return null;
  }

  return (
    <section className="space-y-3">
      <SectionHeading>{title}</SectionHeading>
      <div className="divide-y divide-line border-t border-line">
        {rows.map((row) => {
          const value = safeText(row.value);
          return (
            <div
              key={`${safeText(row.label)}-${value}`}
              className="grid min-h-[62px] grid-cols-[20px_minmax(0,1fr)_28px] items-center gap-4 py-3"
            >
              <span className="text-ink">{icon}</span>
              <span className="grid min-w-0 gap-1">
                <span className="text-[14px] font-medium text-ink">
                  {safeText(row.label)}
                </span>
                <span className="break-all font-mono text-[13px] leading-5 text-muted">
                  {value}
                </span>
              </span>
              <button
                type="button"
                className="grid h-7 w-7 place-items-center rounded-md text-muted transition hover:bg-control hover:text-ink"
                aria-label={`Copy ${safeText(row.label)}`}
                title="Copy"
                onClick={() => {
                  copyValue(value);
                }}
              >
                <Copy aria-hidden="true" className="h-4 w-4" />
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function DetailBlock({
  title,
  children,
}: {
  title: string;
  children: ReactElement;
}): ReactElement {
  return (
    <section className="space-y-2 border-t border-line py-4">
      <h3 className="text-[13px] font-medium uppercase tracking-[0.06em] text-faint">
        {title}
      </h3>
      {children}
    </section>
  );
}

function SummaryScreen({
  model,
  onOpenDetail,
}: {
  model: PluginBuilderModel;
  onOpenDetail: (selection: DetailSelection) => void;
}): ReactElement {
  return (
    <main className="min-h-screen bg-canvas px-7 py-6 text-ink">
      <header className="flex flex-col gap-5 border-b border-line pb-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 items-start gap-4">
          <div className="grid h-16 w-16 shrink-0 place-items-center rounded-lg border border-line bg-panel shadow-hairline">
            <Package2 aria-hidden="true" className="h-8 w-8" />
          </div>
          <div className="min-w-0 pt-1">
            <h1 className="text-balance text-[28px] font-semibold leading-8 text-ink">
              {safeText(model.plugin.displayName, "Loading plugin")}
            </h1>
            <p className="mt-2 max-w-[620px] text-[15px] leading-6 text-muted">
              {safeText(model.plugin.description)}
            </p>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <button
            type="button"
            className="inline-flex h-11 items-center justify-center rounded-md border border-line-strong bg-panel px-4 text-[14px] font-medium text-ink transition hover:bg-control disabled:cursor-not-allowed disabled:opacity-45"
            disabled={!model.plugin.viewUrl}
            onClick={() => openCodexLink(model.plugin.viewUrl)}
          >
            View in Codex
          </button>
          <button
            type="button"
            className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ink px-4 text-[14px] font-medium text-canvas transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-45"
            disabled={!model.plugin.shareUrl}
            onClick={() => openCodexLink(model.plugin.shareUrl)}
          >
            <Upload aria-hidden="true" className="h-4 w-4" />
            Share in Codex
          </button>
        </div>
      </header>

      <div className="mt-6 grid gap-6">
        <ResourceSection
          title="Skills"
          kind="skill"
          items={model.skills}
          onOpen={onOpenDetail}
        />
        <ResourceSection
          title="Apps"
          kind="app"
          items={model.apps}
          onOpen={onOpenDetail}
        />
        <ResourceSection
          title="MCP servers"
          kind="mcp"
          items={model.mcpServers}
          onOpen={onOpenDetail}
        />
        <MetadataSection
          title="Marketplaces"
          rows={model.marketplaces}
          icon={<Store aria-hidden="true" className="h-4 w-4" />}
        />
        <MetadataSection
          title="Local details"
          rows={model.localDetails}
          icon={<FolderClosed aria-hidden="true" className="h-4 w-4" />}
        />
      </div>
    </main>
  );
}

function DetailScreen({
  detail,
  onBack,
}: {
  detail: Exclude<DetailSelection, null>;
  onBack: () => void;
}): ReactElement {
  const title = safeText(detail.item.title, detail.item.id);
  const summary = safeText(detail.item.summary);

  return (
    <main className="min-h-screen bg-canvas px-7 py-6 text-ink">
      <button
        type="button"
        className="mb-6 inline-flex items-center gap-2 text-[14px] font-medium text-muted transition hover:text-ink"
        onClick={onBack}
      >
        <ChevronLeft aria-hidden="true" className="h-4 w-4" />
        Back to plugin summary
      </button>

      <header className="border-b border-line pb-6">
        <div className="mb-3 text-[13px] font-medium uppercase tracking-[0.06em] text-faint">
          {detail.kind === "skill"
            ? "Skill"
            : detail.kind === "app"
              ? "App"
              : "MCP server"}
        </div>
        <div className="flex items-start gap-4">
          <div className="grid h-12 w-12 shrink-0 place-items-center rounded-lg border border-line bg-panel shadow-hairline">
            <RowIcon kind={detail.kind} />
          </div>
          <div className="min-w-0">
            <h1 className="text-[26px] font-semibold leading-8 text-ink">{title}</h1>
            <p className="mt-2 max-w-[720px] text-[15px] leading-6 text-muted">
              {summary}
            </p>
          </div>
        </div>
      </header>

      {detail.kind === "skill" ? (
        <div className="mt-1">
          <DetailBlock title="Summary">
            <p className="max-w-[760px] text-[15px] leading-6 text-muted">
              {safeText(detail.item.frontmatterSummary)}
            </p>
          </DetailBlock>
          <DetailBlock title="Sections">
            {detail.item.headings && detail.item.headings.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {detail.item.headings.map((heading) => (
                  <span
                    key={heading}
                    className="rounded-full border border-line bg-panel px-3 py-1 text-[13px] text-muted"
                  >
                    {heading}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[15px] leading-6 text-muted">
                No section headings were found in this skill.
              </p>
            )}
          </DetailBlock>
          <DetailBlock title="Preview">
            <p className="max-w-[760px] text-[15px] leading-6 text-muted">
              {safeText(detail.item.preview)}
            </p>
          </DetailBlock>
          <DetailBlock title="Source">
            <code className="block max-w-[760px] break-all rounded-md bg-control px-3 py-2 font-mono text-[13px] text-muted">
              {safeText(detail.item.pathLabel)}
            </code>
          </DetailBlock>
        </div>
      ) : detail.kind === "app" ? (
        <div className="mt-1">
          <DetailBlock title="Definition">
            <code className="block max-w-[760px] break-all rounded-md bg-control px-3 py-2 font-mono text-[13px] text-muted">
              {safeText(detail.item.pathLabel)}
            </code>
          </DetailBlock>
          <DetailBlock title="App id">
            <p className="text-[15px] leading-6 text-muted">{safeText(detail.item.appId)}</p>
          </DetailBlock>
        </div>
      ) : (
        <div className="mt-1">
          <DetailBlock title="Definition">
            <code className="block max-w-[760px] break-all rounded-md bg-control px-3 py-2 font-mono text-[13px] text-muted">
              {safeText(detail.item.pathLabel)}
            </code>
          </DetailBlock>
          <DetailBlock title="Command">
            <code className="block max-w-[760px] break-all rounded-md bg-control px-3 py-2 font-mono text-[13px] text-muted">
              {safeText(detail.item.commandLabel)}
            </code>
          </DetailBlock>
        </div>
      )}
    </main>
  );
}

function PluginBuilderApp(): ReactElement {
  const [model, setModel] = useState<PluginBuilderModel>(() => readModel());
  const [detail, setDetail] = useState<DetailSelection>(null);

  useEffect(() => {
    connectMcpApp();

    const syncModel = (): void => {
      setModel(readModel());
    };
    const handleMessage = (event: MessageEvent<HostMessage>): void => {
      const message = event.data;
      if (
        !message ||
        message.jsonrpc !== "2.0" ||
        message.id == null ||
        !pendingRpc.has(message.id) ||
        (!("result" in message) && !("error" in message))
      ) {
        return;
      }

      const pending = pendingRpc.get(message.id);
      pendingRpc.delete(message.id);
      if (!pending) {
        return;
      }
      if (message.error) {
        pending.reject(new Error(message.error.message || "MCP app request failed."));
        return;
      }
      pending.resolve(message.result);
    };

    window.addEventListener("message", handleMessage);
    window.addEventListener("openai:set_globals", syncModel);
    return () => {
      window.removeEventListener("message", handleMessage);
      window.removeEventListener("openai:set_globals", syncModel);
    };
  }, []);

  const selectedDetail = useMemo(() => {
    if (!detail) {
      return null;
    }
    const source =
      detail.kind === "skill"
        ? model.skills
        : detail.kind === "app"
          ? model.apps
          : model.mcpServers;
    const nextItem = source.find((item) => item.id === detail.item.id);
    if (!nextItem) {
      return null;
    }
    return { kind: detail.kind, item: nextItem } as Exclude<DetailSelection, null>;
  }, [detail, model.apps, model.mcpServers, model.skills]);

  return selectedDetail ? (
    <DetailScreen detail={selectedDetail} onBack={() => setDetail(null)} />
  ) : (
    <SummaryScreen model={model} onOpenDetail={setDetail} />
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(
  <Fragment>
    <PluginBuilderApp />
  </Fragment>,
);
