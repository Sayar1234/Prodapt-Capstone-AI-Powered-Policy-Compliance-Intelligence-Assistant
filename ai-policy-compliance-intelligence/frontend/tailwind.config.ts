import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0d1117',
          900: '#111827',
          700: '#374151',
          500: '#6b7280',
        },
        compliance: {
          blue: '#2563eb',
          teal: '#0f766e',
          amber: '#b45309',
          rose: '#be123c',
        },
      },
      boxShadow: {
        line: '0 1px 0 rgba(17,24,39,0.06)',
      },
    },
  },
  plugins: [],
} satisfies Config
