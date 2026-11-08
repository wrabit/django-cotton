# Component Variants

Variants are a simple pattern for giving a component a set of named styling options. Think a button that's *primary*, *danger* or *subtle*, an alert that's *info* or *warning*, and so on. With Cotton you can keep all of those options in one component file, with no extra Python and no duplicated templates.

## The problem {#problem}

Without variants you tend to end up with a template per flavour (`button_primary.html`, `button_danger.html`...) or a tangle of `{% if %}` branches. Both duplicate the component's core markup and drift out of sync over time.

## Defining variants {#defining}

Declare a dictionary of variants with `<c-vars />`, set a sensible default, then look the chosen one up with Cotton's built-in `get_item` filter:

```html label=cotton/button.html
<c-vars
    variant="default"
    :variants="{
        'default': 'bg-gray-200 text-gray-800 hover:bg-gray-300',
        'primary': 'bg-sky-500 text-white hover:bg-sky-600',
        'danger': 'bg-red-500 text-white hover:bg-red-600',
    }"
/>

<button {{ attrs }} class="px-4 py-2 rounded {{ variants|get_item:variant }}">
    {{ slot }}
</button>
```

Because the variant map lives inside `<c-vars />`, it never leaks out as an attribute on the rendered `<button>`. Only the resolved class string does.

## Using variants {#using}

Pick a variant by name. Omit it and the default kicks in:

```html label=view.html preview=demo.variants
<c-button>Click me!</c-button>
<c-button variant="primary">Submit</c-button>
<c-button variant="danger">Delete</c-button>
```

> The variable doesn't have to be called `variant`. Name the `c-vars` key whatever reads best for the component (`theme`, `style`, `kind`, ...) and look it up the same way.

## Beyond styling {#beyond}

Variants aren't limited to a single class string or even to colours. A map value can carry any markup-driving data, and you can keep more than one map for orthogonal options. For example, a `:variants` map for the fill style and an `:outlined-variants` map toggled by a boolean:

```html label=cotton/button.html
<c-vars
    variant="primary"
    :outlined="False"
    :variants="{ 'primary': 'bg-sky-500 text-white', 'danger': 'bg-red-500 text-white' }"
    :outlined-variants="{ 'primary': 'border border-sky-500 text-sky-500', 'danger': 'border border-red-500 text-red-500' }"
/>

<button {{ attrs }} class="px-4 py-2 rounded
    {% if outlined %}{{ outlined_variants|get_item:variant }}{% else %}{{ variants|get_item:variant }}{% endif %}">
    {{ slot }}
</button>
```

## Tips {#tips}

- Keep every flavour of a component centralised in the one component file. That's the whole win.
- Always provide a `default` so callers can stay terse and nothing breaks when a variant is omitted.
- Use descriptive, intent-based names (`info`, `success`, `warning`, `danger`) rather than colour names.
- The same approach scales to alerts, badges, tabs, inputs, modals and menus, or anywhere you'd reach for a "type" or "style" prop.
