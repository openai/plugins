const TOOL_NAME = "creative_production_board";
const MAX_DIAGNOSTIC_EVENTS = 100;
const VIEW_CACHE_DATABASE = "creative-production-board-view-cache-v1";
const VIEW_CACHE_STORE = "boards";
const cropPositions = ["50% 50%", "38% 50%", "62% 50%", "50% 36%", "50% 64%", "28% 42%", "72% 58%", "42% 34%", "58% 68%"];
const aspectRatios = ["0.78 / 1", "1 / 1.24", "1 / 0.74", "0.88 / 1", "1 / 1.38", "1 / 0.92", "0.72 / 1"];

const elements = {
  root: document.querySelector(".app"),
  title: document.getElementById("boardTitle"),
  summary: document.getElementById("boardSummary"),
  feed: document.getElementById("feed"),
  status: document.getElementById("feedStatus"),
  template: document.getElementById("cardTemplate"),
  selectionToolbar: document.getElementById("selectionActionToolbar"),
  selectionAttach: document.getElementById("selectionAttach"),
  selectionDelete: document.getElementById("selectionDelete"),
  clearSelection: document.getElementById("clearSelection"),
  exportActions: document.getElementById("exportActions"),
  exportPrimary: document.getElementById("exportPrimary"),
  exportMenuTrigger: document.getElementById("exportMenuTrigger"),
  exportMenu: document.getElementById("exportMenu"),
  viewer: document.getElementById("viewer"),
  viewerImage: document.getElementById("viewerImage"),
  viewerClose: document.getElementById("viewerClose"),
  viewerPrev: document.getElementById("viewerPrev"),
  viewerNext: document.getElementById("viewerNext"),
  attachImage: document.getElementById("attachImage"),
  remixImage: document.getElementById("remixImage"),
  remixPanel: document.getElementById("viewerRemixPanel"),
  remixTabs: document.getElementById("remixSlotTabs"),
  remixOptions: document.getElementById("remixOptionList"),
  remixStatus: document.getElementById("remixStatus"),
  viewerExportActions: document.getElementById("viewerExportActions"),
  viewerExportPrimary: document.getElementById("viewerExportPrimary"),
  viewerExportMenuTrigger: document.getElementById("viewerExportMenuTrigger"),
  viewerExportMenu: document.getElementById("viewerExportMenu"),
  debugPanel: document.getElementById("debugPanel"),
  debugSummary: document.getElementById("debugSummary"),
  debugFacts: document.getElementById("debugFacts"),
  debugEvents: document.getElementById("debugEvents"),
};

const state = {
  board: null,
  previews: new Map(),
  diagnostics: [],
  pendingTrace: [],
  diagnosticOrigins: new Set(["widget", "server", "host"]),
  pendingDeleteMutations: new Map(),
  pendingDeleteIds: new Set(),
  pendingDeleteDispatches: new Set(),
  pendingDeleteRetryTimer: 0,
  uiEpoch: 0,
  uiCommittedEpoch: 0,
  uiSaveTimer: 0,
  traceTimer: 0,
  generationWatchTimer: 0,
  generationWatchDeadline: 0,
  generationWatchSawActive: false,
  visibleSyncTimer: 0,
  visibleSyncFailed: false,
  viewCacheTimer: 0,
  viewCacheFailed: false,
  viewCacheReady: false,
  viewCacheRestoring: false,
  refreshPromise: null,
  foregroundBridgeQueue: [],
  backgroundBridgeQueue: [],
  bridgeQueueActive: false,
  annotationQueue: Promise.resolve(),
  viewerItemId: null,
  activeAnnotationComposer: null,
  remixSlot: "style",
  remixSelections: {},
  starterView: null,
  lastError: "",
  lastIgnoredSnapshotKey: "",
  traceFlushFailed: false,
};

const REMIX_SLOTS = [
  { id: "style", label: "Style", promptHint: "Apply a different visual treatment while preserving the selected image's intent." },
  { id: "palette", label: "Colors", promptHint: "Shift palette and materials without changing the image's core composition." },
  { id: "scene", label: "Location", promptHint: "Move the image into a new scene while preserving the selected subject." },
  { id: "props", label: "Props", promptHint: "Change supporting context only; keep the image's main subject intact." },
  { id: "character", label: "Character", promptHint: "Change the visible person or persona while preserving the overall mood." },
  { id: "format", label: "Format", promptHint: "Adapt the image to another crop or channel while preserving the key visual." },
];

const REMIX_OPTION_LIBRARY = {
  style: [
    { id: "editorial", lead: "Editorial", description: "Cleaner light and hierarchy with a more polished campaign finish.", promptHint: "Apply a polished editorial treatment" },
    { id: "candid", lead: "Candid", description: "More natural texture and believable lived-in detail.", promptHint: "Shift the image toward documentary realism" },
    { id: "dramatic", lead: "Dramatic", description: "Richer blacks, sharper highlights, and more cinematic emphasis.", promptHint: "Apply a high-contrast cinematic treatment" },
    { id: "material", lead: "Material", description: "A closer tactile read of surface, temperature, and finish.", promptHint: "Rebuild the image as a tactile material study with a visibly different crop" },
    { id: "motion", lead: "Motion", description: "More kinetic gesture, blur, or environmental energy.", promptHint: "Introduce controlled motion" },
    { id: "minimal", lead: "Minimal", description: "Quieter hierarchy, more negative space, and stricter restraint.", promptHint: "Strip the image down to a minimal premium frame" },
  ],
  palette: [
    { id: "warm", lead: "Warm", description: "Warmer neutrals and tactile highlights.", promptHint: "Shift the palette warmer" },
    { id: "cool", lead: "Cool", description: "Crisper whites, cooler shadows, and restrained technical contrast.", promptHint: "Use cooler minimal accents" },
    { id: "accent", lead: "Accent", description: "A stronger accent color against quieter supporting surfaces.", promptHint: "Add a controlled accent palette" },
    { id: "monochrome", lead: "Monochrome", description: "A narrower tonal treatment that lets one key cue stand out.", promptHint: "Reduce the palette to tonal restraint plus one preserved cue" },
    { id: "unexpected", lead: "Unexpected", description: "A surprising secondary color relationship that still belongs.", promptHint: "Introduce one unexpected supporting color" },
  ],
  scene: [
    { id: "studio", suffix: "Studio", description: "A cleaner controlled setting that keeps the subject dominant.", promptHint: "Move the image into a cleaner studio-hero setting" },
    { id: "in-use", suffix: "In Use", description: "A more believable real-world context.", promptHint: "Place the subject into a realistic usage context" },
    { id: "detail", suffix: "Detail", description: "A tighter scene focused on material, craft, or product detail.", promptHint: "Create a close-detail scene" },
    { id: "exterior", suffix: "Exterior", description: "An outdoor or threshold environment with a fresh spatial read.", promptHint: "Relocate the subject into an exterior or entryway scene" },
    { id: "backstage", suffix: "Backstage", description: "A behind-the-scenes environment with more process and atmosphere.", promptHint: "Reframe the subject as a backstage or preparation moment" },
  ],
  props: [
    { id: "minimal-support", label: "Minimal Support", description: "Reduce surrounding objects so the subject carries more weight.", promptHint: "Remove nonessential props" },
    { id: "contextual-cues", suffix: "Cues", description: "Add restrained supporting objects that clarify place or use.", promptHint: "Add a few contextual props" },
    { id: "premium-finish", label: "Premium Finish", description: "Sharper materials, cleaner surfaces, and more elevated detail.", promptHint: "Add premium material cues" },
    { id: "unexpected-prop", lead: "Unexpected", suffix: "Prop", description: "One surprising but believable object that opens a new story.", promptHint: "Add one unexpected supporting prop" },
    { id: "process-cues", label: "Process Cues", description: "Tools, traces, or handling details that make the scene feel active.", promptHint: "Add restrained process cues" },
  ],
  character: [
    { id: "expert", label: "Expert Hands", description: "More credible craft, authority, and purposeful interaction.", promptHint: "Introduce an expert operator interacting naturally with the subject" },
    { id: "everyday", label: "Everyday Use", description: "A more approachable human presence while preserving the mood.", promptHint: "Show the subject in an everyday user context" },
    { id: "no-human", label: "No Human", description: "Let the object, place, or composition carry the frame.", promptHint: "Remove visible people and let the subject carry the image" },
    { id: "passing", label: "Passing Figure", description: "A partial human presence that adds scale and motion.", promptHint: "Add a cropped passing figure or gesture" },
    { id: "collector", label: "Collector Persona", description: "A more intentional, taste-driven persona interacting with the subject.", promptHint: "Introduce a collector or tastemaker presence" },
  ],
  format: [
    { id: "portrait", lead: "Portrait", description: "A tighter vertical crop for social or story placement.", promptHint: "Adapt the image to a portrait social crop" },
    { id: "wide", lead: "Wide", description: "A broader horizontal composition for a landing page or banner.", promptHint: "Adapt the image to a wide hero composition" },
    { id: "crop", suffix: "Crop", description: "A closer inspection of the material, surface, or focal subject.", promptHint: "Create a closer detail crop" },
    { id: "square", lead: "Square", description: "A balanced square crop for gallery or feed review.", promptHint: "Recompose the image as a square frame with a changed focal balance" },
    { id: "split-depth", lead: "Split-Depth", description: "Foreground detail and background atmosphere in one frame.", promptHint: "Create a single-frame split-depth composition" },
  ],
};

