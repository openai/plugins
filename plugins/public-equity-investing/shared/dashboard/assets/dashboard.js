const SOURCE_DATA = __SOURCE_DATA__;
const tabButtons = document.querySelectorAll(".tab-button");
const panels = document.querySelectorAll(".tab-panel");
const tocLinks = document.querySelectorAll(".toc-link");
const printButtons = document.querySelectorAll("[data-print-dashboard]");

printButtons.forEach((button) => {
  button.addEventListener("click", () => window.print());
});

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;
    tabButtons.forEach((item) => {
      const active = item === button;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-selected", String(active));
    });
    panels.forEach((panel) => {
      panel.classList.toggle("is-active", panel.id === target);
    });
  });
});

tocLinks.forEach((link) => {
  link.addEventListener("click", () => {
    tocLinks.forEach((item) => item.classList.toggle("is-active", item === link));
  });
});

if (tocLinks.length > 0 && "IntersectionObserver" in window) {
  const sections = Array.from(document.querySelectorAll(".dashboard-section"));
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) {
        return;
      }
      tocLinks.forEach((link) => {
        link.classList.toggle("is-active", link.getAttribute("href") === `#${visible.target.id}`);
      });
    },
    {rootMargin: "-18% 0px -70% 0px", threshold: [0.1, 0.35, 0.6]}
  );
  sections.forEach((section) => observer.observe(section));
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function reportCopyText() {
  const root = document.querySelector("[data-report-copy-root]") || document.querySelector("main");
  if (!root) return "";
  const clone = root.cloneNode(true);
  clone.querySelectorAll(".toc-list, .tab-list, #sources, [data-report-copy-exclude], .citation-popover, .dashboard-utility-bar, .table-action-bar").forEach((node) => node.remove());
  clone.querySelectorAll(".citation-badge, .citation-chip, .citation-link, .source-id").forEach((node) => {
    const label = (node.innerText || node.textContent || "").trim();
    node.replaceWith(document.createTextNode(label ? ` ${label}` : ""));
  });
  return clone.innerText.replace(/\n{3,}/g, "\n\n").trim();
}

function fallbackCopy(text) {
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.left = "-9999px";
  document.body.appendChild(area);
  area.select();
  const ok = document.execCommand("copy");
  area.remove();
  if (!ok) {
    return Promise.reject(new Error("Clipboard fallback failed"));
  }
  return Promise.resolve(true);
}

function writeClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
  }
  return fallbackCopy(text);
}

function markCopied(button) {
  const original = button.getAttribute("data-label-original") || button.textContent || "Copy";
  button.setAttribute("data-label-original", original);
  button.classList.add("is-copied");
  button.textContent = "Copied";
  window.setTimeout(() => {
    button.classList.remove("is-copied");
    button.textContent = original;
  }, 1300);
}

document.addEventListener("click", (event) => {
  const fullReportButton = event.target.closest("[data-copy-full-report]");
  if (!fullReportButton) return;
  const text = reportCopyText();
  if (!text) return;
  writeClipboard(text)
    .then(() => markCopied(fullReportButton))
    .catch(() => fullReportButton.classList.add("copy-failed"));
});

let citationPopover;
let citationHideTimer;
const CITATION_SELECTOR = ".citation-chip[data-citation-id], .citation-chip[data-citation-title], .citation-link[data-citation-id], .citation-link[data-citation-title]";

function citationField(label, value) {
  if (!value) return "";
  return `<div class="citation-popover-label">${escapeHtml(label)}</div><div class="citation-popover-value">${escapeHtml(value)}</div>`;
}

function ensureCitationPopover() {
  if (citationPopover) return citationPopover;
  citationPopover = document.createElement("div");
  citationPopover.className = "citation-popover";
  citationPopover.id = "citation-popover";
  citationPopover.setAttribute("role", "tooltip");
  document.body.appendChild(citationPopover);
  return citationPopover;
}

function sourceFromChip(chip) {
  const id = chip?.getAttribute("data-citation-id");
  if (id && SOURCE_DATA[id]) return SOURCE_DATA[id];
  const title = chip?.getAttribute("data-citation-title");
  if (!title) return null;
  return {
    id: id || "source",
    title,
    type: "External source",
    status: "",
    date: chip.getAttribute("data-citation-date") || "",
    detail: chip.getAttribute("data-citation-detail") || "",
  };
}

function positionCitationPopover(popover, chip) {
  const rect = chip.getBoundingClientRect();
  const popRect = popover.getBoundingClientRect();
  const margin = 12;
  let left = rect.left + rect.width / 2 - popRect.width / 2;
  left = Math.max(margin, Math.min(left, window.innerWidth - popRect.width - margin));
  let top = rect.bottom + 8;
  if (top + popRect.height > window.innerHeight - margin) {
    top = rect.top - popRect.height - 8;
  }
  if (top < margin) top = margin;
  popover.style.left = `${left}px`;
  popover.style.top = `${top}px`;
}

function showCitationPopover(chip) {
  const source = sourceFromChip(chip);
  if (!source) return;
  window.clearTimeout(citationHideTimer);
  const popover = ensureCitationPopover();
  popover.innerHTML = `
    <div class="citation-popover-title"><span class="citation-popover-id">${escapeHtml(source.id || "source")}</span>${escapeHtml(source.title || "Source")}</div>
    <div class="citation-popover-grid">
      ${citationField("Type", source.type)}
      ${citationField("Status", source.status)}
      ${citationField("Date", source.date)}
      ${citationField("Pinpoint", source.detail)}
    </div>
    <div class="citation-popover-note">Click the citation to jump to the source ledger or open the source in a new window.</div>
  `;
  chip.setAttribute("aria-describedby", "citation-popover");
  popover.classList.add("show");
  positionCitationPopover(popover, chip);
}

function hideCitationPopover(delay = 100) {
  window.clearTimeout(citationHideTimer);
  citationHideTimer = window.setTimeout(() => {
    document.querySelectorAll("[aria-describedby='citation-popover']").forEach((node) => node.removeAttribute("aria-describedby"));
    if (citationPopover) citationPopover.classList.remove("show");
  }, delay);
}

window.addEventListener("resize", () => hideCitationPopover(0));
window.addEventListener("scroll", () => hideCitationPopover(0), true);
document.addEventListener("mouseover", (event) => {
  const chip = event.target.closest(CITATION_SELECTOR);
  if (chip) showCitationPopover(chip);
});
document.addEventListener("mouseout", (event) => {
  const chip = event.target.closest(CITATION_SELECTOR);
  if (chip) hideCitationPopover();
});
document.addEventListener("focusin", (event) => {
  const chip = event.target.closest(CITATION_SELECTOR);
  if (chip) showCitationPopover(chip);
});
document.addEventListener("focusout", (event) => {
  const chip = event.target.closest(CITATION_SELECTOR);
  if (chip) hideCitationPopover();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") hideCitationPopover(0);
});
