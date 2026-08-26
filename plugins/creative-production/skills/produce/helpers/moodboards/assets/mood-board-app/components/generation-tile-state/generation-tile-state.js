const GENERATION_HALFTONE_BASE_DURATIONS = {
  offsetX1: 4500,
  offsetY1: 6330,
  offsetX2: 5600,
  offsetY2: 5750,
  dotSize: 2250,
  radialSize1: 3600,
  radialSize2: 2400,
};
const GENERATION_HALFTONE_SLOWDOWN = 1.2;
const GENERATION_HALFTONE_SPACING_PX = 27;
const GENERATION_HALFTONE_MAX_SIZE_SCALE = 1.35;
const GENERATION_HALFTONE_RADIAL_SIZE_SCALE = 0.78;
const GENERATION_HALFTONE_VISIBILITY_THRESHOLD = 0.03;
const GENERATION_HALFTONE_MIN_SIZE_PX = 0.55;

function clamp01(value) {
  return Math.min(1, Math.max(0, value));
}
function smoothstep(edge0, edge1, value) {
  const time = clamp01((value - edge0) / (edge1 - edge0));
  return time * time * (3 - 2 * time);
}

function pingPong(time) {
  const fraction = time % 1;
  return fraction <= 0.5 ? fraction * 2 : 2 - fraction * 2;
}

function easeInOut(time) {
  return time * time * (3 - 2 * time);
}

function fastOutSlowIn(time) {
  return time < 0.5
    ? 4 * time * time * time
    : 1 - Math.pow(-2 * time + 2, 3) / 2;
}

function lerp(start, end, time) {
  return start + (end - start) * time;
}

function randomBetween(min, max) {
  return min + Math.random() * (max - min);
}

function randomizedValues() {
  const duration = (baseMs) => baseMs * GENERATION_HALFTONE_SLOWDOWN * randomBetween(1, 1.35);
  return {
    durations: Object.fromEntries(
      Object.entries(GENERATION_HALFTONE_BASE_DURATIONS).map(([key, value]) => [key, duration(value)]),
    ),
    phases: {
      offsetX1: Math.random(),
      offsetY1: Math.random(),
      offsetX2: Math.random(),
      offsetY2: Math.random(),
      dotSize: Math.random(),
      radialSize1: Math.random(),
      radialSize2: Math.random(),
    },
    bounds: {
      x1Start: randomBetween(0.1, 0.32),
      x1End: randomBetween(0.68, 0.9),
      y1Start: randomBetween(0.1, 0.32),
      y1End: randomBetween(0.68, 0.9),
      x2Start: randomBetween(0.68, 0.9),
      x2End: randomBetween(0.1, 0.32),
      y2Start: randomBetween(0.68, 0.9),
      y2End: randomBetween(0.1, 0.32),
    },
    dotSizeRange: {
      start: randomBetween(0.08, 0.11),
      end: randomBetween(0.2, 0.25),
    },
    radialSizeRange: {
      r1Start: randomBetween(0.42, 0.52),
      r1End: randomBetween(0.62, 0.75),
      r2Start: randomBetween(0.5, 0.62),
      r2End: randomBetween(0.74, 0.9),
    },
  };
}

function updateLayout(record) {
  const rect = record.container.getBoundingClientRect();
  const width = Math.max(0, Math.floor(rect.width));
  const height = Math.max(0, Math.floor(rect.height));
  if (width === 0 || height === 0) {
    record.layout = null;
    record.needsLayoutUpdate = false;
    return;
  }

  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const deviceWidth = Math.floor(width * dpr);
  const deviceHeight = Math.floor(height * dpr);
  if (record.canvas.width !== deviceWidth || record.canvas.height !== deviceHeight) {
    record.canvas.width = deviceWidth;
    record.canvas.height = deviceHeight;
  }

  const spacingCss = Math.max(1, GENERATION_HALFTONE_SPACING_PX / dpr);
  const columns = Math.max(1, Math.floor(width / spacingCss));
  const rows = Math.max(1, Math.floor(height / spacingCss));
  const gridWidth = (columns - 1) * spacingCss;
  const gridHeight = (rows - 1) * spacingCss;
  const startX = (width - gridWidth) * 0.5;
  const startY = (height - gridHeight) * 0.5;
  const xPositions = new Float32Array(columns);
  const yPositions = new Float32Array(rows);
  const xNormals = new Float32Array(columns);
  const yNormals = new Float32Array(rows);

  for (let column = 0; column < columns; column += 1) {
    xPositions[column] = startX + column * spacingCss;
    xNormals[column] = columns === 1 ? 0.5 : column / (columns - 1);
  }
  for (let row = 0; row < rows; row += 1) {
    yPositions[row] = startY + row * spacingCss;
    yNormals[row] = rows === 1 ? 0.5 : row / (rows - 1);
  }

  record.layout = {
    width,
    height,
    dpr,
    spacingCss,
    columns,
    rows,
    xPositions,
    yPositions,
    xNormals,
    yNormals,
    color: getComputedStyle(record.container).color || "rgba(0, 0, 0, 0.12)",
  };
  record.needsLayoutUpdate = false;
}

