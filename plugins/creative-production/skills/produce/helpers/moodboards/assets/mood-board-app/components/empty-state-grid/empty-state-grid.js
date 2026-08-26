export const EMPTY_STATE_GRID_STARTERS = Object.freeze([
  {
    id: "make-logo-from-scratch",
    title: "Explore logo ideas",
    aspectRatio: "3 / 2",
    image: "bg-make-logo-from-scratch-01.webp",
    scrimRgb: "40 34 38",
  },
  {
    id: "social-ads",
    title: "Come up with social ads",
    aspectRatio: "10 / 11",
    image: "bg-social-ads-01.webp",
    scrimRgb: "57 28 26",
  },
  {
    id: "place-product",
    title: "Place a product in a scene",
    aspectRatio: "3 / 2",
    image: "bg-place-product-01.webp",
    scrimRgb: "49 42 34",
  },
  {
    id: "product-detail-images",
    title: "Create product shots",
    aspectRatio: "3 / 4",
    image: "bg-product-detail-images-01.webp",
    scrimRgb: "122 159 153",
  },
  {
    id: "campaign-ideas",
    title: "Brainstorm ideas for a campaign",
    aspectRatio: "3 / 4",
    image: "bg-campaign-ideas-01.webp",
    scrimRgb: "198 43 105",
  },
  {
    id: "template-assets",
    title: "Create assets for every channel",
    aspectRatio: "3 / 2",
    image: "bg-template-assets-01.webp",
    scrimRgb: "223 137 69",
  },
  {
    id: "social-post-series",
    title: "Create a social carousel",
    aspectRatio: "10 / 11",
    image: "bg-social-post-series-01.webp",
    scrimRgb: "38 82 168",
  },
  {
    id: "place-in-screen",
    title: "Place in a screen",
    aspectRatio: "10 / 11",
    image: "bg-place-in-screen-01.webp",
    scrimRgb: "63 29 7",
  },
  {
    id: "images-in-a-style",
    title: "Create multiple variations from a template",
    aspectRatio: "3 / 4",
    image: "bg-images-in-a-style-01.webp",
    scrimRgb: "178 158 157",
  },
]);

const STARTER_ORDER_IDS = Object.freeze([
  "make-logo-from-scratch",
  "social-ads",
  "campaign-ideas",
  "product-detail-images",
  "template-assets",
  "place-in-screen",
  "social-post-series",
  "images-in-a-style",
  "place-product",
]);

const DEFAULT_ASSET_BASE_URL = new URL(/* @vite-ignore */ "./assets/", import.meta.url);

export function emptyStateGridColumnCountForWidth(width) {
  if (!Number.isFinite(width) || width <= 0) return 3;
  if (width <= 360) return 1;
  if (width <= 600) return 2;
  return 3;
}

function starterOrderIdsFor(starters) {
  const availableIds = new Set(starters.map((starter) => starter.id));
  const orderedIds = STARTER_ORDER_IDS.filter((starterId) => availableIds.has(starterId));
  starters.forEach((starter) => {
    if (!orderedIds.includes(starter.id)) orderedIds.push(starter.id);
  });
  return orderedIds;
}

function aspectRatioHeight(aspectRatio) {
  const [width, height] = String(aspectRatio || "1 / 1").split("/").map((part) => Number(part.trim()));
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) return 1;
  return height / width;
}

function starterColumnsFor(starterIds, columnCount, starterMap) {
  if (columnCount <= 1) return [starterIds];

  const columns = Array.from({ length: columnCount }, () => []);
  const columnHeights = Array.from({ length: columnCount }, () => 0);
  const starterHeights = starterIds.map((starterId) => aspectRatioHeight(starterMap.get(starterId)?.aspectRatio));
  const gapHeight = 0.03;
  let bestColumns = null;
  let bestScore = Number.POSITIVE_INFINITY;

  function scoreColumns() {
    const maxHeight = Math.max(...columnHeights);
    const minHeight = Math.min(...columnHeights);
    const counts = columns.map((column) => column.length);
    return (maxHeight - minHeight) + ((Math.max(...counts) - Math.min(...counts)) * 0.001);
  }

  function assign(index) {
    if (index >= starterIds.length) {
      const score = scoreColumns();
      if (score < bestScore) {
        bestScore = score;
        bestColumns = columns.map((column) => [...column]);
      }
      return;
    }

    for (let columnIndex = 0; columnIndex < columnCount; columnIndex += 1) {
      const addedHeight = starterHeights[index] + (columns[columnIndex].length > 0 ? gapHeight : 0);
      columns[columnIndex].push(starterIds[index]);
      columnHeights[columnIndex] += addedHeight;
      assign(index + 1);
      columnHeights[columnIndex] -= addedHeight;
      columns[columnIndex].pop();
    }
  }

  assign(0);
  return bestColumns || columns;
}

