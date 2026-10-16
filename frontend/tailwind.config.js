/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: "#070709",
          900: "#0a0a0f",
          850: "#0f1016",
          800: "#14151f",
          700: "#1e202e",
          600: "#2a2d3e",
        },
        cyber: {
          cyan: "#00f0ff",
          glow: "rgba(0, 240, 255, 0.3)",
          magenta: "#ff007f",
          gold: "#d4af37",
          amber: "#ff7a00",
        },
        surface: {
          glass: "rgba(18, 20, 28, 0.72)",
          glassHover: "rgba(28, 32, 44, 0.85)",
          border: "rgba(255, 255, 255, 0.08)",
          borderGlow: "rgba(0, 240, 255, 0.3)",
        },
      },
      fontFamily: {
        heading: ["Syne", "Outfit", "sans-serif"],
        body: ["Outfit", "Inter", "sans-serif"],
        mono: ["Space Grotesk", "monospace"],
      },
      boxShadow: {
        "cyber-cyan": "0 0 35px -5px rgba(0, 240, 255, 0.35)",
        "cyber-gold": "0 0 35px -5px rgba(212, 175, 55, 0.35)",
        "cyber-amber": "0 0 45px -5px rgba(255, 122, 0, 0.45)",
        "cyber-ruby": "0 0 45px -5px rgba(255, 0, 127, 0.4)",
        "glass-card": "0 20px 50px rgba(0, 0, 0, 0.6)",
      },
      animation: {
        "float-gentle": "float 5s ease-in-out infinite",
        "pulse-glow": "pulseGlow 3s ease-in-out infinite",
        "laser-scan": "laserScan 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite",
        "sheen": "sheenSweep 3s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px) rotate(0deg)" },
          "50%": { transform: "translateY(-14px) rotate(1deg)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.6", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.04)" },
        },
        laserScan: {
          "0%": { top: "0%", opacity: "0" },
          "15%": { opacity: "1" },
          "85%": { opacity: "1" },
          "100%": { top: "100%", opacity: "0" },
        },
        sheenSweep: {
          "0%": { transform: "translateX(-150%) skewX(-20deg)" },
          "50%, 100%": { transform: "translateX(250%) skewX(-20deg)" },
        },
      },
    },
  },
  plugins: [],
};
