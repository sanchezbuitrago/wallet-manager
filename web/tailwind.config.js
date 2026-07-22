/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        noir: {
          50: "#f5f5f5",
          100: "#e5e5e5",
          200: "#cccccc",
          300: "#aaaaaa",
          400: "#888888",
          500: "#666666",
          600: "#555555",
          700: "#444444",
          800: "#333333",
          900: "#222222",
          950: "#111111",
        },
      },
      keyframes: {
        shrink: {
          from: { width: "100%" },
          to: { width: "0%" },
        },
      },
    },
  },
  plugins: [],
};
