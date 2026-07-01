/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#1F2D4E',
        goldenrod: '#B8860B',
        cream: '#F5F2E8',
        'nhi-gray': '#4A4A4A',
      },
      animation: {
        'pulse-red': 'pulse 1.2s cubic-bezier(0.4,0,0.6,1) infinite',
      },
    },
  },
  plugins: [],
};
