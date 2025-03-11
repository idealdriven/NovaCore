/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4F95D3',
          DEFAULT: '#2563EB',
          dark: '#1E40AF',
        },
        secondary: {
          light: '#98C379',
          DEFAULT: '#65A30D',
          dark: '#4D7C0F',
        },
        background: {
          light: '#F9FAFB',
          DEFAULT: '#F3F4F6',
          dark: '#1F2937',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 