function diagnostic(event, details = {}, outcome = "success", { persist = true } = {}) {
  const record = {
    event,
    details: sanitizeDetails(details),
    outcome,
    surface: "widget",
    timestamp: new Date().toISOString(),
    revision: state.board?.revision,
  };
  state.diagnostics.push(record);
  state.diagnostics = state.diagnostics.slice(-MAX_DIAGNOSTIC_EVENTS);
  if (persist) {
    state.pendingTrace.push(record);
    state.pendingTrace = state.pendingTrace.slice(-MAX_DIAGNOSTIC_EVENTS);
  }
  renderDiagnostics();
  if (persist) scheduleTraceFlush();
}

function sanitizeDetails(details) {
  return Object.fromEntries(Object.entries(details || {}).filter(([key]) => !/prompt|image|content|path|token|secret/i.test(key)));
}

function restorePendingDeleteOutbox(mutations) {
  for (const mutation of mutations || []) {
    if (!mutation?.mutationId || !Array.isArray(mutation.itemIds)) continue;
    state.pendingDeleteMutations.set(mutation.mutationId, mutation);
    mutation.itemIds.forEach((itemId) => state.pendingDeleteIds.add(itemId));
  }
}

let viewCacheDatabasePromise;

function openViewCacheDatabase() {
  if (!("indexedDB" in window)) return Promise.resolve(null);
  if (viewCacheDatabasePromise) return viewCacheDatabasePromise;
  viewCacheDatabasePromise = new Promise((resolve, reject) => {
    const request = window.indexedDB.open(VIEW_CACHE_DATABASE, 1);
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains(VIEW_CACHE_STORE)) {
        request.result.createObjectStore(VIEW_CACHE_STORE, { keyPath: "boardId" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("Could not open board view cache"));
  });
  return viewCacheDatabasePromise;
}

async function readViewCache(boardId) {
  const database = await openViewCacheDatabase();
  if (!database) return null;
  return new Promise((resolve, reject) => {
    const request = database.transaction(VIEW_CACHE_STORE, "readonly").objectStore(VIEW_CACHE_STORE).get(boardId);
    request.onsuccess = () => resolve(request.result || null);
    request.onerror = () => reject(request.error || new Error("Could not read board view cache"));
  });
}

async function writeViewCache(record) {
  const database = await openViewCacheDatabase();
  if (!database) return;
  await new Promise((resolve, reject) => {
    const transaction = database.transaction(VIEW_CACHE_STORE, "readwrite");
    transaction.objectStore(VIEW_CACHE_STORE).put(record);
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error || new Error("Could not write board view cache"));
    transaction.onabort = () => reject(transaction.error || new Error("Board view cache write was aborted"));
  });
}

function scheduleViewCacheWrite() {
  if (!state.viewCacheReady || !state.board?.boardId || state.viewCacheTimer) return;
  state.viewCacheTimer = window.setTimeout(() => {
    state.viewCacheTimer = 0;
    void persistViewCache();
  }, 80);
}

async function persistViewCache() {
  if (!state.board?.boardId) return;
  try {
    await writeViewCache({
      boardId: state.board.boardId,
      board: structuredClone(state.board),
      previews: [...state.previews.entries()],
      pendingDeleteMutations: [...state.pendingDeleteMutations.values()].slice(-100),
      savedAt: new Date().toISOString(),
    });
    state.viewCacheFailed = false;
  } catch {
    if (!state.viewCacheFailed) {
      state.viewCacheFailed = true;
      diagnostic("board.cache.write_failed", {}, "failure", { persist: false });
    }
  }
}

async function restoreViewCache() {
  if (!state.board?.boardId) return false;
  try {
    const cached = await readViewCache(state.board.boardId);
    if (!cached) {
      applyPendingDeleteOverlay(state.board);
      renderBoard();
      void replayPendingDeletes();
      return false;
    }
    restorePendingDeleteOutbox(cached.pendingDeleteMutations);
    if (!cached.board || cached.board.revision < state.board.revision) {
      applyPendingDeleteOverlay(state.board);
      renderBoard();
      void replayPendingDeletes();
      return false;
    }
    for (const [itemId, source] of cached.previews || []) state.previews.set(itemId, source);
    applyBoard(cached.board, [], { quiet: true, authoritative: true });
    diagnostic("board.cache.restored", { revision: cached.board.revision }, "success", { persist: false });
    void replayPendingDeletes();
    return true;
  } catch {
    diagnostic("board.cache.read_failed", {}, "failure", { persist: false });
    return false;
  } finally {
    state.viewCacheReady = true;
    scheduleViewCacheWrite();
  }
}

function scheduleTraceFlush() {
  if (!state.board?.boardId || state.traceTimer) return;
  state.traceTimer = window.setTimeout(() => {
    state.traceTimer = 0;
    void flushTrace();
  }, 500);
}

async function flushTrace() {
  if (!state.board?.boardId || !state.pendingTrace.length) return;
  const events = state.pendingTrace.splice(0, MAX_DIAGNOSTIC_EVENTS);
  try {
    await enqueueAction(
      "append_log",
      () => rawToolCall({ action: "append_log", boardId: state.board.boardId, traceEvents: events }),
      { priority: "background", trace: false },
    );
    state.traceFlushFailed = false;
  } catch (error) {
    state.pendingTrace.unshift(...events.slice(-40));
    if (!state.traceFlushFailed) {
      diagnostic("trace.flush.failed", { action: "append_log", errorCode: "append_log_failed" }, "failure", { persist: false });
    }
    state.traceFlushFailed = true;
  }
}

function renderDiagnostics() {
  if (!elements.debugPanel || !elements.debugSummary || !elements.debugFacts || !elements.debugEvents) return;
  const board = state.board;
  const latest = state.diagnostics.at(-1);
  const visibleDiagnostics = state.diagnostics.filter((entry) => state.diagnosticOrigins.has(diagnosticOrigin(entry)));
  elements.debugSummary.textContent = state.lastError || latest?.event || (board ? "Ready" : "Waiting for board");
  elements.debugFacts.replaceChildren();
  for (const value of [
    `board=${board?.boardId || "unknown"}`,
    `revision=${board?.revision ?? "unknown"}`,
    `widget=${window.openai?.widgetInstanceId || "unknown"}`,
    `pendingLogs=${state.pendingTrace.length}`,
    `visibleLogs=${visibleDiagnostics.length}/${state.diagnostics.length}`,
  ]) {
    const span = document.createElement("span");
    span.textContent = value;
    elements.debugFacts.append(span);
  }
  elements.debugEvents.replaceChildren(...visibleDiagnostics.slice().reverse().map((entry) => {
    const item = document.createElement("li");
    const time = document.createElement("time");
    time.textContent = new Date(entry.timestamp).toLocaleTimeString();
    const origin = diagnosticOrigin(entry);
    const originLabel = document.createElement("span");
    originLabel.className = `debug-origin debug-origin--${origin}`;
    originLabel.textContent = diagnosticOriginLabel(origin);
    const code = document.createElement("code");
    const action = entry.details?.action ? ` (${entry.details.action})` : "";
    code.textContent = `${entry.event}${action}${entry.outcome === "failure" ? " [failed]" : ""}`;
    item.append(time, originLabel, code);
    return item;
  }));
}

