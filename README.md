<img alt="Django Cotton Logo" src="https://github.com/wrabit/django-cotton/assets/5918271/1b0de6be-e943-4250-84c5-4662e2be07f5" width="400">

<!--<img src="https://github.com/wrabit/django-cotton/assets/5918271/e1c204dd-a91d-4883-8b76-b47af264c251" width="400">-->

# Django Cotton

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Bringing component-based design to Django templates.

- Docs site + demos: <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>

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
[In-component Variables with `<c-vars>`](#in-component-variables-with-c-vars)  
[HTMX Example](#an-example-with-htmx)  
[Limitations in Django that Cotton overcomes](#limitations-in-django-that-cotton-overcomes)  
[Caching](#caching)  
[Version support](#support)
[Changelog](#changelog)  
[Comparison with other packages](#comparison-with-other-packages)  


## Why Cotton?

Cotton aims to overcome [certain limitations](#limitations-in-django-that-cotton-overcomes) that exist in the django template system that hold us back when we want to apply modern practices to compose UIs in a modular and reusable way.

## Key Features
- **Modern UI Composition:** Efficiently compose and reuse UI components.
- **Interoperable with Django:** Cotton only enhances django's existing template system (no Jinja needed).
- **HTML-like Syntax:** Better code editor support and productivity as component tags are similar to html tags.
- **Minimal Overhead:** Compiles to native Django components with dynamic caching.
- **Encapsulates UI:** Keep layout, design and interaction in one file (especially when paired with Tailwind and Alpine.js)
- **Compliments HTMX:** Create smart components, reducing repetition and enhancing maintainability.

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
  - Component filenames use snake_case: `my_component.html`
  - Components are called using kebab-case prefixed by 'c-': `<c-my-component />`

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

### Add attributes

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
        {{ icon }} 
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

Named slots can also contain any django native template logic:

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

`{{ attrs }}` is a special variable that contains all the attributes passed to the component in an key="value" format. This is useful when you want to pass all attributes to a child element without having to explicitly define them in the component template. For example, you have inputs that can have any number of attributes defined:

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

### In-component Variables with `<c-vars>`

Django templates adhere quite strictly to the MVC model and does not permit a lot of data manipulation in views. Fair enough, but what if we want to handle data for the purpose of UI state only? Having presentation related variables defined in the back is overkill and can quickly lead to higher maintenance cost and loses encapsulation of the component. Cotton allows you define in-component variables for the following reasons:

#### 1. Using `<c-vars>` for default attributes

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

#### 2. Using `<c-vars>` to govern `{{ attrs }}`

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

### An example with HTMX

Cotton helps carve out re-usable components, here we show how to make a re-usable form, reducing code repetition and improving maintainability:

```html
<!-- cotton/form.html -->
<div id="result" class="..."></div>

<form {{ attrs }} hx-target="#result" hx-swap="outerHTML">
    {{ slot }}
    <button type="submit">Submit</button>
</form>
```

```html
<!-- in view -->
<c-form hx-post="/contact">
    <input type="text" name="name" placeholder="Name" />
    <input type="text" name="email" placeholder="Email" />
    <input type="checkbox" name="signup" />
</c-form>

<c-form hx-post="/buy">
    <input type="text" name="type" />
    <input type="text" name="quantity" />
</c-form>
```

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
{% my_component header="<h1>Header</h1>" %}
```
✅ **Cotton:**
```html
<c-my-component>
    <c-slot name="header">
        <h1>Header</h1>
    </c-slot>
</c-my-component>
```

### Template expressions in attributes
❌ **Django native:**
```html
{% my_component model="todos.{{ index }}.name" extra="{% get_extra %}" %}
```
✅ **Cotton:**
```html
<c-my-component model="todos.{{ index }}.name" extra="{% get_extra %} />
```

### Pass simple python types
❌ **Django native:**
```html
{% my_component default_options="['yes', 'no', 'maybe']" %}
{% my_component config="{'open': True}" %}
```
✅ **Cotton:**
```html
<c-my-component :default_options="['yes', 'no', 'maybe']" />
<c-my-component :config="{'open': True}" />

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

## Caching

Cotton is optimal when used with Django's cached.Loader. If you use <a href="https://django-cotton.com/docs/quickstart">automatic configuration</a> then the cached loader will be automatically applied. This feature has room for improvement, some desirables are:

- Integration with a cache backend to survive runtime restarts / deployments.
- Cache warming

For full docs and demos, checkout <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>

## Version Support

- Python >= 3.8
- Django >4.2,<5.2

## Changelog

[See releases](https://github.com/wrabit/django-cotton/releases)


## Comparison with other packages  

**Note:** This comparison was created due to multiple requests, apologies for any mistakes or if I have missed something from other packages - please get in touch / create an issue!

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
| **Django Template Expressions in Attribute Values** <br> Use Django expressions in attribute values | ✅                        | ❌                                    | ❌                                                         |
| **Attribute Merging** <br> Replace existing attributes with component attributes                    | ✅                        | ✅                                    | ❌                                                         |
| **Multi-line Component Tags** <br> Write component tags over multiple lines                         | ✅                        | ✅                                     | ❌                                                         |
