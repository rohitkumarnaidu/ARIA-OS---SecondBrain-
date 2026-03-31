/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: {
          dark: '#0A0A0F',
          card: '#12121A',
          elevated: '#1A1A24',
        },
        border: {
          DEFAULT: '#2A2A3A',
        },
        accent: {
          primary: '#6366F1',
          secondary: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
          info: '#3B82F6',
        },
        priority: {
          urgent: '#EF4444',
          high: '#F97316',
          medium: '#EAB308',
          low: '#22C55E',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}