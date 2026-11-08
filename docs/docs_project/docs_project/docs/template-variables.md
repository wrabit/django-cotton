# Template variables

What a component template can see.

## `{{ slot }}`

The content between the component's opening and closing tags, minus any named slots. Already rendered and safe.

## Named slots

Each `<c-slot name="header">` is available as `{{ header }}`. See [c-slot](c-slot.md).

## Attributes by name

Every attribute is a variable: `title="Hi"` gives `{{ title }}`. Hyphenated names are snake_case, `data-id` gives `{{ data_id }}`. Dynamic attributes keep their type, so `:items="[1, 2]"` gives a list you can loop over.

## `{{ attrs }}`

All attributes the parent passed, minus anything declared in [`<c-vars />`](c-vars.md) and minus `is`. Printed as HTML attributes:

```html label=cotton/input.html
<input type="text" {{ attrs }} />
```

```html
<c-input name="email" placeholder="Email" required />
<!-- <input type="text" name="email" placeholder="Email" required /> -->
```

Boolean attributes print as the bare name. Values are quoted, choosing the quote style to suit the content.

`attrs` is also a mapping, so single values and iteration work:

```html
{{ attrs.placeholder }}
{% for key, value in attrs.items %}{{ key }}={{ value }} {% endfor %}
```

Dictionaries passed with `:attrs` are merged into it. A `class` declared with `class:merge` holds the merged value in `attrs.class`.

## Declared vars

Keys from `<c-vars />` are variables with their default or the parent's value. See [c-vars](c-vars.md).

## Parent context

By default a component sees everything its parent template sees: the view's context, context processors, loop variables. `only` on the tag removes all of it, and [`COTTON_ISOLATE_BY_DEFAULT`](configuration.md) removes the parent template's variables project-wide while keeping context processors.
