# Components

Components are reusable pieces of view template. They can contain native Django template syntax and can be used inside standard Django templates. This page walks through the ideas in the order you'll meet them. The exact rules for each live in the [API](component-tag.md) section.

## 1. The basic building block: `{{ slot }}` {#slot}

The `{{ slot }}` variable captures all content passed between a component's opening and closing tags.

```html label=cotton/box.html
<div class="box">
    {{ slot }}
</div>
```

Used in a parent template:

```html label=my_view.html preview=demo.components.box
<c-box>
    <p>Some <strong>content</strong></p>
</c-box>
```

## 2. Adding Component Attributes {#attributes}

We can further customize components with attributes, which allow you to pass specific data into the component as key-value pairs.

```html label=cotton/weather.html
<p>It's {{ temperature }}<sup>o</sup>{{ unit }} and the condition is {{ condition }}.</p>
```

```html label=view.html preview=demo.components.weather
<c-weather temperature="23" unit=unit condition="windy"></c-weather>
```

## 3. Using Named Slots {#named-slots}

If we want to pass HTML instead of just a string (or another data type) into a component, we can pass them as **named slots** with the `<c-slot name="...">...</c-slot>` syntax.

So as with normal attributes, you reference the slot content like normal variables, as in:

```html label=cotton/weather_card.html
<div class="flex ...">
    <h2>{{ day }}:</h2> {{ icon }} {{ label }}
</div>
```

```html label=view.html preview=demo.components.weather-card
<c-weather-card day="Tuesday">
    <c-slot name="icon">
        <img src="sunny-icon.png" alt="Sunny">
    </c-slot>

    <c-slot name="label">
        <div class="yellow">Sunny</div>
    </c-slot>
</c-weather-card>
```

Reference: [c-slot](c-slot.md).

## 4. Dynamic Attributes {#dynamic-attributes}

By default, every attribute you pass to a component arrives as a string. To pass anything else, a variable from context, a boolean, a number, a list or a dict, prefix the attribute name with a colon.

```html label=view.html
<!--
context = { 'today': Weather.objects.get(...) }
-->
<c-weather :today="today" />
```

```html label=cotton/weather.html
<p>It's {{ today.temperature }}<sup>o</sup>{{ today.unit }} and the condition is {{ today.condition }}.</p>
```

`:today="today"` and `today="{{ today }}"` do different things. The colon form hands the variable itself to the component, so it can read `today.temperature`. The template expression form renders in place first, so the component receives a string.

The colon form also takes Python literals. A typical use is a select component that takes its options from the parent:

```html label=view.html preview=demo.components.select
<c-select :options="['no', 'yes', 'maybe']" />
```

```html label=cotton/select.html
<select>
    {% for option in options %}
        <option value="{{ option }}">{{ option }}</option>
    {% endfor %}
</select>
```

Reference: [Attributes](attributes.md) covers every value type, unquoted values and the `:attrs` dictionary.

## 5. Working with `{{ attrs }}` {#attrs}

Every attribute passed to a component is collected into `attrs`, a dictionary the component can print, add to, pass on or trim. The simplest use is to reflect everything onto an element, which is what makes [form inputs](form-fields.md) practical.

```html label=form_view.html preview=demo.components.attrs-inputs
<c-input name="first_name" placeholder="First name" />
<c-input name="last_name" placeholder="Last name" value="Smith" readonly  />
```

```html label=cotton/input.html
<input type="text" {{ attrs }} />

<!-- html output
<input type="text" name="first_name" placeholder="First name" />
<input type="text" name="last_name" placeholder="Last name" value="Smith" readonly />
-->
```

A parent can add to `attrs` with a dictionary, `:attrs="widget_attrs"`, and a wrapper component can pass its whole `attrs` on to the component it wraps. See [attribute proxying](attribute-proxying.md) for that pattern.

Reference: [Template variables](template-variables.md).

## 6. Claiming attributes with c-vars {#vars}

Some attributes are for the component to use, not for its HTML. Declare those in a single `<c-vars />` at the top of the component. A declared key is removed from `attrs` and becomes an ordinary template variable, with a default if you give one.

```html label=cotton/alert.html
<c-vars type="success" />

<div class="{% if type == 'success' %} .. {% elif type == 'danger' %} .. {% endif %}">
    {{ slot }}
</div>
```

```html label=form_view.html preview=demo.components.alerts
<c-alert>All good!</c-alert>
<c-alert type="danger">Oh no!</c-alert>
```

Declaring a key with no value claims it without setting a default. Here `label` and `errors` are claimed, so they never reach the input, while `placeholder` is not, so it does.

```html label=cotton/input_group.html
<c-vars label errors />

<label>{{ label }}</label>

<input type="text" class="border ..." {{ attrs }} />

{% if errors %}
    {% for error in errors %}
        {{ error }}
    {% endfor %}
{% endif %}
```

```html label=form_view.html preview=demo.components.input-group
<c-input-group label="First name" placeholder="First name" :errors="errors.first_name" />
<c-input-group label="Last name" placeholder="Last name" :errors="errors.last_name" />
```

For `class` you usually want the parent's classes added to the component's own rather than replacing them. `class:merge="btn btn-primary"` does that.

Reference: [c-vars](c-vars.md) covers dynamic defaults, template expressions in defaults and merging.

## 7. Boolean attributes {#boolean-attributes}

Sometimes you just want to pass a simple boolean to a component. Cotton supports providing the attribute name without a value which will provide a boolean True to the component.

```html label=cotton/input.html
<input type="text" {{ attrs }} />

{% if required is True %}
    <span class="text-red-500">*</span>
{% endif %}
```

```html label=form_view.html preview=demo.components.required
<c-input name="telephone" required />
```

## 8. Dynamic Components {#dynamic-components}

There can be times where components need to be included dynamically. For these cases we can reach for a special `<c-component>` tag with an `is` attribute:

```html label=cotton/icon_list.html
{% for icon in icons %}
    <c-component is="icons.{{ icon }}" />
{% endfor %}
```

The `is` attribute is similar to other attributes so we have a number of possibilities to define it:

```html label=cotton/icon_list.html
<!-- as variable -->
<c-component :is="icon_name" />

<!-- as an expression -->
<c-component is="icon_{{ icon_name }}" />
```

Reference: [Component tag](component-tag.md), which also covers `only` and context isolation.

## Where next {#where-next}

That's the whole model: a slot, attributes, named slots and `<c-vars />` to say which attributes are the component's own. The [tutorials](form-fields.md) build real components with it, and the API section has the precise rules for the [component tag](component-tag.md), [attributes](attributes.md), [c-vars](c-vars.md), [c-slot](c-slot.md) and the [template variables](template-variables.md), including Alpine.js support and context isolation.
