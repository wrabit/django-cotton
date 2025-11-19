# Cotton UI Component Creation Guide

This document outlines the complete process for creating new components in Cotton UI, based on the checkbox and radio component implementations.

## Overview

Cotton UI components follow a consistent pattern:
- **Alpine.js** for JavaScript interactivity
- **Django Cotton** for templating and component composition
- **Tailwind CSS v3** for styling
- **esbuild** for JavaScript bundling

## Component Architecture

### Directory Structure

```
cottonui/
├── js/
│   ├── component-name.js          # Alpine.js component logic
│   └── cotton-ui.js                # Main entry point (register components here)
├── templates/cotton/ui/
│   └── component-name/
│       ├── index.html              # Individual component item
│       └── group.html              # Optional: wrapper/group component
├── css/
│   └── cotton-ui.css               # Global CSS variables and theming
└── static/cotton-ui/               # Build output directory (generated)

docs_project/
└── templates/ui_docs/
    └── component-name.html         # Documentation page
```

## Step-by-Step Component Creation

### 1. Create Alpine.js Component

**Location:** `cottonui/js/component-name.js`

**Pattern:**
```javascript
export default (name, initialValue) => ({
    // State
    value: initialValue,
    name: name,

    // Lifecycle
    init() {
        // Initialize component state
    },

    // Methods
    methodName() {
        // Component logic
        this.$dispatch('event-name', { data });
    },

    // Computed properties
    isSelected(value) {
        return this.value === value;
    }
})
```

**Key Points:**
- Export a **default function** that returns an object
- Function parameters: typically `(name, initialValue)`
- Use `this.$el` to access the DOM element
- Use `this.$dispatch()` to emit custom events
- Use `this.$refs` to access referenced elements

**Example (Radio):**
```javascript
export default (name, initialValue = null) => ({
    value: initialValue,
    name: name,

    init() {
        if (this.value === null) {
            const checkedInput = this.$el.querySelector('input[type="radio"]:checked');
            if (checkedInput) {
                this.value = checkedInput.value;
            }
        }
    },

    select(optionValue) {
        this.value = optionValue;
        this.$dispatch('change', { value: optionValue });
    },

    isSelected(optionValue) {
        return this.value === optionValue;
    }
})
```

**Example (Checkbox):**
```javascript
export default (name, initialValues = []) => ({
    values: Array.isArray(initialValues) ? initialValues : [],
    name: name,

    init() {
        if (this.values.length === 0) {
            const checkedInputs = this.$el.querySelectorAll('input[type="checkbox"]:checked');
            this.values = Array.from(checkedInputs).map(input => input.value);
        }
    },

    toggle(optionValue) {
        if (this.isChecked(optionValue)) {
            this.values = this.values.filter(v => v !== optionValue);
        } else {
            this.values.push(optionValue);
        }
        this.$dispatch('change', { values: this.values });
    },

    isChecked(optionValue) {
        return this.values.includes(optionValue);
    }
})
```

### 2. Register Component in Main Bundle

**Location:** `cottonui/js/cotton-ui.js`

**Steps:**
1. Import the component at the top
2. Register it in the Alpine.js init event

```javascript
// 1. Import
import componentName from './component-name.js';

// 2. Register
document.addEventListener('alpine:init', () => {
    Alpine.data('componentName', componentName)
})
```

### 3. Create Component Templates

#### 3.1. Individual Component (`index.html`)

**Location:** `cottonui/templates/cotton/ui/component-name/index.html`

**Key Elements:**

1. **Component Variables** (c-vars):
```html
<c-vars
    value=""
    label=""
    description=""
    :disabled="False"
    :accent="True"
/>
```

2. **Main Element with Alpine.js Bindings**:
```html
<label
    role="checkbox"
    data-value="{{ value }}"
    :aria-checked="isChecked('{{ value }}').toString()"
    @click="{% if not disabled %}toggle('{{ value }}'){% endif %}"
    class="cursor-pointer"
    x-bind:class="(() => {
        const variant = $el.closest('[data-variant]')?.dataset.variant || 'default';
        // Dynamic class logic
        return classes;
    })()"
>
```

3. **Hidden Native Input** (for form submission):
```html
<input
    type="checkbox"
    name="{{ name }}"
    value="{{ value }}"
    :checked="isChecked('{{ value }}')"
    {% if disabled %}disabled{% endif %}
    class="sr-only"
/>
```

