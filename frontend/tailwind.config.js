/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Theme-aware tokens (driven by CSS variables in globals.css).
        // Channels are space-separated RGB so Tailwind opacity modifiers work.
        bg: {
          0: 'rgb(var(--bg-0) / <alpha-value>)',
          1: 'rgb(var(--bg-1) / <alpha-value>)',
          2: 'rgb(var(--bg-2) / <alpha-value>)',
          3: 'rgb(var(--bg-3) / <alpha-value>)',
          4: 'rgb(var(--bg-4) / <alpha-value>)',
        },
        text: {
          1: 'rgb(var(--text-1) / <alpha-value>)',
          2: 'rgb(var(--text-2) / <alpha-value>)',
          3: 'rgb(var(--text-3) / <alpha-value>)',
        },
        line: 'rgb(var(--line) / <alpha-value>)',
        accent: {
          purple: '#6B46C1',
          'purple-light': '#8B5CF6',
          'purple-dark': '#4C1D95',
          blue: '#2563EB',
          gold: '#C9A84C',
          'gold-light': '#E2C068',
          'gold-dark': '#A07830',
        },
        status: {
          active: '#10B981',
          thinking: '#F59E0B',
          idle: '#94A3B8',
          error: '#EF4444',
        },
      },
      fontFamily: {
        display: ['var(--font-playfair)', 'Playfair Display', 'serif'],
        sans: ['var(--font-inter)', 'Inter', 'sans-serif'],
        mono: ['var(--font-mono)', 'DM Mono', 'monospace'],
      },
      animation: {
        'float': 'float 4s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.22,1,0.36,1)',
        'slide-in': 'slideIn 0.4s cubic-bezier(0.22,1,0.36,1)',
        'orbit': 'orbit 20s linear infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
        'ring-rot': 'ringRot 22s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        glow: {
          from: { boxShadow: '0 0 20px rgba(107,70,193,0.25)' },
          to: { boxShadow: '0 0 40px rgba(107,70,193,0.5), 0 0 80px rgba(107,70,193,0.18)' },
        },
        slideUp: {
          from: { opacity: 0, transform: 'translateY(20px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        slideIn: {
          from: { opacity: 0, transform: 'translateX(-16px)' },
          to: { opacity: 1, transform: 'translateX(0)' },
        },
        orbit: {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        ringRot: {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
      },
      boxShadow: {
        'soft': 'var(--shadow)',
        'card': 'var(--shadow-md)',
        'card-hover': 'var(--shadow-lg)',
        'purple': '0 8px 28px rgba(107,70,193,0.30)',
        'purple-lg': '0 14px 44px rgba(107,70,193,0.40)',
        'gold': '0 8px 28px rgba(201,168,76,0.25)',
      },
      borderRadius: {
        'xl2': '20px',
      },
    },
  },
  plugins: [],
};
