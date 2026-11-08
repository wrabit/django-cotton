# c-vars

`<c-vars />` declares the attributes a component uses for itself. A declared key is removed from `{{ attrs }}` and becomes a template variable, with a default if one is given. One `<c-vars />` per component, normally at the top.

```html label=cotton/input.html
<c-vars type="text" label errors />

<label>{{ label }}</label>
<input type="{{ type }}" {{ attrs }} />
```

## Defaults

A value is the default, used when the parent doesn't pass that attribute. The parent's value always wins.

```html
<c-vars type="text" size="md" />
```

## Claiming without a default

A key on its own keeps the attribute out of `{{ attrs }}` without setting anything. The variable is undefined unless the parent passes it, so `{% if errors %}` works as expected.

```html
<c-vars label errors />
```

## Dynamic defaults

Prefix with `:` to give a Python literal or a context variable as the default, the same way as a [dynamic attribute](attributes.md).

```html
<c-vars :items="[]" :open="False" :user="request.user" />
```

A bare value without quotes is treated as dynamic too, falling back to the literal string if it isn't a variable or literal:

```html
<c-vars enabled=False />
```

## Template expressions in defaults

A quoted default can contain template syntax, rendered when the component renders:

```html
<c-vars label="{% trans 'Loading' %}" css="btn btn-{{ size }}" />
```

## Merging classes

Add `:merge` to `class` and the parent's classes are appended to the default instead of replacing it. Only `class` can be merged.

```html
<c-vars class:merge="btn btn-primary" />

<button class="{{ class }}" {{ attrs }}>{{ slot }}</button>
```

```html
<c-button class="w-full" />
<!-- <button class="btn btn-primary w-full"> -->
```

A dynamic `:class` from the parent merges the same way. `{{ attrs.class }}` holds the merged value.

## Names

Hyphenated keys are available as snake_case variables: `data-id` becomes `{{ data_id }}`. If the parent passes a named slot with the same name as a declared key, the slot takes precedence.

## Template tag syntax

```django
{% cotton:vars type="text" label errors %}
```