4. **Visual Indicator**:
```html
<div x-show="{% if show_indicator %}...{% else %}false{% endif %}" class="...">
    <!-- Visual checkbox/radio indicator -->
</div>
```

5. **Label and Description**:
```html
{% if slot %}
    {{ slot }}
{% else %}
    <div class="flex-1">
        <div class="text-sm font-medium">{{ label }}</div>
        {% if description %}
            <div class="text-sm text-zinc-600">{{ description }}</div>
        {% endif %}
    </div>
{% endif %}
```

**Alpine.js Patterns:**

- **Variant Detection:** Use `$el.closest('[data-variant]')?.dataset.variant` to detect parent variant
- **Dynamic Classes:** Use IIFE in `x-bind:class` for complex logic
- **Static Layout Classes:** Add base layout classes (e.g., `flex items-start gap-3`) directly to the static `class` attribute to prevent layout shift on Alpine initialization
- **Conditional Attributes:** Use Django template tags for static conditions, Alpine for dynamic
- **Event Handlers:** Use `@click`, `@keydown.enter`, etc. For checkboxes, use `@click.prevent` to stop native browser behavior from interfering
- **ARIA Attributes:** Use `:aria-*` for reactive accessibility

#### 3.2. Group Component (`group.html`)

**Location:** `cottonui/templates/cotton/ui/component-name/group.html`

**Pattern:**
```html
<c-vars
    name=""
    label=""
    description=""
    :values="[]"
    variant="default"
    class=""
/>

<fieldset
    x-data='componentName("{{ name }}", {{ values|json_encode }})'
    role="group"
    data-variant="{{ variant }}"
    class="..."
    {{ attrs }}
>
    {% if label %}
        <legend class="...">{{ label }}</legend>
    {% endif %}

    {% if description %}
        <p class="...">{{ description }}</p>
    {% endif %}

    <div class="...">
        {{ slot }}
    </div>
</fieldset>
```

**Key Points:**
- Use `x-data` to initialize Alpine.js component
- Use `data-variant` attribute for child components to detect variant
- Use `{{ attrs }}` to pass through additional attributes
- Use `{{ slot }}` to render child components

### 4. Theming and Styling

#### CSS Variables

**Location:** `cottonui/css/cotton-ui.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
    :root {
        /* Accent colors - Teal by default */
        --color-accent: #14b8a6;
        --color-accent-content: #0d9488;
        --color-accent-foreground: #ffffff;

        /* Border radius */
        --radius: 0.5rem;
    }

    .dark :root {
        /* Accent colors in dark mode */
        --color-accent: #2dd4bf;
        --color-accent-content: #5eead4;
        --color-accent-foreground: #042f2e;
    }
}
```

#### Accent Prop Pattern

All components should support the `:accent` prop for theming consistency:

```html
<c-vars :accent="True" />

{# In template #}
{% if accent %}
    'border-accent bg-accent': isSelected('{{ value }}'),
{% else %}
    'border-zinc-900 dark:border-zinc-100 bg-zinc-900 dark:bg-zinc-100': isSelected('{{ value }}'),
{% endif %}
```

#### Variant System

Components support multiple variants through the `variant` prop:

- `default` - Traditional vertical list
- `buttons` - Horizontal button group
- `cards` - Card-style layout

Variant detection in child components:
```javascript
const variant = $el.closest('[data-variant]')?.dataset.variant || 'default';
```

### 5. Build Process

#### Build Commands

**CSS Build:**
```bash
cd /path/to/docs_project
npx tailwindcss -i ./cottonui/css/cotton-ui.css -o ./cottonui/static/cotton-ui/cotton-ui.css --minify
```

**JavaScript Build:**
```bash
cd /path/to/docs_project/cottonui
npm run build
```

Run the JavaScript build after:
- Creating a new JavaScript component file
- Modifying any existing JavaScript file
- Registering a component in `cotton-ui.js`

**Note:** CSS changes do NOT require manual rebuild. The docker-compose.yaml includes a Tailwind watcher service (`cotton-docs-tailwind`) that automatically rebuilds CSS when changes are detected. Only JavaScript changes require running `npm run build`.

