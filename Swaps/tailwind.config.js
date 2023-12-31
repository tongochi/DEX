/* eslint-env node */
import flowbite from "flowbite/plugin";

const theme = {
  fontFamily: {
    sans: ["Mulish"],
  },
  fontSize: {
    title1: [
      "2rem",
      {
        lineHeight: "2.35rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    title2: [
      "1.42rem",
      {
        lineHeight: "1.64rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    title3: [
      "1.21rem",
      {
        lineHeight: "1.42rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    headline1: [
      "1.14rem",
      {
        lineHeight: "1.35rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    headline2: [
      "1.14rem",
      {
        lineHeight: "1.35rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    headline3: [
      "1.07rem",
      {
        lineHeight: "1.28rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    regular1: [
      "1.14rem",
      {
        lineHeight: "1.35rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    regular2: [
      "1.07rem",
      {
        lineHeight: "1.28rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    subtitle1: [
      "1rem",
      {
        lineHeight: "1.14rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    subtitle2: [
      "1rem",
      {
        lineHeight: "1.14rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    subtitle3: [
      "0.92rem",
      {
        lineHeight: "1.07rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    caption1: [
      "0.92rem",
      {
        lineHeight: "1.07rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
    caption2: [
      "0.85rem",
      {
        lineHeight: "0.92rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    caption3: [
      "0.78rem",
      {
        lineHeight: "0.92rem",
        letterSpacing: "0rem",
        fontWeight: "400",
      },
    ],
    caption4: [
      "0.78rem",
      {
        lineHeight: "0.92rem",
        letterSpacing: "0rem",
        fontWeight: "500",
      },
    ],
  },
  colors: {
    transparent: "transparent",
    current: "currentColor",
    white: {
      1: "#ffffff",
      2: "#cccccc",
      3: "#999999",
      4: "#666666",
      5: "#333333",
    },
    black: {
      1: "#cccccc",
      2: "#999999",
      3: "#666666",
      4: "#333333",
      5: "#000000",
    },
    main: {
      light: {
        1: "#cce7f5",
        2: "#99cfeb",
        3: "#66b8e0",
        4: "#33a0d6",
        5: "#0088cc",
        6: "#006da3",
        7: "#00527a",
        8: "#003652",
        9: "#001b29",
      },
      dark: {
        1: "#cdecfb",
        2: "#9cd9f7",
        3: "#6ac6f4",
        4: "#39b3f0",
        5: "#07a0ec",
        6: "#0680bd",
        7: "#04608e",
        8: "#03405e",
        9: "#01202f",
      },
    },
    gray: {
      light: {
        1: "#fdfefe",
        2: "#fcfdfd",
        3: "#fafbfd",
        4: "#f9fafc",
        5: "#f7f9fb",
        6: "#c6c7c9",
        7: "#949597",
        8: "#636464",
        9: "#313232",
      },
      dark: {
        1: "#d3d3d4",
        2: "#a7a7a9",
        3: "#7b7b7e",
        4: "#4f4f53",
        5: "#232328",
        6: "#1c1c20",
        7: "#151518",
        8: "#0e0e10",
        9: "#070708",
      },
    },
  },
};

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
      ...theme,
      fontFamily: {
        sans: ["Orbitron"],
      },
    },
  },
  plugins: [flowbite],
};
