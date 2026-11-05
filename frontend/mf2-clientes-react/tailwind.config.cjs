/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [require('../design-system/tailwind.preset.js')],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

