const grid = document.querySelector("#grid");
const tileTemplate = document.querySelector("#tileTemplate");
const anchorMedia = document.querySelector("#anchorMedia");
const title = document.querySelector("#title");
const anchorSummary = document.querySelector("#anchorSummary");
const stageLabel = document.querySelector("#stageLabel");
const metaGrid = document.querySelector("#metaGrid");
const exportJson = document.querySelector("#exportJson");
const exportMarkdown = document.querySelector("#exportMarkdown");
const viewer = document.querySelector("#viewer");
const viewerImage = document.querySelector("#viewerImage");
const viewerClose = document.querySelector("#viewerClose");
const RUN_TOKEN = window.BV_RUN_TOKEN || "";

let spec = null;
let state = {
  selectedId: null,
  rejectedIds: [],
  images: {}
};

function storageKey() {
  return `logo-explorer:${spec?.meta?.run_id || spec?.meta?.title || "default"}`;
}

async function fetchJson(path, fallback = null) {
  try {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return await response.json();
  } catch {
    return fallback;
  }
}

function saveLocalState() {
  localStorage.setItem(storageKey(), JSON.stringify(state));
}

function loadLocalState() {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey()) || "{}");
    state = {
      selectedId: stored.selectedId || state.selectedId,
      rejectedIds: Array.isArray(stored.rejectedIds) ? stored.rejectedIds : [],
      images: stored.images && typeof stored.images === "object" ? stored.images : {}
    };
  } catch {
    saveLocalState();
  }
}

function routeById(id) {
  return spec.routes.find((route) => route.id === id);
}

function selectedRoute() {
  return routeById(state.selectedId) || null;
}

function baseAssetUrl() {
  return spec?.meta?.base_asset_url || spec?.meta?.base_asset || "";
}

