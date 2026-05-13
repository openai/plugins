module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "var(--codex-bg)",
        panel: "var(--codex-panel)",
        raised: "var(--codex-raised)",
        control: "var(--codex-control)",
        ink: "var(--codex-text)",
        muted: "var(--codex-text-secondary)",
        faint: "var(--codex-text-tertiary)",
        line: "var(--codex-border)",
        "line-strong": "var(--codex-border-heavy)",
        accent: "var(--codex-accent)",
      },
      borderRadius: {
        sm: "var(--codex-radius-sm)",
        md: "var(--codex-radius-md)",
        lg: "var(--codex-radius-lg)",
        xl: "var(--codex-radius-xl)",
      },
      boxShadow: {
        hairline: "var(--codex-shadow-hairline)",
      },
      fontFamily: {
        sans: "var(--codex-font-sans)",
        mono: "var(--codex-font-mono)",
      },
    },
  },
  plugins: [],
};