function diagnosticOrigin(entry) {
  if (entry.surface === "server") return "server";
  if (entry.surface === "host" || entry.surface === "host-observed") return "host";
  return "widget";
}

function diagnosticOriginLabel(origin) {
  return origin === "server" ? "MCP server" : origin === "host" ? "Host" : "Widget";
}

function bridge() {
  return window.creativeProductionMcp;
}

async function rawToolCall(arguments_) {
  if (!bridge()?.callServerTool) throw new Error("Creative Production bridge is unavailable");
  const result = await bridge().callServerTool({ name: TOOL_NAME, arguments: arguments_ });
  if (result?.isError) throw new Error(result.content?.[0]?.text || "Creative Production tool failed");
  return result;
}

function enqueueAction(label, operation, { priority = "foreground", trace = true } = {}) {
  const queue = priority === "foreground" ? state.foregroundBridgeQueue : state.backgroundBridgeQueue;
  const queueDepth = state.foregroundBridgeQueue.length + state.backgroundBridgeQueue.length + (state.bridgeQueueActive ? 1 : 0) + 1;
  if (trace) diagnostic("bridge.call.enqueued", { action: label, priority, queueDepth }, "pending");
  return new Promise((resolve, reject) => {
    queue.push({ label, operation, resolve, reject, trace, queuedAt: performance.now(), queueDepth });
    void drainBridgeQueue();
  });
}

async function drainBridgeQueue() {
  if (state.bridgeQueueActive) return;
  state.bridgeQueueActive = true;
  while (state.foregroundBridgeQueue.length || state.backgroundBridgeQueue.length) {
    const task = state.foregroundBridgeQueue.shift() || state.backgroundBridgeQueue.shift();
    const started = performance.now();
    const queueWaitMs = Math.round(started - task.queuedAt);
    if (task.trace) diagnostic("bridge.call.started", { action: task.label, queueDepth: task.queueDepth, queueWaitMs }, "pending");
    try {
      const value = await task.operation();
      state.lastError = "";
      if (task.trace) diagnostic("bridge.call.completed", { action: task.label, durationMs: Math.round(performance.now() - started), queueDepth: task.queueDepth, queueWaitMs });
      task.resolve(value);
    } catch (error) {
      if (task.trace) {
        state.lastError = messageFor(error);
        diagnostic("bridge.call.failed", { action: task.label, durationMs: Math.round(performance.now() - started), errorCode: "bridge_call_failed", queueDepth: task.queueDepth, queueWaitMs }, "failure");
      }
      task.reject(error);
    }
  }
  state.bridgeQueueActive = false;
}

function enqueueQuietAction(operation) {
  return enqueueAction("background", operation, { priority: "background", trace: false });
}

function enqueueBackgroundAction(label, operation) {
  return enqueueAction(label, operation, { priority: "background" });
}

function widgetDataFrom(value = window.openai) {
  return value?.toolResponseMetadata?.widgetData
    || value?.toolOutput?.widgetData
    || (value?.toolOutput?.kind ? value.toolOutput : null)
    || value?.widgetData
    || value?._meta?.widgetData
    || null;
}

async function applyWidgetData(payload, options = {}) {
  if (!payload) return false;
  if (payload.kind === "board" && payload.board) {
    for (const asset of payload.assets || []) {
      state.previews.set(asset.itemId, `data:${asset.mimeType};base64,${asset.data}`);
    }
    applyBoard(payload.board, payload.trace || [], options);
    if (!state.viewCacheReady && !state.viewCacheRestoring) {
      state.viewCacheRestoring = true;
      try {
        await restoreViewCache();
      } finally {
        state.viewCacheRestoring = false;
      }
    } else {
      scheduleViewCacheWrite();
    }
    return true;
  }
  if (payload.kind === "asset" && payload.asset) {
    state.previews.set(payload.asset.itemId, `data:${payload.asset.mimeType};base64,${payload.asset.data}`);
    diagnostic("asset.preview.received", { itemId: payload.asset.itemId, bytes: payload.asset.bytes });
    renderBoard();
    scheduleViewCacheWrite();
    return true;
  }
  if (payload.kind === "receipt" && payload.receipt) {
    diagnostic("mutation.receipt.received", { action: payload.receipt.action, revision: payload.receipt.revision });
    if (payload.receipt.action !== "append_log") await refreshBoard("receipt");
    return true;
  }
  return false;
}

function applyBoard(incoming, trace = [], { quiet = false, authoritative = false } = {}) {
  if (state.board && incoming.boardId !== state.board.boardId) {
    diagnostic("board.identity.rejected", { incomingBoardId: incoming.boardId }, "failure");
    return;
  }
  mergeTrace(trace);
  reconcilePendingDeletes(incoming);
  if (state.board && incoming.revision < state.board.revision) {
    const snapshotKey = `${incoming.revision}:${state.board.revision}`;
    if (snapshotKey !== state.lastIgnoredSnapshotKey) {
      state.lastIgnoredSnapshotKey = snapshotKey;
      diagnostic("board.stale_snapshot.ignored", { incomingRevision: incoming.revision });
    } else {
      renderDiagnostics();
    }
    return;
  }
  const previousRevision = state.board?.revision;
  const localUi = state.uiEpoch > state.uiCommittedEpoch ? structuredClone(state.board?.ui) : null;
  if (state.board && incoming.revision === state.board.revision && !localUi && !authoritative) {
    state.lastError = "";
    renderDiagnostics();
    return;
  }
  state.lastIgnoredSnapshotKey = "";
  state.board = structuredClone(incoming);
  if (localUi) state.board.ui = localUi;
  applyPendingDeleteOverlay(state.board);
  if (quiet && previousRevision === incoming.revision && !localUi) {
    state.lastError = "";
    renderDiagnostics();
    return;
  }
  state.lastError = "";
  if (!quiet) diagnostic("board.state.reconciled", { revision: state.board.revision, itemCount: state.board.items.length });
  renderBoard();
  void loadMissingPreviews();
  if (hasActiveGeneration()) startGenerationWatch(true);
  scheduleVisibleSync();
  scheduleViewCacheWrite();
}

function applyPendingDeleteOverlay(board) {
  for (const item of board.items) {
    if (state.pendingDeleteIds.has(item.id)) item.deletedAt = item.deletedAt || "pending:local";
  }
}

function reconcilePendingDeletes(incoming) {
  let changed = false;
  for (const [mutationId, mutation] of state.pendingDeleteMutations) {
    const applied = incoming.appliedMutationIds?.includes(mutationId);
    const deleted = mutation.itemIds.every((itemId) => {
      const item = incoming.items.find((candidate) => candidate.id === itemId);
      return !item || (item.deletedAt && !String(item.deletedAt).startsWith("pending:"));
    });
    if (!applied && !deleted) continue;
    state.pendingDeleteMutations.delete(mutationId);
    changed = true;
  }
  if (changed) rebuildPendingDeleteIds();
}

function mergeTrace(trace) {
  for (const event of trace) {
    if (!state.diagnostics.some((candidate) => candidate.eventId && candidate.eventId === event.eventId)) {
      state.diagnostics.push(event);
    }
  }
  state.diagnostics = state.diagnostics.slice(-MAX_DIAGNOSTIC_EVENTS);
}

async function refreshBoard(reason = "manual", { quiet = false, trace = true } = {}) {
  if (!state.board?.boardId) return;
  if (state.refreshPromise) return state.refreshPromise;
  const operation = async () => {
    if (!quiet) diagnostic("board.refresh.started", { reason }, "pending");
    const result = await rawToolCall({ action: "read", boardId: state.board.boardId, correlationId: crypto.randomUUID() });
    await applyWidgetData(widgetDataFrom(result), { quiet, authoritative: true });
  };
  state.refreshPromise = (trace ? enqueueBackgroundAction("read", operation) : enqueueQuietAction(operation))
    .finally(() => { state.refreshPromise = null; });
  return state.refreshPromise;
}

function scheduleVisibleSync(delayMs = 2_000) {
  if (!state.board?.boardId || state.visibleSyncTimer) return;
  state.visibleSyncTimer = window.setTimeout(() => {
    state.visibleSyncTimer = 0;
    void runVisibleSync();
  }, delayMs);
}

