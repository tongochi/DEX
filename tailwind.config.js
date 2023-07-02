/** @type {import('tailwindcss').Config} */
const tdsTheme = require('@designervoid/ton-design-system/lib');

module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: tdsTheme,
  },
  plugins: [],
};