function draw(record, now) {
  if (record.start === 0) record.start = now;
  const elapsed = now - record.start;
  if (record.needsLayoutUpdate || !record.layout) updateLayout(record);
  if (!record.layout) return;

  const progress = (duration, phase) => pingPong((elapsed / duration + phase) % 1);
  const { randomized, layout, context } = record;
  const offsetX1 = lerp(
    randomized.bounds.x1Start,
    randomized.bounds.x1End,
    fastOutSlowIn(progress(randomized.durations.offsetX1, randomized.phases.offsetX1)),
  );
  const offsetY1 = lerp(
    randomized.bounds.y1Start,
    randomized.bounds.y1End,
    easeInOut(progress(randomized.durations.offsetY1, randomized.phases.offsetY1)),
  );
  const offsetX2 = lerp(
    randomized.bounds.x2Start,
    randomized.bounds.x2End,
    fastOutSlowIn(progress(randomized.durations.offsetX2, randomized.phases.offsetX2)),
  );
  const offsetY2 = lerp(
    randomized.bounds.y2Start,
    randomized.bounds.y2End,
    easeInOut(progress(randomized.durations.offsetY2, randomized.phases.offsetY2)),
  );
  const radialSize1 = GENERATION_HALFTONE_RADIAL_SIZE_SCALE * lerp(
    randomized.radialSizeRange.r1Start,
    randomized.radialSizeRange.r1End,
    easeInOut(progress(randomized.durations.radialSize1, randomized.phases.radialSize1)),
  );
  const radialSize2 = GENERATION_HALFTONE_RADIAL_SIZE_SCALE * lerp(
    randomized.radialSizeRange.r2Start,
    randomized.radialSizeRange.r2End,
    easeInOut(progress(randomized.durations.radialSize2, randomized.phases.radialSize2)),
  );
  const dotSizeScale = lerp(
    randomized.dotSizeRange.start,
    randomized.dotSizeRange.end,
    easeInOut(progress(randomized.durations.dotSize, randomized.phases.dotSize)),
  );

  context.save();
  context.setTransform(layout.dpr, 0, 0, layout.dpr, 0, 0);
  context.clearRect(0, 0, layout.width, layout.height);
  context.fillStyle = layout.color;
  context.beginPath();

  for (let row = 0; row < layout.rows; row += 1) {
    const y = layout.yPositions[row];
    const yNormal = layout.yNormals[row];
    for (let column = 0; column < layout.columns; column += 1) {
      const x = layout.xPositions[column];
      const xNormal = layout.xNormals[column];
      const distance1 = Math.hypot(xNormal - offsetX1, yNormal - offsetY1);
      const distance2 = Math.hypot(xNormal - offsetX2, yNormal - offsetY2);
      const radial1 = 1 - smoothstep(0, radialSize1, distance1);
      const radial2 = 1 - smoothstep(0, radialSize2, distance2);
      const intensity = Math.pow(clamp01(radial1 * 1.2 + radial2 * 0.82), 1.18);
      if (intensity <= GENERATION_HALFTONE_VISIBILITY_THRESHOLD) continue;

      const radius = Math.max(
        GENERATION_HALFTONE_MIN_SIZE_PX,
        layout.spacingCss * 0.5 * GENERATION_HALFTONE_MAX_SIZE_SCALE * intensity * dotSizeScale,
      );
      context.moveTo(x + radius, y);
      context.arc(x, y, radius, 0, Math.PI * 2);
    }
  }

  context.fill();
  context.restore();
}

export function createGenerationTileState({
  state = "waiting",
  label = "Couldn’t generate",
  reducedMotion = false,
} = {}) {
  const root = document.createElement("figure");
  root.className = "cp-generation-tile";
  root.innerHTML = `
    <span class="cp-generation-tile__pulse" aria-hidden="true">
      <canvas class="cp-generation-tile__canvas"></canvas>
    </span>
    <span class="cp-generation-tile__failure"></span>
  `;
  const canvas = root.querySelector("canvas");
  const failure = root.querySelector(".cp-generation-tile__failure");
  const context = canvas.getContext("2d");
  let frame = 0;
  let currentState = "waiting";
  const record = {
    canvas,
    container: canvas.parentElement,
    context,
    randomized: randomizedValues(),
    layout: null,
    needsLayoutUpdate: true,
    start: 0,
  };
  const observer = new ResizeObserver(() => {
    record.needsLayoutUpdate = true;
    schedule();
  });
  observer.observe(record.container);

  function render(now) {
    frame = 0;
    if (!context || !root.isConnected || currentState !== "waiting") return;
    draw(record, now);
    if (!reducedMotion) schedule();
  }

  function schedule() {
    if (!frame && currentState === "waiting") frame = requestAnimationFrame(render);
  }

  function setState(nextState) {
    currentState = nextState === "failed" ? "failed" : "waiting";
    root.dataset.state = currentState;
    root.setAttribute("aria-label", currentState === "failed" ? label : "Generating image");
    failure.textContent = label;
    if (currentState === "waiting") schedule();
  }

  setState(state);

  return {
    element: root,
    setState,
    restart() {
      record.start = 0;
      record.randomized = randomizedValues();
      schedule();
    },
    destroy() {
      if (frame) cancelAnimationFrame(frame);
      observer.disconnect();
      root.remove();
    },
  };
}

export function mountGenerationTileState(container, options = {}) {
  if (!(container instanceof Element)) {
    throw new TypeError("mountGenerationTileState requires a DOM element container.");
  }
  const component = createGenerationTileState(options);
  container.replaceChildren(component.element);
  component.restart();
  return component;
}
