(() => {
  const root = document.documentElement;
  const colorScheme = window.matchMedia?.("(prefers-color-scheme: dark)");
  const themeKeys = ["theme", "colorScheme", "colorMode", "mode", "appearance", "resolvedTheme", "name"];

  function normalizeTheme(value) {
    if (!value) return "";
    if (typeof value === "string") {
      const normalized = value.toLowerCase();
      if (normalized.includes("dark")) return "dark";
      if (normalized.includes("light")) return "light";
      return "";
    }
    if (typeof value !== "object") return "";
    for (const key of themeKeys) {
      const theme = normalizeTheme(value[key]);
      if (theme) return theme;
    }
    return "";
  }

  function hostTheme() {
    const openai = window.openai || {};
    const variables = openai.hostContext?.styles?.variables || {};
    return (
      normalizeTheme(openai.hostContext?.theme) ||
      normalizeTheme(openai.theme) ||
      normalizeTheme(openai.hostContext?.colorScheme) ||
      normalizeTheme(openai.hostContext?.colorMode) ||
      normalizeTheme(variables["color-scheme"]) ||
      normalizeTheme(variables["--color-scheme"])
    );
  }

  function currentTheme() {
    const previewTheme = normalizeTheme(new URLSearchParams(window.location.search).get("theme"));
    if (previewTheme) return previewTheme;
    const detectedHostTheme = hostTheme();
    if (detectedHostTheme) return detectedHostTheme;
    return colorScheme?.matches ? "dark" : "light";
  }

  function applyTheme() {
    const theme = currentTheme();
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
  }

  applyTheme();
  window.addEventListener("openai:set_globals", applyTheme);
  colorScheme?.addEventListener?.("change", applyTheme);
})();
