<img alt="Django Cotton Logo" src="https://github.com/wrabit/django-cotton/assets/5918271/1b0de6be-e943-4250-84c5-4662e2be07f5" width="400">

<!--<img src="https://github.com/wrabit/django-cotton/assets/5918271/e1c204dd-a91d-4883-8b76-b47af264c251" width="400">-->

# Django Cotton

![PyPI](https://img.shields.io/pypi/v/django-cotton?color=blue&style=flat-square)
[![PyPI Downloads](https://static.pepy.tech/badge/django-cotton/month)](https://pepy.tech/projects/django-cotton)

Bringing component-based design to Django templates.

- Docs site + demos: <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>
- <a href="https://discord.gg/4x8ntQwHMe" target="_blank">Discord community</a> (new)

## Contents

[Why?](#why-cotton)  
[Install](#install)  
[Usage Basics](#usage-basics)   
[Your First component](#your-first-component)  
[Attributes](#add-attributes)  
[Named Slots](#named-slots)  
[Pass Template Variables](#pass-template-variable-as-an-attribute)  
[Template expressions in attributes](#template-expressions-inside-attributes)  
[Boolean attributes](#boolean-attributes)  
[Passing Python data types](#passing-python-data-types)  
[Increase Re-usability with `{{ attrs }}`](#increase-re-usability-with--attrs-)  
[Merging and Proxying Attributes with `:attrs`](#merging-and-proxying-attributes-with-attrs)  
[In-component Variables with `<c-vars>`](#in-component-variables-with-c-vars)  
[HTMX Example](#an-example-with-htmx)  
[Limitations in Django that Cotton overcomes](#limitations-in-django-that-cotton-overcomes)  
[Template Syntax Options](#template-syntax-options)  
[Configuration](#configuration)  
[Caching](#caching)  
[Tools](#tools)  
[Version support](#version-support)  
[Changelog](#changelog)  
[Comparison with other packages](#comparison-with-other-packages)  

<hr>

## Why Cotton?

Cotton aims to overcome [certain limitations](#limitations-in-django-that-cotton-overcomes) that exist in the django template system that hold us back when we want to apply modern practices to compose UIs in a modular and reusable way.

## Key Features
- **Modern UI Composition:** Efficiently compose and reuse UI components.
- **Interoperable with Django:** Cotton only enhances django's existing template system (no Jinja needed).
- **HTML-like Syntax:** Native code editor syntax highlighting, code formatting and autoclosing ([VS Code plugin](#tools) for autocompletion).  
- **Minimal Overhead:** Compiles to native Django template tags with dynamic caching.
- **Encapsulates UI:** Keep layout, design and interaction in one file (especially when paired with Tailwind and Alpine.js)
- **Compliments HTMX:** Create reusable htmx components, render components directly from views.

<hr>

## Install

```bash
pip install django-cotton
```

### settings.py

```python
INSTALLED_APPS = [
    'django_cotton'
]
```

If you have previously specified a custom loader, you should perform [manual setup](https://django-cotton.com/docs/quickstart#install).

## Usage Basics
- **Component Placement:** Components should be placed in the `templates/cotton` folder (or define a [custom folder](https://django-cotton.com/docs/configuration)).
- **Naming Conventions:**
  - Components are called using kebab-case prefixed by 'c-': `<c-my-component />`
  - Component filenames use snake_case: `my_component.html` (or [configure](https://django-cotton.com/docs/configuration) for kebab-case)

## Walkthrough

### Your first component

```html
<!-- cotton/button.html -->
<a href="/" class="...">{{ slot }}</a>
```
```html
<!-- in view -->
<c-button>Contact</c-button>
```
```html
<!-- html output -->
<a href="/" class="...">Contact</a>
```

Everything provided between the opening and closing tag is provided to the component as `{{ slot }}`. It can contain any content, HTML or Django template expression.

### Adding attributes

```html
<!-- cotton/button.html -->
<a href="{{ url }}" class="...">
    {{ slot }}
</a>
```
```html
<!-- in view -->
<c-button url="/contact">Contact</c-button>
```
```html
<!-- html output -->
<a href="/contact" class="...">
    Contact
</a>
```

### Named slots

Named slots are a powerful concept. They allow us to provide HTML to appear in one or more areas in the component. Here we allow the button to optionally display an svg icon: 

```html
<!-- cotton/button.html -->
<a href="{{ url }}" class="...">
    {{ slot }}

    {% if icon %}
        <span class="some-class">
            {{ icon }}
        </span>
    {% endif %}
</a>
```
```html
<!-- in view -->
<c-button url="/contact">
    Contact
    <c-slot name="icon">
        <svg>...</svg>
    </c-slot>
</c-button>
```

Named slots can also contain any html or django template expression:

```html
<!-- in view -->
<c-button url="/contact">
    <c-slot name="icon">
      {% if mode == 'edit' %}
          <svg id="pencil">...</svg>
      {% else %}
          <svg id="disk">...</svg>
      {% endif %}
    </c-slot>
</c-button>
```

### Pass template variable as an attribute

To pass a template variable you prepend the attribute name with a colon `:`. Consider a bio card component:

```html
<!-- in view -->
<c-bio-card :user="user" />
```

That has a component definition like:

```html
<!-- cotton/bio_card.html -->
<div class="...">
  <img src="{{ user.avatar }}" alt="...">
  {{ user.username }} {{ user.country_code }}
</div>
```


### Template expressions inside attributes

You can use template expression statements inside attributes.

```html
<c-weather icon="fa-{{ icon }}"
           unit="{{ unit|default:'c' }}"
           condition="very {% get_intensity %}"
/>
```

### Boolean attributes

Boolean attributes reduce boilerplate when we just want to indicate a certain attribute should be `True` or not.

```html
<!-- in view -->
<c-button url="/contact" external>Contact</c-button>
```
By passing just the attribute name without a value, it will automatically be provided to the component as `True`

```html
<!-- cotton/button.html -->
<a href="{{ url }}" {% if external %} target="_blank" {% endif %} class="...">
    {{ slot }}
</a>
```

### Passing Python data types

Using the ':' to prefix an attribute tells Cotton we're passing a dynamic type down. We already know we can use this to send a variable, but you can also send basic python types, namely:

- Integers and Floats
- None, True and False
- Lists
- Dictionaries

This benefits a number of use-cases, for example if you have a select component that you want to provide the possible options from the parent:

```html
<!-- cotton/select.html -->
<select {{ attrs }}>
    {% for option in options %}
        <option value="{{ option }}">{{ option }}</option>
    {% endfor %}
</select>
```

```html
<c-select name="q1" :options="['yes', 'no', 'maybe']" />
```

```html
<!-- source code output -->
<select name="q1">
    <option value="yes">yes</option>
    <option value="no">no</option>
    <option value="maybe">maybe</option>
</select>
```

### Increase Re-usability with `{{ attrs }}`

`{{ attrs }}` is a special variable that contains all the attributes passed to the component (except those defined as [c-vars](https://github.com/wrabit/django-cotton?tab=readme-ov-file#in-component-variables-with-c-vars)) in a key="value" format. This is useful when you want to pass all attributes to a child element without having to explicitly define them in the component template. For example, you have inputs that can have any number of attributes defined:

```html
<!-- cotton/input.html -->
<input type="text" class="..." {{ attrs }} />
```

```html
<!-- example usage -->
<c-input placeholder="Enter your name" />
<c-input name="country" id="country" value="Japan" required />
```

```html
<!-- html output -->
<input type="text" class="..." placeholder="Enter your name" />
<input type="text" class="..." name="country" id="country" value="Japan" required />
```

### Merging and Proxying Attributes with `:attrs`

While `{{ attrs }}` is great for outputting all attributes passed to a component, Cotton provides more control with the special dynamic attribute `:attrs`.

**Merge a dictionary of attributes**

You can pass a dictionary of attributes (e.g., from your Django view's context) to a component using the `:attrs` syntax. These attributes are then merged with any other attributes passed directly and become available in the component's `attrs` variable (for use with `{{ attrs }}`). This is useful for applying a pre-defined set of attributes.

```html
<!-- cotton/input.html -->
<input type="text" {{ attrs }} />
```

```python
# In your view context
context = {
    'widget_attrs': {
        'placeholder': 'Enter your name',
        'data-validate': 'true',
        'size': '40'
    }
}
```

```html
<!-- In your template (e.g., form_view.html) -->
<c-input :attrs="widget_attrs" required />
```

```html
<!-- HTML output -->
<input type="text" placeholder="Enter your name" data-validate="true" size="40" required />
```
Notice how `required` (passed directly to `<c-input>`) is merged with attributes from `widget_attrs`.

**Proxy attributes to a nested component**

The `:attrs` attribute also allows you to pass all attributes received by a wrapper component directly to a nested component. This is powerful for creating higher-order components or wrapping existing ones. When you use `<c-child :attrs="attrs">`, the child component receives the `attrs` dictionary of the parent.

```html
<!-- cotton/outer_wrapper.html -->
<c-vars message /> <!-- 'message' is for outer_wrapper, not to be passed via attrs -->
<p>Outer message: {{ message }}</p>
<c-inner-component :attrs="attrs">
    {{ slot }}
</c-inner-component>
```

```html
<!-- cotton/inner_component.html -->
<div class="inner {{ class }}">
    {{ slot }}
</div>
```

```html
<!-- In view -->
<c-outer-wrapper message="Hello from outside"
                 class="special-class">
    Inner content
</c-outer-wrapper>
```

```html
<!-- HTML output -->
<p>Outer message: Hello from outside</p>
<div class="inner special-class">
    Inner content
</div>
```
Attributes like `class` are passed from `<c-outer_wrapper>` to `<c-inner_component>` via its `attrs` variable, while `message` (declared in `<c-vars>`) is used by `outer-wrapper` itself and excluded from the `attrs` passed down.

### In-component Variables with `<c-vars>`

Django templates adhere quite strictly to the MVC model and does not permit a lot of data manipulation in views. Fair enough, but what if we want to handle data for the purpose of UI state only? Having presentation related variables defined in the back is overkill and can quickly lead to higher maintenance cost and loses encapsulation of the component. Cotton allows you define in-component variables for the following reasons:

#### Using `<c-vars>` for default attributes

In this example we have a button component with a default "theme" but it can be overridden.

```html
<!-- cotton/button.html -->
<c-vars theme="bg-purple-500" />

<a href="..." class="{{ theme }}">
    {{ slot }}
</a>
```
```html
<!-- in view -->
<c-button>I'm a purple button</c-button>
```
```html
<!-- html output -->
<a href="..." class="bg-purple-500">
    I'm a purple button
</a>
```

Now we have a default theme for our button, but it is overridable:

```html
<!-- in view -->
<c-button theme="bg-green-500">But I'm green</c-button>
```
```html
<!-- html output -->
<a href="..." class="bg-green-500">
    But I'm green
</a>
```

#### Using `<c-vars>` to govern `{{ attrs }}`

Using `{{ attrs }}` to pass all attributes from parent scope onto an element in the component, you'll sometimes want to provide additional properties to the component which are not intended to be an attributes. In this case you can declare them in `<c-vars />` and it will prevent it from being in `{{ attrs }}`

Take this example where we want to provide any number of attributes to an input but also an icon setting which is not intened to be an attribute on `<input>`:

```html
<!-- in view -->
<c-input type="password" id="password" icon="padlock" />
```
```html
<!-- cotton/input.html -->
<c-vars icon />

<img src="icons/{{ icon }}.png" />

<input {{ attrs }} />
```

Input will have all attributes provided apart from the `icon`:

```html
<input type="password" id="password" />
```

### Dynamic Components

Sometimes there is a need to include a component dynamically, for example, you are looping through some data and the type of component is defined within a variable.

```html
<!--
form_fields = [
  {'type': 'text'},
  {'type': 'textarea'},
  {'type': 'checkbox'}  
]
-->

{% for field in form_fields %}
    <c-component :is="field.type" />
{% endfor %}
```

You can also provide a template expression, should the component be inside a subdirectory or have a prefix:

```html
{% for field in form_fields %}
    <!-- subfolder -->
    <c-component is="form-fields.{{ field.type }}" />

    <!-- component prefix -->
    <c-component is="field_{{ field.type }}" />
{% endfor %}
```

<hr>

### An example with HTMX

Cotton helps you build re-usable HTMX-powered components. Define your styles and markup once, then pass different HTMX attributes via attributes:

```html
<!-- cotton/button.html -->
<button {{ attrs }} class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    {{ slot }}
</button>
```

```html
<!-- in view -->
<c-button hx-post="/users/1/follow" hx-swap="outerHTML">
    Follow
</c-button>

<c-button hx-delete="/posts/1" hx-confirm="Are you sure?">
    Delete Post
</c-button>

<c-button hx-get="/notifications" hx-target="#notifications">
    Load More
</c-button>
```

### Rendering Components from Views (HTMX Partials)

When building HTMX-powered interfaces, you often need to return partial HTML from view functions. Cotton provides `render_component()` to programmatically render components from views:

```html
<!-- cotton/notification.html -->
<div class="alert alert-{{ type }}">{{ message }}</div>
```

```python
# views.py
from django.http import HttpResponse
from django_cotton import render_component

def user_deleted(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return HttpResponse(
        render_component(request, "notification",
            message=f"{user.name} deleted",
            type="success"
        )
    )
```

<hr>

## Limitations in Django that Cotton overcomes

Whilst you _can_ build frontends with Django’s native tags, there are a few things that hold us back when we want to apply modern practices:

### `{% block %}` and `{% extends %}`
This system strongly couples child and parent templates making it hard to create a truly re-usable component that can be used in places without it having a related base template.

### What about `{% include %}` ?
Modern libraries allow components to be highly configurable, whether it’s by attributes, passing variables, passing HTML with default and named slots. {% include %} tags, whilst they have the ability to pass simple variables and text, they will not allow you to easily send HTML blocks with template expressions let alone other niceties such as boolean attributes, named slots etc.

### What's with `{% with %}`?
Whilst {% with %} tags allow us to provide variables and strings it quickly busies up your code and has the same limitations about passing more complex types.

### Custom `{% templatetags %}`
Cotton does essentially compile down to templatetags but there is some extra work it performs above it to help with scoping and auto-managing keys which will be difficult to manage manually in complex nested structures.

<a href="https://medium.com/@willabbott/introducing-django-cotton-revolutionizing-ui-composition-in-django-ea7fe06156b0" target="_blank">[Source article]</a>

## Native Django template tags vs Cotton

In addition, Cotton enables you to navigate around some of the limitations with Django's native tags and template language:

### HTML in attributes
❌ **Django native:**
```html
{% my_header icon="<svg>...</svg>" %}
```
✅ **Cotton:**
```html
<c-my-header>
    <c-slot name="icon">
        <svg>...</svg>
    </c-slot>
</c-my-header>
```

### Template expressions in attributes
❌ **Django native:**
```html
{% bio name="{{ first_name }} {{ last_name }}" extra="{% get_extra %}" %}
```
✅ **Cotton:**
```html
<c-bio name="{{ first_name }} {{ last_name }}" extra="{% get_extra %} />
```

### Pass simple python types
❌ **Django native:**
```html
{% my_component default_options="['yes', 'no', 'maybe']" %}
{% my_component config="{'open': True}" %}
{% my_component enabled="True" %}
```
✅ **Cotton:**
```html
<c-my-component :default_options="['yes', 'no', 'maybe']" />
<c-my-component :config="{'open': True}" />
<c-my-component :enabled="True" />

(provides a List and Dict to component)
```

### Multi-line definitions
❌ **Django native:** 
```html
{% my_component
    arg=1 %}
```
✅ **Cotton:**
```html
<c-my-component
    class="blue"
    x-data="{
        something: 1
    }" />
```

### Dynamic components
❌ **Django native:** 
```html
{% {{ templatetag_name }} arg=1 %}
```
✅ **Cotton:**
```html
<c-component :is="component_name" />
<c-component is="{{ component_name }}" />
<c-component is="subfolder1.subfolder2.{{ component_name }}" />
```

<hr>

## Template Syntax Options

Cotton supports two syntax styles for using components in your templates:

### HTML-like Syntax (Recommended)
This syntax has better IDE support - code formatting, autocompletion, autoclosing and syntax highlighting. 

### Native Django Template Tag Syntax
For those who prefer Django's native template tag style, Cotton provides equivalent template tags for all features.

### Syntax Comparison

| Feature | HTML-like Syntax | Native Template Syntax |
|---------|-----------------|------------------------|
| **Component** | `<c-button>...</c-button>` | `{% cotton button %}...{% endcotton %}` |
| **Self-closing** | `<c-button />` | `{% cotton button / %}` |
| **Variables** | `<c-vars title />` | `{% cotton:vars title %}` |
| **Named Slot** | `<c-slot name="header">...</c-slot>` | `{% cotton:slot header %}...{% endcotton:slot %}` |

<hr>

## Configuration

`COTTON_DIR` (default: "cotton")  

The directory where your components are stored.

`COTTON_BASE_DIR` (default: None)  

If you use a project-level templates folder then you can set the path here. This is not needed if your project already has a `BASE_DIR` variable.

`COTTON_SNAKE_CASED_NAMES` (default: True)  

Whether to search for component filenames in snake_case. If set to False, you can use kebab-cased / hyphenated filenames.

<hr>

## Caching

Cotton is optimal when used with Django's cached.Loader. If you use <a href="https://django-cotton.com/docs/quickstart">automatic configuration</a> then the cached loader will be automatically applied.

<hr>

## Tools

- [Cotton VS Code plugin](https://marketplace.visualstudio.com/items?itemName=twentyforty.django-cotton) from [twentyforty](https://github.com/twentyforty)  
- [Cotton Icons](https://github.com/wrabit/cotton-icons) - Heroicons and Tabler Icon sets for Cotton

## Version Support

- Python >=3.8,<4
- Django >4.2,<5.3

<hr>

## Changelog

[See releases](https://github.com/wrabit/django-cotton/releases)

<hr>

## Comparison with other packages

| **Feature**                                                                                         | **Cotton**                 | **django-components**                  | **Slippers**                                               |
|-----------------------------------------------------------------------------------------------------|----------------------------|----------------------------------------|------------------------------------------------------------|
| **Intro**                                                                                           | UI-focused, expressive syntax       | Holistic solution with backend logic   | Enhances DTL for reusable components                       |
| **Definition of ‘component’**                                                                       | An HTML template           | A backend class with template          | An HTML template                                           |
| **Syntax Style**                                                                                     | HTML-like                  | Django Template Tags                   | Django Template Tags with custom tags                      |
| **One-step package install**                                                                        | ✅                        | ❌                                    | ❌                                                        |
| **Create component in one step?**                                                                   | ✅ <br> (place in folder) | ✅ <br> (Technically yes with single-file components) | ❌ <br> (need to register in YAML file or with function)   |
| **Slots** <br> Pass HTML content between tags                                             | ✅                        | ✅                                    | ✅                                                        |
| **Named Slots** <br> Designate a slot in the component template                                     | ✅                        | ✅                                    | ✅ (using ‘fragments’)                                      |
| **Dynamic Components** <br> Dynamically render components based on a variable or expression         | ✅                        | ✅                                    | ❌                                                        |
| **Scoped Slots** <br> Reference component context in parent template                                | ❌                         | ✅                                    | ❌                                                         |
| **Dynamic Attributes** <br> Pass string literals of basic Python types                              | ✅                        | ❌                                    | ❌                                                         |
| **Boolean Attributes** <br> Pass valueless attributes as True                                       | ✅                        | ✅                                    | ❌                                                         |
| **Implicit Attribute Passing** <br> Pass all defined attributes to an element                       | ✅                        | ❌                                     | ✅                                                        |
| **Django Template Expressions in Attribute Values** <br> Use template expressions in attribute values | ✅                        | ❌                                    | ❌                                                         |
| **Attribute Merging** <br> Replace existing attributes with component attributes                    | ✅                        | ✅                                    | ❌                                                         |
| **Multi-line Component Tags** <br> Write component tags over multiple lines                         | ✅                        | ✅                                     | ❌                                                         |

**Notes:** 

- Some features here can be resolved with 3rd party plugins, for example for expressions, you can use something like `django-expr` package. So the list focuses on a comparison of core feature of that library.

<hr>

For full docs and demos, checkout <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>
