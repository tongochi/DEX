const {tdsTheme} = require('@designervoid/ton-design-system/lib');

/** @type {import('tailwindcss').Config} */
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