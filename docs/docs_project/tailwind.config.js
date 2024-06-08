const defaultTheme = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',
    content: [
        "**/*.{html,js,py}",
        "!./**/node_modules/**",
        "!**/node_modules/**",
    ],
    theme: {
        extend: {
            fontFamily: {
                'sans': ['Plus Jakarta Sans', ...defaultTheme.fontFamily.sans],
                'logo': ['Velux Transform', ...defaultTheme.fontFamily.sans],
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