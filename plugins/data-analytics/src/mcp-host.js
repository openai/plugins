import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
} from "@modelcontextprotocol/ext-apps/app-with-deps";

function publishHostGlobals(globals) {
  window.openai = {
    ...(window.openai || {}),
    ...globals,
  };
  window.dispatchEvent(
    new CustomEvent("openai:set_globals", {
      detail: {
        globals: window.openai,
      },
    }),
  );
}

function displayModeDismissedKey(name, mode) {
  return `datascience-widget:${name}:dismissed-initial-${mode}`;
}

function hasDismissedInitialDisplayMode(name, mode) {
  try {
    return window.sessionStorage?.getItem(displayModeDismissedKey(name, mode)) === "1";
  } catch {
    return false;
  }
}

function rememberDismissedInitialDisplayMode(name, mode) {
  try {
    window.sessionStorage?.setItem(displayModeDismissedKey(name, mode), "1");
  } catch {
    // Storage can be unavailable in sandboxed previews.
  }
}

function clearDismissedInitialDisplayMode(name, mode) {
  try {
    window.sessionStorage?.removeItem(displayModeDismissedKey(name, mode));
  } catch {
    // Storage can be unavailable in sandboxed previews.
  }
}

function applyHostContext(context) {
  if (!context) return;
  if (context.theme) applyDocumentTheme(context.theme);
  if (context.styles?.variables) applyHostStyleVariables(context.styles.variables);
  if (context.styles?.css?.fonts) applyHostFonts(context.styles.css.fonts);

  publishHostGlobals({
    hostContext: context,
    displayMode: context.displayMode,
    availableDisplayModes: context.availableDisplayModes,
  });
}

function normalizeDisplayModeRequest(request) {
  if (typeof request === "string") return { mode: request };
  if (request && typeof request === "object") return request;
  return { mode: "inline" };
}

function normalizeDisplayMode(mode) {
  return mode === "inline" || mode === "fullscreen" || mode === "pip" ? mode : "";
}

async function requestInitialDisplayMode(app, name, mode) {
  const normalized = normalizeDisplayMode(mode);
  if (!normalized) return;
  if (hasDismissedInitialDisplayMode(name, normalized)) return;

  try {
    const result = await app.requestDisplayMode({ mode: normalized });
    publishHostGlobals({
      displayMode: normalizeDisplayMode(result?.mode || result?.displayMode) || normalized,
    });
  } catch {
    // Hosts may decline an app-start display request; the widget still renders inline.
  }
}

function installHostCompatibilityShim(app, name) {
  const existing = window.openai || {};
  window.openai = existing;

  if (typeof existing.requestDisplayMode !== "function") {
    existing.requestDisplayMode = async (request) => {
      const normalized = normalizeDisplayModeRequest(request);
      const result = await app.requestDisplayMode(normalized);
      const resultMode = normalizeDisplayMode(result?.mode || result?.displayMode || normalized.mode);
      if (resultMode === "fullscreen") {
        clearDismissedInitialDisplayMode(name, "fullscreen");
      }
      if (resultMode) publishHostGlobals({ displayMode: resultMode });
      return result;
    };
  }

  if (typeof existing.sendMessage !== "function") {
    let supportsMessages = false;
    try {
      supportsMessages = Boolean(app.getHostCapabilities()?.message?.text);
    } catch {
      supportsMessages = false;
    }
    if (supportsMessages) {
      existing.sendMessage = (message) => app.sendMessage(message);
    }
  }
}

export function connectMcpWidgetHost({
  name,
  version,
  availableDisplayModes = ["inline", "fullscreen"],
  initialDisplayMode,
}) {
  let lastDisplayMode = "";
  const app = new App(
    { name, version },
    { availableDisplayModes },
    { autoResize: true },
  );
  if (window.openai) {
    installHostCompatibilityShim(app, name);
  }

  app.addEventListener("hostcontextchanged", (context) => {
    const nextDisplayMode = normalizeDisplayMode(context?.displayMode);
    if (lastDisplayMode === "fullscreen" && nextDisplayMode === "inline") {
      rememberDismissedInitialDisplayMode(name, "fullscreen");
    }
    if (nextDisplayMode) lastDisplayMode = nextDisplayMode;
    applyHostContext(context);
  });

  app.addEventListener("toolresult", (result) => {
    const payload = result?.structuredContent || result;
    publishHostGlobals({ toolOutput: payload });
    window.dispatchEvent(
      new CustomEvent("datascience-widget-tool-result", {
        detail: payload,
      }),
    );
  });

  app.ready = app
    .connect()
    .then(() => {
      installHostCompatibilityShim(app, name);
      applyHostContext(app.getHostContext());
      return requestInitialDisplayMode(app, name, initialDisplayMode);
    })
    .catch(() => {
      // The static file preview uses the same bundle without an MCP Apps host.
    });

  return app;
}
