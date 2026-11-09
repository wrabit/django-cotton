# Tags and filters

Cotton registers its template tags as builtins, so none of this needs `{% load %}`.

## Native tag forms

Every `<c-` tag compiles to one of these, and they can be written directly:

| HTML syntax | Template tag |
|---|---|
| `<c-button>...</c-button>` | `{% cotton button %}...{% endcotton %}` |
| `<c-button />` | `{% cotton button / %}` |
| `<c-vars type="text" />` | `{% cotton:vars type="text" %}` |
| `<c-slot name="header">...</c-slot>` | `{% cotton:slot header %}...{% endcotton:slot %}` |

Attributes, `only` and `is` work the same in both forms.

## `{% cotton:verbatim %}`

Stops the compiler turning `<c-` tags inside it into components, so component markup can be shown as text. It is removed from the output. Pair it with Django's `{% verbatim %}` when the sample also contains `{{ }}` or `{% %}`:

```django ignore-syntax-choice
{% cotton:verbatim %}{% verbatim %}
<c-button title="{{ title }}">Save</c-button>
{% endverbatim %}{% endcotton:verbatim %}
```

## `get_item`

Looks a key up in a dictionary, for variable keys that dot notation can't express:

```html
<c-vars variant="default" :variants="{'default': 'bg-gray-200', 'primary': 'bg-sky-500'}" />

<button class="{{ variants|get_item:variant }}">{{ slot }}</button>
```

See [component variants](variants.md).
