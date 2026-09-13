/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0a0914',
          secondary: '#121024',
          tertiary: '#181530',
          card: '#131126',
        },
        border: {
          subtle: '#262046',
          muted: '#1f1a3a',
          focus: '#4a3f85',
        },
        vertice: {
          primary: '#4200db',
          dark: '#35009e',
          light: '#8575ff',
          pastel: '#e8e6ff',
          glow: 'rgba(133, 117, 255, 0.25)',
        },
        elo: {
          navy: '#0b132b',
          purple: '#4200db',
          lilac: '#8575ff',
          slate: '#64748b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
