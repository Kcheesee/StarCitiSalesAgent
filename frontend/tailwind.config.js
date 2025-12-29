/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'sc-cyan': {
          400: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
        },
      },
    },
  },
  plugins: [],
}