**When to rebuild:**
- **JavaScript changes**: Always run `npm run build` in cottonui directory
- **CSS/Tailwind changes**: No action needed - docker service handles it automatically

#### Build Configuration

**esbuild config** (`cottonui/build.js`):
- Uses ES modules (`import`/`export`)
- Bundles multiple output formats (browser, ESM)
- Generates manifest.json for cache busting
- Creates minified versions with source maps

**Docker Tailwind Watcher** (`docs/docker/docker-compose.yaml`):
- Service: `cotton-docs-tailwind`
- Watches for CSS changes and auto-rebuilds
- No manual intervention needed for CSS/Tailwind changes

### 6. Documentation Page

**Location:** `docs_project/templates/ui_docs/component-name.html`

**Structure:**

```html
<c-layouts.ui>
    <c-header>
        Component Name
        <c-slot name="subheading">
            Brief description of the component.
        </c-slot>
    </c-header>

    <c-slot name="page_index">
        <c-index-sublink><a href="#example-1">Example 1</a></c-index-sublink>
        <c-index-sublink><a href="#example-2">Example 2</a></c-index-sublink>
        <!-- ... -->
    </c-slot>

    <h2 id="example-1">Example 1 Title</h2>
    <p>Description of the example.</p>

    <c-sample>
        <!-- Live example -->
        <c-ui.component-name.group>
            <c-ui.component-name value="option1" label="Option 1" />
        </c-ui.component-name.group>

        <c-slot name="code">
<c-snippet>{% cotton:verbatim %}{% verbatim %}
<!-- Code sample -->
{% endverbatim %}{% endcotton:verbatim %}</c-snippet>
        </c-slot>
    </c-sample>

    <h4 id="reference">Props Reference</h4>
    <c-api-props>
        <c-api-prop
            name="prop-name"
            type="str"
            default=""
            description="Description" />
    </c-api-props>
</c-layouts.ui>
```

**Example Categories:**

Include diverse examples covering:
1. Default usage
2. With descriptions
3. Different layouts (horizontal, vertical)
4. States (checked, disabled)
5. Variants (buttons, cards)
6. With icons
7. Custom content (using slots)

Use varied business/real-world content for examples (payment methods, notifications, features, etc.)

### 7. Props and API Design

#### Standard Props

**Group Component:**
- `name` (str) - Form input name
- `label` (str) - Group label
- `description` (str) - Help text
- `variant` (str) - Visual style (default, buttons, cards)
- `class` (str) - Additional CSS classes
- `:values` (list/str) - Initial selected value(s)

**Individual Component:**
- `value` (str) - Component value
- `label` (str) - Label text
- `description` (str) - Description text
- `icon` (str) - Icon name
- `name` (str) - Form input name (inherited from group)
- `:disabled` (bool) - Disabled state
- `:show_indicator` (bool) - Show/hide indicator
- `:accent` (bool) - Use accent colors

**Naming Conventions:**
- Boolean props: prefix with `:`  (`:disabled="True"`)
- List/dict props: prefix with `:` (`:values="['a', 'b']"`)
- String props: no prefix (`label="Text"`)

### 8. Accessibility (a11y)

#### Required ARIA Attributes

- `role` - Semantic role (checkbox, radio, group, etc.)
- `aria-checked` / `aria-selected` - Selection state
- `aria-disabled` - Disabled state
- `aria-label` / `aria-labelledby` - Label association

#### Keyboard Navigation

**Radio Groups:**
- Arrow keys to navigate between options
- Space/Enter to select
- Roving tabindex pattern

**Checkboxes:**
- Tab to navigate between checkboxes
- Space/Enter to toggle

**Implementation:**
```html
tabindex="{% if disabled %}-1{% else %}0{% endif %}"
@keydown.enter.stop.prevent="..."
@keydown.space.stop.prevent="..."
```

### 9. Common Patterns and Best Practices

#### Alpine.js Scope Management

**DO:**
- Let child components inherit parent scope (no `x-data` on children)
- Use `$el.closest('[data-variant]')` to detect parent context
- Use IIFE for complex computed classes

**DON'T:**
- Add separate `x-data` to child elements within a component
- Use `x-init` to set variables (creates scope issues)

#### Django Template Conditionals

**Static Conditions (Django):**
```html
{% if disabled %}disabled{% endif %}
```

