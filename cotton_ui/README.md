# Django Cotton UI

A UI component library for [Django Cotton](https://github.com/wrabit/django-cotton). Provides ready-to-use, customizable UI components built with Tailwind CSS and Alpine.js.

## Installation

```bash
pip install django-cotton-ui
```

Or for local development:

```bash
pip install -e /path/to/cotton_ui
```

## Setup

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    ...
    "django_cotton",
    "cotton_ui",
]
```

### 2. Configure Tailwind CSS

Cotton UI components use Tailwind CSS classes. You need to include the component templates in your Tailwind content configuration.

```javascript
// tailwind.config.js
const cottonPreset = require("cotton_ui/tailwind/preset.cjs");

module.exports = {
  presets: [cottonPreset],
  content: [
    "./templates/**/*.html",
    // Include cotton_ui templates - find the path with:
    // python -c "import cotton_ui; print(cotton_ui.__path__[0] + '/templates/**/*.html')"
  ],
};
```

### 3. Include Alpine.js

Cotton UI's interactive components require Alpine.js. Include it via CDN or your bundler:

```html
<!-- Via CDN -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

## Usage

Use components with the `c-ui.` prefix:

```django
<!-- Button -->
<c-ui.button>Click me</c-ui.button>
<c-ui.button variant="primary">Primary</c-ui.button>

<!-- Input with label -->
<c-ui.input name="email" label="Email" placeholder="you@example.com" />

<!-- Card -->
<c-ui.card>
    <c-ui.card.header>Title</c-ui.card.header>
    <c-ui.card.content>Content goes here</c-ui.card.content>
</c-ui.card>

<!-- Combobox / Multi-select -->
<c-ui.combobox
    name="skills"
    label="Skills"
    :options="['Python', 'Django', 'JavaScript']"
    :searchable="True"
/>
```

## Customization

Override CSS custom properties to customize the theme:

```css
:root {
  /* Accent color (default: teal) */
  --color-accent: #14b8a6;
  --color-accent-content: #0d9488;
  --color-accent-foreground: #ffffff;

  /* Border radius */
  --radius: 0.5rem;

  /* Focus ring */
  --focus-ring-width: 2px;
  --focus-ring-color: var(--color-accent);
}

/* Dark mode overrides */
.dark {
  --color-accent: #2dd4bf;
  --color-accent-content: #5eead4;
  --color-accent-foreground: #042f2e;
}
```

## Available Components

- **Form Controls**: button, input, textarea, select, checkbox, radio, switch, combobox
- **Layout**: card, accordion, tabs, dialog, slideover
- **Navigation**: navbar, navlist, menu, dropdown
- **Feedback**: badge, tooltip
- **Data**: calendar, datepicker

## Requirements

- Python >= 3.8
- Django >= 4.2
- django-cotton >= 2.5.0
- Tailwind CSS v3 (in your project)
- Alpine.js v3 (in your project)

## License

MIT License
