# Django Cotton UI

A UI component library for [Django Cotton](https://github.com/wrabit/django-cotton). Ready-to-use, customizable components built with Tailwind CSS v4 and Alpine.js.

## Installation

```bash
pip install django-cotton-ui
```

## Setup

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_cotton",
    "cotton_ui",
]
```

### 2. Tailwind CSS (v4)

Cotton UI components are styled with Tailwind utility classes, so your Tailwind build needs to scan the component templates and define the accent palette. In your main CSS entry:

```css
@import "tailwindcss";

/* Scan Cotton UI's templates so their utility classes are generated. */
@source "<path-to-installed>/cotton_ui/templates/**/*.html";

/* Accent palette (Flux-style). Swap teal for any Tailwind hue. */
@theme {
    --color-accent: var(--color-teal-500);
    --color-accent-content: var(--color-teal-600);
    --color-accent-foreground: var(--color-white);
}

@layer theme {
    .dark {
        --color-accent: var(--color-teal-400);
        --color-accent-content: var(--color-teal-300);
        --color-accent-foreground: var(--color-teal-950);
    }
}
```

Find the installed templates path with:

```bash
python -c "import cotton_ui, os; print(os.path.join(cotton_ui.__path__[0], 'templates'))"
```

> Components use a class-based dark variant. If you toggle `.dark` on `<html>`, add
> `@custom-variant dark (&:where(.dark, .dark *));` to your CSS.

### 3. Alpine.js and the Cotton UI bundle

Interactive components register themselves on Alpine's `alpine:init` event, so the
Cotton UI bundle must load **before** Alpine. Include the component stylesheet too
(it provides the radius/focus-ring tokens and the `x-cloak` rule):

```django
{% load static %}
<link rel="stylesheet" href="{% static 'cotton-ui/cotton-ui.css' %}">

<!-- Cotton UI first, then Alpine (both deferred, so they run in order) -->
<script defer src="{% static 'cotton-ui/cotton-ui.min.js' %}"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

Run `python manage.py collectstatic` so the bundle is served in production.

## Usage

Use components with the `c-ui.` prefix:

```django
{# Buttons #}
<c-ui.button>Default</c-ui.button>
<c-ui.button variant="primary">Primary</c-ui.button>

{# Input with label #}
<c-ui.input name="email" label="Email" placeholder="you@example.com" />

{# Card (content goes in the default slot) #}
<c-ui.card>
    <h3 class="font-semibold">Title</h3>
    <p>Content goes here.</p>
</c-ui.card>

{# Tabs #}
<c-ui.tabs>
    <c-ui.tabs.tab name="Account">Account settings…</c-ui.tabs.tab>
    <c-ui.tabs.tab name="Password">Change your password…</c-ui.tabs.tab>
</c-ui.tabs>

{# Combobox / multi-select #}
<c-ui.combobox
    name="skills"
    label="Skills"
    :options="['Python', 'Django', 'JavaScript']"
    :searchable="True"
/>
```

## Customization

The accent palette is set in your `@theme` block (see Setup). Component tokens can be
overridden in plain CSS:

```css
:root {
    --radius: 0.5rem;            /* border radius */
    --focus-ring-width: 2px;
    --focus-ring-color: var(--color-accent);
}
```

Swapping the gray base: Cotton UI components are built on Tailwind's `zinc` scale.
To reskin to another base (slate, neutral and so on), remap those variables in
`@theme`, e.g. `--color-zinc-500: var(--color-slate-500);` for each shade.

## Available Components

- **Form controls**: button, input, textarea, select, checkbox, radio, switch, combobox, field
- **Layout**: card, accordion, tabs, dialog, slideover
- **Navigation**: navbar, navlist, menu, dropdown
- **Feedback**: badge, tooltip
- **Data**: datepicker

## Requirements

- Python >= 3.8
- Django >= 4.2
- django-cotton >= 2.5.0
- Tailwind CSS v4 (in your project)
- Alpine.js v3 (in your project)

## License

MIT License