**Dynamic Conditions (Alpine.js):**
```html
:disabled="{% if disabled %}true{% else %}false{% endif %}"
```

#### Class Binding Pattern

**Static + Dynamic Classes:**
```html
class="static-class {% if disabled %}disabled-class{% endif %}"
x-bind:class="{
    'dynamic-class': someCondition,
    'another-class': anotherCondition
}"
```

**IIFE for Complex Logic:**
```html
x-bind:class="(() => {
    const variant = detectVariant();
    const classes = [];

    if (variant === 'default') {
        classes.push('class-a', 'class-b');
    }

    return classes;
})()"
```

#### Form Integration

Always include hidden native inputs for form submission:
```html
<input
    type="checkbox"
    name="{{ name }}"
    value="{{ value }}"
    :checked="isChecked('{{ value }}')"
    class="sr-only"
/>
```

## Component Checklist

When creating a new component, ensure you complete:

- [ ] Create Alpine.js component file (`js/component-name.js`)
- [ ] Register component in `js/cotton-ui.js` (import + Alpine.data)
- [ ] Create component template(s) (`templates/cotton/ui/component-name/`)
- [ ] Add `:accent` prop support for theming
- [ ] Implement all variants (default, buttons, cards, etc.)
- [ ] Include ARIA attributes for accessibility
- [ ] Add keyboard navigation support
- [ ] Include hidden native inputs for forms
- [ ] Create comprehensive documentation page
- [ ] Include diverse, real-world examples
- [ ] Document all props in reference section
- [ ] Build JavaScript bundle (`npm run build`)
- [ ] Test in light and dark modes
- [ ] Test with accent color variations

## Troubleshooting

### Alpine.js Errors

**"function is not defined" error:**
- Check component is registered in `cotton-ui.js`
- Rebuild JavaScript bundle: `cd cottonui && npm run build`
- Check child components don't have conflicting `x-data`

### Styling Issues

**CSS variables not working:**
- Ensure Tailwind config extends colors with accent variables
- Rebuild CSS: `npx tailwindcss -i ./cottonui/css/cotton-ui.css -o ./cottonui/static/cotton-ui/cotton-ui.css --minify`
- Check using v3 syntax, not v4

**Classes not applied:**
- Check `x-bind:class` syntax
- Use browser dev tools to inspect Alpine data
- Verify variant detection logic

### Build Issues

**Module errors:**
- Ensure `package.json` has `"type": "module"`
- Use ES module syntax (`import`/`export`)
- Check all dependencies installed: `npm install`

## Resources

- **Flux UI Theming:** https://fluxui.dev/docs/theming
- **Alpine.js Docs:** https://alpinejs.dev
- **Django Cotton Docs:** https://django-cotton.com
- **Tailwind CSS v3:** https://tailwindcss.com/docs

## Examples

See these reference implementations:
- **Radio Component:** `cottonui/templates/cotton/ui/radio/`
- **Checkbox Component:** `cottonui/templates/cotton/ui/checkbox/`
- **Documentation:** `docs_project/templates/ui_docs/`

## Cotton Template Patterns

- Cotton's template tags are built-in. Never use `{% load cotton_tags %}`
- Avoid `{% with %}` tags. Use c-vars dictionaries with `get_item` filter for class management
- Cotton has issues nesting component calls inside conditional blocks
- When components need conditional rendering, render the structure inline rather than trying to nest component calls

## Django Integration

- Error handling should integrate with Django's `form.errors` dictionary, not Laravel-style error bags
- Use `<c-ui.error name="fieldname" :form="form" />` for Django form integration
- Error component accesses `form.errors|get_item:name` to lookup field errors
- Use `name="__all__"` for non-field errors via `form.non_field_errors`

## Component Architecture Patterns

- Don't create internal `_control.html` or `_*.html` sub-components for reducing duplication
- Inline duplication is acceptable when component composition causes issues
- Shorthand props in form controls render field structure inline to avoid nesting issues

## Documentation Standards

- Use `<c-header>` with subheading slot for page headers, not manual `<h1>` tags
- Use `<c-sample>` component for all examples, not manual div structures with shadow-lg
- Section headings use `<h2>`, API reference subsections use `<h4>`
- Code snippets go inside `<c-slot name="code">` within `<c-sample>`
- Page index should link to "Reference" section, not "API"
- First sample on component docs pages needs no separate title or description
