/* eslint-env node */
import { tdsTheme } from "@designervoid/ton-design-system";
import flowbite from "flowbite/plugin";

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
    "node_modules/flowbite-vue/**/*.{js,jsx,ts,tsx}",
    "node_modules/flowbite/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      ...tdsTheme,
      fontFamily: {
        sans: ["Orbitron"],
      },
    },
  },
  plugins: [flowbite],
};