async function runVisibleSync() {
  if (!state.board?.boardId) return;
  if (document.hidden) {
    scheduleVisibleSync(3_000);
    return;
  }
  try {
    await refreshBoard("visible_sync", { quiet: true, trace: false });
    if (state.visibleSyncFailed) {
      state.visibleSyncFailed = false;
      diagnostic("board.sync.recovered", {}, "success", { persist: false });
    }
  } catch {
    if (!state.visibleSyncFailed) {
      state.visibleSyncFailed = true;
      diagnostic("board.sync.retrying", { retryDelayMs: 2_000 }, "failure", { persist: false });
    }
  }
  scheduleVisibleSync();
}

function hasActiveGeneration() {
  return visibleItems().some((item) => item.generationState === "generating");
}

function startGenerationWatch(sawActive = false) {
  state.generationWatchDeadline = Math.max(state.generationWatchDeadline, Date.now() + 5 * 60_000);
  state.generationWatchSawActive ||= sawActive || hasActiveGeneration();
  scheduleGenerationWatch(600);
}

function scheduleGenerationWatch(delayMs) {
  if (state.generationWatchTimer) return;
  state.generationWatchTimer = window.setTimeout(() => {
    state.generationWatchTimer = 0;
    void runGenerationWatch();
  }, delayMs);
}

function stopGenerationWatch(event) {
  if (state.generationWatchTimer) window.clearTimeout(state.generationWatchTimer);
  state.generationWatchTimer = 0;
  state.generationWatchDeadline = 0;
  state.generationWatchSawActive = false;
  if (event) diagnostic(event);
}

async function runGenerationWatch() {
  if (!state.generationWatchDeadline || !state.board?.boardId) return;
  if (Date.now() >= state.generationWatchDeadline) {
    stopGenerationWatch("generation.watch.expired");
    return;
  }
  if (document.hidden) {
    scheduleGenerationWatch(2_000);
    return;
  }
  try {
    await refreshBoard("generation_watch", { quiet: true });
  } catch {
    scheduleGenerationWatch(2_000);
    return;
  }
  const active = hasActiveGeneration();
  state.generationWatchSawActive ||= active;
  if (state.generationWatchSawActive && !active) {
    stopGenerationWatch("generation.watch.completed");
    return;
  }
  scheduleGenerationWatch(1_500);
}

async function loadMissingPreviews() {
  const readyItems = visibleItems().filter((item) => item.generationState === "ready" && !state.previews.has(item.id));
  for (const item of readyItems) {
    try {
      const result = await enqueueBackgroundAction("read_preview", () => rawToolCall({ action: "read", boardId: state.board.boardId, itemId: item.id, correlationId: crypto.randomUUID() }));
      await applyWidgetData(widgetDataFrom(result));
    } catch {
      // The diagnostic panel already records the bridge failure.
    }
  }
}

function visibleItems() {
  return (state.board?.items || []).filter((item) => !item.deletedAt);
}

function renderBoard() {
  if (!state.board) return;
  elements.title.textContent = state.board.title || "Creative Production";
  elements.summary.textContent = state.board.summary || "Start with an idea";
  const items = visibleItems();
  renderSelectionToolbar();
  if (!items.length) renderZeroState();
  else renderTiles(items);
  renderViewer();
  renderDiagnostics();
  window.installPlatformIcons?.();
  window.installBrandIcons?.();
  bridge()?.notifyResize?.();
}

function renderZeroState() {
  if (state.starterView) return;
  elements.feed.replaceChildren();
  const panel = document.createElement("section");
  panel.className = "empty-board-panel";
  const starters = document.createElement("div");
  starters.style.width = "100%";
  panel.append(starters);
  elements.feed.append(panel);
  window.mountEmptyStateGrid?.(starters, {
    assetUrlForStarter: (starter) => window.CREATIVE_PRODUCTION_STARTER_ASSETS?.[starter.id],
    onSelect: showStarterIntake,
  });
}

function starterAttachmentRemoveButton(ariaLabel) {
  const button = document.createElement("button");
  button.className = "starter-intake-attachment-remove";
  button.type = "button";
  button.ariaLabel = ariaLabel;
  button.title = "Remove";
  button.innerHTML = `
    <svg class="platform-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path fill-rule="evenodd" d="M5.636 5.636a1 1 0 0 1 1.414 0l4.95 4.95 4.95-4.95a1 1 0 0 1 1.414 1.414L13.414 12l4.95 4.95a1 1 0 0 1-1.414 1.414L12 13.414l-4.95 4.95a1 1 0 0 1-1.414-1.414l4.95-4.95-4.95-4.95a1 1 0 0 1 0-1.414Z" clip-rule="evenodd"></path>
    </svg>`;
  return button;
}

function showStarterIntake(rawStarter) {
  const runtime = window.CreativeProductionStarterIntakeRuntime;
  const starter = runtime?.detailsFor?.(rawStarter) || rawStarter;
  state.starterView = starter;
  const page = document.createElement("section");
  page.className = "starter-intake-page";
  const panel = document.createElement("div");
  panel.className = "starter-intake-panel";
  panel.innerHTML = `
    <div class="starter-intake-copy"><h2>${escapeHtml(runtime?.title?.(starter) || starter.title)}</h2><p>${escapeHtml(runtime?.subtitle?.(starter) || "Share a brief or some quick notes.")}</p></div>
    <form class="starter-intake-form">
      <div class="starter-intake-composer">
        <div class="starter-intake-attachments" aria-live="polite" hidden></div>
        <textarea rows="4" placeholder="Describe what you want to create"></textarea>
        <div class="starter-intake-footer">
          <button class="starter-intake-attach-button" type="button" aria-label="Attach references" title="Attach references">
            <span data-platform-icon="plus" aria-hidden="true"></span>
          </button>
        </div>
      </div>
      ${runtime?.suggestionMarkup?.(starter) || ""}
      <input class="starter-file-input" type="file" accept="image/*" multiple hidden>
      <div class="starter-intake-actions"><div class="starter-intake-actions-inner"><div class="starter-intake-action-buttons"><button class="starter-intake-cancel" type="button">Back</button><button class="starter-intake-submit" type="submit">Create</button></div></div></div>
    </form>`;
  page.append(panel);
  elements.feed.replaceChildren(page);
  const textarea = page.querySelector("textarea");
  const input = page.querySelector("input[type=file]");
  const attachments = page.querySelector(".starter-intake-attachments");
  let starterAsset = null;
  let selectedFiles = [];
  let filePreviewUrls = [];
  const clearFilePreviews = () => {
    filePreviewUrls.forEach((url) => URL.revokeObjectURL(url));
    filePreviewUrls = [];
  };
  const renderAttachments = () => {
    clearFilePreviews();
    attachments.replaceChildren();
    const entries = [];
    if (starterAsset?.previewUrl) {
      entries.push({ label: starterAsset.label || "Starter reference", url: starterAsset.previewUrl, starter: true });
    }
    selectedFiles.forEach((file, index) => {
      const url = URL.createObjectURL(file);
      filePreviewUrls.push(url);
      entries.push({ label: file.name, url, fileIndex: index });
    });
    for (const entry of entries) {
      const preview = document.createElement("div");
      preview.className = "starter-intake-attachment";
      const image = document.createElement("img");
      image.src = entry.url;
      image.alt = entry.label;
      const remove = starterAttachmentRemoveButton(`Remove ${entry.starter ? "starter asset" : entry.label}`);
      remove.addEventListener("click", () => {
        if (entry.starter) starterAsset = null;
        else selectedFiles.splice(entry.fileIndex, 1);
        renderAttachments();
      });
      preview.append(image, remove);
      attachments.append(preview);
    }
    attachments.hidden = entries.length === 0;
    window.installPlatformIcons?.(attachments);
  };
  page.querySelectorAll(".starter-intake-suggestion").forEach((button) => button.addEventListener("click", () => {
    textarea.value = button.dataset.suggestionText || button.textContent.trim();
    const assetPath = button.dataset.suggestionAsset || "";
    const asset = window.CREATIVE_PRODUCTION_STARTER_SUGGESTION_ASSETS?.[assetPath];
    starterAsset = assetPath && asset
      ? {
          path: asset.pluginRelativePath || assetPath,
          label: button.textContent.trim(),
          previewUrl: asset.previewUrl || "",
        }
      : null;
    renderAttachments();
    textarea.focus();
  }));
  page.querySelector(".starter-intake-attach-button").addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    selectedFiles = [...input.files];
    renderAttachments();
  });
  page.querySelector(".starter-intake-cancel").addEventListener("click", () => {
    clearFilePreviews();
    state.starterView = null;
    renderBoard();
  });
  page.querySelector("form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const notes = textarea.value.trim();
    if (!notes) { textarea.focus(); return; }
    const button = page.querySelector(".starter-intake-submit");
    button.disabled = true;
    try {
      const prompt = generationHandoff(
        runtime?.prompt?.(starter, notes, selectedFiles, { starterAsset }) || notes,
        { title: starter.title, count: 4 },
      );
      await sendFollowUp(prompt, selectedFiles);
      clearFilePreviews();
      startGenerationWatch();
      state.starterView = null;
      renderBoard();
      showToast("Follow-up ready. Generation will appear here after it starts.");
      diagnostic("follow_up.accepted", { source: "zero_state" });
    } catch (error) {
      showToast(messageFor(error));
    } finally {
      button.disabled = false;
    }
  });
  window.installPlatformIcons?.(page);
}

