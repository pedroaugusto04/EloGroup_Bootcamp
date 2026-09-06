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
          primary: '#09090b',
          secondary: '#121215',
          tertiary: '#18181b',
          card: '#11131a',
        },
        border: {
          subtle: '#27272a',
          muted: '#1f1f23',
          focus: '#3f3f46',
        },
        elo: {
          navy: '#0b132b',
          cyan: '#38bdf8',
          blue: '#2563eb',
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
