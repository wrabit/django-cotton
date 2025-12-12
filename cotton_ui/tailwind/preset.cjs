/**
 * Cotton UI Tailwind CSS v3 Preset
 *
 * This preset provides the theme tokens used by Cotton UI components.
 * Components use CSS custom properties for easy customization.
 *
 * Usage in tailwind.config.js:
 *
 *   const cottonPreset = require("cotton_ui/tailwind/preset.cjs");
 *
 *   module.exports = {
 *     presets: [cottonPreset],
 *     content: [
 *       "./templates/**\/*.html",
 *       // Include cotton_ui templates - find path with:
 *       // python -c "import cotton_ui; print(cotton_ui.__path__[0] + '/templates/**\/*.html')"
 *     ],
 *   };
 *
 * CSS Custom Properties (override in your CSS):
 *
 *   :root {
 *     --color-accent: #14b8a6;           // Primary accent color (teal-500)
 *     --color-accent-content: #0d9488;   // Darker accent for hover states
 *     --color-accent-foreground: #fff;   // Text color on accent backgrounds
 *     --radius: 0.5rem;                  // Default border radius
 *     --focus-ring-width: 2px;
 *     --focus-ring-color: var(--color-accent);
 *   }
 */

module.exports = {
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: "var(--color-accent, #14b8a6)",
          content: "var(--color-accent-content, #0d9488)",
          foreground: "var(--color-accent-foreground, #ffffff)",
        },
      },
      borderRadius: {
        DEFAULT: "var(--radius, 0.5rem)",
      },
      ringWidth: {
        DEFAULT: "var(--focus-ring-width, 2px)",
      },
      ringColor: {
        DEFAULT: "var(--focus-ring-color, var(--color-accent, #14b8a6))",
      },
    },
  },
};