function renderTiles(items) {
  const columnCount = columnCountForWidth(elements.feed.clientWidth || window.innerWidth);
  elements.feed.style.setProperty("--columns", String(columnCount));
  const columns = Array.from({ length: columnCount }, () => {
    const column = document.createElement("div");
    column.className = "column";
    return column;
  });
  items.forEach((item, index) => columns[index % columnCount].append(createTile(item, index)));
  elements.feed.replaceChildren(...columns);
}

function createTile(item, index) {
  const tile = elements.template.content.firstElementChild.cloneNode(true);
  tile.dataset.itemId = item.id;
  tile.style.aspectRatio = aspectRatios[index % aspectRatios.length];
  const selected = state.board.ui.selectedItemIds.includes(item.id);
  tile.classList.toggle("is-selected", selected);
  const placeholder = tile.querySelector(".generation-placeholder");
  const image = tile.querySelector("img");
  const source = state.previews.get(item.id);
  const pending = item.generationState === "generating";
  const failed = item.generationState === "failed";
  tile.classList.toggle("is-waiting", pending);
  tile.classList.toggle("is-generation-failed", failed);
  placeholder.hidden = !(pending || failed);
  if (pending) window.installGenerationHalftone?.(placeholder.querySelector("canvas"));
  image.hidden = !source;
  if (source) {
    image.src = source;
    image.alt = item.title || "Creative image";
    image.style.objectPosition = cropPositions[index % cropPositions.length];
  }
  const open = tile.querySelector(".tile-open");
  open.disabled = !source;
  open.setAttribute("aria-label", source ? `Open ${item.title}` : item.title);
  open.addEventListener("click", () => openViewer(item.id));
  const selectButton = tile.querySelector(".select-button");
  selectButton.setAttribute("aria-pressed", String(selected));
  selectButton.addEventListener("click", (event) => { event.stopPropagation(); toggleSelection(item.id); });
  tile.querySelector(".remove-button").addEventListener("click", (event) => { event.stopPropagation(); void deleteItems([item.id]); });
  return tile;
}

function columnCountForWidth(width) {
  if (!Number.isFinite(width) || width <= 0) return 5;
  if (width <= 360) return 1;
  if (width <= 480) return 2;
  if (width <= 680) return 3;
  if (width <= 920) return 4;
  return 5;
}

function toggleSelection(itemId) {
  const selected = new Set(state.board.ui.selectedItemIds);
  if (selected.has(itemId)) selected.delete(itemId); else selected.add(itemId);
  state.board.ui.selectedItemIds = [...selected];
  markUiDirty();
  renderBoard();
}

function clearSelection() {
  state.board.ui.selectedItemIds = [];
  markUiDirty();
  renderBoard();
}

function renderSelectionToolbar() {
  const count = state.board.ui.selectedItemIds.length;
  elements.selectionToolbar.hidden = count === 0;
  elements.exportActions.hidden = count === 0;
  elements.selectionAttach.querySelector(".button-label").textContent = count > 1 ? `Attach (${count})` : "Attach";
}

function markUiDirty() {
  state.uiEpoch += 1;
  const epoch = state.uiEpoch;
  scheduleViewCacheWrite();
  window.clearTimeout(state.uiSaveTimer);
  state.uiSaveTimer = window.setTimeout(() => void persistUi(epoch), 120);
}

async function persistUi(epoch) {
  const uiState = structuredClone(state.board.ui);
  try {
    const result = await enqueueBackgroundAction("set_ui_state", () => rawToolCall({
      action: "set_ui_state",
      boardId: state.board.boardId,
      uiState,
      mutationId: `ui-${crypto.randomUUID()}`,
      correlationId: crypto.randomUUID(),
    }));
    state.uiCommittedEpoch = Math.max(state.uiCommittedEpoch, epoch);
    await applyWidgetData(widgetDataFrom(result));
  } catch {
    // The optimistic state remains visible and the diagnostic panel exposes the failure.
  }
}

async function deleteItems(itemIds) {
  const visibleItemIds = new Set(visibleItems().map((item) => item.id));
  const uniqueItemIds = [...new Set(itemIds)].filter((itemId) => visibleItemIds.has(itemId));
  if (!uniqueItemIds.length) return;
  const mutation = {
    mutationId: `delete-${crypto.randomUUID()}`,
    itemIds: uniqueItemIds,
    queuedAt: new Date().toISOString(),
  };
  diagnostic("ui.delete.clicked", { action: "delete_items", itemCount: uniqueItemIds.length, mutationId: mutation.mutationId }, "pending");
  state.pendingDeleteMutations.set(mutation.mutationId, mutation);
  uniqueItemIds.forEach((itemId) => state.pendingDeleteIds.add(itemId));
  for (const item of state.board.items) {
    if (state.pendingDeleteIds.has(item.id)) item.deletedAt = `pending:${mutation.mutationId}`;
  }
  state.board.ui.selectedItemIds = state.board.ui.selectedItemIds.filter((itemId) => !state.pendingDeleteIds.has(itemId));
  if (state.pendingDeleteIds.has(state.board.ui.currentItemId)) state.board.ui.currentItemId = null;
  if (state.pendingDeleteIds.has(state.viewerItemId)) {
    state.viewerItemId = null;
    elements.viewer.classList.remove("active", "has-remix-panel");
    elements.viewer.setAttribute("aria-hidden", "true");
  }
  markUiDirty();
  renderBoard();
  void dispatchPendingDelete(mutation);
  scheduleViewCacheWrite();
}

function rebuildPendingDeleteIds() {
  state.pendingDeleteIds.clear();
  for (const mutation of state.pendingDeleteMutations.values()) {
    mutation.itemIds.forEach((itemId) => state.pendingDeleteIds.add(itemId));
  }
}

function schedulePendingDeleteRetry() {
  if (state.pendingDeleteRetryTimer || !state.pendingDeleteMutations.size) return;
  state.pendingDeleteRetryTimer = window.setTimeout(() => {
    state.pendingDeleteRetryTimer = 0;
    void replayPendingDeletes();
  }, 1_500);
}

async function replayPendingDeletes() {
  if (document.hidden) return;
  for (const mutation of state.pendingDeleteMutations.values()) {
    await dispatchPendingDelete(mutation);
  }
}

async function dispatchPendingDelete(mutation) {
  if (!state.pendingDeleteMutations.has(mutation.mutationId) || state.pendingDeleteDispatches.has(mutation.mutationId)) return;
  state.pendingDeleteDispatches.add(mutation.mutationId);
  try {
    const result = await enqueueAction("delete_items", () => rawToolCall({
      action: "delete_items",
      boardId: state.board.boardId,
      itemIds: mutation.itemIds,
      mutationId: mutation.mutationId,
      correlationId: crypto.randomUUID(),
    }));
    state.pendingDeleteMutations.delete(mutation.mutationId);
    rebuildPendingDeleteIds();
    scheduleViewCacheWrite();
    await applyWidgetData(widgetDataFrom(result));
  } catch {
    diagnostic("ui.delete.queued_for_retry", { action: "delete_items", itemCount: mutation.itemIds.length, mutationId: mutation.mutationId }, "pending");
    showToast("Delete queued for retry");
    schedulePendingDeleteRetry();
  } finally {
    state.pendingDeleteDispatches.delete(mutation.mutationId);
  }
}

