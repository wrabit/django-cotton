# Component tag

A `<c-` tag renders the component template with the same name.

```html
<c-button>Save</c-button>
<c-button />
```

Both render `cotton/button.html`. The content between the tags is available in the component as `{{ slot }}`.

## Resolving the name

| Tag | Template |
|---|---|
| `<c-button />` | `cotton/button.html` |
| `<c-my-button />` | `cotton/my_button.html` |
| `<c-forms.input />` | `cotton/forms/input.html` |
| `<c-card />` | `cotton/card.html`, or `cotton/card/index.html` if that doesn't exist |

Dots are folders. Hyphens become underscores in the filename, see [`COTTON_SNAKE_CASED_NAMES`](configuration.md) to keep them as hyphens. The `cotton` folder can live in any app's `templates` directory or the project's, see [`COTTON_DIR`](configuration.md) to rename it.

## `only`

Renders the component with none of the parent's context. It sees only its own attributes, not even context processor output like `request` or `user`.

```html
<c-card only title="Isolated" />
```

Project-wide isolation that keeps context processors is a setting, [`COTTON_ISOLATE_BY_DEFAULT`](configuration.md).

## Dynamic components

`<c-component>` with an `is` attribute resolves the component name at render time. `is` is not passed on to the component and doesn't appear in `{{ attrs }}`.

```html
<c-component is="icons.{{ name }}" />
<c-component :is="component_name" />
```

## Template tag syntax

Every tag has a native form:

```django
{% cotton button variant="primary" %}Save{% endcotton %}
{% cotton button / %}
{% cotton component is="icons.star" / %}
```

The tags are registered as builtins, so there is nothing to `{% load %}`.
