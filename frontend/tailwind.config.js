/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        blush: "#b95f89",
        ice: "#c4e0f9",
        periwinkle: "#9bbdf9",
        azure: "#67aaf9",
        electric: "#2ec0f9",
        ink: "#102033",
      },
      boxShadow: {
        soft: "0 18px 45px rgba(16, 32, 51, 0.12)",
      },
    },
  },
  plugins: [],
};