function openViewer(itemId) {
  if (!state.previews.has(itemId)) return;
  state.viewerItemId = itemId;
  state.board.ui.currentItemId = itemId;
  elements.viewer.classList.add("active");
  elements.viewer.setAttribute("aria-hidden", "false");
  markUiDirty();
  renderViewer();
}

function closeViewer() {
  closeAnnotationComposer();
  state.viewerItemId = null;
  state.board.ui.currentItemId = null;
  elements.viewer.classList.remove("active", "has-remix-panel");
  elements.viewer.setAttribute("aria-hidden", "true");
  elements.remixPanel.hidden = true;
  elements.remixPanel.setAttribute("aria-hidden", "true");
  elements.remixPanel.style.removeProperty("--viewer-remix-panel-height");
  elements.viewer.style.removeProperty("--viewer-remix-image-shift");
  elements.viewerExportActions.hidden = true;
  markUiDirty();
}

function renderViewer() {
  const itemId = state.viewerItemId || state.board?.ui.currentItemId;
  const item = visibleItems().find((candidate) => candidate.id === itemId);
  const source = item && state.previews.get(item.id);
  if (!item || !source) {
    if (elements.viewer.classList.contains("active")) closeViewer();
    return;
  }
  state.viewerItemId = item.id;
  elements.viewerImage.src = source;
  elements.viewerImage.alt = item.title || "Creative image";
  elements.viewerPrev.disabled = visibleReadyItems().length < 2;
  elements.viewerNext.disabled = visibleReadyItems().length < 2;
  elements.viewerExportActions.hidden = false;
}

function visibleReadyItems() {
  return visibleItems().filter((item) => state.previews.has(item.id));
}

function navigateViewer(direction) {
  closeAnnotationComposer();
  const items = visibleReadyItems();
  const index = items.findIndex((item) => item.id === state.viewerItemId);
  if (index < 0 || items.length < 2) return;
  openViewer(items[(index + direction + items.length) % items.length].id);
}

function toggleRemixPanel() {
  const next = elements.remixPanel.hidden;
  if (next) closeAnnotationComposer();
  elements.remixImage.setAttribute("aria-expanded", String(next));
  elements.remixPanel.setAttribute("aria-hidden", String(!next));
  if (!next) {
    elements.viewer.classList.remove("has-remix-panel");
    elements.remixPanel.hidden = true;
    elements.remixPanel.style.removeProperty("--viewer-remix-panel-height");
    elements.viewer.style.removeProperty("--viewer-remix-image-shift");
    return;
  }
  elements.remixPanel.hidden = false;
  renderRemixPanel();
  const panelHeight = elements.remixPanel.scrollHeight;
  const toolbar = elements.viewer.querySelector(".viewer-toolbar");
  const toolbarClearance = Math.max(window.innerHeight - toolbar.getBoundingClientRect().top + 8, 0);
  elements.viewer.style.setProperty("--viewer-remix-toolbar-clearance", `${toolbarClearance}px`);
  elements.remixPanel.style.setProperty("--viewer-remix-panel-height", `${panelHeight}px`);
  elements.viewer.style.setProperty("--viewer-remix-image-shift", `${-Math.max(Math.round(panelHeight / 2) - 8, 0)}px`);
  requestAnimationFrame(() => elements.viewer.classList.add("has-remix-panel"));
}

function renderRemixPanel() {
  const item = visibleItems().find((candidate) => candidate.id === state.viewerItemId);
  if (!item) return;
  elements.remixTabs.replaceChildren(...REMIX_SLOTS.map((slot, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "viewer-remix-slot-tab";
    button.id = `remix-slot-tab-${slot.id}`;
    button.dataset.remixSlotId = slot.id;
    button.textContent = slot.label;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", "remixOptionList");
    button.setAttribute("aria-selected", String(state.remixSlot === slot.id));
    button.tabIndex = state.remixSlot === slot.id ? 0 : -1;
    button.addEventListener("click", () => { state.remixSlot = slot.id; renderRemixPanel(); });
    button.addEventListener("keydown", (event) => {
      const offsets = { ArrowLeft: -1, ArrowRight: 1 };
      if (!(event.key in offsets) && event.key !== "Home" && event.key !== "End") return;
      event.preventDefault();
      const nextIndex = event.key === "Home"
        ? 0
        : event.key === "End"
          ? REMIX_SLOTS.length - 1
          : (index + offsets[event.key] + REMIX_SLOTS.length) % REMIX_SLOTS.length;
      state.remixSlot = REMIX_SLOTS[nextIndex].id;
      renderRemixPanel();
      elements.remixTabs.querySelector(`[data-remix-slot-id="${state.remixSlot}"]`)?.focus();
    });
    return button;
  }));
  elements.remixOptions.setAttribute("aria-labelledby", `remix-slot-tab-${state.remixSlot}`);
  const slot = REMIX_SLOTS.find((candidate) => candidate.id === state.remixSlot) || REMIX_SLOTS[0];
  const choices = remixOptionsForItem(item, slot);
  elements.remixOptions.replaceChildren(...choices.map((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "viewer-remix-option";
    button.classList.toggle("is-selected", state.remixSelections[state.remixSlot] === option.id);
    button.setAttribute("aria-pressed", String(state.remixSelections[state.remixSlot] === option.id));
    const copy = document.createElement("span");
    copy.className = "viewer-remix-option-copy";
    const label = document.createElement("strong");
    label.textContent = option.label;
    const description = document.createElement("p");
    description.textContent = option.description;
    copy.append(label, description);
    button.append(copy);
    button.addEventListener("click", () => {
      state.remixSelections[state.remixSlot] = option.id;
      renderRemixPanel();
      void requestRemix(option);
    });
    return button;
  }));
}

function compactRemixText(value, limit = 120) {
  const text = String(value || "").replace(/\s+/g, " ").replace(/[.]+$/g, "").trim();
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 3).replace(/\s+\S*$/, "")}...`;
}

function remixFocusLabel(item) {
  const title = compactRemixText(item?.title, 42);
  if (title && !/^image[-\s]*\d*$/i.test(title)) return title;
  const words = String(item?.caption || item?.prompt || "Selected image").match(/[A-Za-z0-9]+/g) || [];
  const meaningful = words.filter((word) => !["and", "the", "with", "from", "into", "for", "image"].includes(word.toLowerCase()));
  return (meaningful.slice(0, 3).join(" ") || "Selected Image").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function remixFocusNoun(item) {
  const stopWords = new Set(["cue", "detail", "echo", "flash", "frame", "image", "life", "moment", "motion", "object", "route", "scene", "service", "shot", "story", "study", "treatment", "ritual"]);
  const words = remixFocusLabel(item).match(/[A-Za-z0-9]+/g) || [];
  const meaningful = words.filter((word) => !/^\d+$/.test(word));
  const specific = meaningful.filter((word) => !stopWords.has(word.toLowerCase()));
  return specific.at(-1) || meaningful.at(-1) || "Image";
}

function remixVisualCue(item) {
  return compactRemixText(item?.caption || item?.prompt || item?.tone || item?.title || "the source image", 120);
}

function remixSeed(item, slotId) {
  const source = [slotId, item?.title, item?.caption, item?.prompt, item?.tone, item?.family].filter(Boolean).join("|");
  return [...source].reduce((total, character, index) => total + character.charCodeAt(0) * (index + 1), 0);
}

function spreadRemixOptions(item, slotId) {
  const options = REMIX_OPTION_LIBRARY[slotId] || [];
  if (options.length <= 3) return options;
  const start = remixSeed(item, slotId) % options.length;
  const rotated = [...options.slice(start), ...options.slice(0, start)];
  const stride = options.length % 2 ? 2 : Math.max(options.length - 1, 1);
  const ordered = [];
  for (let index = 0; ordered.length < options.length; index += stride) {
    const option = rotated[index % rotated.length];
    if (!ordered.includes(option)) ordered.push(option);
  }
  return ordered.slice(0, 3);
}

function contextualRemixOption(item, slot, option) {
  const focus = remixFocusLabel(item);
  const noun = remixFocusNoun(item);
  const cue = remixVisualCue(item);
  const label = option.label || [option.lead, noun, option.suffix].filter(Boolean).join(" ");
  return {
    id: option.id,
    label,
    description: `${option.description} Keep ${focus} recognizable.`,
    promptHint: `${option.promptHint} for ${focus}. Preserve the source image's core cue: ${cue}.`,
  };
}

