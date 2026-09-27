/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#f0f0ff',
          100: '#e4e4ff',
          200: '#cdcbfe',
          300: '#ada8fc',
          400: '#8b7cf8',
          500: '#7c5af2',
          600: '#6c3ee8',
          700: '#5d2cd3',
          800: '#4e25b0',
          900: '#42218e',
        },
        surface: {
          50:  '#f8f9fc',
          100: '#f1f3f9',
          200: '#e8ecf4',
          300: '#d4dae8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.04)',
        'card-hover': '0 4px 12px rgba(0,0,0,.08), 0 12px 32px rgba(0,0,0,.06)',
        glow: '0 0 24px rgba(124,90,242,.25)',
      },
      animation: {
        'fade-in': 'fadeIn .3s ease both',
        'slide-up': 'slideUp .4s cubic-bezier(.16,1,.3,1) both',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
