import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        bgSoft: "var(--bg-soft)",
        panel: "var(--panel)",
        line: "var(--line)",
        text: "var(--text)",
        textSoft: "var(--text-soft)",
        accent: "var(--accent)",
        accentAlt: "var(--accent-alt)",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(141, 120, 255, 0.15), 0 12px 32px rgba(0, 0, 0, 0.35)",
      },
      borderRadius: {
        xl: "14px",
      },
    },
  },
  plugins: [],
};

export default config;