function normalizeProvidedRemixOption(option, index, slot) {
  if (typeof option === "string") return { id: `${slot.id}-${index}`, label: option, description: slot.promptHint, promptHint: option };
  if (!option || typeof option !== "object") return null;
  const label = String(option.label || option.title || option.direction || "").trim();
  if (!label) return null;
  return {
    id: String(option.id || `${slot.id}-${index}`),
    label,
    description: String(option.description || option.summary || option.detail || slot.promptHint),
    promptHint: String(option.promptHint || option.prompt || option.description || label),
  };
}

function remixOptionsForItem(item, slot) {
  const provided = item?.remixSuggestions?.[slot.id];
  if (Array.isArray(provided)) {
    const normalized = provided.map((option, index) => normalizeProvidedRemixOption(option, index, slot)).filter(Boolean).slice(0, 3);
    if (normalized.length) return normalized;
  }
  return spreadRemixOptions(item, slot.id).map((option) => contextualRemixOption(item, slot, option));
}

async function requestRemix(option) {
  const item = visibleItems().find((candidate) => candidate.id === state.viewerItemId);
  if (!item) return;
  const remixSlot = state.remixSlot;
  elements.remixStatus.hidden = true;
  elements.remixStatus.textContent = "";
  const prompt = generationHandoff(`Create a variation of "${item.title}". Change the ${remixSlot} in this direction: ${option.label}. ${option.promptHint}`, { title: `${option.label} variation`, count: 1, parentItemId: item.id });
  try {
    await sendFollowUp(prompt);
    startGenerationWatch();
    diagnostic("follow_up.accepted", { source: "remix", itemId: item.id, slot: remixSlot, direction: option.label });
    showToast("Remix request ready. A placeholder appears only after generation starts.");
  } catch (error) {
    elements.remixStatus.hidden = false;
    elements.remixStatus.textContent = messageFor(error);
    diagnostic("follow_up.failed", { source: "remix", itemId: item.id, error: messageFor(error) }, "failure");
  }
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function clamp01(value) {
  return clamp(value, 0, 1);
}

function closeAnnotationComposer() {
  state.activeAnnotationComposer?.remove();
  state.activeAnnotationComposer = null;
}

function annotationComposerMarkup() {
  return [
    '<span class="annotation-marker" aria-hidden="true"></span>',
    '<div class="annotation-bubble">',
    '<span class="annotation-leading-icon" data-platform-icon="annotate"></span>',
    '<input class="annotation-input" type="text" autocomplete="off" placeholder="Annotate this spot..." />',
    '<button class="annotation-cancel" type="button" aria-label="Cancel"><span data-platform-icon="x"></span></button>',
    '<button class="annotation-submit" type="submit" aria-label="Attach annotation"><span data-platform-icon="chevron-right"></span></button>',
    '</div>',
  ].join("");
}

function viewerImageAnnotationPoint(event) {
  const rect = elements.viewerImage.getBoundingClientRect();
  if (!rect.width || !rect.height) return null;
  const clientX = event?.clientX ?? rect.left + rect.width / 2;
  const clientY = event?.clientY ?? rect.top + rect.height / 2;
  return {
    x: clamp01((clientX - rect.left) / rect.width),
    y: clamp01((clientY - rect.top) / rect.height),
    clientX: clamp(clientX, rect.left, rect.right),
    clientY: clamp(clientY, rect.top, rect.bottom),
  };
}

function placeAnnotationComposer(composer, point) {
  const padding = 16;
  const toolbar = elements.viewer.querySelector(".viewer-toolbar");
  const toolbarRect = toolbar?.getBoundingClientRect();
  const safe = {
    left: padding,
    top: padding,
    right: window.innerWidth - padding,
    bottom: Math.max(padding + 42, Math.min(window.innerHeight - padding, toolbarRect?.top ? toolbarRect.top - 12 : window.innerHeight - padding)),
  };
  const gap = 16;
  const markerX = clamp(point.clientX, safe.left, safe.right);
  const markerY = clamp(point.clientY, safe.top, safe.bottom);
  const width = Math.min(composer.offsetWidth || 420, safe.right - safe.left);
  const height = composer.querySelector(".annotation-bubble")?.offsetHeight || 42;
  const right = markerX + gap;
  const left = markerX - width - gap;
  const fitsRight = right + width <= safe.right;
  const fitsLeft = left >= safe.left;
  const bubbleLeft = fitsRight ? right : fitsLeft ? left : clamp(markerX - 20, safe.left, safe.right - width);
  const bubbleTop = clamp(markerY - height / 2, safe.top, safe.bottom - height);
  composer.classList.toggle("is-edge-aligned", !fitsRight && fitsLeft);
  composer.style.setProperty("--annotation-x", `${markerX}px`);
  composer.style.setProperty("--annotation-y", `${markerY}px`);
  composer.style.setProperty("--annotation-bubble-left", `${bubbleLeft}px`);
  composer.style.setProperty("--annotation-bubble-top", `${bubbleTop}px`);
  composer.style.setProperty("--annotation-marker-left", `${markerX - bubbleLeft}px`);
  composer.style.setProperty("--annotation-marker-top", `${markerY - bubbleTop}px`);
}

async function attachAnnotations(item, annotations) {
  if (!bridge()?.updateModelContext) throw new Error("Composer context is unavailable");
  const parsed = parseDataUrl(state.previews.get(item.id));
  const itemAnnotations = annotations.filter((annotation) => annotation.itemIds.includes(item.id));
  const annotationSummary = itemAnnotations.map((annotation, index) => (
    `${index + 1}. ${annotation.text}. Spot: x=${annotation.point.x}, y=${annotation.point.y}`
  )).join("\n");
  await bridge().updateModelContext({
    content: [
      { type: "text", text: `Edit annotations for ${item.title}:\n${annotationSummary}\nCoordinates are normalized from the image's top-left.` },
      { type: "image", data: parsed.data, mimeType: parsed.mimeType },
    ],
    structuredContent: {
      kind: "creative-production-board-annotation",
      boardId: state.board.boardId,
      revision: state.board.revision,
      sourceItem: { id: item.id, title: item.title, caption: item.caption, prompt: item.prompt },
      annotations: itemAnnotations.map((annotation) => ({
        id: annotation.id,
        text: annotation.text,
        point: annotation.point,
      })),
      coordinateSystem: "normalized_image_top_left",
    },
  });
}

function addAnnotation(event) {
  const item = visibleItems().find((candidate) => candidate.id === state.viewerItemId);
  const point = viewerImageAnnotationPoint(event);
  if (!item || !point) return;
  event?.preventDefault();
  event?.stopPropagation();
  closeAnnotationComposer();
  const composer = document.createElement("form");
  composer.className = "annotation-composer viewer-image-annotation-composer";
  composer.setAttribute("aria-label", "Annotate image point");
  composer.innerHTML = annotationComposerMarkup();
  composer.addEventListener("click", (clickEvent) => clickEvent.stopPropagation());
  composer.querySelector(".annotation-cancel").addEventListener("click", closeAnnotationComposer);
  composer.addEventListener("submit", (submitEvent) => {
    submitEvent.preventDefault();
    const input = composer.querySelector(".annotation-input");
    const text = input.value.trim();
    if (!text) return input.focus();
    const annotationPoint = { x: point.x, y: point.y };
    const annotation = { id: `annotation-${crypto.randomUUID()}`, itemIds: [item.id], text, kind: "edit", point: annotationPoint };
    closeAnnotationComposer();
    const attach = async () => {
      const annotations = [...state.board.ui.annotations, annotation];
      try {
        await attachAnnotations(item, annotations);
        state.board.ui.annotations = annotations;
        markUiDirty();
        diagnostic("composer.annotation.attached", { itemId: item.id, annotationId: annotation.id, annotationCount: annotations.length });
        showToast("Added annotation to the composer");
      } catch (error) {
        diagnostic("composer.annotation.failed", { itemId: item.id, error: messageFor(error) }, "failure");
        showToast(messageFor(error));
      }
    };
    state.annotationQueue = state.annotationQueue.then(attach, attach);
  });
  document.body.append(composer);
  window.installPlatformIcons?.(composer);
  state.activeAnnotationComposer = composer;
  placeAnnotationComposer(composer, point);
  requestAnimationFrame(() => {
    if (state.activeAnnotationComposer === composer) placeAnnotationComposer(composer, point);
    composer.querySelector(".annotation-input").focus();
  });
}

function generationHandoff(brief, { title = "Generated image", count = 1, parentItemId = null } = {}) {
  const boardId = state.board.boardId;
  return [
    brief,
    "",
    "Creative Production board contract:",
    `- Reuse boardId ${boardId}. Do not call open and do not create another board.`,
    `- When image generation actually starts, call ${TOOL_NAME} with action=begin_generation and ${count} stable placeholder item${count === 1 ? "" : "s"}.`,
    `- Use title "${title}" for the first placeholder.${parentItemId ? ` Set parentItemId=${parentItemId}.` : ""}`,
    "- Generate the requested images with the selected image-generation route.",
    `- For every successful output, call ${TOOL_NAME} exactly once with action=complete_generation, the matching itemId, and the absolute generated imagePath.`,
    "- If generation fails, call fail_generation for that item. The task is incomplete if the image only appears in chat.",
    "- Do not pass image bytes or data URLs to the board tool; it imports the original file and creates a bounded preview.",
  ].join("\n");
}

async function sendFollowUp(prompt, files = []) {
  if (!bridge()?.sendFollowUpMessage) throw new Error("Follow-up messaging is unavailable");
  const content = [{ type: "text", text: prompt }];
  for (const file of files) {
    if (!file.type.startsWith("image/")) continue;
    content.push({ type: "image", data: await fileToBase64(file), mimeType: file.type });
  }
  await bridge().sendFollowUpMessage({ prompt, content });
}

async function attachItems(items) {
  const ready = items.filter((item) => state.previews.has(item.id));
  if (!ready.length) return;
  if (!bridge()?.updateModelContext) throw new Error("Composer context is unavailable");
  const content = [{ type: "text", text: `Creative Production board ${state.board.boardId}: ${ready.map((item) => item.title).join(", ")}` }];
  for (const item of ready) {
    const parsed = parseDataUrl(state.previews.get(item.id));
    content.push({ type: "image", data: parsed.data, mimeType: parsed.mimeType });
  }
  await bridge().updateModelContext({
    content,
    structuredContent: {
      kind: "creative-production-board-selection",
      boardId: state.board.boardId,
      revision: state.board.revision,
      items: ready.map((item) => ({ id: item.id, title: item.title, caption: item.caption, prompt: item.prompt })),
    },
  });
  diagnostic("composer.context.attached", { itemCount: ready.length });
  showToast(`${ready.length} image${ready.length === 1 ? "" : "s"} attached to the composer`);
}

async function exportItems(items, target = "finder") {
  if (!items.length) return;
  const names = items.map((item) => item.title).join(", ");
  await sendFollowUp(`Export these Creative Production board images to ${target}: ${names}. Board ID: ${state.board.boardId}. Use the preserved original assets from the board.`);
  diagnostic("export.handoff.accepted", { target, itemCount: items.length });
}

function selectedItems() {
  const selected = new Set(state.board?.ui.selectedItemIds || []);
  return visibleItems().filter((item) => selected.has(item.id));
}

function currentViewerItems() {
  return visibleItems().filter((item) => item.id === state.viewerItemId);
}

function toggleExportMenu(menu, trigger) {
  const open = menu.hidden;
  menu.hidden = !open;
  trigger.setAttribute("aria-expanded", String(open));
}

async function chooseExportTarget(target, items) {
  state.board.ui.exportTarget = target;
  markUiDirty();
  elements.exportMenu.hidden = true;
  elements.viewerExportMenu.hidden = true;
  await exportItems(items, target);
}

function showToast(message) {
  let toast = document.querySelector(".action-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "action-toast";
    document.body.append(toast);
  }
  toast.hidden = false;
  toast.textContent = message;
  requestAnimationFrame(() => toast.classList.add("is-visible"));
  window.setTimeout(() => toast.classList.remove("is-visible"), 2600);
}

function parseDataUrl(url) {
  const match = /^data:([^;]+);base64,(.*)$/.exec(url || "");
  if (!match) throw new Error("Image preview is unavailable");
  return { mimeType: match[1], data: match[2] };
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error);
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.readAsDataURL(file);
  });
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>\"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[character]);
}