export function createEmptyStateGrid({
  starters = EMPTY_STATE_GRID_STARTERS,
  assetBaseUrl = DEFAULT_ASSET_BASE_URL,
  assetUrlForStarter,
  onSelect,
  width,
} = {}) {
  const starterMap = new Map(starters.map((starter) => [starter.id, starter]));
  const starterIds = starterOrderIdsFor(starters);
  const starterCards = new Map(
    starterIds.map((starterId) => {
      const starter = starterMap.get(starterId);
      return [starterId, createStarterCard(starter, assetBaseUrl, assetUrlForStarter, onSelect)];
    }),
  );
  const root = document.createElement("section");
  root.className = "cp-empty-state-grid";
  root.setAttribute("aria-label", "Start a new mood board");

  const grid = document.createElement("div");
  grid.className = "cp-empty-state-grid__grid";
  let renderedColumnCount = 0;

  root.append(grid);

  function renderColumns(columnCount) {
    const normalizedColumnCount = [1, 2, 3].includes(columnCount) ? columnCount : 3;
    if (normalizedColumnCount === renderedColumnCount) return;
    renderedColumnCount = normalizedColumnCount;
    root.dataset.starterColumns = String(normalizedColumnCount);
    grid.style.setProperty("--cp-starter-columns", String(normalizedColumnCount));
    grid.replaceChildren(
      ...starterColumnsFor(starterIds, normalizedColumnCount, starterMap).map((columnStarterIds) => {
        const column = document.createElement("div");
        column.className = "cp-empty-state-grid__column";
        columnStarterIds.forEach((starterId) => column.append(starterCards.get(starterId)));
        return column;
      }),
    );
  }

  function updateLayout(nextWidth = width ?? root.getBoundingClientRect().width) {
    renderColumns(emptyStateGridColumnCountForWidth(nextWidth));
  }

  updateLayout(width);

  return { element: root, updateLayout };
}

export function mountEmptyStateGrid(container, options = {}) {
  if (!(container instanceof Element)) {
    throw new TypeError("mountEmptyStateGrid requires a DOM element container.");
  }

  const { observeResize = true, ...componentOptions } = options;
  const component = createEmptyStateGrid(componentOptions);
  container.replaceChildren(component.element);

  const resizeObserver = observeResize && typeof ResizeObserver === "function"
    ? new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect?.width;
      component.updateLayout(width);
    })
    : null;
  resizeObserver?.observe(container);

  return {
    ...component,
    destroy() {
      resizeObserver?.disconnect();
      component.element.remove();
    },
  };
}

function createStarterCard(starter, assetBaseUrl, assetUrlForStarter, onSelect) {
  const button = document.createElement("button");
  button.className = "cp-empty-state-grid__card";
  button.type = "button";
  button.dataset.starterId = starter.id;
  button.style.setProperty("--cp-starter-aspect-ratio", starter.aspectRatio);
  button.style.setProperty("--cp-starter-scrim-rgb", starter.scrimRgb);
  button.style.setProperty(
    "--cp-starter-image",
    cssImageUrl(assetUrlForStarter?.(starter) || new URL(starter.image, assetBaseUrl).href),
  );

  const label = document.createElement("span");
  label.className = "cp-empty-state-grid__label";
  label.append(
    blurLayer("soft"),
    blurLayer("medium"),
    blurLayer("strong"),
  );

  const title = document.createElement("strong");
  title.textContent = starter.title;
  label.append(title);
  button.append(label);
  button.addEventListener("click", () => onSelect?.(starter));
  return button;
}

function blurLayer(strength) {
  const layer = document.createElement("span");
  layer.className = `cp-empty-state-grid__blur cp-empty-state-grid__blur--${strength}`;
  layer.setAttribute("aria-hidden", "true");
  return layer;
}

function cssImageUrl(value) {
  const url = String(value).replace(/"/g, "%22");
  return `url("${url}")`;
}

if (typeof window !== "undefined") {
  window.mountEmptyStateGrid = mountEmptyStateGrid;
}
