/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#005c55',
          container: '#0f766e',
          fixed: '#9cf2e8',
          'fixed-dim': '#80d5cb',
        },
        'on-primary': '#ffffff',
        'on-primary-container': '#a3faef',
        'on-primary-fixed': '#00201d',
        'on-primary-fixed-variant': '#00504a',
        'inverse-primary': '#80d5cb',

        secondary: {
          DEFAULT: '#565e74',
          container: '#dae2fd',
          fixed: '#dae2fd',
          'fixed-dim': '#bec6e0',
        },
        'on-secondary': '#ffffff',
        'on-secondary-container': '#5c647a',
        'on-secondary-fixed': '#131b2e',
        'on-secondary-fixed-variant': '#3f465c',

        tertiary: {
          DEFAULT: '#3f33d6',
          container: '#5951ef',
          fixed: '#e2dfff',
          'fixed-dim': '#c3c0ff',
        },
        'on-tertiary': '#ffffff',
        'on-tertiary-container': '#ebe8ff',
        'on-tertiary-fixed': '#0f0069',
        'on-tertiary-fixed-variant': '#3323cc',

        ai: {
          indigo: '#4f46e5',
          pulse: 'rgba(79, 70, 229, 0.25)',
        },

        surface: {
          DEFAULT: '#f8f9ff',
          dim: '#cbdbf5',
          bright: '#f8f9ff',
          lowest: '#ffffff',
          low: '#eff4ff',
          container: '#e5eeff',
          high: '#dce9ff',
          highest: '#d3e4fe',
          variant: '#d3e4fe',
        },
        'on-surface': '#0b1c30',
        'on-surface-variant': '#3e4947',
        'inverse-surface': '#213145',
        'inverse-on-surface': '#eaf1ff',

        background: '#f8f9ff',
        'on-background': '#0b1c30',

        error: {
          DEFAULT: '#ba1a1a',
          container: '#ffdad6',
        },
        'on-error': '#ffffff',
        'on-error-container': '#93000a',

        solvency: {
          DEFAULT: '#10b981',
          container: '#ecfdf5',
        },
        review: {
          DEFAULT: '#d97706',
          container: '#fffbeb',
        },
        critical: {
          DEFAULT: '#e11d48',
          container: '#fff1f2',
        },

        outline: {
          DEFAULT: '#6e7977',
          variant: '#bdc9c6',
          crisp: '#e2e8f0',
        },
      },
      fontFamily: {
        headline: ['Plus Jakarta Sans', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        'headline-sm': ['Plus Jakarta Sans', 'sans-serif'],
        'headline-md': ['Plus Jakarta Sans', 'sans-serif'],
        'headline-lg': ['Plus Jakarta Sans', 'sans-serif'],
        'headline-xl': ['Plus Jakarta Sans', 'sans-serif'],
        'body-xs': ['Inter', 'sans-serif'],
        'body-sm': ['Inter', 'sans-serif'],
        'body-md': ['Inter', 'sans-serif'],
        'body-lg': ['Inter', 'sans-serif'],
        'label-code': ['JetBrains Mono', 'monospace'],
        'label-telemetry': ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        sm: '0.25rem',
        DEFAULT: '0.5rem',
        md: '0.75rem',
        lg: '1rem',
        xl: '1.5rem',
        full: '9999px',
      },
      spacing: {
        'space-xxs': '0.125rem',
        'space-xs': '0.25rem',
        'space-sm': '0.5rem',
        'space-md': '0.75rem',
        'space-lg': '1rem',
        'space-xl': '1.5rem',
        'space-2xl': '2rem',
        'space-3xl': '3rem',
        gutter: '1.5rem',
        'gutter-mobile': '0.75rem',
        margin: '2rem',
        'margin-mobile': '1rem',
      },
      boxShadow: {
        'level-1': '0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)',
        'level-2': '0 10px 15px -3px rgba(15, 23, 42, 0.06), 0 4px 6px -4px rgba(15, 23, 42, 0.03)',
        'level-3': '0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)',
        'ai-telemetry': '0 0 0 1px rgba(79, 70, 229, 0.1), 0 4px 12px rgba(79, 70, 229, 0.04)',
      },
    },
  },
};