function messageFor(error) {
  return error instanceof Error ? error.message : String(error || "Unknown error");
}

async function restoreFromHost(reason) {
  const payload = widgetDataFrom();
  if (payload) await applyWidgetData(payload);
  if (state.board?.boardId) await refreshBoard(reason);
}

function bindEvents() {
  document.querySelectorAll("[data-debug-origin]").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) state.diagnosticOrigins.add(input.dataset.debugOrigin);
      else state.diagnosticOrigins.delete(input.dataset.debugOrigin);
      renderDiagnostics();
    });
  });
  elements.selectionAttach.addEventListener("click", () => void attachItems(visibleItems().filter((item) => state.board.ui.selectedItemIds.includes(item.id))));
  elements.selectionDelete.addEventListener("click", () => void deleteItems([...state.board.ui.selectedItemIds]));
  elements.clearSelection.addEventListener("click", clearSelection);
  elements.exportPrimary.addEventListener("click", () => void exportItems(selectedItems(), state.board.ui.exportTarget));
  elements.exportMenuTrigger.addEventListener("click", () => toggleExportMenu(elements.exportMenu, elements.exportMenuTrigger));
  elements.exportMenu.querySelectorAll("[data-export-target]").forEach((button) => button.addEventListener("click", () => void chooseExportTarget(button.dataset.exportTarget, selectedItems())));
  elements.viewerClose.addEventListener("click", closeViewer);
  elements.viewerPrev.addEventListener("click", () => navigateViewer(-1));
  elements.viewerNext.addEventListener("click", () => navigateViewer(1));
  elements.attachImage.addEventListener("click", () => void attachItems(visibleItems().filter((item) => item.id === state.viewerItemId)));
  elements.remixImage.addEventListener("click", toggleRemixPanel);
  elements.viewerExportPrimary.addEventListener("click", () => void exportItems(currentViewerItems(), state.board.ui.exportTarget));
  elements.viewerExportMenuTrigger.addEventListener("click", () => toggleExportMenu(elements.viewerExportMenu, elements.viewerExportMenuTrigger));
  elements.viewerExportMenu.querySelectorAll("[data-export-target]").forEach((button) => button.addEventListener("click", () => void chooseExportTarget(button.dataset.exportTarget, currentViewerItems())));
  elements.viewerImage.addEventListener("click", addAnnotation);
  document.addEventListener("keydown", (event) => {
    if (!elements.viewer.classList.contains("active")) return;
    if (event.key === "Escape" && state.activeAnnotationComposer) return closeAnnotationComposer();
    if (event.key === "Escape") closeViewer();
    if (event.key === "ArrowLeft") navigateViewer(-1);
    if (event.key === "ArrowRight") navigateViewer(1);
  });
  window.addEventListener("resize", () => { closeAnnotationComposer(); renderBoard(); });
  window.addEventListener("pageshow", () => { void restoreFromHost("pageshow").catch(() => {}); });
  document.addEventListener("visibilitychange", () => {
    diagnostic("widget.visibility.changed", { visibility: document.visibilityState });
    if (!document.hidden) {
      void restoreFromHost("visibility").catch(() => {});
      void replayPendingDeletes();
      if (state.generationWatchDeadline || hasActiveGeneration()) startGenerationWatch(hasActiveGeneration());
      scheduleVisibleSync(250);
    }
  });
  window.addEventListener("openai:set_globals", () => { void applyWidgetData(widgetDataFrom()).catch(() => {}); });
}

async function init() {
  bindEvents();
  diagnostic("widget.mounted", { displayMode: window.openai?.displayMode || "unknown" });
  renderDiagnostics();
  const payload = widgetDataFrom();
  if (payload) await applyWidgetData(payload);
  window.setTimeout(() => {
    if (!state.board) diagnostic("widget.initial_payload.waiting", {}, "pending");
  }, 1_500);
}

void init();
