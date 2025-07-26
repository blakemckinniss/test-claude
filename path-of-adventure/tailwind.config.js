/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Parchment theme colors from CSS variables
        'parchment-light': '#f4e8d0',
        'parchment': '#e8dcc3', 
        'parchment-dark': '#d4c4a0',
        'parchment-shadow': '#b8a47d',
        'ink-black': '#2c2416',
        'ink-brown': '#4a3c2a',
        'gold': '#d4af37',
        'ruby-red': '#8b0000',
        'emerald-green': '#2e5e3e',
        'sapphire-blue': '#1e3a5f',
        
        // Original game colors
        'game-primary': '#4a90e2',
        'game-secondary': '#f39c12',
        'game-danger': '#e74c3c',
        'game-success': '#27ae60',
        'game-dark': '#2c3e50',
        'game-light': '#ecf0f1',
      },
      fontFamily: {
        'game': ['Fira Code', 'monospace'],
        'medieval': ['Cinzel', 'Georgia', 'serif'],
        'script': ['Uncial Antiqua', 'Georgia', 'serif'],
        'body': ['Alegreya', 'Georgia', 'serif'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'flicker': 'flicker 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(74, 144, 226, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(74, 144, 226, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        flicker: {
          '0%, 100%': { opacity: '0.8', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-100% 0' },
          '100%': { backgroundPosition: '100% 0' },
        },
      },
      boxShadow: {
        'parchment': 'inset 0 0 40px rgba(184, 164, 125, 0.3), 0 4px 12px rgba(44, 36, 22, 0.4)',
      },
    },
  },
  plugins: [],
}