const defaultTheme = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',
    content: [
        "**/*.{html,js,py}",
        "!./**/node_modules/**",
        "!**/node_modules/**",
    ],
    safelist: [
        // Badge component colors - default variant
        'bg-zinc-100', 'text-zinc-700', 'dark:bg-zinc-800', 'dark:text-zinc-300',
        'bg-red-100', 'text-red-700', 'dark:bg-red-900/30', 'dark:text-red-400',
        'bg-orange-100', 'text-orange-700', 'dark:bg-orange-900/30', 'dark:text-orange-400',
        'bg-amber-100', 'text-amber-700', 'dark:bg-amber-900/30', 'dark:text-amber-400',
        'bg-yellow-100', 'text-yellow-700', 'dark:bg-yellow-900/30', 'dark:text-yellow-400',
        'bg-lime-100', 'text-lime-700', 'dark:bg-lime-900/30', 'dark:text-lime-400',
        'bg-green-100', 'text-green-700', 'dark:bg-green-900/30', 'dark:text-green-400',
        'bg-emerald-100', 'text-emerald-700', 'dark:bg-emerald-900/30', 'dark:text-emerald-400',
        'bg-teal-100', 'text-teal-700', 'dark:bg-teal-900/30', 'dark:text-teal-400',
        'bg-cyan-100', 'text-cyan-700', 'dark:bg-cyan-900/30', 'dark:text-cyan-400',
        'bg-sky-100', 'text-sky-700', 'dark:bg-sky-900/30', 'dark:text-sky-400',
        'bg-blue-100', 'text-blue-700', 'dark:bg-blue-900/30', 'dark:text-blue-400',
        'bg-indigo-100', 'text-indigo-700', 'dark:bg-indigo-900/30', 'dark:text-indigo-400',
        'bg-violet-100', 'text-violet-700', 'dark:bg-violet-900/30', 'dark:text-violet-400',
        'bg-purple-100', 'text-purple-700', 'dark:bg-purple-900/30', 'dark:text-purple-400',
        'bg-fuchsia-100', 'text-fuchsia-700', 'dark:bg-fuchsia-900/30', 'dark:text-fuchsia-400',
        'bg-pink-100', 'text-pink-700', 'dark:bg-pink-900/30', 'dark:text-pink-400',
        'bg-rose-100', 'text-rose-700', 'dark:bg-rose-900/30', 'dark:text-rose-400',
        // Badge component colors - solid variant
        'bg-zinc-700', 'text-white', 'dark:bg-zinc-300', 'dark:text-zinc-900',
        'bg-red-600', 'dark:bg-red-500',
        'bg-orange-600', 'dark:bg-orange-500',
        'bg-amber-600', 'dark:bg-amber-500',
        'bg-yellow-600', 'dark:bg-yellow-500',
        'bg-lime-600', 'dark:bg-lime-500',
        'bg-green-600', 'dark:bg-green-500',
        'bg-emerald-600', 'dark:bg-emerald-500',
        'bg-teal-600', 'dark:bg-teal-500',
        'bg-cyan-600', 'dark:bg-cyan-500',
        'bg-sky-600', 'dark:bg-sky-500',
        'bg-blue-600', 'dark:bg-blue-500',
        'bg-indigo-600', 'dark:bg-indigo-500',
        'bg-violet-600', 'dark:bg-violet-500',
        'bg-purple-600', 'dark:bg-purple-500',
        'bg-fuchsia-600', 'dark:bg-fuchsia-500',
        'bg-pink-600', 'dark:bg-pink-500',
        'bg-rose-600', 'dark:bg-rose-500',
    ],
    theme: {
        extend: {
            colors: {
                accent: {
                    DEFAULT: 'var(--color-accent)',
                    content: 'var(--color-accent-content)',
                    foreground: 'var(--color-accent-foreground)',
                },
            },
            ringColor: {
                DEFAULT: 'var(--color-accent)',
            },
            fontFamily: {
                'sans': ['figtree', 'Inter Variable', 'Plus Jakarta Sans', ...defaultTheme.fontFamily.sans],
                'mono': ['Roboto Mono', ...defaultTheme.fontFamily.mono],
            },
            spacing: {
                '8xl': '96rem',
            },
        }
    },
    plugins: [
        require('@tailwindcss/typography'),
        // ...
    ],
}