const defaultTheme = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',
    content: [
        "**/*.{html,js,py}",
        "!./**/node_modules/**",
        "!**/node_modules/**",
    ],
    // Layout grid classes are wedged between Django {% %} tags in
    // with_sidebar.html, which the JIT content extractor can miss in some
    // builds (works locally, dropped on deploy). Safelist them so the
    // 3-column docs grid (page index on the right) is always emitted.
    safelist: [
        "sm:grid-cols-[200px_auto]",
        "lg:grid-cols-[230px_auto_250px]",
        "lg:grid-cols-[230px_auto]",
    ],
    theme: {
        extend: {
            fontFamily: {
                'sans': ['Plus Jakarta Sans', ...defaultTheme.fontFamily.sans],
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