function fallbackSvg(label = "Logo anchor") {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
      <rect width="1000" height="1000" fill="#f4f1eb"/>
      <circle cx="300" cy="280" r="180" fill="#dfe9e2"/>
      <circle cx="710" cy="710" r="230" fill="#fbfbf7"/>
      <path d="M160 690 C310 520, 450 780, 600 560 S820 500, 870 650" fill="none" stroke="#245f4c" stroke-width="28" opacity="0.26"/>
      <rect x="245" y="310" width="510" height="390" rx="46" fill="#ffffff" opacity="0.78"/>
      <text x="500" y="525" text-anchor="middle" font-family="Arial, sans-serif" font-size="38" fill="#68645f">${label}</text>
    </svg>
  `;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function imageForRoute(route) {
  return state.images[route.id] || route.imageUrl || "";
}

function rejectedSet() {
  return new Set(state.rejectedIds);
}

function metaCard(label, value) {
  const card = document.createElement("div");
  card.className = "meta-card";
  const small = document.createElement("span");
  small.textContent = label;
  const strong = document.createElement("strong");
  strong.textContent = value || "None";
  card.append(small, strong);
  return card;
}

function renderMeta() {
  const selected = selectedRoute();
  const rejected = rejectedSet();
  metaGrid.innerHTML = "";
  metaGrid.append(
    metaCard("Anchor", spec.meta.anchor || spec.meta.title),
    metaCard("Selected", selected?.label || "None selected"),
    metaCard("Rejected", String(rejected.size)),
    metaCard("Next owner", selected?.final_owner || spec.handoff?.default_owner || "external-production-identity")
  );
}

function renderAnchor() {
  const selected = selectedRoute();
  const src = selected ? imageForRoute(selected) : baseAssetUrl();
  const label = selected?.label || spec.meta.anchor || "Logo anchor";
  anchorMedia.innerHTML = "";

  if (src) {
    const img = document.createElement("img");
    img.src = src;
    img.alt = "";
    img.addEventListener("click", () => openViewer(src));
    anchorMedia.appendChild(img);
  } else {
    const fallback = document.createElement("div");
    fallback.className = "anchor-fallback";
    fallback.textContent = label;
    anchorMedia.appendChild(fallback);
  }

  title.textContent = spec.meta.title || "Logo Explorer";
  stageLabel.textContent = spec.meta.stage || "Logo exploration";
  anchorSummary.textContent = selected
    ? selected.rationale || selected.prompt || ""
    : spec.meta.summary || "Select a logo concept to move the anchor toward that identity system.";
  renderMeta();
}

function renderGrid() {
  const rejected = rejectedSet();
  grid.innerHTML = "";

  spec.routes.forEach((route) => {
    const tile = tileTemplate.content.firstElementChild.cloneNode(true);
    const imageWrap = tile.querySelector(".image-wrap");
    const img = tile.querySelector("img");
    const reject = tile.querySelector(".reject");
    const retry = tile.querySelector(".retry");
    const label = tile.querySelector(".tile-copy strong");
    const detail = tile.querySelector(".tile-copy span");
    const routeImage = imageForRoute(route);

    tile.dataset.id = route.id;
    tile.classList.toggle("selected", state.selectedId === route.id);
    tile.classList.toggle("rejected", rejected.has(route.id));
    label.textContent = route.label || route.id;
    detail.textContent = route.usage_contexts?.length
      ? `${route.family || "logo"} | ${route.usage_contexts.join(", ")}`
      : route.family || route.rationale || "Logo concept";

    if (routeImage) {
      img.src = routeImage;
      imageWrap.classList.add("ready");
    }

    imageWrap.addEventListener("click", () => {
      const currentImage = imageForRoute(route);
      if (currentImage) openViewer(currentImage);
      state.selectedId = route.id;
      state.rejectedIds = state.rejectedIds.filter((id) => id !== route.id);
      saveAndRender();
    });

    reject.addEventListener("click", (event) => {
      event.stopPropagation();
      if (state.selectedId === route.id) state.selectedId = null;
      if (!rejected.has(route.id)) state.rejectedIds.push(route.id);
      saveAndRender();
    });

    retry.addEventListener("click", (event) => {
      event.stopPropagation();
      generateRoute(route, tile);
    });

    grid.appendChild(tile);
    if (!routeImage) generateRoute(route, tile);
  });
}

async function generateRoute(route, tile) {
  const imageWrap = tile.querySelector(".image-wrap");
  const img = tile.querySelector("img");
  imageWrap.classList.remove("failed", "ready");

  try {
    const response = await fetch("/api/image", {
      method: "POST",
      headers: { "content-type": "application/json", "x-bv-run-token": RUN_TOKEN },
      body: JSON.stringify({ route, confirmGenerate: true })
    });
    const payload = await response.json();
    if (!response.ok || payload.error) {
      throw new Error(payload.error || "Image generation failed.");
    }
    state.images[route.id] = payload.url;
    saveLocalState();
    img.src = payload.url;
    imageWrap.classList.add("ready");
    if (state.selectedId === route.id) renderAnchor();
  } catch (error) {
    imageWrap.classList.add("failed");
    tile.querySelector(".placeholder span").textContent = error.message || "Failed";
  }
}

async function persistFeedback() {
  try {
    await fetch("/api/feedback", {
      method: "POST",
      headers: { "content-type": "application/json", "x-bv-run-token": RUN_TOKEN },
      body: JSON.stringify(buildHandoff())
    });
  } catch {
    // Local download remains the fallback.
  }
}

function saveAndRender() {
  saveLocalState();
  renderAnchor();
  renderGrid();
  persistFeedback();
}

function buildHandoff() {
  const selected = selectedRoute();
  const rejected = rejectedSet();
  return {
    meta: spec.meta,
    selected_logo_route: selected
      ? {
          ...selected,
          imageUrl: imageForRoute(selected) || null
        }
      : null,
    rejected_directions: spec.routes
      .filter((route) => rejected.has(route.id))
      .map((route) => ({ id: route.id, label: route.label, family: route.family })),
    logo_route_metadata: {
      preserve: spec.constraints?.preserve || [],
      avoid: spec.constraints?.avoid || [],
      next_prompt_hints: selected?.next_prompt_hints || spec.handoff?.next_prompt_hints || []
    },
    final_owner: selected?.final_owner || spec.handoff?.default_owner || "external-production-identity"
  };
}

function handoffMarkdown() {
  const handoff = buildHandoff();
  const selected = handoff.selected_logo_route;
  const rejected = handoff.rejected_directions;
  return [
    `# ${handoff.meta.title || "Logo Explorer Handoff"}`,
    "",
    `Anchor: ${handoff.meta.anchor || "unspecified"}`,
    `Final owner: ${handoff.final_owner}`,
    "",
    "## Selected Logo Route",
    selected ? `- ${selected.label || selected.id}: ${selected.rationale || selected.prompt || ""}` : "- None selected",
    "",
    "## Rejected Directions",
    rejected.length ? rejected.map((item) => `- ${item.label || item.id}`).join("\n") : "- None",
    "",
    "## Preserve",
    (handoff.logo_route_metadata.preserve || []).map((item) => `- ${item}`).join("\n") || "- None specified",
    "",
    "## Avoid",
    (handoff.logo_route_metadata.avoid || []).map((item) => `- ${item}`).join("\n") || "- None specified",
    ""
  ].join("\n");
}

function download(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function openViewer(src) {
  viewerImage.src = src;
  viewer.classList.add("active");
  viewer.setAttribute("aria-hidden", "false");
}

function closeViewer() {
  viewer.classList.remove("active");
  viewer.setAttribute("aria-hidden", "true");
  viewerImage.removeAttribute("src");
}

viewerClose.addEventListener("click", closeViewer);
viewer.addEventListener("click", (event) => {
  if (event.target === viewer) closeViewer();
});

exportJson.addEventListener("click", () => {
  const content = JSON.stringify(buildHandoff(), null, 2);
  download("selected-logo-route.json", content, "application/json");
  persistFeedback();
});

exportMarkdown.addEventListener("click", () => {
  download("handoff.md", handoffMarkdown(), "text/markdown");
  persistFeedback();
});

async function boot() {
  spec = await fetchJson("/api/spec");
  if (!spec) {
    document.body.textContent = "Missing logo spec.";
    return;
  }
  spec.routes = Array.isArray(spec.routes) ? spec.routes : [];
  state.selectedId = spec.initial_selected_id || null;
  loadLocalState();
  renderAnchor();
  renderGrid();
}

boot();
