/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx}", "./components/**/*.{js,jsx}", "./lib/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        desk: "#E8ECF1",
        sheet: "#F7F9FB",
        ink: "#14213D",
        muted: "#586579",
        line: "#C8D0DB",
        verdict: {
          true: "#0F6E66",
          false: "#B3261E",
          mixed: "#A86A12",
          none: "#586579",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
