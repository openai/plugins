import { createRoot } from "react-dom/client";

import {
  ArtifactReader,
  PORTABLE_ARTIFACT_READER_ENVIRONMENT
} from "./analytics-app/App";
import "./styles/codex-theme.css";
import "./analytics-app/tokens.css";
import "./analytics-app/charting/chart-tokens.css";
import "./analytics-app/styles.css";
import "./analytics-app/tables/data-table.css";

declare global {
  interface Window {
    __DATA_ANALYTICS_PORTABLE_ARTIFACT__?: unknown;
  }
}

function portableArtifact(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const record = value as Record<string, unknown>;
  const nested = record.artifact_payload;
  if (nested && typeof nested === "object" && !Array.isArray(nested)) return nested;
  return record;
}

const rootElement = document.getElementById("data-analytics-portable-reader-root");
if (!rootElement) throw new Error("Missing portable artifact reader root element.");

const artifact = portableArtifact(window.__DATA_ANALYTICS_PORTABLE_ARTIFACT__);
if (!artifact) throw new Error("Missing embedded Data Analytics artifact payload.");

let readyDispatched = false;
function dispatchReady() {
  if (readyDispatched) return;
  readyDispatched = true;
  rootElement.dataset.readerReady = "true";
  window.dispatchEvent(new CustomEvent("data-analytics-portable-reader-ready"));
}

createRoot(rootElement).render(
  <ArtifactReader
    artifact={artifact}
    displayMode="fullscreen"
    environment={PORTABLE_ARTIFACT_READER_ENVIRONMENT}
    onReady={dispatchReady}
  />
);
