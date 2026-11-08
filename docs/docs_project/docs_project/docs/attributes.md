# Attributes

Everything on a component tag is an attribute. Each one is available in the component by name, and all of them together as [`{{ attrs }}`](template-variables.md).

## Strings

A quoted value is a string. It can contain template syntax, which is rendered first, so the component still receives a string:

```html
<c-weather unit="c" />
<c-weather unit="{{ today.unit }}" icon="fa-{{ today.icon }}" />
```

## Dynamic values with `:`

A `:` prefix passes the value itself rather than a string. The value is a context variable or a Python literal:

```html
<c-weather :today="today" />
<c-chart :height="300" :animate="True" :fallback="None" />
<c-select :options="['no', 'yes', 'maybe']" />
<c-table :config="{'sortable': True, 'page_size': 20}" />
```

Template expressions work inside literals too, rendered before the literal is evaluated:

```html
<c-gallery :slides="['{{ image1 }}', '{{ image2 }}']" />
<c-row :highlight="{% if important %}True{% else %}False{% endif %}" />
```

## Unquoted values

A value without quotes is looked up as a variable, falling back to the literal text if there is no such variable:

```html
<c-weather unit=unit />
```

## Boolean attributes

An attribute with no value is `True`:

```html
<c-input name="email" required />
```

```html label=cotton/input.html
{% if required %}<span>*</span>{% endif %}
```

In `{{ attrs }}` it prints as the bare name, `required`.

## Passing a dictionary with `:attrs`

`:attrs` takes a dictionary and merges its keys in alongside the other attributes. Useful when a view, or a wrapping component, already holds them:

```html
<c-input :attrs="widget_attrs" required />
```

```html label=cotton/outer.html
<c-inner :attrs="attrs">{{ slot }}</c-inner>
```

See [attribute proxying](attribute-proxying.md).

## Alpine's `:` shorthand {#alpine}

A single `:` is Cotton's dynamic prefix, so escape Alpine's `x-bind` shorthand with `::`. The attribute reaches `{{ attrs }}` with one colon:

```html
<c-button ::class="open ? 'active' : ''" />
<!-- <button :class="open ? 'active' : ''"> -->
```

## Names

Hyphenated attributes are available as snake_case variables, `data-id` becomes `{{ data_id }}`, while `{{ attrs }}` prints them as written. `only` and `is` are reserved: `only` isolates the component and `is` names a [dynamic component](component-tag.md), and neither reaches `{{ attrs }}`.
