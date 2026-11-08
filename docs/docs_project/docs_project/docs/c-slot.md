# c-slot

`<c-slot>` passes a block of HTML into a component under a name. Inside the component it's a variable holding rendered, safe HTML.

```html label=view.html
<c-card>
    <c-slot name="header">
        <h2>Weather</h2>
    </c-slot>

    Sunny, 23°
</c-card>
```

```html label=cotton/card.html
<div class="card">
    <div class="card-header">{{ header }}</div>
    {{ slot }}
</div>
```

## Rules

- `<c-slot>` goes between a component's tags. It can be wrapped in HTML or in template logic like `{% if %}`. Using it outside any component is an error.
- Everything between the component's tags that isn't in a named slot is the default slot, `{{ slot }}`.
- A slot can contain anything a template can: HTML, variables, other components, more slots inside those.
- Hyphenated names are available as snake_case: `name="leading-icon"` becomes `{{ leading_icon }}`.
- A slot with the same name as a `<c-vars />` key takes precedence over the var's default.

## Checking for a slot

Slots are plain variables, so `{% if %}` works:

```html label=cotton/card.html
{% if header %}
    <div class="card-header">{{ header }}</div>
{% endif %}
```

## Template tag syntax

```django
{% cotton:slot header %}<h2>Weather</h2>{% endcotton:slot %}
```
