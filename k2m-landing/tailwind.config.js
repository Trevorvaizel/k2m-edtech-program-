/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pure-black': 'var(--pure-black)',
        'soft-black': 'var(--soft-black)',
        'charcoal': 'var(--charcoal)',
        'ocean-mint-primary': 'var(--ocean-mint-primary)',
        'ocean-mint-glow': 'var(--ocean-mint-glow)',
        'ocean-mint-dim': 'var(--ocean-mint-dim)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-muted': 'var(--text-muted)',
      },
      fontFamily: {
        'space-grotesk': ['"Space Grotesk"', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
