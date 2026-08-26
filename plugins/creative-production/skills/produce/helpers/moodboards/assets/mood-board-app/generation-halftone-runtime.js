(() => {
  const states = new Map();
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let frame = 0;

  function resize(state) {
    const rect = state.container.getBoundingClientRect();
    const width = Math.max(0, Math.floor(rect.width));
    const height = Math.max(0, Math.floor(rect.height));
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    if (!width || !height) return null;
    if (state.canvas.width !== Math.floor(width * dpr) || state.canvas.height !== Math.floor(height * dpr)) {
      state.canvas.width = Math.floor(width * dpr);
      state.canvas.height = Math.floor(height * dpr);
    }
    return { width, height, dpr };
  }

  function draw(state, now) {
    const layout = resize(state);
    if (!layout) return;
    const { context } = state;
    const spacing = 27 / layout.dpr;
    const columns = Math.max(1, Math.floor(layout.width / spacing));
    const rows = Math.max(1, Math.floor(layout.height / spacing));
    const elapsed = (now - state.startedAt) / 1000;
    const first = {
      x: 0.5 + Math.sin(elapsed * 0.72 + state.phase) * 0.28,
      y: 0.5 + Math.cos(elapsed * 0.53 + state.phase) * 0.3,
    };
    const second = {
      x: 0.5 + Math.cos(elapsed * 0.61 + state.phase * 1.7) * 0.32,
      y: 0.5 + Math.sin(elapsed * 0.47 + state.phase * 1.3) * 0.27,
    };

    context.save();
    context.setTransform(layout.dpr, 0, 0, layout.dpr, 0, 0);
    context.clearRect(0, 0, layout.width, layout.height);
    context.fillStyle = getComputedStyle(state.container).color || "rgba(0, 0, 0, 0.12)";
    context.beginPath();
    for (let row = 0; row < rows; row += 1) {
      const y = rows === 1 ? 0.5 : row / (rows - 1);
      for (let column = 0; column < columns; column += 1) {
        const x = columns === 1 ? 0.5 : column / (columns - 1);
        const a = Math.max(0, 1 - Math.hypot(x - first.x, y - first.y) / 0.58);
        const b = Math.max(0, 1 - Math.hypot(x - second.x, y - second.y) / 0.68);
        const intensity = Math.min(1, a * 0.9 + b * 0.7);
        if (intensity < 0.04) continue;
        const radius = Math.max(0.55, spacing * 0.18 * intensity);
        const px = (column + 0.5) * (layout.width / columns);
        const py = (row + 0.5) * (layout.height / rows);
        context.moveTo(px + radius, py);
        context.arc(px, py, radius, 0, Math.PI * 2);
      }
    }
    context.fill();
    context.restore();
  }

  function render(now) {
    frame = 0;
    for (const [canvas, state] of states) {
      if (!canvas.isConnected) {
        state.observer?.disconnect();
        states.delete(canvas);
        continue;
      }
      draw(state, now);
    }
    if (states.size && !reducedMotion.matches) schedule();
  }

  function schedule() {
    if (!frame) frame = window.requestAnimationFrame(render);
  }

  function installGenerationHalftone(canvas) {
    if (!(canvas instanceof HTMLCanvasElement) || states.has(canvas)) return;
    const container = canvas.parentElement;
    const context = canvas.getContext("2d");
    if (!container || !context) return;
    const state = {
      canvas,
      container,
      context,
      phase: Math.random() * Math.PI * 2,
      startedAt: performance.now(),
      observer: null,
    };
    state.observer = typeof ResizeObserver === "function" ? new ResizeObserver(schedule) : null;
    state.observer?.observe(container);
    states.set(canvas, state);
    draw(state, state.startedAt);
    schedule();
  }

  function removeGenerationHalftone(canvas) {
    const state = states.get(canvas);
    if (!state) return;
    state.observer?.disconnect();
    states.delete(canvas);
    state.context.clearRect(0, 0, canvas.width, canvas.height);
  }

  window.installGenerationHalftone = installGenerationHalftone;
  window.removeGenerationHalftone = removeGenerationHalftone;
})();
