# Components

Components are reusable pieces of view template. They can contain native Django template syntax and can be used inside standard Django templates.

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

### Passing variables vs strings

`:today="today"` and `today="{{ today }}"` do different things. The colon form hands the variable itself to the component, so it can read `today.temperature`. The template expression form renders in place first, so the component receives a string. Reach for the colon when the component needs the variable, and a template expression when you want a string, whether passed as is or built up.

```html label="Variable vs string"
<c-weather :today="today" />                 {# today is the Weather object #}
<c-weather unit="{{ today.unit }}" />        {# unit is the string "c" #}
<c-weather icon="fa-{{ today.icon }}" />     {# icon is the string "fa-sun" #}
```

> **Note:** variables can also be passed Django-style, `today=today`.

### Python literals

The colon form evaluates Python literals, so numbers, booleans, `None`, lists and dicts can be written straight into the template.

```html label="Integers & Floats"
<c-mycomp :prop="1" />
{# prop == 1 #}
```

```html label="Booleans & None"
<c-mycomp :enabled="True" :prop="None" />
{# enabled is True, prop is None #}
```

```html label=Lists
<c-mycomp :items="['item1','item2','item3']" />
{# for item in items #}
```

```html label=Dicts
<c-mycomp :mydict="{'name': 'Thom', 'products': [1,2]}" />
{# mydict.name, mydict.products #}
```

```html label="With template expressions"
<c-mycomp :slides="['{{ image1 }}', '{{ image2 }}']" />
{# for image in slides #}
```

```html label="Generated with template expressions"
<c-mycomp :is_highlighted="{% if important %}True{% endif %}" />
{# is_highlighted is True when important #}
```

A typical use is a select component that takes its options from the parent:

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

The next two sections cover the other things you can do with that dictionary: add to it from the outside, and take keys out of it from the inside. Both operate on the same `attrs`.

## 5.1 Adding to attrs with :attrs {#attrs-merging}

Pass a dictionary through the special `:attrs` attribute and its keys are merged into `attrs` alongside anything passed directly. Useful when a view, or another component, already holds the attributes you want applied.

```html label=cotton/input.html
<input type="text" {{ attrs }} />
```

```python label=views.py
def form_view(request):
    return render(request, "form_view.html", {
        "widget_attrs": {
            "placeholder": "Enter your name",
            "data-validate": "true",
            "size": "40",
        }
    })
```

```html label=form_view.html
<c-input :attrs="widget_attrs" required />

<!-- html output
<input type="text" placeholder="Enter your name" data-validate="true" size="40" required />
-->
```

### Passing attrs on to another component

Because `attrs` is just a dictionary, a wrapper component can hand the whole thing to the component it wraps, without naming each attribute.

```html label=cotton/outer_wrapper.html
<c-inner-component :attrs="attrs">
    {{ slot }}
</c-inner-component>
```

See [attribute proxying](attribute-proxying.md) for the full pattern.

## 6. Claiming attributes with c-vars {#vars}

Some attributes are for the component to use, not for its HTML. Declare those in a single `<c-vars />` at the top of the component. A declared key is removed from `attrs` and becomes an ordinary template variable, with a default if you give one.

### Defaults

Set a value in `<c-vars />` and it applies whenever the parent does not pass that attribute.

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

### Keeping configuration out of `{{ attrs }}`

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

### Merging classes

A plain default is replaced when the parent passes the attribute. For `class` you usually want to add to it instead, so the component keeps its own classes and the parent can tweak the layout. Add `:merge` to the key and the parent's classes are appended to the default.

```html label=cotton/button.html
<c-vars class:merge="btn btn-primary" />

<button class="{{ class }}" {{ attrs }}>{{ slot }}</button>
```

```html label=form_view.html
<c-button>Save</c-button>
<c-button class="w-full">Save</c-button>

<!-- renders -->
<button class="btn btn-primary">Save</button>
<button class="btn btn-primary w-full">Save</button>
```

A dynamic `:class` from the parent is merged the same way. Only `class` can be merged for now. The classes are joined as they are, so conflicting utility classes (say `bg-red-500` from the parent and `bg-blue-500` in the default) are both kept and the stylesheet decides which one wins.

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

## 9. Context Isolation {#context-isolation}

By default, components inherit the parent template's full context. There are two ways to opt out:

#### `only`: total isolation per component

Add the `only` attribute to an individual component to block *all* outside context. The component sees nothing except its directly passed attributes: no parent template variables, no context processors (no `request`, no `user`, etc).

#### `COTTON_ISOLATE_BY_DEFAULT`: smart isolation project-wide

Set `COTTON_ISOLATE_BY_DEFAULT = True` in `settings.py` to make every component *silently scoped*: parent template variables (from `{% with %}`, `{% for %}`, the view context, etc.) do not leak in, but global context-processor output is preserved. Useful when you want isolation as the default but still want components to see `request`, `user`, `messages`, etc.

You can still add `only` on a per-component basis to also block context-processor output. See [configuration](configuration.md).

## 10. Alpine.js support {#alpine-js-support}

The following key features allow you to build re-usable components with alpine.js:

- `x-data` is accessible as `{{ x_data }}` inside the component as cotton makes available snake_case versions of all kebab-cased attributes. (If you use `{{ attrs }}` then the output will already be in the correct case).
- [Shorthand x-bind](https://alpinejs.dev/directives/bind) support (`:example`). Because single `:` attribute prefixing is reserved for cotton's [dynamic attributes](#dynamic-attributes), we can escape the first colon using `::`. This will ensure the attribute maintains a single `:` inside `{{ attrs }}`.

## Summary of Concepts {#summary}

- `{{ slot }}` - Default content injection.
- **Attributes** - Simple, straightforward customization.
- **Named Slots** - Provide HTML or template partial as a variable in the component.
- **`:` Dynamic Attributes** - Pass variables and other data types other than strings.
- `{{ attrs }}` - Prints attributes as HTML attributes.
- `<c-vars />` - Set default values and other component state.
- **Boolean attributes** - Attributes without values are passed down as `True`.
- **Dynamic Components** - Insert a component where the name is generated by a variable or template expression: `<c-component :is="my_variable" />`
