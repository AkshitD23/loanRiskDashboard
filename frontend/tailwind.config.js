/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        surface: 'rgba(30, 41, 59, 0.7)',
        primary: '#3b82f6',
        success: '#22c55e',
        danger: '#ef4444',
      },
      scale: {
        '103': '1.03',
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.1)',
        'strong': '0 10px 40px -4px rgba(0, 0, 0, 0.4)',
      },
      transitionProperty: {
        'card': 'transform, box-shadow',
      },
      transitionDuration: {
        '200': '200ms',
      }
    },
  },
  plugins: [],
}
