import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import "../styles/codex-theme.css";
import "./tokens.css";
import "./charting/chart-tokens.css";
import "./styles.css";
import "./tables/data-table.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Missing root element");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>
);
